import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.multiagent_monitor import MultiAgentHIDR


class MultiAgentGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Multi-Agent HIDR System v2.0')
        self.root.geometry('1200x800')
        self.hidr = None
        self.monitoring_active = False
        self.setup_gui()
        self.log_system('Multi-Agent HIDR GUI Initialized. Ready to start.')

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding='10')
        main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.LabelFrame(main_frame, text='System Control')
        control_frame.pack(fill=tk.X, pady=5)
        self.start_btn = ttk.Button(control_frame, text='Start System',
            command=self.start_system)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(control_frame, text='Stop System',
            command=self.stop_system, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.test_btn = ttk.Button(control_frame, text='Run Test Scenario',
            command=self.run_test_scenario)
        self.test_btn.pack(side=tk.LEFT, padx=5)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        self.create_dashboard_tab(notebook)
        self.create_comm_log_tab(notebook)

    def create_dashboard_tab(self, notebook):
        dashboard = ttk.Frame(notebook)
        notebook.add(dashboard, text='Dashboard')
        log_frame = ttk.LabelFrame(dashboard, text='System Log')
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.system_log = tk.Text(log_frame, height=20, state=tk.DISABLED,
            font=('Consolas', 9))
        log_scroll = ttk.Scrollbar(log_frame, command=self.system_log.yview)
        self.system_log.config(yscrollcommand=log_scroll.set)
        self.system_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def create_comm_log_tab(self, notebook):
        comm_log_frame = ttk.Frame(notebook)
        notebook.add(comm_log_frame, text='Agent Communication')
        self.comm_tree = ttk.Treeview(comm_log_frame, columns=('Time',
            'From', 'To', 'Message'), show='headings')
        self.comm_tree.pack(fill=tk.BOTH, expand=True)
        self.comm_tree.heading('Time', text='Time')
        self.comm_tree.column('Time', width=100)
        self.comm_tree.heading('From', text='From Agent')
        self.comm_tree.column('From', width=150)
        self.comm_tree.heading('To', text='To Agent')
        self.comm_tree.column('To', width=150)
        self.comm_tree.heading('Message', text='Message')
        self.comm_tree.column('Message', width=500)

    def start_system(self):
        self.hidr = MultiAgentHIDR(require_human_approval=False)
        self.monitoring_active = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_system('Multi-Agent HIDR System Started.')
        messagebox.showinfo('System Started',
            'The multi-agent HIDR system is now active.')
        self.hidr.human_approval_callback = self.handle_human_approval

    def stop_system(self):
        self.monitoring_active = False
        self.hidr = None
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_system('Multi-Agent HIDR System Stopped.')
        messagebox.showinfo('System Stopped',
            'The multi-agent HIDR system has been deactivated.')

    def run_test_scenario(self):
        if not self.monitoring_active:
            messagebox.showwarning('System Offline',
                'Please start the system before running a test.')
            return

        def test_thread():
            self.log_system('Starting test scenario: Suspicious process...')
            result = self.hidr.analyze_process('ransomware.exe',
                'C:\\Users\\test\\AppData\\Local\\Temp\\ransomware.exe',
                'ransomware.exe --encrypt-all', 9999)
            self.log_system('Test scenario complete.')
            self.update_gui_with_results(result)
        threading.Thread(target=test_thread, daemon=True).start()

    def handle_human_approval(self, analysis_result):
        self.log_system('Human approval required!')
        response = messagebox.askyesno('Human Approval Required',
            f"""Suspicious activity detected!

AI Analysis: {analysis_result.get('summary')}

Do you want to block this activity?"""
            )
        return {'approved': response}

    def is_suspicious_process(self, proc_name, path, cmdline):
        if not path:
            return False
        allowlist = ['C:\\Windows\\System32\\', 'C:\\Program Files\\',
            'C:\\Program Files (x86)\\']
        if any(path.startswith(allowed) for allowed in allowlist):
            return False
        suspicious_indicators = ['temp' in path.lower(), 'downloads' in
            path.lower(), proc_name.lower() in ['encryptor.exe',
            'locker.exe', 'crypt.exe', 'ransomware.exe', 'keylogger.exe'],
            'powershell' in proc_name.lower() and ('encodedcommand' in
            cmdline.lower() or '-enc' in cmdline.lower()), 'suspicious' in
            proc_name.lower(), 'malware' in proc_name.lower()]
        return any(suspicious_indicators)

    def log_comm(self, from_agent, to_agent, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.comm_tree.insert('', 'end', values=(timestamp, from_agent,
            to_agent, message))

    def log_system(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.system_log.config(state=tk.NORMAL)
        self.system_log.insert(tk.END, f'[{timestamp}] {message}\n')
        self.system_log.config(state=tk.DISABLED)
        self.system_log.see(tk.END)

    def update_gui_with_results(self, result):
        self.log_system('Analysis complete. Final Action: ' + result.get(
            'final_action', 'N/A'))
        for msg in result.get('messages', []):
            self.log_comm(msg['from_agent'], msg['to_agent'], msg['message'])


if __name__ == '__main__':
    app = MultiAgentGUI()
    app.root.mainloop()
