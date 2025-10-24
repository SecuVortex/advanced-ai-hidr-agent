import threading
import time
import psutil
import logging
from typing import Callable, Optional

logger = logging.getLogger('HIDR.AutoScanner')

class AutoScanner:
    def __init__(self, multiagent, interval_minutes: int = 5):
        self.multiagent = multiagent
        self.interval = interval_minutes * 60
        self.running = False
        self.thread = None
        self.last_scan_time = None
        self.scan_callback = None
        
    def start(self, callback: Optional[Callable] = None):
        if self.running:
            logger.warning("Auto-scanner already running")
            return
        
        self.running = True
        self.scan_callback = callback
        self.thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.thread.start()
        logger.info(f"Auto-scanner started (interval: {self.interval}s)")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Auto-scanner stopped")
    
    def _scan_loop(self):
        while self.running:
            try:
                self._scan_all_processes()
                self.last_scan_time = time.time()
                if self.scan_callback:
                    self.scan_callback()
            except Exception as e:
                logger.error(f"Auto-scan error: {e}")
            
            time.sleep(self.interval)
    
    def _scan_all_processes(self):
        suspicious_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                if not self.running:
                    break
                
                name = proc.info['name']
                exe = proc.info['exe'] or ''
                cmdline = ' '.join(proc.info['cmdline'] or [])
                pid = proc.info['pid']
                
                if not exe or 'system32' in exe.lower():
                    continue
                
                result = self.multiagent.analyze_process(name, exe, cmdline, pid)
                if result['detection_result'].get('is_suspicious'):
                    suspicious_count += 1
                    logger.warning(f"Suspicious: {name} (PID: {pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.info(f"Auto-scan complete: {suspicious_count} suspicious processes")
    
    def get_time_since_last_scan(self) -> Optional[int]:
        if not self.last_scan_time:
            return None
        return int(time.time() - self.last_scan_time)
