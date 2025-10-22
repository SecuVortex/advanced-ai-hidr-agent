# 🏗️ Multi-Agent HIDR System Architecture

## System Overview

The Multi-Agent HIDR System is built on a **collaborative multi-agent architecture** where specialized agents work together to detect, analyze, and respond to security threats.

---

## 🎯 Design Principles

1. **Separation of Concerns** - Each agent has a single, well-defined responsibility
2. **Loose Coupling** - Agents communicate through messages, not direct calls
3. **Scalability** - New agents can be added without modifying existing ones
4. **Observability** - All agent communication is logged and traceable
5. **Human-Centric** - Critical decisions involve human judgment

---

## 🤖 Agent Architecture

### Base Agent Class

All agents inherit from `BaseAgent`:

```python
class BaseAgent(ABC):
    def __init__(self, name: str, role: str)
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]
    
    def send_message(self, to_agent: str, message: str, data: Dict)
    def log_info(self, message: str)
    def get_messages(self) -> List[Dict]
```

### Agent Specializations

#### 1. DetectionAgent
**Role:** Threat Detection Specialist

**Responsibilities:**
- Heuristic analysis of processes and files
- Behavioral pattern matching
- Threat level calculation (0-10 scale)
- Initial threat classification

**Tools Used:**
- SecurityTools (hash calculation, path analysis)
- ProcessTools (process information)

**Output:**
```python
{
    "threat_level": 7,
    "is_suspicious": True,
    "reasons": ["Launched from temp", "Malicious name pattern"],
    "recommendation": "terminate_permanent"
}
```

#### 2. IntelligenceAgent
**Role:** Threat Intelligence Specialist

**Responsibilities:**
- Query external threat databases (VirusTotal)
- Calculate reputation scores
- Identify known malware
- Provide threat context

**Tools Used:**
- VirusTotalTool (API integration)

**Output:**
```python
{
    "virustotal": {
        "malicious": 45,
        "suspicious": 12,
        "harmless": 3
    },
    "threat_score": 8.5,
    "is_known_malware": True,
    "recommendation": "quarantine"
}
```

#### 3. AnalystAgent
**Role:** Security Analyst (AI-Powered)

**Responsibilities:**
- AI-powered threat analysis using LLMs
- Natural language explanations
- Severity rating
- Actionable recommendations

**Tools Used:**
- LLMTools (Gemini/ChatGPT/Mistral)

**Output:**
```python
{
    "summary": "This is ransomware based on...",
    "severity": "Critical",
    "user_explanation": "Detailed explanation for humans",
    "recommendations": ["Terminate immediately", "Scan system"]
}
```

#### 4. CoordinatorAgent
**Role:** Multi-Agent Coordinator

**Responsibilities:**
- Workflow orchestration
- Priority calculation
- Conflict resolution between agent recommendations
- Determine if human approval is needed

**Output:**
```python
{
    "priority": "Critical",
    "recommended_action": "terminate_permanent",
    "requires_human_approval": True,
    "coordination_notes": "Multiple indicators confirm threat"
}
```

#### 5. ResponseAgent
**Role:** Incident Response Specialist

**Responsibilities:**
- Execute security actions
- Process termination (temporary/permanent)
- File quarantine
- Action logging

**Tools Used:**
- ProcessTools (terminate, kill, suspend)
- FileTools (quarantine, backup, restore)

**Output:**
```python
{
    "action": "terminate_permanent",
    "success": True,
    "message": "Process terminated and quarantined",
    "quarantine_path": "C:\\quarantine\\malware.exe.123456.quar"
}
```

---

## 🔄 Workflow Orchestration (LangGraph)

### State Machine

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   DETECT    │ ◄── DetectionAgent analyzes threat
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ INTELLIGENCE│ ◄── IntelligenceAgent queries VirusTotal
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ANALYZE   │ ◄── AnalystAgent provides AI analysis
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ COORDINATE  │ ◄── CoordinatorAgent determines priority
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   HUMAN     │ ◄── Human approval (if required)
│  APPROVAL   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   RESPOND   │ ◄── ResponseAgent executes action
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     END     │
└─────────────┘
```

### State Definition

```python
class AgentState(TypedDict):
    event_type: str                    # "process" or "file"
    target: Dict[str, Any]             # Target information
    detection_result: Dict[str, Any]   # Detection output
    intelligence_result: Dict[str, Any] # Intelligence output
    analysis_result: Dict[str, Any]    # Analysis output
    coordination_result: Dict[str, Any] # Coordination output
    response_result: Dict[str, Any]    # Response output
    final_action: str                  # Final action taken
    messages: list                     # Agent communication log
    human_decision: Dict[str, Any]     # Human decision
    workflow_start_time: float         # Performance tracking
    workflow_end_time: float
```

---

## 📨 Communication Protocol

### Message Structure

```python
{
    "from_agent": "DetectionAgent",
    "to_agent": "IntelligenceAgent",
    "message": "Suspicious process detected! Threat level: 7/10",
    "data": {
        "threat_level": 7,
        "reasons": ["Temp directory", "Malicious name"]
    },
    "timestamp": 1234567890.123
}
```

### Communication Flow

1. **DetectionAgent → IntelligenceAgent**
   - "Suspicious process detected" or "Normal process detected"

2. **IntelligenceAgent → AnalystAgent**
   - "Confirmed malware" or "Threat score: X/10"

3. **AnalystAgent → CoordinatorAgent**
   - "Analysis complete - Severity: X"

4. **CoordinatorAgent → Human/ResponseAgent**
   - "Priority: X, Recommended action: Y"

5. **Human → ResponseAgent** (if approval required)
   - "User chose: ALLOW/TERMINATE/MONITOR"

6. **ResponseAgent → System**
   - "Action completed: Success/Failure"

---

## 🛠️ Tool Architecture

### Tool Categories

1. **Security Tools** (`security_tools.py`)
   - File hash calculation
   - Path analysis
   - Name pattern matching
   - Threat score calculation

2. **File Tools** (`file_tools.py`)
   - Quarantine operations
   - Backup/restore
   - File information retrieval

3. **Process Tools** (`process_tools.py`)
   - Process information
   - Termination (graceful/force)
   - Suspend/resume
   - Child process management

4. **VirusTotal Tool** (`virustotal_tool.py`)
   - API integration
   - Hash reputation queries
   - Reputation score calculation

5. **LLM Tools** (`llm_tools.py`)
   - Multi-provider support (Gemini/OpenAI/Mistral)
   - Threat analysis
   - Natural language generation
   - Severity determination

---

## 🔐 Security Architecture

### API Key Management

```
.env (gitignored)
    ↓
Config.py (loads environment)
    ↓
Tools (use Config for keys)
```

### Quarantine System

```
Original File → Detection → Quarantine Directory
                              ↓
                    filename.timestamp.quar
                              ↓
                    Secure isolation
```

### Privilege Management

- **Read Operations** - Standard user privileges
- **Write Operations** - Administrator required
- **Process Termination** - Administrator required
- **Quarantine** - Administrator required

---

## 📊 Data Flow

### Process Analysis Flow

```
User/System
    ↓
MultiAgentHIDR.analyze_process()
    ↓
Orchestrator.process_event()
    ↓
┌─────────────────────────────────┐
│ LangGraph Workflow              │
│                                 │
│ 1. DetectionAgent               │
│    ├─ Heuristic analysis        │
│    └─ Threat scoring            │
│                                 │
│ 2. IntelligenceAgent            │
│    ├─ VirusTotal query          │
│    └─ Reputation analysis       │
│                                 │
│ 3. AnalystAgent                 │
│    ├─ LLM analysis              │
│    └─ Explanation generation    │
│                                 │
│ 4. CoordinatorAgent             │
│    ├─ Priority calculation      │
│    └─ Action recommendation     │
│                                 │
│ 5. Human Approval (optional)    │
│    ├─ Display AI explanation    │
│    └─ Get user decision         │
│                                 │
│ 6. ResponseAgent                │
│    ├─ Execute action            │
│    └─ Log results               │
└─────────────────────────────────┘
    ↓
Final State (with all results)
    ↓
User/System
```

---

## ⚡ Performance Considerations

### Optimization Strategies

1. **Parallel Execution** - Independent operations run concurrently
2. **Caching** - VirusTotal results cached temporarily
3. **Lazy Loading** - LLM initialized only when needed
4. **Timeout Management** - API calls have configurable timeouts
5. **Resource Limits** - Process operations have timeout limits

### Performance Metrics

- **Average Workflow Time** - ~2-5 seconds
- **Detection Time** - < 100ms
- **VirusTotal Query** - ~1-2 seconds
- **LLM Analysis** - ~1-3 seconds
- **Response Execution** - < 500ms

---

## 🔄 Extensibility

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement `analyze()` method
3. Add to orchestrator workflow
4. Update state definition if needed

```python
class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="NewAgent", role="New Role")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        return result
```

### Adding New Tools

1. Create tool class in `tools/`
2. Implement tool methods
3. Add to agent's tool collection
4. Update documentation

```python
class NewTool:
    @staticmethod
    def new_operation(param: str) -> Dict:
        # Implementation
        return result
```

---

## 🧪 Testing Architecture

### Test Levels

1. **Unit Tests** - Individual agent/tool testing
2. **Integration Tests** - Agent collaboration testing
3. **End-to-End Tests** - Complete workflow testing
4. **Performance Tests** - Execution time benchmarks

### Mock Strategy

- **External APIs** - Mocked (VirusTotal, LLM)
- **System Operations** - Mocked (process termination)
- **File Operations** - Temporary test directories

---

## 📈 Monitoring & Observability

### Logging Levels

- **INFO** - Normal operations
- **WARNING** - Suspicious activity detected
- **ERROR** - Operation failures

### Metrics Collected

- Workflow execution count
- Priority distribution
- Action distribution
- Execution times
- Agent communication patterns

---

## 🎯 Design Patterns Used

1. **Strategy Pattern** - Different LLM providers
2. **Observer Pattern** - Agent message passing
3. **State Machine** - LangGraph workflow
4. **Factory Pattern** - LLM initialization
5. **Template Method** - Base agent class

---

## 🔮 Future Enhancements

1. **Machine Learning** - Adaptive threat scoring
2. **Distributed Agents** - Multi-system deployment
3. **Real-time Dashboard** - Web-based monitoring
4. **Threat Hunting** - Proactive threat search
5. **Integration APIs** - SIEM/SOAR integration

---

**Last Updated:** 2024
**Version:** 2.0.0
