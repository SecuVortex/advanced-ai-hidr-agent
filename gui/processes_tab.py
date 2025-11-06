"""Processes Tab - Real-time process monitoring"""
import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from gui.tooltip import add_tooltip

class ProcessesTab:
    def __init__(self, parent, multiagent, auto_scanner=None, reports_tab=None, database=None):
        self.parent = parent
        self.multiagent = multiagent
        self.auto_scanner = auto_scanner
        self.reports_tab = reports_tab
        self.database = database
        self.running = False
        self.scan_thread = None
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        if auto_scanner:
            self._update_autoscan_status()
    
    def _create_widgets(self):
        # Canvas with scrollbar
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Control buttons
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="⚡ Start Scan", command=self.start_scan)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        add_tooltip(self.start_btn, "Start scanning all running processes (Ctrl+S)")
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        add_tooltip(self.stop_btn, "Stop the current scan")
        
        ttk.Label(btn_frame, text="Status:").pack(side=tk.LEFT, padx=10)
        self.status_label = ttk.Label(btn_frame, text="Idle", foreground="gray")
        self.status_label.pack(side=tk.LEFT)
        
        if self.auto_scanner:
            self.autoscan_label = ttk.Label(btn_frame, text="Auto-scan: Disabled", foreground="gray")
            self.autoscan_label.pack(side=tk.RIGHT, padx=10)
        
        # Process tree
        tree_frame = ttk.Frame(scrollable_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("PID", "Name", "Publisher", "Parent", "Threat", "YARA", "Cert", "Action")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "PID":
                width = 60
            elif col in ["Threat", "YARA", "Cert"]:
                width = 80
            elif col in ["Action", "Parent"]:
                width = 120
            elif col == "Publisher":
                width = 150
            else:
                width = 180
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to show details
        self.tree.bind('<Double-Button-1>', self._show_process_details)
        
        # Stats
        stats_frame = ttk.LabelFrame(scrollable_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Scanned: 0 | Threats: 0 | Quarantined: 0")
        self.stats_label.pack()
    
    def start_scan(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED, text="⏳ Scanning...")
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="🔍 Scanning processes...", foreground="green")
        self.tree.delete(*self.tree.get_children())  # Clear previous results
        
        self.scan_thread = threading.Thread(target=self._scan_processes, daemon=True)
        self.scan_thread.start()
    
    def stop_scan(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL, text="⚡ Start Scan")
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="✓ Scan complete" if self.running == False else "⏹ Stopped", foreground="blue")
    
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
                intelligence = result.get('intelligence_result', {})
                action = result.get('final_action', 'allow')
                
                # Get publisher from certificate or file properties
                cert_validation = intelligence.get('cert_validation', {})
                publisher = "Unknown"
                cert_display = "-"
                
                if cert_validation:
                    cert_verdict = cert_validation.get('verdict', '-')
                    if cert_verdict == 'valid':
                        cert_display = "✓ Signed"
                        # Extract publisher from cert (simplified)
                        publisher = "Microsoft" if "microsoft" in path.lower() else "Verified"
                    elif cert_verdict == 'revoked':
                        cert_display = "⚠ Revoked"
                        publisher = "REVOKED"
                    elif cert_verdict == 'invalid':
                        cert_display = "✗ Invalid"
                        publisher = "Invalid"
                    else:
                        cert_display = "Unsigned"
                        publisher = "Unknown"
                else:
                    # Infer publisher from path
                    if "microsoft" in path.lower() or "windows" in path.lower():
                        publisher = "Microsoft"
                        cert_display = "System"
                    elif "program files" in path.lower():
                        # Extract from path
                        parts = path.lower().split("\\")
                        if "program files" in parts:
                            idx = parts.index("program files") + 1
                            if idx < len(parts):
                                publisher = parts[idx].title()[:20]
                
                # Get parent process
                try:
                    parent_proc = psutil.Process(pid).parent()
                    parent_name = parent_proc.name() if parent_proc else "-"
                except:
                    parent_name = "-"
                
                if threat >= 5:
                    threats += 1
                    # Log to reports tab
                    if self.reports_tab:
                        self.reports_tab.log_threat(name, threat, yara_count, action)
                    # Log to database
                    if self.database:
                        self.database.add_threat(name, pid, path, threat, str(detection.get('yara_matches', [])), str(mitre), action)
                
                # Execute response action
                if action in ['terminate_temporary', 'terminate_permanent']:
                    if self._execute_response(action, pid, path, name, detection):
                        quarantined += 1
                
                self.tree.insert('', 0, values=(
                    pid, name[:30], publisher[:20], parent_name[:15],
                    f"{threat}/10", yara_count, cert_display, action
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
    
    def _show_process_details(self, event):
        """Show detailed process information"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
        
        pid = values[0]
        name = values[1]
        publisher = values[2]
        parent = values[3]
        threat = values[4]
        yara = values[5]
        cert = values[6]
        action = values[7]
        
        # Get full process info
        try:
            proc = psutil.Process(pid)
            cmdline = ' '.join(proc.cmdline())
            path = proc.exe()
            username = proc.username()
            create_time = proc.create_time()
            
            from datetime import datetime
            start_time = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
        except:
            cmdline = "N/A"
            path = "N/A"
            username = "N/A"
            start_time = "N/A"
        
        # Create detail window
        detail_window = tk.Toplevel(self.frame)
        detail_window.title(f"Process Details - {name}")
        detail_window.geometry("700x500")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(detail_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add process information
        info = f"""PROCESS DETAILS
{'='*60}

BASIC INFORMATION:
  Process Name: {name}
  PID: {pid}
  Publisher: {publisher}
  Parent Process: {parent}
  User: {username}
  Started: {start_time}

LOCATION:
  Path: {path}
  Command Line: {cmdline}

THREAT ANALYSIS:
  Threat Level: {threat}
  YARA Matches: {yara}
  Certificate: {cert}
  Action Taken: {action}

WHY IS THIS RUNNING?
{'='*60}
"""
        
        # Add reason based on analysis
        if "System" in cert or "Microsoft" in publisher:
            reason = "This is a Windows system process required for OS operation."
        elif parent == "explorer.exe":
            reason = "User launched this application from Windows Explorer."
        elif parent == "services.exe":
            reason = "This is a Windows service running in the background."
        elif "Program Files" in path:
            reason = f"Installed application from {publisher}. Launched by {parent}."
        elif int(threat.split('/')[0]) >= 5:
            reason = f"SUSPICIOUS: High threat level detected. Running from untrusted location.\nRecommended action: {action}"
        else:
            reason = f"Standard application process. Parent: {parent}"
        
        info += f"\n{reason}\n"
        
        text.insert('1.0', info)
        text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)
    
    def get_frame(self):
        return self.frame
