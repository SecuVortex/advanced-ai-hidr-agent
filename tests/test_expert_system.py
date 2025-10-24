"""Tests for Expert System"""
import pytest
from core.expert_system import ThreatExpertSystem

class TestExpertSystem:
    """Test expert system functionality"""
    
    def test_init(self, sample_config):
        """Test expert system initialization"""
        expert = ThreatExpertSystem(sample_config)
        assert expert is not None
        assert expert.weights['yara'] == 3.0
        assert expert.weights['virustotal'] == 2.5
    
    def test_calculate_threat_score(self, sample_config):
        """Test threat score calculation"""
        expert = ThreatExpertSystem(sample_config)
        score = expert.calculate_threat_score(yara=8, vt=6, behavior=4, mitre_count=2)
        
        assert isinstance(score, float)
        assert 0 <= score <= 10
        assert score > 0  # Should be positive with these inputs
    
    def test_determine_action_high_threat(self, sample_config):
        """Test action determination for high threat"""
        expert = ThreatExpertSystem(sample_config)
        action = expert.determine_action(threat_score=9.0, is_known_malware=True)
        assert action == 'terminate_permanent'
    
    def test_determine_action_medium_threat(self, sample_config):
        """Test action determination for medium threat"""
        expert = ThreatExpertSystem(sample_config)
        action = expert.determine_action(threat_score=6.5)
        assert action == 'terminate_temporary'
    
    def test_determine_action_low_threat(self, sample_config):
        """Test action determination for low threat"""
        expert = ThreatExpertSystem(sample_config)
        action = expert.determine_action(threat_score=2.0)
        assert action == 'allow'
    
    def test_get_severity(self, sample_config):
        """Test severity classification"""
        expert = ThreatExpertSystem(sample_config)
        
        assert expert.get_severity(9.0) == 'Critical'
        assert expert.get_severity(7.0) == 'High'
        assert expert.get_severity(4.0) == 'Medium'
        assert expert.get_severity(1.0) == 'Low'
    
    def test_analyze(self, sample_config, sample_detection, sample_intelligence):
        """Test full analysis"""
        expert = ThreatExpertSystem(sample_config)
        result = expert.analyze(sample_detection, sample_intelligence)
        
        assert 'summary' in result
        assert 'severity' in result
        assert 'threat_score' in result
        assert 'mitre_techniques' in result
        assert result['ai_used'] == 'Expert System'
    
    def test_get_mitre_techniques(self, sample_config, sample_detection, sample_intelligence):
        """Test MITRE technique mapping"""
        expert = ThreatExpertSystem(sample_config)
        techniques = expert.get_mitre_techniques(sample_detection, sample_intelligence)
        
        assert isinstance(techniques, list)
        for tech in techniques:
            assert 'id' in tech
            assert 'source' in tech
