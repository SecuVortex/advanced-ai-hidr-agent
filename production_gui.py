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
from core.background_monitor import BackgroundMonitor
from core.event_queue import EventQueue
from core.database import Database
from gui.dashboard_tab import DashboardTab
from gui.processes_tab import ProcessesTab
from gui.quarantine_tab import QuarantineTab
from gui.reports_tab import ReportsTab
from gui.settings_tab import SettingsTab
from gui.about_tab import AboutTab
from gui.agent_logs_tab import AgentLogsTab

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
        
        # Phase 1: Real-time monitoring components
        self.event_queue = EventQueue()
        self.background_monitor = BackgroundMonitor(self._handle_event, interval=5)
        
        # Phase 2: Database
        self.database = Database()
        
        self._create_widgets()
        
        # Start background monitoring
        self.background_monitor.start()
        
        # Phase 6: Add keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Start GUI update loop
        self.root.after(500, self._update_from_queue)
        
    def _create_widgets(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: self.notebook.select(6))
        
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
        self.dashboard_tab = DashboardTab(self.notebook, self.database)
        self.reports_tab = ReportsTab(self.notebook)
        self.processes_tab = ProcessesTab(self.notebook, self.multiagent, self.auto_scanner, self.reports_tab, self.database)
        self.quarantine_tab = QuarantineTab(self.notebook)
        self.agent_logs_tab = AgentLogsTab(self.notebook)
        self.settings_tab = SettingsTab(self.notebook, self.auto_scanner)
        self.about_tab = AboutTab(self.notebook, self.multiagent)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab.get_frame(), text="Dashboard")
        self.notebook.add(self.processes_tab.get_frame(), text="Processes")
        self.notebook.add(self.quarantine_tab.get_frame(), text="Quarantine")
        self.notebook.add(self.reports_tab.get_frame(), text="Reports")
        self.notebook.add(self.agent_logs_tab.get_frame(), text="Agent Logs")
        self.notebook.add(self.settings_tab.get_frame(), text="Settings")
        self.notebook.add(self.about_tab.get_frame(), text="About")
        
        # Footer
        footer = ttk.Frame(self.root)
        footer.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(footer, text="HIDR v3.0 | SecuVortex (Lakshya Agarwal) | © 2025", font=('Arial', 8)).pack(side=tk.LEFT)
        
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
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts (Phase 6)"""
        # Scan shortcut
        self.root.bind('<Control-s>', lambda e: self._safe_start_scan())
        self.root.bind('<Control-S>', lambda e: self._safe_start_scan())
        
        # Refresh shortcuts
        self.root.bind('<Control-r>', lambda e: self._safe_refresh())
        self.root.bind('<Control-R>', lambda e: self._safe_refresh())
        self.root.bind('<F5>', lambda e: self._safe_refresh())
        
        # Export shortcut
        self.root.bind('<Control-e>', lambda e: self._safe_export())
        self.root.bind('<Control-E>', lambda e: self._safe_export())
        
        # Quit shortcut
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
        
        # Show shortcuts help
        self.root.bind('<F1>', lambda e: self._show_shortcuts_help())
    
    def _safe_start_scan(self):
        """Safely start scan if not already running"""
        try:
            if not self.processes_tab.running:
                self.processes_tab.start_scan()
                self.status_label.config(text="Scan started (Ctrl+S)")
        except Exception as e:
            print(f"Scan error: {e}")
    
    def _safe_refresh(self):
        """Safely refresh dashboard"""
        try:
            self.dashboard_tab.update_dashboard()
            self.status_label.config(text="Dashboard refreshed (F5)")
        except Exception as e:
            print(f"Refresh error: {e}")
    
    def _safe_export(self):
        """Safely export report"""
        try:
            self.reports_tab.export_html()
            self.status_label.config(text="Report exported (Ctrl+E)")
        except Exception as e:
            print(f"Export error: {e}")
    
    def _show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog"""
        from tkinter import messagebox
        help_text = """
Keyboard Shortcuts:

Ctrl+S - Start Scan
Ctrl+R / F5 - Refresh Dashboard
Ctrl+E - Export Report
Ctrl+Q - Quit Application
F1 - Show this help

Tip: Use keyboard shortcuts for faster workflow!
        """
        messagebox.showinfo("Keyboard Shortcuts", help_text)
    
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
    
    def _handle_event(self, event: dict):
        """Handle events from background monitor"""
        self.event_queue.put(event)
    
    def _update_from_queue(self):
        """Process events from queue and update GUI"""
        events = self.event_queue.get_all(max_events=10)
        
        for event in events:
            event_type = event.get('type')
            
            if event_type == 'PROCESS_DETECTED':
                # Log to agent logs
                self.agent_logs_tab.add_log(
                    'BackgroundMonitor',
                    f"New process: {event['name']} (PID: {event['pid']})",
                    'INFO'
                )
        
        # Schedule next update
        self.root.after(500, self._update_from_queue)
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            # Cleanup
            self.background_monitor.stop()

if __name__ == "__main__":
    app = ProductionGUI()
    app.run()
