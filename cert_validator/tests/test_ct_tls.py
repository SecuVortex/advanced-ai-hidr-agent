"""
Unit tests for CT and TLS modules
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from cert_validator.ct_checker import CTChecker
from cert_validator.tls_fetcher import TLSCertFetcher

def test_ct_checker_init():
    """Test CT checker initialization"""
    checker = CTChecker()
    assert checker.timeout == 5
    assert checker.cache == {}

def test_ct_check_presence():
    """Test CT presence check"""
    checker = CTChecker()
    fingerprint = "sha256:abc123"
    
    result = checker.check_ct_presence(fingerprint)
    
    assert 'ct_present' in result
    assert 'scts' in result
    assert 'checked_at' in result

def test_ct_cache():
    """Test CT result caching"""
    checker = CTChecker()
    fingerprint = "sha256:test123"
    
    # First call
    result1 = checker.check_ct_presence(fingerprint)
    
    # Second call should hit cache
    result2 = checker.check_ct_presence(fingerprint)
    
    assert result1 == result2
    assert fingerprint in checker.cache

def test_ct_policy_validation_public_tls():
    """Test CT policy for public TLS"""
    checker = CTChecker()
    
    ct_result = {'ct_present': False, 'scts': []}
    context = {'type': 'tls', 'public': True}
    
    policy = checker.validate_ct_policy(ct_result, context)
    
    assert 'warnings' in policy
    assert len(policy['warnings']) > 0

def test_tls_fetcher_init():
    """Test TLS fetcher initialization"""
    fetcher = TLSCertFetcher()
    assert fetcher.timeout == 5

@patch('socket.create_connection')
@patch('ssl.create_default_context')
def test_tls_fetch_success(mock_ssl_context, mock_socket):
    """Test successful TLS certificate fetch"""
    # Mock SSL socket
    mock_ssock = Mock()
    mock_ssock.getpeercert.return_value = b'mock_cert_data'
    mock_ssock.version.return_value = 'TLSv1.3'
    mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
    mock_ssock.__enter__ = Mock(return_value=mock_ssock)
    mock_ssock.__exit__ = Mock(return_value=False)
    
    mock_context = Mock()
    mock_context.wrap_socket.return_value = mock_ssock
    mock_ssl_context.return_value = mock_context
    
    mock_sock = Mock()
    mock_sock.__enter__ = Mock(return_value=mock_sock)
    mock_sock.__exit__ = Mock(return_value=False)
    mock_socket.return_value = mock_sock
    
    fetcher = TLSCertFetcher()
    
    # This will fail on cert parsing, but tests connection logic
    result = fetcher.fetch_cert_chain('example.com', 443)
    
    assert 'host' in result
    assert result['host'] == 'example.com'

def test_tls_fetch_timeout():
    """Test TLS fetch timeout handling"""
    fetcher = TLSCertFetcher(timeout=0.001)
    
    result = fetcher.fetch_cert_chain('192.0.2.1', 443)  # TEST-NET-1 (unreachable)
    
    assert not result['success']
    assert 'error' in result

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
