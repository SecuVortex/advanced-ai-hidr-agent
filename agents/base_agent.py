from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class AgentMessage:

    def __init__(self, from_agent: str, to_agent: str, message: str, data:
        Optional[Dict]=None):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) ->Dict[str, Any]:
        return {'from_agent': self.from_agent, 'to_agent': self.to_agent,
            'message': self.message, 'data': self.data, 'timestamp': self.
            timestamp.isoformat()}

    def __str__(self) ->str:
        return f'[{self.from_agent}] → [{self.to_agent}]: {self.message}'


class BaseAgent(ABC):

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.messages: List[AgentMessage] = []
        self.logger = logging.getLogger(self.name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) ->Dict[str, Any]:
        pass

    def send_message(self, to_agent: str, message: str, data: Optional[Dict
        ]=None) ->AgentMessage:
        msg = AgentMessage(from_agent=self.name, to_agent=to_agent, message
            =message, data=data)
        self.messages.append(msg)
        return msg

    def log_info(self, message: str) ->None:
        self.logger.info(f'[{self.name}] {message}')

    def log_warning(self, message: str) ->None:
        self.logger.warning(f'[{self.name}] ⚠️  {message}')

    def log_error(self, message: str) ->None:
        self.logger.error(f'[{self.name}] ❌ {message}')

    def get_messages(self) ->List[Dict[str, Any]]:
        return [msg.to_dict() for msg in self.messages]

    def clear_messages(self) ->None:
        self.messages.clear()

    def __repr__(self) ->str:
        return (
            f"{self.__class__.__name__}(name='{self.name}', role='{self.role}')"
            )
