"""
Multi-Agent HIDR Monitor
Main interface for the multi-agent security system.
"""

from pathlib import Path
from typing import Dict, Any
from agents.orchestrator import MultiAgentOrchestrator
from agents.config import Config


class MultiAgentHIDR:
    """
    Multi-Agent Host Intrusion Detection & Response System
    
    Features:
        - 5 specialized agents working collaboratively
        - LangGraph orchestration
        - Human-in-the-loop decision making
        - AI-powered threat analysis
        - VirusTotal integration
        - Automated response actions
    
    Usage:
        >>> hidr = MultiAgentHIDR(require_human_approval=True)
        >>> result = hidr.analyze_process("suspicious.exe", "C:\\temp\\suspicious.exe", "", 1234)
        >>> print(result['final_action'])
    """
    
    def __init__(self, require_human_approval: bool = None):
        """
        Initialize Multi-Agent HIDR System
        
        Args:
            require_human_approval: Enable human-in-the-loop (default: from config)
        """
        self.base_path = Path.cwd()
        self.quarantine_dir = str(Config.QUARANTINE_DIR)
        self.human_approval_callback = None
        
        # Initialize orchestrator
        self.orchestrator = MultiAgentOrchestrator(
            quarantine_dir=self.quarantine_dir,
            require_human_approval=require_human_approval
        )
        
        self._print_banner()
    
    def _print_banner(self):
        """Print system initialization banner"""
        print("\n" + "="*70)
        print("🤖 MULTI-AGENT HIDR SYSTEM v2.0")
        print("="*70)
        print(f"✓ {self.orchestrator.detection_agent.role}")
        print(f"✓ {self.orchestrator.intelligence_agent.role}")
        print(f"✓ {self.orchestrator.response_agent.role}")
        print(f"✓ {self.orchestrator.analyst_agent.role}")
        print(f"✓ {self.orchestrator.coordinator_agent.role}")
        print(f"\n⚙️  Configuration:")
        print(f"   - LLM Provider: {Config.LLM_PROVIDER}")
        print(f"   - Human Approval: {'ENABLED ✓' if self.orchestrator.require_human_approval else 'DISABLED'}")
        print(f"   - Quarantine: {'ENABLED ✓' if Config.QUARANTINE_ENABLED else 'DISABLED'}")
        print("="*70 + "\n")
    
    def analyze_process(
        self,
        proc_name: str,
        path: str,
        cmdline: str,
        pid: int
    ) -> Dict[str, Any]:
        """
        Analyze process through multi-agent system
        
        Args:
            proc_name: Process name
            path: Process executable path
            cmdline: Command line arguments
            pid: Process ID
            
        Returns:
            Complete workflow results
        """
        target = {
            "name": proc_name,
            "path": path,
            "cmdline": cmdline,
            "pid": pid
        }
        
        if self.human_approval_callback:
            self.orchestrator.human_approval_callback = self.human_approval_callback
        
        return self.orchestrator.process_event("process", target)
    
    def analyze_file(self, filepath: str, old_hash: str = None) -> Dict[str, Any]:
        """
        Analyze file through multi-agent system
        
        Args:
            filepath: Path to file
            old_hash: Previous file hash (for integrity check)
            
        Returns:
            Complete workflow results
        """
        target = {
            "filepath": filepath,
            "old_hash": old_hash
        }
        
        return self.orchestrator.process_event("file", target)
    
    def print_agent_communication(self, result: Dict[str, Any]) -> None:
        """
        Display agent communication log
        
        Args:
            result: Workflow result containing messages
        """
        messages = result.get("messages", [])
        
        if not messages:
            print("No agent communication recorded.")
            return
        
        print("\n📨 AGENT COMMUNICATION LOG:")
        print("-" * 70)
        for i, msg in enumerate(messages, 1):
            print(f"{i}. [{msg['from_agent']}] → [{msg['to_agent']}]")
            print(f"   {msg['message']}")
        print("-" * 70)
    
    def print_summary(self, result: Dict[str, Any]) -> None:
        """
        Print workflow summary
        
        Args:
            result: Workflow result
        """
        print("\n📊 WORKFLOW SUMMARY:")
        print("-" * 70)
        print(f"Event Type: {result.get('event_type', 'Unknown')}")
        print(f"Final Action: {result.get('final_action', 'Unknown')}")
        
        # Detection summary
        detection = result.get("detection_result", {})
        print(f"\n🔍 Detection:")
        print(f"   Threat Level: {detection.get('threat_level', 0)}/10")
        print(f"   Suspicious: {detection.get('is_suspicious', False)}")
        
        # Intelligence summary
        intelligence = result.get("intelligence_result", {})
        if not intelligence.get("skipped"):
            print(f"\n🌐 Intelligence:")
            print(f"   Known Malware: {intelligence.get('is_known_malware', False)}")
            print(f"   Threat Score: {intelligence.get('threat_score', 0):.1f}/10")
        
        # Analysis summary
        analysis = result.get("analysis_result", {})
        print(f"\n🤖 AI Analysis:")
        print(f"   Severity: {analysis.get('severity', 'Unknown')}")
        print(f"   Summary: {analysis.get('summary', 'N/A')[:100]}...")
        
        # Response summary
        response = result.get("response_result", {})
        print(f"\n🛡️ Response:")
        print(f"   Success: {response.get('success', False)}")
        print(f"   Message: {response.get('message', 'N/A')}")
        
        # Execution time
        if result.get("workflow_start_time") and result.get("workflow_end_time"):
            exec_time = result["workflow_end_time"] - result["workflow_start_time"]
            print(f"\n⏱️  Execution Time: {exec_time:.2f}s")
        
        print("-" * 70)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Statistics dictionary
        """
        return self.orchestrator.coordinator_agent.get_workflow_summary()


if __name__ == "__main__":
    # Quick test
    print("🧪 Multi-Agent HIDR System - Quick Test\n")
    
    hidr = MultiAgentHIDR(require_human_approval=False)
    
    # Test suspicious process
    result = hidr.analyze_process(
        "ransomware.exe",
        "C:\\Users\\test\\AppData\\Local\\Temp\\ransomware.exe",
        "ransomware.exe --encrypt-all",
        9999
    )
    
    hidr.print_summary(result)
    hidr.print_agent_communication(result)
