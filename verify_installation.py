"""
Installation Verification Script
Verifies that the Multi-Agent HIDR System is properly installed and configured.
"""

import sys
from pathlib import Path

def print_header(text):
    """Print section header"""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70)

def check_python_version():
    """Check Python version"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("\n📦 Checking dependencies...")
    
    required = [
        ("langgraph", "LangGraph"),
        ("langchain", "LangChain"),
        ("langchain_google_genai", "Gemini Integration"),
        ("psutil", "Process Tools"),
        ("requests", "HTTP Client"),
        ("dotenv", "Environment Config"),
    ]
    
    all_ok = True
    for module, name in required:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (Missing)")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """Check project structure"""
    print("\n📁 Checking project structure...")
    
    required_dirs = [
        "agents",
        "tools",
        "core",
        "examples",
        "tests",
        "docs"
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ (Missing)")
            all_ok = False
    
    return all_ok

def check_configuration():
    """Check configuration files"""
    print("\n⚙️  Checking configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    all_ok = True
    
    if env_example.exists():
        print("   ✅ .env.example (Template found)")
    else:
        print("   ❌ .env.example (Missing)")
        all_ok = False
    
    if env_file.exists():
        print("   ✅ .env (Configuration found)")
        
        # Check if API keys are set
        try:
            from agents.config import Config
            
            if Config.GOOGLE_API_KEY:
                print("   ✅ Gemini API key configured")
            else:
                print("   ⚠️  Gemini API key not set (AI analysis will be limited)")
            
            if Config.VIRUSTOTAL_API_KEY:
                print("   ✅ VirusTotal API key configured")
            else:
                print("   ⚠️  VirusTotal API key not set (Threat intelligence limited)")
        except Exception as e:
            print(f"   ⚠️  Could not verify API keys: {e}")
    else:
        print("   ⚠️  .env (Not found - copy from .env.example)")
        all_ok = False
    
    return all_ok

def check_agents():
    """Check agent implementations"""
    print("\n🤖 Checking agents...")
    
    try:
        from agents.detection_agent import DetectionAgent
        from agents.intelligence_agent import IntelligenceAgent
        from agents.response_agent import ResponseAgent
        from agents.analyst_agent import AnalystAgent
        from agents.coordinator_agent import CoordinatorAgent
        
        agents = [
            (DetectionAgent, "DetectionAgent"),
            (IntelligenceAgent, "IntelligenceAgent"),
            (ResponseAgent, "ResponseAgent"),
            (AnalystAgent, "AnalystAgent"),
            (CoordinatorAgent, "CoordinatorAgent")
        ]
        
        all_ok = True
        for agent_class, name in agents:
            try:
                agent = agent_class() if name != "ResponseAgent" else agent_class("./quarantine")
                print(f"   ✅ {name} - {agent.role}")
            except Exception as e:
                print(f"   ❌ {name} - Error: {e}")
                all_ok = False
        
        return all_ok
    except ImportError as e:
        print(f"   ❌ Failed to import agents: {e}")
        return False

def check_tools():
    """Check tool implementations"""
    print("\n🛠️  Checking tools...")
    
    try:
        from tools.security_tools import SecurityTools
        from tools.file_tools import FileTools
        from tools.process_tools import ProcessTools
        from tools.virustotal_tool import VirusTotalTool
        from tools.llm_tools import LLMTools
        
        tools = [
            (SecurityTools, "SecurityTools"),
            (FileTools, "FileTools"),
            (ProcessTools, "ProcessTools"),
            (VirusTotalTool, "VirusTotalTool"),
            (LLMTools, "LLMTools")
        ]
        
        all_ok = True
        for tool_class, name in tools:
            try:
                tool = tool_class()
                print(f"   ✅ {name}")
            except Exception as e:
                print(f"   ❌ {name} - Error: {e}")
                all_ok = False
        
        return all_ok
    except ImportError as e:
        print(f"   ❌ Failed to import tools: {e}")
        return False

def check_orchestrator():
    """Check orchestrator"""
    print("\n🔄 Checking orchestrator...")
    
    try:
        from agents.orchestrator import MultiAgentOrchestrator
        
        orchestrator = MultiAgentOrchestrator(
            quarantine_dir="./test_quarantine",
            require_human_approval=False
        )
        
        print("   ✅ MultiAgentOrchestrator initialized")
        print(f"   ✅ Workflow compiled successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Orchestrator error: {e}")
        return False

def run_quick_test():
    """Run a quick functionality test"""
    print("\n🧪 Running quick functionality test...")
    
    try:
        from core.multiagent_monitor import MultiAgentHIDR
        
        # Initialize system (without human approval for testing)
        hidr = MultiAgentHIDR(require_human_approval=False)
        
        print("   ✅ System initialized successfully")
        
        # Test with a benign process
        print("   🔍 Testing process analysis...")
        result = hidr.analyze_process(
            "test.exe",
            "C:\\Windows\\System32\\test.exe",
            "test.exe",
            9999
        )
        
        if result and "final_action" in result:
            print(f"   ✅ Process analysis completed")
            print(f"      Action: {result['final_action']}")
            print(f"      Threat Level: {result['detection_result'].get('threat_level', 0)}/10")
            return True
        else:
            print("   ❌ Process analysis failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print_header("🔍 MULTI-AGENT HIDR SYSTEM - INSTALLATION VERIFICATION")
    
    print("\nThis script will verify that your Multi-Agent HIDR System")
    print("is properly installed and configured.\n")
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Project Structure", check_project_structure()))
    results.append(("Configuration", check_configuration()))
    results.append(("Agents", check_agents()))
    results.append(("Tools", check_tools()))
    results.append(("Orchestrator", check_orchestrator()))
    results.append(("Functionality Test", run_quick_test()))
    
    # Print summary
    print_header("📊 VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {name}")
    
    # Final verdict
    print_header("🎯 FINAL VERDICT")
    
    if passed == total:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nYour Multi-Agent HIDR System is properly installed and ready to use!")
        print("\nNext steps:")
        print("   1. Run: python examples\\demo_basic.py")
        print("   2. Read: README_MULTIAGENT.md")
        print("   3. Try: python examples\\demo_human_loop.py")
    elif passed >= total * 0.7:
        print("\n⚠️  MOSTLY WORKING")
        print("\nYour system is mostly functional but has some issues.")
        print("Review the failed checks above and fix them.")
        print("\nYou can still try running:")
        print("   python examples\\demo_basic.py")
    else:
        print("\n❌ INSTALLATION INCOMPLETE")
        print("\nSeveral components are missing or not working.")
        print("\nPlease:")
        print("   1. Install dependencies: pip install -r requirements_multiagent.txt")
        print("   2. Configure API keys: copy .env.example .env")
        print("   3. Run this script again")
    
    print("\n" + "="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
