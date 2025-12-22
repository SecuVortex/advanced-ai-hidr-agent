"""
Caching layer for certificate validation results
Simplified in-memory cache (production would use Redis)
"""
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from threading import Lock

logger = logging.getLogger('HIDR.CertValidator.Cache')

class ValidationCache:
    """In-memory cache for validation results"""
    
    def __init__(self, default_ttl=86400):  # 24 hours default
        self.cache = {}
        self.lock = Lock()
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check expiry
                if datetime.now(timezone.utc) < entry['expires']:
                    self.hits += 1
                    logger.debug(f"Cache hit: {key}")
                    return entry['data']
                else:
                    # Expired
                    del self.cache[key]
                    logger.debug(f"Cache expired: {key}")
            
            self.misses += 1
            return None
    
    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None):
        """Set cached result"""
        with self.lock:
            expires = datetime.now(timezone.utc) + timedelta(seconds=ttl or self.default_ttl)
            self.cache[key] = {
                'data': data,
                'expires': expires,
                'cached_at': datetime.now(timezone.utc)
            }
            logger.debug(f"Cache set: {key} (TTL: {ttl or self.default_ttl}s)")
    
    def delete(self, key: str):
        """Delete cached entry"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache delete: {key}")
    
    def clear(self):
        """Clear all cache"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cache cleared: {count} entries")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        with self.lock:
            now = datetime.now(timezone.utc)
            to_remove = [k for k, v in self.cache.items() if now >= v['expires']]
            
            for key in to_remove:
                del self.cache[key]
            
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
