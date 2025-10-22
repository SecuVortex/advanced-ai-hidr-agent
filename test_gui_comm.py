"""Test GUI Communication"""
import sys
import time

# Test if simple_multiagent works
try:
    from simple_multiagent import SimpleMultiAgent
    
    print("Testing SimpleMultiAgent...")
    agent = SimpleMultiAgent()
    
    # Test with suspicious process
    result = agent.analyze_process(
        proc_name="suspicious.exe",
        path="C:\\Users\\Test\\Downloads\\suspicious.exe",
        cmdline="suspicious.exe --encrypt",
        pid=1234
    )
    
    print(f"\n=== RESULT ===")
    print(f"Messages: {len(result['messages'])}")
    print(f"Action: {result['final_action']}")
    print(f"\n=== MESSAGES ===")
    for msg in result['messages']:
        print(f"[{msg['from_agent']}] -> [{msg['to_agent']}]: {msg['message']}")
    
    print("\n✓ SimpleMultiAgent working!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
