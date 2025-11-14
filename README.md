# GRACE - General Recursive Autonomous Cognitive Engine

**Version:** 2.0  
**Status:** Production Ready  
**Last Updated:** November 14, 2025

---

## 🚀 Quick Start

### Start Grace
```bash
python serve.py
```

Or with auto-restart protection:
```bash
scripts\startup\start_grace.cmd
```

### Run Tests
```bash
python tests\e2e\FINAL_COMPLETE_TEST.py
```

### Check Status
```bash
scripts\startup\grace.cmd status
```

---

## 📖 System Overview

Grace is an enterprise-grade autonomous AI system with:

- **12+ Layer 1 Kernels** - Core intelligence components
- **Multi-OS Fabric** - Manages Windows/Linux/macOS hosts
- **Auto-Restart System** - 3-layer resilience
- **Self-Healing** - 17 triggers, 9 automated playbooks
- **HTM Orchestration** - Priority queues with temporal SLAs
- **Event-Driven** - Intelligent routing via message bus

---

## 🏗️ Architecture

```
grace_2/
├── backend/           # Core backend (Python/FastAPI)
├── frontend/          # Web interface (React/TypeScript)
├── docs/              # All documentation
├── scripts/           # Startup, test, utility scripts
├── tests/             # Test suites
├── databases/         # SQLite databases
├── storage/           # File storage
├── logs/              # Runtime logs
└── serve.py           # Main entry point
```

---

## 📚 Documentation

### Essential Reading
- **[START_HERE.md](docs/START_HERE.md)** - Begin here
- **[System Architecture](docs/architecture/FINAL_COMPREHENSIVE_SYSTEM_DOCUMENT.md)** - Complete technical docs
- **[Quick Start Guide](docs/guides/QUICK_START_GUIDE.md)** - Get running fast

### By Category
- **Architecture:** `docs/architecture/` - System design
- **Guides:** `docs/guides/` - How-to documentation
- **Status:** `docs/status/` - Current system state
- **Milestones:** `docs/milestones/` - Progress markers

---

## 🎯 Key Features

### Multi-OS Infrastructure Management
Grace tracks and manages hosts across operating systems:
- Windows, Linux, macOS support
- Dependency detection (pip, npm, conda)
- Resource monitoring (CPU, RAM, GPU, disk)
- OS-specific policy enforcement

### Auto-Restart & Resilience
Three-layer protection keeps Grace running:
- **Layer 1:** Kernel supervision (10s recovery)
- **Layer 2:** Process watchdog (30s recovery)
- **Layer 3:** System service (auto-start on boot)

### Self-Healing Triggers
Proactive monitoring prevents issues:
- Heartbeat failures → Auto-restart
- API timeouts → Service recovery
- Resource spikes → Cleanup/optimization
- Dependency drift → Auto-sync
- Anomalies → Diagnostics

### Hierarchical Task Manager (HTM)
Intelligent task prioritization:
- **CRITICAL** - Prod outages (<5min SLA)
- **HIGH** - Canary failures (<30min SLA)
- **NORMAL** - Daily tasks (<4hr SLA)
- **LOW** - Background jobs (<24hr SLA)

### Learning & Improvement
Grace learns from experience:
- Records successful workflows
- Recommends proven solutions
- Improves response times over time

---

## 🚦 Commands

### Start/Stop
```bash
# Start with watchdog
scripts\startup\start_grace.cmd

# Stop (kill switch)
scripts\startup\stop_grace.cmd

# Restart
scripts\startup\grace.cmd restart

# Status
scripts\startup\grace.cmd status
```

### Testing
```bash
# Quick validation
python tests\e2e\FINAL_COMPLETE_TEST.py

# Full E2E test
python tests\e2e\test_multi_os_fabric_e2e.py

# Diagnostics
python scripts\utilities\DIAGNOSE_BACKEND.py
```

### Deployment
```bash
# Verify system
scripts\deployment\VERIFY_SYSTEM.bat

# PM2 (production)
pm2 start pm2.config.js

# Systemd (Linux)
sudo systemctl start grace
```

---

## 🔧 Configuration

### Environment Variables
Create `.env` from `.env.example`:
```bash
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///databases/grace.db
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### System Requirements
- Python 3.11+
- Node.js 18+
- 8GB+ RAM
- 20GB+ disk space

---

## 📊 System Status

**All Core Systems:**
- [x] Message Bus
- [x] Infrastructure Manager (Multi-OS)
- [x] Governance Kernel
- [x] Memory Kernel
- [x] Enhanced HTM
- [x] Event Policy Kernel
- [x] Self-Healing System
- [x] Auto-Restart System

**Test Status:** 100% Pass Rate ✅  
**Production Ready:** Yes ✅

---

## 📁 Project Structure

### Backend (`backend/`)
- `core/` - Layer 1 kernels and core systems
- `kernels/` - Domain-specific kernels
- `routes/` - API endpoints
- `self_heal/` - Self-healing system
- `middleware/` - Request/response middleware

### Frontend (`frontend/`)
- `src/` - React components
- `public/` - Static assets

### Scripts (`scripts/`)
- `startup/` - Start/stop/control scripts
- `test/` - Test runners
- `deployment/` - Deployment tools
- `utilities/` - Helper scripts

### Tests (`tests/`)
- `e2e/` - End-to-end tests
- `unit/` - Unit tests
- `integration/` - Integration tests

### Docs (`docs/`)
- `architecture/` - System design documents
- `guides/` - How-to guides
- `milestones/` - Progress tracking
- `status/` - Status reports
- `summaries/` - Summary documents

---

## 🔌 API Endpoints

**Backend:** http://localhost:8000

**Key Endpoints:**
- `GET /api/health` - System health
- `POST /api/chat` - Conversational interface
- `GET /api/kernels` - Kernel status
- `POST /api/memory` - Memory operations
- `POST /api/books/ingest` - Book ingestion
- `GET /docs` - API documentation

---

## 🛠️ Development

### Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Run Development Server
```bash
# Backend
python serve.py

# Frontend
cd frontend
npm run dev
```

### Run Tests
```bash
# All tests
pytest tests/

# Specific test
python tests/e2e/FINAL_COMPLETE_TEST.py
```

---

## 📞 Troubleshooting

### Backend Won't Start
```bash
# Check port 8000
netstat -ano | findstr :8000

# Run diagnostics
python scripts\utilities\DIAGNOSE_BACKEND.py

# View logs
type logs\backend.log
```

### Tests Fail
```bash
# Ensure backend is running
python serve.py

# Run validation
python tests\e2e\FINAL_COMPLETE_TEST.py
```

### See Full Guides
Check `docs/guides/` for detailed troubleshooting and setup guides.

---

## 🎯 What Makes Grace Special

### Autonomous
- Self-healing from failures
- Auto-restarts on crashes
- Learns from experience
- Improves over time

### Multi-Platform
- Windows, Linux, macOS support
- Unified host management
- OS-specific policy enforcement

### Resilient
- 3-layer auto-restart
- Survives kernel crashes
- Survives process crashes
- Survives system reboots

### Intelligent
- Priority-based task queuing
- Temporal SLA management
- Health-aware throttling
- Workload-based agent spawning

---

## 📄 License

See LICENSE file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

---

## 📧 Support

- **Documentation:** `docs/`
- **Issues:** GitHub Issues
- **Guides:** `docs/guides/`

---

**Grace is production-ready with enterprise-grade resilience and intelligence!**

*Built with ❤️ for autonomous AI systems*
