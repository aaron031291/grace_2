# Grace Repository Cleanup Log
**Date:** 2025-11-09

## PART 1: Duplicate Files Analysis & Removal

### PowerShell Boot Scripts (Keep Newest)
**Keeping:** BOOT_GRACE_REAL.ps1 (2025-11-09 15:09:16) - NEWEST
**Deleting:**
- BOOT_GRACE_COMPLETE_E2E.ps1 (2025-11-09 14:04:35) - Older duplicate
- boot_grace_complete.ps1 (2025-11-09 12:15:48) - Older duplicate

### Grace Start Scripts (Keep Newest)
**Keeping:** GRACE.ps1 (2025-11-09 14:04:35) - Main entry point
**Deleting:**
- START_GRACE_NOW.ps1 (2025-11-09 14:04:35) - Same timestamp, redundant
- START_GRACE_FIXED.ps1 (2025-11-09 14:04:35) - Same timestamp, redundant
- RUN_THIS_NOW.ps1 (2025-11-09 14:04:35) - Same timestamp, redundant
- RUN_GRACE.ps1 (2025-11-09 13:10:05) - Older duplicate
- START.ps1 (2025-11-09 14:15:28) - Ambiguous name
- start_grace.ps1 (2025-11-09 12:10:04) - Older duplicate

### Batch Files (Consolidate & Move)
**Moving to scripts/:**
- grace.bat → scripts/grace.bat
- start_grace.bat → scripts/start_grace.bat
- chat_with_grace.bat → scripts/chat_with_grace.bat
- demo_web_learning.bat → scripts/demo_web_learning.bat
- test_new_systems.bat → scripts/test_new_systems.bat
- run_integration_tests.bat → scripts/run_integration_tests.bat
- fix_database.bat → scripts/fix_database.bat
- verify_coding_agent_active.bat → scripts/verify_coding_agent_active.bat
- check_agentic_status.bat → scripts/check_agentic_status.bat
- restart_backend.bat → scripts/restart_backend.bat
- start_both.bat → scripts/start_both.bat
- START_GRACE_AND_MONITOR.bat → scripts/START_GRACE_AND_MONITOR.bat

**Deleting:**
- RUN_GRACE.bat (2025-11-09 12:27:54) - Duplicate of GRACE.ps1
- RUN_GRACE_SIMPLE.bat (2025-11-09 12:27:54) - Duplicate

### Monitoring Scripts (Move to scripts/monitoring/)
**Moving:**
- watch_all_logs.ps1 → scripts/monitoring/watch_all_logs.ps1
- watch_healing.ps1 → scripts/monitoring/watch_healing.ps1
- view_logs.ps1 → scripts/monitoring/view_logs.ps1
- chat_with_grace.ps1 → scripts/monitoring/chat_with_grace.ps1

### Utility Scripts (Move to scripts/)
**Moving:**
- grace_control.ps1 → scripts/grace_control.ps1
- FIX_AND_START.ps1 → scripts/FIX_AND_START.ps1
- CHECK_BACKEND_LOGS.ps1 → scripts/CHECK_BACKEND_LOGS.ps1
- START_BACKEND_SIMPLE.ps1 → scripts/START_BACKEND_SIMPLE.ps1
- INSTALL_DEPENDENCIES.ps1 → scripts/INSTALL_DEPENDENCIES.ps1
- VERIFY_TOKEN_FIX.ps1 → scripts/VERIFY_TOKEN_FIX.ps1
- TEST_E2E_BOOT.ps1 → scripts/TEST_E2E_BOOT.ps1
- GO.ps1 → scripts/GO.ps1

### Docker Scripts (Move to scripts/)
**Moving:**
- docker-build.ps1 → scripts/docker-build.ps1
- docker-start.ps1 → scripts/docker-start.ps1

## PART 2: Python Test Files (Move to tests/)

**Moving to tests/:**
- test_github_token.py → tests/test_github_token.py
- test_with_token.py → tests/test_with_token.py
- test_reddit_integration.py → tests/test_reddit_integration.py
- test_reddit_simple.py → tests/test_reddit_simple.py
- test_youtube_api_direct.py → tests/test_youtube_api_direct.py
- test_youtube_real_api.py → tests/test_youtube_real_api.py
- test_kernels_quick.py → tests/test_kernels_quick.py

## PART 3: Markdown Documentation Organization

### Keep in Root:
- README.md
- QUICK_START.md
- START_HERE.md

### Move to docs/:
- IMPLEMENTATION_SUMMARY.md → docs/IMPLEMENTATION_SUMMARY.md (duplicate check)
- GRACE_SYSTEM_REAL.md → docs/GRACE_SYSTEM_REAL.md
- METRICS_SYSTEM_COMPLETE.md → docs/METRICS_SYSTEM_COMPLETE.md
- DEPLOYMENT_VERIFIED.md → docs/DEPLOYMENT_VERIFIED.md
- COMPLETE_SYSTEM_READY.md → docs/COMPLETE_SYSTEM_READY.md
- IMPORT_FIXES_COMPLETE.md → docs/IMPORT_FIXES_COMPLETE.md
- IMPORT_FIXES_SUMMARY.md → docs/IMPORT_FIXES_SUMMARY.md
- FIXED_READY_TO_RUN.md → docs/FIXED_READY_TO_RUN.md
- BACKEND_STUCK_FIX.md → docs/guides/BACKEND_STUCK_FIX.md
- FIX_SCRIPT_NOT_FOUND.md → docs/guides/FIX_SCRIPT_NOT_FOUND.md
- START_FULL_SYSTEM.md → docs/guides/START_FULL_SYSTEM.md
- QUICK_FIX.md → docs/guides/QUICK_FIX.md
- FIXED_BACKEND.md → docs/guides/FIXED_BACKEND.md
- FIX_BACKEND.md → docs/guides/FIX_BACKEND.md
- INDEX.md → docs/INDEX.md
- HOW_TO_START.md → docs/guides/HOW_TO_START.md
- SUBSYSTEM_CHECKLIST.md → docs/SUBSYSTEM_CHECKLIST.md
- README_NEW.md → docs/README_NEW.md
- BOOT_README.md → docs/BOOT_README.md

### Move to docs/api/:
- README_KERNELS.md → docs/api/README_KERNELS.md
- KERNEL_API_AUDIT_COMPLETE.md → docs/api/KERNEL_API_AUDIT_COMPLETE.md
- KERNEL_IMPLEMENTATION_COMPLETE.md → docs/api/KERNEL_IMPLEMENTATION_COMPLETE.md

### Move to docs/guides/:
- YOUTUBE_API_INTEGRATION_COMPLETE.md → docs/guides/YOUTUBE_API_INTEGRATION_COMPLETE.md
- GITHUB_TOKEN_CHANGES.md → docs/guides/GITHUB_TOKEN_CHANGES.md
- REDDIT_API_INTEGRATION.md → docs/guides/REDDIT_API_INTEGRATION.md

### Delete (Redundant):
- COPY_PASTE_COMMANDS.txt (outdated commands)
- frontend.log (log file in root)

## Summary of Actions
- **Files Deleted:** 8 duplicate PowerShell scripts, 2 redundant files
- **Files Moved to scripts/:** 12 batch files, 8 PowerShell scripts
- **Files Moved to scripts/monitoring/:** 4 scripts
- **Files Moved to tests/:** 7 Python test files
- **Files Moved to docs/:** 23 markdown files
- **Files Kept in Root:** 3 markdown files, GRACE.ps1, BOOT_GRACE_REAL.ps1, Docker configs, .env files

## Final Root Directory Structure
- README.md
- QUICK_START.md
- START_HERE.md
- GRACE.ps1 (main entry point)
- BOOT_GRACE_REAL.ps1 (complete boot script)
- docker-compose.yml
- docker-compose.complete.yml
- Dockerfile
- .env
- .env.example
- .gitignore
- alembic.ini
- CLEANUP_LOG.md (this file)
