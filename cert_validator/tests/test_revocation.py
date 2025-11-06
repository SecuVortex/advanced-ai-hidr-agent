"""
Unit tests for revocation checking
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from cert_validator.revocation import RevocationChecker

def generate_test_cert():
    """Generate a test certificate"""
    private_key = rsa.generate_private_key(65537, 2048, default_backend())
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com")])
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject).issuer_name(issuer)
    builder = builder.public_key(private_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(datetime.now(timezone.utc))
    builder = builder.not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
    cert = builder.sign(private_key, hashes.SHA256(), default_backend())
    return cert, private_key

def test_revocation_checker_init():
    """Test revocation checker initialization"""
    checker = RevocationChecker()
    assert checker.cache == {}
    assert checker.timeout == 5

def test_check_revocation_no_urls():
    """Test revocation check when no OCSP/CRL URLs present"""
    cert, _ = generate_test_cert()
    checker = RevocationChecker()
    
    result = checker.check_revocation(cert)
    
    assert result['status'] == 'unknown'
    assert 'method' in result

def test_ocsp_cache_hit():
    """Test OCSP cache hit"""
    cert, _ = generate_test_cert()
    checker = RevocationChecker()
    
    # Pre-populate cache with proper structure
    cache_key = f"ocsp:{cert.serial_number}"
    cached_result = {
        'status': 'good',
        'method': 'ocsp',
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'expires': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }
    checker.cache[cache_key] = {
        'data': cached_result,
        'expires': cached_result['expires']
    }
    
    # Mock OCSP URL to trigger cache check
    with patch.object(checker, '_get_ocsp_url', return_value='http://ocsp.example.com'):
        result = checker._check_ocsp(cert, cert)
    
    assert result['status'] == 'good'
    assert result['method'] == 'ocsp'

def test_crl_cache_hit():
    """Test CRL cache hit"""
    cert, _ = generate_test_cert()
    checker = RevocationChecker()
    
    # Pre-populate cache
    cache_key = "crl:http://example.com/crl"
    checker.cache[cache_key] = {
        'data': {'revoked_serials': []},
        'expires': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }
    
    # Mock CRL URL extraction
    with patch.object(checker, '_get_crl_url', return_value='http://example.com/crl'):
        result = checker._check_crl(cert)
    
    assert result['status'] == 'good'
    assert result['method'] == 'crl'

@patch('requests.get')
def test_crl_download_and_parse(mock_get):
    """Test CRL download and parsing"""
    cert, key = generate_test_cert()
    checker = RevocationChecker()
    
    # Generate a CRL
    builder = x509.CertificateRevocationListBuilder()
    builder = builder.issuer_name(cert.issuer)
    builder = builder.last_update(datetime.now(timezone.utc))
    builder = builder.next_update(datetime.now(timezone.utc) + timedelta(days=1))
    crl = builder.sign(key, hashes.SHA256(), default_backend())
    
    # Mock HTTP response
    mock_response = Mock()
    mock_response.content = crl.public_bytes(encoding=serialization.Encoding.DER)
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    # Mock CRL URL extraction
    with patch.object(checker, '_get_crl_url', return_value='http://example.com/crl'):
        result = checker._check_crl(cert)
    
    assert result['status'] == 'good'
    assert result['method'] == 'crl'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
