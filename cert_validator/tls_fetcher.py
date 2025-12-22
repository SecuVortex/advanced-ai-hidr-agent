"""
TLS Certificate Fetcher
Fetches server certificates from TLS endpoints
"""
import ssl
import socket
import logging
from typing import Dict, List, Optional, Any
from cryptography import x509
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger('HIDR.CertValidator.TLS')

class TLSCertFetcher:
    """Fetch certificates from TLS endpoints"""
    
    def __init__(self, timeout=5):
        self.timeout = timeout
    
    def fetch_cert_chain(self, host: str, port: int = 443) -> Dict[str, Any]:
        """Fetch certificate chain from TLS endpoint"""
        try:
            logger.info(f"Fetching TLS cert from {host}:{port}")
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    # Get DER-encoded certificate
                    der_cert = ssock.getpeercert(binary_form=True)
                    
                    # Parse certificate
                    cert = x509.load_der_x509_certificate(der_cert, default_backend())
                    
                    # Convert to PEM
                    from cryptography.hazmat.primitives import serialization
                    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
                    
                    return {
                        'success': True,
                        'cert_pem': cert_pem,
                        'host': host,
                        'port': port,
                        'protocol': ssock.version(),
                        'cipher': ssock.cipher()[0] if ssock.cipher() else None
                    }
        
        except socket.timeout:
            logger.error(f"TLS fetch timeout for {host}:{port}")
            return {
                'success': False,
                'error': 'Connection timeout',
                'host': host,
                'port': port
            }
        
        except Exception as e:
            logger.error(f"TLS fetch failed for {host}:{port}: {e}")
            return {
                'success': False,
                'error': str(e),
                'host': host,
                'port': port
            }
    
    def fetch_with_intermediates(self, host: str, port: int = 443) -> Dict[str, Any]:
        """Fetch full certificate chain including intermediates"""
        try:
            # Fetch leaf certificate
            result = self.fetch_cert_chain(host, port)
            
            if not result['success']:
                return result
            
            # In production, would fetch intermediate certs from AIA extension
            # For now, return leaf only
            result['intermediates'] = []
            result['chain_complete'] = False
            
            return result
        
        except Exception as e:
            logger.error(f"TLS chain fetch failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'host': host,
                'port': port
            }
