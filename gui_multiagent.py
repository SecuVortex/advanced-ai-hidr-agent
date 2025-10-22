"""Multi-Agent HIDR GUI - Fully Functional"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import time
import psutil

try:
    from simple_multiagent import SimpleMultiAgent
    from gui_monitor import HIDRGui, EnhancedFileWatcher
    from monitor import HIDRAgent
    from watchdog.observers import Observer
    MULTIAGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Multi-agent unavailable: {e}")
    MULTIAGENT_AVAILABLE = False

class HumanApprovalDialog:
    def __init__(self, parent, detection, analysis, recommended):
        self.result = recommended
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🚨 Threat Detected")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        header = tk.Frame(self.dialog, bg="#d32f2f", height=50)
        header.pack(fill=tk.X)
        tk.Label(header, text="⚠️ SECURITY ALERT", font=("Arial", 14, "bold"),
                bg="#d32f2f", fg="white").pack(pady=10)
        
        content = tk.Frame(self.dialog, padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)
        
        info = ttk.LabelFrame(content, text="Threat Information")
        info.pack(fill=tk.X, pady=5)
        
        tk.Label(info, text=f"Process: {detection.get('process_name', 'Unknown')}",
                font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(info, text=f"Threat Level: {detection.get('threat_level', 0)}/10",
                fg="red").pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(info, text=f"Severity: {analysis.get('severity', 'Unknown')}",
                fg="orange").pack(anchor=tk.W, padx=10, pady=2)
        
        analysis_frame = ttk.LabelFrame(content, text="AI Analysis")
        analysis_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        text = tk.Text(analysis_frame, height=8, wrap=tk.WORD, font=("Arial", 9))
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text.insert("1.0", analysis.get('summary', 'No analysis'))
        text.config(state=tk.DISABLED)
        
        reasons_frame = ttk.LabelFrame(content, text="Detection Reasons")
        reasons_frame.pack(fill=tk.X, pady=5)
        
        reasons_text = tk.Text(reasons_frame, height=3, wrap=tk.WORD, font=("Arial", 9))
        reasons_text.pack(fill=tk.X, padx=5, pady=5)
        reasons = detection.get('reasons', [])
        reasons_text.insert("1.0", "\n".join(f"• {r}" for r in reasons[:3]))
        reasons_text.config(state=tk.DISABLED)
        
        tk.Label(content, text=f"Recommended: {recommended.upper()}",
                font=("Arial", 10, "bold"), fg="#1976d2").pack(pady=5)
        
        btn_frame = tk.Frame(content)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="✓ Allow",
                  command=lambda: self.set_action("allow")).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="👁 Monitor",
                  command=lambda: self.set_action("monitor")).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="🛑 Terminate",
                  command=lambda: self.set_action("terminate_temporary")).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: self.set_action(recommended))
    
    def set_action(self, action):
        self.result = action
        self.dialog.destroy()
    
    def get_result(self):
        self.dialog.wait_window()
        return self.result

class MultiAgentHIDRGui(HIDRGui):
    def __init__(self):
        super().__init__()
        self.root.title("Multi-Agent HIDR System")
        self.orchestrator = None
        self.agent_labels = {}
        
        if MULTIAGENT_AVAILABLE:
            self.create_multiagent_tab()
    
    def create_multiagent_tab(self):
        self.multiagent_frame = ttk.Frame(self.notebook)
        self.notebook.insert(1, self.multiagent_frame, text="🤖 AI Agents")
        
        status_frame = ttk.LabelFrame(self.multiagent_frame, text="Agent Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        agents = [
            ("DetectionAgent", "🔍 Detection"),
            ("IntelligenceAgent", "🌐 Intelligence"),
            ("AnalystAgent", "🤖 AI Analyst"),
            ("CoordinatorAgent", "🎯 Coordinator"),
            ("ResponseAgent", "🛡️ Response")
        ]
        
        for i, (name, display) in enumerate(agents):
            frame = ttk.Frame(status_frame)
            frame.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
            ttk.Label(frame, text=display, font=("Arial", 9, "bold")).pack()
            label = ttk.Label(frame, text="●", foreground="gray", font=("Arial", 14))
            label.pack()
            self.agent_labels[name] = label
        
        comm_frame = ttk.LabelFrame(self.multiagent_frame, text="Agent Communication (Live)")
        comm_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.comm_text = tk.Text(comm_frame, height=20, state=tk.DISABLED, font=("Consolas", 9))
        comm_scroll = ttk.Scrollbar(comm_frame, orient=tk.VERTICAL, command=self.comm_text.yview)
        self.comm_text.configure(yscrollcommand=comm_scroll.set)
        self.comm_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        comm_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def start_monitoring(self):
        if not MULTIAGENT_AVAILABLE:
            super().start_monitoring()
            return
        
        try:
            self.agent = HIDRAgent()
            self.orchestrator = SimpleMultiAgent()
            self.start_time = datetime.now()
            self.monitoring_active = True
            
            self.process_monitor_thread = threading.Thread(target=self.multiagent_process_monitor, daemon=True)
            self.process_monitor_thread.start()
            
            file_watcher = EnhancedFileWatcher(self.agent, self)
            self.file_observer = Observer()
            self.file_observer.schedule(file_watcher, str(self.agent.watched_dir), recursive=True)
            self.file_observer.start()
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.log_activity("🤖 Multi-Agent System started!")
            self.log_comm("System", "All Agents", "Multi-agent orchestration initialized")
            
            messagebox.showinfo("Success", "Multi-Agent System Active!\n\n✓ 5 AI agents\n✓ Human-in-the-loop\n✓ Dual API support")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def multiagent_process_monitor(self):
        seen_pids = set()
        
        try:
            for proc in psutil.process_iter(['pid']):
                seen_pids.add(proc.info['pid'])
        except Exception:
            pass
        
        while self.monitoring_active:
            try:
                current_processes = {}
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                    try:
                        current_processes[proc.info['pid']] = proc.info
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                current_pids = set(current_processes.keys())
                new_pids = current_pids - seen_pids
                
                for pid in new_pids:
                    try:
                        proc_info = current_processes[pid]
                        self.handle_multiagent_process(proc_info)
                    except Exception:
                        pass
                
                seen_pids = current_pids
                time.sleep(0.05)
                
            except Exception:
                time.sleep(1)
    
    def handle_multiagent_process(self, proc_info):
        proc_name = proc_info.get('name', 'Unknown')
        pid = proc_info.get('pid', 0)
        path = proc_info.get('exe', '') or ''
        cmdline = ' '.join(proc_info.get('cmdline', []) or [])
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        action = "Allowed"
        reason = "Normal process execution"
        
        try:
            # Quick check if suspicious
            is_suspicious = self.agent and self.is_enhanced_suspicious_process(proc_name, path, cmdline)
            
            # ALWAYS run multi-agent for demo (remove this later)
            if is_suspicious or "notepad" in proc_name.lower() or "calc" in proc_name.lower():
                # Log to agent communication
                self.log_comm("System", "DetectionAgent", f"Analyzing: {proc_name}")
                
                # Run multi-agent analysis
                result = self.orchestrator.analyze_process(proc_name, path, cmdline, pid)
                
                # Update agent indicators
                for agent_name, label in self.agent_labels.items():
                    label.config(foreground="green")
                    self.root.after(1500, lambda l=label: l.config(foreground="gray"))
                
                # Log all agent messages
                for msg in result.get('messages', []):
                    self.log_comm(msg['from_agent'], msg['to_agent'], msg['message'])
                
                detection = result['detection_result']
                final_action = result['final_action']
                
                action = "BLOCKED" if final_action in ['terminate_temporary', 'terminate_permanent'] else "FLAGGED"
                reason = f"Threat: {detection['threat_level']}/10"
                
                if final_action in ['terminate_temporary', 'terminate_permanent']:
                    if self.agent.kill_process(pid):
                        action = "TERMINATED"
                        self.log_activity(f"🚨 TERMINATED: {proc_name} (PID: {pid}) - {reason}")
                    else:
                        self.log_activity(f"🚨 BLOCKED: {proc_name} (PID: {pid}) - {reason}")
                else:
                    self.log_activity(f"⚠️  FLAGGED: {proc_name} (PID: {pid}) - {reason}")
            else:
                # Normal process - just log
                self.log_activity(f"✓ ALLOWED: {proc_name} (PID: {pid})")
            
        except Exception as e:
            self.log_activity(f"❌ Error analyzing {proc_name}: {str(e)}")
            action = "Error"
            reason = str(e)
        
        # Add to process table
        self.add_process_event(timestamp, proc_name, str(pid), path, action, reason)
    
    def human_approval(self, detection, intelligence, analysis, recommended):
        dialog = HumanApprovalDialog(self.root, detection, analysis, recommended)
        return dialog.get_result()
    
    def is_enhanced_suspicious_process(self, proc_name, path, cmdline):
        """Check if process is suspicious (copied from gui_monitor.py)"""
        if not path:
            return False
        
        allowlist = [
            "C:\\Windows\\System32\\",
            "C:\\Program Files\\",
            "C:\\Program Files (x86)\\",
        ]
        
        if any(path.startswith(allowed) for allowed in allowlist):
            return False
        
        suspicious_indicators = [
            "temp" in path.lower(),
            "downloads" in path.lower(),
            proc_name.lower() in ["encryptor.exe", "locker.exe", "crypt.exe", "ransomware.exe", "keylogger.exe"],
            "powershell" in proc_name.lower() and ("encodedcommand" in cmdline.lower() or "-enc" in cmdline.lower()),
            "suspicious" in proc_name.lower(),
            "malware" in proc_name.lower(),
        ]
        
        return any(suspicious_indicators)
    
    def log_comm(self, from_agent, to_agent, message):
        """Log agent communication to GUI"""
        if not hasattr(self, 'comm_text'):
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{from_agent}] -> [{to_agent}]: {message}\n"
        
        def update():
            try:
                self.comm_text.config(state=tk.NORMAL)
                self.comm_text.insert(tk.END, log_entry)
                self.comm_text.see(tk.END)
                self.comm_text.config(state=tk.DISABLED)
            except:
                pass
        
        try:
            self.root.after_idle(update)
        except:
            pass

def main():
    if not MULTIAGENT_AVAILABLE:
        print("❌ Multi-agent unavailable!")
        return
    
    app = MultiAgentHIDRGui()
    app.run()

if __name__ == "__main__":
    main()
