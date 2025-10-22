# 🤖 Multi-Agent HIDR System v2.0

**A Collaborative Multi-Agent System for Host Intrusion Detection & Response**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0+-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

The Multi-Agent HIDR System is an advanced cybersecurity solution that uses **5 specialized AI agents** working collaboratively to detect, analyze, and respond to security threats in real-time. Built with **LangGraph** for orchestration and powered by **Gemini AI** for intelligent analysis.

### ✨ Key Features

- **🤖 5 Specialized Agents** - Detection, Intelligence, Response, Analyst, Coordinator
- **🔄 LangGraph Orchestration** - State machine workflow with conditional routing
- **👤 Human-in-the-Loop** - Intelligent approval with AI explanations
- **🧠 AI-Powered Analysis** - Gemini/ChatGPT/Mistral integration
- **🌐 Threat Intelligence** - VirusTotal API integration
- **⚡ Real-Time Response** - Automated quarantine and termination
- **📊 Performance Metrics** - Execution time and accuracy tracking
- **🔒 Production-Ready** - Professional code quality and testing

---

## 🏗️ Architecture

### Multi-Agent Collaboration

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY EVENT                            │
│                  (Process or File)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  DetectionAgent       │  Heuristic Analysis
         │  - Pattern matching   │  Threat Scoring
         │  - Behavioral analysis│
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  IntelligenceAgent    │  Threat Intelligence
         │  - VirusTotal query   │  Reputation Scoring
         │  - IOC checking       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  AnalystAgent         │  AI Analysis
         │  - LLM explanation    │  Severity Rating
         │  - Recommendations    │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  CoordinatorAgent     │  Workflow Coordination
         │  - Priority calc      │  Conflict Resolution
         │  - Action selection   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Human Approval       │  Decision Making
         │  - AI explanation     │  4 Options
         │  - User choice        │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  ResponseAgent        │  Action Execution
         │  - Terminate process  │  Quarantine File
         │  - Monitor activity   │
         └───────────────────────┘
```

### Agent Roles

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **DetectionAgent** | Threat Detection Specialist | Heuristic analysis, pattern matching, threat scoring |
| **IntelligenceAgent** | Threat Intelligence Specialist | VirusTotal queries, reputation analysis, IOC checking |
| **AnalystAgent** | Security Analyst (AI-Powered) | LLM analysis, natural language explanations, recommendations |
| **CoordinatorAgent** | Multi-Agent Coordinator | Workflow orchestration, priority calculation, conflict resolution |
| **ResponseAgent** | Incident Response Specialist | Process termination, file quarantine, automated remediation |

---

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Python 3.8+
- Administrator privileges
- API Keys (VirusTotal, Gemini)

### Installation

1. **Clone the repository**
   ```bash
   cd "advanced hidr-agent system"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_multiagent.txt
   ```

3. **Configure API keys**
   ```bash
   # Copy .env.example to .env
   copy .env.example .env
   
   # Edit .env and add your API keys
   notepad .env
   ```

4. **Run demo**
   ```bash
   python examples\demo_basic.py
   ```

### First Run

```python
from core.multiagent_monitor import MultiAgentHIDR

# Initialize system
hidr = MultiAgentHIDR(require_human_approval=True)

# Analyze suspicious process
result = hidr.analyze_process(
    "suspicious.exe",
    "C:\\temp\\suspicious.exe",
    "suspicious.exe --payload",
    1234
)

# View results
hidr.print_summary(result)
hidr.print_agent_communication(result)
```

---

## 📋 Usage Examples

### Example 1: Automated Detection (No Human Approval)

```python
from core.multiagent_monitor import MultiAgentHIDR

# Initialize without human approval
hidr = MultiAgentHIDR(require_human_approval=False)

# Analyze process
result = hidr.analyze_process(
    "ransomware.exe",
    "C:\\temp\\ransomware.exe",
    "ransomware.exe --encrypt",
    9999
)

print(f"Action taken: {result['final_action']}")
print(f"Threat level: {result['detection_result']['threat_level']}/10")
```

### Example 2: Human-in-the-Loop

```python
from core.multiagent_monitor import MultiAgentHIDR

# Initialize with human approval
hidr = MultiAgentHIDR(require_human_approval=True)

# Analyze suspicious process
# System will ask for your decision
result = hidr.analyze_process(
    "suspicious.exe",
    "C:\\downloads\\suspicious.exe",
    "suspicious.exe",
    5555
)

# View your decision
print(f"Your choice: {result['human_decision']['reason']}")
print(f"Action taken: {result['final_action']}")
```

### Example 3: File Analysis

```python
from core.multiagent_monitor import MultiAgentHIDR

hidr = MultiAgentHIDR()

# Analyze file with integrity check
result = hidr.analyze_file(
    filepath="C:\\data\\important.docx",
    old_hash="abc123..."  # Previous hash
)

# Check if file was modified
if result['detection_result']['is_modified']:
    print("File integrity violation detected!")
```

---

## 🛠️ Configuration

### Environment Variables (.env)

```env
# API Keys
VIRUSTOTAL_API_KEY=your_key_here
GOOGLE_API_KEY=your_gemini_key_here

# LLM Provider (gemini, openai, mistral)
LLM_PROVIDER=gemini

# System Settings
REQUIRE_HUMAN_APPROVAL=true
LOG_LEVEL=INFO
QUARANTINE_ENABLED=true
```

### Detection Thresholds

```python
# In agents/config.py
SUSPICIOUS_THRESHOLD = 3   # Threat level >= 3 is suspicious
CRITICAL_THRESHOLD = 7     # Threat level >= 7 is critical
MAX_THREAT_SCORE = 10      # Maximum threat score
```

---

## 📊 Agent Communication Protocol

Agents communicate through structured messages:

```python
{
    "from_agent": "DetectionAgent",
    "to_agent": "IntelligenceAgent",
    "message": "Suspicious process detected! Threat level: 7/10",
    "data": {"threat_level": 7, "reasons": [...]},
    "timestamp": 1234567890.123
}
```

View communication log:

```python
result = hidr.analyze_process(...)
hidr.print_agent_communication(result)
```

Output:
```
📨 AGENT COMMUNICATION LOG:
--------------------------------------------------
1. [DetectionAgent] → [IntelligenceAgent]
   ⚠️ Suspicious process detected! Threat level: 7/10
2. [IntelligenceAgent] → [AnalystAgent]
   🚨 CONFIRMED MALWARE! VirusTotal: 45 detections
3. [AnalystAgent] → [CoordinatorAgent]
   Analysis complete - Severity: Critical
...
```

---

## 🎯 Human-in-the-Loop Decision Making

When a threat is detected, the system presents:

1. **AI Explanation** - Natural language analysis from Gemini
2. **Threat Details** - Severity, threat level, VirusTotal results
3. **Evidence** - Specific reasons for flagging
4. **4 Options**:
   - **ALLOW** - False positive, let it continue
   - **TERMINATE TEMPORARILY** - Kill process (can restart)
   - **TERMINATE PERMANENTLY** - Kill and quarantine
   - **MONITOR** - Watch closely without action

Example interaction:

```
⚠️  HUMAN DECISION REQUIRED
==================================================

🤖 AI ANALYST EXPLANATION:
This appears to be ransomware based on the process name
and location. It's launching from a temporary directory
with encryption-related command line arguments. Immediate
termination and quarantine is strongly recommended.

📊 THREAT DETAILS:
   Severity: Critical
   Threat Level: 8/10

🌐 VIRUSTOTAL ANALYSIS:
   Malicious: 45 detections
   Suspicious: 12 detections

WHAT WOULD YOU LIKE TO DO?
==================================================
  1. ALLOW
  2. TERMINATE TEMPORARILY
  3. TERMINATE PERMANENTLY (recommended)
  4. MONITOR

Your decision (1/2/3/4): 3
✓ Process will be TERMINATED and QUARANTINED
```

---

## 📈 Performance Metrics

The system tracks:

- **Execution Time** - Workflow completion time
- **Agent Communication** - Message count and patterns
- **Detection Accuracy** - Threat identification rate
- **Response Time** - Time to action
- **Priority Distribution** - Critical/High/Medium/Low

View statistics:

```python
stats = hidr.get_statistics()
print(f"Total workflows: {stats['total_workflows']}")
print(f"Priority distribution: {stats['priority_distribution']}")
print(f"Action distribution: {stats['action_distribution']}")
```

---

## 🧪 Testing

### Run Basic Demo

```bash
python examples\demo_basic.py
```

### Run Human-in-the-Loop Demo

```bash
python examples\demo_human_loop.py
```

### Run Complete Demo

```bash
python examples\demo_complete.py
```

### Run Original Test Attacks

```bash
python test_attack.py
python advanced_keylogger_sim.py
```

---

## 🔒 Security Considerations

- **API Keys** - Never commit `.env` file (use `.env.example`)
- **Administrator Rights** - Required for process termination
- **Quarantine** - Files are securely isolated
- **Logging** - All actions are logged for audit
- **Human Approval** - Recommended for production use

---

## 📚 Project Structure

```
advanced-hidr-agent-system/
├── agents/                  # Multi-agent system
│   ├── detection_agent.py   # Threat detection
│   ├── intelligence_agent.py # Threat intelligence
│   ├── response_agent.py    # Incident response
│   ├── analyst_agent.py     # AI analysis
│   ├── coordinator_agent.py # Coordination
│   └── orchestrator.py      # LangGraph workflow
├── tools/                   # Agent tools
│   ├── security_tools.py    # Core security ops
│   ├── file_tools.py        # File operations
│   ├── process_tools.py     # Process management
│   ├── virustotal_tool.py   # VirusTotal API
│   └── llm_tools.py         # LLM integration
├── core/                    # Core system
│   └── multiagent_monitor.py # Main interface
├── examples/                # Demo scripts
│   ├── demo_basic.py
│   ├── demo_human_loop.py
│   └── demo_complete.py
└── README_MULTIAGENT.md     # This file
```

---

## 🎓 AAIDC Module 2 Criteria

This project meets all AAIDC Module 2 requirements:

### ✅ Required Components

- **Multi-Agent System** - 5 agents with distinct roles
- **Agent Communication** - Structured message passing protocol
- **Orchestration Framework** - LangGraph state machine
- **Tool Integration** - 8+ tools (file, process, VT, LLM, etc.)
- **Built-in + Custom Tools** - LangChain + custom security tools

### ✅ Optional Enhancements

- **Human-in-the-Loop** - Intelligent approval with AI explanations
- **Communication Protocol** - Logged agent messages
- **Evaluation Metrics** - Performance and accuracy tracking

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👥 Authors

- **Lakshay Agarwal**
- **Ayush Gaur**
- **Ansh Pratap**

---

## 🙏 Acknowledgments

- **LangChain & LangGraph** - Multi-agent orchestration framework
- **Google Gemini** - AI-powered threat analysis
- **VirusTotal** - Threat intelligence platform
- **AAIDC Program** - Project inspiration and requirements

---

**Built with ❤️ for the cybersecurity community**

*Protecting systems through intelligent collaboration, one threat at a time.* 🛡️
