"""
Prometheus Metrics for Certificate Validator
"""
import logging
from typing import Dict, Any
from datetime import datetime, timezone
from collections import defaultdict
from threading import Lock

logger = logging.getLogger('HIDR.CertValidator.Metrics')

class MetricsCollector:
    """Collect and expose Prometheus-style metrics"""
    
    def __init__(self):
        self.lock = Lock()
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.last_reset = datetime.now(timezone.utc)
    
    def increment_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.gauges[key] = value
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a histogram value"""
        with self.lock:
            key = self._make_key(name, labels)
            self.histograms[key].append(value)
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create metric key with labels"""
        if not labels:
            return name
        label_str = ','.join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_metrics_text(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        
        # Counters
        for key, value in self.counters.items():
            lines.append(f"{key} {value}")
        
        # Gauges
        for key, value in self.gauges.items():
            lines.append(f"{key} {value}")
        
        # Histograms (simplified - just count and sum)
        for key, values in self.histograms.items():
            if values:
                lines.append(f"{key}_count {len(values)}")
                lines.append(f"{key}_sum {sum(values)}")
        
        return '\n'.join(lines)
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary"""
        with self.lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {k: {'count': len(v), 'sum': sum(v)} for k, v in self.histograms.items()},
                'last_reset': self.last_reset.isoformat()
            }
    
    def reset(self):
        """Reset all metrics"""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.last_reset = datetime.now(timezone.utc)

# Global metrics instance
metrics = MetricsCollector()

# Metric recording functions
def record_validation(verdict: str, duration: float):
    """Record a validation event"""
    metrics.increment_counter('certs_validated_total', labels={'verdict': verdict})
    metrics.observe_histogram('cert_validation_duration_seconds', duration)

def record_revocation_check(method: str, status: str):
    """Record a revocation check"""
    metrics.increment_counter('revocation_checks_total', labels={'method': method, 'status': status})

def record_ocsp_request(success: bool):
    """Record an OCSP request"""
    status = 'success' if success else 'failure'
    metrics.increment_counter('ocsp_requests_total', labels={'status': status})

def record_crl_request(success: bool):
    """Record a CRL request"""
    status = 'success' if success else 'failure'
    metrics.increment_counter('crl_requests_total', labels={'status': status})

def record_ct_check(present: bool):
    """Record a CT check"""
    status = 'present' if present else 'missing'
    metrics.increment_counter('ct_checks_total', labels={'status': status})

def record_cache_hit(hit: bool):
    """Record a cache access"""
    status = 'hit' if hit else 'miss'
    metrics.increment_counter('cert_cache_total', labels={'status': status})

def set_queue_size(size: int):
    """Set current queue size"""
    metrics.set_gauge('cert_validation_queue_size', size)

def set_cache_size(size: int):
    """Set current cache size"""
    metrics.set_gauge('cert_cache_size', size)
