

**A defensive cybersecurity tool built for threat detection and automated response**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-52%20passing-brightgreen.svg)](tests/)



---
 # PDF Preview  [![PDF Preview](https://img.shields.io/badge/PDF-View%20Document-red?logo=adobeacrobatreader)](https://fuchsia-erika-13.tiiny.site/)

## 📖 The Story Behind HIDR

As a cybersecurity enthusiast, I noticed a critical gap in the security tools landscape. Most solutions are either prohibitively expensive for researchers and students, or they're black boxes that don't teach you anything about how threats are detected.

I wanted to build something different - a tool that's:
- **Transparent**: Every detection decision is explainable
- **Educational**: Learn how multi-agent systems work in cybersecurity
- **Defensive**: Built to protect, not to attack
- **Accessible**: Free and open for everyone

HIDR combines multiple detection techniques (YARA signatures, behavioral analysis, expert systems) into one cohesive platform. It's not just a tool - it's my contribution to making cybersecurity more accessible and defensive security stronger.

**— Lakshya Agarwal (SecuVortex)**

---

## 🎯 What is HIDR?

HIDR is a multi-agent cybersecurity system that automatically detects and responds to threats on your system. It uses:

- **Path-Based Trust**: Legitimate software in trusted directories (Program Files, Windows) is automatically trusted
- **YARA Rules**: Signature-based malware detection (5 rule categories)
- **Expert System**: Rule-based threat scoring with MITRE ATT&CK mapping
- **Behavioral Analysis**: Process behavior monitoring
- **VirusTotal Integration**: Optional threat intelligence (API key required)
- **Automated Response**: Quarantine, terminate, or monitor threats

---

## ✨ Key Features

```
┌─────────────────────────────────────────────────────────────┐
│                    HIDR Architecture                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Process Detection                                          │
│         ↓                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Path Check   │ →  │ YARA Scanner │ →  │ Expert System│ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         ↓                    ↓                    ↓        │
│  Trusted Path?        Signature Match      Threat Scoring  │
│  → Allow              MITRE Mapping        Action Decision │
│                              ↓                    ↓         │
│                       ┌──────────────┐    ┌──────────────┐ │
│                       │ Cert Validator│ →  │   Response   │ │
│                       └──────────────┘    └──────────────┘ │
│                              ↓                    ↓         │
│                       OCSP/CRL/CT          Quarantine       │
│                       Revocation           Terminate        │
│                                            Monitor          │
└─────────────────────────────────────────────────────────────┘
```

### Core Capabilities

✅ **Smart Detection**
- Path-based trust system (no false positives on legitimate software)
- YARA signature scanning (5 rule categories)
- Heuristic analysis
- Behavioral monitoring
- VirusTotal integration (optional)
- **Certificate validation (OCSP/CRL/CT)** - NEW in v3.0

✅ **Intelligent Analysis**
- Expert system with weighted scoring
- MITRE ATT&CK technique mapping
- Multi-factor threat assessment
- Deterministic decision-making

✅ **Automated Response**
- Process termination (temporary/permanent)
- File quarantine with metadata
- Real-time monitoring
- Automated reporting

✅ **Production-Ready GUI**
- 6-tab interface (Processes, Quarantine, Reports, Agent Logs, Settings, About)
- **Real-time Background Monitoring** - Automatic process detection every 5 seconds
- **Agent Logs Tab** - Live agent activity with color-coded logs
- **Trusted Paths Management** - Add custom trusted directories
- Auto-scan capability (configurable intervals)
- Real-time statistics
- Export reports (JSON/CSV/HTML)
- Non-blocking GUI (always responsive)

---

## 🚀 Quick Setup

### Prerequisites

- Python 3.8 or higher
- Windows/Linux/macOS
- 4GB RAM (8GB recommended)
- **Administrator privileges** (required for process termination and quarantine)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/hidr-system.git
cd hidr-system

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir logs quarantine reports

# Run GUI as Administrator (Windows)
# Right-click Command Prompt → Run as Administrator
python production_gui.py
```

### First Run

1. **Launch the GUI**: `python production_gui.py` (as Administrator)
2. Go to **Settings** tab
3. Configure thresholds (default: Threat=5, Terminate=8)
4. **Add Trusted Paths** (optional):
   - Click "Add Path" in Trusted Paths section
   - Select directories containing legitimate software
   - Examples: `D:\Steam\`, `C:\Development\`, `C:\Adobe\`
5. Enable auto-scan if desired (1-30 minute intervals)
6. Click **Save Settings**
7. Go to **Processes** tab and click "Start Scan"

---

## 📊 How It Works

### Detection Flow

```
┌─────────────┐
│   Process   │
│  Detected   │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────┐
│  Path Check                             │
│  • Is process in trusted path?          │
│  • C:\Windows\, C:\Program Files\       │
│  • Custom trusted paths from config     │
└──────┬──────────────────────────────────┘
       │
       ├─ YES → Allow (0/10 threat)
       │
       └─ NO → Continue Analysis
              ↓
       ┌─────────────────────────────────────────┐
       │  Detection Agent                        │
       │  • Heuristic analysis                   │
       │  • YARA signature matching              │
       │  • Suspicious location check            │
       └──────┬──────────────────────────────────┘
              │
              ↓
       ┌─────────────────────────────────────────┐
       │  Intelligence Agent                     │
       │  • VirusTotal lookup (optional)         │
       │  • Behavioral analysis                  │
       │  • Process monitoring                   │
       └──────┬──────────────────────────────────┘
              │
              ↓
       ┌─────────────────────────────────────────┐
       │  Analysis Agent (Expert System)         │
       │  • Weighted threat scoring              │
       │  • MITRE ATT&CK mapping                 │
       │  • Severity classification              │
       └──────┬──────────────────────────────────┘
              │
              ↓
       ┌─────────────────────────────────────────┐
       │  Coordinator Agent                      │
       │  • Action determination                 │
       │  • Threshold evaluation                 │
       │  • Response selection                   │
       └──────┬──────────────────────────────────┘
              │
              ↓
       ┌─────────────────────────────────────────┐
       │  Response Agent                         │
       │  • Terminate process                    │
       │  • Quarantine file                      │
       │  • Monitor activity                     │
       │  • Log incident                         │
       └─────────────────────────────────────────┘
```

### Path-Based Trust System

**Default Trusted Paths:**
- `C:\Windows\` - All Windows system files
- `C:\Program Files\` - Installed applications
- `C:\Program Files (x86)\` - 32-bit applications
- `/usr/bin/`, `/usr/sbin/` - Linux system binaries

**Custom Trusted Paths:**
Add your own trusted directories in Settings → Trusted Paths:
- `D:\Steam\` - Gaming platform
- `C:\Development\` - Development tools
- `C:\Adobe\` - Creative software
- Any directory containing legitimate software

**How it works:**
1. Process detected → Check if path starts with any trusted path
2. If YES → 0/10 threat, allow immediately (no YARA scan needed)
3. If NO → Full analysis with YARA, heuristics, and expert system

### Threat Scoring

HIDR uses a weighted scoring system:

| Component | Weight | Description |
|-----------|--------|-------------|
| YARA | 3.0 | Signature matches |
| VirusTotal | 2.5 | Threat intelligence |
| Behavioral | 1.5 | Process behavior |
| MITRE | 2.0 | ATT&CK techniques |

**Final Score = (YARA × 3.0) + (VT × 2.5) + (Behavior × 1.5) + (MITRE × 2.0)**

### Actions

- **Score 0-4**: Allow (safe process)
- **Score 5-7**: Monitor (suspicious activity)
- **Score 8-9**: Terminate Temporary (high threat)
- **Score 10**: Terminate Permanent + Quarantine (critical threat)

---

## 🎮 Usage Examples

### Command Line

```python
from simple_multiagent import SimpleMultiAgent

# Initialize system
agent = SimpleMultiAgent()

# Analyze legitimate software (trusted path)
result = agent.analyze_process(
    proc_name='chrome.exe',
    path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    cmdline='chrome.exe',
    pid=1234
)
print(f"Chrome: {result['detection_result']['threat_level']}/10")  # Output: 0/10

# Analyze suspicious process (untrusted location)
result = agent.analyze_process(
    proc_name='ransomware.exe',
    path='C:\\temp\\ransomware.exe',
    cmdline='ransomware.exe --encrypt',
    pid=9999
)
print(f"Ransomware: {result['detection_result']['threat_level']}/10")  # Output: 9/10
print(f"Action: {result['final_action']}")  # Output: terminate_permanent
```

### GUI Mode

```bash
# Run as Administrator (Windows)
python production_gui.py
```

**Features:**
- **Processes Tab**: Real-time scanning with threat levels, YARA matches, MITRE techniques
- **Quarantine Tab**: Manage quarantined files (restore/delete with metadata)
- **Reports Tab**: View statistics and export reports (JSON/CSV/HTML)
- **Settings Tab**: 
  - Configure thresholds and weights
  - **Manage Trusted Paths** (Add/Remove custom directories)
  - Enable auto-scan (1-30 minute intervals)
- **About Tab**: System information, agent status, creator info

---

## 🧪 Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Test Coverage

```bash
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Categories

- **Configuration** (4 tests): Config loading and validation
- **Detection** (10 tests): YARA, heuristics, threat scoring
- **Expert System** (8 tests): Weighted scoring, MITRE mapping
- **LangGraph** (5 tests): State machine orchestration
- **Multi-Agent** (6 tests): Agent communication and workflow
- **Resilience** (12 tests): Retry, timeout, circuit breaker
- **YARA Scanner** (8 tests): Rule loading, file scanning

**Total: 60 tests passing** (52 original + 8 Phase 1)

---

## ⚙️ Configuration

### config.yaml

```yaml
detection:
  threat_threshold: 5          # Flag as suspicious (0-10)
  terminate_threshold: 8       # Auto-terminate (0-10)

paths:
  trusted_paths:               # Processes in these paths are trusted
  - c:\windows\
  - c:\program files\
  - c:\program files (x86)\
  # Add custom paths here or via GUI Settings

yara:
  enabled: true
  rules_dir: "yara_rules"
  scan_timeout: 2

expert_system:
  enabled: true
  weights:
    yara: 3.0
    virustotal: 2.5
    behavioral: 1.5
    mitre: 2.0

langgraph:
  enabled: false               # Optional state machine orchestration

monitoring:
  vt_timeout: 2                # VirusTotal API timeout
  behavior_timeout: 0.5        # Behavioral analysis timeout
```

### .env (Optional)

```bash
# VirusTotal API (optional - system works without it)
VIRUSTOTAL_API_KEY=your_key_here
```

**Note**: System works perfectly without any API keys using local YARA scanning and expert system.

---

## 📈 Performance

- **Average Analysis Time**: 2-5 seconds per process
- **Trusted Path Check**: < 1ms (instant allow)
- **YARA Scan**: < 100ms
- **Expert System**: < 50ms
- **Memory Usage**: ~100MB
- **CPU Usage**: < 5% idle, ~20% during scan

---

## 🔒 Security Features

### What Works WITHOUT API Keys

✅ **Path-Based Trust** - Automatic trust for legitimate software locations  
✅ **YARA Scanning** - Local signature matching (5 rule categories)  
✅ **Expert System** - Rule-based threat scoring  
✅ **Heuristic Detection** - Process name/path analysis  
✅ **Behavioral Analysis** - Process monitoring  
✅ **MITRE ATT&CK Mapping** - Technique identification  
✅ **Quarantine** - Secure file isolation with metadata  
✅ **Auto-Scan** - Periodic system scanning (1-30 min intervals)  
✅ **Reports** - JSON/CSV/HTML export  
✅ **Trusted Paths Management** - Add custom trusted directories  

### Optional Features (Require API Keys)

⚠️ **VirusTotal Integration** - Threat intelligence lookup (free tier: 4 requests/min)

---

## 🛠️ Troubleshooting

### Issue: Legitimate software flagged as threat

**Solution**: Add the software's directory to Trusted Paths
1. Go to Settings → Trusted Paths
2. Click "Add Path"
3. Select the directory (e.g., `D:\MyApp\`)
4. Click "Save Settings"
5. Restart application

### Issue: "Access Denied" when terminating process

**Solution**: Run as Administrator
- Windows: Right-click Command Prompt → Run as Administrator
- Linux/Mac: Use `sudo python production_gui.py`

### Issue: Quarantine not working

**Solution**: 
1. Check Administrator privileges
2. Verify `quarantine/` folder exists and is writable
3. Check logs: `type logs\hidr.log | findstr "Response"`

### Issue: YARA rules not loading

**Solution**: 
1. Verify `yara_rules/` folder exists
2. Check it contains 5 .yar files (ransomware, malware, rat, keylogger, cryptominer)
3. Install yara-python: `pip install yara-python`

---

## 📝 License

MIT License

Copyright (c) 2025 Lakshya Agarwal (SecuVortex)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 👨💻 About the Creator

**SecuVortex (Lakshya Agarwal)**

I'm a cybersecurity enthusiast passionate about building defensive security tools that are accessible to everyone. HIDR represents my vision of transparent, educational, and effective threat detection.

My goal is to make cybersecurity less intimidating and more approachable for students, researchers, and security professionals alike. Every line of code in HIDR is written with the intention of teaching while protecting.

**Why I built HIDR:**
- To provide a free, open-source alternative to expensive security tools
- To demonstrate how multi-agent systems work in cybersecurity
- To create a tool that's transparent and educational, not a black box
- To contribute to the defensive security community

**Contact**: secuvortex@gmail.com

---

## 🙏 Acknowledgments

- **YARA Project** - For the powerful signature matching engine
- **MITRE ATT&CK** - For the comprehensive threat framework
- **LangChain/LangGraph** - For multi-agent orchestration capabilities
- **VirusTotal** - For threat intelligence API

---

## 🔄 Version History

### v3.0.0 (October 2025) - Production Release
- ✅ Background monitoring thread (non-blocking)
- ✅ Event queue system (thread-safe)
- ✅ Agent Logs tab (real-time activity)
- ✅ GUI live updates (500ms refresh)
- ✅ Automatic process detection
- ✅ Phase 1 test suite (8 tests)
- 📄 [Phase 1 Documentation](PHASE1_COMPLETE.md)
- 📄 [Phase 1 Quick Start](PHASE1_QUICKSTART.md)
- 📄 [Phase 1 Architecture](PHASE1_ARCHITECTURE.md)

### v2.0.0 (September 2025) - Production Ready
- ✅ Path-based trust system (no false positives)
- ✅ Trusted Paths management (GUI + config)
- ✅ YARA integration (5 rule categories)
- ✅ Expert system (weighted scoring)
- ✅ LangGraph orchestration (optional)
- ✅ Resilience layer (retry, circuit breaker)
- ✅ Production GUI (5 tabs)
- ✅ Auto-scan feature (1-30 min intervals)
- ✅ Process termination & quarantine
- ✅ Test suite (52 tests)
- ✅ Complete documentation

### v1.0.0 (August 2025) - Initial Release
- Basic multi-agent system
- Simple detection
- Command-line interface

---

**Built with ❤️ for Defensive Cybersecurity**

*Making security accessible, one threat at a time.*

**SecuVortex (Lakshya Agarwal)** | secuvortex@gmail.com
