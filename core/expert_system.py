"""
Threat Expert System - Rule-based threat analysis
Replaces AI analyst with deterministic scoring
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger('HIDR.ExpertSystem')

class ThreatExpertSystem:
    """Rule-based expert system for threat analysis"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.weights = self.config.get('expert_system', {}).get('weights', {
            'yara': 3.0,
            'malwarebazaar': 3.5,
            'virustotal': 2.5,
            'behavioral': 1.5,
            'mitre': 2.0
        })
        logger.info(f"Expert system initialized with weights: {self.weights}")
    
    def analyze(self, detection: Dict, intelligence: Dict) -> Dict:
        """Main analysis method"""
        # Extract scores
        yara_score = detection.get('yara_score', 0)
        vt_score = intelligence.get('threat_score', 0)
        behavior_score = intelligence.get('behavior_score', 0)
        mitre_techniques = detection.get('mitre_techniques', [])
        mb_score = intelligence.get('malwarebazaar', {}).get('score', 0)
        
        # Calculate weighted threat score
        threat_score = self.calculate_threat_score(
            yara_score, vt_score, behavior_score, len(mitre_techniques), mb_score
        )
        
        # Determine severity
        severity = self.get_severity(threat_score)
        
        # Get reasoning
        reasoning = self.get_reasoning(detection, intelligence, threat_score)
        
        # Map MITRE techniques
        mitre_details = self.get_mitre_techniques(detection, intelligence)
        
        return {
            'summary': reasoning,
            'severity': severity,
            'threat_score': threat_score,
            'mitre_techniques': mitre_details,
            'ai_used': 'Expert System'
        }
    
    def calculate_threat_score(self, yara: float, vt: float, behavior: float, mitre_count: int, mb: float = 0) -> float:
        """Calculate weighted threat score (0-10)"""
        score = (
            (yara * self.weights['yara']) +
            (mb * self.weights['malwarebazaar']) +
            (vt * self.weights['virustotal']) +
            (behavior * self.weights['behavioral']) +
            (mitre_count * self.weights['mitre'])
        )
        
        # Normalize to 0-10 scale
        max_possible = (10 * self.weights['yara']) + (10 * self.weights['malwarebazaar']) + \
                       (10 * self.weights['virustotal']) + (10 * self.weights['behavioral']) + \
                       (5 * self.weights['mitre'])
        
        normalized = (score / max_possible) * 10 if max_possible > 0 else 0
        return min(round(normalized, 1), 10.0)
    
    def determine_action(self, threat_score: float, is_known_malware: bool = False) -> str:
        """Determine action based on threat score"""
        if is_known_malware or threat_score >= 8.0:
            return 'terminate_permanent'
        elif threat_score >= 6.0:
            return 'terminate_temporary'
        elif threat_score >= 3.0:
            return 'monitor'
        else:
            return 'allow'
    
    def get_severity(self, threat_score: float) -> str:
        """Map threat score to severity level"""
        if threat_score >= 8.0:
            return 'Critical'
        elif threat_score >= 6.0:
            return 'High'
        elif threat_score >= 3.0:
            return 'Medium'
        else:
            return 'Low'
    
    def get_reasoning(self, detection: Dict, intelligence: Dict, threat_score: float) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        # MalwareBazaar findings
        mb_data = intelligence.get('malwarebazaar', {})
        if mb_data.get('verdict') == 'malicious':
            family = mb_data.get('malware_family', 'Unknown')
            reasons.append(f"MalwareBazaar: {family} detected")
        
        # YARA findings
        yara_matches = detection.get('yara_matches', [])
        if yara_matches:
            rules = [m['rule'] for m in yara_matches[:2]]
            reasons.append(f"YARA detected: {', '.join(rules)}")
        
        # VirusTotal
        vt_score = intelligence.get('threat_score', 0)
        if vt_score > 5:
            detections = intelligence.get('detections', 0)
            reasons.append(f"VirusTotal: {detections} detections")
        
        # Behavioral
        behaviors = intelligence.get('behaviors', [])
        if behaviors:
            reasons.append(f"Suspicious behaviors: {', '.join(behaviors[:2])}")
        
        # MITRE
        mitre = detection.get('mitre_techniques', [])
        if mitre:
            reasons.append(f"MITRE: {', '.join(mitre[:2])}")
        
        # Detection reasons
        det_reasons = detection.get('reasons', [])
        if det_reasons and not reasons:
            reasons.extend(det_reasons[:2])
        
        if not reasons:
            reasons.append("Heuristic analysis")
        
        # Build summary
        severity = self.get_severity(threat_score)
        action = self.determine_action(threat_score, intelligence.get('is_known_malware', False))
        
        summary = f"{severity} threat (score: {threat_score}/10). {' | '.join(reasons)}. Recommended action: {action}."
        return summary
    
    def get_mitre_techniques(self, detection: Dict, intelligence: Dict) -> List[Dict[str, str]]:
        """Map indicators to MITRE ATT&CK techniques"""
        techniques = []
        seen = set()
        
        # From YARA rules
        for match in detection.get('yara_matches', []):
            mitre = match.get('mitre')
            if mitre and mitre not in seen:
                techniques.append({'id': mitre, 'source': 'YARA'})
                seen.add(mitre)
        
        # From detection reasons
        reasons = detection.get('reasons', [])
        mitre_map = {
            'Ransomware': 'T1486',
            'Keylogger': 'T1056.001',
            'RAT': 'T1219',
            'Encoded PowerShell': 'T1059.001',
            'Command chaining': 'T1059.003',
            'Temp directory': 'T1036',
            'Downloads folder': 'T1036'
        }
        
        for reason in reasons:
            for key, tid in mitre_map.items():
                if key.lower() in reason.lower() and tid not in seen:
                    techniques.append({'id': tid, 'source': 'Detection'})
                    seen.add(tid)
        
        # From behaviors
        behaviors = intelligence.get('behaviors', [])
        behavior_map = {
            'network': 'T1071',
            'file_creation': 'T1105',
            'registry': 'T1112',
            'process_injection': 'T1055'
        }
        
        for behavior in behaviors:
            for key, tid in behavior_map.items():
                if key in behavior.lower() and tid not in seen:
                    techniques.append({'id': tid, 'source': 'Behavior'})
                    seen.add(tid)
        
        return techniques[:5]  # Limit to top 5
