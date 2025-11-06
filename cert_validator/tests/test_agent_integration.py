"""
Unit tests for agent integration
"""
import pytest
from unittest.mock import Mock, patch
import requests

from cert_validator.agent_integration import CertValidatorClient, extract_pe_certificate

def test_client_init():
    """Test client initialization"""
    client = CertValidatorClient()
    assert client.api_url == "http://localhost:8001"
    assert client.api_key is not None

@patch('requests.post')
def test_validate_pe_signature_success(mock_post):
    """Test successful PE signature validation"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'verdict': 'valid',
        'cert_score': 90,
        'confidence_breakdown': {'signature': 50, 'policy': 40},
        'chain': ['sha256:abc'],
        'errors': []
    }
    mock_post.return_value = mock_response
    
    client = CertValidatorClient()
    result = client.validate_pe_signature("cert_pem", {'host': 'test'})
    
    assert result['verdict'] == 'valid'
    assert result['cert_score'] == 90

@patch('requests.post')
def test_validate_pe_signature_timeout(mock_post):
    """Test validation timeout handling"""
    mock_post.side_effect = requests.Timeout()
    
    client = CertValidatorClient()
    result = client.validate_pe_signature("cert_pem", {'host': 'test'})
    
    assert result['verdict'] == 'unknown'
    assert 'Timeout' in result['errors'][0]

def test_enrich_alert_no_cert():
    """Test alert enrichment without certificate"""
    client = CertValidatorClient()
    alert = {'host': 'test', 'pid': 123, 'threat_score': 5}
    
    enriched = client.enrich_alert(alert, cert_pem=None)
    
    assert 'cert_validation' not in enriched
    assert enriched['threat_score'] == 5

@patch('requests.post')
def test_enrich_alert_with_cert(mock_post):
    """Test alert enrichment with certificate"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'verdict': 'valid',
        'cert_score': 85,
        'confidence_breakdown': {'signature': 50},
        'chain': ['sha256:abc'],
        'errors': [],
        'leaf_cert': {'issuer': 'Test CA', 'not_after': '2025-12-31'}
    }
    mock_post.return_value = mock_response
    
    client = CertValidatorClient()
    alert = {'host': 'test', 'pid': 123, 'threat_score': 5, 'reasons': []}
    
    enriched = client.enrich_alert(alert, cert_pem="test_cert")
    
    assert 'cert_validation' in enriched
    assert enriched['cert_validation']['verdict'] == 'valid'
    assert enriched['cert_validation']['issuer'] == 'Test CA'

@patch('requests.post')
def test_enrich_alert_revoked_cert(mock_post):
    """Test alert enrichment with revoked certificate"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'verdict': 'revoked',
        'cert_score': 0,
        'confidence_breakdown': {},
        'chain': [],
        'errors': ['Certificate revoked']
    }
    mock_post.return_value = mock_response
    
    client = CertValidatorClient()
    alert = {'host': 'test', 'pid': 123, 'threat_score': 5, 'reasons': []}
    
    enriched = client.enrich_alert(alert, cert_pem="revoked_cert")
    
    assert enriched['threat_score'] == 10  # Increased by 5
    assert 'Revoked certificate' in enriched['reasons']

def test_extract_pe_certificate():
    """Test PE certificate extraction (stub)"""
    result = extract_pe_certificate("test.exe")
    assert result is None  # Not implemented yet

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
