"""Comprehensive GUI Feature Test Script"""
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow

def test_all_features():
    """Test all GUI features"""
    print("="*70)
    print("HIDR GUI FEATURE TEST")
    print("="*70)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    results = {}
    
    # Test 1: Window loads
    print("\n[TEST 1] Window Loading...")
    results['window_load'] = window.isVisible()
    print(f"  Result: {'✓ PASS' if results['window_load'] else '✗ FAIL'}")
    
    # Test 2: All tabs present
    print("\n[TEST 2] Tab Count...")
    tab_count = window.tabs.count()
    results['tab_count'] = (tab_count == 7)
    print(f"  Expected: 7 tabs")
    print(f"  Found: {tab_count} tabs")
    print(f"  Result: {'✓ PASS' if results['tab_count'] else '✗ FAIL'}")
    
    # Test 3: Tab names
    print("\n[TEST 3] Tab Names...")
    expected_tabs = ["🔍 Processes", "🔒 Quarantine", "📊 Reports", 
                     "📈 Dashboard", "📋 Agent Logs", "⚙ Settings", "ℹ About"]
    actual_tabs = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    results['tab_names'] = (actual_tabs == expected_tabs)
    print(f"  Expected: {expected_tabs}")
    print(f"  Found: {actual_tabs}")
    print(f"  Result: {'✓ PASS' if results['tab_names'] else '✗ FAIL'}")
    
    # Test 4: Processes view components
    print("\n[TEST 4] Processes View Components...")
    processes_view = window.processes_view
    has_filter = hasattr(processes_view, 'filter_input')
    has_start_btn = hasattr(processes_view, 'start_btn')
    has_stop_btn = hasattr(processes_view, 'stop_btn')
    has_table = hasattr(processes_view, 'table')
    has_stats = hasattr(processes_view, 'stats_label')
    
    results['processes_components'] = all([has_filter, has_start_btn, has_stop_btn, has_table, has_stats])
    print(f"  Filter: {'✓' if has_filter else '✗'}")
    print(f"  Start Button: {'✓' if has_start_btn else '✗'}")
    print(f"  Stop Button: {'✓' if has_stop_btn else '✗'}")
    print(f"  Table: {'✓' if has_table else '✗'}")
    print(f"  Stats: {'✓' if has_stats else '✗'}")
    print(f"  Result: {'✓ PASS' if results['processes_components'] else '✗ FAIL'}")
    
    # Test 5: Start button functionality
    print("\n[TEST 5] Start Button State...")
    initial_enabled = processes_view.start_btn.isEnabled()
    initial_text = processes_view.start_btn.text()
    results['start_button'] = (initial_enabled and initial_text == "⚡ Start Scan")
    print(f"  Enabled: {initial_enabled}")
    print(f"  Text: {initial_text}")
    print(f"  Result: {'✓ PASS' if results['start_button'] else '✗ FAIL'}")
    
    # Test 6: Dashboard components
    print("\n[TEST 6] Dashboard Components...")
    dashboard = window.dashboard_view
    has_cards = hasattr(dashboard, 'total_scans_card')
    results['dashboard_components'] = has_cards
    print(f"  Stat Cards: {'✓' if has_cards else '✗'}")
    print(f"  Result: {'✓ PASS' if results['dashboard_components'] else '✗ FAIL'}")
    
    # Test 7: Reports view
    print("\n[TEST 7] Reports View...")
    reports = window.reports_view
    has_stats_text = hasattr(reports, 'stats_text')
    has_threats_text = hasattr(reports, 'threats_text')
    results['reports_view'] = (has_stats_text and has_threats_text)
    print(f"  Stats Display: {'✓' if has_stats_text else '✗'}")
    print(f"  Threats Display: {'✓' if has_threats_text else '✗'}")
    print(f"  Result: {'✓ PASS' if results['reports_view'] else '✗ FAIL'}")
    
    # Test 8: Quarantine view
    print("\n[TEST 8] Quarantine View...")
    quarantine = window.quarantine_view
    has_table = hasattr(quarantine, 'table')
    results['quarantine_view'] = has_table
    print(f"  Table: {'✓' if has_table else '✗'}")
    print(f"  Result: {'✓ PASS' if results['quarantine_view'] else '✗ FAIL'}")
    
    # Test 9: Settings view
    print("\n[TEST 9] Settings View...")
    settings = window.settings_view
    has_threshold = hasattr(settings, 'threat_threshold')
    has_paths = hasattr(settings, 'paths_list')
    results['settings_view'] = (has_threshold and has_paths)
    print(f"  Threshold Control: {'✓' if has_threshold else '✗'}")
    print(f"  Paths List: {'✓' if has_paths else '✗'}")
    print(f"  Result: {'✓ PASS' if results['settings_view'] else '✗ FAIL'}")
    
    # Test 10: Agent Logs view
    print("\n[TEST 10] Agent Logs View...")
    agent_logs = window.agent_logs_view
    has_logs_text = hasattr(agent_logs, 'logs_text')
    results['agent_logs_view'] = has_logs_text
    print(f"  Logs Display: {'✓' if has_logs_text else '✗'}")
    print(f"  Result: {'✓ PASS' if results['agent_logs_view'] else '✗ FAIL'}")
    
    # Test 11: About view
    print("\n[TEST 11] About View...")
    about = window.about_view
    results['about_view'] = (about is not None)
    print(f"  View Exists: {'✓' if about else '✗'}")
    print(f"  Result: {'✓ PASS' if results['about_view'] else '✗ FAIL'}")
    
    # Test 12: Theme toggle
    print("\n[TEST 12] Theme Toggle...")
    initial_theme = window._current_theme
    window._toggle_theme()
    new_theme = window._current_theme
    results['theme_toggle'] = (initial_theme != new_theme)
    print(f"  Initial: {initial_theme}")
    print(f"  After Toggle: {new_theme}")
    print(f"  Result: {'✓ PASS' if results['theme_toggle'] else '✗ FAIL'}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print("="*70)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test}: {status}")
    
    print("\n" + "="*70)
    if passed == total:
        print("ALL TESTS PASSED ✓")
    else:
        print(f"SOME TESTS FAILED ({total-passed} failures)")
    print("="*70)
    
    # Keep window open for manual inspection
    print("\nWindow will remain open for manual testing...")
    print("Press Ctrl+C to exit")
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(test_all_features())
