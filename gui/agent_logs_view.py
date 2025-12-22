"""Agent Logs View - PyQt6"""
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextCursor

logger = logging.getLogger('HIDR.AgentLogsView')

class AgentLogsView(QWidget):
    """Agent activity logs view"""
    def __init__(self):
        super().__init__()
        self.event_queue = None
        self._create_ui()
        logger.info("Agent logs view initialized")
    
    def _create_ui(self):
        """Create UI layout"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Agent Activity Logs")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Logs text area
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("font-family: 'Consolas', monospace;")
        layout.addWidget(self.logs_text)
        
        self.setLayout(layout)
        
        # Setup timer to poll event queue
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_logs)
        self.timer.start(500)  # Update every 500ms
    
    def set_event_queue(self, event_queue):
        """Set event queue for monitoring"""
        self.event_queue = event_queue
    
    def _update_logs(self):
        """Update logs from event queue"""
        if not self.event_queue:
            return
        
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get()
                
                # Format event
                timestamp = event.get('timestamp', '')
                agent = event.get('agent', 'Unknown')
                action = event.get('action', '')
                details = event.get('details', '')
                
                log_entry = f"[{timestamp}] {agent}: {action} - {details}\n"
                
                # Color code by agent
                if 'Detection' in agent:
                    color = '#4CAF50'  # Green
                elif 'Intelligence' in agent:
                    color = '#2196F3'  # Blue
                elif 'Analysis' in agent:
                    color = '#FF9800'  # Orange
                elif 'Response' in agent:
                    color = '#F44336'  # Red
                else:
                    color = '#9E9E9E'  # Gray
                
                # Append with color
                self.logs_text.moveCursor(QTextCursor.MoveOperation.End)
                self.logs_text.insertHtml(f'<span style="color: {color};">{log_entry}</span>')
                self.logs_text.moveCursor(QTextCursor.MoveOperation.End)
                
        except Exception as e:
            logger.debug(f"Error updating logs: {e}")
