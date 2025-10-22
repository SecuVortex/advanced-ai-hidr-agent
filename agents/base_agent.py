"""
Base Agent Class
Provides common functionality for all agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class AgentMessage:
    """Structured message for agent communication"""
    
    def __init__(self, from_agent: str, to_agent: str, message: str, data: Optional[Dict] = None):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        return f"[{self.from_agent}] → [{self.to_agent}]: {self.message}"


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.logger = logging.getLogger(f"hidr.agent.{name}")
        self.messages: List[AgentMessage] = []
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data and return results
        
        Args:
            data: Input data to analyze
            
        Returns:
            Analysis results
        """
        pass
    
    def send_message(self, to_agent: str, message: str, data: Optional[Dict] = None) -> AgentMessage:
        """
        Send message to another agent
        
        Args:
            to_agent: Target agent name
            message: Message content
            data: Additional data
            
        Returns:
            Created message
        """
        msg = AgentMessage(self.name, to_agent, message, data)
        self.messages.append(msg)
        self.logger.info(f"📨 {msg}")
        return msg
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(f"[{self.name}] ⚠️  {message}")
    
    def log_error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(f"[{self.name}] ❌ {message}")
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages sent by this agent"""
        return [msg.to_dict() for msg in self.messages]
    
    def clear_messages(self) -> None:
        """Clear message history"""
        self.messages.clear()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', role='{self.role}')"
