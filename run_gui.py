#!/usr/bin/env python3

import sys
from pathlib import Path

def main():
    print("=== HIDR Agent - Host Intrusion Detection & Response ===")
    print("Starting GUI application...")
    
    try:
        from gui_monitor import HIDRGui
        
        print("Dependencies loaded successfully")
        print("Launching HIDR Agent GUI...")
        
        app = HIDRGui()
        app.run()
        
    except ImportError as e:
        print(f"Missing dependencies: {e}")
        print("\nPlease install required packages:")
        print("pip install -r requirements_gui.txt")
        print("\nOr install individually:")
        print("pip install wmi psutil watchdog win10toast matplotlib pandas plotly")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()