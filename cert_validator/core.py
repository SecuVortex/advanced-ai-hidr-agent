"""
CA Certificate Validator - Core Module
Validates certificate chains, performs policy checks, and extracts metadata
"""
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.x509.oid import ExtensionOID, ExtendedKeyUsageOID
except ImportError:
    raise ImportError("cryptography library required: pip install cryptography")

logger = logging.getLogger('HIDR.CertValidator')

class CertificateValidator:
    """Core certificate validation logic"""
    
    FORBIDDEN_SIG_ALGS = ['md5', 'sha1']
    MIN_RSA_KEY_SIZE = 2048
    MIN_ECC_KEY_SIZE = 256
    
    def __init__(self, trust_store_path: Optional[str] = None):
        self.trust_store_path = trust_store_path
        self.trust_store_certs = self._load_trust_store()
    
    def _load_trust_store(self) -> List[x509.Certificate]:
        """Load system trust store certificates"""
        certs = []
        if self.trust_store_path and Path(self.trust_store_path).exists():
            try:
                with open(self.trust_store_path, 'rb') as f:
                    cert_data = f.read()
                    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                    certs.append(cert)
            except Exception as e:
                logger.warning(f"Failed to load trust store: {e}")
        return certs
    
    def parse_certificate(self, cert_pem: str) -> Dict[str, Any]:
        """Parse PEM certificate and extract metadata"""
        try:
            if isinstance(cert_pem, str):
                cert_pem = cert_pem.encode('utf-8')
            
            cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
            
            # Extract fingerprint
            fingerprint = hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
            
            # Extract subject/issuer
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            
            # Extract validity
            not_before = cert.not_valid_before_utc if hasattr(cert, 'not_valid_before_utc') else cert.not_valid_before
            not_after = cert.not_valid_after_utc if hasattr(cert, 'not_valid_after_utc') else cert.not_valid_after
            
            # Extract public key info
            pub_key = cert.public_key()
            key_type = pub_key.__class__.__name__
            key_size = pub_key.key_size if hasattr(pub_key, 'key_size') else 0
            
            # Extract signature algorithm
            sig_alg = cert.signature_algorithm_oid._name
            
            # Extract extensions
            eku = self._extract_eku(cert)
            san = self._extract_san(cert)
            
            return {
                'fingerprint': f"sha256:{fingerprint}",
                'subject': subject,
                'issuer': issuer,
                'serial': str(cert.serial_number),
                'not_before': not_before.isoformat(),
                'not_after': not_after.isoformat(),
                'key_type': key_type,
                'key_size': key_size,
                'signature_algorithm': sig_alg,
                'extended_key_usage': eku,
                'subject_alt_names': san,
                'cert_object': cert
            }
        except Exception as e:
            logger.error(f"Certificate parsing failed: {e}")
            raise ValueError(f"Invalid certificate: {e}")
    
    def _extract_eku(self, cert: x509.Certificate) -> List[str]:
        """Extract Extended Key Usage"""
        try:
            ext = cert.extensions.get_extension_for_oid(ExtensionOID.EXTENDED_KEY_USAGE)
            return [oid._name for oid in ext.value]
        except x509.ExtensionNotFound:
            return []
    
    def _extract_san(self, cert: x509.Certificate) -> List[str]:
        """Extract Subject Alternative Names"""
        try:
            ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            return [str(name.value) for name in ext.value]
        except x509.ExtensionNotFound:
            return []
    
    def build_chain(self, leaf_cert: Dict, intermediates: List[str] = None) -> List[Dict]:
        """Build certificate chain from leaf to root"""
        chain = [leaf_cert]
        current = leaf_cert['cert_object']
        
        # Parse intermediates
        intermediate_certs = []
        if intermediates:
            for int_pem in intermediates:
                try:
                    parsed = self.parse_certificate(int_pem)
                    intermediate_certs.append(parsed)
                except Exception as e:
                    logger.warning(f"Failed to parse intermediate: {e}")
        
        # Try to build chain
        for _ in range(10):  # Max chain depth
            if current.issuer == current.subject:
                break  # Self-signed root
            
            # Find issuer in intermediates or trust store
            issuer_cert = None
            for int_cert in intermediate_certs:
                if int_cert['subject'] == leaf_cert['issuer']:
                    issuer_cert = int_cert
                    break
            
            if issuer_cert:
                chain.append(issuer_cert)
                current = issuer_cert['cert_object']
            else:
                break
        
        return chain
    
    def verify_chain(self, chain: List[Dict]) -> Dict[str, Any]:
        """Verify certificate chain signatures"""
        errors = []
        
        for i in range(len(chain) - 1):
            cert = chain[i]['cert_object']
            issuer = chain[i + 1]['cert_object']
            
            try:
                issuer.public_key().verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    cert.signature_hash_algorithm
                )
            except Exception as e:
                errors.append(f"Signature verification failed at depth {i}: {e}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def check_policy(self, cert_info: Dict, context: Dict = None) -> Dict[str, Any]:
        """Perform policy checks on certificate"""
        errors = []
        warnings = []
        
        # Check expiry
        not_after = datetime.fromisoformat(cert_info['not_after'])
        if datetime.now(timezone.utc) > not_after:
            errors.append("Certificate expired")
        
        # Check key size
        if 'RSA' in cert_info['key_type'] and cert_info['key_size'] < self.MIN_RSA_KEY_SIZE:
            errors.append(f"RSA key too small: {cert_info['key_size']} < {self.MIN_RSA_KEY_SIZE}")
        
        # Check signature algorithm
        sig_alg_lower = cert_info['signature_algorithm'].lower()
        for forbidden in self.FORBIDDEN_SIG_ALGS:
            if forbidden in sig_alg_lower:
                errors.append(f"Forbidden signature algorithm: {cert_info['signature_algorithm']}")
        
        # Check EKU constraints
        if context and context.get('type') == 'code_signing':
            eku = cert_info.get('extended_key_usage', [])
            if 'codeSigning' not in eku and eku:
                warnings.append("Certificate not intended for code signing")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def validate_chain(self, cert_pem: str, intermediates: List[str] = None, context: Dict = None) -> Dict[str, Any]:
        """Main validation entry point"""
        try:
            # Parse leaf certificate
            leaf_cert = self.parse_certificate(cert_pem)
            
            # Build chain
            chain = self.build_chain(leaf_cert, intermediates)
            
            # Verify signatures
            sig_result = self.verify_chain(chain)
            
            # Check policy
            policy_result = self.check_policy(leaf_cert, context)
            
            # Calculate score
            score = 100
            if not sig_result['valid']:
                score -= 50
            if not policy_result['valid']:
                score -= 30
            if policy_result['warnings']:
                score -= 10
            
            return {
                'verdict': 'valid' if sig_result['valid'] and policy_result['valid'] else 'invalid',
                'cert_score': max(score, 0),
                'chain': [c['fingerprint'] for c in chain],
                'chain_length': len(chain),
                'leaf_cert': {
                    'subject': leaf_cert['subject'],
                    'issuer': leaf_cert['issuer'],
                    'not_after': leaf_cert['not_after'],
                    'fingerprint': leaf_cert['fingerprint']
                },
                'signature_verification': sig_result,
                'policy_check': policy_result,
                'errors': sig_result['errors'] + policy_result['errors']
            }
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                'verdict': 'error',
                'cert_score': 0,
                'errors': [str(e)]
            }
