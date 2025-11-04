# Grace - Autonomous AI System

**Version:** 0.5.0 (Transcendence)  
**Status:** Production-Ready  
**License:** MIT

## 🚀 What is Grace?

Grace is a fully autonomous AI system with self-governance, self-healing, and complete auditability. Unlike traditional AI assistants, Grace actively monitors herself, learns from patterns, enforces security policies, and can heal failures automatically.

## ✨ Key Features

### 🤖 Autonomous Intelligence
- **Self-observation** - Monitors all conversations and actions
- **Self-reflection** - Identifies patterns every 10 seconds
- **Self-learning** - Auto-creates tasks from repeated topics
- **Self-optimization** - Meta-loops improve own performance
- **Self-healing** - Repairs component failures automatically

### 🔒 Enterprise Security
- **Governance Engine** - Policy-based access control
- **Hunter Protocol** - Real-time threat detection
- **Immutable Audit Log** - Tamper-proof hash-chained history
- **Approval Workflows** - Human-in-loop for critical actions
- **Complete Forensics** - Every action traced and logged

### 💻 Transcendence IDE
- **Monaco Editor** - VSCode-quality code editing
- **Multi-language Support** - Python, JavaScript, TypeScript, Bash
- **Live Execution** - Run code with real-time output
- **Auto-Fix** - One-click error remediation
- **Security Scanning** - Static analysis on every file

### 📚 Knowledge Management
- **Multi-format Ingestion** - Text, PDF, URLs, images, audio, video
- **File-explorer Interface** - Browse like your filesystem
- **Version History** - Complete edit trail
- **Deduplication** - Hash-based duplicate detection
- **Governed Access** - All operations policy-checked

## 📦 Quick Start

```bash
# Install
python grace_cli.py install

# Start all services
python grace_cli.py start

# Access Grace
open http://localhost:5173
```

**Default credentials:** `admin` / `admin123`

## 🏗️ Architecture

```
User Interface (React + Monaco)
    ↓
API Gateway (FastAPI + WebSocket)
    ↓
Trigger Mesh (Event Bus)
    ↓
┌─────────────┬──────────────┬─────────────┐
│   Memory    │ Immutable Log│  Subsystems │
│ (Workspace) │(Ground Truth)│  (20+)      │
└─────────────┴──────────────┴─────────────┘
```

## 🎯 Core Subsystems

1. **Chat & Memory** - Persistent conversations
2. **Reflection Loop** - Pattern analysis (10s)
3. **Learning Engine** - Auto-task generation
4. **Causal Tracker** - Cause/effect mapping
5. **Governance** - Policy enforcement
6. **Hunter** - Threat detection
7. **Self-Healing** - Component monitoring
8. **Meta-Loops** - Self-optimization (Level 1 & 2)
9. **Trigger Mesh** - Event distribution
10. **Immutable Log** - Forensic audit trail
11. **Task Executor** - 3 parallel workers
12. **Sandbox** - Safe code execution
13. **Remedy Engine** - Auto-fix suggestions
14. **MLDL** - ML lifecycle tracking
15. **AVN/AVM** - Integrity verification
16. **Knowledge Ingestion** - Multi-format learning
17. **WebSocket** - Real-time updates
18. **Plugin System** - Extensible architecture

## 📊 Interface

### 💬 Chat
Talk with Grace, view history, see reflections

### 💻 IDE (Transcendence)
- Write code in Monaco
- Execute safely in sandbox
- Get auto-fix suggestions
- Security scanning

### 📊 Dashboard
- Real-time metrics
- System monitor
- Background tasks
- Reflections & insights

### 📁 Memory Browser
- File-explorer view
- Complete audit trails
- Hash verification
- Version history

### 🛡️ Hunter
- Security alerts
- Active rules
- Resolve/ignore workflow

## 🔐 Security

- JWT authentication
- Policy-based governance
- Threat detection (Hunter)
- Immutable audit log
- Approval workflows
- Hash-chain verification
- Static code analysis
- Secret detection

## 📚 Documentation

- [INSTALL.md](INSTALL.md) - Installation guide
- [USER_GUIDE.md](USER_GUIDE.md) - How to use Grace
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [META_LOOPS.md](META_LOOPS.md) - Self-optimization
- [SELF_HEALING.md](SELF_HEALING.md) - Auto-repair
- [GRACE_IDE.md](GRACE_IDE.md) - IDE architecture
- [PRODUCTION.md](PRODUCTION.md) - Deployment guide
- [SECURITY_SECRETS_INVENTORY.md](SECURITY_SECRETS_INVENTORY.md) - Secrets & credentials catalog
- [HARDENING_COMPLETE.md](HARDENING_COMPLETE.md) - System status

## 🧪 Testing

```bash
# Run test suite
pytest tests/ -v

# Specific tests
pytest tests/test_chat.py -v
pytest tests/test_self_healing.py -v
```

## 🔄 Development

```bash
# Backend
uvicorn backend.main:app --reload

# Frontend
cd grace-frontend && npm run dev

# Seed knowledge
python seed_knowledge.py

# Seed security rules
python seed_security_rules.py
```

## 📡 API Reference

### Core Endpoints
- Auth: `/api/auth/*`
- Chat: `/api/chat/`
- Memory: `/api/memory/*`
- Tasks: `/api/tasks/*`

### Intelligence
- Reflections: `/api/reflections/*`
- Causal: `/api/causal/patterns`
- Meta-loops: `/api/meta/*`

### Security
- Governance: `/api/governance/*`
- Hunter: `/api/hunter/*`
- Health: `/api/health/*`

### IDE
- Sandbox: `/api/sandbox/*`
- Execution: `/api/executor/*`
- Issues: `/api/issues/*`

### Knowledge
- Ingest: `/api/ingest/*`
- Export: `/api/memory/export`

**Full API docs:** http://localhost:8000/docs

## 🌟 What Makes Grace Unique

1. **Fully Autonomous** - Observes, learns, acts without prompting
2. **Self-Governing** - Enforces own policies
3. **Self-Healing** - Repairs failures automatically
4. **Completely Auditable** - Immutable tamper-proof logs
5. **No Vendor Lock-in** - Self-hosted, open architecture
6. **Production-Ready** - Enterprise security & governance

## 🎯 Use Cases

- Autonomous code execution & testing
- Self-governing AI research
- Secure sandboxed development
- Knowledge base management
- Automated task orchestration
- AI safety research
- Self-optimizing systems

## 📈 Roadmap

- **v0.6:** LLM integration, vector search
- **v0.7:** PostgreSQL, Redis, WebSocket enhancements
- **v0.8:** Level 3 meta-loops (self-architecture)
- **v1.0:** Full public release

## 💡 Support

- **GitHub:** [Repository URL]
- **Docs:** http://localhost:8000/docs
- **Issues:** [Issues URL]

## 📄 License

MIT License - See LICENSE file

---

**Grace - The future of autonomous AI is here.** 🚀🤖

*Built with FastAPI, React, Monaco, SQLAlchemy, and a vision for truly autonomous systems.*
