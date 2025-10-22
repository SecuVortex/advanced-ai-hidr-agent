"""
Response Agent
Executes security responses including process termination and file quarantine.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from tools.process_tools import ProcessTools
from tools.file_tools import FileTools
from agents.config import Config


class ResponseAgent(BaseAgent):
    """Agent responsible for incident response actions"""
    
    def __init__(self, quarantine_dir: str = None):
        super().__init__(name="ResponseAgent", role="Incident Response Specialist")
        self.process_tools = ProcessTools()
        self.file_tools = FileTools()
        self.quarantine_dir = quarantine_dir or str(Config.QUARANTINE_DIR)
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute response action
        
        Args:
            data: Action data (action type and target)
            
        Returns:
            Response results
        """
        action = data.get("action", "monitor")
        target = data.get("target", {})
        
        return self.execute_action(action, target)
    
    def execute_action(self, action: str, target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute security action
        
        Args:
            action: Action to execute (allow, monitor, terminate_temporary, terminate_permanent, quarantine)
            target: Target data (process or file info)
            
        Returns:
            Execution results
        """
        self.log_info(f"Executing action: {action}")
        
        if action == "allow":
            return self._action_allow(target)
        elif action == "monitor":
            return self._action_monitor(target)
        elif action == "terminate_temporary":
            return self._action_terminate_temporary(target)
        elif action == "terminate_permanent":
            return self._action_terminate_permanent(target)
        elif action == "quarantine":
            return self._action_quarantine(target)
        else:
            return {
                "agent": self.name,
                "action": action,
                "success": False,
                "message": f"Unknown action: {action}"
            }
    
    def _action_allow(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Allow process/file (no action)"""
        self.log_info("Action: ALLOW - No action taken")
        return {
            "agent": self.name,
            "action": "allow",
            "success": True,
            "message": "Process/file allowed by user decision"
        }
    
    def _action_monitor(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor process/file (no immediate action)"""
        self.log_info("Action: MONITOR - Continuing surveillance")
        return {
            "agent": self.name,
            "action": "monitor",
            "success": True,
            "message": "Continuing to monitor for suspicious activity"
        }
    
    def _action_terminate_temporary(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate process temporarily (can restart)"""
        pid = target.get("pid")
        
        if not pid:
            return {
                "agent": self.name,
                "action": "terminate_temporary",
                "success": False,
                "message": "No process ID provided"
            }
        
        self.log_info(f"Terminating process temporarily: PID {pid}")
        success = self.process_tools.terminate_process(pid, timeout=Config.PROCESS_TIMEOUT)
        
        if success:
            self.log_info(f"Process {pid} terminated successfully")
            return {
                "agent": self.name,
                "action": "terminate_temporary",
                "success": True,
                "message": f"Process {pid} terminated (can restart)"
            }
        else:
            self.log_error(f"Failed to terminate process {pid}")
            return {
                "agent": self.name,
                "action": "terminate_temporary",
                "success": False,
                "message": f"Failed to terminate process {pid}"
            }
    
    def _action_terminate_permanent(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate process and quarantine executable"""
        pid = target.get("pid")
        exe_path = target.get("path")
        
        if not pid:
            return {
                "agent": self.name,
                "action": "terminate_permanent",
                "success": False,
                "message": "No process ID provided"
            }
        
        self.log_info(f"Terminating process permanently: PID {pid}")
        
        # Terminate process
        terminated = self.process_tools.terminate_process(pid, timeout=Config.PROCESS_TIMEOUT)
        
        if not terminated:
            # Try force kill
            terminated = self.process_tools.kill_process(pid)
        
        # Quarantine executable if path provided
        quar_path = None
        if exe_path and Config.QUARANTINE_ENABLED:
            quar_path = self.file_tools.quarantine_file(exe_path, self.quarantine_dir)
        
        if terminated:
            message = f"Process {pid} terminated"
            if quar_path:
                message += f" and executable quarantined to {quar_path}"
            
            self.log_info(message)
            return {
                "agent": self.name,
                "action": "terminate_permanent",
                "success": True,
                "message": message,
                "quarantine_path": quar_path
            }
        else:
            self.log_error(f"Failed to terminate process {pid}")
            return {
                "agent": self.name,
                "action": "terminate_permanent",
                "success": False,
                "message": f"Failed to terminate process {pid}"
            }
    
    def _action_quarantine(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Quarantine file"""
        filepath = target.get("filepath")
        
        if not filepath:
            return {
                "agent": self.name,
                "action": "quarantine",
                "success": False,
                "message": "No file path provided"
            }
        
        if not Config.QUARANTINE_ENABLED:
            return {
                "agent": self.name,
                "action": "quarantine",
                "success": False,
                "message": "Quarantine is disabled in configuration"
            }
        
        self.log_info(f"Quarantining file: {filepath}")
        quar_path = self.file_tools.quarantine_file(filepath, self.quarantine_dir)
        
        if quar_path:
            self.log_info(f"File quarantined to: {quar_path}")
            return {
                "agent": self.name,
                "action": "quarantine",
                "success": True,
                "message": f"File quarantined to {quar_path}",
                "quarantine_path": quar_path
            }
        else:
            self.log_error(f"Failed to quarantine file: {filepath}")
            return {
                "agent": self.name,
                "action": "quarantine",
                "success": False,
                "message": f"Failed to quarantine file: {filepath}"
            }
