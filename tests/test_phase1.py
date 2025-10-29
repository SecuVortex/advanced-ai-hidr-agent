"""
Test Phase 1: Real-Time Foundation
"""
import pytest
import time
from core.background_monitor import BackgroundMonitor
from core.event_queue import EventQueue

class TestBackgroundMonitor:
    def test_initialization(self):
        """Test monitor initialization"""
        events = []
        monitor = BackgroundMonitor(lambda e: events.append(e), interval=1)
        assert monitor.interval == 1
        assert not monitor.running
    
    def test_start_stop(self):
        """Test monitor start/stop"""
        events = []
        monitor = BackgroundMonitor(lambda e: events.append(e), interval=1)
        
        monitor.start()
        assert monitor.running
        time.sleep(0.5)
        
        monitor.stop()
        assert not monitor.running
    
    def test_process_detection(self):
        """Test process detection"""
        events = []
        monitor = BackgroundMonitor(lambda e: events.append(e), interval=1)
        
        monitor.start()
        time.sleep(2)
        monitor.stop()
        
        # Should detect some processes
        assert len(events) > 0
        assert events[0]['type'] == 'PROCESS_DETECTED'
        assert 'pid' in events[0]
        assert 'name' in events[0]

class TestEventQueue:
    def test_initialization(self):
        """Test queue initialization"""
        queue = EventQueue(maxsize=100)
        assert queue.size() == 0
    
    def test_put_get(self):
        """Test put and get operations"""
        queue = EventQueue()
        
        event = {'type': 'THREAT_DETECTED', 'data': 'test'}
        queue.put(event)
        
        assert queue.size() == 1
        retrieved = queue.get()
        assert retrieved == event
    
    def test_get_all(self):
        """Test batch retrieval"""
        queue = EventQueue()
        
        for i in range(5):
            queue.put({'type': 'TEST', 'id': i})
        
        events = queue.get_all(max_events=10)
        assert len(events) == 5
        assert events[0]['id'] == 0
    
    def test_stats(self):
        """Test statistics"""
        queue = EventQueue()
        
        queue.put({'type': 'THREAT_DETECTED'})
        queue.put({'type': 'PROCESS_SCANNED'})
        queue.put({'type': 'THREAT_DETECTED'})
        
        stats = queue.get_stats()
        assert stats['event_counts']['THREAT_DETECTED'] == 2
        assert stats['event_counts']['PROCESS_SCANNED'] == 1

class TestIntegration:
    def test_monitor_queue_integration(self):
        """Test monitor and queue working together"""
        queue = EventQueue()
        monitor = BackgroundMonitor(lambda e: queue.put(e), interval=1)
        
        monitor.start()
        time.sleep(2)
        monitor.stop()
        
        events = queue.get_all()
        assert len(events) > 0
        assert all(e['type'] == 'PROCESS_DETECTED' for e in events)
