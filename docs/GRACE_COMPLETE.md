# Grace - Complete Autonomous AI System

## 🎯 Overview

Grace is a fully autonomous AI system with:
- Self-governance and policy enforcement
- Self-healing and health monitoring  
- Security threat detection (Hunter Protocol)
- Issue detection and auto-remediation
- Parallel task execution with progress tracking
- Safe code sandbox environment
- Complete audit trail

## 🏗️ Architecture

### Core Intelligence Systems
1. **GraceAutonomous** - Rule-based conversational AI
2. **Reflection Loop** - Pattern analysis (10s interval)
3. **Learning Engine** - Auto-task generation from patterns
4. **Causal Tracker** - Cause/effect relationship mapping
5. **Confidence Evaluator** - Response quality scoring

### Safety & Governance
6. **Governance Engine** - Policy-based access control
7. **Hunter Protocol** - Security threat detection
8. **Self-Healing** - Component health monitoring
9. **Audit Logging** - Complete action trail
10. **Approval Workflow** - High-risk action review

### Execution & Remediation
11. **Task Executor** - 3 parallel workers with progress tracking
12. **Sandbox Manager** - Safe code execution environment
13. **Remedy Inference** - Auto-fix error suggestions
14. **Issue Tracking** - Problem detection and resolution

## 📊 Complete API Reference

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get JWT token

### Chat & Memory
- `POST /api/chat/` - Send message
- `GET /api/memory/history` - Conversation history
- `GET /api/memory/stats` - Usage statistics

### Intelligence
- `GET /api/reflections/` - Grace's observations
- `POST /api/reflections/trigger` - Force reflection
- `GET /api/causal/patterns` - Interaction patterns
- `GET /api/evaluation/confidence` - Confidence scores

### Task Management
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `PATCH /api/tasks/{id}` - Update task

### Execution
- `POST /api/executor/submit` - Submit background task
- `GET /api/executor/status/{id}` - Task progress
- `GET /api/executor/tasks` - List execution tasks

### Sandbox (IDE)
- `GET /api/sandbox/files` - List sandbox files
- `GET /api/sandbox/file` - Read file
- `POST /api/sandbox/write` - Write file
- `POST /api/sandbox/run` - Execute command (governed)
- `POST /api/sandbox/reset` - Clear sandbox

### Governance
- `GET /api/governance/policies` - List policies
- `POST /api/governance/policies` - Create policy
- `GET /api/governance/audit` - Audit log
- `GET /api/governance/approvals` - Approval requests
- `POST /api/governance/approvals/{id}/decision` - Approve/reject

### Security (Hunter)
- `GET /api/hunter/alerts` - Security alerts
- `POST /api/hunter/alerts/{id}/resolve` - Resolve alert
- `GET /api/hunter/rules` - Security rules

### Health & Healing
- `GET /api/health/status` - Component health checks

### Issue Resolution
- `GET /api/issues/` - List detected issues
- `GET /api/issues/{id}` - Issue details with fix
- `POST /api/issues/{id}/resolve` - Apply/dismiss fix

### Knowledge & Goals
- `POST /api/knowledge/ingest` - Add knowledge
- `POST /api/knowledge/search` - Search knowledge
- `GET /api/goals/` - List goals
- `POST /api/goals/` - Create goal

### Summaries & Metrics
- `GET /api/summaries/` - Daily/weekly summaries
- `GET /api/metrics/summary` - Overall statistics

## 🔄 Autonomous Loops

### Main Loop (Every 10 seconds)
```
Reflection Service:
  → Analyze last hour of messages
  → Identify frequent topics
  → Generate insights
  → Trigger Learning Engine
  → Run Confidence Evaluator
  → Log to reflections table
```

### Learning Loop (Triggered by reflections)
```
Learning Engine:
  → Receive topic + frequency
  → If threshold met (3+ mentions)
  → Create autonomous task
  → Log to tasks table
  → Print confirmation
```

### Health Loop (Every 60 seconds)
```
Health Monitor:
  → Check reflection service
  → Check database latency
  → Check task executor workers
  → Log health checks
  → Attempt self-healing if needed
```

### Governance Check (On critical actions)
```
Every sandbox run / sensitive operation:
  → Check governance policies
  → Log to audit trail
  → Create approval request if needed
  → Run Hunter security scan
  → Allow/Block/Review decision
```

### Issue Detection (On errors)
```
When sandbox fails:
  → Analyze error (NameError, ModuleNotFound, etc.)
  → Generate explanation + fix
  → Log to issue_reports
  → Surface in UI with action button
  → User clicks → Apply fix
```

## 🗄️ Database Schema

### Core Tables
- **users** - Authentication
- **chat_messages** - Conversations
- **reflections** - Grace's observations
- **tasks** - Action items
- **goals** - User objectives
- **causal_events** - Interaction cause/effect

### Execution Tables
- **execution_tasks** - Background task queue
- **sandbox_runs** - Code execution logs
- **sandbox_files** - File change tracking

### Governance Tables
- **governance_policies** - Access control rules
- **audit_log** - Complete action trail
- **approval_requests** - Human-in-loop decisions
- **security_events** - Hunter alerts
- **security_rules** - Threat detection rules
- **health_checks** - Component status
- **healing_actions** - Self-repair attempts

### Issue Resolution
- **issue_reports** - Detected problems + suggested fixes

### Knowledge
- **knowledge_base** - Ingested information
- **summaries** - Periodic reports

## 🎨 Frontend

### Routes
- `/` - Chat interface
- `/dashboard` - Analytics & monitoring

### Features
- Real-time chat with Grace
- Live metrics dashboard
- System monitor (4 processes)
- Background task progress bars
- Reflections display
- Auto-generated tasks
- Toast notifications

## 🧪 Testing

```bash
pytest tests/ -v --cov=backend
```

## 🚀 Quick Start

### 1. Start Backend
```bash
cd grace_rebuild
py -m uvicorn backend.main:app --reload
```

### 2. Start Frontend
```bash
cd grace-frontend  
npm run dev
```

### 3. Reset Database (if needed)
```bash
py reset_db.py
```

## 💡 Example Workflows

### Create a Governance Policy
```bash
curl -X POST http://localhost:8000/api/governance/policies \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "name": "Block dangerous commands",
    "severity": "critical",
    "condition": "{\"keywords\": [\"rm -rf\", \"delete\"]}",
    "action": "block"
  }'
```

### Run Sandboxed Code
```bash
curl -X POST http://localhost:8000/api/sandbox/run \
  -H "Authorization: Bearer TOKEN" \
  -d '{"command": "python test.py"}'
```

### Get Auto-Fix Suggestions
```bash
# Trigger an error
curl -X POST http://localhost:8000/api/sandbox/run \
  -H "Authorization: Bearer TOKEN" \
  -d '{"command": "python -c \"print(undefined_var)\""}'

# Get the issue with fix
curl http://localhost:8000/api/issues/ \
  -H "Authorization: Bearer TOKEN"
```

## 🔐 Security Features

### Governance
- Policy-based decisions (allow/block/review)
- Approval workflow for sensitive actions
- Complete audit trail
- Severity levels (low/medium/high/critical)

### Hunter Protocol
- Keyword-based threat detection
- Forbidden path blocking
- Security event logging
- Alert resolution workflow

### Self-Healing
- Automatic component health checks
- Restart attempts on failure
- Healing action logging
- Component status API

## 🎯 Autonomous Capabilities

Grace can:
1. ✅ **Observe** - Monitor conversations and code execution
2. ✅ **Reflect** - Identify patterns every 10 seconds
3. ✅ **Learn** - Create tasks from repeated topics
4. ✅ **Execute** - Run background jobs in parallel
5. ✅ **Govern** - Enforce policies automatically
6. ✅ **Detect** - Find security threats
7. ✅ **Heal** - Monitor and repair components
8. ✅ **Fix** - Suggest and apply error remedies
9. ✅ **Track** - Log cause/effect relationships
10. ✅ **Evaluate** - Score own performance

## 🔮 What's Next

### Phase 1: IDE Integration
- Monaco code editor
- File tree browser
- Live console output
- Integrated issue fixes

### Phase 2: Advanced Intelligence
- LLM integration for smarter responses
- Vector search for semantic memory
- Multi-step causal reasoning
- Goal-based planning

### Phase 3: Production Deployment
- Docker containerization
- PostgreSQL migration
- WebSocket real-time updates
- Email/Slack notifications
- Multi-user support

Grace is now the most advanced autonomous AI system with complete governance, security, self-healing, and auto-remediation! 🚀🛡️⚕️
