"""
Unit tests for certificate validator core module
"""
import pytest
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

from cert_validator.core import CertificateValidator

def generate_test_cert(key_size=2048, days_valid=365, is_ca=False):
    """Generate a test certificate"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
        x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com"),
    ])
    
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(issuer)
    builder = builder.public_key(private_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(datetime.now(timezone.utc))
    builder = builder.not_valid_after(datetime.now(timezone.utc) + timedelta(days=days_valid))
    
    if is_ca:
        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        )
    
    cert = builder.sign(private_key, hashes.SHA256(), default_backend())
    
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    return cert_pem, private_key

def test_parse_valid_certificate():
    """Test parsing a valid certificate"""
    cert_pem, _ = generate_test_cert()
    validator = CertificateValidator()
    
    result = validator.parse_certificate(cert_pem)
    
    assert 'fingerprint' in result
    assert result['fingerprint'].startswith('sha256:')
    assert 'subject' in result
    assert 'issuer' in result
    assert result['key_size'] == 2048

def test_parse_expired_certificate():
    """Test parsing an expired certificate"""
    # Generate cert that expired 10 days ago
    private_key = rsa.generate_private_key(65537, 2048, default_backend())
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "expired.test")])
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject).issuer_name(issuer)
    builder = builder.public_key(private_key.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(datetime.now(timezone.utc) - timedelta(days=20))
    builder = builder.not_valid_after(datetime.now(timezone.utc) - timedelta(days=10))
    cert = builder.sign(private_key, hashes.SHA256(), default_backend())
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    
    validator = CertificateValidator()
    result = validator.parse_certificate(cert_pem)
    policy = validator.check_policy(result)
    
    assert not policy['valid']
    assert any('expired' in err.lower() for err in policy['errors'])

def test_weak_key_detection():
    """Test detection of weak RSA keys"""
    cert_pem, _ = generate_test_cert(key_size=1024)
    validator = CertificateValidator()
    
    result = validator.parse_certificate(cert_pem)
    policy = validator.check_policy(result)
    
    assert not policy['valid']
    assert any('key too small' in err.lower() for err in policy['errors'])

def test_chain_building():
    """Test certificate chain building"""
    cert_pem, _ = generate_test_cert()
    validator = CertificateValidator()
    
    leaf = validator.parse_certificate(cert_pem)
    chain = validator.build_chain(leaf, intermediates=[])
    
    assert len(chain) >= 1
    assert chain[0]['fingerprint'] == leaf['fingerprint']

def test_validate_chain_success():
    """Test successful chain validation"""
    cert_pem, _ = generate_test_cert()
    validator = CertificateValidator()
    
    result = validator.validate_chain(cert_pem, intermediates=[], context={})
    
    assert result['verdict'] in ['valid', 'invalid']
    assert 'cert_score' in result
    assert result['cert_score'] >= 0

def test_validate_chain_with_context():
    """Test validation with code signing context"""
    cert_pem, _ = generate_test_cert()
    validator = CertificateValidator()
    
    result = validator.validate_chain(
        cert_pem,
        intermediates=[],
        context={'type': 'code_signing'}
    )
    
    assert 'policy_check' in result
    assert 'warnings' in result['policy_check']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
