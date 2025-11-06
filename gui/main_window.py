"""Main Window - PyQt6 with Tkinter Integration"""
import logging
import tkinter as tk
from tkinter import ttk
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QStatusBar, 
                              QToolBar, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from simple_multiagent import SimpleMultiAgent
from core.database import Database
from core.auto_scanner import AutoScanner
from gui.processes_tab import ProcessesTab
from gui.quarantine_tab import QuarantineTab
from gui.reports_tab import ReportsTab
from gui.settings_tab import SettingsTab
from gui.dashboard_tab import DashboardTab
from gui.agent_logs_tab import AgentLogsTab
from gui.about_tab import AboutTab

logger = logging.getLogger('HIDR.MainWindow')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIDR - Hybrid Intelligent Detection & Response")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize core components
        self.multiagent = SimpleMultiAgent()
        self.database = Database()
        self.auto_scanner = AutoScanner(self.multiagent)
        
        # Create Tkinter root (embedded)
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()  # Hide root window
        
        # Setup UI
        self._create_toolbar()
        self._create_tabs()
        self._create_statusbar()
        
        # Apply theme
        self.apply_theme('dark')
        
        logger.info("Main window initialized")
    
    def _create_toolbar(self):
        """Create main toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Start Scan
        scan_action = QAction("⚡ Start Scan", self)
        scan_action.setShortcut("Ctrl+S")
        scan_action.triggered.connect(self._start_scan)
        toolbar.addAction(scan_action)
        
        # Stop Scan
        stop_action = QAction("⏹ Stop", self)
        stop_action.triggered.connect(self._stop_scan)
        toolbar.addAction(stop_action)
        
        toolbar.addSeparator()
        
        # Export
        export_action = QAction("📊 Export", self)
        export_action.triggered.connect(self._export_data)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Theme Toggle
        theme_action = QAction("🌓 Theme", self)
        theme_action.triggered.connect(self._toggle_theme)
        toolbar.addAction(theme_action)
        
        self.toolbar = toolbar
    
    def _create_tabs(self):
        """Create main tab widget with Tkinter tabs"""
        # Create Tkinter notebook
        self.notebook = ttk.Notebook(self.tk_root)
        
        # Create tabs using existing Tkinter components
        self.reports_tab = ReportsTab(self.notebook, self.database)
        self.processes_tab = ProcessesTab(self.notebook, self.multiagent, 
                                         self.auto_scanner, self.reports_tab, self.database)
        self.quarantine_tab = QuarantineTab(self.notebook)
        self.dashboard_tab = DashboardTab(self.notebook, self.database)
        self.agent_logs_tab = AgentLogsTab(self.notebook)
        self.settings_tab = SettingsTab(self.notebook, self.auto_scanner)
        self.about_tab = AboutTab(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.processes_tab.get_frame(), text="🔍 Processes")
        self.notebook.add(self.quarantine_tab.get_frame(), text="🔒 Quarantine")
        self.notebook.add(self.reports_tab.get_frame(), text="📊 Reports")
        self.notebook.add(self.dashboard_tab.get_frame(), text="📈 Dashboard")
        self.notebook.add(self.agent_logs_tab.get_frame(), text="📋 Agent Logs")
        self.notebook.add(self.settings_tab.get_frame(), text="⚙ Settings")
        self.notebook.add(self.about_tab.get_frame(), text="ℹ About")
        
        # Embed Tkinter in PyQt6
        from PyQt6.QtWidgets import QWidget
        from PyQt6.QtCore import QTimer
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Create a simple label for now (Tkinter embedding is complex)
        from PyQt6.QtWidgets import QLabel
        label = QLabel("HIDR GUI - Using Tkinter Backend")
        label.setStyleSheet("font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        self.setCentralWidget(container)
        
        # Start Tkinter event loop in background
        self.tk_timer = QTimer()
        self.tk_timer.timeout.connect(self._update_tk)
        self.tk_timer.start(100)
        
        logger.info("Tabs initialized with Tkinter backend")
    
    def _update_tk(self):
        """Update Tkinter event loop"""
        try:
            self.tk_root.update()
        except:
            pass
    
    def _create_statusbar(self):
        """Create status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
    
    def _start_scan(self):
        """Start process scan"""
        self.processes_tab.start_scan()
        self.statusbar.showMessage("Scanning processes...")
    
    def _stop_scan(self):
        """Stop process scan"""
        self.processes_tab.stop_scan()
        self.statusbar.showMessage("Scan stopped")
    
    def _export_data(self):
        """Export scan results"""
        self.statusbar.showMessage("Export functionality available in Reports tab")
    
    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        current = getattr(self, '_current_theme', 'dark')
        new_theme = 'light' if current == 'dark' else 'dark'
        self.apply_theme(new_theme)
    
    def apply_theme(self, theme='dark'):
        """Apply color theme"""
        self._current_theme = theme
        
        if theme == 'dark':
            stylesheet = """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #d4d4d4;
                padding: 8px 16px;
                border: 1px solid #3c3c3c;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QToolBar {
                background-color: #2d2d30;
                border: none;
                spacing: 5px;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QTableView {
                background-color: #1e1e1e;
                alternate-background-color: #252526;
                gridline-color: #3c3c3c;
                selection-background-color: #094771;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #d4d4d4;
                padding: 5px;
                border: 1px solid #3c3c3c;
            }
            """
        else:
            stylesheet = """
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #f3f3f3;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #000000;
                padding: 8px 16px;
                border: 1px solid #cccccc;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: white;
            }
            QToolBar {
                background-color: #f0f0f0;
                border: none;
            }
            QStatusBar {
                background-color: #0078d4;
                color: white;
            }
            """
        
        self.setStyleSheet(stylesheet)
        logger.info(f"Applied {theme} theme")
    
    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            'Are you sure you want to exit HIDR?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing")
            event.accept()
        else:
            event.ignore()
