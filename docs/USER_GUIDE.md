# Grace User Guide

## 🎯 Getting Started

### First Launch
1. **Install:** `python grace_cli.py install`
2. **Start:** `python grace_cli.py start`
3. **Login:** Visit http://localhost:5173
4. **Credentials:** `admin` / `admin123` (default)

### Interface Overview
- **💬 Chat** - Converse with Grace
- **💻 IDE** - Write and run code
- **📊 Dashboard** - View metrics and system status
- **📁 Memory** - Browse knowledge base

## 💬 Using Chat

### Basic Conversation
```
You: Hello Grace
Grace: Hello! I'm Grace. How can I help you today?

You: Show me my history
Grace: Here are your last 10 interactions...
```

### Supported Commands
- `hello` / `hi` - Greeting
- `show me my history` - View past conversations
- `how are you` - System status
- `thank you` - Gratitude response

### Autonomous Features
- **Reflections** - Grace observes patterns every 10 seconds
- **Auto-tasks** - Created when topics mentioned 3+ times
- **Causal tracking** - Every interaction logged

## 💻 Using the IDE

### Writing Code
1. Click **💻 IDE** button
2. Monaco editor opens (like VSCode)
3. Write Python code
4. Click **💾 Save** to store in sandbox

### Running Code
1. Write or open a `.py` file
2. Click **▶ Run** button
3. Output appears in console panel
4. Errors trigger auto-fix suggestions

### File Management
- **Left panel:** Browse sandbox files
- **Click file:** Opens in editor
- **Save:** Stores with full audit trail

### Auto-Fix Issues
When errors occur:
1. Issue detected automatically
2. Appears in **⚠️ ISSUES** panel
3. Shows explanation + suggested fix
4. Click **⚡ Apply Fix** button
5. Grace attempts remediation

## 📊 Using the Dashboard

### Metrics Overview
- **Messages:** Total conversations
- **Users:** Active users
- **Interactions:** Logged events
- **Reflections:** Generated insights

### System Monitor
Real-time status of 4 core systems:
- 🟢 **Reflection Loop** - Running/Idle + count
- 🟡 **Learning Engine** - Auto-tasks created
- 🟢 **Causal Tracker** - Events logged
- ⚪ **Confidence Score** - Unhandled rate

### Background Tasks
- View running tasks
- See progress bars (0-100%)
- Track completion status

### Task Lists
- **Auto-generated** (🤖 icon) - Created by Grace
- **Manual** - Created by you
- Filter by status

## 📁 Using Memory Browser

### Navigation
- **File-explorer style** tree view
- Organized by domain/category
- Click items to view

### Viewing Artifacts
- **Content** - Full text/code
- **Metadata** - Domain, category, version
- **Audit Trail** - Complete edit history
- **Hash Verification** - Tamper detection

### Creating Knowledge
```bash
POST /api/memory/items
{
  "path": "security/protocols.md",
  "content": "# Security Protocols\n...",
  "domain": "security",
  "category": "policy"
}
```

## 🔒 Understanding Governance

### What Gets Governed
- Sandbox code execution
- Memory artifact changes
- System mode transitions
- Component restarts
- High-risk operations

### Approval Workflow
1. Action triggered
2. Policy checked
3. If requires review → Approval request created
4. Admin approves/rejects
5. Action executed or blocked
6. All logged immutably

### Viewing Approvals
```bash
GET /api/governance/approvals
```

## 🛡️ Security (Hunter Protocol)

### What Hunter Monitors
- Suspicious code patterns
- Dangerous commands (`rm -rf`, etc.)
- Secret leakage attempts
- Repeated failure patterns

### Alert Handling
1. Hunter detects threat
2. Security event logged
3. Appears in dashboard
4. Can be resolved with notes
5. All actions audited

## ⚕️ Self-Healing

### Automatic Recovery
Grace monitors herself:
- Component health every 30s
- Auto-restart on failure
- Fallback to safe modes
- All healing logged

### System Modes
- **normal** - Full operation
- **read_only** - DB issues (no writes)
- **observation_only** - Monitor but don't act
- **emergency** - Critical lockdown

### Manual Control
```bash
POST /api/health/restart
{"component": "reflection_service"}
```

## 🔄 Meta-Loops Explained

### Level 1: Optimization
- Runs every 5 minutes
- Analyzes task completion rates
- Checks reflection effectiveness
- Recommends improvements

### Level 2: Evaluation
- Measures if optimizations helped
- Tracks before/after metrics
- Detects regressions
- Triggers rollbacks if needed

### Viewing Recommendations
```bash
GET /api/meta/analyses
GET /api/meta/evaluations
```

## 💡 Best Practices

### For Chat
- Be specific in requests
- Use "show me my history" to see past conversations
- Grace learns from repetition (3+ mentions = auto-task)

### For IDE
- Save files before running
- Check console for errors
- Apply auto-fixes when suggested
- Files are governed and audited

### For Memory
- Organize by domain (security, technical, research)
- Add metadata for context
- Check audit trail for changes
- Verify hash chain integrity

### For Security
- Review Hunter alerts regularly
- Approve/reject governance requests promptly
- Check immutable log for suspicious patterns
- Monitor system health

## 🆘 Common Issues

### "Chat request failed"
- **Cause:** Not logged in or token expired
- **Fix:** Logout and login again

### "Sandbox execution blocked"
- **Cause:** Governance policy or Hunter alert
- **Fix:** Check `/api/governance/audit` and `/api/hunter/alerts`

### "Component critical"
- **Cause:** Service failure
- **Fix:** Self-healing will attempt restart, or use `/api/health/restart`

### "Chain verification failed"
- **Cause:** Audit tampering detected
- **Fix:** Check `/api/log/verify` for details

## 📚 Advanced Usage

### Export Knowledge for Training
```bash
POST /api/memory/export
{"domains": ["security", "technical"]}
```

### Create Custom Policies
```bash
POST /api/governance/policies
{
  "name": "Block dangerous commands",
  "condition": "{\"keywords\": [\"rm -rf\"]}",
  "action": "block"
}
```

### Monitor Background Tasks
```bash
GET /api/executor/tasks
GET /api/executor/status/{task_id}
```

Grace is now fully documented and ready to use! 🚀📚
