"""Tests for multi-agent system"""
import pytest
from simple_multiagent import SimpleMultiAgent

class TestMultiAgent:
    """Test multi-agent system core functionality"""
    
    def test_init(self):
        """Test multi-agent initialization"""
        agent = SimpleMultiAgent()
        assert agent is not None
        assert agent.config is not None
    
    def test_analyze_process(self):
        """Test process analysis"""
        agent = SimpleMultiAgent()
        result = agent.analyze_process('notepad.exe', 'C:\\Windows\\System32\\notepad.exe', 'notepad.exe', 1234)
        
        assert 'detection_result' in result
        assert 'final_action' in result
        assert result['final_action'] in ['allow', 'monitor', 'terminate_temporary', 'terminate_permanent']
    
    def test_calculate_threat_level(self):
        """Test threat level calculation"""
        agent = SimpleMultiAgent()
        
        # Safe process
        level = agent._calculate_threat_level('notepad.exe', 'C:\\Windows\\System32\\notepad.exe', 'notepad.exe')
        assert level == 0
        
        # Suspicious process
        level = agent._calculate_threat_level('suspicious.exe', 'C:\\temp\\suspicious.exe', 'suspicious.exe')
        assert level > 0
    
    def test_get_threat_reasons(self):
        """Test threat reason extraction"""
        agent = SimpleMultiAgent()
        reasons = agent._get_threat_reasons('test.exe', 'C:\\temp\\test.exe', 'test.exe')
        
        assert isinstance(reasons, list)
        assert len(reasons) > 0
        assert 'Temp directory' in reasons
    
    def test_run_detection(self):
        """Test detection agent"""
        agent = SimpleMultiAgent()
        result = agent._run_detection('test.exe', 'C:\\test.exe', 'test.exe')
        
        assert 'process_name' in result
        assert 'threat_level' in result
        assert 'is_suspicious' in result
        assert 'reasons' in result
    
    def test_fallback_analysis(self):
        """Test fallback analysis"""
        agent = SimpleMultiAgent()
        result = agent._fallback_analysis('test.exe', 'C:\\test.exe', 'test.exe')
        
        assert 'detection_result' in result
        assert 'final_action' in result
