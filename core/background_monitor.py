"""
Background Monitoring Thread - Real-time process scanning
Phase 1, Task 1.1
"""
import threading
import time
import psutil
import logging
from typing import Callable, Optional

logger = logging.getLogger('HIDR.BackgroundMonitor')

class BackgroundMonitor:
    def __init__(self, callback: Callable, interval: int = 5):
        """
        Initialize background monitor
        
        Args:
            callback: Function to call when threat detected (receives event dict)
            interval: Scan interval in seconds (default: 5)
        """
        self.callback = callback
        self.interval = interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.scanned_pids = set()
        logger.info(f"BackgroundMonitor initialized (interval: {interval}s)")
    
    def start(self):
        """Start background monitoring thread"""
        if self.running:
            logger.warning("Monitor already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Background monitoring started")
    
    def stop(self):
        """Stop background monitoring thread"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Background monitoring stopped")
    
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                self._scan_processes()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(self.interval)
    
    def _scan_processes(self):
        """Scan all running processes"""
        try:
            current_pids = set()
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    pid = proc.info['pid']
                    current_pids.add(pid)
                    
                    # Only scan new processes
                    if pid in self.scanned_pids:
                        continue
                    
                    name = proc.info['name'] or 'Unknown'
                    path = proc.info['exe'] or ''
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    # Send to callback for analysis
                    event = {
                        'type': 'PROCESS_DETECTED',
                        'pid': pid,
                        'name': name,
                        'path': path,
                        'cmdline': cmdline
                    }
                    self.callback(event)
                    self.scanned_pids.add(pid)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Clean up dead processes
            self.scanned_pids &= current_pids
        
        except Exception as e:
            logger.error(f"Process scan error: {e}")
