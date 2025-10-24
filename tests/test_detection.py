"""Unit Tests for HIDR Detection Logic"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from simple_multiagent import SimpleMultiAgent

class TestThreatDetection:
    
    @pytest.fixture
    def agent(self):
        return SimpleMultiAgent()
    
    def test_ransomware_detection(self, agent):
        """Test ransomware is detected with high threat level"""
        threat = agent._calculate_threat_level("ransomware.exe", "C:\\temp\\ransomware.exe", "")
        assert threat >= 8, "Ransomware should have threat level >= 8"
    
    def test_keylogger_detection(self, agent):
        """Test keylogger is detected"""
        threat = agent._calculate_threat_level("keylogger.exe", "C:\\downloads\\keylogger.exe", "")
        assert threat >= 7, "Keylogger should have threat level >= 7"
    
    def test_rat_detection(self, agent):
        """Test RAT malware is detected"""
        threat = agent._calculate_threat_level("njrat.exe", "C:\\temp\\njrat.exe", "")
        assert threat >= 9, "RAT should have threat level >= 9"
    
    def test_temp_directory_suspicious(self, agent):
        """Test processes from temp directory are flagged"""
        threat = agent._calculate_threat_level("test.exe", "C:\\temp\\test.exe", "")
        assert threat >= 3, "Temp directory should add suspicion"
    
    def test_encoded_powershell(self, agent):
        """Test encoded PowerShell commands are detected"""
        threat = agent._calculate_threat_level("powershell.exe", "C:\\Windows\\System32\\powershell.exe", 
                                               "powershell.exe -enc ABCD1234")
        assert threat >= 6, "Encoded PowerShell should be flagged"
    
    def test_safe_process_allowed(self, agent):
        """Test legitimate processes have low threat scores"""
        threat = agent._calculate_threat_level("notepad.exe", "C:\\Windows\\System32\\notepad.exe", "")
        assert threat < 3, "Safe processes should have low threat level"
    
    def test_threat_reasons_generated(self, agent):
        """Test threat reasons are properly generated"""
        reasons = agent._get_threat_reasons("ransomware.exe", "C:\\temp\\ransomware.exe", "")
        assert len(reasons) > 0, "Should generate threat reasons"
        assert any("ransomware" in r.lower() or "temp" in r.lower() for r in reasons)
    
    def test_action_determination_terminate(self, agent):
        """Test high threats trigger termination"""
        detection = {'threat_level': 10, 'is_suspicious': True}
        intelligence = {'threat_score': 8, 'is_known_malware': True, 'behavior_score': 0}
        analysis = {'severity': 'Critical'}
        
        action = agent._determine_action(detection, intelligence, analysis)
        assert action in ['terminate_temporary', 'terminate_permanent'], "High threats should terminate"
    
    def test_action_determination_allow(self, agent):
        """Test low threats are allowed"""
        detection = {'threat_level': 2, 'is_suspicious': False}
        intelligence = {'threat_score': 0, 'is_known_malware': False, 'behavior_score': 0}
        analysis = {'severity': 'Low'}
        
        action = agent._determine_action(detection, intelligence, analysis)
        assert action == 'allow', "Low threats should be allowed"
    
    def test_combined_threat_scoring(self, agent):
        """Test static + behavioral threat scoring"""
        detection = {'threat_level': 5, 'is_suspicious': True}
        intelligence = {'threat_score': 3, 'is_known_malware': False, 'behavior_score': 4}
        analysis = {'severity': 'Medium'}
        
        action = agent._determine_action(detection, intelligence, analysis)
        assert action in ['terminate_temporary', 'monitor'], "Combined score should trigger action"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
