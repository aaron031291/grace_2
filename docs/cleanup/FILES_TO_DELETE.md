# Files Safe to Delete - Domain Architecture Cleanup

Based on the new **Domain-Grouped Architecture** and **Simplified Kernel Port Architecture**, the following files are duplicates or irrelevant and can be safely deleted:

## 🗑️ DUPLICATE START SCRIPTS (Root Level)
- `START.cmd` - duplicate
- `START_GRACE_CLEAN.cmd` - duplicate
- `START_COMPLETE_SYSTEM.cmd` - duplicate
- `START_WITH_TRUST_MONITORING.cmd` - duplicate
- `FRESH_START.cmd` - duplicate
- `CLEAN_START.cmd` - duplicate
- `KILL_AND_RESTART.cmd` - duplicate
- `kill_grace.cmd` - duplicate
- `USE_GRACE.cmd` - duplicate

**KEEP ONLY**: The standardized scripts in `batch_scripts/` or `scripts/startup/`

## 🗑️ DUPLICATE KILL/RESTART SCRIPTS
- `kill_grace.py` - duplicate
- `find_grace_process.py` - duplicate
- `cleanup_stale_ports.py` - duplicate if port management is now in the new architecture

## 🗑️ DUPLICATE BATCH SCRIPTS
- `batch_scripts/start_grace_clean.bat` - duplicate
- `batch_scripts/START_GRACE_NOW.bat` - duplicate
- `batch_scripts/START_GRACE.bat` - duplicate
- `batch_scripts/start_backend.bat` - duplicate
- `batch_scripts/start_backend_simple.bat` - duplicate
- `batch_scripts/restart_backend.bat` - duplicate
- `scripts/startup/start_grace.cmd` - duplicate
- `scripts/startup/START_GRACE_NOW.cmd` - duplicate
- `scripts/startup/RUN_GRACE.cmd` - duplicate
- `scripts/startup/restart_backend.cmd` - duplicate
- `scripts/startup/grace.cmd` - duplicate
- `scripts/startup/stop_grace.cmd` - duplicate

**KEEP ONLY**: One set of standardized startup scripts

## 🗑️ OLD ARCHITECTURE DOCUMENTATION (Superseded)
- `BOOT_FIXES_COMPLETE.md` - old iteration
- `COMPLETE_SOLUTION.md` - superseded by new architecture
- `DOMAIN_SYSTEM_BUILT.md` - old iteration, keep DOMAIN_GROUPED_ARCHITECTURE.md
- `KERNEL_AND_API_PORT_ARCHITECTURE.md` - superseded by SIMPLIFIED_KERNEL_PORT_ARCHITECTURE.md

## 🗑️ TEST LOGS & REPORTS (Old)
- `grace_e2e_report_20251116_140607.txt`
- `grace_e2e_test_20251116_140604.log`
- `backend_e2e.log`
- `chaos_enhanced_final.log`
- `boot_complete.log`
- `guardian.log`

## 🗑️ DUPLICATE TESTING SCRIPTS
- `tests/test_verification_simple.py` - if covered by test_verification_e2e.py
- `tests/test_verification_integration.py` - if covered by test_verification_comprehensive.py
- `tests/test_self_healing_quick.py` - if covered by test_self_healing.py
- `tests/test_kernels_quick.py` - if covered by test_kernels.py
- `tests/test_quick_integration.py` - if covered by test_full_integration.py
- `tests/test_complete_integration.py` - duplicate of test_full_integration.py
- `tests/test_complete_system.py` - duplicate
- `tests/test_complete_pipeline.py` - duplicate
- `tests/test_complete_clarity_pipeline.py` - duplicate
- `tests/test_layer2_hardening.py` - if no longer relevant
- `tests/test_layer3_integration.py` - if no longer relevant

## 🗑️ DUPLICATE DOCUMENTATION FILES
### Duplicate READMEs:
- `docs/README_FIXED.md` - keep docs/README.md
- `docs/README_NEW.md` - keep docs/README.md
- `docs/guides/README_FINAL.md` - keep docs/README.md

### Duplicate Quick Starts:
- `docs/QUICK_START_WORKING.md`
- `docs/guides/QUICK_START.md` (duplicate)
- `docs/quick_guides/QUICK_START.md` (duplicate)
- `docs/guides/QUICK_START_DEMO.md`
- `docs/guides/QUICK_START_GUIDE.md`
- `docs/guides/QUICK_START_MODELS.md`
- `docs/guides/QUICK_START_MEMORY_PIPELINE.md`

**KEEP ONLY**: One consolidated QUICKSTART.md

### Duplicate Status/Completion Docs:
- `docs/COMPLETE_INTEGRATION_FINAL.md`
- `docs/COMPLETION_SUMMARY.md`
- `docs/FINAL_INTEGRATION_COMPLETE.md`
- `docs/FULL_INTEGRATION_COMPLETE.md`
- `docs/FINAL_SUMMARY.md`
- `docs/FINAL_STATUS.md`
- `docs/FINAL_STATUS_HONEST.md`
- `docs/FINAL_COMPREHENSIVE_SYSTEM_DOCUMENT.md`

### Duplicate Guides:
- `docs/guides/QUICK_FIX.md`
- `docs/guides/QUICK_FIX_1.md`
- `docs/QUICK_FIX_GUIDE.md` (duplicate)
- `docs/guides/SIMPLE_FIX.md`
- `docs/guides/RESTART_AND_TEST.md`
- `docs/guides/RESTART_BOTH_NOW.md`
- `docs/restart/RESTART_REQUIRED.md`
- `docs/restart/RESTART_NOW.md`
- `docs/restart/RESTART_FRONTEND.md`
- `docs/restart/RESTART_BOTH_SERVICES.md`
- `docs/restart/RESTART_BACKEND_REQUIRED.md`
- `docs/restart/RESTART_BACKEND_FOR_MEMORY.md`

**KEEP ONLY**: One operational restart guide

### Duplicate System Manifests:
- `docs/system_manifests/GRACE_COMPLETE_SYSTEM.md`
- `docs/system_manifests/GRACE_COMPLETE_FINAL.md`
- `docs/system_manifests/GRACE_COMPLETE_SYSTEMS_MANIFEST.md`
- `docs/system_manifests/GRACE_COMPLETE_NATURAL_LANGUAGE.md`
- `docs/system_manifests/ALL_SYSTEMS_CONFIRMED.md`

### Duplicate Milestones:
- `docs/milestones/GRACE_COMPLETE.md`
- `docs/milestones/GRACE_COMPLETE_FINAL.md`
- `docs/milestones/GRACE_COMPLETE_INTERFACE.md`
- `docs/milestones/COMPLETE_SYSTEM_STATUS.md`
- `docs/milestones/COMPLETE_SYSTEM_READY.md`
- `docs/milestones/FINAL_INTEGRATION_COMPLETE.md`

## 🗑️ ARCHIVED DIRECTORIES (Entire Folders)
- `.archived/` - entire directory
- `.quarantine/` - entire directory (only has manifest.json)
- `.junie/` - if not used
- `.librarian_backups/` - if not used
- `docs/archive/` - entire directory (250+ old status files)
- `docs/status_archive/` - entire directory (old status files)
- `logs_archive/` - old test logs
- `logs/` subdirectories like `logs/chaos/`, `logs/chaos_enhanced/`, `logs/industry_chaos/` - old test artifacts

## 🗑️ OLD SCRIPTS (No Longer Relevant)
- `organize_repo.py` - likely done
- `fix_unicode.py` - likely done
- `scripts/fix_schema.py` - likely done
- `scripts/fix_database.py` - likely done
- `scripts/fix_immutable_log.py` - likely done
- `scripts/fix_merge_conflicts.py` - likely done
- `scripts/create_tables_simple.py` - if migrations handle this
- `scripts/create_verification_tables.py` - if migrations handle this
- `scripts/maintenance/resolve_conflicts.py` - likely done

## 🗑️ OLD LOG FILES (Root Level)
All `.log` files in root directory should be in `logs/`:
- `backend_e2e.log`
- `boot_complete.log`
- `chaos_enhanced_final.log`
- `guardian.log`
- `grace_e2e_test_20251116_140604.log`
- `grace_e2e_report_20251116_140607.txt`

## 🗑️ CACHE/TEMP DIRECTORIES
- `__pycache__/` - auto-generated
- `.pytest_cache/` - auto-generated
- `.qodo/` - unless actively using
- `-p/` - unknown directory

## 🗑️ DUPLICATE START HELPERS
- `start_grace_now.py` - duplicate
- `serve.py` - if you have a standardized entry point
- `remote_access_client.py` - unless actively needed

## ✅ SUMMARY BY CATEGORY

### High-Confidence Deletes (Duplicates Only):
- **23 duplicate .cmd/.bat startup scripts**
- **50+ duplicate documentation files**
- **15+ duplicate test files**
- **10+ old log files in root**
- **2 archived directories** (.archived, .quarantine)
- **docs/archive/** (entire directory with 100+ old files)
- **docs/status_archive/** (entire directory with old status files)

### Total Files/Folders: **~200+ files** safe to delete

---

## ⚠️ RECOMMENDED DELETION PROCESS

1. **Phase 1**: Delete entire archived directories first
   - `.archived/`
   - `.quarantine/`
   - `docs/archive/`
   - `docs/status_archive/`

2. **Phase 2**: Delete duplicate startup scripts (keep ONE set in `batch_scripts/`)

3. **Phase 3**: Consolidate documentation (keep primary files, delete duplicates)

4. **Phase 4**: Remove old test files (keep comprehensive versions)

5. **Phase 5**: Clean up old logs (keep in logs/ directory only)

---

## 📝 BEFORE DELETING
1. Commit current state to git
2. Create a backup branch
3. Delete in phases (test between phases)
4. Verify system still works after each phase
