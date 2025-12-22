"""Quarantine View - Manage quarantined files"""
import logging
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QMessageBox, QLabel)
from PyQt6.QtCore import Qt

logger = logging.getLogger('HIDR.QuarantineView')

class QuarantineView(QWidget):
    """Quarantine management view"""
    def __init__(self):
        super().__init__()
        self.quarantine_dir = Path('quarantine')
        self._create_ui()
        self.refresh()
        logger.info("Quarantine view initialized")
    
    def _create_ui(self):
        """Create UI layout"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Quarantined Files")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["File", "Original Path", "Threat", "Date", "Actions"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("🗑 Delete Selected")
        delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh quarantine list"""
        self.table.setRowCount(0)
        
        if not self.quarantine_dir.exists():
            return
        
        for file in self.quarantine_dir.glob('*'):
            if file.suffix == '.json':
                continue
            
            # Load metadata
            metadata_file = file.with_suffix(file.suffix + '.json')
            metadata = {}
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            # Add row
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(file.name))
            self.table.setItem(row, 1, QTableWidgetItem(metadata.get('original_path', 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(str(metadata.get('threat_level', 'N/A'))))
            self.table.setItem(row, 3, QTableWidgetItem(metadata.get('timestamp', 'N/A')))
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, f=file: self._delete_file(f))
            self.table.setCellWidget(row, 4, delete_btn)
        
        logger.info(f"Loaded {self.table.rowCount()} quarantined files")
    
    def _delete_selected(self):
        """Delete selected files"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select files to delete")
            return
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f'Delete {len(selected)} selected file(s)?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected:
                row = item.row()
                filename = self.table.item(row, 0).text()
                file_path = self.quarantine_dir / filename
                self._delete_file(file_path)
            
            self.refresh()
    
    def _delete_file(self, file_path):
        """Delete quarantined file"""
        try:
            if file_path.exists():
                file_path.unlink()
            
            metadata_file = file_path.with_suffix(file_path.suffix + '.json')
            if metadata_file.exists():
                metadata_file.unlink()
            
            logger.info(f"Deleted quarantined file: {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")
