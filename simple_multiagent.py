"""
Simplified Multi-Agent System - Role-Based, No Recursion
"""
import time
import asyncio
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hidr.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('HIDR.MultiAgent')

class SimpleMultiAgent:
    def __init__(self, config_path: str = "config.yaml", use_langgraph: bool = False):
        self.messages = []
        self.yara_scanner = None
        self.expert_system = None
        self.langgraph_orchestrator = None
        self.use_langgraph = use_langgraph
        self.config = self._load_config(config_path)
        self._init_yara()
        self._init_expert_system()
        if use_langgraph:
            self._init_langgraph()
        logger.info(f"Multi-Agent System initialized (LangGraph: {use_langgraph})")
    
    def _load_config(self, config_path: str) -> Dict:
        try:
            config_file = Path(config_path).resolve()
            if '..' in config_file.parts:
                logger.warning(f"Invalid config path: {config_path}")
                return self._default_config()
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {config_path}")
                return config
        except (IOError, yaml.YAMLError) as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        return self._default_config()
    
    def _default_config(self) -> Dict:
        return {
            'detection': {'threat_threshold': 5, 'terminate_threshold': 8},
            'monitoring': {'vt_timeout': 2, 'behavior_timeout': 0.5}
        }
    
    def _init_yara(self):
        if not self.config.get('yara', {}).get('enabled', False):
            logger.info("YARA scanning disabled in config")
            return
        
        try:
            from core.yara_scanner import YaraScanner
            rules_dir = self.config.get('yara', {}).get('rules_dir', 'yara_rules')
            self.yara_scanner = YaraScanner(rules_dir)
            info = self.yara_scanner.get_rules_info()
            logger.info(f"YARA scanner initialized: {info['rules_count']} rule files loaded")
        except Exception as e:
            logger.warning(f"YARA initialization failed: {e}")
            self.yara_scanner = None
    
    def _init_expert_system(self):
        if not self.config.get('expert_system', {}).get('enabled', True):
            logger.info("Expert system disabled in config")
            return
        
        try:
            from core.expert_system import ThreatExpertSystem
            self.expert_system = ThreatExpertSystem(self.config)
            logger.info("Expert system initialized")
        except Exception as e:
            logger.warning(f"Expert system initialization failed: {e}")
            self.expert_system = None
    
    def _init_langgraph(self):
        try:
            from core.langgraph_wrapper import LangGraphOrchestrator
            self.langgraph_orchestrator = LangGraphOrchestrator(self)
            logger.info("LangGraph orchestrator initialized")
        except Exception as e:
            logger.warning(f"LangGraph initialization failed: {e}")
            self.langgraph_orchestrator = None
            self.use_langgraph = False
    
    def log_message(self, from_agent: str, to_agent: str, message: str):
        msg = {
            'from_agent': from_agent,
            'to_agent': to_agent,
            'message': message,
            'timestamp': time.time()
        }
        self.messages.append(msg)
        logger.debug(f"[{from_agent}] -> [{to_agent}]: {message}")
    
    def analyze_process(self, proc_name: str, path: str, cmdline: str, pid: int) -> Dict[str, Any]:
        self.messages = []
        
        if self.use_langgraph and self.langgraph_orchestrator:
            logger.info(f"Analyzing process with LangGraph: {proc_name} (PID: {pid})")
            try:
                return self.langgraph_orchestrator.analyze_process(proc_name, path, cmdline, pid)
            except Exception as e:
                logger.error(f"LangGraph analysis failed: {e}, falling back to direct")
                self.use_langgraph = False
        
        logger.info(f"Analyzing process: {proc_name} (PID: {pid})")
        
        try:
            self.log_message("System", "DetectionAgent", f"Analyzing: {proc_name}")
            detection = self._run_detection(proc_name, path, cmdline)
            self.log_message("DetectionAgent", "System", f"Threat level: {detection['threat_level']}/10")
            
            intelligence = self._run_intelligence(detection, pid, proc_name, path, cmdline)
            
            self.log_message("System", "AnalystAgent", "Generating analysis")
            analysis = self._run_analysis(detection, intelligence)
            self.log_message("AnalystAgent", "System", f"Severity: {analysis['severity']}")
            
            self.log_message("System", "CoordinatorAgent", "Determining action")
            action = self._run_coordinator(detection, intelligence, analysis)
            self.log_message("CoordinatorAgent", "System", f"Action: {action}")
            
            self.log_message("System", "ResponseAgent", f"Executing: {action}")
            response = {'action': action, 'success': True}
            self.log_message("ResponseAgent", "System", "Complete")
            
            logger.info(f"Analysis complete: {proc_name} -> {action}")
            
            return {
                'detection_result': detection,
                'intelligence_result': intelligence,
                'analysis_result': analysis,
                'final_action': action,
                'response_result': response,
                'messages': self.messages
            }
        
        except Exception as e:
            logger.error(f"Analysis failed for {proc_name}: {e}", exc_info=True)
            return self._fallback_analysis(proc_name, path, cmdline)
    
    def _is_trusted_path(self, file_path: str) -> bool:
        """Check if file is in trusted path"""
        if not file_path:
            return False
        
        file_path_lower = file_path.lower()
        trusted_paths = self.config.get('paths', {}).get('trusted_paths', [])
        
        for trusted_path in trusted_paths:
            if file_path_lower.startswith(trusted_path.lower()):
                return True
        
        return False
    
    def _run_detection(self, proc_name: str, path: str, cmdline: str) -> Dict:
        try:
            # CRITICAL: Check trusted paths FIRST
            if self._is_trusted_path(path):
                logger.info(f"Trusted path: {path}")
                return {
                    'process_name': proc_name,
                    'path': path,
                    'threat_level': 0,
                    'is_suspicious': False,
                    'reasons': ['Trusted path'],
                    'yara_matches': [],
                    'yara_score': 0,
                    'mitre_techniques': []
                }
            
            threat_level = self._calculate_threat_level(proc_name, path, cmdline)
            reasons = self._get_threat_reasons(proc_name, path, cmdline)
            yara_matches = []
            yara_score = 0
            mitre_techniques = []
            
            is_trusted = threat_level == 0 and reasons == ['Trusted location']
            
            if self.config.get('yara', {}).get('enabled', False) and not is_trusted:
                yara_result = self._scan_with_yara(path)
                yara_matches = yara_result.get('matches', [])
                yara_score = yara_result.get('threat_score', 0)
                
                if yara_matches:
                    for match in yara_matches:
                        reasons.append(f"YARA: {match['rule']} ({match['severity']})")
                        if match.get('mitre'):
                            mitre_techniques.append(match['mitre'])
                    
                    threat_level = min(threat_level + yara_score, 10)
            
            threshold = self.config.get('detection', {}).get('threat_threshold', 5)
            is_suspicious = threat_level >= threshold
            
            return {
                'process_name': proc_name,
                'path': path,
                'threat_level': threat_level,
                'is_suspicious': is_suspicious,
                'reasons': reasons,
                'yara_matches': yara_matches,
                'yara_score': yara_score,
                'mitre_techniques': list(set(mitre_techniques))
            }
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return {
                'process_name': proc_name,
                'path': path,
                'threat_level': 0,
                'is_suspicious': False,
                'reasons': ['Detection error'],
                'yara_matches': [],
                'yara_score': 0,
                'mitre_techniques': []
            }
    
    def _run_intelligence(self, detection: Dict, pid: int, proc_name: str, path: str, cmdline: str) -> Dict:
        intelligence = {'threat_score': 0, 'is_known_malware': False, 'behaviors': [], 'behavior_score': 0, 'malwarebazaar': {}}
        
        if not detection.get('is_suspicious', False):
            return intelligence
        
        threat_level = detection.get('threat_level', 0)
        self.log_message("System", "IntelligenceAgent", f"Checking intelligence (threat: {threat_level})")
        
        try:
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                vt_result, behavior = loop.run_until_complete(
                    self._run_intelligence_async(path, pid, proc_name, cmdline)
                )
                
                intelligence.update(vt_result)
                intelligence['behaviors'] = behavior['behaviors']
                intelligence['behavior_score'] = behavior['behavior_threat_score']
                
                # Query MalwareBazaar if threat >= 5
                if threat_level >= 5 and vt_result.get('file_hash'):
                    from core.malwarebazaar_client import MalwareBazaarClient
                    mb_client = MalwareBazaarClient()
                    mb_response = mb_client.query_file_hash(vt_result['file_hash'])
                    mb_parsed = mb_client.parse_response(mb_response)
                    mb_score = mb_client.calculate_threat_score(mb_response)
                    intelligence['malwarebazaar'] = {
                        'verdict': mb_parsed['verdict'],
                        'malware_family': mb_parsed['malware_family'],
                        'tags': mb_parsed['tags'],
                        'score': mb_score
                    }
                    if mb_parsed['verdict'] == 'malicious':
                        intelligence['is_known_malware'] = True
                        logger.warning(f"MalwareBazaar: {mb_parsed['malware_family']} detected")
                
                mb_score = intelligence.get('malwarebazaar', {}).get('score', 0)
                self.log_message("IntelligenceAgent", "System", 
                               f"VT:{vt_result.get('threat_score', 0)} MB:{mb_score} Behavior:{behavior['behavior_threat_score']}")
            finally:
                if loop:
                    loop.close()
        
        except Exception as e:
            logger.error(f"Intelligence gathering failed: {e}")
            self.log_message("IntelligenceAgent", "System", "Error - using defaults")
        
        return intelligence
    
    async def _run_intelligence_async(self, path: str, pid: int, proc_name: str, cmdline: str):
        vt_timeout = self.config.get('monitoring', {}).get('vt_timeout', 2)
        behavior_timeout = self.config.get('monitoring', {}).get('behavior_timeout', 0.5)
        
        vt_task = asyncio.create_task(self._check_virustotal_async(path, vt_timeout))
        behavior_task = asyncio.create_task(self._analyze_behavior_async(pid, proc_name, path, cmdline, behavior_timeout))
        
        vt_result, behavior = await asyncio.gather(vt_task, behavior_task, return_exceptions=True)
        
        if isinstance(vt_result, Exception):
            logger.warning(f"VirusTotal check failed: {vt_result}")
            vt_result = {'threat_score': 0, 'is_known_malware': False}
        
        if isinstance(behavior, Exception):
            logger.warning(f"Behavior analysis failed: {behavior}")
            behavior = {'behaviors': [], 'behavior_threat_score': 0, 'is_suspicious': False}
        
        return vt_result, behavior
    
    async def _check_virustotal_async(self, path: str, timeout: int):
        return await asyncio.wait_for(
            asyncio.to_thread(self._check_virustotal, path, timeout),
            timeout=timeout
        )
    
    async def _analyze_behavior_async(self, pid: int, proc_name: str, path: str, cmdline: str, timeout: float):
        return await asyncio.wait_for(
            asyncio.to_thread(self._analyze_behavior, pid, proc_name, path, cmdline),
            timeout=timeout
        )
    
    def _run_analysis(self, detection: Dict, intelligence: Dict) -> Dict:
        if self.expert_system:
            try:
                return self.expert_system.analyze(detection, intelligence)
            except Exception as e:
                logger.error(f"Expert system failed: {e}")
        
        threat_level = detection.get('threat_level', 0)
        reasons = detection.get('reasons', [])
        return self._rule_based_analysis(threat_level, reasons)
    
    def _run_coordinator(self, detection: Dict, intelligence: Dict, analysis: Dict) -> str:
        try:
            if self.expert_system:
                detection_threat = detection.get('threat_level', 0)
                expert_threat = analysis.get('threat_score', 0)
                threat_score = max(detection_threat, expert_threat)
                is_known_malware = intelligence.get('is_known_malware', False)
                return self.expert_system.determine_action(threat_score, is_known_malware)
            
            return self._determine_action(detection, intelligence, analysis)
        except Exception as e:
            logger.error(f"Coordinator failed: {e}")
            threat_level = detection.get('threat_level', 0)
            if threat_level >= 8:
                return 'terminate_permanent'
            elif threat_level >= 5:
                return 'monitor'
            else:
                return 'allow'
    
    def _fallback_analysis(self, proc_name: str, path: str, cmdline: str) -> Dict:
        logger.warning(f"Using fallback analysis for {proc_name}")
        
        try:
            threat_level = 5 if path and any(x in path.lower() for x in ['temp', 'downloads']) else 0
            action = 'monitor' if threat_level >= 5 else 'allow'
            
            return {
                'detection_result': {
                    'process_name': proc_name,
                    'path': path,
                    'threat_level': threat_level,
                    'is_suspicious': threat_level >= 5,
                    'reasons': ['Fallback analysis']
                },
                'intelligence_result': {'threat_score': 0, 'is_known_malware': False, 'behaviors': [], 'behavior_score': 0},
                'analysis_result': {'summary': 'Analysis failed, using fallback', 'severity': 'Medium', 'ai_used': 'Fallback'},
                'final_action': action,
                'response_result': {'action': action, 'success': True},
                'messages': self.messages
            }
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return {
                'detection_result': {'process_name': proc_name, 'path': path, 'threat_level': 0, 'is_suspicious': False, 'reasons': ['Error']},
                'intelligence_result': {'threat_score': 0, 'is_known_malware': False, 'behaviors': [], 'behavior_score': 0},
                'analysis_result': {'summary': 'Error', 'severity': 'Low', 'ai_used': 'None'},
                'final_action': 'allow',
                'response_result': {'action': 'allow', 'success': False},
                'messages': self.messages
            }
    
    def _calculate_threat_level(self, proc_name: str, path: str, cmdline: str) -> int:
        proc_lower = proc_name.lower()
        path_lower = path.lower()
        cmd_lower = cmdline.lower()
        
        # Get trusted paths from config
        trusted_paths = self.config.get('paths', {}).get('trusted_paths', [
            'c:\\windows\\',
            'c:\\program files\\',
            'c:\\program files (x86)\\',
            '/usr/bin/', '/usr/sbin/', '/bin/', '/sbin/'
        ])
        
        # Normalize paths
        trusted_paths = [p.lower() for p in trusted_paths]
        in_trusted_path = any(trusted in path_lower for trusted in trusted_paths)
        
        score = 0
        
        # Suspicious locations (only if NOT in trusted path)
        if not in_trusted_path:
            if 'temp' in path_lower or 'tmp' in path_lower: score += 2
            if 'downloads' in path_lower: score += 1
            if 'appdata\\roaming' in path_lower: score += 1
            if 'appdata\\local\\temp' in path_lower: score += 2
        
        # Known malware names
        if proc_lower in ['encryptor.exe', 'locker.exe', 'crypt.exe', 'ransomware.exe']: score += 7
        if proc_lower in ['keylogger.exe', 'stealer.exe', 'logger.exe']: score += 6
        
        rat_names = ['rat.exe', 'njrat.exe', 'darkcomet.exe', 'cybergate.exe', 'poison.exe', 'blackshades.exe', 'remcos.exe', 'asyncrat.exe']
        if proc_lower in rat_names: score += 8
        
        # Suspicious keywords
        if 'suspicious' in proc_lower: score += 3
        if 'hack' in proc_lower or 'crack' in proc_lower: score += 3
        if 'backdoor' in proc_lower or 'trojan' in proc_lower: score += 5
        
        # Suspicious command patterns
        if 'powershell' in proc_lower and '-enc' in cmd_lower: score += 4
        if 'powershell' in proc_lower and ('-nop' in cmd_lower or '-w hidden' in cmd_lower): score += 3
        if 'cmd' in proc_lower and ('&' in cmd_lower or '|' in cmd_lower) and not in_trusted_path: score += 2
        
        return min(score, 10)
    
    def _get_threat_reasons(self, proc_name: str, path: str, cmdline: str) -> list:
        proc_lower = proc_name.lower()
        path_lower = path.lower()
        cmd_lower = cmdline.lower()
        
        # Get trusted paths from config
        trusted_paths = self.config.get('paths', {}).get('trusted_paths', [
            'c:\\windows\\',
            'c:\\program files\\',
            'c:\\program files (x86)\\',
            '/usr/bin/', '/usr/sbin/', '/bin/', '/sbin/'
        ])
        
        # Normalize paths
        trusted_paths = [p.lower() for p in trusted_paths]
        if any(trusted in path_lower for trusted in trusted_paths):
            return ['Trusted location']
        
        reasons = []
        
        if 'temp' in path_lower or 'tmp' in path_lower: reasons.append("Temp directory")
        if 'downloads' in path_lower: reasons.append("Downloads folder")
        if 'appdata\\roaming' in path_lower: reasons.append("AppData\\Roaming")
        
        if proc_lower in ['encryptor.exe', 'locker.exe', 'crypt.exe', 'ransomware.exe']: reasons.append("Ransomware name")
        if proc_lower in ['keylogger.exe', 'stealer.exe', 'logger.exe']: reasons.append("Keylogger/Stealer")
        
        rat_names = ['rat.exe', 'njrat.exe', 'darkcomet.exe', 'cybergate.exe', 'poison.exe', 'blackshades.exe', 'remcos.exe', 'asyncrat.exe']
        if proc_lower in rat_names: reasons.append("Known RAT")
        
        if 'suspicious' in proc_lower: reasons.append("Suspicious name")
        if 'hack' in proc_lower or 'crack' in proc_lower: reasons.append("Hacking tool")
        if 'backdoor' in proc_lower or 'trojan' in proc_lower: reasons.append("Trojan/Backdoor")
        
        if 'powershell' in proc_lower and '-enc' in cmd_lower: reasons.append("Encoded PowerShell")
        if 'cmd' in proc_lower and ('&' in cmd_lower or '|' in cmd_lower): reasons.append("Command chaining")
        
        return reasons if reasons else ["Heuristic analysis"]
    
    def _check_virustotal(self, path: str, timeout: int = 2) -> Dict:
        try:
            from tools.virustotal_tool import VirusTotalTool
            from tools.security_tools import SecurityTools
            
            if not path or not path.endswith('.exe'):
                return {'threat_score': 0, 'is_known_malware': False, 'file_hash': None}
            
            vt = VirusTotalTool()
            file_hash = SecurityTools.calculate_file_hash(path)
            
            if file_hash:
                result = vt.query_file_hash(file_hash)
                malicious = result.get('malicious', 0)
                score = min((malicious / 5) * 10, 10) if malicious > 0 else 0
                
                return {
                    'threat_score': score,
                    'is_known_malware': malicious >= 5,
                    'detections': malicious,
                    'file_hash': file_hash
                }
        except:
            pass
        
        return {'threat_score': 0, 'is_known_malware': False, 'file_hash': None}
    
    def _analyze_behavior(self, pid: int, proc_name: str, path: str, cmdline: str) -> Dict:
        try:
            from tools.behavior_monitor import BehaviorMonitor
            monitor = BehaviorMonitor()
            return monitor.analyze_process_behavior(pid, proc_name, path, cmdline)
        except:
            return {'behaviors': [], 'behavior_threat_score': 0, 'is_suspicious': False}
    
    def _scan_with_yara(self, filepath: str) -> Dict:
        if not self.yara_scanner:
            return {'matches': [], 'threat_score': 0}
        
        if not filepath or not filepath.endswith('.exe'):
            return {'matches': [], 'threat_score': 0}
        
        try:
            from core.resilience import resilience
            yara_config = self.config.get('yara', {})
            timeout = yara_config.get('scan_timeout', 5)
            
            result = resilience.call_with_resilience(
                self.yara_scanner.scan_file,
                filepath,
                timeout=timeout,
                config=yara_config,
                max_attempts=2,
                circuit_breaker_name='yara'
            )
            return result
        except Exception as e:
            logger.debug(f"YARA scan failed: {e}")
            return {'matches': [], 'threat_score': 0}
    
    def _rule_based_analysis(self, threat_level: int, reasons: list) -> Dict:
        if threat_level >= 8:
            return {
                'summary': f"Critical threat detected. {', '.join(reasons[:2])}. Immediate termination recommended.",
                'severity': 'Critical'
            }
        elif threat_level >= 5:
            return {
                'summary': f"Suspicious activity. {', '.join(reasons[:2])}. Recommend termination.",
                'severity': 'High'
            }
        elif threat_level >= 3:
            return {
                'summary': f"Low-level suspicious behavior. {', '.join(reasons[:1])}. Monitor recommended.",
                'severity': 'Medium'
            }
        else:
            return {
                'summary': "Minimal threat. Process appears safe.",
                'severity': 'Low'
            }
    
    def _determine_action(self, detection: Dict, intelligence: Dict, analysis: Dict) -> str:
        threat_level = detection.get('threat_level', 0)
        severity = analysis.get('severity', 'Low')
        is_known_malware = intelligence.get('is_known_malware', False)
        behavior_score = intelligence.get('behavior_score', 0)
        
        total_threat = threat_level + behavior_score
        
        if is_known_malware or total_threat >= 12:
            return 'terminate_permanent'
        elif total_threat >= 8 or threat_level >= 5 or severity == 'High':
            return 'terminate_temporary'
        elif total_threat >= 5 or threat_level >= 3:
            return 'monitor'
        else:
            return 'allow'
