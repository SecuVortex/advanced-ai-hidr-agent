import sys
from pathlib import Path


def print_header(text):
    print('\n' + f' {text} '.center(70, '='))


def check_python_version():
    print('\n🐍 Checking Python version...')
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(
            f'   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)'
            )
        return True
    else:
        print(
            f'   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)'
            )
        return False


def check_project_structure():
    print('\n📁 Checking project structure...')
    required_dirs = ['agents', 'tools', 'core', 'examples', 'tests']
    all_ok = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f'   ✅ {dir_name}/')
        else:
            print(f'   ❌ {dir_name}/ (Missing)')
            all_ok = False
    return all_ok


def check_dependencies():
    print('\n📦 Checking core dependencies...')
    try:
        import langgraph
        print('   ✅ langgraph')
        import langchain_core
        print('   ✅ langchain_core')
        import langchain_google_genai
        print('   ✅ langchain_google_genai')
        import dotenv
        print('   ✅ python-dotenv')
        import psutil
        print('   ✅ psutil')
        import requests
        print('   ✅ requests')
        return True
    except ImportError as e:
        print(f'   ❌ Missing dependency: {e.name}')
        return False


def check_configuration():
    print('\n🔑 Checking API configuration...')
    try:
        from agents.config import Config
        print(
            f"  VirusTotal API: {'✓ Configured' if Config.VIRUSTOTAL_API_KEY and Config.VIRUSTOTAL_API_KEY != 'your_virustotal_api_key_here' else '✗ Not configured'}"
            )
        print(
            f"  Gemini API: {'✓ Configured' if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_google_api_key_here' else '✗ Not configured'}"
            )
        print(f'  LLM Provider: {Config.LLM_PROVIDER}')
        return True
    except Exception as e:
        print(f'✗ API configuration test failed: {e}')
        return False


def check_agents():
    print('\n🤖 Checking agents...')
    try:
        from agents.detection_agent import DetectionAgent
        from agents.intelligence_agent import IntelligenceAgent
        from agents.response_agent import ResponseAgent
        from agents.analyst_agent import AnalystAgent
        from agents.coordinator_agent import CoordinatorAgent
        agents = [(DetectionAgent, 'DetectionAgent'), (IntelligenceAgent,
            'IntelligenceAgent'), (ResponseAgent, 'ResponseAgent'), (
            AnalystAgent, 'AnalystAgent'), (CoordinatorAgent,
            'CoordinatorAgent')]
        all_ok = True
        for agent_class, name in agents:
            try:
                agent = agent_class(
                    ) if name != 'ResponseAgent' else agent_class(
                    './quarantine')
                print(f'   ✅ {name} - {agent.role}')
            except Exception as e:
                print(f'   ❌ {name} - Error: {e}')
                all_ok = False
        return all_ok
    except ImportError as e:
        print(f'   ❌ Failed to import agents: {e}')
        return False


def check_orchestrator():
    print('\n🔄 Checking orchestrator...')
    try:
        from agents.orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator(quarantine_dir=
            './test_quarantine', require_human_approval=False)
        print('   ✅ MultiAgentOrchestrator initialized')
        print(f'   ✅ Workflow compiled successfully')
        return True
    except Exception as e:
        print(f'   ❌ Orchestrator error: {e}')
        return False


def run_quick_test():
    print('\n⚡ Running quick functionality test...')
    try:
        from core.multiagent_monitor import MultiAgentHIDR
        hidr = MultiAgentHIDR(require_human_approval=False)
        result = hidr.analyze_process('test.exe', 'C:\\test.exe', '', 1234)
        if result and 'final_action' in result:
            print('   ✅ Quick test completed successfully')
            return True
        else:
            print('   ❌ Quick test failed to produce a result')
            return False
    except Exception as e:
        print(f'   ❌ Quick test failed: {e}')
        return False


def main():
    print_header('🔍 MULTI-AGENT HIDR SYSTEM - INSTALLATION VERIFICATION')
    print('\nThis script will verify that your Multi-Agent HIDR System')
    print('is properly installed and configured.\n')
    results = []
    results.append(('Python Version', check_python_version()))
    results.append(('Dependencies', check_dependencies()))
    results.append(('Project Structure', check_project_structure()))
    results.append(('Configuration', check_configuration()))
    results.append(('Agents', check_agents()))
    results.append(('Orchestrator', check_orchestrator()))
    results.append(('Functionality Test', run_quick_test()))
    print_header('📊 VERIFICATION SUMMARY')
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f'\nTests Passed: {passed}/{total}')
    print('\nDetailed Results:')
    for name, result in results:
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'   {status} - {name}')
    print_header('🎯 FINAL VERDICT')
    if passed == total:
        print('\n✅ ALL CHECKS PASSED!')
        print(
            '\nYour Multi-Agent HIDR System is properly installed and ready to use!'
            )
        print('\nNext steps:')
        print('   1. Run: python examples/demo_basic.py')
        print('   2. Try: python examples/demo_human_loop.py')
    elif passed >= total * 0.7:
        print('\n⚠️  MOSTLY WORKING')
        print('\nYour system is mostly functional but has some issues.')
        print('Review the failed checks above and fix them.')
        print('\nYou can still try running:')
        print('   python examples/demo_basic.py')
    else:
        print('\n❌ INSTALLATION INCOMPLETE')
        print('\nSeveral components are missing or not working.')
        print('\nPlease:')
        print(
            '   1. Install dependencies: pip install -r requirements_multiagent.txt'
            )
        print('   2. Configure API keys: copy .env.example .env')
        print('   3. Run this script again')
    print('\n' + '=' * 70 + '\n')
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
