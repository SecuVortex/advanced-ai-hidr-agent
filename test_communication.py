import unittest
from unittest.mock import MagicMock
import time
from agents.base_agent import BaseAgent, AgentMessage


class MockAgent(BaseAgent):

    def analyze(self, data):
        return {'status': 'processed'}


class TestAgentCommunication(unittest.TestCase):

    def setUp(self):
        self.agent1 = MockAgent(name='Agent1', role='Tester1')
        self.agent2 = MockAgent(name='Agent2', role='Tester2')

    def test_message_creation(self):
        msg = AgentMessage('Agent1', 'Agent2', 'Test message')
        self.assertEqual(msg.from_agent, 'Agent1')
        self.assertEqual(msg.to_agent, 'Agent2')
        self.assertEqual(msg.message, 'Test message')
        self.assertIsNotNone(msg.timestamp)

    def test_send_and_receive(self):
        self.agent1.send_message('Agent2', 'Hello')
        messages = self.agent1.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['to_agent'], 'Agent2')

    def test_clear_messages(self):
        self.agent1.send_message('Agent2', 'Some message')
        self.agent1.clear_messages()
        self.assertEqual(len(self.agent1.get_messages()), 0)


if __name__ == '__main__':
    unittest.main()
