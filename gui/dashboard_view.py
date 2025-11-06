"""Dashboard View - Statistics and Charts"""
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

logger = logging.getLogger('HIDR.DashboardView')

class StatCard(QFrame):
    """Statistics card widget"""
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(title_label)
        
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def update_value(self, value):
        """Update card value"""
        self.value_label.setText(str(value))

class DashboardView(QWidget):
    """Dashboard with statistics"""
    def __init__(self, database):
        super().__init__()
        self.database = database
        self._create_ui()
        logger.info("Dashboard view initialized")
    
    def _create_ui(self):
        """Create UI layout"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("System Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Stats cards
        cards_layout = QHBoxLayout()
        
        self.total_scans_card = StatCard("Total Scans", "0")
        cards_layout.addWidget(self.total_scans_card)
        
        self.threats_card = StatCard("Active Threats", "0")
        cards_layout.addWidget(self.threats_card)
        
        self.quarantined_card = StatCard("Quarantined", "0")
        cards_layout.addWidget(self.quarantined_card)
        
        self.yara_card = StatCard("YARA Detections", "0")
        cards_layout.addWidget(self.yara_card)
        
        layout.addLayout(cards_layout)
        
        # Placeholder for charts
        chart_label = QLabel("Charts: Coming soon (matplotlib/plotly integration)")
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_label.setStyleSheet("padding: 50px; color: #888;")
        layout.addWidget(chart_label)
        
        layout.addStretch()
        self.setLayout(layout)
