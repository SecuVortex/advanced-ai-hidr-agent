"""
Lightweight Host Intrusion Detection & Response (HIDR) Agent
Detects suspicious processes, monitors file integrity, quarantines threats, and generates incident reports.
"""
import os
import time
import json
import csv
import hashlib
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path

try:
    import wmi
    import psutil
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    from win10toast import ToastNotifier
    WMI_AVAILABLE = True
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install wmi psutil watchdog win10toast pywin32")
    WMI_AVAILABLE = False

class HIDRAgent:
    def __init__(self):
        self.base_path = Path.cwd()
        self.watched_dir = self.base_path / "watched"
        self.decoys_dir = self.watched_dir / "decoys"
        self.backup_dir = self.base_path / "backups"
        self.quarantine_dir = self.base_path / "quarantine"
        
        # Create directories
        for d in [self.watched_dir, self.decoys_dir, self.backup_dir, self.quarantine_dir]:
            d.mkdir(exist_ok=True)
        
        self.incident_log = self.base_path / "incident_report.csv"
        self.file_hashes = {}
        self.suspicious_events = []
        self.toaster = ToastNotifier() if WMI_AVAILABLE else None
        
        # Allowlist of trusted processes
        self.allowlist = [
            "C:\\Windows\\System32\\",
            "C:\\Program Files\\",
            "C:\\Program Files (x86)\\",
        ]
        
        # Initialize CSV log
        if not self.incident_log.exists():
            with open(self.incident_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'type', 'process_name', 'pid', 'path', 'command', 'action', 'details'])
        
        self.setup_decoys()
        self.initialize_file_hashes()
    
    def setup_decoys(self):
        """Create decoy files to detect ransomware-like activity"""
        decoy_files = [
            ("passwords.txt", "username:password\nadmin:secret123"),
            ("important_data.docx", "This is a decoy document file"),
            ("backup_keys.txt", "SSH_KEY=abc123\nAPI_KEY=xyz789"),
            ("financial_data.xlsx", "Account,Balance\n12345,50000")
        ]
        
        for filename, content in decoy_files:
            decoy_path = self.decoys_dir / filename
            if not decoy_path.exists():
                decoy_path.write_text(content)
        
        print(f"Created {len(decoy_files)} decoy files in {self.decoys_dir}")
    
    def sha256_file(self, filepath):
        """Calculate SHA256 hash of a file"""
        try:
            h = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None
    
    def initialize_file_hashes(self):
        """Initialize hash database for file integrity monitoring"""
        for file_path in self.watched_dir.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.watched_dir))
                file_hash = self.sha256_file(file_path)
                if file_hash:
                    self.file_hashes[rel_path] = file_hash
                    # Create backup
                    backup_path = self.backup_dir / rel_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
        
        print(f"Initialized monitoring for {len(self.file_hashes)} files")
    
    def log_incident(self, event_type, process_name="", pid="", path="", command="", action="", details=""):
        """Log incident to CSV file"""
        timestamp = datetime.now().isoformat()
        with open(self.incident_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event_type, process_name, pid, path, command, action, details])
    
    def notify(self, title, message):
        """Show Windows notification"""
        if self.toaster:
            try:
                self.toaster.show_toast(title, message, duration=5)
            except Exception:
                pass
        print(f"[ALERT] {title}: {message}")
    
    def is_suspicious_process(self, proc_name, path, cmdline):
        """Heuristic to detect suspicious processes"""
        if not path:
            return False
        
        # Check allowlist
        if any(path.startswith(allowed) for allowed in self.allowlist):
            return False
        
        suspicious_patterns = [
            "temp" in path.lower(),
            "downloads" in path.lower(),
            proc_name.lower() in ["encryptor.exe", "locker.exe", "crypt.exe"],
            "powershell" in proc_name.lower() and "encodedcommand" in cmdline.lower(),
            proc_name.lower().endswith(".exe") and "appdata" in path.lower()
        ]
        
        return any(suspicious_patterns)
    
    def kill_process(self, pid):
        """Attempt to terminate suspicious process"""
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], 
                         check=True, capture_output=True)
            return True
        except Exception:
            return False
    
    def quarantine_file(self, file_path):
        """Move file to quarantine"""
        try:
            quar_name = f"{file_path.name}.{int(time.time())}.quar"
            quar_path = self.quarantine_dir / quar_name
            shutil.move(str(file_path), str(quar_path))
            return str(quar_path)
        except Exception as e:
            print(f"Failed to quarantine {file_path}: {e}")
            return None
    
    def restore_from_backup(self, rel_path):
        """Restore file from backup"""
        try:
            backup_path = self.backup_dir / rel_path
            target_path = self.watched_dir / rel_path
            if backup_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, target_path)
                return True
        except Exception as e:
            print(f"Failed to restore {rel_path}: {e}")
        return False

class FileWatcher(FileSystemEventHandler):
    def __init__(self, agent):
        self.agent = agent
        self.modification_count = {}
        self.modification_window = 10  # seconds
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        self.handle_file_event(event.src_path, "modified")
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        self.handle_file_event(event.src_path, "created")
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        rel_path = str(file_path.relative_to(self.agent.watched_dir))
        
        self.agent.log_incident("file_deleted", path=event.src_path, 
                               action="restore_attempted", details=f"File deleted: {rel_path}")
        
        # Attempt to restore from backup
        if self.agent.restore_from_backup(rel_path):
            self.agent.notify("File Restored", f"Restored deleted file: {rel_path}")
        
        # Check if this is part of mass deletion (ransomware behavior)
        current_time = time.time()
        self.modification_count[current_time] = self.modification_count.get(current_time, 0) + 1
        
        # Clean old entries
        cutoff = current_time - self.modification_window
        self.modification_count = {t: c for t, c in self.modification_count.items() if t > cutoff}
        
        total_recent = sum(self.modification_count.values())
        if total_recent > 5:  # More than 5 deletions in 10 seconds
            self.agent.notify("RANSOMWARE ALERT", f"Mass file deletion detected: {total_recent} files")
    
    def handle_file_event(self, src_path, event_type):
        try:
            file_path = Path(src_path)
            rel_path = str(file_path.relative_to(self.agent.watched_dir))
            
            if not file_path.exists():
                return
            
            new_hash = self.agent.sha256_file(file_path)
            old_hash = self.agent.file_hashes.get(rel_path)
            
            if old_hash and new_hash != old_hash:
                # File modified - potential threat
                self.agent.log_incident("file_modified", path=src_path, 
                                       action="quarantined", details=f"Hash changed: {old_hash[:8]}→{new_hash[:8]}")
                
                # Quarantine the modified file
                quar_path = self.agent.quarantine_file(file_path)
                if quar_path:
                    self.agent.notify("File Quarantined", f"Suspicious modification: {rel_path}")
                
                # Restore from backup
                if self.agent.restore_from_backup(rel_path):
                    self.agent.notify("File Restored", f"Restored from backup: {rel_path}")
            
            # Update hash database
            if new_hash:
                self.agent.file_hashes[rel_path] = new_hash
                
        except Exception as e:
            print(f"Error handling file event: {e}")

class ProcessMonitor:
    def __init__(self, agent):
        self.agent = agent
        self.wmi_conn = None
        if WMI_AVAILABLE:
            try:
                self.wmi_conn = wmi.WMI()
            except Exception as e:
                print(f"Failed to initialize WMI: {e}")
    
    def start_monitoring(self):
        """Start process monitoring in separate thread"""
        if not self.wmi_conn:
            print("WMI not available - process monitoring disabled")
            return
        
        def monitor_loop():
            try:
                process_watcher = self.wmi_conn.Win32_ProcessStartTrace.watch()
                for event in process_watcher:
                    self.handle_process_event(event)
            except Exception as e:
                print(f"Process monitoring error: {e}")
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        print("Process monitoring started")
    
    def handle_process_event(self, event):
        """Handle process creation event"""
        try:
            proc_name = event.ProcessName
            pid = event.ProcessId
            
            # Get additional process info
            try:
                proc = self.wmi_conn.Win32_Process(ProcessId=pid)[0]
                path = proc.ExecutablePath or ""
                cmdline = proc.CommandLine or ""
            except Exception:
                path = ""
                cmdline = ""
            
            timestamp = datetime.now().isoformat()
            print(f"[{timestamp}] Process: {proc_name} (PID: {pid}) Path: {path}")
            
            # Check if process is suspicious
            if self.agent.is_suspicious_process(proc_name, path, cmdline):
                self.agent.log_incident("suspicious_process", proc_name, pid, path, cmdline, 
                                       "terminated", "Heuristic match")
                
                # Attempt to kill the process
                if self.agent.kill_process(pid):
                    self.agent.notify("Process Terminated", f"Killed suspicious process: {proc_name}")
                else:
                    self.agent.notify("Process Alert", f"Could not terminate: {proc_name}")
                
                # Add to suspicious events for correlation
                self.agent.suspicious_events.append({
                    'timestamp': time.time(),
                    'type': 'process',
                    'name': proc_name,
                    'pid': pid,
                    'path': path
                })
                
        except Exception as e:
            print(f"Error handling process event: {e}")

def main():
    print("=== Lightweight HIDR Agent Starting ===")
    
    if not WMI_AVAILABLE:
        print("Warning: Some dependencies missing. Install with:")
        print("pip install wmi psutil watchdog win10toast pywin32")
        return
    
    # Initialize agent
    agent = HIDRAgent()
    
    # Start process monitoring
    proc_monitor = ProcessMonitor(agent)
    proc_monitor.start_monitoring()
    
    # Start file monitoring
    file_watcher = FileWatcher(agent)
    observer = Observer()
    observer.schedule(file_watcher, str(agent.watched_dir), recursive=True)
    observer.start()
    
    print(f"Monitoring directory: {agent.watched_dir}")
    print(f"Decoy files created in: {agent.decoys_dir}")
    print(f"Incident log: {agent.incident_log}")
    print("\nAgent running... Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping agent...")
        observer.stop()
        observer.join()
        
        # Generate final report
        print(f"\nIncident report saved to: {agent.incident_log}")
        if agent.incident_log.exists():
            with open(agent.incident_log, 'r') as f:
                lines = f.readlines()
                print(f"Total incidents logged: {len(lines) - 1}")

if __name__ == "__main__":
    main()