"""
VirusTotal Integration Tool
Provides threat intelligence from VirusTotal API.
Optimized for free tier with caching and rate limiting.
"""

import requests
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('HIDR.VirusTotal')


class VirusTotalTool:
    """VirusTotal API integration with free tier optimizations"""
    
    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            try:
                from agents.config import Config
                api_key = Config.VIRUSTOTAL_API_KEY
            except:
                api_key = ""
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.cache = {}
        self.last_request_time = 0
        self.min_request_interval = 15
    
    def query_file_hash(self, file_hash: str, use_resilience: bool = False) -> Dict[str, Any]:
        """
        Query VirusTotal for file hash reputation (with caching for free tier)
        
        Args:
            file_hash: SHA256 file hash
            
        Returns:
            Dictionary with analysis results
        """
        if not self.api_key or self.api_key == "your_virustotal_api_key_here":
            return {
                "error": "No API key configured",
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "cached": False
            }
        
        if use_resilience:
            try:
                from core.resilience import resilience
                return resilience.call_with_resilience(
                    self._query_internal,
                    file_hash,
                    max_attempts=2,
                    circuit_breaker_name='virustotal'
                )
            except Exception as e:
                logger.error(f"VirusTotal with resilience failed: {e}")
                return {"error": str(e), "malicious": 0, "suspicious": 0, "harmless": 0, "undetected": 0, "cached": False}
        
        return self._query_internal(file_hash)
    
    def _query_internal(self, file_hash: str) -> Dict[str, Any]:
        """Internal query method"""
        # Check cache first
        if file_hash in self.cache:
            cached_result = self.cache[file_hash].copy()
            cached_result['cached'] = True
            return cached_result
        
        # Rate limiting for free tier
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            return {
                "error": "Rate limit - using local analysis only",
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "cached": False
            }
        
        try:
            url = f"{self.base_url}/files/{file_hash}"
            headers = {"x-apikey": self.api_key}
            
            self.last_request_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                
                result = {
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0),
                    "undetected": stats.get("undetected", 0),
                    "total_scans": sum(stats.values()) if stats else 0,
                    "scan_date": data.get("data", {}).get("attributes", {}).get("last_analysis_date"),
                    "file_type": data.get("data", {}).get("attributes", {}).get("type_description"),
                    "names": data.get("data", {}).get("attributes", {}).get("names", []),
                    "cached": False
                }
                # Cache the result
                self.cache[file_hash] = result.copy()
                return result
            elif response.status_code == 404:
                result = {
                    "error": "File not found in VirusTotal database",
                    "malicious": 0,
                    "suspicious": 0,
                    "harmless": 0,
                    "undetected": 0,
                    "cached": False
                }
                self.cache[file_hash] = result.copy()
                return result
            elif response.status_code == 429:
                return {
                    "error": "Rate limit exceeded - free tier limit reached",
                    "malicious": 0,
                    "suspicious": 0,
                    "harmless": 0,
                    "undetected": 0,
                    "cached": False
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "malicious": 0,
                    "suspicious": 0,
                    "harmless": 0,
                    "undetected": 0,
                    "cached": False
                }
        
        except requests.Timeout:
            return {
                "error": "Request timeout",
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "cached": False
            }
        except Exception as e:
            return {
                "error": str(e),
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "cached": False
            }
    
    def calculate_reputation_score(self, vt_result: Dict[str, Any]) -> float:
        """
        Calculate reputation score from VirusTotal results
        
        Args:
            vt_result: VirusTotal query result
            
        Returns:
            Reputation score (0-10, higher is more malicious)
        """
        malicious = vt_result.get("malicious", 0)
        suspicious = vt_result.get("suspicious", 0)
        total = vt_result.get("total_scans", 1)
        
        if total == 0:
            return 0.0
        
        # Calculate weighted score
        score = (malicious * 1.0 + suspicious * 0.5) / total * 10
        return min(score, 10.0)
    
    def is_known_malware(self, vt_result: Dict[str, Any], threshold: int = 1) -> bool:
        """
        Check if file is known malware
        
        Args:
            vt_result: VirusTotal query result
            threshold: Minimum detections to consider malware
            
        Returns:
            True if known malware
        """
        return vt_result.get("malicious", 0) >= threshold
