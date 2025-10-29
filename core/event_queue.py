"""
Event Queue System - Thread-safe event handling
Phase 1, Task 1.2
"""
import queue
import logging
from typing import Dict, List, Optional

logger = logging.getLogger('HIDR.EventQueue')

class EventQueue:
    def __init__(self, maxsize: int = 1000):
        """
        Initialize event queue
        
        Args:
            maxsize: Maximum queue size (default: 1000)
        """
        self.queue = queue.Queue(maxsize=maxsize)
        self.event_count = {'THREAT_DETECTED': 0, 'PROCESS_SCANNED': 0, 'AGENT_LOG': 0}
        logger.info(f"EventQueue initialized (maxsize: {maxsize})")
    
    def put(self, event: Dict):
        """
        Add event to queue
        
        Args:
            event: Event dictionary with 'type' key
        """
        try:
            self.queue.put_nowait(event)
            event_type = event.get('type', 'UNKNOWN')
            if event_type in self.event_count:
                self.event_count[event_type] += 1
        except queue.Full:
            logger.warning("Event queue full, dropping event")
    
    def get(self, timeout: float = 0.1) -> Optional[Dict]:
        """
        Retrieve single event
        
        Args:
            timeout: Wait timeout in seconds
            
        Returns:
            Event dict or None if empty
        """
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_all(self, max_events: int = 100) -> List[Dict]:
        """
        Retrieve all pending events (batch)
        
        Args:
            max_events: Maximum events to retrieve
            
        Returns:
            List of event dicts
        """
        events = []
        for _ in range(max_events):
            event = self.get(timeout=0)
            if event is None:
                break
            events.append(event)
        return events
    
    def size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def get_stats(self) -> Dict:
        """Get event statistics"""
        return {
            'queue_size': self.size(),
            'event_counts': self.event_count.copy()
        }
