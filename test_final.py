"""Final Test - Multi-Agent with Safety Checks"""
import sys

print("=" * 60)
print("Multi-Agent System - Final Test")
print("=" * 60)

try:
    from simple_multiagent import SimpleMultiAgent
    
    print("\n[1] Initializing agents...")
    agent = SimpleMultiAgent()
    
    print("\n[2] Testing with suspicious process...")
    result = agent.analyze_process(
        proc_name="suspicious.exe",
        path="C:\\Users\\Test\\Downloads\\suspicious.exe",
        cmdline="suspicious.exe --encrypt",
        pid=1234
    )
    
    print(f"\n{'=' * 60}")
    print("RESULTS")
    print("=" * 60)
    print(f"Messages Generated: {len(result['messages'])}")
    print(f"Threat Level: {result['detection_result']['threat_level']}/10")
    print(f"AI Used: {result['analysis_result']['ai_used']}")
    print(f"Severity: {result['analysis_result']['severity']}")
    print(f"Action: {result['final_action']}")
    
    print(f"\n{'=' * 60}")
    print("AGENT COMMUNICATION")
    print("=" * 60)
    for msg in result['messages']:
        print(f"[{msg['from_agent']}] -> [{msg['to_agent']}]: {msg['message']}")
    
    print(f"\n{'=' * 60}")
    if len(result['messages']) >= 8:
        print("[SUCCESS] Multi-agent communication working!")
    else:
        print("[WARNING] Expected 8+ messages, got", len(result['messages']))
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
