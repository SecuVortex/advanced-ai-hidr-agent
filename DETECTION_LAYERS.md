# Multi-Layer Threat Detection System

## 🛡️ Detection Layers (In Order)

### Layer 1: Static Analysis (Name & Location)
**Speed**: Instant  
**Accuracy**: Medium (can be bypassed by renaming)

**Detects:**
- Known malware names (njRAT, DarkComet, etc.)
- Suspicious locations (Temp, Downloads, AppData\Roaming)
- Suspicious command-line flags

**Threat Score**: 0-10 points

---

### Layer 2: Hash-Based Detection (VirusTotal)
**Speed**: 2-15 seconds (with rate limiting)  
**Accuracy**: High (detects known malware regardless of name)

**How it works:**
1. Calculate SHA-256 hash of executable
2. Query VirusTotal database
3. Check detections from 70+ antivirus engines

**Detects:**
- Known malware (even if renamed)
- Variants of existing threats
- Recently discovered threats

**Threat Score**: 0-10 points (based on AV detections)

---

### Layer 3: Behavioral Analysis (Real-time)
**Speed**: 0.1-1 second  
**Accuracy**: High (detects zero-day threats)

**Monitors:**
1. **Network Activity**
   - Active connections (RAT indicator)
   - External IPs contacted
   - +2 points per connection

2. **Resource Usage**
   - High CPU (crypto-miner indicator)
   - High memory usage
   - +1-2 points

3. **Process Behavior**
   - Child processes (injection)
   - Open files (ransomware)
   - +1-2 points

4. **Command Line**
   - Hidden execution flags
   - PowerShell code execution
   - +3 points

5. **Parent Process**
   - Suspicious parent (cmd.exe, powershell.exe)
   - +2 points

**Threat Score**: 0-10 points

---

## 🎯 Combined Threat Scoring

**Total Threat = Static Score + Behavioral Score**

### Actions Based on Total Score:

| Total Score | Action | Description |
|------------|--------|-------------|
| 12+ | **TERMINATE (Permanent)** | Critical threat - immediate kill |
| 8-11 | **TERMINATE (Temporary)** | High threat - kill and monitor |
| 5-7 | **MONITOR** | Suspicious - watch closely |
| 0-4 | **ALLOW** | Safe - normal execution |

---

## 📊 Example Scenarios

### Scenario 1: Renamed RAT
- **Name**: `update.exe` (0 points - looks normal)
- **VirusTotal**: 45/70 detections (9 points)
- **Behavior**: Active network connections (2 points)
- **Total**: 11 points → **TERMINATE**

### Scenario 2: Crypto Miner
- **Name**: `svchost.exe` (0 points - mimics system)
- **VirusTotal**: Not in database (0 points)
- **Behavior**: 95% CPU + high memory (4 points)
- **Total**: 4 points → **ALLOW** (but flagged for monitoring)

### Scenario 3: Known Ransomware
- **Name**: `encryptor.exe` (8 points)
- **VirusTotal**: 60/70 detections (10 points)
- **Behavior**: 50 open files (2 points)
- **Total**: 20 points → **TERMINATE (Permanent)**

---

## 🔍 Why Multiple Layers?

1. **Name-based**: Fast first filter
2. **Hash-based**: Catches known threats (even renamed)
3. **Behavioral**: Catches zero-day and polymorphic malware

**Result**: Comprehensive protection that's hard to bypass!

---

## 🚀 Test Your System

```bash
python test_final.py
```

Watch how all 3 layers work together to detect threats!
