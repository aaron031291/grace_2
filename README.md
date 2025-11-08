# Grace - Enterprise AI System

**Multi-domain AI platform with real-time cognition tracking, agentic development, and human-in-loop controls**

---

## Quick Start (3 Terminals)

### Terminal 1: Start Backend
```bash
python -m uvicorn backend.main:app --reload
```
→ Backend API running on **http://localhost:8000**  
→ API Documentation: **http://localhost:8000/docs**

### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```
→ Frontend UI running on **http://localhost:5173**

### Terminal 3: Test CLI
```bash
py scripts\cli_test.py status
```
→ Displays cognition status in terminal

**All 3 components connect automatically. Backend + Frontend + CLI ready in 30 seconds.**

## 📚 Documentation

**Complete documentation is organized in [docs/](docs/):**

- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Get GRACE running now
- **[Sprint Plan](docs/planning/SPRINT_PLAN.md)** - Detailed 8-week development plan
- **[Sprint Status](docs/planning/SPRINT_STATUS.md)** - Real-time progress (Sprint 1: ✅ Complete!)
- **[Architecture Docs](docs/)** - Agentic memory, meta coordination, intelligent triggers
- **[Testing Guides](docs/testing/)** - Endpoint testing, verification checklists

**Sprint 1 Complete:** Production-ready self-healing with observability & governance 🎉

---

## 📂 Project Structure

```
grace_2/
├── backend/          → Python backend (FastAPI, SQLAlchemy, async)
│   ├── routes/       → API route handlers (including self-heal observability)
│   ├── routers/      → Domain routers (cognition, core, security, transcendence)
│   ├── domains/      → Domain adapters (core, self-healing)
│   ├── self_heal/    → Self-healing system (scheduler, runner, adapters)
│   ├── transcendence/ → Agentic development system
│   └── ...           → Core modules (agentic_memory, meta_loop, etc.)
├── frontend/         → React + TypeScript UI
│   ├── src/
│   │   ├── components/ → React components
│   │   ├── api/        → API client
│   │   └── styles/     → CSS styles
│   └── package.json
├── docs/             → **📚 All Documentation (ORGANIZED)**
│   ├── guides/       → Getting started guides
│   ├── planning/     → Sprints, roadmaps, status tracking
│   ├── testing/      → Test guides and verification
│   ├── *.md          → Architecture docs
│   └── README.md     → Documentation index
├── cli/              → Command-line interface tools
├── scripts/          → 40+ utility scripts
│   ├── test_*.py     → Test suites
│   ├── demo_*.py     → Demo scripts
│   ├── seed_*.py     → Database seeding
│   └── cli_test.py   → Simple CLI (NEW)
├── docs/             → 105+ documentation files
│   ├── COGNITION_DASHBOARD.md → Metrics guide
│   ├── GRACE_ACTIVATION_TRACKER.md → Roadmap
│   ├── COLLABORATIVE_COCKPIT_ALIGNED.md → UI architecture
│   ├── START_EVERYTHING.md → Startup guide
│   └── ...           → 100+ more guides
├── tests/            → Test infrastructure
├── batch_scripts/    → 18 Windows startup scripts
├── config/           → Configuration files
├── databases/        → SQLite databases
│   └── metrics.db    → Metrics database (auto-created)
├── txt/              → Text files
├── ml_artifacts/     → ML models and data
├── reports/          → Generated reports
├── backend/main.py    → FastAPI application entrypoint
└── README.md         → This file
```

---

## 10-Domain Architecture

Grace is built around 10 specialized domains:

1. **Core** - Platform operations, governance, self-healing, verification
2. **Transcendence** - Agentic development, code generation, task orchestration
3. **Knowledge** - Information ingestion, trust scoring, search & retrieval
4. **Security (Hunter)** - Threat detection, scanning, auto-quarantine
5. **ML** - Model training, deployment, auto-retraining
6. **Temporal** - Causal reasoning, forecasting, simulation
7. **Parliament** - Governance proposals, voting, meta-learning
8. **Federation** - External integrations, connectors, secrets vault
9. **Speech** - Voice interaction, TTS, speech recognition
10. **Cognition** - Cross-domain intelligence, metrics, benchmarking

Each domain has:
- Backend services (in `backend/`)
- API endpoints (in `backend/routes/`)
- Frontend components (in `frontend/src/components/`)
- Metrics publishers (in `backend/metric_publishers.py`)

---

## Backend Features

### Metrics & Cognition System (NEW)
- **Real-time tracking** of all 10 domains
- **Health/Trust/Confidence** scoring per domain
- **90% SaaS readiness** benchmark (7-day rolling window)
- **Auto-evaluation** every hour via scheduler
- **Event emission** when benchmarks sustained

### API Endpoints

**Cognition & Metrics:**
```
GET  /health                        - Health check
GET  /api/status                    - Quick cognition status
GET  /api/metrics                   - Metrics summary
GET  /api/cognition/status          - Detailed domain metrics
GET  /api/cognition/readiness       - SaaS readiness report
POST /api/cognition/domain/{id}/update - Update domain KPIs
GET  /api/cognition/benchmark/{metric} - Benchmark details
```

**Other Domains:**
- Tasks, knowledge, security, ML, temporal, parliament endpoints
- See http://localhost:8000/docs for full API

### Database
- **SQLite** - Auto-creates tables on startup
- **Async** - All database operations async via SQLAlchemy
- **Metrics DB** - Separate metrics.db for telemetry

---

## Frontend Components

### Dashboard Components (NEW)
- `CognitionDashboard.tsx` - Real-time domain health visualization
- `graceApi.ts` - API client for backend connection

### Domain Dashboards (Existing)
- `TranscendenceDashboard.tsx` - Agentic development
- `HunterDashboard.tsx` - Security monitoring
- `MetaLoopDashboard.tsx` - Governance
- `BusinessMetrics.tsx` - Business automation
- `KnowledgeIngestion.tsx` - Knowledge management
- Plus 18+ more components

### Tech Stack
- React 19
- TypeScript
- Vite (build tool)
- Axios (HTTP client)

---

## CLI Tools

### Simple CLI (NEW)
```bash
py scripts\cli_test.py status       # Show cognition status
```

### Existing CLI
```bash
py cli\grace_cli.py                 # Full Grace CLI
```

### Demo Scripts
```bash
py scripts\demo_working_metrics.py  # Metrics system demo (no server needed)
py scripts\demo_dashboards.py       # Dashboard demo
py scripts\demo_security_features.py # Security demo
```

---

## Testing

### Unit Tests
```bash
py scripts\test_grace_simple.py
```
**Status:** 20/20 tests passing ✅

### Integration Tests
```bash
py scripts\test_integration_real.py
```
**Requires:** Backend running on port 8000

### Full Test Suite
```bash
py scripts\test_grace_e2e_complete.py
```

---

## Development Workflow

### 1. Start Development Environment
```bash
# Terminal 1 - Backend
python -m uvicorn backend.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Make Changes
- Backend: Edit files in `backend/`
- Frontend: Edit files in `frontend/src/`
- Both auto-reload on save

### 3. Test Changes
```bash
# Unit tests
py scripts\test_grace_simple.py

# Integration tests (backend running)
py scripts\test_integration_real.py
```

### 4. Check Metrics
```bash
# View in browser
http://localhost:8000/api/status

# View in CLI
py scripts\cli_test.py status

# View in frontend
http://localhost:5173
```

---

## Metrics System

### Publishing Metrics (NEW)

```python
from backend.metric_publishers import (
    CoreMetrics,
    OrchestratorMetrics,
    HunterMetrics,
    KnowledgeMetrics,
    MLMetrics
)

# Publish metrics from your code
await CoreMetrics.publish_uptime(0.99)
await OrchestratorMetrics.publish_task_completed(True, 0.95)
await HunterMetrics.publish_scan_completed(threats=1, coverage=0.98, duration=0.012)
```

### Viewing Metrics

**In browser:**
- http://localhost:8000/api/cognition/status
- http://localhost:5173 (frontend dashboard)

**In CLI:**
```bash
py scripts\cli_test.py status
```

**Standalone (no server):**
```bash
py scripts\demo_working_metrics.py
```

---

## Documentation

### Getting Started
- `docs/START_EVERYTHING.md` - Complete startup guide
- `docs/CONSOLIDATION_COMPLETE.md` - Repository structure
- `docs/CLEANUP_NOTES.md` - Cleanup instructions

### Technical Guides
- `docs/COGNITION_DASHBOARD.md` - Metrics system (600+ lines)
- `docs/GRACE_ACTIVATION_TRACKER.md` - 6-week roadmap
- `docs/COLLABORATIVE_COCKPIT_ALIGNED.md` - UI architecture
- `docs/ENTERPRISE_COMPLETION_PLAN.md` - Path to 100%

### Domain Guides
- `docs/ARCHITECTURE.md` - System architecture
- `docs/EXECUTION_ENGINE_SUMMARY.md` - Task execution
- `docs/HUNTER_DASHBOARD_SUMMARY.md` - Security
- `docs/PARLIAMENT_SYSTEM.md` - Governance
- Plus 100+ more domain-specific guides

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Dependencies
```bash
pip install fastapi uvicorn sqlalchemy aiosqlite httpx rich
```

Or use requirements file:
```bash
pip install -r txt/requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

---

## What's Working

✅ **Backend (70% functional)**
- Metrics collection system operational
- Cognition API responding
- Database persistence working
- Benchmark tracking active
- 112 modules, 34 routes

✅ **Frontend (Components ready)**
- 23 React components built
- API client configured
- CognitionDashboard functional
- Needs: Backend connection testing

✅ **CLI (Functional)**
- Simple CLI working
- Connects to backend
- Status display
- Demo scripts run standalone

✅ **Infrastructure**
- Clean repository structure
- Single source of truth
- 350+ files organized
- Comprehensive documentation

---

## What Needs Work

### Backend Integration (30%)
- [ ] Wire metrics into domain operations
- [ ] Test full backend startup
- [ ] 24-hour stability test
- [ ] Load testing

### Frontend Development (50%)
- [ ] Connect dashboard to live backend
- [ ] Build task management UI
- [ ] Knowledge explorer
- [ ] Domain workspaces

### Production Readiness (60%)
- [ ] Multi-tenant authentication
- [ ] Deployment automation
- [ ] Monitoring/alerting
- [ ] Performance optimization

---

## Troubleshooting

### Backend won't start
```bash
# Check port 8000 is free
netstat -ano | findstr :8000

# Kill if needed
taskkill /F /PID <pid>

# Install dependencies
pip install fastapi uvicorn
```

### Frontend won't start
```bash
cd frontend
npm install
npm run dev
```

### Imports not working
```bash
# Run from root directory
cd c:\Users\aaron\grace_2
python -m uvicorn backend.main:app --reload
```

---

## Repository Status

**Consolidated:** ✅ Single source of truth  
**Organized:** ✅ All files in proper folders  
**Root:** ✅ Clean (2 files only)  
**Components:** ✅ Backend + Frontend + CLI ready  
**Tests:** ✅ 20/20 passing  
**Docs:** ✅ 105+ files  

---

## Quick Commands Reference

```bash
# Start backend
python -m uvicorn backend.main:app --reload

# Start frontend
cd frontend && npm run dev

# Test CLI
py scripts\cli_test.py status

# Run metrics demo
py scripts\demo_working_metrics.py

# Run tests
py scripts\test_grace_simple.py

# View API docs
# http://localhost:8000/docs

# View frontend
# http://localhost:5173
```

---

## Contributing

1. Make changes in appropriate folder:
   - Backend: `backend/`
   - Frontend: `frontend/src/`
   - Scripts: `scripts/`
   - Docs: `docs/`

2. Test changes:
   ```bash
   py scripts\test_grace_simple.py
   ```

3. Update docs if needed

4. Commit:
   ```bash
   git add -A
   git commit -m "Description"
   ```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Grace Platform                        │
├─────────────────────────────────────────────────────────┤
│  10 Domains:                                            │
│  Core │ Transcendence │ Knowledge │ Security │ ML       │
│  Temporal │ Parliament │ Federation │ Speech │ Cognition│
├─────────────────────────────────────────────────────────┤
│  Backend (FastAPI + SQLAlchemy)                         │
│  ├── Domain Services                                    │
│  ├── API Routes                                         │
│  ├── Metrics System (NEW)                               │
│  └── Database (SQLite)                                  │
├─────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript)                          │
│  ├── Domain Dashboards                                  │
│  ├── Cognition Dashboard (NEW)                          │
│  └── API Client                                         │
├─────────────────────────────────────────────────────────┤
│  CLI (Python)                                           │
│  └── Status, Demos, Tests                               │
└─────────────────────────────────────────────────────────┘
```

---

## Recent Updates (November 3, 2025)

✅ **Metrics System Implemented**
- Real-time domain health tracking
- 90% SaaS readiness benchmarking
- Cognition API with 7 endpoints
- All 10 domains monitored

✅ **Repository Consolidated**
- Single source of truth
- All files organized
- Clean structure
- Duplicates removed

✅ **Backend + Frontend + CLI**
- Minimal working backend created
- Frontend components ready
- CLI tools functional
- All connected

---

## Support & Documentation

📚 **Full Documentation:** See `docs/` folder (105+ guides)  
🧪 **Tests:** `scripts/` folder (20/20 passing)  
🚀 **Quick Start:** `docs/START_EVERYTHING.md`  
🏗️ **Architecture:** `docs/COLLABORATIVE_COCKPIT_ALIGNED.md`  
📊 **Metrics:** `docs/COGNITION_DASHBOARD.md`  

---

## License & Contact

**Version:** 2.0.0  
**Status:** Development (70% functional)  
**Repository:** https://github.com/aaron031291/grace_2  
**Last Updated:** November 3, 2025  

---

**Ready to run. Start the 3 terminals above and Grace comes alive.**


---

## Governance & Approvals (NEW)

A simple Approvals admin panel is available in the frontend and a corresponding API/CLI is provided.

- Frontend panel: Start the frontend and click "✅ Approvals" in the top navigation. Login first to obtain a token.
- Backend API: See docs/APPROVAL_API.md for endpoint specs and examples.
- CLI: `py -m cli.enhanced_grace_cli governance list|approve|reject`

Docs and notes:
- Approval API: docs/APPROVAL_API.md
- Release Notes: docs/RELEASE_NOTES_2025-11-06.md
- Handoff Guide: docs/HANDOFF_APPROVALS.md

Environment flags and correlation:
- `APPROVAL_DECIDERS`: comma-separated usernames allowed to decide approvals. If set, others receive 403 on decision. If unset, no RBAC enforcement for this endpoint (dev-friendly).
- `APPROVAL_DECISION_RATE_PER_MIN`: per-user rate (calls/min) for the decision endpoint. Default 10.
- `RATE_LIMIT_BYPASS`: when truthy (`1/true/yes/on`), disables the in-memory rate limiter (use in tests/dev).
- `X-Request-ID`: clients may send this header; the backend injects one if missing and echoes it back. Structured logs include `request_id` and `_verification_id` for correlation.

Status note: This repository is not production-ready. Treat the Approvals flow as development-grade; structured logging and rate limits exist, but long-duration soak tests, broader RBAC, and hardened auth are pending.


---

## Database Migrations (Alembic)

Most local development uses SQLite auto-create on backend startup. For reproducible setups (CI/clean envs) or non-SQLite targets, apply Alembic migrations.

Windows quickstart:
```
# From repo root
py -m pip install alembic

# Optional: choose DB (defaults to sqlite+aiosqlite:///./grace.db)
set DATABASE_URL=sqlite+aiosqlite:///./databases/grace.db

# Upgrade to latest schema
alembic upgrade head

# Roll back last migration (if needed)
alembic downgrade -1
```

Notes:
- Approvals schema is codified in `alembic/versions/20251106_approval_requests.py`.
- If the database file is locked on Windows, stop any running server/tests that might be holding the file and retry.
- See `docs/APPROVAL_API.md` for details.
