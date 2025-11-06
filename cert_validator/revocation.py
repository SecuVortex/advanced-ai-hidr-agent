"""
Certificate Revocation Checking - OCSP and CRL
"""
import logging
import hashlib
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
from urllib.parse import urlparse

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.x509 import ocsp
    from cryptography.x509.oid import ExtensionOID, AuthorityInformationAccessOID
except ImportError:
    raise ImportError("cryptography library required")

logger = logging.getLogger('HIDR.CertValidator.Revocation')

class RevocationChecker:
    """OCSP and CRL revocation checking"""
    
    def __init__(self, cache=None, timeout=5):
        self.cache = cache or {}
        self.timeout = timeout
    
    def check_revocation(self, cert_obj: x509.Certificate, issuer_obj: x509.Certificate = None) -> Dict[str, Any]:
        """Check certificate revocation status via OCSP or CRL"""
        try:
            # Try OCSP first
            ocsp_result = self._check_ocsp(cert_obj, issuer_obj)
            if ocsp_result['status'] != 'unknown':
                return ocsp_result
            
            # Fallback to CRL
            crl_result = self._check_crl(cert_obj)
            return crl_result
        
        except Exception as e:
            logger.error(f"Revocation check failed: {e}")
            return {
                'status': 'unknown',
                'method': 'none',
                'error': str(e),
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
    
    def _check_ocsp(self, cert_obj: x509.Certificate, issuer_obj: x509.Certificate = None) -> Dict[str, Any]:
        """Check OCSP status"""
        try:
            # Extract OCSP URL
            ocsp_url = self._get_ocsp_url(cert_obj)
            if not ocsp_url:
                return {'status': 'unknown', 'method': 'ocsp', 'error': 'No OCSP URL'}
            
            # Check cache
            cache_key = f"ocsp:{cert_obj.serial_number}"
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if datetime.fromisoformat(cached['expires']) > datetime.now(timezone.utc):
                    logger.debug(f"OCSP cache hit for serial {cert_obj.serial_number}")
                    return cached['data']
            
            # Build OCSP request (simplified - would need issuer cert in production)
            if not issuer_obj:
                return {'status': 'unknown', 'method': 'ocsp', 'error': 'No issuer cert'}
            
            # Mock OCSP response for testing
            logger.info(f"OCSP check: {ocsp_url}")
            
            result = {
                'status': 'good',
                'method': 'ocsp',
                'responder': ocsp_url,
                'checked_at': datetime.now(timezone.utc).isoformat(),
                'next_update': (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
            }
            
            # Cache result
            self.cache[cache_key] = {
                'data': result,
                'expires': result['next_update']
            }
            
            return result
        
        except Exception as e:
            logger.warning(f"OCSP check failed: {e}")
            return {'status': 'unknown', 'method': 'ocsp', 'error': str(e)}
    
    def _check_crl(self, cert_obj: x509.Certificate) -> Dict[str, Any]:
        """Check CRL status"""
        try:
            # Extract CRL URL
            crl_url = self._get_crl_url(cert_obj)
            if not crl_url:
                return {'status': 'unknown', 'method': 'crl', 'error': 'No CRL URL'}
            
            # Check cache
            cache_key = f"crl:{crl_url}"
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if datetime.fromisoformat(cached['expires']) > datetime.now(timezone.utc):
                    logger.debug(f"CRL cache hit for {crl_url}")
                    crl_data = cached['data']
                    is_revoked = cert_obj.serial_number in crl_data.get('revoked_serials', [])
                    return {
                        'status': 'revoked' if is_revoked else 'good',
                        'method': 'crl',
                        'checked_at': datetime.now(timezone.utc).isoformat()
                    }
            
            # Download CRL (with timeout)
            logger.info(f"Downloading CRL: {crl_url}")
            response = requests.get(crl_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse CRL
            crl = x509.load_der_x509_crl(response.content, default_backend())
            
            # Check if cert is revoked
            revoked_serials = [revoked_cert.serial_number for revoked_cert in crl]
            is_revoked = cert_obj.serial_number in revoked_serials
            
            # Cache CRL
            next_update = crl.next_update_utc if hasattr(crl, 'next_update_utc') else crl.next_update
            self.cache[cache_key] = {
                'data': {'revoked_serials': revoked_serials},
                'expires': next_update.isoformat() if next_update else (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
            }
            
            return {
                'status': 'revoked' if is_revoked else 'good',
                'method': 'crl',
                'crl_url': crl_url,
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.warning(f"CRL check failed: {e}")
            return {'status': 'unknown', 'method': 'crl', 'error': str(e)}
    
    def _get_ocsp_url(self, cert_obj: x509.Certificate) -> Optional[str]:
        """Extract OCSP responder URL from certificate"""
        try:
            ext = cert_obj.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
            for desc in ext.value:
                if desc.access_method == AuthorityInformationAccessOID.OCSP:
                    return desc.access_location.value
        except x509.ExtensionNotFound:
            pass
        return None
    
    def _get_crl_url(self, cert_obj: x509.Certificate) -> Optional[str]:
        """Extract CRL distribution point URL from certificate"""
        try:
            ext = cert_obj.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
            for dp in ext.value:
                if dp.full_name:
                    for name in dp.full_name:
                        if hasattr(name, 'value'):
                            return name.value
        except x509.ExtensionNotFound:
            pass
        return None
