"""Settings View - Configuration management"""
import logging
import yaml
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QSpinBox, QGroupBox,
                              QFormLayout, QMessageBox, QListWidget, QFileDialog)
from PyQt6.QtCore import Qt

logger = logging.getLogger('HIDR.SettingsView')

class SettingsView(QWidget):
    """Settings configuration view"""
    def __init__(self):
        super().__init__()
        self.config_file = Path('config.yaml')
        self.config = self._load_config()
        self._create_ui()
        logger.info("Settings view initialized")
    
    def _load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            QMessageBox.information(self, "Success", "Settings saved successfully")
            logger.info("Configuration saved")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
            logger.error(f"Failed to save config: {e}")
    
    def _create_ui(self):
        """Create UI layout"""
        layout = QVBoxLayout()
        
        # Detection settings
        detection_group = QGroupBox("Detection Settings")
        detection_layout = QFormLayout()
        
        self.threat_threshold = QSpinBox()
        self.threat_threshold.setRange(0, 10)
        self.threat_threshold.setValue(self.config.get('detection', {}).get('threat_threshold', 5))
        detection_layout.addRow("Threat Threshold:", self.threat_threshold)
        
        self.terminate_threshold = QSpinBox()
        self.terminate_threshold.setRange(0, 10)
        self.terminate_threshold.setValue(self.config.get('detection', {}).get('terminate_threshold', 8))
        detection_layout.addRow("Terminate Threshold:", self.terminate_threshold)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Trusted paths
        paths_group = QGroupBox("Trusted Paths")
        paths_layout = QVBoxLayout()
        
        self.paths_list = QListWidget()
        trusted_paths = self.config.get('paths', {}).get('trusted_paths', [])
        for path in trusted_paths:
            self.paths_list.addItem(path)
        paths_layout.addWidget(self.paths_list)
        
        paths_btn_layout = QHBoxLayout()
        add_path_btn = QPushButton("Add Path")
        add_path_btn.clicked.connect(self._add_path)
        paths_btn_layout.addWidget(add_path_btn)
        
        remove_path_btn = QPushButton("Remove Selected")
        remove_path_btn.clicked.connect(self._remove_path)
        paths_btn_layout.addWidget(remove_path_btn)
        
        paths_layout.addLayout(paths_btn_layout)
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _add_path(self):
        """Add trusted path"""
        path = QFileDialog.getExistingDirectory(self, "Select Trusted Directory")
        if path:
            self.paths_list.addItem(path)
    
    def _remove_path(self):
        """Remove selected path"""
        current = self.paths_list.currentRow()
        if current >= 0:
            self.paths_list.takeItem(current)
    
    def _save_settings(self):
        """Save all settings"""
        # Update config
        if 'detection' not in self.config:
            self.config['detection'] = {}
        
        self.config['detection']['threat_threshold'] = self.threat_threshold.value()
        self.config['detection']['terminate_threshold'] = self.terminate_threshold.value()
        
        # Update paths
        if 'paths' not in self.config:
            self.config['paths'] = {}
        
        paths = []
        for i in range(self.paths_list.count()):
            paths.append(self.paths_list.item(i).text())
        
        self.config['paths']['trusted_paths'] = paths
        
        # Save
        self._save_config()
