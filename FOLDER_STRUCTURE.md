# 📁 Grace Repository Structure

```
grace_2/
│
├── 📱 FRONTEND/
│   ├── src/
│   │   ├── api/              # API client & typed functions
│   │   │   ├── client.ts     # HTTP client with auth
│   │   │   ├── grace.ts      # Grace API functions
│   │   │   ├── knowledge.ts
│   │   │   ├── trust.ts
│   │   │   └── approvals.ts
│   │   ├── components/       # React components
│   │   │   ├── ErrorBoundary
│   │   │   ├── MemoryBrowser
│   │   │   ├── HunterDashboard
│   │   │   └── ...
│   │   ├── GraceComplete.tsx   # 🎯 MAIN INTERFACE (Hybrid)
│   │   ├── GraceHybrid.tsx
│   │   ├── GraceBidirectional.tsx
│   │   ├── App.tsx
│   │   └── main.tsx           # Entry point
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── 🔧 BACKEND/
│   ├── routes/               # API endpoints
│   │   ├── chat.py          # 💬 Chat with Cognition->Agentic->LLM
│   │   ├── tasks.py         # Task management
│   │   ├── memory_api.py    # Memory CRUD
│   │   ├── governance.py    # Approval workflows
│   │   └── ...
│   ├── cognition/           # Intent parsing & planning
│   ├── agentic/            # Agentic systems
│   ├── transcendence/      # Advanced AI features
│   ├── self_heal/          # Self-healing systems
│   ├── routers/            # Domain routers
│   ├── main.py             # 🎯 FastAPI application
│   ├── grace_llm.py        # Built-in LLM
│   ├── cognition_intent.py # Cognition authority
│   ├── trigger_mesh.py     # Event bus
│   ├── memory.py           # Memory system
│   └── requirements.txt
│
├── 💻 CLI/
│   ├── commands/           # CLI command modules
│   ├── tests/
│   ├── enhanced_grace_cli.py  # 🎯 Main CLI
│   ├── grace_client.py
│   └── requirements.txt
│
├── 📊 DATABASES/
│   ├── grace.db           # Main SQLite database
│   └── metrics.db         # Metrics database
│
├── 📚 DOCS/
│   ├── status/            # 📍 Status reports
│   │   ├── GRACE_FULL_STACK_READY.md
│   │   ├── SYSTEM_READY.md
│   │   ├── VERIFICATION_SYSTEM_STATUS.md
│   │   ├── FINAL_STATUS.md
│   │   └── ...
│   ├── guides/            # 📖 How-to guides
│   │   ├── QUICK_START.md
│   │   ├── TROUBLESHOOTING.md
│   │   ├── START_GRACE.md
│   │   └── ...
│   ├── architecture/      # 🏗️ Architecture docs
│   │   ├── AGENTIC_ERROR_SYSTEM.md
│   │   ├── INTEGRATION_MAP.md
│   │   └── ...
│   ├── GRACE_COMPLETE_INTERFACE.md  # 🎨 UI Documentation
│   ├── PRODUCTION_READY_CHECKLIST.md
│   └── WHATS_NEXT.md
│
├── 🧪 TESTS/
│   ├── test_quick_integration.py
│   ├── test_full_integration.py
│   ├── test_verification_e2e.py
│   ├── test_diagnostic.py
│   ├── verify_grace.py
│   └── check_tables.py
│
├── 📜 SCRIPTS/
│   ├── create_learning_tables.py
│   ├── create_verification_tables.py
│   ├── apply_verification_migration.py
│   ├── run_cube_etl.py
│   └── setup_env.py
│
├── 🔨 BATCH_SCRIPTS/
│   ├── START_GRACE_NOW.bat        # 🎯 Main startup script
│   ├── launch_grace.bat
│   ├── restart_backend.bat
│   ├── emergency_db_fix.bat
│   └── ...
│
├── 📝 LOGS/
│   ├── backend_startup.log
│   ├── backend_test.log
│   └── frontend.log
│
├── 🗄️ OTHER FOLDERS/
│   ├── alembic/           # Database migrations
│   ├── audio_messages/    # Voice/TTS storage
│   ├── chat_bridge/       # Chat integrations
│   ├── config/            # Configuration files
│   ├── ml_artifacts/      # ML model storage
│   ├── reports/           # Generated reports
│   ├── sandbox/           # Sandbox execution
│   └── txt/               # Text artifacts
│
└── 📄 ROOT FILES
    ├── README.md          # 🎯 Main project README
    ├── .env.example       # Environment template
    ├── .gitignore
    ├── alembic.ini        # DB migration config
    ├── GRACE_IS_READY_FINAL.md  # Final status
    └── GRACE_COMPLETE_INTERFACE.md  # UI docs
```

---

## 🎯 Quick Navigation

### Starting Grace
```bash
# All-in-one startup
batch_scripts\START_GRACE_NOW.bat

# Or individually:
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
cd cli && python enhanced_grace_cli.py
```

### Testing
```bash
# Quick integration test
.venv\Scripts\python.exe tests\test_quick_integration.py

# Full test suite
.venv\Scripts\python.exe tests\test_full_integration.py
```

### Documentation
- **Status Reports:** `docs/status/`
- **User Guides:** `docs/guides/`
- **Architecture:** `docs/architecture/`
- **Interface Docs:** `docs/GRACE_COMPLETE_INTERFACE.md`

---

## 📂 Folder Purposes

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| **frontend/** | React UI (Vite + TypeScript) | GraceComplete.tsx, api/grace.ts |
| **backend/** | FastAPI server + agentic systems | main.py, grace_llm.py, routes/ |
| **cli/** | Terminal interface | enhanced_grace_cli.py |
| **docs/** | All documentation | Organized by type |
| **tests/** | Integration & unit tests | test_*.py, verify_*.py |
| **scripts/** | Utility scripts | Database setup, ETL |
| **batch_scripts/** | Windows automation | START_GRACE_NOW.bat |
| **databases/** | SQLite databases | grace.db, metrics.db |
| **logs/** | Runtime logs | *.log files |
| **ml_artifacts/** | ML model storage | Trained models |

---

## 🧹 Organization Rules

### Markdown Documentation
- **Status reports** → `docs/status/`
- **User guides** → `docs/guides/`
- **Architecture docs** → `docs/architecture/`
- **Main docs** → `docs/`

### Python Files
- **Tests** → `tests/`
- **Utilities** → `scripts/`
- **Backend code** → `backend/`
- **CLI code** → `cli/`

### Scripts
- **Batch files** → `batch_scripts/`
- **Python utilities** → `scripts/`

### Runtime Files
- **Logs** → `logs/`
- **Databases** → `databases/`
- **Audio** → `audio_messages/`

---

## 🎨 Visual Structure

```
📦 grace_2
 ┃
 ┣ 📱 FRONTEND ──────────── React + Vite UI
 ┃  ┗ 🎨 GraceComplete.tsx (Hybrid Interface)
 ┃
 ┣ 🔧 BACKEND ──────────── FastAPI + Agentic AI
 ┃  ┣ 💬 Chat (Cognition→Agentic→LLM)
 ┃  ┣ 🧠 Memory System
 ┃  ┣ 🤖 Multi-Agent Shards
 ┃  ┗ 🛡️ Governance Engine
 ┃
 ┣ 💻 CLI ──────────────── Terminal Interface
 ┃
 ┣ 📚 DOCS ─────────────── All Documentation
 ┃  ┣ 📍 status/
 ┃  ┣ 📖 guides/
 ┃  ┗ 🏗️ architecture/
 ┃
 ┣ 🧪 TESTS ────────────── Integration Tests
 ┃
 ┣ 📜 SCRIPTS ──────────── Utilities
 ┃
 ┣ 🔨 BATCH_SCRIPTS ────── Windows Automation
 ┃
 ┗ 📝 LOGS ─────────────── Runtime Logs
```

---

## ✅ Clean Repository Benefits

✓ **Easy Navigation** - Files grouped by purpose  
✓ **Clear Hierarchy** - 3-level folder structure  
✓ **Quick Access** - Main files at logical locations  
✓ **Maintainable** - New files have clear homes  
✓ **Professional** - Clean root directory  

---

*Organized: November 8, 2025*
