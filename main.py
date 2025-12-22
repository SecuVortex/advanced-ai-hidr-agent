"""HIDR - Hybrid Intelligent Detection & Response
Main application entry point with PyQt6
"""
import sys
import logging
from pathlib import Path

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
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from gui.main_window import MainWindow
        
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
        
    except ImportError as e:
        logger.error(f"PyQt6 not installed: {e}")
        print("\n" + "="*60)
        print("ERROR: PyQt6 is not installed")
        print("="*60)
        print("\nPlease install PyQt6:")
        print("  pip install PyQt6>=6.6.0")
        print("\nOr use the legacy Tkinter GUI:")
        print("  python production_gui.py")
        print("="*60 + "\n")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
