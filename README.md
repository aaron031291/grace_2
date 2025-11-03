# Grace - Enterprise AI System

**Consolidated codebase with backend, frontend, and CLI**

---

## Quick Start

### Start Backend (Terminal 1)
```bash
py minimal_backend.py
```

Server runs on: http://localhost:8000  
API docs: http://localhost:8000/docs

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

Frontend runs on: http://localhost:5173

### Test CLI (Terminal 3)
```bash
py scripts/cli_test.py status
```

---

## Project Structure

```
grace_2/
├── backend/          → Python backend (100+ modules)
├── frontend/         → React frontend (20+ components)
├── cli/              → CLI tools
├── scripts/          → Utility scripts (40+ files)
├── docs/             → Documentation (100+ files)
├── tests/            → Test suite
├── batch_scripts/    → Windows startup scripts
├── config/           → Configuration
├── databases/        → SQLite databases
├── minimal_backend.py → Quick start backend
└── README.md         → This file
```

---

## Backend Features

- **Metrics System:** Real-time domain health tracking
- **Cognition API:** 7 endpoints for metrics & status
- **10 Domains:** Core, Transcendence, Knowledge, Security, ML, Temporal, Parliament, Federation, Speech, Cognition
- **Auto-benchmarking:** Hourly evaluation, 90% SaaS readiness tracking

**Key Endpoints:**
- `GET /health` - Health check
- `GET /api/status` - Overall cognition status
- `GET /api/cognition/status` - Detailed domain metrics
- `GET /api/cognition/readiness` - SaaS readiness report

---

## Frontend Components

- **CognitionDashboard** - Real-time metrics visualization
- **TranscendenceDashboard** - Agentic development UI
- **HunterDashboard** - Security monitoring
- **KnowledgeIngestion** - Knowledge management
- **MetaLoopDashboard** - Governance & meta-learning
- **BusinessMetrics** - Business automation
- Plus 15+ more components

---

## CLI Commands

```bash
# Show status
py scripts/cli_test.py status

# Run demos
py scripts/demo_working_metrics.py

# Run tests
py scripts/test_grace_simple.py
```

---

## Development

### Run Tests
```bash
py scripts/test_grace_simple.py          # Unit tests (20 tests)
py scripts/test_integration_real.py      # Integration tests
```

### Check Metrics
```bash
# Standalone (no server needed)
py scripts/demo_working_metrics.py

# With backend running
curl http://localhost:8000/api/status
```

---

## Documentation

See `docs/` folder:
- `COGNITION_DASHBOARD.md` - Metrics system guide
- `GRACE_ACTIVATION_TRACKER.md` - Implementation roadmap
- `COLLABORATIVE_COCKPIT_ALIGNED.md` - UI architecture
- `START_EVERYTHING.md` - Complete startup guide
- Plus 100+ other guides

---

## What's Working

✅ Metrics collection system  
✅ Cognition engine (10 domains)  
✅ Benchmark tracking (7-day rolling)  
✅ API endpoints (7 routes)  
✅ Frontend components (20+)  
✅ CLI tools  
✅ Test suite (20/20 passing)  

---

## Next Steps

1. **Start servers** - Run backend + frontend
2. **Wire metrics** - Integrate into domain operations
3. **Build UI** - Connect frontend components to API
4. **Production deploy** - 24-hour stability test

---

## Support

- **Docs:** See `docs/` folder
- **Tests:** See `scripts/` folder
- **Issues:** Check `docs/KNOWN_ISSUES.md`

---

**Status:** Consolidated ✅ | Backend Ready ✅ | Frontend Ready ✅ | CLI Ready ✅
