"""Behavioral Analysis - Phase 3 Task 3.4"""
import psutil
import time
import logging

logger = logging.getLogger('HIDR.BehavioralAnalyzer')

class BehavioralAnalyzer:
    def __init__(self):
        self.patterns = {
            'ransomware': {'file_ops': 100, 'cpu_high': 0.7},
            'keylogger': {'connections': 5, 'cpu_low': 0.1},
            'cryptominer': {'cpu_high': 0.8, 'memory_high': 0.6}
        }
    
    def analyze(self, pid, proc_name, path):
        """Analyze process behavior"""
        behavior_score = 0
        detected_patterns = []
        
        try:
            proc = psutil.Process(pid)
            
            # CPU usage pattern
            cpu = proc.cpu_percent(interval=0.5)
            if cpu > 70:
                behavior_score += 0.3
                detected_patterns.append('high_cpu')
            
            # Memory usage
            mem = proc.memory_percent()
            if mem > 50:
                behavior_score += 0.2
                detected_patterns.append('high_memory')
            
            # Network connections
            try:
                conns = len(proc.connections())
                if conns > 10:
                    behavior_score += 0.3
                    detected_patterns.append('many_connections')
            except:
                pass
            
            # File handles
            try:
                handles = proc.num_handles() if hasattr(proc, 'num_handles') else 0
                if handles > 500:
                    behavior_score += 0.2
                    detected_patterns.append('many_handles')
            except:
                pass
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {e}")
        
        return {
            'behavior_score': min(behavior_score, 1.0),
            'patterns': detected_patterns,
            'threat_type': self._classify_threat(detected_patterns)
        }
    
    def _classify_threat(self, patterns):
        """Classify threat type based on patterns"""
        if 'high_cpu' in patterns and 'high_memory' in patterns:
            return 'cryptominer'
        elif 'many_connections' in patterns:
            return 'keylogger'
        elif 'many_handles' in patterns:
            return 'ransomware'
        return 'unknown'
