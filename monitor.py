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
    print(f'Missing dependencies: {e}')
    print('Install with: pip install wmi psutil watchdog win10toast pywin32')
    WMI_AVAILABLE = False


class HIDRAgent:

    def __init__(self):
        self.base_path = Path.cwd()
        self.watched_dir = self.base_path / 'watched'
        self.decoys_dir = self.watched_dir / 'decoys'
        self.backup_dir = self.base_path / 'backups'
        self.quarantine_dir = self.base_path / 'quarantine'
        for d in [self.watched_dir, self.decoys_dir, self.backup_dir, self.
            quarantine_dir]:
            d.mkdir(exist_ok=True)
        self.incident_log = self.base_path / 'hidr_incidents.csv'
        self.file_hashes = {}
        self.suspicious_events = []
        self.toaster = ToastNotifier() if WMI_AVAILABLE else None
        self.allowlist = ['C:\\Windows\\System32\\', 'C:\\Program Files\\',
            'C:\\Program Files (x86)\\']
        if not self.incident_log.exists():
            with open(self.incident_log, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'type', 'process_name', 'pid',
                    'path', 'command', 'action', 'details'])
        self.setup_decoys()
        self.initialize_file_hashes()

    def setup_decoys(self):
        (self.decoys_dir / 'passwords.txt').write_text('admin:password123')
        (self.decoys_dir / 'financial_data.xlsx').touch()
        (self.decoys_dir / 'backup_keys.txt').write_text('ssh-rsa ...')
        (self.decoys_dir / 'important_data.docx').touch()

    def sha256_file(self, filepath):
        try:
            h = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda : f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def initialize_file_hashes(self):
        for root, _, files in os.walk(self.watched_dir):
            for file in files:
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.watched_dir))
                self.file_hashes[rel_path] = self.sha256_file(file_path)
                backup_path = self.backup_dir / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)

    def log_incident(self, event_type, process_name='', pid=0, path='',
        command='', action='', details=''):
        timestamp = datetime.now().isoformat()
        with open(self.incident_log, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event_type, process_name, pid, path,
                command, action, details])

    def notify(self, title, message):
        print(f'[ALERT] {title}: {message}')
        if self.toaster:
            self.toaster.show_toast(title, message, duration=10)

    def is_suspicious_process(self, proc_name, path, cmdline):
        if not path:
            return False
        if any(path.startswith(allowed) for allowed in self.allowlist):
            return False
        suspicious_patterns = ['temp' in path.lower(), 'downloads' in path.
            lower(), proc_name.lower() in ['encryptor.exe', 'locker.exe',
            'crypt.exe'], 'powershell' in proc_name.lower() and
            'encodedcommand' in cmdline.lower(), proc_name.lower().endswith
            ('.exe') and 'appdata' in path.lower()]
        return any(suspicious_patterns)

    def kill_process(self, pid):
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=3)
            return True
        except psutil.NoSuchProcess:
            return True
        except (psutil.TimeoutExpired, psutil.AccessDenied):
            try:
                p.kill()
                p.wait(timeout=3)
                return True
            except Exception:
                return False
        except Exception:
            return False

    def quarantine_file(self, file_path):
        try:
            quar_name = f'{file_path.name}.{int(time.time())}.quar'
            quar_path = self.quarantine_dir / quar_name
            shutil.move(str(file_path), str(quar_path))
            return str(quar_path)
        except Exception as e:
            print(f'Failed to quarantine {file_path}: {e}')
            return None

    def restore_from_backup(self, rel_path):
        backup_path = self.backup_dir / rel_path
        if backup_path.exists():
            try:
                shutil.copy2(backup_path, self.watched_dir / rel_path)
                return True
            except Exception as e:
                print(f'Failed to restore {rel_path}: {e}')
        return False

    def start_monitoring(self):
        if WMI_AVAILABLE:
            self.wmi_conn = wmi.WMI()
            self.monitor_processes()
        file_watcher = FileChangeHandler(self)
        self.file_observer = Observer()
        self.file_observer.schedule(file_watcher, str(self.watched_dir),
            recursive=True)
        self.file_observer.start()
        print('File system monitoring started')

    def monitor_processes(self):
        if not self.wmi_conn:
            print('WMI not available - process monitoring disabled')
            return

        def monitor_loop():
            try:
                process_watcher = self.wmi_conn.Win32_ProcessStartTrace.watch()
                for event in process_watcher:
                    self.handle_process_event(event)
            except Exception as e:
                print(f'Process monitoring error: {e}')
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        print('Process monitoring started')

    def handle_process_event(self, event):
        try:
            pid = event.ProcessId
            proc_name = event.ProcessName
            proc = self.wmi_conn.Win32_Process(ProcessId=pid)[0]
            path = proc.ExecutablePath or ''
            cmdline = proc.CommandLine or ''
            if self.is_suspicious_process(proc_name, path, cmdline):
                self.notify('Suspicious Process Detected',
                    f'{proc_name} (PID: {pid})')
                self.log_incident('suspicious_process', proc_name, pid,
                    path, cmdline, 'detected', 'Heuristic analysis')
                if 'encryptor.exe' in proc_name.lower():
                    self.kill_process(pid)
                    self.log_incident('ransomware_blocked', proc_name, pid,
                        path, cmdline, 'terminated', 'Ransomware signature')
                    self.notify('Ransomware Blocked',
                        f'{proc_name} (PID: {pid}) was terminated.')
        except Exception as e:
            print(f'Error handling process event: {e}')


class FileChangeHandler(FileSystemEventHandler):

    def __init__(self, agent):
        self.agent = agent

    def on_any_event(self, event):
        if event.is_directory:
            return
        try:
            file_path = Path(event.src_path)
            if not file_path.exists() and event.event_type != 'deleted':
                return
            rel_path = str(file_path.relative_to(self.agent.watched_dir))
            if event.event_type == 'modified':
                new_hash = self.agent.sha256_file(file_path)
                old_hash = self.agent.file_hashes.get(rel_path)
                if old_hash and new_hash != old_hash:
                    self.agent.notify('File Integrity Compromised', rel_path)
                    if self.agent.decoys_dir in file_path.parents:
                        self.agent.log_incident('decoy_access', path=
                            rel_path, action='triggered', details=
                            'Decoy file modified')
                        self.agent.notify('DECOY TRIGGERED',
                            f'Decoy file {rel_path} was modified!')
                    quar_path = self.agent.quarantine_file(file_path)
                    if quar_path:
                        self.agent.notify('File Quarantined',
                            f'{rel_path} was moved to quarantine.')
                        self.agent.log_incident('file_modified', path=
                            rel_path, action='quarantined', details=
                            'Hash mismatch')
                        self.agent.restore_from_backup(rel_path)
                self.agent.file_hashes[rel_path] = new_hash
            elif event.event_type == 'deleted':
                self.agent.notify('File Deleted', rel_path)
                self.agent.log_incident('file_deleted', path=rel_path,
                    action='detected')
                if self.agent.restore_from_backup(rel_path):
                    self.agent.notify('File Restored',
                        f'{rel_path} was restored from backup.')
        except Exception as e:
            print(f'Error handling file event: {e}')


if __name__ == '__main__':
    if not WMI_AVAILABLE:
        sys.exit(1)
    agent = HIDRAgent()
    agent.start_monitoring()
    print('HIDR Agent is running. Press Ctrl+C to stop.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping HIDR Agent...')
        agent.file_observer.stop()
        agent.file_observer.join()
        print('Agent stopped.')
