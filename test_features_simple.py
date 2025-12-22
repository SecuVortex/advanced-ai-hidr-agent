"""Simple Feature Verification Test"""
import sys

def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    
    try:
        from gui.main_window import MainWindow
        print("  [OK] MainWindow")
    except Exception as e:
        print(f"  [FAIL] MainWindow: {e}")
        return False
    
    try:
        from gui.processes_view import ProcessesView
        print("  [OK] ProcessesView")
    except Exception as e:
        print(f"  [FAIL] ProcessesView: {e}")
        return False
    
    try:
        from gui.dashboard_view import DashboardView
        print("  [OK] DashboardView")
    except Exception as e:
        print(f"  [FAIL] DashboardView: {e}")
        return False
    
    try:
        from gui.quarantine_view import QuarantineView
        print("  [OK] QuarantineView")
    except Exception as e:
        print(f"  [FAIL] QuarantineView: {e}")
        return False
    
    try:
        from gui.settings_view import SettingsView
        print("  [OK] SettingsView")
    except Exception as e:
        print(f"  [FAIL] SettingsView: {e}")
        return False
    
    try:
        from gui.reports_view import ReportsView
        print("  [OK] ReportsView")
    except Exception as e:
        print(f"  [FAIL] ReportsView: {e}")
        return False
    
    try:
        from gui.agent_logs_view import AgentLogsView
        print("  [OK] AgentLogsView")
    except Exception as e:
        print(f"  [FAIL] AgentLogsView: {e}")
        return False
    
    try:
        from gui.about_view import AboutView
        print("  [OK] AboutView")
    except Exception as e:
        print(f"  [FAIL] AboutView: {e}")
        return False
    
    return True

def test_features():
    """Test feature implementations"""
    print("\nTesting feature implementations...")
    
    from gui.processes_view import ProcessesView
    
    all_methods = [m for m in dir(ProcessesView) if callable(getattr(ProcessesView, m))]
    required_methods = ['start_scan', 'stop_scan', 'export_results']
    
    for method in required_methods:
        if method in all_methods:
            print(f"  [OK] {method}")
        else:
            print(f"  [FAIL] {method} MISSING")
            return False
    
    feature_methods = ['_apply_filter', '_show_details', '_show_context_menu', 
                      '_reanalyze_process', '_add_to_whitelist', '_terminate_process']
    
    for method in feature_methods:
        if method in all_methods:
            print(f"  [OK] {method}")
        else:
            print(f"  [FAIL] {method} MISSING")
            return False
    
    return True

if __name__ == '__main__':
    print("="*70)
    print("HIDR FEATURE VERIFICATION TEST")
    print("="*70)
    
    test1 = test_imports()
    test2 = test_features()
    
    print("\n" + "="*70)
    if test1 and test2:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("="*70)
    
    sys.exit(0 if (test1 and test2) else 1)
