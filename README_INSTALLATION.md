# 🚀 Installation Guide - Multi-Agent HIDR System

Complete installation guide for the Multi-Agent HIDR System v2.0

---

## 📋 Prerequisites

### System Requirements

- **Operating System:** Windows 10/11 (64-bit)
- **Python:** 3.8 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 500MB free space
- **Privileges:** Administrator rights (for process termination)

### API Keys Required

1. **VirusTotal API Key** (Free)
   - Sign up at: https://www.virustotal.com/gui/join-us
   - Get API key: https://www.virustotal.com/gui/my-apikey

2. **Google Gemini API Key** (Free)
   - Sign up at: https://makersuite.google.com/
   - Get API key: https://makersuite.google.com/app/apikey

3. **Optional:** OpenAI or Mistral API keys

---

## 🔧 Installation Steps

### Step 1: Verify Python Installation

```bash
python --version
```

Should show Python 3.8 or higher. If not, download from: https://www.python.org/downloads/

### Step 2: Navigate to Project Directory

```bash
cd "l:\Personal\MY LEARNING\MY PROJECTS\advanced hidr-agent system"
```

### Step 3: Install Dependencies

```bash
pip install -r requirements_multiagent.txt
```

This will install:
- LangGraph & LangChain (multi-agent framework)
- Gemini/OpenAI/Mistral integrations
- Security tools (psutil, watchdog, etc.)
- API clients (requests, python-dotenv)

**Installation time:** ~2-3 minutes

### Step 4: Configure API Keys

1. **Copy environment template:**
   ```bash
   copy .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   notepad .env
   ```

3. **Add your API keys:**
   ```env
   VIRUSTOTAL_API_KEY=your_virustotal_key_here
   GOOGLE_API_KEY=your_gemini_key_here
   LLM_PROVIDER=gemini
   REQUIRE_HUMAN_APPROVAL=true
   ```

4. **Save and close**

### Step 5: Verify Installation

```bash
python verify_installation.py
```

This will check:
- ✅ Python version
- ✅ Dependencies installed
- ✅ Project structure
- ✅ Configuration files
- ✅ Agents functional
- ✅ Tools working
- ✅ Orchestrator operational

**Expected output:**
```
✅ ALL CHECKS PASSED!
Your Multi-Agent HIDR System is properly installed and ready to use!
```

---

## 🧪 Test Installation

### Quick Test (No Human Approval)

```bash
python examples\demo_basic.py
```

**What it does:**
- Tests all 5 agents
- Analyzes 3 different scenarios
- Shows agent communication
- Displays results

**Expected output:**
```
🤖 MULTI-AGENT HIDR SYSTEM v2.0
✓ Threat Detection Specialist
✓ Threat Intelligence Specialist
✓ Incident Response Specialist
✓ Security Analyst (AI-Powered)
✓ Multi-Agent Coordinator

TEST 1: RANSOMWARE DETECTION
🔍 [DetectionAgent] Analyzing process...
🌐 [IntelligenceAgent] Querying threat databases...
🤖 [AnalystAgent] Generating AI analysis...
...
✅ WORKFLOW COMPLETE
```

### Interactive Test (With Human Approval)

```bash
python examples\demo_human_loop.py
```

**What it does:**
- Enables human-in-the-loop
- Shows AI explanations
- Asks for your decisions
- Demonstrates full workflow

---

## 🔍 Troubleshooting

### Issue: "No module named 'langgraph'"

**Solution:**
```bash
pip install -r requirements_multiagent.txt
```

### Issue: "API key not configured"

**Solution:**
1. Check `.env` file exists
2. Verify API keys are correct
3. No extra spaces or quotes

```bash
# Correct:
GOOGLE_API_KEY=AIzaSyD...

# Wrong:
GOOGLE_API_KEY = "AIzaSyD..."
```

### Issue: "Permission denied" when terminating processes

**Solution:**
Run as Administrator:
1. Right-click Command Prompt
2. Select "Run as Administrator"
3. Navigate to project directory
4. Run commands

### Issue: "LLM not working"

**Solution:**
Check LLM configuration:
```python
python
>>> from agents.config import Config
>>> print(f"Provider: {Config.LLM_PROVIDER}")
>>> print(f"API Key: {Config.GOOGLE_API_KEY[:10]}...")
>>> exit()
```

### Issue: "Import errors"

**Solution:**
Ensure you're in the correct directory:
```bash
cd "l:\Personal\MY LEARNING\MY PROJECTS\advanced hidr-agent system"
python verify_installation.py
```

---

## 📦 What Gets Installed

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| langgraph | 0.2.0+ | Multi-agent orchestration |
| langchain | 0.1.0+ | Agent framework |
| langchain-google-genai | 1.0.0+ | Gemini integration |
| psutil | 5.9.0+ | Process management |
| watchdog | 2.1.9+ | File monitoring |
| requests | 2.31.0+ | HTTP client |
| python-dotenv | 1.0.0+ | Environment config |
| matplotlib | 3.5.0+ | Visualization |
| pandas | 1.3.0+ | Data analysis |

**Total size:** ~200MB

### Project Structure

```
advanced-hidr-agent-system/
├── agents/          # 5 specialized agents
├── tools/           # 8 security tools
├── core/            # Main system interface
├── examples/        # 3 demo scripts
├── tests/           # Unit tests
├── docs/            # Documentation
├── quarantine/      # Isolated threats
├── backups/         # File backups
├── logs/            # System logs
└── reports/         # Generated reports
```

---

## ✅ Post-Installation Checklist

After installation, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] `.env` file created with API keys
- [ ] `verify_installation.py` passes all checks
- [ ] `demo_basic.py` runs successfully
- [ ] Can see agent communication logs
- [ ] AI analysis working (Gemini)
- [ ] VirusTotal queries working

---

## 🎯 Next Steps

### 1. Run Demos

```bash
# Basic demo (automated)
python examples\demo_basic.py

# Human-in-the-loop demo
python examples\demo_human_loop.py

# Complete demo (all features)
python examples\demo_complete.py
```

### 2. Read Documentation

- **QUICKSTART.md** - 5-minute quick start
- **README_MULTIAGENT.md** - Complete documentation
- **docs/ARCHITECTURE.md** - System architecture
- **CONTRIBUTING.md** - How to contribute

### 3. Integrate with Your System

```python
from core.multiagent_monitor import MultiAgentHIDR

# Initialize
hidr = MultiAgentHIDR(require_human_approval=True)

# Analyze threats
result = hidr.analyze_process(...)

# View results
hidr.print_summary(result)
```

### 4. Customize Configuration

Edit `agents/config.py`:
```python
SUSPICIOUS_THRESHOLD = 3   # Adjust sensitivity
CRITICAL_THRESHOLD = 7     # Adjust critical level
```

---

## 🔄 Updating

### Update Dependencies

```bash
pip install -r requirements_multiagent.txt --upgrade
```

### Update Configuration

```bash
# Backup current config
copy .env .env.backup

# Update from template
copy .env.example .env

# Restore your API keys
notepad .env
```

### Verify After Update

```bash
python verify_installation.py
```

---

## 🆘 Getting Help

### Documentation

- **README_MULTIAGENT.md** - Main documentation
- **QUICKSTART.md** - Quick start guide
- **docs/ARCHITECTURE.md** - Technical details
- **PROJECT_SUMMARY.md** - Project overview

### Support

- **GitHub Issues** - Report bugs
- **Examples** - See `examples/` directory
- **Tests** - See `tests/` directory

### Common Commands

```bash
# Verify installation
python verify_installation.py

# Run basic demo
python examples\demo_basic.py

# Run tests
python tests\test_multiagent.py

# Check configuration
python -c "from agents.config import Config; Config.validate()"
```

---

## 📊 Installation Verification Output

When `verify_installation.py` succeeds, you'll see:

```
🔍 MULTI-AGENT HIDR SYSTEM - INSTALLATION VERIFICATION

🐍 Checking Python version...
   ✅ Python 3.11.0 (OK)

📦 Checking dependencies...
   ✅ LangGraph
   ✅ LangChain
   ✅ Gemini Integration
   ✅ Process Tools
   ✅ HTTP Client
   ✅ Environment Config

📁 Checking project structure...
   ✅ agents/
   ✅ tools/
   ✅ core/
   ✅ examples/
   ✅ tests/
   ✅ docs/

⚙️  Checking configuration...
   ✅ .env.example (Template found)
   ✅ .env (Configuration found)
   ✅ Gemini API key configured
   ✅ VirusTotal API key configured

🤖 Checking agents...
   ✅ DetectionAgent - Threat Detection Specialist
   ✅ IntelligenceAgent - Threat Intelligence Specialist
   ✅ ResponseAgent - Incident Response Specialist
   ✅ AnalystAgent - Security Analyst (AI-Powered)
   ✅ CoordinatorAgent - Multi-Agent Coordinator

🛠️  Checking tools...
   ✅ SecurityTools
   ✅ FileTools
   ✅ ProcessTools
   ✅ VirusTotalTool
   ✅ LLMTools

🔄 Checking orchestrator...
   ✅ MultiAgentOrchestrator initialized
   ✅ Workflow compiled successfully

🧪 Running quick functionality test...
   ✅ System initialized successfully
   🔍 Testing process analysis...
   ✅ Process analysis completed
      Action: monitor
      Threat Level: 0/10

📊 VERIFICATION SUMMARY

Tests Passed: 8/8

Detailed Results:
   ✅ PASS - Python Version
   ✅ PASS - Dependencies
   ✅ PASS - Project Structure
   ✅ PASS - Configuration
   ✅ PASS - Agents
   ✅ PASS - Tools
   ✅ PASS - Orchestrator
   ✅ PASS - Functionality Test

🎯 FINAL VERDICT

✅ ALL CHECKS PASSED!

Your Multi-Agent HIDR System is properly installed and ready to use!

Next steps:
   1. Run: python examples\demo_basic.py
   2. Read: README_MULTIAGENT.md
   3. Try: python examples\demo_human_loop.py
```

---

## 🎉 Installation Complete!

You now have a fully functional Multi-Agent HIDR System!

**What you can do:**
- ✅ Detect threats using 5 specialized agents
- ✅ Get AI-powered threat analysis
- ✅ Query VirusTotal for threat intelligence
- ✅ Make informed decisions with human-in-the-loop
- ✅ Automate incident response
- ✅ Track performance metrics

**Start using it:**
```bash
python examples\demo_basic.py
```

---

**Need help?** Check QUICKSTART.md or README_MULTIAGENT.md

**Ready to contribute?** See CONTRIBUTING.md

**Want to learn more?** Read docs/ARCHITECTURE.md
