"""Launch Multi-Agent GUI with Debug Info"""
import sys

print("=" * 60)
print("HIDR Multi-Agent System - Starting...")
print("=" * 60)

try:
    from gui_multiagent import MultiAgentHIDRGui
    print("[OK] GUI module loaded")
    
    print("\nInstructions:")
    print("1. Click 'Start Protection'")
    print("2. Open Notepad or Calculator to see agent communication")
    print("3. Check 'AI Agents' tab for live messages")
    print("\n" + "=" * 60)
    
    app = MultiAgentHIDRGui()
    app.run()
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
