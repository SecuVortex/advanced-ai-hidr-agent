"""Processes View - PyQt6 Table with Real-time Scanning"""
import logging
import psutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLineEdit, QLabel, QTableView, QHeaderView,
                              QMenu, QMessageBox, QDialog, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QAction
from datetime import datetime

logger = logging.getLogger('HIDR.ProcessesView')

class ProcessTableModel(QAbstractTableModel):
    """Table model for process data"""
    def __init__(self):
        super().__init__()
        self.headers = ["PID", "Name", "Publisher", "Parent", "Threat", "YARA", "Cert", "Action"]
        self.processes = []
        self._filter_text = ""
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.processes)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self.processes[row][col]
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Color code by threat level
            threat_str = str(self.processes[row][4])
            try:
                threat = int(threat_str.split('/')[0])
                if threat >= 7:
                    return QColor(139, 0, 0, 50)  # Dark red
                elif threat >= 5:
                    return QColor(255, 140, 0, 50)  # Orange
                elif threat >= 3:
                    return QColor(255, 255, 0, 30)  # Yellow
            except:
                pass
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None
    
    def add_process(self, process_data):
        """Add process to table"""
        row = len(self.processes)
        self.beginInsertRows(QModelIndex(), row, row)
        self.processes.append(process_data)
        self.endInsertRows()
    
    def clear(self):
        """Clear all processes"""
        self.beginResetModel()
        self.processes.clear()
        self.endResetModel()
    
    def get_process(self, row):
        """Get process data by row"""
        if 0 <= row < len(self.processes):
            return self.processes[row]
        return None

class ScanWorker(QThread):
    """Background thread for process scanning"""
    process_found = pyqtSignal(tuple)
    scan_complete = pyqtSignal(dict)
    
    def __init__(self, multiagent):
        super().__init__()
        self.multiagent = multiagent
        self.running = False
    
    def run(self):
        """Scan all processes"""
        self.running = True
        stats = {'scanned': 0, 'threats': 0, 'quarantined': 0}
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                if not self.running:
                    break
                
                try:
                    pid = proc.info.get('pid', -1)
                    name = proc.info.get('name') or "Unknown"
                    path = proc.info.get('exe') or "N/A"
                    cmdline = ' '.join(proc.info.get('cmdline') or [])
                    
                    # Analyze process
                    result = self.multiagent.analyze_process(name, path, cmdline, pid)
                    
                    detection = result.get('detection_result', {})
                    intelligence = result.get('intelligence_result', {})
                    
                    threat = detection.get('threat_level', 0)
                    yara_count = len(detection.get('yara_matches', []))
                    action = result.get('final_action', 'allow')
                    
                    # Extract publisher
                    publisher = self._extract_publisher(path)
                    
                    # Extract cert status
                    cert_validation = intelligence.get('cert_validation', {})
                    cert_display = self._format_cert(cert_validation, path)
                    
                    # Get parent
                    try:
                        parent_proc = psutil.Process(pid).parent()
                        parent_name = parent_proc.name() if parent_proc else "-"
                    except:
                        parent_name = "-"
                    
                    # Emit process data
                    process_data = (
                        pid,
                        name[:30],
                        publisher[:20],
                        parent_name[:15],
                        f"{threat}/10",
                        yara_count,
                        cert_display,
                        action
                    )
                    
                    self.process_found.emit(process_data)
                    
                    stats['scanned'] += 1
                    if threat >= 5:
                        stats['threats'] += 1
                    
                    self.msleep(50)  # Throttle
                    
                except Exception as e:
                    logger.debug(f"Error scanning PID {pid}: {e}")
                    continue
        
        finally:
            self.scan_complete.emit(stats)
    
    def stop(self):
        """Stop scanning"""
        self.running = False
    
    def _extract_publisher(self, path):
        """Extract publisher from path"""
        if not path or path == "N/A":
            return "Unknown"
        
        path_lower = path.lower()
        if "windows" in path_lower or "system32" in path_lower:
            return "Microsoft"
        elif "google" in path_lower:
            return "Google"
        elif "program files" in path_lower:
            parts = path.split("\\")
            for i, part in enumerate(parts):
                if "program files" in part.lower() and i + 1 < len(parts):
                    return parts[i + 1][:20]
        
        return "Unknown"
    
    def _format_cert(self, cert_validation, path):
        """Format certificate status"""
        if not path.endswith('.exe'):
            return "N/A"
        
        if not cert_validation:
            path_lower = path.lower()
            if "windows" in path_lower or "system32" in path_lower:
                return "System"
            return "Unsigned"
        
        verdict = cert_validation.get('verdict', '')
        if verdict == 'valid':
            return "✓ Valid"
        elif verdict == 'revoked':
            return "⚠ Revoked"
        elif verdict in ('invalid', 'untrusted'):
            return "✗ Invalid"
        
        return "Unsigned"

class ProcessesView(QWidget):
    """Main processes view widget"""
    def __init__(self, multiagent, database):
        super().__init__()
        self.multiagent = multiagent
        self.database = database
        self.scan_worker = None
        
        self._create_ui()
        logger.info("Processes view initialized")
    
    def _create_ui(self):
        """Create UI layout"""
        layout = QVBoxLayout()
        
        # Top controls
        controls = QHBoxLayout()
        
        # Filter
        controls.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search by name, PID, publisher...")
        self.filter_input.textChanged.connect(self._apply_filter)
        controls.addWidget(self.filter_input)
        
        # Buttons
        self.start_btn = QPushButton("⚡ Start Scan")
        self.start_btn.clicked.connect(self.start_scan)
        controls.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        controls.addWidget(self.stop_btn)
        
        layout.addLayout(controls)
        
        # Table
        self.model = ProcessTableModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self._show_details)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        layout.addWidget(self.table)
        
        # Stats
        self.stats_label = QLabel("Scanned: 0 | Threats: 0 | Quarantined: 0")
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def start_scan(self):
        """Start process scan"""
        if self.scan_worker and self.scan_worker.isRunning():
            return
        
        self.model.clear()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.scan_worker = ScanWorker(self.multiagent)
        self.scan_worker.process_found.connect(self._add_process)
        self.scan_worker.scan_complete.connect(self._scan_finished)
        self.scan_worker.start()
        
        logger.info("Process scan started")
    
    def stop_scan(self):
        """Stop process scan"""
        if self.scan_worker:
            self.scan_worker.stop()
            self.scan_worker.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        logger.info("Process scan stopped")
    
    def _add_process(self, process_data):
        """Add process to table"""
        self.model.add_process(process_data)
    
    def _scan_finished(self, stats):
        """Handle scan completion"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.stats_label.setText(
            f"Scanned: {stats['scanned']} | "
            f"Threats: {stats['threats']} | "
            f"Quarantined: {stats['quarantined']}"
        )
        
        logger.info(f"Scan complete: {stats}")
    
    def _apply_filter(self):
        """Apply filter to table"""
        # TODO: Implement proxy model filtering
        pass
    
    def _show_details(self, index):
        """Show process details dialog"""
        row = index.row()
        process_data = self.model.get_process(row)
        
        if not process_data:
            return
        
        dialog = ProcessDetailsDialog(process_data, self.multiagent, self)
        dialog.exec()
    
    def _show_context_menu(self, position):
        """Show context menu"""
        index = self.table.indexAt(position)
        if not index.isValid():
            return
        
        menu = QMenu()
        
        details_action = menu.addAction("ℹ View Details")
        reanalyze_action = menu.addAction("🔄 Reanalyze")
        menu.addSeparator()
        terminate_action = menu.addAction("⚠ Terminate")
        quarantine_action = menu.addAction("🚨 Terminate & Quarantine")
        menu.addSeparator()
        whitelist_action = menu.addAction("✅ Add to Whitelist")
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == details_action:
            self._show_details(index)
        elif action == terminate_action:
            self._terminate_process(index, False)
        elif action == quarantine_action:
            self._terminate_process(index, True)
    
    def _terminate_process(self, index, quarantine=False):
        """Terminate process (simulated mode)"""
        process_data = self.model.get_process(index.row())
        if not process_data:
            return
        
        pid = process_data[0]
        name = process_data[1]
        
        reply = QMessageBox.warning(
            self,
            "Simulated Mode",
            f"SIMULATED: Would terminate {name} (PID: {pid})\n\n"
            f"Quarantine: {quarantine}\n\n"
            f"Run as Administrator to enable real termination.",
            QMessageBox.StandardButton.Ok
        )
        
        logger.info(f"SIMULATED: Terminate {name} (PID: {pid}), quarantine={quarantine}")
    
    def export_results(self):
        """Export scan results"""
        # TODO: Implement CSV/JSON export
        QMessageBox.information(self, "Export", "Export functionality coming soon")

class ProcessDetailsDialog(QDialog):
    """Process details dialog"""
    def __init__(self, process_data, multiagent, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Process Details - {process_data[1]}")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # Summary tab
        summary = QTextEdit()
        summary.setReadOnly(True)
        summary.setText(f"""PROCESS SUMMARY
{'='*70}

PID: {process_data[0]}
Name: {process_data[1]}
Publisher: {process_data[2]}
Parent: {process_data[3]}
Threat Level: {process_data[4]}
YARA Matches: {process_data[5]}
Certificate: {process_data[6]}
Action: {process_data[7]}
""")
        tabs.addTab(summary, "Summary")
        
        # ML tab
        ml_tab = QTextEdit()
        ml_tab.setReadOnly(True)
        ml_tab.setText("""ML & BEHAVIORAL ANALYSIS
{'='*70}

ML Score: N/A - Model not configured
Behavioral Score: N/A
Confidence: N/A

Note: ML model not loaded. Using heuristic fallback.
""")
        tabs.addTab(ml_tab, "ML & Confidence")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
