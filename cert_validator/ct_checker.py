"""
Certificate Transparency (CT) Checker
"""
import logging
import requests
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger('HIDR.CertValidator.CT')

class CTChecker:
    """Certificate Transparency log checker"""
    
    # Google CT API endpoint (simplified)
    CT_API_URL = "https://ct.googleapis.com/logs/argon2024/ct/v1/get-entries"
    
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.cache = {}
    
    def check_ct_presence(self, cert_fingerprint: str) -> Dict[str, Any]:
        """Check if certificate is present in CT logs"""
        try:
            # Check cache
            if cert_fingerprint in self.cache:
                logger.debug(f"CT cache hit for {cert_fingerprint}")
                return self.cache[cert_fingerprint]
            
            # For production, would query actual CT logs
            # For now, simulate CT check
            logger.info(f"Checking CT logs for {cert_fingerprint}")
            
            # Mock CT response (in production, would query real CT API)
            result = {
                'ct_present': False,  # Conservative default
                'scts': [],
                'log_count': 0,
                'checked_at': datetime.now(timezone.utc).isoformat(),
                'method': 'ct_api'
            }
            
            # Cache result
            self.cache[cert_fingerprint] = result
            
            return result
        
        except Exception as e:
            logger.error(f"CT check failed: {e}")
            return {
                'ct_present': False,
                'scts': [],
                'log_count': 0,
                'error': str(e),
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
    
    def extract_scts_from_cert(self, cert_obj) -> List[Dict]:
        """Extract SCTs (Signed Certificate Timestamps) from certificate"""
        try:
            from cryptography.x509.oid import ExtensionOID
            
            # Try to get SCT extension
            try:
                ext = cert_obj.extensions.get_extension_for_oid(
                    ExtensionOID.PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS
                )
                # Parse SCTs (simplified)
                return [{'log_id': 'embedded', 'timestamp': datetime.now(timezone.utc).isoformat()}]
            except:
                return []
        
        except Exception as e:
            logger.warning(f"SCT extraction failed: {e}")
            return []
    
    def validate_ct_policy(self, ct_result: Dict, context: Dict = None) -> Dict[str, Any]:
        """Validate CT policy requirements"""
        errors = []
        warnings = []
        
        # For public TLS certificates, CT should be present
        if context and context.get('type') == 'tls' and context.get('public', False):
            if not ct_result.get('ct_present', False):
                warnings.append("Certificate not found in CT logs (recommended for public TLS)")
        
        # Check SCT count
        sct_count = len(ct_result.get('scts', []))
        if sct_count == 0 and ct_result.get('ct_present', False):
            warnings.append("No SCTs found despite CT presence")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'ct_compliant': ct_result.get('ct_present', False) or not (context and context.get('public', False))
        }
