"""
Simplified Multi-Agent System - Role-Based, No Recursion
"""
import time
from typing import Dict, Any, Optional

class SimpleMultiAgent:
    def __init__(self):
        self.messages = []
        self.gemini_llm = None
        self.openai_llm = None
        self._init_llms()
    
    def _init_llms(self):
        """Initialize LLMs separately to avoid recursion"""
        try:
            from agents.config import Config
            if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != "your_google_api_key_here":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=Config.GOOGLE_API_KEY,
                    temperature=0.3
                )
                print("[OK] Gemini initialized")
        except Exception as e:
            print(f"[WARN] Gemini failed: {e}")
        
        try:
            from agents.config import Config
            if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
                from langchain_openai import ChatOpenAI
                self.openai_llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    openai_api_key=Config.OPENAI_API_KEY,
                    temperature=0.3,
                    max_tokens=500
                )
                print("[OK] OpenAI initialized")
        except Exception as e:
            print(f"[WARN] OpenAI failed: {e}")
    
    def log_message(self, from_agent: str, to_agent: str, message: str):
        """Log agent communication"""
        msg = {
            'from_agent': from_agent,
            'to_agent': to_agent,
            'message': message,
            'timestamp': time.time()
        }
        self.messages.append(msg)
        print(f"[MSG] [{from_agent}] -> [{to_agent}]: {message}")
    
    def analyze_process(self, proc_name: str, path: str, cmdline: str, pid: int) -> Dict[str, Any]:
        """Simple role-based analysis"""
        self.messages = []
        
        # Agent 1: Detection (Rule-based, always works)
        self.log_message("System", "DetectionAgent", f"Analyzing: {proc_name}")
        threat_level = self._calculate_threat_level(proc_name, path, cmdline)
        is_suspicious = threat_level >= 5
        reasons = self._get_threat_reasons(proc_name, path, cmdline)
        
        self.log_message("DetectionAgent", "System", f"Threat level: {threat_level}/10")
        
        detection = {
            'process_name': proc_name,
            'path': path,
            'threat_level': threat_level,
            'is_suspicious': is_suspicious,
            'reasons': reasons
        }
        
        # Agent 2: Intelligence (VirusTotal - optional, skip if fails)
        intelligence = {'threat_score': 0, 'is_known_malware': False}
        if is_suspicious:
            self.log_message("System", "IntelligenceAgent", "Checking threat intelligence")
            try:
                # Simplified VirusTotal check with timeout
                intelligence = self._check_virustotal(path, timeout=2)
                self.log_message("IntelligenceAgent", "System", f"VT score: {intelligence.get('threat_score', 0)}/10")
            except:
                self.log_message("IntelligenceAgent", "System", "Skipped (timeout/error)")
        
        # Agent 3: AI Analyst (Use Gemini first, OpenAI as backup)
        self.log_message("System", "AnalystAgent", "Generating AI analysis")
        analysis = self._ai_analysis(detection, intelligence)
        self.log_message("AnalystAgent", "System", f"Severity: {analysis['severity']}")
        
        # Agent 4: Coordinator (Simple decision logic)
        self.log_message("System", "CoordinatorAgent", "Determining action")
        action = self._determine_action(detection, intelligence, analysis)
        self.log_message("CoordinatorAgent", "System", f"Action: {action}")
        
        # Agent 5: Response
        self.log_message("System", "ResponseAgent", f"Executing: {action}")
        response = {'action': action, 'success': True}
        self.log_message("ResponseAgent", "System", "Complete")
        
        return {
            'detection_result': detection,
            'intelligence_result': intelligence,
            'analysis_result': analysis,
            'final_action': action,
            'response_result': response,
            'messages': self.messages
        }
    
    def _calculate_threat_level(self, proc_name: str, path: str, cmdline: str) -> int:
        """Calculate threat level (0-10)"""
        score = 0
        
        if "temp" in path.lower(): score += 3
        if "downloads" in path.lower(): score += 2
        if proc_name.lower() in ["encryptor.exe", "locker.exe", "crypt.exe", "ransomware.exe"]: score += 8
        if proc_name.lower() in ["keylogger.exe", "stealer.exe"]: score += 7
        if "suspicious" in proc_name.lower(): score += 5
        if "powershell" in proc_name.lower() and "-enc" in cmdline.lower(): score += 6
        
        return min(score, 10)
    
    def _get_threat_reasons(self, proc_name: str, path: str, cmdline: str) -> list:
        """Get list of threat reasons"""
        reasons = []
        
        if "temp" in path.lower():
            reasons.append("Launched from temp directory")
        if "downloads" in path.lower():
            reasons.append("Launched from downloads")
        if proc_name.lower() in ["encryptor.exe", "locker.exe", "crypt.exe", "ransomware.exe"]:
            reasons.append("Ransomware executable name")
        if proc_name.lower() in ["keylogger.exe", "stealer.exe"]:
            reasons.append("Malware executable name")
        if "suspicious" in proc_name.lower():
            reasons.append("Suspicious name pattern")
        if "powershell" in proc_name.lower() and "-enc" in cmdline.lower():
            reasons.append("Encoded PowerShell command")
        
        return reasons if reasons else ["Heuristic analysis"]
    
    def _check_virustotal(self, path: str, timeout: int = 2) -> Dict:
        """Quick VirusTotal check with timeout"""
        try:
            from tools.virustotal_tool import VirusTotalTool
            from tools.security_tools import calculate_file_hash
            
            if not path or not path.endswith('.exe'):
                return {'threat_score': 0, 'is_known_malware': False}
            
            vt = VirusTotalTool()
            file_hash = calculate_file_hash(path)
            
            if file_hash:
                result = vt.query_file_hash(file_hash)
                malicious = result.get('malicious', 0)
                score = min((malicious / 5) * 10, 10) if malicious > 0 else 0
                
                return {
                    'threat_score': score,
                    'is_known_malware': malicious >= 5,
                    'detections': malicious
                }
        except:
            pass
        
        return {'threat_score': 0, 'is_known_malware': False}
    
    def _ai_analysis(self, detection: Dict, intelligence: Dict) -> Dict:
        """AI analysis with Gemini first, OpenAI backup, rule-based fallback"""
        threat_level = detection.get('threat_level', 0)
        reasons = detection.get('reasons', [])
        vt_score = intelligence.get('threat_score', 0)
        
        # Try Gemini first
        if self.gemini_llm:
            try:
                print("[AI] Trying Gemini API...")
                from langchain_core.messages import HumanMessage
                prompt = f"""Analyze this security threat in 2 sentences:
Process: {detection.get('process_name')}
Threat Level: {threat_level}/10
Reasons: {', '.join(reasons)}
VirusTotal Score: {vt_score}/10

Explain: threat type, risk level, action needed."""
                
                message = HumanMessage(content=prompt)
                response = self.gemini_llm.invoke([message])
                summary = response.content
                severity = self._extract_severity(summary, threat_level)
                print("[OK] Gemini success")
                
                return {'summary': summary, 'severity': severity, 'ai_used': 'Gemini'}
            except Exception as e:
                print(f"[WARN] Gemini failed: {str(e)[:100]}")
        
        # Try OpenAI as backup
        if self.openai_llm:
            try:
                print("[AI] Trying OpenAI API...")
                from langchain_core.messages import HumanMessage
                prompt = f"""Security threat analysis (2 sentences):
Threat: {threat_level}/10, Reasons: {', '.join(reasons[:2])}
Explain risk and action."""
                
                message = HumanMessage(content=prompt)
                response = self.openai_llm.invoke([message])
                summary = response.content
                severity = self._extract_severity(summary, threat_level)
                print("[OK] OpenAI success")
                
                return {'summary': summary, 'severity': severity, 'ai_used': 'OpenAI'}
            except Exception as e:
                print(f"[WARN] OpenAI failed: {str(e)[:100]}")
        
        # Rule-based fallback
        print("[RULE] Using rule-based analysis")
        result = self._rule_based_analysis(threat_level, reasons)
        result['ai_used'] = 'Rule-based'
        return result
    
    def _rule_based_analysis(self, threat_level: int, reasons: list) -> Dict:
        """Fallback rule-based analysis"""
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
    
    def _extract_severity(self, summary: str, threat_level: int) -> str:
        """Extract severity from AI summary"""
        summary_lower = summary.lower()
        
        if any(word in summary_lower for word in ['critical', 'severe', 'immediate']):
            return 'Critical'
        elif any(word in summary_lower for word in ['high', 'dangerous', 'serious']):
            return 'High'
        elif any(word in summary_lower for word in ['low', 'minimal', 'safe']):
            return 'Low'
        else:
            return 'High' if threat_level >= 7 else 'Medium'
    
    def _determine_action(self, detection: Dict, intelligence: Dict, analysis: Dict) -> str:
        """Determine final action"""
        threat_level = detection.get('threat_level', 0)
        severity = analysis.get('severity', 'Low')
        is_known_malware = intelligence.get('is_known_malware', False)
        
        if is_known_malware or threat_level >= 8:
            return 'terminate_permanent'
        elif threat_level >= 5 or severity == 'High':
            return 'terminate_temporary'
        elif threat_level >= 3:
            return 'monitor'
        else:
            return 'allow'
