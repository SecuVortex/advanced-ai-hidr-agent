"""
Agent Logs Tab - Real-time agent activity logging
Phase 1, Task 1.4
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from datetime import datetime
import logging

logger = logging.getLogger('HIDR.AgentLogsTab')

class AgentLogsTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        self.log_count = 0
        logger.info("AgentLogsTab initialized")
    
    def _create_widgets(self):
        # Header
        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header, text="Agent Activity Logs", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Clear", command=self.clear_logs).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Export", command=self.export_logs).pack(side=tk.LEFT, padx=2)
        
        # Log display
        log_frame = ttk.Frame(self.frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for color coding
        self.log_text.tag_config('INFO', foreground='#4ec9b0')
        self.log_text.tag_config('WARNING', foreground='#ce9178')
        self.log_text.tag_config('ERROR', foreground='#f48771')
        self.log_text.tag_config('CRITICAL', foreground='#ff0000', font=('Consolas', 9, 'bold'))
        self.log_text.tag_config('timestamp', foreground='#858585')
        self.log_text.tag_config('agent', foreground='#dcdcaa')
    
    def add_log(self, agent: str, message: str, level: str = 'INFO'):
        """
        Add log entry
        
        Args:
            agent: Agent name (e.g., 'DetectionAgent')
            message: Log message
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.log_text.insert(tk.END, f"[{agent}] ", 'agent')
        self.log_text.insert(tk.END, f"{message}\n", level)
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)
        
        self.log_count += 1
        
        # Limit log size (keep last 1000 lines)
        if self.log_count > 1000:
            self.log_text.delete('1.0', '2.0')
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_text.delete('1.0', tk.END)
        self.log_count = 0
        self.add_log('System', 'Logs cleared', 'INFO')
    
    def export_logs(self):
        """Export logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"agent_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if filename:
                content = self.log_text.get('1.0', tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.add_log('System', f'Logs exported to {filename}', 'INFO')
        except Exception as e:
            logger.error(f"Export failed: {e}")
            self.add_log('System', f'Export failed: {e}', 'ERROR')
    
    def get_frame(self):
        """Get the tab frame"""
        return self.frame
