# 🧪 HIDR Testing Guide

**Complete guide for testing the HIDR Multi-Agent Threat Detection System**

---

## 🚀 Quick Test (5 Minutes)

### Prerequisites
- Python 3.8+ installed
- Administrator/root privileges
- Windows/Linux/macOS

### Steps

1. **Install Dependencies**
   ```bash
   cd hidr-system
   pip install -r requirements.txt
   ```

2. **Launch GUI** (as Administrator)
   ```bash
   # Windows: Right-click Command Prompt → Run as Administrator
   python production_gui.py
   
   # Linux/Mac
   sudo python production_gui.py
   ```

3. **Run First Scan**
   - Click **Processes** tab
   - Click **Start Scan** button
   - Watch real-time threat detection

4. **View Results**
   - Check threat levels (0-10 scale)
   - See YARA matches
   - View actions taken
   - Go to **Reports** tab for statistics

**Expected Results**: 
- Legitimate software: 0/10 threat (trusted paths)
- Suspicious processes: 5-7/10 threat
- System scans 50-200 processes in 30-60 seconds

---

## 🎯 Comprehensive Testing

### Test 1: Trusted Paths Protection

**Purpose**: Verify legitimate software is not flagged

**Steps**:
1. Launch HIDR GUI
2. Go to **Processes** tab
3. Click **Start Scan**
4. Look for common applications:
   - `chrome.exe` (Google Chrome)
   - `explorer.exe` (Windows Explorer)
   - `Code.exe` (VS Code)

**Expected Results**:
- All legitimate software: **0/10 threat**
- Action: **allow**
- Reason: **Trusted path**

**Pass Criteria**: ✅ No false positives on legitimate software

---

### Test 2: Threat Detection

**Purpose**: Verify system detects suspicious processes

**Steps**:
1. Create a test file in temp directory:
   ```bash
   # Windows
   echo test > C:\Temp\suspicious.exe
   
   # Linux/Mac
   echo test > /tmp/suspicious.exe
   ```

2. Run the file (it will just exit)

3. Scan with HIDR while it's running

**Expected Results**:
- Threat level: **5-7/10**
- Reason: **Temp directory, Suspicious name**
- Action: **monitor** or **terminate_temporary**

**Pass Criteria**: ✅ System flags suspicious locations

---

### Test 3: YARA Detection

**Purpose**: Verify YARA signature matching works

**Steps**:
1. Check YARA rules loaded:
   ```bash
   python -c "from core.yara_scanner import YaraScanner; s = YaraScanner(); print(f'YARA Rules: {s.rules_count}')"
   ```

2. Expected output: `YARA Rules: 5`

3. Verify rule categories:
   - `yara_rules/ransomware.yar`
   - `yara_rules/rat.yar`
   - `yara_rules/keylogger.yar`
   - `yara_rules/cryptominer.yar`
   - `yara_rules/malware.yar`

**Pass Criteria**: ✅ All 5 YARA rule files loaded

---

### Test 4: Expert System Scoring

**Purpose**: Verify weighted threat scoring

**Steps**:
1. Test with command line:
   ```bash
   python -c "from simple_multiagent import SimpleMultiAgent; a = SimpleMultiAgent(); r = a.analyze_process('test.exe', 'C:\\Temp\\test.exe', '', 12345); print(f'Threat: {r[\"detection_result\"][\"threat_level\"]}/10'); print(f'Reasons: {r[\"detection_result\"][\"reasons\"]}')"
   ```

2. Check threat calculation:
   - YARA weight: 3.0
   - MalwareBazaar weight: 3.5
   - VirusTotal weight: 2.5
   - Behavioral weight: 1.5
   - MITRE weight: 2.0

**Expected Results**:
- Threat score: 0-10 range
- Multiple detection reasons listed
- Action based on threshold

**Pass Criteria**: ✅ Threat score calculated correctly

---

### Test 5: API Integration (Optional)

**Purpose**: Test MalwareBazaar API connection

**Prerequisites**: API key configured in Settings

**Steps**:
1. Go to **Settings** tab
2. Enter MalwareBazaar API key
3. Click **Test** button

**Expected Results**:
- ✅ Success message: "MalwareBazaar API key is valid!"
- OR ❌ Error: "Invalid API key" (if key is wrong)

**Pass Criteria**: ✅ API connection successful (if key provided)

---

### Test 6: Reports & Export

**Purpose**: Verify reporting functionality

**Steps**:
1. Run a scan (Processes tab)
2. Go to **Reports** tab
3. Click **Refresh Stats**
4. Click **Export HTML**
5. Save report to file

**Expected Results**:
- Statistics displayed (scans, threats, quarantined)
- Recent threats table populated
- HTML file generated successfully
- Report opens in browser

**Pass Criteria**: ✅ Reports generate and export correctly

---

### Test 7: Settings Management

**Purpose**: Test configuration changes

**Steps**:
1. Go to **Settings** tab
2. Add a trusted path:
   - Click **Add Path**
   - Select a directory (e.g., `D:\MyApp\`)
   - Click **Save Settings**
3. Adjust threat threshold (slider)
4. Click **Save Settings**

**Expected Results**:
- Success message: "Settings saved successfully!"
- Changes persist after restart
- New trusted path appears in list

**Pass Criteria**: ✅ Settings save and persist

---

### Test 8: Quarantine Functionality

**Purpose**: Verify file quarantine works

**Prerequisites**: Administrator privileges

**Steps**:
1. Create a test file:
   ```bash
   echo malware > C:\Temp\malware.exe
   ```

2. Manually trigger quarantine (if threat level ≥ 8)

3. Go to **Quarantine** tab

4. Check quarantined files list

**Expected Results**:
- File moved to `quarantine/` folder
- Metadata saved (`.json` file)
- Original file deleted
- Can restore or permanently delete

**Pass Criteria**: ✅ Quarantine isolates files correctly

---

### Test 9: Auto-Scan Feature

**Purpose**: Test periodic scanning

**Steps**:
1. Go to **Settings** tab
2. Enable **Auto-Scan** checkbox
3. Set interval to 1 minute
4. Click **Save Settings**
5. Wait 1 minute

**Expected Results**:
- Scan starts automatically after 1 minute
- Status shows "Last scan: Xm ago"
- Scans repeat every interval

**Pass Criteria**: ✅ Auto-scan runs periodically

---

### Test 10: Error Handling

**Purpose**: Verify graceful degradation

**Steps**:
1. Test without API keys:
   ```bash
   # Remove .env file temporarily
   python production_gui.py
   ```

2. Scan processes

**Expected Results**:
- System works without API keys
- Uses local YARA + Expert System
- No crashes or errors
- Fallback analysis used

**Pass Criteria**: ✅ System works without external dependencies

---

## 🧪 Unit Tests

### Run All Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Open coverage report
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

**Expected Results**:
- 52+ tests passing
- 75%+ code coverage
- No failures or errors

**Test Categories**:
- Configuration (4 tests)
- Detection (10 tests)
- Expert System (8 tests)
- LangGraph (5 tests)
- Multi-Agent (6 tests)
- Resilience (12 tests)
- YARA Scanner (8 tests)

---

## 🎮 Interactive Testing Scenarios

### Scenario 1: Clean System Scan

**Goal**: Verify no false positives on clean system

1. Fresh Windows/Linux installation
2. Only legitimate software installed
3. Run HIDR scan
4. **Expected**: All processes 0-4/10 threat, action: allow

### Scenario 2: Suspicious Activity

**Goal**: Detect suspicious behavior

1. Create process in temp directory
2. Use suspicious name (e.g., `keylogger.exe`)
3. Run HIDR scan
4. **Expected**: 6-8/10 threat, action: terminate_temporary

### Scenario 3: Known Malware Pattern

**Goal**: Detect YARA signature matches

1. File with malware-like strings
2. YARA rules match patterns
3. Run HIDR scan
4. **Expected**: 8-10/10 threat, YARA matches shown

---

## 📊 Performance Testing

### Benchmark Tests

```bash
# Test scan speed
python -c "import time; from simple_multiagent import SimpleMultiAgent; a = SimpleMultiAgent(); start = time.time(); r = a.analyze_process('test.exe', 'C:\\test.exe', '', 1); print(f'Analysis time: {time.time()-start:.2f}s')"
```

**Expected Performance**:
- Trusted path check: < 1ms
- YARA scan: < 100ms
- Expert system: < 50ms
- Total analysis: 2-5 seconds

---

## 🐛 Troubleshooting Tests

### Test 1: Permission Issues

**Problem**: "Access Denied" errors

**Test**:
```bash
# Run without admin
python production_gui.py
```

**Expected**: Warning message about admin privileges

**Solution**: Run as Administrator

### Test 2: Missing Dependencies

**Problem**: Import errors

**Test**:
```bash
python -c "import yara; import psutil; import yaml; print('All dependencies OK')"
```

**Expected**: "All dependencies OK"

**Solution**: `pip install -r requirements.txt`

### Test 3: YARA Rules Not Loading

**Problem**: 0 rules loaded

**Test**:
```bash
python -c "from core.yara_scanner import YaraScanner; s = YaraScanner(); print(f'Rules: {s.rules_count}')"
```

**Expected**: "Rules: 5"

**Solution**: Verify `yara_rules/` folder exists with 5 .yar files

---

## ✅ Test Checklist

Use this checklist to verify all functionality:

- [ ] GUI launches successfully
- [ ] Process scanning works
- [ ] Trusted paths prevent false positives
- [ ] YARA rules load (5 files)
- [ ] Expert system calculates threat scores
- [ ] Reports tab shows statistics
- [ ] Settings tab saves configuration
- [ ] API keys can be configured
- [ ] Quarantine functionality works
- [ ] Auto-scan feature works
- [ ] Unit tests pass (52+ tests)
- [ ] No crashes or errors
- [ ] Performance acceptable (< 5s per process)
- [ ] Documentation is clear

---

## 📧 Reporting Issues

If you find bugs or issues:

1. Check [Troubleshooting Guide](README.md#troubleshooting)
2. Review logs: `logs/hidr.log`
3. Open GitHub issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Log excerpts

---

## 🎓 Learning Exercises

### Exercise 1: Add Custom YARA Rule

1. Create `yara_rules/custom.yar`
2. Add a simple rule
3. Restart HIDR
4. Verify rule loads

### Exercise 2: Modify Threat Thresholds

1. Go to Settings
2. Lower threat threshold to 3
3. Scan system
4. Observe more processes flagged

### Exercise 3: Create Custom Trusted Path

1. Install software in custom location
2. Add path to trusted paths
3. Verify software scores 0/10

---

## 🏆 Success Criteria

Your HIDR system is working correctly if:

✅ All 52+ unit tests pass  
✅ No false positives on legitimate software  
✅ Suspicious processes detected (5-10/10 threat)  
✅ YARA rules load and match patterns  
✅ Reports generate and export  
✅ Settings persist across restarts  
✅ System handles errors gracefully  
✅ Performance is acceptable (< 5s per process)  

---

**Happy Testing! 🛡️**

For questions or issues: secuvortex@gmail.com
