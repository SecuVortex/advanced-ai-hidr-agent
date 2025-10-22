import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.multiagent_monitor import MultiAgentHIDR


def print_section(title: str):
    print('\n' + f' {title} '.center(70, '='))


def main():
    print_section('COMPLETE DEMO: Multi-Agent HIDR System')
    hidr = MultiAgentHIDR(require_human_approval=True)
    print_section('TEST 1: SUSPICIOUS POWERSHELL COMMAND (HUMAN APPROVAL)')
    result = hidr.analyze_process('powershell.exe',
        'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
        'powershell -e JABzAD0ATgBlAHcALQBPA...', 4321)
    hidr.print_summary(result)
    hidr.print_agent_communication(result)
    print_section('DEMO COMPLETE')


if __name__ == '__main__':
    main()
