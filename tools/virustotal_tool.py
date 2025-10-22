import requests
import time
from typing import Dict, Any, Optional
from agents.config import Config


class VirusTotalTool:

    def __init__(self, api_key: Optional[str]=None):
        self.api_key = api_key or Config.VIRUSTOTAL_API_KEY
        self.base_url = 'https://www.virustotal.com/api/v3'
        self.cache = {}
        self.last_request_time = 0
        self.min_request_interval = 15

    def query_file_hash(self, file_hash: str) ->Dict[str, Any]:
        if not self.api_key or self.api_key == 'your_virustotal_api_key_here':
            return {'error': 'No API key configured', 'malicious': 0,
                'suspicious': 0, 'harmless': 0, 'undetected': 0, 'cached':
                False}
        if file_hash in self.cache:
            cached_result = self.cache[file_hash].copy()
            cached_result['cached'] = True
            return cached_result
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            return {'error': 'Rate limit - using local analysis only',
                'malicious': 0, 'suspicious': 0, 'harmless': 0,
                'undetected': 0, 'cached': False}
        try:
            url = f'{self.base_url}/files/{file_hash}'
            headers = {'x-apikey': self.api_key}
            self.last_request_time = time.time()
            response = requests.get(url, headers=headers, timeout=Config.
                API_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get(
                    'last_analysis_stats', {})
                result = {'malicious': stats.get('malicious', 0),
                    'suspicious': stats.get('suspicious', 0), 'harmless':
                    stats.get('harmless', 0), 'undetected': stats.get(
                    'undetected', 0), 'total_scans': sum(stats.values()) if
                    stats else 0, 'scan_date': data.get('data', {}).get(
                    'attributes', {}).get('last_analysis_date'),
                    'file_type': data.get('data', {}).get('attributes', {})
                    .get('type_description'), 'names': data.get('data', {})
                    .get('attributes', {}).get('names', []), 'cached': False}
                self.cache[file_hash] = result.copy()
                return result
            elif response.status_code == 404:
                result = {'error': 'File not found in VirusTotal database',
                    'malicious': 0, 'suspicious': 0, 'harmless': 0,
                    'undetected': 0, 'cached': False}
                self.cache[file_hash] = result.copy()
                return result
            elif response.status_code == 429:
                return {'error':
                    'Rate limit exceeded - free tier limit reached',
                    'malicious': 0, 'suspicious': 0, 'harmless': 0,
                    'undetected': 0, 'cached': False}
            else:
                return {'error': f'API error: {response.status_code}',
                    'malicious': 0, 'suspicious': 0, 'harmless': 0,
                    'undetected': 0, 'cached': False}
        except requests.Timeout:
            return {'error': 'Request timeout', 'malicious': 0,
                'suspicious': 0, 'harmless': 0, 'undetected': 0, 'cached':
                False}
        except Exception as e:
            return {'error': str(e), 'malicious': 0, 'suspicious': 0,
                'harmless': 0, 'undetected': 0, 'cached': False}

    def calculate_reputation_score(self, vt_result: Dict[str, Any]) ->float:
        malicious = vt_result.get('malicious', 0)
        suspicious = vt_result.get('suspicious', 0)
        total = vt_result.get('total_scans', 1)
        if total == 0:
            return 0.0
        score = (malicious * 1.0 + suspicious * 0.5) / total * 10
        return min(score, 10.0)

    def is_known_malware(self, vt_result: Dict[str, Any], threshold: int=1
        ) ->bool:
        return vt_result.get('malicious', 0) >= threshold
