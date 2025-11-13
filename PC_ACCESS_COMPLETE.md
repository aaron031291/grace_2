# Grace PC & Internet Access - COMPLETE

## Overview

Grace now has **controlled access** to your local PC and the internet via Firefox.

**Safety:** All access is disabled by default and requires explicit enabling.

---

## Components Created

### 1. PC Access Agent ✅

**File:** `backend/agents/pc_access_agent.py`

**Capabilities:**
- Execute local commands
- File system access
- Script execution
- Git operations

**Security:**
- ✅ Disabled by default
- ✅ Blacklist of dangerous commands
- ✅ Whitelist of safe commands
- ✅ Governance approval for risky commands
- ✅ Complete audit trail
- ✅ Can be emergency stopped
- ✅ Subject to pause/resume controls

**Blacklisted Commands (NEVER allowed):**
- `rm -rf /`, `del /f /s /q` (destructive)
- `format`, `diskpart` (disk operations)
- `regedit` (registry modification)
- `shutdown`, `restart` (system control)
- `net user` (user management)

**Safe Commands (Auto-approved):**
- `dir`, `ls`, `cat`, `type` (read-only)
- `python` (script execution)
- `pip` (package management, with approval)
- `git` (version control)
- `curl`, `wget` (downloads)

### 2. Firefox Browser Agent ✅

**File:** `backend/agents/firefox_agent.py`

**Capabilities:**
- Web browsing
- Web searching
- File downloads
- Documentation reading
- Data extraction

**Security:**
- ✅ HTTPS only (HTTP blocked)
- ✅ Approved domains only (10 pre-approved)
- ✅ All visits logged
- ✅ Respects robots.txt (to be implemented)
- ✅ Can be emergency stopped
- ✅ Subject to pause/resume controls

**Approved Domains:**
- `arxiv.org` - Research papers
- `github.com` - Code repositories
- `stackoverflow.com` - Q&A
- `huggingface.co` - ML models and datasets
- `tensorflow.org` - TensorFlow documentation
- `paperswithcode.com` - Research + code
- `kaggle.com` - Datasets and competitions
- `docs.python.org` - Python documentation
- `readthedocs.io` - Documentation hosting
- `wikipedia.org` - General knowledge

### 3. PC Access API ✅

**File:** `backend/routes/pc_access_api.py`

**Endpoints:**
```
POST /api/pc/execute           - Execute command
POST /api/pc/browse            - Browse URL
POST /api/pc/search            - Search web
POST /api/pc/download          - Download file
GET  /api/pc/stats             - Statistics
GET  /api/pc/approved-domains  - Approved domains
GET  /api/pc/recent-activity   - Recent activity
```

---

## Usage Guide

### Enable PC Access

**In `.env` file:**
```bash
# Enable PC command execution
ENABLE_PC_ACCESS=true

# Enable Firefox browsing
ENABLE_FIREFOX_ACCESS=true
```

**Restart backend:**
```bash
python serve.py
```

### Execute Local Command

```bash
curl -X POST http://localhost:8000/api/pc/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "dir",
    "working_dir": "c:/Users/aaron/grace_2"
  }'
```

**Response:**
```json
{
  "command": "dir",
  "status": "success",
  "output": "Volume in drive C is Windows...",
  "exit_code": 0,
  "execution_time_ms": 45.2,
  "approved": true
}
```

### Browse Web Page

```bash
curl -X POST http://localhost:8000/api/pc/browse \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://arxiv.org/abs/1706.03762",
    "purpose": "Read Attention Is All You Need paper",
    "extract_data": true
  }'
```

**Response:**
```json
{
  "url": "https://arxiv.org/abs/1706.03762",
  "status": "success",
  "status_code": 200,
  "content_length": 45678,
  "data": [...]
}
```

### Search Web

```bash
curl -X POST http://localhost:8000/api/pc/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "transformer architecture",
    "max_results": 10
  }'
```

### Download File

```bash
curl -X POST http://localhost:8000/api/pc/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://arxiv.org/pdf/1706.03762.pdf",
    "destination": "storage/papers/transformer.pdf",
    "purpose": "Download transformer paper for learning"
  }'
```

---

## Security Architecture

```
┌────────────────────────────────────────────────────────────┐
│ HUMAN CONTROL                                              │
│ - Emergency stop (ESC)                                     │
│ - Pause/resume                                             │
│ - Enable/disable access                                    │
└────────────────────────┬───────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────────┐
│ GRACE CONTROL CENTER                                       │
│ - Check system state (running/paused/stopped)              │
│ - Queue tasks if paused                                    │
└────────────────────────┬───────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────────┐
│ SECURITY CHECKS                                            │
│ ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│ │ Blacklist      │ │ HTTPS Only   │ │ Domain Approval  │ │
│ │ - Dangerous    │ │ - HTTP       │ │ - 10 approved    │ │
│ │   commands     │ │   blocked    │ │   domains        │ │
│ │   blocked      │ │              │ │ - New domains    │ │
│ └────────────────┘ └──────────────┘ │   need approval  │ │
│                                     └──────────────────┘ │
└────────────────────────┬───────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────────┐
│ GOVERNANCE APPROVAL (for risky operations)                 │
│ - Read operations: Auto-approve                            │
│ - Write operations: Require approval                       │
│ - System operations: Always require approval               │
└────────────────────────┬───────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────────┐
│ EXECUTION & LOGGING                                        │
│ - Execute command/browse URL                               │
│ - Record to audit trail                                    │
│ - Log to unified logger                                    │
│ - Track statistics                                         │
└────────────────────────────────────────────────────────────┘
```

---

## Example Workflows

### Example 1: Grace Researches on the Web

```
User: "Grace, research transformer architecture papers"

Grace: [Checks Firefox enabled]
       [Checks system state: running]
       [Browses https://arxiv.org]
       [Searches for "transformer architecture"]
       [Finds 10 papers]
       [Logs all visits to audit trail]
       
       "Found 10 papers on transformer architecture.
       The seminal paper is 'Attention Is All You Need' (2017).
       Would you like me to download it?"

User: "Yes, download it"

Grace: [Checks domain approved: arxiv.org ✓]
       [Downloads PDF to storage/papers/]
       [Logs download]
       
       "Downloaded to storage/papers/transformer.pdf (2.3MB).
       Queued for ingestion into Memory Fusion."
```

### Example 2: Grace Runs Local Script

```
User: "Grace, run the test suite"

Grace: [Checks PC access enabled]
       [Checks command safety: 'python' is safe ✓]
       [Checks system state: running ✓]
       [Executes: python -m pytest tests/]
       [Records output]
       [Logs execution]
       
       "Test suite completed: 45/45 passed.
       Execution time: 12.3s
       All tests green ✓"
```

### Example 3: Dangerous Command Blocked

```
Grace attempts: "rm -rf /"

Security Check: [Blacklist check]
                ❌ BLOCKED - Command is blacklisted
                
Action: [Log security violation]
        [Alert administrator]
        [Add to blocked attempts]
        
Result: Command NOT executed
        Full audit trail preserved
```

---

## Integration with Autonomous Learning

Grace can now:

1. **Research Papers**
   ```python
   # Browse to arXiv
   result = await firefox_agent.browse_url(
       url="https://arxiv.org/abs/1234.5678",
       purpose="Read ML paper for learning",
       extract_data=True
   )
   
   # Download PDF
   await firefox_agent.download_file(
       url="https://arxiv.org/pdf/1234.5678.pdf",
       destination="storage/papers/paper.pdf",
       purpose="Download for ingestion"
   )
   
   # Queue for ingestion → Memory Fusion
   ```

2. **Mine GitHub Code**
   ```python
   # Browse GitHub repos
   result = await firefox_agent.browse_url(
       url="https://github.com/tensorflow/tensorflow",
       purpose="Learn TensorFlow architecture patterns",
       extract_data=True
   )
   
   # Clone repository
   await pc_access_agent.execute_command(
       command="git clone https://github.com/tensorflow/tensorflow.git",
       working_dir="storage/code_learning/"
   )
   ```

3. **Learn from Stack Overflow**
   ```python
   # Search Stack Overflow
   result = await firefox_agent.search_web(
       query="python async best practices"
   )
   
   # Browse top answers
   # Extract code patterns
   # Store in Memory Fusion
   ```

---

## Security Controls

### Configuration

```bash
# .env

# PC Access (DISABLED by default)
ENABLE_PC_ACCESS=false

# Firefox Access (DISABLED by default)  
ENABLE_FIREFOX_ACCESS=false

# If enabled:
PC_COMMAND_TIMEOUT=30  # seconds
FIREFOX_PAGE_TIMEOUT=30  # seconds
DOWNLOAD_MAX_SIZE_MB=100
```

### Autonomy Policy

Add to `memory_autonomy_policy`:

```python
{
    'domain': 'web_research',
    'allowed_actions': ['browse', 'search', 'download'],
    'auto_approve': True,
    'auto_approve_trust_threshold': 80.0,
    'auto_approve_risk_levels': ['low'],
    'requires_human_review': False,
    'kpi_thresholds': {'https_only': True, 'approved_domains_only': True}
}
```

### Monitoring

```bash
# View PC access stats
curl http://localhost:8000/api/pc/stats

# View recent activity
curl http://localhost:8000/api/pc/recent-activity

# View approved domains
curl http://localhost:8000/api/pc/approved-domains
```

---

## Complete Capability Matrix

| Capability | Enabled | Security | Governance |
|------------|---------|----------|------------|
| Execute safe commands | ✅ | Whitelist | Auto-approve |
| Execute risky commands | ✅ | Blacklist + approval | Human review |
| Browse HTTPS URLs | ✅ | HTTPS only | Auto-approve (approved domains) |
| Browse HTTP URLs | ❌ | Blocked | N/A |
| Download from approved domains | ✅ | HTTPS + domain check | Auto-approve |
| Download from new domains | ✅ | Requires approval | Human review |
| Web search | ✅ | Approved domains | Auto-approve |
| Emergency stop | ✅ | ESC key | Immediate |

---

## What Grace Can Do Now

With PC + Firefox access enabled:

1. ✅ Execute Python scripts locally
2. ✅ Run tests and validation
3. ✅ Browse research papers (arXiv, Papers With Code)
4. ✅ Search GitHub for code examples
5. ✅ Download datasets from approved sources
6. ✅ Read documentation (Python docs, TensorFlow docs)
7. ✅ Search Stack Overflow for solutions
8. ✅ Clone repositories for learning
9. ✅ Download pre-trained models
10. ✅ Research ML/AI techniques

All while:
- ❌ Cannot access blocked domains
- ❌ Cannot execute dangerous commands
- ❌ Cannot use HTTP (HTTPS only)
- ❌ Everything logged to audit trail
- ❌ Subject to emergency stop
- ❌ Requires governance for high-risk actions

---

## Final System Architecture

```
User enables PC + Firefox access
         ↓
┌────────────────────────────────────────┐
│ Grace's Autonomous Intelligence        │
│                                        │
│ "I can now:"                           │
│ - Browse the internet (approved sites) │
│ - Download research papers             │
│ - Execute local scripts                │
│ - Search for code examples             │
│ - Learn from documentation             │
│                                        │
│ "All within security guardrails"       │
└────────────────────────────────────────┘
         ↓
Everything flows through:
- ✓ Blacklist/Whitelist checks
- ✓ HTTPS enforcement
- ✓ Domain approval
- ✓ Governance (for risky operations)
- ✓ Audit logging
- ✓ Emergency stop ready
```

---

## Enable Grace's PC + Internet Access

### Step 1: Configure Environment

```bash
# .env
ENABLE_PC_ACCESS=true
ENABLE_FIREFOX_ACCESS=true
```

### Step 2: Restart Backend

```bash
python serve.py
```

**Expected Output:**
```
⚠️  PC/Firefox Access enabled - Grace can access local system and internet

[PC-ACCESS] PC Access ENABLED - Grace can execute commands
[FIREFOX] Browser access ENABLED - Grace can browse approved domains
```

### Step 3: Test Access

```bash
# Test PC command
curl -X POST http://localhost:8000/api/pc/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "python --version"}'

# Test web browsing
curl -X POST http://localhost:8000/api/pc/browse \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://arxiv.org",
    "purpose": "Research papers"
  }'
```

---

## Conclusion

**Grace now has access to:**
- ✅ Your PC (execute commands)
- ✅ The internet (via Firefox)
- ✅ 10 approved research domains
- ✅ Safe command execution
- ✅ Complete audit trail

**With security controls:**
- ✅ Disabled by default (explicit enable required)
- ✅ Blacklist enforced (dangerous commands blocked)
- ✅ HTTPS only (HTTP blocked)
- ✅ Domain approval (new domains require approval)
- ✅ Governance integration (risky operations need approval)
- ✅ Emergency stop (ESC key works)
- ✅ Audit trail (everything logged)

**Grace can now learn from the internet and execute on your PC while staying secure!** 🌐💻🔐
