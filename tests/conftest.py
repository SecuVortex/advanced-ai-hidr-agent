"""Pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'detection': {'threat_threshold': 5, 'terminate_threshold': 8},
        'yara': {'enabled': True, 'rules_dir': 'yara_rules', 'scan_timeout': 2},
        'expert_system': {
            'enabled': True,
            'weights': {'yara': 3.0, 'virustotal': 2.5, 'behavioral': 1.5, 'mitre': 2.0}
        },
        'monitoring': {'vt_timeout': 2, 'behavior_timeout': 0.5}
    }

@pytest.fixture
def sample_detection():
    """Sample detection result"""
    return {
        'process_name': 'test.exe',
        'path': 'C:\\temp\\test.exe',
        'threat_level': 5,
        'is_suspicious': True,
        'reasons': ['Temp directory', 'Suspicious name'],
        'yara_matches': [],
        'yara_score': 0,
        'mitre_techniques': []
    }

@pytest.fixture
def sample_intelligence():
    """Sample intelligence result"""
    return {
        'threat_score': 3,
        'is_known_malware': False,
        'behaviors': ['network_connection'],
        'behavior_score': 2
    }

@pytest.fixture
def eicar_string():
    """EICAR test string"""
    return 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
