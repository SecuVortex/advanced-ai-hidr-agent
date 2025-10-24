"""
YARA Scanner Module
Scans files and processes for malware signatures
"""
import yara
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger('HIDR.YaraScanner')

class YaraScanner:
    """YARA-based malware scanner"""
    
    def __init__(self, rules_dir: str = "yara_rules"):
        """Initialize YARA scanner with rules directory"""
        self.rules_dir = Path(rules_dir)
        self.rules = None
        self.rules_count = 0
        self.load_rules()
    
    def load_rules(self) -> bool:
        """Load all YARA rules from directory"""
        try:
            if not self.rules_dir.exists():
                logger.error(f"YARA rules directory not found: {self.rules_dir}")
                return False
            
            rule_files = {}
            for rule_file in self.rules_dir.glob("*.yar"):
                namespace = rule_file.stem
                rule_files[namespace] = str(rule_file)
                logger.debug(f"Found YARA rule file: {rule_file}")
            
            if not rule_files:
                logger.warning("No YARA rule files found")
                return False
            
            self.rules = yara.compile(filepaths=rule_files)
            self.rules_count = len(rule_files)
            logger.info(f"Loaded {self.rules_count} YARA rule files")
            return True
            
        except yara.Error as e:
            logger.error(f"YARA compilation error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load YARA rules: {e}")
            return False
    
    def _get_file_size_mb(self, filepath: str) -> float:
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(filepath)
            size_mb = size_bytes / (1024 * 1024)
            return size_mb
        except Exception as e:
            logger.error(f"Failed to get file size: {e}")
            return 0.0
    
    def scan_file(self, filepath: str, timeout: int = 5, config: Dict = None) -> Dict:
        """
        Scan a file with YARA rules
        
        Args:
            filepath: Path to file to scan
            timeout: Scan timeout in seconds
            config: Optional config dict with skip_large_files settings
            
        Returns:
            Dict with matches, threat_score, and details
        """
        if not self.rules:
            return {'matches': [], 'threat_score': 0, 'error': 'No rules loaded'}
        
        try:
            if not os.path.exists(filepath):
                return {'matches': [], 'threat_score': 0, 'error': 'File not found'}
            
            if not os.path.isfile(filepath):
                return {'matches': [], 'threat_score': 0, 'error': 'Not a file'}
            
            # Check file size if configured
            if config and config.get('skip_large_files', False):
                max_size_mb = config.get('max_file_size_mb', 50)
                file_size_mb = self._get_file_size_mb(filepath)
                
                if file_size_mb > max_size_mb:
                    if config.get('log_skipped_files', False):
                        logger.info(f"Skipping large file: {filepath} ({file_size_mb:.1f}MB)")
                    return {
                        'matches': [],
                        'threat_score': 0,
                        'skipped': True,
                        'reason': f'File too large ({file_size_mb:.1f}MB > {max_size_mb}MB)'
                    }
            
            matches = self.rules.match(filepath, timeout=timeout)
            
            match_details = []
            for match in matches:
                severity = match.meta.get('severity', 'medium')
                mitre = match.meta.get('mitre', '')
                description = match.meta.get('description', match.rule)
                
                match_details.append({
                    'rule': match.rule,
                    'namespace': match.namespace,
                    'severity': severity,
                    'mitre': mitre,
                    'description': description,
                    'tags': match.tags
                })
            
            threat_score = self._calculate_threat_score(match_details)
            
            return {
                'matches': match_details,
                'match_count': len(match_details),
                'threat_score': threat_score,
                'file': filepath
            }
            
        except yara.TimeoutError:
            logger.warning(f"YARA scan timeout: {filepath}")
            return {'matches': [], 'threat_score': 0, 'error': 'Scan timeout'}
        except yara.Error as e:
            logger.error(f"YARA scan error: {e}")
            return {'matches': [], 'threat_score': 0, 'error': str(e)}
        except Exception as e:
            logger.error(f"File scan failed: {e}")
            return {'matches': [], 'threat_score': 0, 'error': str(e)}
    
    def scan_process(self, pid: int) -> Dict:
        """
        Scan a running process (requires admin privileges)
        
        Args:
            pid: Process ID to scan
            
        Returns:
            Dict with matches and threat_score
        """
        if not self.rules:
            return {'matches': [], 'threat_score': 0, 'error': 'No rules loaded'}
        
        try:
            matches = self.rules.match(pid=pid)
            
            match_details = []
            for match in matches:
                severity = match.meta.get('severity', 'medium')
                mitre = match.meta.get('mitre', '')
                description = match.meta.get('description', match.rule)
                
                match_details.append({
                    'rule': match.rule,
                    'namespace': match.namespace,
                    'severity': severity,
                    'mitre': mitre,
                    'description': description
                })
            
            threat_score = self._calculate_threat_score(match_details)
            
            return {
                'matches': match_details,
                'match_count': len(match_details),
                'threat_score': threat_score,
                'pid': pid
            }
            
        except yara.Error as e:
            logger.debug(f"Process scan failed (PID {pid}): {e}")
            return {'matches': [], 'threat_score': 0, 'error': str(e)}
        except Exception as e:
            logger.debug(f"Process scan error (PID {pid}): {e}")
            return {'matches': [], 'threat_score': 0, 'error': str(e)}
    
    def _calculate_threat_score(self, matches: List[Dict]) -> int:
        """
        Calculate threat score based on YARA matches
        
        Args:
            matches: List of match dictionaries
            
        Returns:
            Threat score 0-10
        """
        if not matches:
            return 0
        
        severity_weights = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        total_score = 0
        for match in matches:
            severity = match.get('severity', 'medium').lower()
            weight = severity_weights.get(severity, 2)
            total_score += weight
        
        normalized_score = min(total_score, 10)
        return normalized_score
    
    def get_mitre_techniques(self, matches: List[Dict]) -> List[str]:
        """
        Extract MITRE ATT&CK techniques from matches
        
        Args:
            matches: List of match dictionaries
            
        Returns:
            List of unique MITRE technique IDs
        """
        techniques = set()
        for match in matches:
            mitre = match.get('mitre', '')
            if mitre:
                techniques.add(mitre)
        return sorted(list(techniques))
    
    def get_rules_info(self) -> Dict:
        """Get information about loaded rules"""
        return {
            'rules_dir': str(self.rules_dir),
            'rules_loaded': self.rules is not None,
            'rules_count': self.rules_count
        }
