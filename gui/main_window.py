"""Main Window - PyQt6 Professional GUI"""
import logging
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QToolBar,
                              QMessageBox, QWidget, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from simple_multiagent import SimpleMultiAgent
from core.database import ThreatDatabase
from gui.processes_view import ProcessesView
from gui.dashboard_view import DashboardView
from gui.quarantine_view import QuarantineView
from gui.settings_view import SettingsView

logger = logging.getLogger('HIDR.MainWindow')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIDR - Hybrid Intelligent Detection & Response")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize core components
        self.multiagent = SimpleMultiAgent()
        self.database = ThreatDatabase()
        
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
        """Create main tab widget"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Processes Tab
        self.processes_view = ProcessesView(self.multiagent, self.database)
        self.tabs.addTab(self.processes_view, "🔍 Processes")
        
        # Dashboard Tab
        self.dashboard_view = DashboardView(self.database)
        self.tabs.addTab(self.dashboard_view, "📊 Dashboard")
        
        # Quarantine Tab
        self.quarantine_view = QuarantineView()
        self.tabs.addTab(self.quarantine_view, "🔒 Quarantine")
        
        # Settings Tab
        self.settings_view = SettingsView()
        self.tabs.addTab(self.settings_view, "⚙ Settings")
    
    def _create_statusbar(self):
        """Create status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
    
    def _start_scan(self):
        """Start process scan"""
        self.processes_view.start_scan()
        self.statusbar.showMessage("Scanning processes...")
    
    def _stop_scan(self):
        """Stop process scan"""
        self.processes_view.stop_scan()
        self.statusbar.showMessage("Scan stopped")
    
    def _export_data(self):
        """Export scan results"""
        self.processes_view.export_results()
    
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
