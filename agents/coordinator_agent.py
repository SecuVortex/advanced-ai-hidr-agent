"""
Coordinator Agent
Orchestrates collaboration between agents and manages workflow.
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class CoordinatorAgent(BaseAgent):
    """Agent responsible for coordinating multi-agent collaboration"""
    
    def __init__(self):
        super().__init__(name="CoordinatorAgent", role="Multi-Agent Coordinator")
        self.workflow_history: List[Dict] = []
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate agent workflow
        
        Args:
            data: Workflow data
            
        Returns:
            Coordination results
        """
        return self.coordinate_workflow(data)
    
    def coordinate_workflow(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate the multi-agent workflow
        
        Args:
            workflow_state: Current workflow state
            
        Returns:
            Coordination decisions
        """
        self.log_info("Coordinating multi-agent workflow...")
        
        # Analyze workflow state
        detection = workflow_state.get("detection_result", {})
        intelligence = workflow_state.get("intelligence_result", {})
        analysis = workflow_state.get("analysis_result", {})
        
        # Determine priority
        priority = self._calculate_priority(detection, intelligence, analysis)
        
        # Resolve conflicts if any
        final_action = self._resolve_action_conflicts(detection, intelligence, analysis)
        
        # Generate coordination summary
        coordination = {
            "agent": self.name,
            "priority": priority,
            "recommended_action": final_action,
            "requires_human_approval": self._requires_human_approval(priority, final_action),
            "coordination_notes": self._generate_notes(workflow_state)
        }
        
        # Log workflow
        self.workflow_history.append({
            "state": workflow_state,
            "coordination": coordination
        })
        
        self.log_info(f"Coordination complete - Priority: {priority}, Action: {final_action}")
        
        return coordination
    
    def _calculate_priority(
        self,
        detection: Dict,
        intelligence: Dict,
        analysis: Dict
    ) -> str:
        """
        Calculate incident priority
        
        Args:
            detection: Detection results
            intelligence: Intelligence results
            analysis: Analysis results
            
        Returns:
            Priority level (Critical/High/Medium/Low)
        """
        threat_level = detection.get("threat_level", 0)
        is_known_malware = intelligence.get("is_known_malware", False)
        severity = analysis.get("severity", "Medium")
        
        if is_known_malware or severity == "Critical" or threat_level >= 8:
            return "Critical"
        elif severity == "High" or threat_level >= 6:
            return "High"
        elif severity == "Medium" or threat_level >= 3:
            return "Medium"
        else:
            return "Low"
    
    def _resolve_action_conflicts(
        self,
        detection: Dict,
        intelligence: Dict,
        analysis: Dict
    ) -> str:
        """
        Resolve conflicts between agent recommendations
        
        Args:
            detection: Detection results
            intelligence: Intelligence results
            analysis: Analysis results
            
        Returns:
            Final recommended action
        """
        # Get recommendations from each agent
        detection_rec = detection.get("recommendation", "monitor")
        intelligence_rec = intelligence.get("recommendation", "monitor")
        
        # Priority order: terminate_permanent > terminate_temporary > quarantine > monitor > allow
        action_priority = {
            "terminate_permanent": 5,
            "terminate_temporary": 4,
            "quarantine": 3,
            "monitor": 2,
            "allow": 1
        }
        
        # Choose most severe action
        recommendations = [detection_rec, intelligence_rec]
        final_action = max(recommendations, key=lambda x: action_priority.get(x, 0))
        
        # Override if known malware
        if intelligence.get("is_known_malware"):
            final_action = "terminate_permanent"
        
        return final_action
    
    def _requires_human_approval(self, priority: str, action: str) -> bool:
        """
        Determine if human approval is required
        
        Args:
            priority: Incident priority
            action: Recommended action
            
        Returns:
            True if human approval needed
        """
        # Require approval for high-impact actions
        high_impact_actions = ["terminate_permanent", "terminate_temporary", "quarantine"]
        
        return action in high_impact_actions
    
    def _generate_notes(self, workflow_state: Dict) -> str:
        """
        Generate coordination notes
        
        Args:
            workflow_state: Workflow state
            
        Returns:
            Coordination notes
        """
        detection = workflow_state.get("detection_result", {})
        intelligence = workflow_state.get("intelligence_result", {})
        messages = workflow_state.get("messages", [])
        
        notes = []
        
        # Detection notes
        if detection.get("is_suspicious"):
            notes.append(f"Detection flagged {len(detection.get('reasons', []))} suspicious indicators")
        
        # Intelligence notes
        if intelligence.get("is_known_malware"):
            vt_detections = intelligence.get("virustotal", {}).get("malicious", 0)
            notes.append(f"Confirmed malware with {vt_detections} VirusTotal detections")
        
        # Communication notes
        notes.append(f"Agent communication: {len(messages)} messages exchanged")
        
        return "; ".join(notes) if notes else "No special notes"
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get summary of workflow history
        
        Returns:
            Workflow statistics
        """
        total_workflows = len(self.workflow_history)
        
        if total_workflows == 0:
            return {"total_workflows": 0}
        
        priorities = [w["coordination"]["priority"] for w in self.workflow_history]
        actions = [w["coordination"]["recommended_action"] for w in self.workflow_history]
        
        return {
            "total_workflows": total_workflows,
            "priority_distribution": {
                "Critical": priorities.count("Critical"),
                "High": priorities.count("High"),
                "Medium": priorities.count("Medium"),
                "Low": priorities.count("Low")
            },
            "action_distribution": {
                action: actions.count(action) for action in set(actions)
            }
        }
