"""HIDR - Hybrid Intelligent Detection & Response
Main application entry point with PyQt6 GUI
"""
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'hidr_ui.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('HIDR.Main')

def main():
    """Main application entry point"""
    try:
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication(sys.argv)
        app.setApplicationName("HIDR")
        app.setOrganizationName("SecuVortex")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("HIDR application started")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
