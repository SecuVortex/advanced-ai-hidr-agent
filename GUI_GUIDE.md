# 🖥️ Multi-Agent HIDR GUI Guide

Complete guide to using the Multi-Agent HIDR System GUI

---

## 🚀 Quick Start

### Launch the GUI

```bash
python run_multiagent_gui.py
```

**First time?** The GUI will show:
- ✅ 5 agent status indicators
- ✅ Real-time agent communication log
- ✅ Live monitoring dashboards
- ✅ Interactive charts and analytics

---

## 📊 GUI Overview

### Main Tabs

1. **Dashboard** - System status and live metrics
2. **🤖 Multi-Agent System** - Agent communication and workflow
3. **Live Monitoring** - Process and file events
4. **Quarantine** - Isolated threats
5. **Reports & Analytics** - Charts and statistics

---

## 🤖 Multi-Agent System Tab

### Agent Status Panel

Shows real-time status of all 5 agents:

- **🔍 DetectionAgent** - Threat Detection Specialist
  - Lights up GREEN when analyzing threats
  - Uses heuristics and behavioral analysis

- **🌐 IntelligenceAgent** - Threat Intelligence Specialist
  - Lights up GREEN when querying VirusTotal
  - Provides reputation scores

- **🤖 AnalystAgent** - AI Analysis (Gemini-powered)
  - Lights up GREEN when generating AI analysis
  - Provides natural language explanations

- **🎯 CoordinatorAgent** - Multi-Agent Coordinator
  - Lights up GREEN when coordinating workflow
  - Manages agent collaboration

- **🛡️ ResponseAgent** - Incident Response Specialist
  - Lights up GREEN when executing actions
  - Handles quarantine and termination

### Agent Communication Log

Real-time display of agent-to-agent messages:

```
[14:23:45] [DetectionAgent] → [IntelligenceAgent]: ⚠️ Suspicious process detected!
[14:23:46] [IntelligenceAgent] → [AnalystAgent]: Threat score: 7.5/10
[14:23:47] [AnalystAgent] → [CoordinatorAgent]: Analysis complete - Severity: High
[14:23:48] [CoordinatorAgent] → [ResponseAgent]: Priority: High, Action: terminate
[14:23:49] [ResponseAgent] → [System]: Action 'terminate' completed successfully
```

### Workflow Status

Shows current workflow state:
- **IDLE** - No active analysis
- **Analyzing process...** - Detection in progress
- **Complete: terminate** - Action executed
- **Error** - Something went wrong

---

## 📈 Dashboard Tab

### Live Metrics

Six real-time metric cards:

1. **Process Events** - Total processes monitored
2. **File Events** - Total file operations
3. **Threats Blocked** - Suspicious processes terminated
4. **Files Quarantined** - Files isolated
5. **Uptime** - System running time
6. **Status** - ACTIVE or STOPPED

### Control Buttons

- **Start Protection** - Activate multi-agent monitoring
- **Stop Protection** - Deactivate monitoring
- **Quick Test** - Run basic attack simulation
- **Advanced Attack** - Run multi-stage attack
- **Keylogger Test** - Test keylogger detection

### Live Activity Log

Scrolling log of all system activities:

```
[14:23:45] 🤖 Multi-Agent HIDR System started - 5 agents active!
[14:23:50] ✓ ALLOWED: notepad.exe (PID: 1234)
[14:24:10] ⚠️ THREAT: ransomware.exe (PID: 5678) - Threat: 8/10 - Critical
[14:24:11] TERMINATED: ransomware.exe (PID: 5678) - Ransomware executable detected
```

---

## 🔍 Live Monitoring Tab

### Process Events Table

Columns:
- **Time** - When process was detected
- **Process** - Process name
- **PID** - Process ID
- **Path** - Executable location
- **Action** - ALLOWED, BLOCKED, TERMINATED, ANALYZED
- **Reason** - Why action was taken

**Color Coding:**
- 🟢 Green background = Allowed (normal)
- 🔴 Red background = Blocked/Terminated (threat)

### File Events Table

Columns:
- **Time** - When file event occurred
- **File** - File path
- **Event** - modified, created, deleted
- **Action** - MONITORED, QUARANTINED, RESTORED
- **Reason** - Why action was taken

**Color Coding:**
- 🟣 Purple background = Normal activity
- 🟠 Orange background = Quarantined

---

## 🔒 Quarantine Tab

### Quarantined Files List

Shows all isolated threats:
- **File** - Quarantine filename
- **Original** - Original filename
- **Date** - When quarantined
- **Size** - File size
- **Reason** - Why quarantined

### Actions

- **Refresh** - Update quarantine list
- **Export List** - Save to CSV
- **Clear All** - Delete all quarantined files (requires confirmation)

---

## 📊 Reports & Analytics Tab

### Generate Report

Creates comprehensive HTML report with:
- Summary metrics
- Recent process events
- Recent file events
- Charts and graphs

### Export CSV

Exports incident log to CSV for analysis

### Update Charts

Refreshes all visualizations

### Charts

1. **Timeline** - Security events over time
2. **Distribution** - Event types and actions pie charts
3. **Statistics** - Detailed text statistics

---

## 🎮 How to Use

### Basic Workflow

1. **Launch GUI**
   ```bash
   python run_multiagent_gui.py
   ```

2. **Start Protection**
   - Click "Start Protection" button
   - Wait for confirmation message
   - Watch agents activate (green indicators)

3. **Monitor Activity**
   - Switch to "🤖 Multi-Agent System" tab
   - Watch agent communication in real-time
   - See workflow status updates

4. **View Events**
   - Switch to "Live Monitoring" tab
   - See all process and file events
   - Color-coded for easy identification

5. **Check Quarantine**
   - Switch to "Quarantine" tab
   - Review isolated threats
   - Export or clear as needed

6. **Generate Reports**
   - Switch to "Reports & Analytics" tab
   - Click "Generate Report"
   - View in browser

### Testing the System

1. **Quick Test**
   - Click "Quick Test" button
   - Simulates basic ransomware attack
   - Watch agents detect and respond

2. **Advanced Attack**
   - Click "Advanced Attack" button
   - Multi-stage attack simulation
   - Tests all detection capabilities

3. **Keylogger Test**
   - Click "Keylogger Test" button
   - Simulates keylogger malware
   - Tests comprehensive detection

---

## 🎨 Visual Indicators

### Agent Status Colors

- **Gray ●** - Idle
- **Green ●** - Active (flashes for 1 second)
- **Red ●** - Error (if implemented)

### Event Colors

**Process Events:**
- 🟢 Green = Allowed (normal process)
- 🔴 Red = Blocked/Terminated (threat)

**File Events:**
- 🟣 Purple = Normal activity
- 🟠 Orange = Quarantined

### Workflow Status Colors

- **Gray** - IDLE
- **Blue** - Analyzing/Processing
- **Green** - Complete
- **Red** - Error

---

## 💡 Tips & Tricks

### Performance

- **Minimize tabs** - Only view active tab for better performance
- **Clear logs** - Restart GUI if logs get too large
- **Update charts** - Click "Update Charts" manually for latest data

### Monitoring

- **Watch agent communication** - Best way to understand what's happening
- **Check workflow status** - Shows current analysis stage
- **Review activity log** - Comprehensive event history

### Testing

- **Use test buttons** - Safe way to test detection
- **Monitor all tabs** - See different aspects of detection
- **Generate reports** - Document test results

---

## 🔧 Troubleshooting

### GUI Won't Start

**Error:** "Multi-agent system not available"

**Solution:**
```bash
pip install -r requirements_multiagent.txt
```

### Agents Not Activating

**Problem:** Agent indicators stay gray

**Solution:**
1. Check if protection is started
2. Verify API keys in `.env`
3. Check activity log for errors

### No Agent Communication

**Problem:** Communication log is empty

**Solution:**
1. Ensure multi-agent system is active
2. Trigger a test attack
3. Check if processes are being monitored

### Charts Not Showing

**Problem:** "Install dependencies for charts"

**Solution:**
```bash
pip install matplotlib pandas plotly
```

---

## 🆚 GUI vs Command Line

### Use GUI When:

✅ You want visual feedback  
✅ You need real-time monitoring  
✅ You want to see agent collaboration  
✅ You prefer interactive interface  
✅ You need charts and analytics  

### Use Command Line When:

✅ You want quick testing  
✅ You need automation  
✅ You're running on server  
✅ You prefer scripting  
✅ You want minimal resource usage  

---

## 🎯 Best Practices

### Daily Use

1. **Start protection** when system boots
2. **Monitor periodically** throughout the day
3. **Review quarantine** weekly
4. **Generate reports** monthly
5. **Update charts** before reports

### Testing

1. **Use test buttons** instead of real malware
2. **Monitor all tabs** during tests
3. **Document results** with reports
4. **Clear quarantine** after tests

### Maintenance

1. **Clear old logs** monthly
2. **Export quarantine list** before clearing
3. **Update dependencies** regularly
4. **Backup configuration** before changes

---

## 📸 Screenshots Guide

### Dashboard View
- Shows system status and metrics
- Control buttons at top
- Live activity log at bottom

### Multi-Agent Tab
- Agent status indicators at top
- Communication log in middle
- Workflow status at bottom

### Live Monitoring
- Process events table (top half)
- File events table (bottom half)
- Color-coded for easy scanning

### Quarantine
- List of isolated files
- Action buttons at top
- Sortable columns

### Reports & Analytics
- Control buttons at top
- Three chart tabs
- Interactive visualizations

---

## 🚀 Advanced Features

### Custom Monitoring

Edit `agents/config.py` to adjust:
- Detection thresholds
- Suspicious patterns
- Allowlist paths

### Integration

The GUI can be integrated with:
- SIEM systems (export CSV)
- Alerting systems (activity log)
- Reporting tools (HTML reports)

### Automation

Use command-line demos for:
- Scheduled scans
- Automated testing
- CI/CD integration

---

## 📞 Need Help?

### Documentation

- **START_HERE.md** - Getting started
- **README_MULTIAGENT.md** - Complete docs
- **QUICKSTART.md** - Quick start guide

### Support

- **GitHub Issues** - Report bugs
- **Examples** - See `examples/` directory
- **Tests** - See `tests/` directory

---

## 🎉 Enjoy the GUI!

The Multi-Agent HIDR GUI provides a powerful, visual way to:

✅ Monitor threats in real-time  
✅ See agent collaboration  
✅ Understand AI analysis  
✅ Track system performance  
✅ Generate professional reports  

**Launch it now:**
```bash
python run_multiagent_gui.py
```

---

**Questions?** Check START_HERE.md for navigation!

**Want command-line?** See examples/ directory!

**Ready to contribute?** See CONTRIBUTING.md!
