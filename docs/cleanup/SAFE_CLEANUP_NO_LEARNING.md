# Safe Cleanup - Preserving Learning Elements

## ✅ SAFE TO DELETE (No Learning Impact)

### 1. **Old Timestamped Boot Logs** (Safe - Just noise)
```bash
del /q "logs\boot_boot_20251111_*.log"
```
These are old boot attempts from Nov 11, not used for learning.

### 2. **Old Chaos Test Artifacts** (Safe - Not learning data)
```bash
rmdir /s /q "logs\chaos"
rmdir /s /q "logs\chaos_artifacts" 
rmdir /s /q "logs\chaos_enhanced"
rmdir /s /q "logs\industry_chaos"
```
These are old stress test logs, not learning data.

### 3. **Duplicate Batch Scripts** (Safe - Just duplicates)
Keep ONE startup script, delete the rest:
```bash
# Keep: batch_scripts/launch_grace.bat
# Delete duplicates in scripts/:
del /q "scripts\start_grace.bat"
del /q "scripts\grace.bat"
del /q "scripts\start_both.bat"
del /q "scripts\START_GRACE_AND_MONITOR.bat"
```

### 4. **One-Time Migration Scripts** (Safe - Already completed)
```bash
del /q "scripts\add_passed_column.py"
del /q "scripts\apply_recording_migration.py"
del /q "scripts\apply_vector_migration.py"
del /q "scripts\apply_verification_migration.py"
del /q "scripts\create_crypto_tables.py"
del /q "scripts\create_htm_tables.py"
del /q "scripts\create_layer3_tables.py"
del /q "scripts\create_learning_tables.py"
del /q "scripts\create_lightning_tables.py"
del /q "scripts\create_secrets_tables.py"
del /q "scripts\bootstrap_verification.py"
del /q "scripts\migrate_memory_scoring.py"
del /q "scripts\populate_model_registry.py"
del /q "scripts\populate_verification_matrix.py"
```

### 5. **Old Fix Scripts** (Safe - One-time fixes)
```bash
del /q "scripts\FIX_ALL_ROUTERS.py"
del /q "scripts\fix_cognition_imports.py"
del /q "scripts\remove_conflict_markers.py"
del /q "scripts\rehash_users.py"
```

### 6. **Duplicate Demo Scripts in Batch** (Safe - Duplicates)
```bash
del /q "batch_scripts\run_alert_ml_demo.bat"
del /q "batch_scripts\run_business_demo.bat"
del /q "batch_scripts\run_dashboard_demo.bat"
```
Keep the Python versions in `scripts/demo_*.py`

### 7. **External Model Audit Logs** (Safe - Old audit)
```bash
rmdir /s /q "logs\external_model_audit"
```

### 8. **Old Serve Logs** (Safe - Old process logs)
```bash
del /q "logs\serve_auto_pipeline.log"
del /q "logs\serve_book_upload_fix.log"
del /q "logs\serve_business_intel.log"
del /q "logs\serve_e2e_test.log"
```

---

## ⚠️ DO NOT DELETE (Learning/Training Related)

### **Preserve All Learning Elements:**
```
✅ KEEP: grace_training/            # All training data
✅ KEEP: logs/immutable_audit.jsonl # Audit trail for learning
✅ KEEP: logs/boot_ledger.jsonl     # Boot history for learning
✅ KEEP: sandbox/learning_projects/ # Learning experiments
✅ KEEP: reports/autonomous_improvement/ # Learning cycles
✅ KEEP: scripts/analyze_*.py       # Analysis for learning
✅ KEEP: scripts/demo_*.py          # Demos for learning/examples
✅ KEEP: ml_artifacts/              # ML models and artifacts
✅ KEEP: knowledge_base/            # Knowledge for learning
✅ KEEP: .grace_cache/              # Cache may have learning data
✅ KEEP: .grace_snapshots/          # Snapshots for learning
✅ KEEP: .grace_vault/              # Vault may have learning data
✅ KEEP: logs/ingestion/            # Ingestion learning data
✅ KEEP: logs/alerts/               # Alert learning data
✅ KEEP: backend/autonomy/          # Autonomous learning code
✅ KEEP: backend/learning/          # Learning systems
```

---

## 🎯 Conservative Cleanup Script (Safe)

```bash
# Phase 1: Old boot logs only
del /q "c:\Users\aaron\grace_2\logs\boot_boot_20251111_*.log"

# Phase 2: Old chaos test artifacts
rmdir /s /q "c:\Users\aaron\grace_2\logs\chaos"
rmdir /s /q "c:\Users\aaron\grace_2\logs\chaos_artifacts"
rmdir /s /q "c:\Users\aaron\grace_2\logs\chaos_enhanced"
rmdir /s /q "c:\Users\aaron\grace_2\logs\industry_chaos"

# Phase 3: Old external audit logs
rmdir /s /q "c:\Users\aaron\grace_2\logs\external_model_audit"

# Phase 4: Old serve logs
del /q "c:\Users\aaron\grace_2\logs\serve_*.log"

# Phase 5: One-time migration scripts
del /q "c:\Users\aaron\grace_2\scripts\add_passed_column.py"
del /q "c:\Users\aaron\grace_2\scripts\apply_recording_migration.py"
del /q "c:\Users\aaron\grace_2\scripts\apply_vector_migration.py"
del /q "c:\Users\aaron\grace_2\scripts\apply_verification_migration.py"
del /q "c:\Users\aaron\grace_2\scripts\create_crypto_tables.py"
del /q "c:\Users\aaron\grace_2\scripts\create_htm_tables.py"
del /q "c:\Users\aaron\grace_2\scripts\create_layer3_tables.py"
del /q "c:\Users\aaron\grace_2\scripts\create_learning_tables.py"
del /q "c:\Users\aaron\grace_2\scripts\create_lightning_tables.py"
del /q "c:\Users\aaron\grace_2\scripts\create_secrets_tables.py"
del /q "c:\Users\aaron\grace_2\scripts\bootstrap_verification.py"
del /q "c:\Users\aaron\grace_2\scripts\migrate_memory_scoring.py"
del /q "c:\Users\aaron\grace_2\scripts\populate_model_registry.py"
del /q "c:\Users\aaron\grace_2\scripts\populate_verification_matrix.py"

# Phase 6: Old fix scripts
del /q "c:\Users\aaron\grace_2\scripts\FIX_ALL_ROUTERS.py"
del /q "c:\Users\aaron\grace_2\scripts\fix_cognition_imports.py"
del /q "c:\Users\aaron\grace_2\scripts\remove_conflict_markers.py"
del /q "c:\Users\aaron\grace_2\scripts\rehash_users.py"

# Phase 7: Duplicate startup scripts
del /q "c:\Users\aaron\grace_2\scripts\start_grace.bat"
del /q "c:\Users\aaron\grace_2\scripts\grace.bat"
del /q "c:\Users\aaron\grace_2\scripts\start_both.bat"
del /q "c:\Users\aaron\grace_2\scripts\START_GRACE_AND_MONITOR.bat"

# Phase 8: Duplicate demo batch files
del /q "c:\Users\aaron\grace_2\batch_scripts\run_alert_ml_demo.bat"
del /q "c:\Users\aaron\grace_2\batch_scripts\run_business_demo.bat"
del /q "c:\Users\aaron\grace_2\batch_scripts\run_dashboard_demo.bat"
```

---

## 📊 Impact Summary

**Files to Delete**: ~80 files
**Learning Elements Preserved**: 100%
**Risk Level**: Very Low

### What Gets Deleted:
- ✅ Old timestamped boot logs (25 files)
- ✅ Chaos/stress test artifacts (5 directories)
- ✅ One-time migration scripts (14 files)
- ✅ One-time fix scripts (4 files)
- ✅ Duplicate startup scripts (4 files)
- ✅ Old serve logs (4 files)
- ✅ Duplicate demo batch files (3 files)
- ✅ Old external audit logs (1 directory)

### What Gets Preserved:
- ✅ All of `grace_training/`
- ✅ All learning/ML artifacts
- ✅ All knowledge base
- ✅ All autonomous improvement reports
- ✅ Learning-related logs (immutable_audit, boot_ledger)
- ✅ Ingestion and alert logs (potential learning data)
- ✅ All cache/snapshot/vault data
- ✅ All demo Python scripts (examples for learning)
- ✅ All analysis scripts
- ✅ Sandbox learning projects

---

## 🚀 Execute Safe Cleanup?

This cleanup is **conservative** and **safe**:
- No learning data affected
- No training data affected
- Only old logs and completed one-time scripts
- Easy to verify nothing important deleted

Ready to execute?
