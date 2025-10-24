"""Tests for configuration management"""
import pytest
import yaml
from pathlib import Path
from simple_multiagent import SimpleMultiAgent

class TestConfig:
    """Test configuration loading and management"""
    
    def test_load_config(self):
        """Test loading configuration from file"""
        agent = SimpleMultiAgent()
        assert agent.config is not None
        assert 'detection' in agent.config
    
    def test_default_config(self):
        """Test default configuration"""
        agent = SimpleMultiAgent('nonexistent.yaml')
        config = agent.config
        
        assert 'detection' in config
        assert 'monitoring' in config
    
    def test_config_values(self):
        """Test configuration values"""
        agent = SimpleMultiAgent()
        
        assert agent.config['detection']['threat_threshold'] >= 0
        assert agent.config['detection']['terminate_threshold'] >= 0
    
    def test_expert_system_config(self):
        """Test expert system configuration"""
        agent = SimpleMultiAgent()
        
        if 'expert_system' in agent.config:
            assert 'weights' in agent.config['expert_system']
            weights = agent.config['expert_system']['weights']
            assert 'yara' in weights
            assert 'virustotal' in weights
