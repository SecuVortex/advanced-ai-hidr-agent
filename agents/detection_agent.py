"""
Detection Agent
Monitors and detects threats using heuristic analysis and behavioral patterns.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from tools.security_tools import SecurityTools
from tools.process_tools import ProcessTools
from agents.config import Config


class DetectionAgent(BaseAgent):
    """Agent responsible for threat detection"""
    
    def __init__(self):
        super().__init__(name="DetectionAgent", role="Threat Detection Specialist")
        self.security_tools = SecurityTools()
        self.process_tools = ProcessTools()
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data for threats
        
        Args:
            data: Event data to analyze
            
        Returns:
            Detection results
        """
        event_type = data.get("event_type")
        
        if event_type == "process":
            return self.analyze_process(
                data.get("name", ""),
                data.get("path", ""),
                data.get("cmdline", ""),
                data.get("pid", 0)
            )
        elif event_type == "file":
            return self.analyze_file(
                data.get("filepath", ""),
                data.get("old_hash")
            )
        else:
            return {"error": "Unknown event type"}
    
    def analyze_process(self, proc_name: str, path: str, cmdline: str, pid: int) -> Dict[str, Any]:
        """
        Analyze process for suspicious behavior
        
        Args:
            proc_name: Process name
            path: Process executable path
            cmdline: Command line arguments
            pid: Process ID
            
        Returns:
            Analysis results with threat level and reasons
        """
        self.log_info(f"Analyzing process: {proc_name} (PID: {pid})")
        
        indicators = {}
        reasons = []
        threat_level = 0
        
        # Check path
        if self.security_tools.is_suspicious_path(path):
            indicators["suspicious_path"] = True
            reasons.append(f"Launched from suspicious location: {path}")
            threat_level += 3
        
        # Check name
        if self.security_tools.is_suspicious_name(proc_name):
            indicators["suspicious_name"] = True
            reasons.append(f"Malicious process name pattern: {proc_name}")
            threat_level += 5
        
        # Check command line
        if "encodedcommand" in cmdline.lower() or "-enc" in cmdline.lower():
            indicators["encoded_command"] = True
            reasons.append("Encoded PowerShell command detected")
            threat_level += 4
        
        # Check for system process impersonation
        system_processes = ["svchost.exe", "explorer.exe", "winlogon.exe", "csrss.exe"]
        if proc_name.lower() in system_processes and not path.lower().startswith("c:\\windows"):
            reasons.append(f"System process impersonation: {proc_name}")
            threat_level += 6
        
        # Get process details
        proc_info = self.process_tools.get_process_info(pid)
        
        # Calculate final threat score
        threat_level = min(threat_level, Config.MAX_THREAT_SCORE)
        is_suspicious = threat_level >= Config.SUSPICIOUS_THRESHOLD
        
        result = {
            "agent": self.name,
            "threat_level": threat_level,
            "is_suspicious": is_suspicious,
            "reasons": reasons,
            "indicators": indicators,
            "process_info": proc_info or {},
            "recommendation": self._get_recommendation(threat_level)
        }
        
        if is_suspicious:
            self.log_warning(f"Suspicious process detected: {proc_name} (Threat: {threat_level}/10)")
        else:
            self.log_info(f"Process appears normal: {proc_name}")
        
        return result
    
    def analyze_file(self, filepath: str, old_hash: str = None) -> Dict[str, Any]:
        """
        Analyze file for threats
        
        Args:
            filepath: Path to file
            old_hash: Previous file hash (for integrity check)
            
        Returns:
            Analysis results
        """
        self.log_info(f"Analyzing file: {filepath}")
        
        # Calculate file hash
        file_hash = self.security_tools.calculate_file_hash(filepath)
        
        if not file_hash:
            return {
                "agent": self.name,
                "error": "Failed to calculate file hash",
                "is_suspicious": False
            }
        
        # Check for modification
        is_modified = old_hash and file_hash != old_hash
        
        result = {
            "agent": self.name,
            "file_hash": file_hash,
            "is_modified": is_modified,
            "is_suspicious": is_modified,
            "threat_level": 5 if is_modified else 0,
            "reasons": ["File integrity violation - hash mismatch"] if is_modified else [],
            "recommendation": "quarantine" if is_modified else "allow"
        }
        
        if is_modified:
            self.log_warning(f"File modified: {filepath}")
        
        return result
    
    def _get_recommendation(self, threat_level: int) -> str:
        """
        Get action recommendation based on threat level
        
        Args:
            threat_level: Threat score (0-10)
            
        Returns:
            Recommended action
        """
        if threat_level >= Config.CRITICAL_THRESHOLD:
            return "terminate_permanent"
        elif threat_level >= Config.SUSPICIOUS_THRESHOLD:
            return "terminate_temporary"
        else:
            return "monitor"
