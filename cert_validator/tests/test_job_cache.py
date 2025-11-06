"""
Unit tests for job queue and caching
"""
import pytest
import time
from unittest.mock import Mock
from datetime import datetime, timedelta, timezone

from cert_validator.job_queue import JobQueue, JobStatus, ValidationJob
from cert_validator.cache import ValidationCache

def test_validation_job_creation():
    """Test validation job creation"""
    job = ValidationJob("test-123", "cert_pem", [], {})
    
    assert job.job_id == "test-123"
    assert job.status == JobStatus.PENDING
    assert job.result is None

def test_job_queue_init():
    """Test job queue initialization"""
    mock_validator = Mock()
    queue = JobQueue(mock_validator, max_workers=2)
    
    assert queue.max_workers == 2
    assert not queue.running

def test_job_queue_submit():
    """Test job submission"""
    mock_validator = Mock()
    queue = JobQueue(mock_validator)
    
    job_id = queue.submit_job("cert_pem", [], {})
    
    assert job_id in queue.jobs
    assert queue.jobs[job_id].status == JobStatus.PENDING

def test_job_queue_get_status():
    """Test getting job status"""
    mock_validator = Mock()
    queue = JobQueue(mock_validator)
    
    job_id = queue.submit_job("cert_pem", [], {})
    status = queue.get_job_status(job_id)
    
    assert status is not None
    assert status['job_id'] == job_id
    assert status['status'] == 'pending'

def test_cache_init():
    """Test cache initialization"""
    cache = ValidationCache(default_ttl=3600)
    
    assert cache.default_ttl == 3600
    assert cache.hits == 0
    assert cache.misses == 0

def test_cache_set_get():
    """Test cache set and get"""
    cache = ValidationCache()
    
    cache.set("key1", {"result": "valid"}, ttl=60)
    result = cache.get("key1")
    
    assert result is not None
    assert result['result'] == 'valid'
    assert cache.hits == 1

def test_cache_miss():
    """Test cache miss"""
    cache = ValidationCache()
    
    result = cache.get("nonexistent")
    
    assert result is None
    assert cache.misses == 1

def test_cache_expiry():
    """Test cache expiry"""
    cache = ValidationCache()
    
    # Set with 1 second TTL
    cache.set("key1", {"result": "valid"}, ttl=1)
    
    # Should hit
    result1 = cache.get("key1")
    assert result1 is not None
    
    # Wait for expiry
    time.sleep(1.1)
    
    # Should miss
    result2 = cache.get("key1")
    assert result2 is None

def test_cache_stats():
    """Test cache statistics"""
    cache = ValidationCache()
    
    cache.set("key1", {"data": 1})
    cache.get("key1")  # hit
    cache.get("key2")  # miss
    
    stats = cache.get_stats()
    
    assert stats['hits'] == 1
    assert stats['misses'] == 1
    assert stats['size'] == 1
    assert stats['hit_rate'] == 50.0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
