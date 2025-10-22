"""Check All Components Integration"""
import sys

print("=" * 60)
print("HIDR Multi-Agent System - Integration Check")
print("=" * 60)

errors = []
warnings = []
success = []

# 1. Check core modules
print("\n[1] Checking Core Modules...")
try:
    from agents.config import Config
    success.append("Config loaded")
    print(f"  [OK] Config - VT Key: {Config.VIRUSTOTAL_API_KEY[:20]}...")
except Exception as e:
    errors.append(f"Config failed: {e}")

try:
    from monitor import HIDRAgent
    success.append("HIDRAgent loaded")
    print("  [OK] HIDRAgent")
except Exception as e:
    errors.append(f"HIDRAgent failed: {e}")

# 2. Check multi-agent system
print("\n[2] Checking Multi-Agent System...")
try:
    from simple_multiagent import SimpleMultiAgent
    agent = SimpleMultiAgent()
    success.append("SimpleMultiAgent loaded")
    print("  [OK] SimpleMultiAgent")
except Exception as e:
    errors.append(f"SimpleMultiAgent failed: {e}")

# 3. Check tools
print("\n[3] Checking Tools...")
try:
    from tools.virustotal_tool import VirusTotalTool
    success.append("VirusTotal tool loaded")
    print("  [OK] VirusTotal Tool")
except Exception as e:
    errors.append(f"VirusTotal tool failed: {e}")

try:
    from tools.security_tools import calculate_file_hash
    success.append("Security tools loaded")
    print("  [OK] Security Tools")
except Exception as e:
    errors.append(f"Security tools failed: {e}")

try:
    from tools.behavior_monitor import BehaviorMonitor
    success.append("Behavior monitor loaded")
    print("  [OK] Behavior Monitor")
except Exception as e:
    errors.append(f"Behavior monitor failed: {e}")

# 4. Check GUI
print("\n[4] Checking GUI Components...")
try:
    from gui_monitor import HIDRGui
    success.append("Base GUI loaded")
    print("  [OK] Base GUI (HIDRGui)")
except Exception as e:
    errors.append(f"Base GUI failed: {e}")

try:
    from gui_multiagent import MultiAgentHIDRGui
    success.append("Multi-Agent GUI loaded")
    print("  [OK] Multi-Agent GUI")
except Exception as e:
    errors.append(f"Multi-Agent GUI failed: {e}")

# 5. Test integration
print("\n[5] Testing Integration...")
try:
    from simple_multiagent import SimpleMultiAgent
    orchestrator = SimpleMultiAgent()
    result = orchestrator.analyze_process("test.exe", "C:\\test\\test.exe", "", 1234)
    if len(result.get('messages', [])) >= 8:
        success.append("Multi-agent communication working")
        print(f"  [OK] Agent communication ({len(result['messages'])} messages)")
    else:
        warnings.append(f"Only {len(result['messages'])} messages generated")
except Exception as e:
    errors.append(f"Integration test failed: {e}")

# 6. Check dependencies
print("\n[6] Checking Dependencies...")
deps = ['psutil', 'watchdog', 'requests', 'langchain_openai']
for dep in deps:
    try:
        __import__(dep)
        print(f"  [OK] {dep}")
    except ImportError:
        warnings.append(f"Missing dependency: {dep}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"[OK] Success: {len(success)}")
print(f"[WARN] Warnings: {len(warnings)}")
print(f"[ERROR] Errors: {len(errors)}")

if errors:
    print("\n[ERRORS]")
    for err in errors:
        print(f"  - {err}")

if warnings:
    print("\n[WARNINGS]")
    for warn in warnings:
        print(f"  - {warn}")

print("\n" + "=" * 60)
if not errors:
    print("[SUCCESS] All components integrated properly!")
    print("\nRun the GUI:")
    print("  python run_multiagent_gui.py")
else:
    print("[FAILED] Fix errors above before running GUI")
print("=" * 60)
