"""About View - PyQt6"""
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt

logger = logging.getLogger('HIDR.AboutView')

class AboutView(QWidget):
    """About and system information view"""
    def __init__(self):
        super().__init__()
        self._create_ui()
        logger.info("About view initialized")
    
    def _create_ui(self):
        """Create UI layout"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("About HIDR")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # About text
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <div style='text-align: center; padding: 20px;'>
            <h1>🛡️ HIDR</h1>
            <h2>Hybrid Intelligent Detection & Response</h2>
            <p><b>Version:</b> 3.0.0</p>
            <p><b>Release:</b> October 2025</p>
            <hr>
            <h3>About</h3>
            <p>HIDR is a multi-agent cybersecurity system that automatically detects and responds to threats on your system.</p>
            
            <h3>Features</h3>
            <ul style='text-align: left; display: inline-block;'>
                <li>Path-Based Trust System</li>
                <li>YARA Signature Scanning (5 rule categories)</li>
                <li>Expert System with Weighted Scoring</li>
                <li>Behavioral Analysis</li>
                <li>Certificate Validation (OCSP/CRL/CT)</li>
                <li>MITRE ATT&CK Mapping</li>
                <li>Automated Response (Quarantine/Terminate)</li>
            </ul>
            
            <h3>Creator</h3>
            <p><b>Lakshya Agarwal (SecuVortex)</b></p>
            <p>Email: secuvortex@gmail.com</p>
            
            <h3>License</h3>
            <p>MIT License - Open Source</p>
            
            <hr>
            <p><i>Built with ❤️ for Defensive Cybersecurity</i></p>
            <p><i>Making security accessible, one threat at a time.</i></p>
        </div>
        """)
        layout.addWidget(about_text)
        
        self.setLayout(layout)
