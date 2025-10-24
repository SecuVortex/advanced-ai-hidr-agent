"""Processes Tab - Real-time process monitoring"""
import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time

class ProcessesTab:
    def __init__(self, parent, multiagent, auto_scanner=None, reports_tab=None):
        self.parent = parent
        self.multiagent = multiagent
        self.auto_scanner = auto_scanner
        self.reports_tab = reports_tab
        self.running = False
        self.scan_thread = None
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        if auto_scanner:
            self._update_autoscan_status()
    
    def _create_widgets(self):
        # Control buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Scan", command=self.start_scan)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(btn_frame, text="Status:").pack(side=tk.LEFT, padx=10)
        self.status_label = ttk.Label(btn_frame, text="Idle", foreground="gray")
        self.status_label.pack(side=tk.LEFT)
        
        if self.auto_scanner:
            self.autoscan_label = ttk.Label(btn_frame, text="Auto-scan: Disabled", foreground="gray")
            self.autoscan_label.pack(side=tk.RIGHT, padx=10)
        
        # Process tree
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("PID", "Name", "Path", "Threat", "YARA", "MB", "MITRE", "Action")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80 if col in ["PID", "Threat", "YARA", "MB"] else 150 if col in ["MITRE", "Action"] else 180
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Stats
        stats_frame = ttk.LabelFrame(self.frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Scanned: 0 | Threats: 0 | Quarantined: 0")
        self.stats_label.pack()
    
    def start_scan(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Scanning...", foreground="green")
        
        self.scan_thread = threading.Thread(target=self._scan_processes, daemon=True)
        self.scan_thread.start()
    
    def stop_scan(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", foreground="red")
    
    def _scan_processes(self):
        scanned = 0
        threats = 0
        quarantined = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            if not self.running:
                break
            
            try:
                pid = proc.info['pid']
                name = proc.info['name'] or "Unknown"
                path = proc.info['exe'] or "N/A"
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                result = self.multiagent.analyze_process(name, path, cmdline, pid)
                
                detection = result.get('detection_result', {})
                analysis = result.get('analysis_result', {})
                
                threat = detection.get('threat_level', 0)
                yara_count = len(detection.get('yara_matches', []))
                
                # MalwareBazaar verdict
                intelligence = result.get('intelligence_result', {})
                mb_data = intelligence.get('malwarebazaar', {})
                mb_verdict = mb_data.get('verdict', '-')
                if mb_verdict == 'malicious':
                    mb_display = f"⚠ {mb_data.get('malware_family', 'Malware')[:15]}"
                elif mb_verdict == 'clean':
                    mb_display = "✓ Clean"
                else:
                    mb_display = "-"
                
                mitre = ', '.join(detection.get('mitre_techniques', [])[:2])
                action = result.get('final_action', 'allow')
                
                if threat >= 5:
                    threats += 1
                    # Log to reports tab
                    if self.reports_tab:
                        self.reports_tab.log_threat(name, threat, yara_count, action)
                
                # Execute response action
                if action in ['terminate_temporary', 'terminate_permanent']:
                    if self._execute_response(action, pid, path, name, detection):
                        quarantined += 1
                
                self.tree.insert('', 0, values=(
                    pid, name[:30], path[:35], f"{threat}/10",
                    yara_count, mb_display, mitre or "-", action
                ))
                
                scanned += 1
                self.stats_label.config(text=f"Scanned: {scanned} | Threats: {threats} | Quarantined: {quarantined}")
                
                # Update reports tab stats
                if self.reports_tab:
                    self.reports_tab.update_stats(
                        total_scans=scanned,
                        threats_detected=threats,
                        files_quarantined=quarantined,
                        yara_detections=self.reports_tab.stats.get('yara_detections', 0) + (1 if yara_count > 0 else 0),
                        mb_detections=self.reports_tab.stats.get('mb_detections', 0) + (1 if mb_verdict == 'malicious' else 0),
                        actions_taken=self.reports_tab.stats.get('actions_taken', 0) + (1 if action != 'allow' else 0)
                    )
                
                time.sleep(0.1)
            except:
                continue
        
        self.stop_scan()
    
    def _execute_response(self, action, pid, path, name, detection):
        import os
        import shutil
        from datetime import datetime
        import json
        import logging
        
        logger = logging.getLogger('HIDR.Response')
        
        try:
            # Terminate process
            terminated = False
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=3)
                terminated = True
                logger.info(f"Terminated process {name} (PID: {pid})")
            except psutil.NoSuchProcess:
                logger.warning(f"Process {pid} already terminated")
                terminated = True
            except psutil.AccessDenied:
                logger.error(f"Access denied to terminate {name} (PID: {pid}) - Run as Administrator")
                return False
            except Exception as e:
                logger.error(f"Failed to terminate {name}: {e}")
                try:
                    proc = psutil.Process(pid)
                    proc.kill()
                    terminated = True
                    logger.info(f"Force killed process {name} (PID: {pid})")
                except:
                    return False
            
            # Quarantine file if permanent termination
            if action == 'terminate_permanent' and path and path != 'N/A':
                if not os.path.exists(path):
                    logger.warning(f"File not found for quarantine: {path}")
                    return terminated
                
                try:
                    quarantine_dir = 'quarantine'
                    os.makedirs(quarantine_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    quarantine_name = f"{name}_{timestamp}"
                    quarantine_path = os.path.join(quarantine_dir, quarantine_name)
                    
                    # Copy instead of move (safer)
                    shutil.copy2(path, quarantine_path)
                    logger.info(f"Quarantined: {path} -> {quarantine_path}")
                    
                    # Try to delete original
                    try:
                        os.remove(path)
                        logger.info(f"Deleted original: {path}")
                    except Exception as e:
                        logger.warning(f"Could not delete original: {e}")
                    
                    # Save metadata
                    metadata = {
                        'original_path': path,
                        'quarantine_path': quarantine_path,
                        'timestamp': timestamp,
                        'threat_level': detection.get('threat_level', 0),
                        'yara_matches': [m.get('rule', '') for m in detection.get('yara_matches', [])],
                        'mitre_techniques': detection.get('mitre_techniques', [])
                    }
                    
                    with open(f"{quarantine_path}.json", 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    return True
                except Exception as e:
                    logger.error(f"Quarantine failed: {e}")
                    return terminated
            
            return terminated
        except Exception as e:
            logger.error(f"Response execution failed: {e}")
            return False
    
    def _update_autoscan_status(self):
        if not self.auto_scanner:
            return
        
        if self.auto_scanner.running:
            time_since = self.auto_scanner.get_time_since_last_scan()
            if time_since:
                mins = time_since // 60
                self.autoscan_label.config(text=f"Last scan: {mins}m ago", foreground="green")
            else:
                self.autoscan_label.config(text="Auto-scan: Active", foreground="green")
        else:
            self.autoscan_label.config(text="Auto-scan: Disabled", foreground="gray")
        
        self.frame.after(10000, self._update_autoscan_status)
    
    def get_frame(self):
        return self.frame
