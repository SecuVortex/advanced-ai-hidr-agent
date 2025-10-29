"""Feature Extraction - Phase 3 Task 3.1"""
import psutil
import os
import logging

logger = logging.getLogger('HIDR.FeatureExtractor')

class FeatureExtractor:
    def extract(self, pid, proc_name, path, cmdline):
        """Extract features from process"""
        features = {}
        
        try:
            proc = psutil.Process(pid)
            
            # Basic features
            features['name_length'] = len(proc_name)
            features['path_is_trusted'] = 1 if self._is_trusted(path) else 0
            features['cmdline_length'] = len(cmdline)
            
            # Resource usage
            features['cpu_percent'] = proc.cpu_percent(interval=0.1)
            features['memory_mb'] = proc.memory_info().rss / (1024 * 1024)
            features['num_threads'] = proc.num_threads()
            
            # Connections
            try:
                features['num_connections'] = len(proc.connections())
            except:
                features['num_connections'] = 0
            
            # File info
            features['has_signature'] = 1 if os.path.exists(path) else 0
            
            # Parent process
            try:
                parent = proc.parent()
                features['parent_is_trusted'] = 1 if parent and self._is_trusted(parent.exe()) else 0
            except:
                features['parent_is_trusted'] = 0
            
            # Normalize
            features['cpu_percent'] = min(features['cpu_percent'] / 100, 1.0)
            features['memory_mb'] = min(features['memory_mb'] / 1000, 1.0)
            features['num_threads'] = min(features['num_threads'] / 100, 1.0)
            features['num_connections'] = min(features['num_connections'] / 50, 1.0)
            features['name_length'] = min(features['name_length'] / 50, 1.0)
            features['cmdline_length'] = min(features['cmdline_length'] / 500, 1.0)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            features = {k: 0 for k in ['name_length', 'path_is_trusted', 'cmdline_length', 
                                       'cpu_percent', 'memory_mb', 'num_threads', 
                                       'num_connections', 'has_signature', 'parent_is_trusted']}
        
        return features
    
    def _is_trusted(self, path):
        if not path:
            return False
        path_lower = path.lower()
        trusted = ['c:\\windows\\', 'c:\\program files\\', '/usr/bin/', '/usr/sbin/']
        return any(t in path_lower for t in trusted)
