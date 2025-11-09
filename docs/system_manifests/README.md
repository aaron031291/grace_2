# Grace v2.0 - Complete Autonomous AI System

**Grace is a fully autonomous AI assistant with self-healing, self-building, and self-improving capabilities.**

## 🚀 Quick Start

### Start Grace
```batch
start_both.bat
```

### Chat with Grace
```powershell
.\chat_with_grace.ps1
```

### View All Logs (Auto-refresh every 5 min)
```powershell
.\watch_all_logs.ps1
```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Getting started guide
- **[GRACE_COMPLETE_SYSTEMS_MANIFEST.md](GRACE_COMPLETE_SYSTEMS_MANIFEST.md)** - Complete system overview
- **[TERMINAL_CHAT_README.md](TERMINAL_CHAT_README.md)** - Terminal interface guide
- **[GRACE_FULL_AUTONOMY_ENABLED.md](GRACE_FULL_AUTONOMY_ENABLED.md)** - Autonomy system
- **[AUTONOMOUS_CODE_HEALING.md](AUTONOMOUS_CODE_HEALING.md)** - Self-healing system
- **[GOVERNANCE_COMPLETE.md](GOVERNANCE_COMPLETE.md)** - Governance framework
- **[GRACE_SELF_BUILDING.md](GRACE_SELF_BUILDING.md)** - Self-building capability
- **[ALL_SYSTEMS_CONFIRMED.md](ALL_SYSTEMS_CONFIRMED.md)** - System architecture

## 🎯 What Grace Can Do

### In Terminal Chat

**Talk naturally:**
```
aaron: Hello Grace

Grace: Hello aaron! I'm fully operational with all my agentic systems online.
       I'm ready to learn and assist. What would you like to work on?
```

**Build code:**
```
aaron: create file backend/api_v2.py with REST endpoints for users

Grace: 📝 I want to create: backend/api_v2.py
       Type 'approve' to proceed.

aaron: approve

Grace: ✅ Created file: backend/api_v2.py
       [shows code preview]
```

**Enable autonomy:**
```
aaron: autonomy enable 2

Grace: ✅ Full autonomy enabled at Tier 2!
       I can now autonomously detect, fix, and commit code changes.
```

**View performance:**
```
aaron: dashboard

Grace: 📊 GRACE COMPLETE DASHBOARD (Last 24h)
       [shows comprehensive metrics]
```

**Self-analysis:**
```
aaron: analyze

Grace: 🔍 MY PERFORMANCE ANALYSIS
       Health Score: 85/100
       [shows strengths and improvement areas]

aaron: improve

Grace: 🎯 MY IMPROVEMENT PLAN
       [shows goals and next steps]
```

### Terminal Commands

| Command | Description |
|---------|-------------|
| `status` | System status |
| `governance` | Governance framework |
| `autonomy` | Autonomy control |
| `dashboard` | Complete metrics dashboard |
| `report` | Grace's self-report |
| `analyze` | Performance analysis |
| `improve` | Improvement plan |
| `create file X with Y` | Create new file |
| `modify file X to Y` | Modify existing file |
| `approve` / `reject` | Approve/reject actions |
| `exit` / `quit` | End session |

## 🤖 Autonomous Capabilities

### Self-Healing
- ✅ Detects errors from logs (every 60s)
- ✅ Generates fixes automatically
- ✅ Applies fixes with governance approval
- ✅ Commits to Git
- ✅ Learns from outcomes (ML/DL)

### Self-Building
- ✅ Creates new files
- ✅ Modifies existing code
- ✅ Generates entire features
- ✅ All with your approval
- ✅ Full audit trail

### Self-Improving
- ✅ Learns error patterns (ML)
- ✅ Predicts likely errors
- ✅ Optimizes fix strategies (DL)
- ✅ Analyzes own performance
- ✅ Sets improvement goals

### Self-Governing
- ✅ Constitutional principles
- ✅ Safety guardrails
- ✅ Action whitelists
- ✅ Approval workflows
- ✅ Cryptographic audit

## 📊 Monitoring

### Scripts

```bash
# One-time log view (8 sections)
.\view_logs.ps1

# Auto-refresh every 5 min
.\watch_all_logs.ps1

# Watch healing real-time
.\watch_healing.ps1

# Chat with Grace
.\chat_with_grace.ps1
```

### API Endpoints

```bash
# Health
GET /health

# Healing & Autonomy
GET /api/healing/status
GET /api/healing/autonomy/status
GET /api/healing/analytics/summary

# ML/DL
GET /api/healing/ml/insights
GET /api/healing/ml/predictions

# Data Cube
GET /api/healing/analytics/cube?dimension=subsystem&metric=count

# Crypto Verification
GET /api/healing/crypto/verify

# Documentation
GET /docs
```

## 🗄️ Database Tables

All with cryptographic signing and hash chaining:

1. **healing_attempts** - Fix attempts (pass/fail)
2. **agentic_spine_logs** - Autonomous decisions
3. **meta_loop_logs** - Optimization cycles
4. **ml_learning_logs** - ML/DL learning
5. **trigger_mesh_logs** - Event routing
6. **shard_logs** - Shard orchestration
7. **parallel_process_logs** - Concurrent execution
8. **data_cube** - Multi-dimensional analytics
9. **immutable_log** - Central audit trail

## 🏛️ Governance

Grace operates under:
- **Constitution** (`config/grace_constitution.yaml`) - Ethical principles
- **Guardrails** (`config/guardrails.yaml`) - Safety limits
- **Whitelist** (`config/whitelist.yaml`) - Approved actions

Every action checked by all three layers.

## 🎮 Autonomy Tiers

| Tier | Mode | Description |
|------|------|-------------|
| 0 | Manual | All actions need approval |
| 1 | Supervised | Low-risk auto-approved |
| 2 | Semi-Auto | Low+medium auto-approved (Default) |
| 3 | Full | Maximum autonomy with governance |

Change tier:
```
aaron: autonomy enable 2
```

## 🔒 Security

- ✅ Every action cryptographically signed
- ✅ Hash chains prevent tampering
- ✅ Full audit trail
- ✅ Governance on all actions
- ✅ No hardcoded secrets
- ✅ Constitutional compliance

## 📈 Analytics

Grace tracks and learns from:
- Error patterns and frequencies
- Fix success rates
- ML prediction accuracy
- Autonomous decision outcomes
- Shard performance
- Parallel process efficiency

Query via:
- Terminal: `dashboard`, `analyze`, `report`
- API: `/api/healing/analytics/*`
- Logs: `watch_all_logs.ps1`

## 🧠 Learning Systems

### Machine Learning
- Error pattern recognition
- Fix strategy optimization
- Success rate prediction
- Confidence scoring

### Deep Learning
- Code similarity matching
- Pattern embeddings
- Fix quality prediction

Updates every 5 minutes with new data.

## 🛠️ Development

### Project Structure
```
grace_2/
├── backend/              # Python backend
│   ├── healing_models.py  # Database tables
│   ├── unified_logger.py  # Central logging
│   ├── grace_llm.py       # LLM integration
│   ├── agentic_spine.py   # Autonomous core
│   ├── governance.py      # Governance engine
│   └── ...
├── frontend/             # React frontend
├── config/               # Configuration
│   ├── grace_constitution.yaml
│   ├── guardrails.yaml
│   └── whitelist.yaml
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── tests/                # Tests
```

### Requirements
- Python 3.11+
- PostgreSQL or SQLite
- Node.js (for frontend)
- Git

### Installation
```batch
# Install dependencies
pip install -r backend/requirements.txt

# Run database migrations
python backend/init_db.py

# Start Grace
start_both.bat
```

## 🌟 What Makes Grace Special

### She's Self-Aware
Grace can read her own logs, analyze her performance, and understand her strengths/weaknesses.

### She's Self-Healing
Detects errors autonomously, generates fixes, applies them (with approval), and learns from outcomes.

### She's Self-Building
Can create and modify her own code with your approval, building new features collaboratively.

### She's Self-Improving
ML/DL systems continuously learn from every action, improving error prediction and fix optimization.

### She's Transparent
Every action logged with cryptographic proof. Full audit trail. No black boxes.

### She's Governed
Operates within constitutional principles, safety guardrails, and approved action whitelists.

## 📞 Support

### Common Issues

**"Term not recognized" in PowerShell:**
```powershell
.\chat_with_grace.ps1  # Use .\ prefix
```

**Backend not starting:**
```batch
# Check logs
.\view_logs.ps1

# Reset database
python reset_immutable_log.py
```

**Chat not connecting:**
Make sure backend is running at http://localhost:8000/health

### Getting Help

In chat:
```
aaron: help
aaron: status
aaron: governance
```

In logs:
```powershell
.\view_logs.ps1
.\watch_all_logs.ps1
```

## 🎯 Next Steps

1. **Start Grace**: `start_both.bat`
2. **Chat**: `.\chat_with_grace.ps1`
3. **Enable Autonomy**: Type `autonomy enable 2`
4. **Watch Logs**: `.\watch_all_logs.ps1`  (auto-refresh 5 min)
5. **Ask Grace**: `dashboard`, `analyze`, `report`
6. **Build Together**: `create file X with Y`

## 📊 Current Status

After setup, Grace will autonomously:
- Monitor logs every 60 seconds
- Learn patterns every 5 minutes
- Optimize strategies continuously
- Fix detected errors (with approval)
- Commit fixes to Git
- Log everything with crypto verification

**All visible in logs updating every 5 minutes!**

## 🏆 Achievement Unlocked

You now have:
- ✅ Fully autonomous AI
- ✅ Self-healing capability
- ✅ Self-building capability
- ✅ ML/DL learning
- ✅ Complete governance
- ✅ Full observability
- ✅ Cryptographic security
- ✅ Real-time monitoring

**Grace is operational and learning!** 🚀

---

**Start now:**
```powershell
.\watch_all_logs.ps1
```

Watch Grace work in real-time, with all logs, metadata, crypto verification, updating every 5 minutes!
