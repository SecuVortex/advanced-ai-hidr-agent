"""HIDR - Hybrid Intelligent Detection & Response
Main application entry point
"""
import sys
import logging
from pathlib import Path

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'hidr_ui.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('HIDR.Main')

def main():
    """Main application entry point"""
    try:
        # Import and run production GUI
        import tkinter as tk
        from tkinter import ttk
        from simple_multiagent import SimpleMultiAgent
        from core.database import Database
        from core.auto_scanner import AutoScanner
        from core.background_monitor import BackgroundMonitor
        from core.event_queue import EventQueue
        from gui.processes_tab import ProcessesTab
        from gui.quarantine_tab import QuarantineTab
        from gui.reports_tab import ReportsTab
        from gui.settings_tab import SettingsTab
        from gui.dashboard_tab import DashboardTab
        from gui.agent_logs_tab import AgentLogsTab
        from gui.about_tab import AboutTab
        
        # Create main window
        root = tk.Tk()
        root.title("HIDR - Hybrid Intelligent Detection & Response")
        root.geometry("1400x900")
        
        # Initialize core components
        multiagent = SimpleMultiAgent()
        database = Database()
        auto_scanner = AutoScanner(multiagent)
        event_queue = EventQueue()
        background_monitor = BackgroundMonitor(multiagent, event_queue)
        
        # Create notebook
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        reports_tab = ReportsTab(notebook, database)
        processes_tab = ProcessesTab(notebook, multiagent, auto_scanner, reports_tab, database)
        quarantine_tab = QuarantineTab(notebook)
        dashboard_tab = DashboardTab(notebook, database)
        agent_logs_tab = AgentLogsTab(notebook)
        settings_tab = SettingsTab(notebook, auto_scanner)
        about_tab = AboutTab(notebook)
        
        # Add tabs
        notebook.add(processes_tab.get_frame(), text="🔍 Processes")
        notebook.add(quarantine_tab.get_frame(), text="🔒 Quarantine")
        notebook.add(reports_tab.get_frame(), text="📊 Reports")
        notebook.add(dashboard_tab.get_frame(), text="📈 Dashboard")
        notebook.add(agent_logs_tab.get_frame(), text="📋 Agent Logs")
        notebook.add(settings_tab.get_frame(), text="⚙ Settings")
        notebook.add(about_tab.get_frame(), text="ℹ About")
        
        # Connect event queue to agent logs
        agent_logs_tab.set_event_queue(event_queue)
        
        # Start background monitor
        background_monitor.start()
        
        logger.info("HIDR application started")
        
        # Run main loop
        try:
            root.mainloop()
        finally:
            background_monitor.stop()
            logger.info("HIDR application closed")
        
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
