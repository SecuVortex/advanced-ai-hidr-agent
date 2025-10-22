"""
HIDR Multi-Agent System
~~~~~~~~~~~~~~~~~~~~~~~

A collaborative multi-agent system for host intrusion detection and response.

Agents:
    - DetectionAgent: Threat detection using heuristics
    - IntelligenceAgent: Threat intelligence from external sources
    - ResponseAgent: Automated incident response
    - AnalystAgent: AI-powered analysis and recommendations
    - CoordinatorAgent: Agent orchestration and coordination

Usage:
    >>> from agents.orchestrator import MultiAgentOrchestrator
    >>> orchestrator = MultiAgentOrchestrator(quarantine_dir="./quarantine")
    >>> result = orchestrator.process_event("process", target_data)
"""

__version__ = "2.0.0"
__author__ = "HIDR Agent Team"

from agents.detection_agent import DetectionAgent
from agents.intelligence_agent import IntelligenceAgent
from agents.response_agent import ResponseAgent
from agents.analyst_agent import AnalystAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.orchestrator import MultiAgentOrchestrator

__all__ = [
    "DetectionAgent",
    "IntelligenceAgent",
    "ResponseAgent",
    "AnalystAgent",
    "CoordinatorAgent",
    "MultiAgentOrchestrator",
]
