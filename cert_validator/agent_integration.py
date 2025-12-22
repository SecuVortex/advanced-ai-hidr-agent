"""
HIDR Agent Integration for Certificate Validation
Enriches process alerts with certificate validation data
"""
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger('HIDR.CertValidator.AgentIntegration')

class CertValidatorClient:
    """Client for calling cert validator API from HIDR agent"""
    
    def __init__(self, api_url: str = "http://localhost:8001", api_key: str = None):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key or "hidr-agent-key-12345"
        self.timeout = 2  # Fast timeout for sync calls
    
    def validate_pe_signature(self, cert_pem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PE file signature certificate"""
        try:
            response = requests.post(
                f"{self.api_url}/api/validate",
                json={
                    "type": "file_sig",
                    "cert_pem": cert_pem,
                    "intermediates": [],
                    "context": context
                },
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Validation API error: {response.status_code}")
                return self._fallback_result("API error")
        
        except requests.Timeout:
            logger.warning("Cert validation timeout, using fallback")
            return self._fallback_result("Timeout")
        
        except Exception as e:
            logger.error(f"Cert validation failed: {e}")
            return self._fallback_result(str(e))
    
    def _fallback_result(self, reason: str) -> Dict[str, Any]:
        """Fallback result when validation fails"""
        return {
            'verdict': 'unknown',
            'cert_score': 50,
            'confidence_breakdown': {'fallback': 50},
            'chain': [],
            'errors': [f"Validation unavailable: {reason}"]
        }
    
    def enrich_alert(self, alert: Dict[str, Any], cert_pem: Optional[str] = None) -> Dict[str, Any]:
        """Enrich HIDR alert with certificate validation"""
        if not cert_pem:
            # No certificate to validate
            return alert
        
        context = {
            'host': alert.get('host', 'unknown'),
            'pid': alert.get('pid', 0),
            'request_id': alert.get('request_id', 'unknown'),
            'type': 'code_signing'
        }
        
        # Validate certificate
        cert_result = self.validate_pe_signature(cert_pem, context)
        
        # Add cert_validation block to alert
        alert['cert_validation'] = {
            'verdict': cert_result['verdict'],
            'cert_score': cert_result['cert_score'],
            'confidence_breakdown': cert_result['confidence_breakdown'],
            'issuer': cert_result.get('leaf_cert', {}).get('issuer', 'Unknown'),
            'not_after': cert_result.get('leaf_cert', {}).get('not_after', 'Unknown'),
            'errors': cert_result.get('errors', []),
            'chain_length': len(cert_result.get('chain', []))
        }
        
        # Adjust overall threat score based on cert validation
        if cert_result['verdict'] == 'invalid':
            alert['threat_score'] = min(alert.get('threat_score', 0) + 2, 10)
            alert['reasons'] = alert.get('reasons', []) + ['Invalid certificate']
        elif cert_result['verdict'] == 'revoked':
            alert['threat_score'] = min(alert.get('threat_score', 0) + 5, 10)
            alert['reasons'] = alert.get('reasons', []) + ['Revoked certificate']
        
        return alert

def extract_pe_certificate(file_path: str) -> Optional[str]:
    """Extract certificate from PE file (stub implementation)"""
    try:
        # In production, would use pefile or similar to extract Authenticode signature
        # For now, return None (no cert extraction)
        logger.debug(f"Certificate extraction not implemented for {file_path}")
        return None
    except Exception as e:
        logger.error(f"Failed to extract certificate: {e}")
        return None
