__version__ = '2.0.0'
__author__ = 'HIDR Agent Team'
from agents.detection_agent import DetectionAgent
from agents.intelligence_agent import IntelligenceAgent
from agents.response_agent import ResponseAgent
from agents.analyst_agent import AnalystAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.orchestrator import MultiAgentOrchestrator
__all__ = ['DetectionAgent', 'IntelligenceAgent', 'ResponseAgent',
    'AnalystAgent', 'CoordinatorAgent', 'MultiAgentOrchestrator']
