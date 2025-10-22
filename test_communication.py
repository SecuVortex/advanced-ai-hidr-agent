"""Test agent communication"""
from simple_multiagent import SimpleMultiAgent

print("="*60)
print("TESTING AGENT COMMUNICATION")
print("="*60)

agent = SimpleMultiAgent()

print("\n" + "="*60)
print("TEST 1: Normal Process")
print("="*60)
result = agent.analyze_process("notepad.exe", "C:\\Windows\\System32\\notepad.exe", "", 1234)
print(f"\nFinal Action: {result['final_action']}")
print(f"Messages: {len(result['messages'])}")

print("\n" + "="*60)
print("TEST 2: Suspicious Process")
print("="*60)
result = agent.analyze_process("ransomware.exe", "C:\\Temp\\ransomware.exe", "", 5678)
print(f"\nFinal Action: {result['final_action']}")
print(f"Messages: {len(result['messages'])}")
print(f"AI Used: {result['analysis_result'].get('ai_used', 'Unknown')}")

print("\n" + "="*60)
print("COMMUNICATION LOG:")
print("="*60)
for msg in result['messages']:
    print(f"[{msg['from_agent']}] → [{msg['to_agent']}]: {msg['message']}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
