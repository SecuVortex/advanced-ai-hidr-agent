"""
Intelligence Agent
Queries external threat intelligence sources for reputation and IOC data.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from tools.virustotal_tool import VirusTotalTool


class IntelligenceAgent(BaseAgent):
    """Agent responsible for threat intelligence gathering"""
    
    def __init__(self):
        super().__init__(name="IntelligenceAgent", role="Threat Intelligence Specialist")
        self.vt_tool = VirusTotalTool()
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather threat intelligence
        
        Args:
            data: Data to analyze (must contain file_hash)
            
        Returns:
            Intelligence results
        """
        file_hash = data.get("file_hash")
        
        if not file_hash or file_hash.startswith("Error"):
            return {
                "agent": self.name,
                "skipped": True,
                "reason": "No valid file hash provided"
            }
        
        return self.enrich_file_analysis(file_hash)
    
    def enrich_file_analysis(self, file_hash: str) -> Dict[str, Any]:
        """
        Enrich file analysis with threat intelligence
        
        Args:
            file_hash: SHA256 file hash
            
        Returns:
            Enriched analysis with VirusTotal data
        """
        self.log_info(f"Querying threat intelligence for hash: {file_hash[:16]}...")
        
        # Query VirusTotal
        vt_result = self.vt_tool.query_file_hash(file_hash)
        
        # Calculate threat score
        threat_score = self.vt_tool.calculate_reputation_score(vt_result)
        is_known_malware = self.vt_tool.is_known_malware(vt_result)
        
        result = {
            "agent": self.name,
            "file_hash": file_hash,
            "virustotal": vt_result,
            "threat_score": threat_score,
            "is_known_malware": is_known_malware,
            "recommendation": self._get_recommendation(threat_score, is_known_malware)
        }
        
        if is_known_malware:
            self.log_warning(
                f"Known malware detected! VT detections: {vt_result.get('malicious', 0)}"
            )
        elif vt_result.get("error"):
            self.log_info(f"VirusTotal query: {vt_result['error']}")
        else:
            self.log_info(f"Threat score: {threat_score:.1f}/10")
        
        return result
    
    def _get_recommendation(self, threat_score: float, is_known_malware: bool) -> str:
        """
        Get recommendation based on intelligence
        
        Args:
            threat_score: Calculated threat score
            is_known_malware: Whether file is known malware
            
        Returns:
            Recommended action
        """
        if is_known_malware or threat_score >= 7.0:
            return "quarantine"
        elif threat_score >= 3.0:
            return "monitor"
        else:
            return "allow"
    
    def get_threat_context(self, threat_type: str) -> str:
        """
        Provide context about threat type
        
        Args:
            threat_type: Type of threat
            
        Returns:
            Context description
        """
        contexts = {
            "ransomware": "File encryption malware that demands ransom payment for decryption",
            "keylogger": "Malware that captures keystrokes to steal credentials and sensitive data",
            "trojan": "Malicious software disguised as legitimate that provides backdoor access",
            "rootkit": "System-level malware designed to hide its presence and maintain persistence",
            "spyware": "Software that secretly monitors and collects user information",
            "worm": "Self-replicating malware that spreads across networks",
            "backdoor": "Malware that provides unauthorized remote access to the system"
        }
        
        return contexts.get(threat_type.lower(), "Unknown threat type - requires further analysis")
