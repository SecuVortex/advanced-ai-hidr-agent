"""Processes Tab - Real-time process monitoring (Improved)

Key improvements:
- Thread-safe UI updates using queue + after()
- Better error handling and logging
- Publisher extraction refined
- Ctrl+S shortcut to start scan
- Simple search/filter input
- Stable start/stop logic
"""

import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
import queue
import logging
from gui.tooltip import add_tooltip

LOG = logging.getLogger("HIDR.ProcessesTab")


class ProcessesTab:
    def __init__(self, parent, multiagent, auto_scanner=None, reports_tab=None, database=None):
        self.parent = parent
        self.multiagent = multiagent
        self.auto_scanner = auto_scanner
        self.reports_tab = reports_tab
        self.database = database

        self.running = False
        self.scan_thread = None
        self.ui_queue = queue.Queue()  # thread-safe UI update queue
        self.parent.bind_all("<Control-s>", lambda e: self.start_scan())  # Ctrl+S shortcut

        self.frame = ttk.Frame(parent)
        self._create_widgets()
        self._start_ui_poller()

        if auto_scanner:
            self._update_autoscan_status()

    def _create_widgets(self):
        # Top controls: search + start/stop
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        ttk.Label(top_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 8))
        add_tooltip(search_entry, "Filter processes by name or PID")

        ttk.Button(top_frame, text="Clear", command=self._clear_filter).pack(side=tk.LEFT, padx=(0, 8))

        self.start_btn = ttk.Button(top_frame, text="⚡ Start Scan", command=self.start_scan)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        add_tooltip(self.start_btn, "Start scanning all running processes (Ctrl+S)")

        self.stop_btn = ttk.Button(top_frame, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        add_tooltip(self.stop_btn, "Stop the current scan")

        ttk.Label(top_frame, text="Status:").pack(side=tk.LEFT, padx=10)
        self.status_label = ttk.Label(top_frame, text="Idle", foreground="gray")
        self.status_label.pack(side=tk.LEFT)

        if self.auto_scanner:
            self.autoscan_label = ttk.Label(top_frame, text="Auto-scan: Disabled", foreground="gray")
            self.autoscan_label.pack(side=tk.RIGHT, padx=10)

        # Canvas with scrollbar for tree and controls (kept for large lists)
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar_outer = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        canvas.configure(yscrollcommand=scrollbar_outer.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_outer.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Process tree
        tree_frame = ttk.Frame(scrollable_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("PID", "Name", "Publisher", "Parent", "Threat", "YARA", "Cert", "Action")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        col_widths = {
            "PID": 60, "Threat": 80, "YARA": 80, "Cert": 80,
            "Action": 120, "Parent": 120, "Publisher": 150, "Name": 180
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 120), anchor="w")

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

        # Internal caches
        self.parent_cache = {}  # pid -> parent name
        self.latest_scan_summary = {"scanned": 0, "threats": 0, "quarantined": 0}

    def _start_ui_poller(self):
        """Poll the UI queue and apply updates on the main thread."""
        def poll():
            try:
                while True:
                    action, payload = self.ui_queue.get_nowait()
                    try:
                        if action == "insert_row":
                            values = payload
                            self.tree.insert('', 0, values=values)
                        elif action == "update_stats":
                            self.latest_scan_summary.update(payload)
                            s = self.latest_scan_summary
                            self.stats_label.config(text=f"Scanned: {s['scanned']} | Threats: {s['threats']} | Quarantined: {s['quarantined']}")
                        elif action == "clear_tree":
                            self.tree.delete(*self.tree.get_children())
                        elif action == "set_status":
                            text, color = payload
                            self.status_label.config(text=text, foreground=color)
                        elif action == "update_autoscan_label":
                            text, color = payload
                            if hasattr(self, "autoscan_label"):
                                self.autoscan_label.config(text=text, foreground=color)
                    except Exception as e:
                        LOG.exception("UI update failed: %s", e)
            except queue.Empty:
                pass
            finally:
                self.frame.after(150, poll)
        poll()

    def _clear_filter(self):
        self.search_var.set("")
        # Note: we don't re-run the scan; just clear the filter input

    def start_scan(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED, text="⏳ Scanning...")
        self.stop_btn.config(state=tk.NORMAL)
        self.ui_queue.put(("set_status", ("🔍 Scanning processes...", "green")))
        self.ui_queue.put(("clear_tree", None))

        # reset stats
        self.latest_scan_summary = {"scanned": 0, "threats": 0, "quarantined": 0}
        self.ui_queue.put(("update_stats", self.latest_scan_summary.copy()))

        self.scan_thread = threading.Thread(target=self._scan_processes, daemon=True)
        self.scan_thread.start()

    def stop_scan(self):
        if not self.running:
            return
        self.running = False
        # Buttons updated on UI thread for consistency
        self.start_btn.config(state=tk.NORMAL, text="⚡ Start Scan")
        self.stop_btn.config(state=tk.DISABLED)
        self.ui_queue.put(("set_status", ("✓ Scan stopping...", "blue")))

    def _scan_processes(self):
        scanned = 0
        threats = 0
        quarantined = 0

        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                if not self.running:
                    break

                try:
                    pid = int(proc.info.get('pid') or -1)
                    name = proc.info.get('name') or "Unknown"
                    path = proc.info.get('exe') or "N/A"
                    cmdline = ' '.join(proc.info.get('cmdline') or [])

                    # Call analysis (may be blocking) - keep in worker thread
                    try:
                        result = self.multiagent.analyze_process(name, path, cmdline, pid)
                    except Exception as e:
                        LOG.exception("analysis failed for pid %s (%s): %s", pid, name, e)
                        result = {}

                    detection = result.get('detection_result', {}) or {}
                    analysis = result.get('analysis_result', {}) or {}

                    threat = detection.get('threat_level', 0)
                    yara_count = len(detection.get('yara_matches', []) or [])
                    intelligence = result.get('intelligence_result', {}) or {}
                    action = result.get('final_action', 'allow')

                    # Extract publisher and cert info (best-effort heuristics)
                    publisher = "Unknown"
                    cert_display = "Unsigned"
                    path_lower = (path or "").lower()

                    try:
                        if path and path != "N/A":
                            if "windows" in path_lower or "system32" in path_lower:
                                publisher = "Microsoft"
                                cert_display = "System"
                            elif "program files\\google" in path_lower or "google\\chrome" in path_lower:
                                publisher = "Google"
                                cert_display = "Signed"
                            elif "program files\\microsoft" in path_lower or "microsoft vs code" in path_lower:
                                publisher = "Microsoft"
                                cert_display = "Signed"
                            elif "program files" in path_lower:
                                parts = path.split("\\")
                                # pick folder after "Program Files" or "Program Files (x86)"
                                for i, part in enumerate(parts):
                                    pl = part.lower()
                                    if "program files" in pl and i + 1 < len(parts):
                                        publisher = parts[i + 1][:20]
                                        cert_display = "Signed"
                                        break
                    except Exception:
                        # keep defaults
                        LOG.debug("publisher extraction failed for path: %s", path, exc_info=True)

                    # Override with actual cert validation if available
                    cert_validation = intelligence.get('cert_validation') or {}
                    if cert_validation:
                        cert_verdict = cert_validation.get('verdict', '')
                        if cert_verdict == 'valid':
                            cert_display = "✓ Valid"
                        elif cert_verdict == 'revoked':
                            cert_display = "⚠ Revoked"
                            publisher = "REVOKED"
                        elif cert_verdict in ('invalid', 'untrusted'):
                            cert_display = "✗ Invalid"

                    # Parent process lookup (cached)
                    parent_name = "-"
                    try:
                        if pid in self.parent_cache:
                            parent_name = self.parent_cache[pid]
                        else:
                            p = psutil.Process(pid)
                            parent = p.parent()
                            pname = parent.name() if parent else "-"
                            parent_name = pname
                            self.parent_cache[pid] = parent_name
                    except Exception:
                        parent_name = "-"

                    # Threat bookkeeping and persistence
                    if int(float(threat)) >= 5:
                        threats += 1
                        if self.reports_tab:
                            self.reports_tab.log_threat(name, threat, yara_count, action)
                        if self.database:
                            try:
                                mitre_list = detection.get('mitre_techniques', [])
                                self.database.add_threat(name, pid, path, threat, str(detection.get('yara_matches', [])), str(mitre_list), action)
                            except Exception:
                                LOG.exception("failed to write threat to database")

                    # Execute response action (termination/quarantine)
                    executed_quarantine = False
                    if action in ['terminate_temporary', 'terminate_permanent']:
                        try:
                            if self._execute_response(action, pid, path, name, detection):
                                quarantined += 1
                                executed_quarantine = True
                        except Exception:
                            LOG.exception("response execution failed for pid %s", pid)

                    # Prepare row and push to UI queue
                    row = (
                        pid,
                        str(name)[:30],
                        str(publisher)[:20],
                        str(parent_name)[:15],
                        f"{threat}/10",
                        yara_count,
                        cert_display,
                        action
                    )
                    self.ui_queue.put(("insert_row", row))

                    scanned += 1
                    # update stats in UI
                    self.ui_queue.put(("update_stats", {"scanned": scanned, "threats": threats, "quarantined": quarantined}))

                    # Update reports_tab stats if present (runs on UI thread via queue)
                    if self.reports_tab:
                        try:
                            self.reports_tab.update_stats(
                                total_scans=scanned,
                                threats_detected=threats,
                                files_quarantined=quarantined,
                                yara_detections=self.reports_tab.stats.get('yara_detections', 0) + (1 if yara_count > 0 else 0),
                                mb_detections=self.reports_tab.stats.get('mb_detections', 0),
                                actions_taken=self.reports_tab.stats.get('actions_taken', 0) + (1 if action != 'allow' else 0)
                            )
                        except Exception:
                            LOG.exception("reports_tab.update_stats failed")

                    time.sleep(0.05)  # small throttle to keep UI responsive
                except Exception:
                    LOG.exception("error scanning process")
                    continue
        finally:
            # Always ensure we flip running flag and update UI
            self.running = False
            self.ui_queue.put(("set_status", ("✓ Scan complete", "blue")))
            # Reset buttons on main thread
            self.frame.after(0, lambda: (self.start_btn.config(state=tk.NORMAL, text="⚡ Start Scan"),
                                         self.stop_btn.config(state=tk.DISABLED)))

    def _execute_response(self, action, pid, path, name, detection):
        import os
        import shutil
        from datetime import datetime
        import json

        logger = logging.getLogger('HIDR.Response')

        terminated = False
        try:
            # Terminate process
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=3)
                terminated = True
                logger.info("Terminated process %s (PID: %s)", name, pid)
            except psutil.NoSuchProcess:
                logger.warning("Process %s (PID: %s) already terminated", name, pid)
                terminated = True
            except psutil.AccessDenied:
                logger.error("Access denied to terminate %s (PID: %s) - Run as Administrator", name, pid)
                return False
            except Exception:
                # attempt kill
                try:
                    proc = psutil.Process(pid)
                    proc.kill()
                    proc.wait(timeout=3)
                    terminated = True
                    logger.info("Force killed process %s (PID: %s)", name, pid)
                except Exception as e:
                    logger.exception("Failed to kill process %s (PID: %s): %s", name, pid, e)
                    return False

            # Quarantine: copy file & save metadata
            if action == 'terminate_permanent' and path and path != 'N/A':
                try:
                    if not os.path.exists(path):
                        logger.warning("File not found for quarantine: %s", path)
                        return terminated

                    quarantine_dir = os.path.abspath('quarantine')
                    os.makedirs(quarantine_dir, exist_ok=True)

                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    safe_name = "".join([c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name])
                    quarantine_name = f"{safe_name}_{timestamp}"
                    quarantine_path = os.path.join(quarantine_dir, quarantine_name)

                    # Copy file
                    shutil.copy2(path, quarantine_path)
                    logger.info("Quarantined: %s -> %s", path, quarantine_path)

                    # Attempt to delete original (best-effort)
                    try:
                        os.remove(path)
                        logger.info("Deleted original: %s", path)
                    except Exception as e:
                        logger.warning("Could not delete original: %s", e)

                    metadata = {
                        'original_path': path,
                        'quarantine_path': quarantine_path,
                        'timestamp': timestamp,
                        'threat_level': detection.get('threat_level', 0),
                        'yara_matches': [m.get('rule', '') for m in detection.get('yara_matches', [])] if detection.get('yara_matches') else [],
                        'mitre_techniques': detection.get('mitre_techniques', [])
                    }

                    with open(f"{quarantine_path}.json", 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)

                    return True
                except Exception:
                    logger.exception("Quarantine failed for %s", path)
                    return terminated

            return terminated
        except Exception:
            logger.exception("Response execution failed for PID %s", pid)
            return False

    def _update_autoscan_status(self):
        if not self.auto_scanner:
            return

        try:
            if self.auto_scanner.running:
                time_since = self.auto_scanner.get_time_since_last_scan()
                if time_since:
                    mins = time_since // 60
                    self.ui_queue.put(("update_autoscan_label", (f"Last scan: {mins}m ago", "green")))
                else:
                    self.ui_queue.put(("update_autoscan_label", ("Auto-scan: Active", "green")))
            else:
                self.ui_queue.put(("update_autoscan_label", ("Auto-scan: Disabled", "gray")))
        except Exception:
            LOG.exception("autoscan status update failed")
        finally:
            # schedule next update on main thread
            self.frame.after(10000, self._update_autoscan_status)

    def _show_process_details(self, event):
        """Show detailed process information (runs on main thread)"""
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
            proc = psutil.Process(int(pid))
            cmdline = ' '.join(proc.cmdline())
            path = proc.exe()
            username = proc.username()
            create_time = proc.create_time()
            from datetime import datetime
            start_time = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
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
        try:
            try:
                threat_score_val = int(str(threat).split('/')[0])
            except Exception:
                threat_score_val = 0

            if "System" in cert or "Microsoft" in publisher:
                reason = "This is a Windows system process required for OS operation."
            elif parent == "explorer.exe":
                reason = "User launched this application from Windows Explorer."
            elif parent == "services.exe":
                reason = "This is a Windows service running in the background."
            elif "Program Files" in path:
                reason = f"Installed application from {publisher}. Launched by {parent}."
            elif threat_score_val >= 5:
                reason = f"SUSPICIOUS: High threat level detected. Running from untrusted location.\nRecommended action: {action}"
            else:
                reason = f"Standard application process. Parent: {parent}"
        except Exception:
            reason = "Unable to determine reason."

        info += f"\n{reason}\n"

        text.insert('1.0', info)
        text.config(state=tk.DISABLED)

        # Close button
        ttk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)

    def get_frame(self):
        return self.frame
