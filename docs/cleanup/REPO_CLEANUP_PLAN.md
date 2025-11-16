# 🧹 Repository Cleanup Plan

## Current Issue
Root directory has 100+ files scattered everywhere - needs organization!

## Target Structure

```
grace_2/
├── docs/
│   ├── collaboration/         # Collaboration system docs
│   ├── memory/               # Memory system docs  
│   ├── clarity/              # Clarity pipeline docs
│   ├── autonomous/           # Autonomous systems docs
│   ├── deployment/           # Deployment & production docs
│   ├── testing/              # Test documentation
│   ├── status_archive/       # Historical status files
│   └── guides/               # User guides & quickstarts
│
├── scripts/
│   ├── boot/                 # Boot scripts
│   ├── deployment/           # Deployment scripts
│   ├── testing/              # Test scripts
│   ├── maintenance/          # Cleanup & maintenance
│   └── utilities/            # Utility scripts
│
├── backend/                  # Backend code (already organized)
├── frontend/                 # Frontend code (already organized)
├── tests/                    # Test files
├── config/                   # Configuration files
├── databases/                # Database files
└── [essential root files]    # Only critical root files
```

## File Mapping

### Move to `docs/collaboration/`:
- COLLABORATION_*.md (8 files)

### Move to `docs/memory/`:
- MEMORY_*.md (20 files)
- GRACE_MEMORY_*.md

### Move to `docs/clarity/`:
- CLARITY_*.md (6 files)

### Move to `docs/autonomous/`:
- AUTONOMOUS_*.md (5 files)
- AGENT_*.md

### Move to `docs/deployment/`:
- DEPLOYMENT_*.md
- PRODUCTION_*.md
- READY_FOR_PRODUCTION.md

### Move to `docs/testing/`:
- TEST_*.md
- *_TEST_*.md

### Move to `docs/status_archive/`:
- COMPLETE_*.md (10+ files)
- FINAL_*.md
- SESSION_*.md
- *_COMPLETE.md
- *_SUMMARY.md
- *_VERIFICATION.md
- WARNINGS_FIXED.md
- WHATS_WORKING_NOW.md

### Move to `docs/guides/`:
- QUICK_*.md
- MANUAL_*.md
- *_QUICKSTART.md
- *_GUIDE.md
- FOR_JUNIE.md
- FRONTEND_DEBUG_STEPS.md

### Move to `scripts/boot/`:
- BOOT_*.ps1
- start_grace.*
- grace-universal.ps1
- GRACE_SAFE.ps1
- GRACE_PRODUCTION.ps1
- install-grace.ps1
- boot_grace.py
- restart_grace.ps1

### Move to `scripts/deployment/`:
- deploy_*.ps1
- commit_and_push.*

### Move to `scripts/testing/`:
- test_*.py (move to tests/ if actual tests, scripts/testing/ if utilities)
- run_*_tests.py
- create_and_run_test.py

### Move to `scripts/utilities/`:
- check_*.py
- debug_*.py
- diagnose_*.py
- fix_*.py
- resolve_*.py
- scan_*.py
- seed_*.py
- show_*.py
- validate_*.py
- open_correct_files.py
- grace_memory_examples.py

### Move to `scripts/maintenance/`:
- batch_*.ps1
- enhanced_batch_resolve.ps1
- remove_bom.ps1
- resolve_all_conflicts.ps1

### Keep in Root:
- README.md
- REPO_ORGANIZATION.md  
- GRACE.ps1 (main entry point)
- serve.py (main server)
- pyproject.toml
- alembic.ini
- docker-compose.yml
- Dockerfile
- .env.example
- .gitignore
- .gitattributes

## Execution

Will create folders and move ~100 files to organized locations.
