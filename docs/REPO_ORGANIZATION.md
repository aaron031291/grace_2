# Repository Organization Plan

## New Folder Structure

```
grace_2/
├── backend/               # Core backend code (KEEP AS IS)
│   ├── core/
│   ├── kernels/
│   ├── routes/
│   └── ...
│
├── frontend/             # Frontend code (KEEP AS IS)
│
├── docs/                 # ALL DOCUMENTATION (NEW)
│   ├── architecture/     # System architecture docs
│   ├── guides/          # How-to guides
│   ├── milestones/      # Progress markers (*_COMPLETE.md)
│   ├── status/          # Status reports (*_STATUS.md, *_READY.md)
│   └── summaries/       # Summary documents (*_SUMMARY.md)
│
├── scripts/             # ALL SCRIPTS (NEW)
│   ├── startup/         # Start/stop scripts
│   ├── test/            # Test runners
│   ├── deployment/      # Deployment helpers
│   └── utilities/       # Utility scripts
│
├── tests/               # ALL TEST FILES (REORGANIZED)
│   ├── e2e/            # End-to-end tests
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
│
├── logs/                # Log files (EXISTS)
├── databases/           # Database files (EXISTS)
├── storage/             # Storage (EXISTS)
│
├── .archived/           # REDUNDANT/OLD FILES (NEW)
│   ├── old_logs/
│   └── deprecated_docs/
│
├── README.md            # Main README (UPDATED)
├── .env.example         # Environment template
└── .gitignore           # Git ignore
```

## Files to Move

### Documentation (*.md) - Move to docs/

**Milestones (docs/milestones/):**
- ALL_12_KERNELS_COMPLETE.md
- AUTO_PIPELINE_COMPLETE.md
- AUTO_RESTART_COMPLETE.md
- AUTONOMOUS_LEARNING_COMPLETE.md
- BOOK_SYSTEM_READY.md
- BOOKS_COMPLETE_READY.md
- CODING_AGENT_STATUS.md
- COMPLETE_RESILIENCE_SYSTEM.md
- DRAG_DROP_COMPLETE.md
- ELEVATED_HTM_COMPLETE.md
- GRACE_COMPLETE_FINAL.md
- INTEGRATED_SYSTEM_READY.md
- LAYER1_COMPLETE_README.md
- LIBRARIAN_KERNEL_COMPLETE.md
- LIBRARIAN_PRODUCTION_READY.md
- MEMORY_FUSION_STYLE_COMPLETE.md
- MEMORY_PANEL_COMPLETE.md
- MEMORY_WORKSPACE_COMPLETE.md
- ML_AI_INTEGRATION_COMPLETE.md
- MODEL_REGISTRY_COMPLETE.md
- MULTI_OS_FABRIC_COMPLETE.md
- PC_ACCESS_COMPLETE.md
- REMOTE_ACCESS_COMPLETE.md
- SELF_HEALING_INTEGRATED.md
- SELF_HEALING_TRIGGERS_COMPLETE.md
- UNBREAKABLE_CORE_COMPLETE.md
- UNBREAKABLE_GRACE_COMPLETE.md
- UX_IMPROVEMENTS_COMPLETE.md

**Status Reports (docs/status/):**
- ALL_FEATURES_INTEGRATED.md
- ALL_SYSTEMS_COMPLETE.md
- COMPLETE_LIBRARY_STATUS.md
- COMPLETE_SYSTEM_STATUS.md
- COMPREHENSIVE_API_STATUS.md
- SYSTEM_READY.md
- TESTS_READY.md

**Summaries (docs/summaries/):**
- COMPLETE_INTEGRATION_SUMMARY.md
- FINAL_SUMMARY.md
- LAYER1_COMPLETION_SUMMARY.md
- LIBRARIAN_FINAL_SUMMARY.md
- LOGS_SUMMARY.md
- TODAY_IMPLEMENTATION_SUMMARY.md

**Guides (docs/guides/):**
- BOOK_INGESTION_GUIDE.md
- CONCURRENT_PROCESSING_GUIDE.md
- DEMO_FLOW_GUIDE.md
- DEMO_WALKTHROUGH.md
- DRAG_DROP_GUIDE.md
- DRAG_DROP_TEST.md
- INTEGRATION_GUIDE.md
- MEMORY_PANEL_SETUP.md
- PRODUCTION_DEPLOYMENT_GUIDE.md
- QUICK_INTEGRATION_GUIDE.md
- QUICK_START_DEMO.md
- QUICK_START_GUIDE.md
- UPLOAD_BOOKS_GUIDE.md

**Architecture (docs/architecture/):**
- BUSINESS_INTELLIGENCE_LIBRARY.md
- CLEAN_ARCHITECTURE_FINAL.md
- COMPREHENSIVE_API_COMPLETE.md
- COMPREHENSIVE_SYSTEM_COMPLETE.md
- FINAL_COMPREHENSIVE_SYSTEM_DOCUMENT.md
- GRACE_LLM_ARCHITECTURE.md
- INGESTION_LLM_LEARNING_INTEGRATION.md

**Keep in Root:**
- README.md (main)
- START_HERE.md
- DO_THIS_NOW.md (if still relevant)

### Scripts (*.bat, *.cmd, *.ps1) - Move to scripts/

**Startup (scripts/startup/):**
- START_BACKEND.bat
- START_FRONTEND.bat
- START_GRACE_AND_WATCH.bat
- START_GRACE_CLEAN.bat
- START_GRACE_COMPLETE.bat
- START_HERE.bat
- START_LAYER1_MULTI_OS.bat
- START_WITH_LOGS.bat
- LAYER1_COMPLETE_STARTUP.bat
- RESTART_BACKEND_NOW.bat
- SIMPLE_START_AND_TEST.bat
- start_grace.cmd
- stop_grace.cmd
- grace.cmd
- GRACE.ps1

**Test Runners (scripts/test/):**
- RUN_BACKEND_NOW.py
- RUN_DEMO.bat
- RUN_E2E_NOW.bat
- RUN_LAYER1_E2E_TEST.bat
- RUN_MODEL_REGISTRY_TESTS.bat
- RUN_TEST_NOW.bat
- TEST_BACKEND_START.bat
- TEST_COMPREHENSIVE_API.bat
- TEST_FACTORY_API.bat
- test_routes_work.bat

**Deployment (scripts/deployment/):**
- DEMO_PATCH_WORKFLOW.bat
- VERIFY_SYSTEM.bat
- CHECK_UI_STATUS.bat

**Utilities (scripts/utilities/):**
- DIAGNOSE_BACKEND.py
- FIX_INFRA_KERNEL_FINAL.py
- FIX_LOG_EVENTS.py
- FIX_NPM_ERROR.md
- UPDATE_ALL_KERNELS_TO_SDK.py
- UPDATE_KERNELS_SDK.bat
- VIEW_LOGS_NOW.bat
- VIEW_LOGS_NOW.md
- WATCH_GRACE_LIVE.bat
- watch_grace_live.py

**Book Ingestion (scripts/utilities/):**
- INGEST_ALL_BOOKS.bat
- INGEST_BUSINESS_BOOKS.md
- INGEST_FROM_PATH.bat
- MONITOR_BOOK_UPLOAD.bat
- SYNC_ALL_BOOKS.bat
- UPLOAD_AND_TRACK.bat
- UPLOAD_BOOK_NOW.md

### Test Files (*.py tests) - Move to tests/

**E2E Tests (tests/e2e/):**
- test_system_e2e.py
- test_layer1_e2e.py
- test_layer1_e2e_with_logs.py
- test_multi_os_fabric_e2e.py
- test_integrated_orchestration_e2e.py
- test_autonomous_learning_e2e.py
- FINAL_COMPLETE_TEST.py

**Integration Tests (tests/integration/):**
- test_safe_integrations.py
- test_integrated_orchestration_e2e.py

**Component Tests (tests/unit/):**
- test_api.py
- test_auto_pipeline.py
- test_boot_layer.py
- test_clarity_kernel.py
- test_librarian_kernel.py
- test_memory_panel.py
- test_model_registry_e2e.py

### Redundant Files - Move to .archived/

**Old Logs:**
- backend_*.log (except latest)
- serve_*.log (except latest)
- All boot_boot_*.log files

**Old Test Files:**
- FINAL_TEST.md
- E2E_TEST_SUCCESS.md
- RESTART_AND_TEST.md

**Deprecated Docs:**
- Duplicate guides
- Old status files
- Superseded integration docs

---

This organization will make the repo clean and maintainable!
