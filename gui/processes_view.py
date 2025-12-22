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
    stats_update = pyqtSignal(dict)
    
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
                    if action in ['terminate_temporary', 'terminate_permanent']:
                        stats['quarantined'] += 1
                    
                    # Log threat to database
                    if threat >= 5:
                        try:
                            from core.database import Database
                            db = Database()
                            db.add_threat(name, pid, path, threat, str(detection.get('yara_matches', [])),
                                        str(detection.get('mitre_techniques', [])), action)
                        except Exception as e:
                            logger.debug(f"Failed to log threat: {e}")
                    
                    # Emit stats update every 10 processes
                    if stats['scanned'] % 10 == 0:
                        self.stats_update.emit(stats.copy())
                    
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
    def __init__(self, multiagent, database, reports_view=None):
        super().__init__()
        self.multiagent = multiagent
        self.database = database
        self.reports_view = reports_view
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
        self.start_btn.setText("⏳ Scanning...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.stats_label.setText("Scanning: 0 | Threats: 0 | Quarantined: 0")
        
        self.scan_worker = ScanWorker(self.multiagent)
        self.scan_worker.process_found.connect(self._add_process)
        self.scan_worker.stats_update.connect(self._update_stats)
        self.scan_worker.scan_complete.connect(self._scan_finished)
        self.scan_worker.start()
        
        logger.info("Process scan started")
    
    def stop_scan(self):
        """Stop process scan"""
        if self.scan_worker:
            self.scan_worker.stop()
            self.scan_worker.wait()
        
        self.start_btn.setText("⚡ Start Scan")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        logger.info("Process scan stopped")
    
    def _add_process(self, process_data):
        """Add process to table"""
        self.model.add_process(process_data)
    
    def _update_stats(self, stats):
        """Update stats during scan"""
        self.stats_label.setText(
            f"Scanning: {stats['scanned']} | "
            f"Threats: {stats['threats']} | "
            f"Quarantined: {stats['quarantined']}"
        )
    
    def _scan_finished(self, stats):
        """Handle scan completion"""
        self.start_btn.setText("⚡ Start Scan")
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
        filter_text = self.filter_input.text().lower()
        for row in range(self.model.rowCount()):
            process = self.model.get_process(row)
            if not process:
                continue
            
            # Search in PID, Name, Publisher, Parent
            match = (filter_text in str(process[0]) or
                    filter_text in str(process[1]).lower() or
                    filter_text in str(process[2]).lower() or
                    filter_text in str(process[3]).lower())
            
            self.table.setRowHidden(row, not match)
    
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
        elif action == reanalyze_action:
            self._reanalyze_process(index)
        elif action == terminate_action:
            self._terminate_process(index, False)
        elif action == quarantine_action:
            self._terminate_process(index, True)
        elif action == whitelist_action:
            self._add_to_whitelist(index)
    
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
    
    def _reanalyze_process(self, index):
        """Reanalyze a specific process"""
        process_data = self.model.get_process(index.row())
        if not process_data:
            return
        
        pid = process_data[0]
        name = process_data[1]
        
        try:
            proc = psutil.Process(int(pid))
            path = proc.exe()
            cmdline = ' '.join(proc.cmdline())
            
            # Reanalyze
            result = self.multiagent.analyze_process(name, path, cmdline, pid)
            threat = result.get('detection_result', {}).get('threat_level', 0)
            action = result.get('final_action', 'allow')
            
            QMessageBox.information(
                self, "Reanalysis Complete",
                f"Process: {name}\nThreat: {threat}/10\nAction: {action}"
            )
            logger.info(f"Reanalyzed {name}: {threat}/10 - {action}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Reanalysis failed: {e}")
            logger.error(f"Reanalysis failed: {e}")
    
    def _add_to_whitelist(self, index):
        """Add process to whitelist"""
        import json
        import os
        
        process_data = self.model.get_process(index.row())
        if not process_data:
            return
        
        name = process_data[1]
        whitelist_file = 'config/whitelist.json'
        
        try:
            # Load existing whitelist
            if os.path.exists(whitelist_file):
                with open(whitelist_file, 'r') as f:
                    whitelist = json.load(f)
            else:
                whitelist = {'processes': []}
            
            # Add to whitelist
            if name not in whitelist.get('processes', []):
                whitelist.setdefault('processes', []).append(name)
                
                # Save whitelist
                os.makedirs('config', exist_ok=True)
                with open(whitelist_file, 'w') as f:
                    json.dump(whitelist, f, indent=2)
                
                QMessageBox.information(
                    self, "Success",
                    f"{name} added to whitelist.\n\nIt will be ignored in future scans."
                )
                logger.info(f"Added {name} to whitelist")
            else:
                QMessageBox.information(self, "Already Whitelisted", f"{name} is already in the whitelist.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add to whitelist: {e}")
            logger.error(f"Whitelist failed: {e}")
    
    def export_results(self):
        """Export scan results"""
        from PyQt6.QtWidgets import QFileDialog
        import csv
        import json
        
        filename, filter_type = QFileDialog.getSaveFileName(
            self, "Export Results", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if not filename:
            return
        
        try:
            processes = [self.model.get_process(i) for i in range(self.model.rowCount())]
            
            if filename.endswith('.csv'):
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.model.headers)
                    writer.writerows(processes)
            else:
                data = [dict(zip(self.model.headers, p)) for p in processes]
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            QMessageBox.information(self, "Success", f"Exported {len(processes)} processes to {filename}")
            logger.info(f"Exported {len(processes)} processes to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
            logger.error(f"Export failed: {e}")

class ProcessDetailsDialog(QDialog):
    """Process details dialog with full analysis"""
    def __init__(self, process_data, multiagent, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Process Details - {process_data[1]}")
        self.setGeometry(200, 200, 900, 700)
        
        pid = process_data[0]
        name = process_data[1]
        
        # Re-analyze to get full data
        try:
            proc = psutil.Process(int(pid))
            path = proc.exe()
            cmdline = ' '.join(proc.cmdline())
            result = multiagent.analyze_process(name, path, cmdline, pid)
            
            detection = result.get('detection_result', {})
            intelligence = result.get('intelligence_result', {})
            analysis = result.get('analysis_result', {})
        except:
            detection = {}
            intelligence = {}
            analysis = {}
        
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
Severity: {analysis.get('severity', 'N/A')}
""")
        tabs.addTab(summary, "Summary")
        
        # ML & Confidence tab
        ml_score = intelligence.get('ml_score', 0)
        behavior_score = intelligence.get('behavior_score', 0)
        yara_score = detection.get('yara_score', 0)
        mb_score = intelligence.get('malwarebazaar', {}).get('score', 0)
        
        weights = multiagent.config.get('expert_system', {}).get('weights', {})
        yara_weight = weights.get('yara', 3.0)
        ml_weight = weights.get('ml', 3.0)
        behavior_weight = weights.get('behavioral', 1.5)
        mb_weight = weights.get('malwarebazaar', 3.5)
        
        ml_tab = QTextEdit()
        ml_tab.setReadOnly(True)
        ml_tab.setText(f"""ML & BEHAVIORAL ANALYSIS
{'='*70}

ML PREDICTION:
  ML Score: {ml_score:.2f}/10
  Model: Heuristic Fallback (no trained model)
  Confidence: {'Low' if ml_score < 3 else 'Medium' if ml_score < 7 else 'High'}

BEHAVIORAL ANALYSIS:
  Behavior Score: {behavior_score:.2f}/10
  Patterns: {', '.join(intelligence.get('behaviors', [])) or 'None'}

CONFIDENCE BREAKDOWN:
{'='*70}
  Component          Score    Weight    Contribution
  {'─'*70}
  YARA Signatures    {yara_score:5.1f}    {yara_weight:5.1f}     {yara_score * yara_weight:5.1f}
  ML Prediction      {ml_score:5.1f}    {ml_weight:5.1f}     {ml_score * ml_weight:5.1f}
  Behavioral         {behavior_score:5.1f}    {behavior_weight:5.1f}     {behavior_score * behavior_weight:5.1f}
  MalwareBazaar      {mb_score:5.1f}    {mb_weight:5.1f}     {mb_score * mb_weight:5.1f}
  {'─'*70}
  TOTAL: {analysis.get('threat_score', detection.get('threat_level', 0)):.1f}/10

FALLBACK: {analysis.get('ai_used', 'Expert System')}
""")
        tabs.addTab(ml_tab, "ML & Confidence")
        
        # Detection tab
        yara_matches = detection.get('yara_matches', [])
        mitre_techniques = detection.get('mitre_techniques', [])
        reasons = detection.get('reasons', [])
        
        detection_tab = QTextEdit()
        detection_tab.setReadOnly(True)
        detection_text = f"""DETECTION DETAILS
{'='*70}

YARA MATCHES ({len(yara_matches)}):
"""
        if yara_matches:
            for match in yara_matches:
                detection_text += f"  • {match.get('rule', 'Unknown')} - {match.get('severity', 'N/A')}\n"
                detection_text += f"    MITRE: {match.get('mitre', 'N/A')}\n"
        else:
            detection_text += "  No YARA matches\n"
        
        detection_text += f"\nMITRE ATT&CK TECHNIQUES ({len(mitre_techniques)}):\n"
        if mitre_techniques:
            for technique in mitre_techniques:
                detection_text += f"  • {technique}\n"
        else:
            detection_text += "  No MITRE techniques\n"
        
        detection_text += "\nDETECTION REASONS:\n"
        for reason in reasons:
            detection_text += f"  • {reason}\n"
        
        detection_tab.setText(detection_text)
        tabs.addTab(detection_tab, "Detection")
        
        # Certificate tab
        cert_validation = intelligence.get('cert_validation', {})
        cert_tab = QTextEdit()
        cert_tab.setReadOnly(True)
        cert_tab.setText(f"""CERTIFICATE VALIDATION
{'='*70}

Status: {cert_validation.get('verdict', 'Not validated').upper()}
Score: {cert_validation.get('cert_score', 'N/A')}/100
Chain Length: {cert_validation.get('chain_length', 'N/A')}

Errors:
{chr(10).join('  • ' + str(e) for e in cert_validation.get('errors', [])) or '  No errors'}
""")
        tabs.addTab(cert_tab, "Certificate")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
