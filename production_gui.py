"""
Production GUI - Enhanced 5-tab interface
"""
import tkinter as tk
from tkinter import ttk
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from simple_multiagent import SimpleMultiAgent
from core.auto_scanner import AutoScanner
from gui.processes_tab import ProcessesTab
from gui.quarantine_tab import QuarantineTab
from gui.reports_tab import ReportsTab
from gui.settings_tab import SettingsTab
from gui.about_tab import AboutTab

class ProductionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HIDR Multi-Agent System - Production")
        self.root.geometry("1200x700")
        
        # Check for admin rights on Windows
        self._check_admin_rights()
        
        # Load config to check LangGraph setting
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            use_langgraph = config.get('langgraph', {}).get('enabled', False)
        except:
            use_langgraph = False
        
        # Initialize multiagent system with LangGraph if enabled
        self.multiagent = SimpleMultiAgent(use_langgraph=use_langgraph)
        self.auto_scanner = AutoScanner(self.multiagent, interval_minutes=5)
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: self.notebook.select(4))
        
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header, text="HIDR Multi-Agent System", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        status_frame = ttk.Frame(header)
        status_frame.pack(side=tk.RIGHT)
        
        ttk.Label(status_frame, text="Status:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green", font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.reports_tab = ReportsTab(self.notebook)
        self.processes_tab = ProcessesTab(self.notebook, self.multiagent, self.auto_scanner, self.reports_tab)
        self.quarantine_tab = QuarantineTab(self.notebook)
        self.settings_tab = SettingsTab(self.notebook, self.auto_scanner)
        self.about_tab = AboutTab(self.notebook, self.multiagent)
        
        # Add tabs to notebook
        self.notebook.add(self.processes_tab.get_frame(), text="Processes")
        self.notebook.add(self.quarantine_tab.get_frame(), text="Quarantine")
        self.notebook.add(self.reports_tab.get_frame(), text="Reports")
        self.notebook.add(self.settings_tab.get_frame(), text="Settings")
        self.notebook.add(self.about_tab.get_frame(), text="About")
        
        # Footer
        footer = ttk.Frame(self.root)
        footer.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(footer, text="HIDR v2.0 | Production Ready | © 2024", font=('Arial', 8)).pack(side=tk.LEFT)
        
        # Agent status indicators
        agent_status = ttk.Frame(footer)
        agent_status.pack(side=tk.RIGHT)
        
        agents = [
            ("YARA", self.multiagent.yara_scanner is not None),
            ("Expert", self.multiagent.expert_system is not None),
            ("LangGraph", self.multiagent.langgraph_orchestrator is not None)
        ]
        
        for name, active in agents:
            color = "green" if active else "gray"
            ttk.Label(agent_status, text=f"{name}: ", font=('Arial', 8)).pack(side=tk.LEFT)
            ttk.Label(agent_status, text="●", foreground=color, font=('Arial', 12)).pack(side=tk.LEFT, padx=(0, 10))
    
    def _check_admin_rights(self):
        import platform
        if platform.system() == 'Windows':
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    from tkinter import messagebox
                    messagebox.showwarning(
                        "Administrator Rights Required",
                        "HIDR requires Administrator privileges to terminate processes and quarantine files.\n\n"
                        "Some features may not work properly.\n\n"
                        "Please restart as Administrator for full functionality."
                    )
            except:
                pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProductionGUI()
    app.run()
