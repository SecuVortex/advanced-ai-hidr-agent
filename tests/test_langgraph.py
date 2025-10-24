"""Tests for LangGraph wrapper"""
import pytest
from simple_multiagent import SimpleMultiAgent

class TestLangGraph:
    """Test LangGraph orchestration"""
    
    def test_init_without_langgraph(self):
        """Test initialization without LangGraph"""
        agent = SimpleMultiAgent(use_langgraph=False)
        assert agent.langgraph_orchestrator is None
        assert agent.use_langgraph is False
    
    def test_init_with_langgraph(self):
        """Test initialization with LangGraph"""
        agent = SimpleMultiAgent(use_langgraph=True)
        assert agent.langgraph_orchestrator is not None
        assert agent.use_langgraph is True
    
    def test_analyze_with_langgraph(self):
        """Test process analysis with LangGraph"""
        agent = SimpleMultiAgent(use_langgraph=True)
        result = agent.analyze_process('test.exe', 'C:\\test.exe', 'test.exe', 1234)
        
        assert 'detection_result' in result
        assert 'intelligence_result' in result
        assert 'analysis_result' in result
        assert 'final_action' in result
    
    def test_langgraph_state_transitions(self):
        """Test LangGraph state transitions"""
        agent = SimpleMultiAgent(use_langgraph=True)
        result = agent.analyze_process('test.exe', 'C:\\test.exe', 'test.exe', 1234)
        
        messages = result.get('messages', [])
        langgraph_messages = [m for m in messages if 'LangGraph' in m.get('from_agent', '')]
        
        assert len(langgraph_messages) > 0
    
    def test_langgraph_fallback(self):
        """Test fallback to direct execution"""
        agent = SimpleMultiAgent(use_langgraph=True)
        
        # Force LangGraph to fail by setting to None
        agent.langgraph_orchestrator = None
        
        result = agent.analyze_process('test.exe', 'C:\\test.exe', 'test.exe', 1234)
        assert 'final_action' in result
