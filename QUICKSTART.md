# 🚀 Quick Start Guide - Multi-Agent HIDR System

Get up and running with the Multi-Agent HIDR System in 5 minutes!

---

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
cd "advanced hidr-agent system"
pip install -r requirements_multiagent.txt
```

### Step 2: Configure API Keys (1 minute)

1. Copy the environment template:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   VIRUSTOTAL_API_KEY=your_key_here
   GOOGLE_API_KEY=your_gemini_key_here
   LLM_PROVIDER=gemini
   ```

### Step 3: Run Your First Demo (2 minutes)

```bash
python examples\demo_basic.py
```

**That's it!** 🎉 You're now running a multi-agent security system!

---

## 🎯 What Just Happened?

You just ran a **5-agent collaborative system** that:

1. **DetectionAgent** analyzed threats using heuristics
2. **IntelligenceAgent** queried VirusTotal for reputation
3. **AnalystAgent** used Gemini AI to explain threats
4. **CoordinatorAgent** orchestrated the workflow
5. **ResponseAgent** executed security actions

All orchestrated by **LangGraph** with agent-to-agent communication!

---

## 🧪 Try More Examples

### Example 1: Human-in-the-Loop

Experience AI-powered threat analysis with human decision making:

```bash
python examples\demo_human_loop.py
```

You'll see:
- AI explains threats in plain English
- VirusTotal detections
- 4 decision options (Allow, Terminate Temp, Terminate Permanent, Monitor)

### Example 2: Complete Demo

See all features in action:

```bash
python examples\demo_complete.py
```

Includes:
- Multiple threat scenarios
- Performance metrics
- Agent communication analysis
- AAIDC criteria verification

---

## 💻 Use in Your Code

### Basic Usage

```python
from core.multiagent_monitor import MultiAgentHIDR

# Initialize system
hidr = MultiAgentHIDR(require_human_approval=False)

# Analyze a process
result = hidr.analyze_process(
    proc_name="suspicious.exe",
    path="C:\\temp\\suspicious.exe",
    cmdline="suspicious.exe --payload",
    pid=1234
)

# View results
print(f"Threat Level: {result['detection_result']['threat_level']}/10")
print(f"Action Taken: {result['final_action']}")
print(f"AI Analysis: {result['analysis_result']['summary']}")
```

### With Human Approval

```python
# Enable human-in-the-loop
hidr = MultiAgentHIDR(require_human_approval=True)

# System will ask for your decision when threats are detected
result = hidr.analyze_process(...)

# View your decision
print(f"Your choice: {result['human_decision']['reason']}")
```

### Analyze Files

```python
# Check file integrity
result = hidr.analyze_file(
    filepath="C:\\data\\important.docx",
    old_hash="previous_hash_here"  # Optional
)

if result['detection_result']['is_modified']:
    print("File integrity violation!")
```

---

## 📊 View Results

### Print Summary

```python
hidr.print_summary(result)
```

Output:
```
📊 WORKFLOW SUMMARY:
--------------------------------------------------
Event Type: process
Final Action: terminate_permanent

🔍 Detection:
   Threat Level: 8/10
   Suspicious: True

🌐 Intelligence:
   Known Malware: True
   Threat Score: 9.2/10

🤖 AI Analysis:
   Severity: Critical
   Summary: This is ransomware based on...

🛡️ Response:
   Success: True
   Message: Process terminated and quarantined
```

### View Agent Communication

```python
hidr.print_agent_communication(result)
```

Output:
```
📨 AGENT COMMUNICATION LOG:
--------------------------------------------------
1. [DetectionAgent] → [IntelligenceAgent]
   ⚠️ Suspicious process detected! Threat level: 8/10
2. [IntelligenceAgent] → [AnalystAgent]
   🚨 CONFIRMED MALWARE! VirusTotal: 45 detections
3. [AnalystAgent] → [CoordinatorAgent]
   Analysis complete - Severity: Critical
...
```

---

## 🔧 Configuration

### Change LLM Provider

Edit `.env`:
```env
LLM_PROVIDER=gemini    # or openai, mistral
GOOGLE_API_KEY=your_key
```

### Adjust Detection Sensitivity

Edit `agents/config.py`:
```python
SUSPICIOUS_THRESHOLD = 3   # Lower = more sensitive
CRITICAL_THRESHOLD = 7     # Lower = more critical alerts
```

### Enable/Disable Features

Edit `.env`:
```env
REQUIRE_HUMAN_APPROVAL=true   # Enable human-in-the-loop
QUARANTINE_ENABLED=true       # Enable file quarantine
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
```

---

## 🎓 Next Steps

### 1. Read the Documentation

- **README_MULTIAGENT.md** - Complete system documentation
- **docs/ARCHITECTURE.md** - System architecture and design
- **CONTRIBUTING.md** - How to contribute

### 2. Explore the Code

```
agents/          # 5 specialized agents
tools/           # Security tools
core/            # Main system interface
examples/        # Demo scripts
tests/           # Unit tests
```

### 3. Run Tests

```bash
python tests\test_multiagent.py
```

### 4. Integrate with Your System

```python
# In your security monitoring code
from core.multiagent_monitor import MultiAgentHIDR

hidr = MultiAgentHIDR()

# When you detect suspicious activity
result = hidr.analyze_process(...)

# Take action based on result
if result['final_action'] == 'terminate_permanent':
    # Handle critical threat
    pass
```

---

## 🐛 Troubleshooting

### "No module named 'langgraph'"

```bash
pip install -r requirements_multiagent.txt
```

### "API key not configured"

Make sure `.env` file exists and contains your API keys:
```bash
copy .env.example .env
notepad .env
```

### "Permission denied" errors

Run as Administrator (required for process termination):
```bash
# Right-click Command Prompt → Run as Administrator
python examples\demo_basic.py
```

### LLM not working

Check your API key and provider:
```python
from agents.config import Config
print(f"Provider: {Config.LLM_PROVIDER}")
print(f"API Key set: {bool(Config.GOOGLE_API_KEY)}")
```

---

## 💡 Tips & Tricks

### Disable Human Approval for Testing

```python
hidr = MultiAgentHIDR(require_human_approval=False)
```

### View Detailed Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Without Real Threats

Use the demo scripts - they simulate threats safely:
```bash
python examples\demo_basic.py
```

### Get System Statistics

```python
stats = hidr.get_statistics()
print(f"Total workflows: {stats['total_workflows']}")
print(f"Priority distribution: {stats['priority_distribution']}")
```

---

## 🎉 You're Ready!

You now have a **production-ready multi-agent security system** running!

### What You've Learned

✅ How to install and configure the system  
✅ How to run demos and examples  
✅ How to use the system in your code  
✅ How to view results and agent communication  
✅ How to configure and customize  

### What's Next?

- Integrate with your existing security tools
- Customize agents for your specific needs
- Add new tools and capabilities
- Contribute back to the project

---

## 📞 Need Help?

- **Documentation**: README_MULTIAGENT.md
- **Issues**: GitHub Issues
- **Examples**: examples/ directory
- **Tests**: tests/ directory

---

**Happy Threat Hunting!** 🛡️🔍
