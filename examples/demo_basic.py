import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.multiagent_monitor import MultiAgentHIDR


def main():
    print('\n' + '=' * 70)
    print('🧪 BASIC DEMO: Multi-Agent Threat Detection')
    print('=' * 70)
    print('\nThis demo shows automated threat detection and response')
    print('without human approval (for testing purposes).\n')
    hidr = MultiAgentHIDR(require_human_approval=False)
    print('\n' + 'TEST 1: RANSOMWARE DETECTION'.center(70, '='))
    result1 = hidr.analyze_process('ransomware.exe',
        'C:\\Users\\test\\AppData\\Local\\Temp\\ransomware.exe',
        'ransomware.exe --encrypt-all --target C:\\Users', 9999)
    hidr.print_summary(result1)
    print('\n\n' + 'TEST 2: LEGITIMATE PROCESS'.center(70, '='))
    result2 = hidr.analyze_process('notepad.exe',
        'C:\\Windows\\System32\\notepad.exe', 'notepad.exe document.txt', 1234)
    hidr.print_summary(result2)
    print('\n\n' + 'TEST 3: SUSPICIOUS DOWNLOAD'.center(70, '='))
    result3 = hidr.analyze_process('setup.exe',
        'C:\\Users\\test\\Downloads\\setup.exe',
        'setup.exe /silent /install', 5678)
    hidr.print_summary(result3)
    print('\n')
    hidr.print_agent_communication(result3)
    print('\n📊 SYSTEM STATISTICS:')
    stats = hidr.get_statistics()
    print(f"   Total Workflows: {stats.get('total_workflows', 0)}")
    print(f"   Priority Distribution: {stats.get('priority_distribution', {})}"
        )
    print('\n✅ DEMO COMPLETE\n')


if __name__ == '__main__':
    main()
