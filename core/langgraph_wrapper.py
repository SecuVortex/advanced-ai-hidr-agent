"""
LangGraph Orchestrator - Academic requirement wrapper
Provides state machine orchestration for multi-agent workflow
"""
import logging
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

logger = logging.getLogger('HIDR.LangGraph')

class AgentState(TypedDict):
    """State passed between agents"""
    process_name: str
    path: str
    cmdline: str
    pid: int
    detection_result: Dict[str, Any]
    intelligence_result: Dict[str, Any]
    analysis_result: Dict[str, Any]
    final_action: str
    messages: list

class LangGraphOrchestrator:
    """LangGraph wrapper for multi-agent orchestration"""
    
    def __init__(self, multiagent):
        self.multiagent = multiagent
        self.graph = self.build_graph()
        logger.info("LangGraph orchestrator initialized")
    
    def build_graph(self) -> StateGraph:
        """Build the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("detection", self._detection_node)
        workflow.add_node("intelligence", self._intelligence_node)
        workflow.add_node("analysis", self._analysis_node)
        workflow.add_node("coordinator", self._coordinator_node)
        
        # Define edges (workflow)
        workflow.set_entry_point("detection")
        workflow.add_edge("detection", "intelligence")
        workflow.add_edge("intelligence", "analysis")
        workflow.add_edge("analysis", "coordinator")
        workflow.add_edge("coordinator", END)
        
        return workflow.compile()
    
    def analyze_process(self, proc_name: str, path: str, cmdline: str, pid: int) -> Dict[str, Any]:
        """Analyze process using LangGraph orchestration"""
        logger.info(f"LangGraph analyzing: {proc_name} (PID: {pid})")
        
        # Initialize state
        initial_state = {
            'process_name': proc_name,
            'path': path,
            'cmdline': cmdline,
            'pid': pid,
            'detection_result': {},
            'intelligence_result': {},
            'analysis_result': {},
            'final_action': '',
            'messages': []
        }
        
        # Execute graph
        final_state = self.graph.invoke(initial_state)
        
        logger.info(f"LangGraph complete: {proc_name} -> {final_state['final_action']}")
        
        return {
            'detection_result': final_state['detection_result'],
            'intelligence_result': final_state['intelligence_result'],
            'analysis_result': final_state['analysis_result'],
            'final_action': final_state['final_action'],
            'response_result': {'action': final_state['final_action'], 'success': True},
            'messages': final_state['messages']
        }
    
    def _detection_node(self, state: AgentState) -> AgentState:
        """Detection agent node"""
        logger.debug("LangGraph: Detection node")
        self.multiagent.log_message("LangGraph", "DetectionAgent", f"Analyzing: {state['process_name']}")
        
        detection = self.multiagent._run_detection(
            state['process_name'],
            state['path'],
            state['cmdline']
        )
        
        state['detection_result'] = detection
        state['messages'] = self.multiagent.messages.copy()
        return state
    
    def _intelligence_node(self, state: AgentState) -> AgentState:
        """Intelligence agent node"""
        logger.debug("LangGraph: Intelligence node")
        
        if not state['detection_result'].get('is_suspicious', False):
            state['intelligence_result'] = {
                'threat_score': 0,
                'is_known_malware': False,
                'behaviors': [],
                'behavior_score': 0
            }
        else:
            self.multiagent.log_message("LangGraph", "IntelligenceAgent", "Gathering intelligence")
            intelligence = self.multiagent._run_intelligence(
                state['detection_result'],
                state['pid'],
                state['process_name'],
                state['path'],
                state['cmdline']
            )
            state['intelligence_result'] = intelligence
        
        state['messages'] = self.multiagent.messages.copy()
        return state
    
    def _analysis_node(self, state: AgentState) -> AgentState:
        """Analysis agent node"""
        logger.debug("LangGraph: Analysis node")
        self.multiagent.log_message("LangGraph", "AnalystAgent", "Generating analysis")
        
        analysis = self.multiagent._run_analysis(
            state['detection_result'],
            state['intelligence_result']
        )
        
        state['analysis_result'] = analysis
        state['messages'] = self.multiagent.messages.copy()
        return state
    
    def _coordinator_node(self, state: AgentState) -> AgentState:
        """Coordinator agent node"""
        logger.debug("LangGraph: Coordinator node")
        self.multiagent.log_message("LangGraph", "CoordinatorAgent", "Determining action")
        
        action = self.multiagent._run_coordinator(
            state['detection_result'],
            state['intelligence_result'],
            state['analysis_result']
        )
        
        state['final_action'] = action
        state['messages'] = self.multiagent.messages.copy()
        return state
