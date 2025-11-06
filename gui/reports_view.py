"""Reports View - PyQt6"""
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTextEdit, QLabel, QGroupBox)
from PyQt6.QtCore import Qt

logger = logging.getLogger('HIDR.ReportsView')

class ReportsView(QWidget):
    """Reports and statistics view"""
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.stats = {'total_scans': 0, 'threats_detected': 0, 'files_quarantined': 0,
                     'yara_detections': 0, 'mb_detections': 0, 'actions_taken': 0}
        self._create_ui()
        logger.info("Reports view initialized")
    
    def _create_ui(self):
        """Create UI layout"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Scan Reports & Statistics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Stats group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        self._update_stats_display()
        stats_layout.addWidget(self.stats_text)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_stats)
        btn_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("📊 Export Report")
        export_btn.clicked.connect(self._export_report)
        btn_layout.addWidget(export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Recent threats
        threats_group = QGroupBox("Recent Threats (24h)")
        threats_layout = QVBoxLayout()
        
        self.threats_text = QTextEdit()
        self.threats_text.setReadOnly(True)
        threats_layout.addWidget(self.threats_text)
        
        threats_group.setLayout(threats_layout)
        layout.addWidget(threats_group)
        
        self.setLayout(layout)
        self._refresh_stats()
        
        # Auto-refresh every 10 seconds
        from PyQt6.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_stats)
        self.timer.start(10000)
    
    def update_stats(self, **kwargs):
        """Update statistics"""
        self.stats.update(kwargs)
        self._update_stats_display()
    
    def _update_stats_display(self):
        """Update stats text"""
        self.stats_text.setText(f"""
Total Scans: {self.stats['total_scans']}
Threats Detected: {self.stats['threats_detected']}
Files Quarantined: {self.stats['files_quarantined']}
YARA Detections: {self.stats['yara_detections']}
MalwareBazaar Detections: {self.stats['mb_detections']}
Actions Taken: {self.stats['actions_taken']}
""")
    
    def _refresh_stats(self):
        """Refresh statistics from database"""
        try:
            db_stats = self.database.get_stats()
            threats_24h = self.database.get_threats_24h()
            
            self.stats['total_scans'] = db_stats.get('total_scans', 0)
            self.stats['threats_detected'] = db_stats.get('total_threats', 0)
            
            self._update_stats_display()
            
            # Update threats list
            threats_text = ""
            for timestamp, threat_level in threats_24h:
                threats_text += f"{timestamp}: Threat Level {threat_level}/10\n"
            
            self.threats_text.setText(threats_text or "No threats in last 24 hours")
            
            logger.info("Stats refreshed")
        except Exception as e:
            logger.error(f"Failed to refresh stats: {e}")
    
    def _export_report(self):
        """Export report"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json
        from datetime import datetime
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "", "JSON Files (*.json);;HTML Files (*.html)"
        )
        
        if not filename:
            return
        
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'statistics': self.stats,
                'threats_24h': self.database.get_threats_24h()
            }
            
            if filename.endswith('.json'):
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
            else:
                # Simple HTML report
                html = f"""<html><body>
                <h1>HIDR Report</h1>
                <p>Generated: {report['timestamp']}</p>
                <h2>Statistics</h2>
                <ul>
                {''.join(f'<li>{k}: {v}</li>' for k, v in self.stats.items())}
                </ul>
                </body></html>"""
                with open(filename, 'w') as f:
                    f.write(html)
            
            QMessageBox.information(self, "Success", f"Report exported to {filename}")
            logger.info(f"Report exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")
            logger.error(f"Export failed: {e}")
    
    def log_threat(self, name, threat, yara_count, action):
        """Log a threat"""
        self.stats['threats_detected'] += 1
        if yara_count > 0:
            self.stats['yara_detections'] += 1
        if action != 'allow':
            self.stats['actions_taken'] += 1
        self._update_stats_display()
