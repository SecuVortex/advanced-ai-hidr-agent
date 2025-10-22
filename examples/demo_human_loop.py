import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.multiagent_monitor import MultiAgentHIDR


def main():
    print('\n' + '=' * 70)
    print('🧪 HUMAN-IN-THE-LOOP DEMO')
    print('=' * 70)
    print('\nThis demo shows intelligent human approval:')
    print('  ✓ AI explains threats in plain English')
    print('  ✓ Human makes informed decisions')
    print('  ✓ 4 options: Allow, Terminate Temp, Terminate Permanent, Monitor')
    print('=' * 70 + '\n')
    hidr = MultiAgentHIDR(require_human_approval=True)
    print('\n' + 'TEST 1: SUSPICIOUS PROCESS FROM TEMP'.center(70, '='))
    print('A process with suspicious characteristics has been detected.')
    print('The AI will analyze it and ask for your decision.\n')
    result1 = hidr.analyze_process('suspicious.exe',
        'C:\\Users\\test\\AppData\\Local\\Temp\\suspicious.exe',
        'suspicious.exe --payload --encrypt', 5555)
    print('\n📊 RESULT:')
    print(f"   Your Decision: {result1['human_decision'].get('reason')}")
    print(f"   Action Taken: {result1['final_action']}")
    print(f"   Success: {result1['response_result'].get('success')}")
    print('\n\n' + 'TEST 2: RANSOMWARE DETECTION'.center(70, '='))
    print('A process with ransomware characteristics has been detected.')
    print('The AI will provide detailed analysis.\n')
    result2 = hidr.analyze_process('encryptor.exe',
        'C:\\Users\\test\\Downloads\\encryptor.exe',
        'encryptor.exe --target C:\\Users --key abc123', 7777)
    print('\n📊 RESULT:')
    print(f"   Your Decision: {result2['human_decision'].get('reason')}")
    print(f"   Action Taken: {result2['final_action']}")
    print(f"   Success: {result2['response_result'].get('success')}")
    hidr.print_agent_communication(result2)
    print('\n📊 SESSION STATISTICS:')
    stats = hidr.get_statistics()
    print(f"   Total Decisions: {stats.get('total_workflows', 0)}")
    print(f"   Priority Distribution: {stats.get('priority_distribution', {})}"
        )
    print(f"   Action Distribution: {stats.get('action_distribution', {})}")
    print('\n✅ DEMO COMPLETE')
    print('\nKey Features Demonstrated:')
    print('  ✓ Multi-agent collaboration (5 agents)')
    print('  ✓ AI-powered threat analysis (Gemini)')
    print('  ✓ VirusTotal integration')
    print('  ✓ Human-in-the-loop decision making')
    print('  ✓ LangGraph orchestration')
    print('  ✓ Agent-to-agent communication\n')


if __name__ == '__main__':
    main()
