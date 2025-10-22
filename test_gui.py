"""
Quick GUI Test Script
Tests both standard and multi-agent GUI functionality
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required imports work"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter available")
    except ImportError:
        print("✗ tkinter not available")
        return False
    
    try:
        from gui_monitor import HIDRGui
        print("✓ Standard GUI available")
    except ImportError as e:
        print(f"✗ Standard GUI import failed: {e}")
        return False
    
    try:
        from gui_multiagent import MultiAgentHIDRGui, MULTIAGENT_AVAILABLE
        print(f"✓ Multi-agent GUI available (multiagent: {MULTIAGENT_AVAILABLE})")
    except ImportError as e:
        print(f"✗ Multi-agent GUI import failed: {e}")
        return False
    
    return True

def test_standard_gui():
    """Test standard GUI initialization"""
    print("\nTesting standard GUI...")
    
    try:
        from gui_monitor import HIDRGui
        app = HIDRGui()
        print("✓ Standard GUI initialized successfully")
        app.root.destroy()
        return True
    except Exception as e:
        print(f"✗ Standard GUI initialization failed: {e}")
        return False

def test_multiagent_gui():
    """Test multi-agent GUI initialization"""
    print("\nTesting multi-agent GUI...")
    
    try:
        from gui_multiagent import MultiAgentHIDRGui, MULTIAGENT_AVAILABLE
        
        if not MULTIAGENT_AVAILABLE:
            print("⚠️  Multi-agent features not available (missing dependencies)")
            print("   Install with: pip install -r requirements_multiagent.txt")
            return True  # Not a failure, just not available
        
        app = MultiAgentHIDRGui()
        print("✓ Multi-agent GUI initialized successfully")
        
        # Check if multi-agent tab exists
        if hasattr(app, 'multiagent_frame'):
            print("✓ Multi-agent tab created")
        else:
            print("⚠️  Multi-agent tab not found")
        
        app.root.destroy()
        return True
    except Exception as e:
        print(f"✗ Multi-agent GUI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_config():
    """Test API configuration"""
    print("\nTesting API configuration...")
    
    try:
        from agents.config import Config
        
        print(f"  VirusTotal API: {'✓ Configured' if Config.VIRUSTOTAL_API_KEY and Config.VIRUSTOTAL_API_KEY != 'your_virustotal_api_key_here' else '✗ Not configured'}")
        print(f"  Gemini API: {'✓ Configured' if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_google_api_key_here' else '✗ Not configured'}")
        print(f"  LLM Provider: {Config.LLM_PROVIDER}")
        
        return True
    except Exception as e:
        print(f"✗ API configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("HIDR GUI Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test standard GUI
    results.append(("Standard GUI", test_standard_gui()))
    
    # Test multi-agent GUI
    results.append(("Multi-agent GUI", test_multiagent_gui()))
    
    # Test API config
    results.append(("API Configuration", test_api_config()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nYou can now run:")
        print("  python run_multiagent_gui.py  (for multi-agent GUI)")
        print("  python gui_monitor.py         (for standard GUI)")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the GUI")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
