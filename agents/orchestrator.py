"""
Multi-Agent Orchestrator
Uses LangGraph to coordinate agent collaboration with human-in-the-loop.
"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from agents.detection_agent import DetectionAgent
from agents.intelligence_agent import IntelligenceAgent
from agents.response_agent import ResponseAgent
from agents.analyst_agent import AnalystAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.config import Config
import time


class AgentState(TypedDict):
    """State shared between agents in the workflow"""
    event_type: str
    target: Dict[str, Any]
    detection_result: Dict[str, Any]
    intelligence_result: Dict[str, Any]
    analysis_result: Dict[str, Any]
    coordination_result: Dict[str, Any]
    response_result: Dict[str, Any]
    final_action: str
    messages: list
    human_decision: Dict[str, Any]
    workflow_start_time: float
    workflow_end_time: float


class MultiAgentOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent collaboration
    
    Workflow:
        1. Detection Agent analyzes threat
        2. Intelligence Agent enriches with external data
        3. Analyst Agent provides AI analysis
        4. Coordinator Agent determines priority
        5. Human Approval (if required)
        6. Response Agent executes action
    """
    
    def __init__(self, quarantine_dir: str = None, require_human_approval: bool = None):
        # Initialize agents
        self.detection_agent = DetectionAgent()
        self.intelligence_agent = IntelligenceAgent()
        self.response_agent = ResponseAgent(quarantine_dir)
        self.analyst_agent = AnalystAgent()
        self.coordinator_agent = CoordinatorAgent()
        
        # Configuration
        self.require_human_approval = (
            require_human_approval if require_human_approval is not None 
            else Config.REQUIRE_HUMAN_APPROVAL
        )
        
        # Build workflow
        self.workflow = self._build_workflow()
        
        print(f"✓ Multi-Agent Orchestrator initialized")
        print(f"  - Human-in-the-loop: {'ENABLED' if self.require_human_approval else 'DISABLED'}")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("detect", self._detect_node)
        workflow.add_node("intelligence", self._intelligence_node)
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("coordinate", self._coordinate_node)
        workflow.add_node("human_approval", self._human_approval_node)
        workflow.add_node("respond", self._respond_node)
        
        # Define workflow edges
        workflow.set_entry_point("detect")
        workflow.add_edge("detect", "intelligence")
        workflow.add_edge("intelligence", "analyze")
        workflow.add_edge("analyze", "coordinate")
        workflow.add_edge("coordinate", "human_approval")
        workflow.add_edge("human_approval", "respond")
        workflow.add_edge("respond", END)
        
        return workflow.compile()
    
    def _add_message(self, state: AgentState, from_agent: str, to_agent: str, message: str):
        """Add message to communication log"""
        msg = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message": message,
            "timestamp": time.time()
        }
        state["messages"].append(msg)
        print(f"📨 [{from_agent}] → [{to_agent}]: {message}")
    
    def _detect_node(self, state: AgentState) -> AgentState:
        """Detection agent node"""
        print(f"\n🔍 [{self.detection_agent.name}] Analyzing {state['event_type']}...")
        
        # Prepare data for detection
        data = {"event_type": state["event_type"], **state["target"]}
        
        # Run detection
        result = self.detection_agent.analyze(data)
        state["detection_result"] = result
        
        # Add message
        if result.get("is_suspicious"):
            self._add_message(
                state,
                self.detection_agent.name,
                self.intelligence_agent.name,
                f"⚠️ Suspicious {state['event_type']} detected! Threat level: {result.get('threat_level')}/10"
            )
        else:
            self._add_message(
                state,
                self.detection_agent.name,
                self.intelligence_agent.name,
                f"✓ Normal {state['event_type']} detected"
            )
        
        return state
    
    def _intelligence_node(self, state: AgentState) -> AgentState:
        """Intelligence agent node"""
        print(f"🌐 [{self.intelligence_agent.name}] Querying threat intelligence...")
        
        # Prepare data for intelligence
        detection = state["detection_result"]
        data = {"file_hash": detection.get("file_hash")}
        
        # Run intelligence gathering
        result = self.intelligence_agent.analyze(data)
        state["intelligence_result"] = result
        
        # Add message
        if result.get("is_known_malware"):
            vt_detections = result.get("virustotal", {}).get("malicious", 0)
            self._add_message(
                state,
                self.intelligence_agent.name,
                self.analyst_agent.name,
                f"🚨 CONFIRMED MALWARE! VirusTotal: {vt_detections} detections"
            )
        elif result.get("skipped"):
            self._add_message(
                state,
                self.intelligence_agent.name,
                self.analyst_agent.name,
                "Intelligence check skipped (no file hash available)"
            )
        else:
            threat_score = result.get("threat_score", 0)
            self._add_message(
                state,
                self.intelligence_agent.name,
                self.analyst_agent.name,
                f"Threat intelligence score: {threat_score:.1f}/10"
            )
        
        return state
    
    def _analyze_node(self, state: AgentState) -> AgentState:
        """Analyst agent node"""
        print(f"🤖 [{self.analyst_agent.name}] Generating AI analysis...")
        
        # Prepare data for analysis
        data = {
            "detection": state["detection_result"],
            "intelligence": state["intelligence_result"],
            "response": {}
        }
        
        # Run AI analysis
        result = self.analyst_agent.analyze(data)
        state["analysis_result"] = result
        
        # Add message
        severity = result.get("severity", "Medium")
        self._add_message(
            state,
            self.analyst_agent.name,
            self.coordinator_agent.name,
            f"Analysis complete - Severity: {severity}"
        )
        
        return state
    
    def _coordinate_node(self, state: AgentState) -> AgentState:
        """Coordinator agent node"""
        print(f"🎯 [{self.coordinator_agent.name}] Coordinating response...")
        
        # Run coordination
        result = self.coordinator_agent.coordinate_workflow(state)
        state["coordination_result"] = result
        
        # Add message
        priority = result.get("priority", "Medium")
        action = result.get("recommended_action", "monitor")
        self._add_message(
            state,
            self.coordinator_agent.name,
            "HumanOperator" if self.require_human_approval else self.response_agent.name,
            f"Priority: {priority}, Recommended action: {action}"
        )
        
        return state
    
    def _human_approval_node(self, state: AgentState) -> AgentState:
        """Human-in-the-loop approval node"""
        coordination = state["coordination_result"]
        requires_approval = coordination.get("requires_human_approval", False)
        
        if not self.require_human_approval or not requires_approval:
            # Auto-approve
            state["human_decision"] = {
                "approved": True,
                "action": coordination.get("recommended_action", "monitor"),
                "reason": "Auto-approved (no human approval required)"
            }
            return state
        
        # Display AI analysis to human
        analysis = state["analysis_result"]
        detection = state["detection_result"]
        intelligence = state["intelligence_result"]
        
        print(f"\n{'='*70}")
        print(f"⚠️  HUMAN DECISION REQUIRED")
        print(f"{'='*70}")
        print(f"\n🤖 AI ANALYST EXPLANATION:")
        print(f"{analysis.get('summary', 'Analysis unavailable')}")
        print(f"\n📊 THREAT DETAILS:")
        print(f"   Severity: {analysis.get('severity', 'Unknown')}")
        print(f"   Priority: {coordination.get('priority', 'Unknown')}")
        print(f"   Threat Level: {detection.get('threat_level', 0)}/10")
        
        # Show target information
        if state["event_type"] == "process":
            print(f"\n🔍 PROCESS INFORMATION:")
            print(f"   Name: {state['target']['name']}")
            print(f"   Path: {state['target']['path']}")
            print(f"   PID: {state['target']['pid']}")
        else:
            print(f"\n📁 FILE INFORMATION:")
            print(f"   Path: {state['target'].get('filepath', 'Unknown')}")
        
        # Show reasons
        print(f"\n⚠️  REASONS FOR FLAGGING:")
        for i, reason in enumerate(detection.get("reasons", []), 1):
            print(f"   {i}. {reason}")
        
        # Show VirusTotal results
        if intelligence.get("virustotal"):
            vt = intelligence["virustotal"]
            if not vt.get("error"):
                print(f"\n🌐 VIRUSTOTAL ANALYSIS:")
                print(f"   Malicious: {vt.get('malicious', 0)} detections")
                print(f"   Suspicious: {vt.get('suspicious', 0)} detections")
                print(f"   Harmless: {vt.get('harmless', 0)} detections")
        
        # Get user decision
        print(f"\n{'='*70}")
        print(f"WHAT WOULD YOU LIKE TO DO?")
        print(f"{'='*70}")
        print(f"  1. ALLOW - Let it continue (false positive)")
        print(f"  2. TERMINATE TEMPORARILY - Kill process now (can restart)")
        print(f"  3. TERMINATE PERMANENTLY - Kill and quarantine (recommended)")
        print(f"  4. MONITOR - Watch closely but don't act yet")
        print(f"{'='*70}")
        
        while True:
            choice = input("\nYour decision (1/2/3/4): ").strip()
            
            if choice == "1":
                state["human_decision"] = {
                    "approved": False,
                    "action": "allow",
                    "reason": "User approved - false positive"
                }
                print("✓ Process/file ALLOWED by user")
                self._add_message(state, "HumanOperator", self.response_agent.name, 
                                "User chose to ALLOW. Treating as false positive.")
                break
            
            elif choice == "2":
                state["human_decision"] = {
                    "approved": True,
                    "action": "terminate_temporary",
                    "reason": "User requested temporary termination"
                }
                print("✓ Process will be TERMINATED (temporary)")
                self._add_message(state, "HumanOperator", self.response_agent.name,
                                "User chose TEMPORARY termination.")
                break
            
            elif choice == "3":
                state["human_decision"] = {
                    "approved": True,
                    "action": "terminate_permanent",
                    "reason": "User requested permanent termination and quarantine"
                }
                print("✓ Process will be TERMINATED and QUARANTINED (permanent)")
                self._add_message(state, "HumanOperator", self.response_agent.name,
                                "User chose PERMANENT termination with quarantine.")
                break
            
            elif choice == "4":
                state["human_decision"] = {
                    "approved": False,
                    "action": "monitor",
                    "reason": "User chose to monitor without action"
                }
                print("✓ Will continue MONITORING")
                self._add_message(state, "HumanOperator", self.response_agent.name,
                                "User chose to MONITOR. No action taken.")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        return state
    
    def _respond_node(self, state: AgentState) -> AgentState:
        """Response agent node"""
        print(f"\n🛡️ [{self.response_agent.name}] Executing action...")
        
        # Get action from human decision or coordination
        human_decision = state.get("human_decision", {})
        action = human_decision.get("action") or state["coordination_result"].get("recommended_action", "monitor")
        
        # Prepare data for response
        data = {
            "action": action,
            "target": state["target"]
        }
        
        # Execute response
        result = self.response_agent.analyze(data)
        state["response_result"] = result
        state["final_action"] = action
        
        # Add message
        success = result.get("success", False)
        message = result.get("message", "")
        self._add_message(
            state,
            self.response_agent.name,
            "System",
            f"Action '{action}' {'completed' if success else 'failed'}: {message}"
        )
        
        return state
    
    def process_event(self, event_type: str, target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process security event through multi-agent workflow
        
        Args:
            event_type: Type of event ("process" or "file")
            target: Target data (process or file information)
            
        Returns:
            Final workflow state with all agent results
        """
        # Initialize state
        initial_state = {
            "event_type": event_type,
            "target": target,
            "detection_result": {},
            "intelligence_result": {},
            "analysis_result": {},
            "coordination_result": {},
            "response_result": {},
            "final_action": "monitor",
            "messages": [],
            "human_decision": {},
            "workflow_start_time": time.time(),
            "workflow_end_time": 0.0
        }
        
        print(f"\n{'='*70}")
        print(f"🚨 NEW SECURITY EVENT: {event_type.upper()}")
        print(f"{'='*70}")
        
        # Execute workflow
        final_state = self.workflow.invoke(initial_state)
        final_state["workflow_end_time"] = time.time()
        
        # Calculate execution time
        execution_time = final_state["workflow_end_time"] - final_state["workflow_start_time"]
        
        print(f"\n{'='*70}")
        print(f"✅ WORKFLOW COMPLETE")
        print(f"   Final Action: {final_state['final_action']}")
        print(f"   Execution Time: {execution_time:.2f}s")
        print(f"   Messages Exchanged: {len(final_state['messages'])}")
        if final_state.get("human_decision"):
            print(f"   Human Decision: {final_state['human_decision'].get('reason', 'N/A')}")
        print(f"{'='*70}\n")
        
        return final_state
