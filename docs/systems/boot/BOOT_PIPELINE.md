# Grace Boot Pipeline - 8-Stage Error Mitigation

**Comprehensive startup system that catches and fixes issues before they crash Grace**

## Overview

The boot pipeline runs automatically before Grace starts, executing 8 stages of validation, healing, and verification to ensure a clean startup.

## 8-Stage Pipeline

```
┌─────────────────────────────────────────────────────────┐
│  GRACE BOOT PIPELINE                                    │
├─────────────────────────────────────────────────────────┤
│  1. Preflight Gate        → Validation & schema checks  │
│  2. Schema Sync & Secrets → Migrations & UTF-8 setup    │
│  3. Core Services         → Boot DB, mesh, governance   │
│  4. Startup Playbooks     → Run self-heal fixes         │
│  5. Codec Validation      → UTF-8 sanity tests          │
│  6. Autonomy Load         → Load playbooks & metrics    │
│  7. Smoke Tests           → Quick validation tests      │
│  8. Continuous Monitor    → Setup ongoing health checks │
└─────────────────────────────────────────────────────────┘
```

## Stage Details

### Stage 1: Preflight Gate ⚠️ CRITICAL

**Purpose**: Validate database and schema before proceeding

**Checks**:
- Database file exists
- Required tables present (verification_events, playbooks, etc.)
- Schema version matches code

**Auto-Fixes**:
- Creates database if missing
- Runs migrations if schema outdated

**Metrics**:
- `startup.preflight_status` → "pass" or "fail"
- `startup.validation_errors` → count
- `startup.schema_mismatches` → count

**Failure Mode**: **ABORT** - Cannot continue if preflight fails

---

### Stage 2: Schema Sync & Secrets ⚠️ CRITICAL

**Purpose**: Ensure database schema and secrets are ready

**Checks**:
- `verification_events.passed` column exists
- `playbooks.risk_level` and `autonomy_tier` columns exist
- `SECRET_KEY` and `DATABASE_URL` environment variables set
- UTF-8 encoding configured

**Auto-Fixes**:
- Runs Alembic migrations for missing columns
- Configures stdout/stderr to UTF-8
- Sets `PYTHONIOENCODING=utf-8`

**Failure Mode**: **WARN** for missing secrets, **ABORT** for schema failures

---

### Stage 3: Core Services Isolation ⚠️ CRITICAL

**Purpose**: Boot foundational systems in safe mode

**Systems Started**:
1. Database connection
2. Trigger mesh
3. Metrics collector
4. Governance framework

**Mode**: Safe/observe-only mode (no execution)

**Failure Mode**: **ABORT** - Core services must start

---

### Stage 4: Startup Playbooks

**Purpose**: Run self-healing playbooks specific to startup

**Playbooks**:
1. `fix_unicode_logging` → Configure UTF-8 for console
2. `apply_pending_migrations` → Run database updates
3. `verify_async_subscriptions` → Check trigger mesh async calls

**Each playbook has**:
- `risk_level`: low, medium, high, critical
- `autonomy_tier`: tier_1 (auto), tier_2 (notify), tier_3 (approve), tier_4 (parliament)

**Failure Mode**: **CONTINUE** - Non-critical

---

### Stage 5: Codec Validation ⚠️ CRITICAL

**Purpose**: UTF-8 encoding sanity check

**Tests**:
1. ASCII output works
2. Emoji output works (✅)
3. Unicode output works (日本語)

**Failure Mode**: **ABORT** if ASCII fails, **WARN** if emoji fails

---

### Stage 6: Autonomy & Playbook Load

**Purpose**: Load AI/ML systems and playbooks

**Loaded**:
1. Metrics catalog (domain KPIs, thresholds, bands)
2. Playbook definitions from database
3. Proactive intelligence rules

**Failure Mode**: **CONTINUE** - Can start with reduced intelligence

---

### Stage 7: Smoke Tests

**Purpose**: Quick validation that systems work

**Tests**:
1. Import critical modules (VerificationEvent, Playbook)
2. Verify attributes exist (passed, risk_level, autonomy_tier)
3. Database query test
4. Metrics snapshot test

**Metrics**:
- `startup.boot_pipeline_stage` → current stage (7)
- `startup.tests_passed` → count

**Failure Mode**: **WARN** - Issues logged but not blocking

---

### Stage 8: Continuous Monitor Setup

**Purpose**: Schedule ongoing health monitoring

**Schedules**:
- Self-heal loop: Every 5 minutes
- Metrics snapshot: Every 1 minute
- Proactive intelligence: Every 10 minutes

**Failure Mode**: **CONTINUE** - Manual monitoring still possible

---

## Training & Learning

### Boot Data Collection

Every boot creates training data:

**File**: `grace_training/startup_failures/boot_YYYYMMDD_HHMMSS.json`

```json
{
  "boot_timestamp": "2025-11-09T18:30:00",
  "stages": [
    {
      "stage": "1. Preflight Gate",
      "success": true,
      "metrics": {...},
      "issues": [],
      "fixes": []
    }
  ],
  "summary": {
    "success": true,
    "stages_passed": 8,
    "stages_failed": 0
  }
}
```

### Startup Failure Patterns

**File**: `grace_training/startup_failures/_metadata.json`

Contains known startup incidents with:
- Pattern recognition (error signatures)
- Root cause analysis
- Fix playbooks
- Verification steps

**Example patterns**:
- `unicode_logging_crash` → UnicodeEncodeError
- `verification_events_schema_mismatch` → Missing passed column
- `circular_import_avn_models` → Import loop
- `database_locked` → SQLite lock
- `trigger_mesh_unawaited` → Missing await

### Learning Loop

1. **Detection**: Boot pipeline recognizes error pattern
2. **Application**: Runs corresponding playbook
3. **Verification**: Confirms fix worked
4. **Training**: Records success/failure
5. **Refinement**: ML improves playbook over time

---

## Usage

### Automatic (via GRACE.ps1)

Boot pipeline runs automatically:

```powershell
.\GRACE.ps1
```

Output:
```
============================================================
GRACE BOOT PIPELINE - 8 STAGES
============================================================

============================================================
1. Preflight Gate
============================================================
[CHECK] Running preflight validator...
  [OK] Database exists
  [OK] Schema up to date
[OK] 1. Preflight Gate complete

... (continues through all 8 stages) ...

============================================================
BOOT PIPELINE SUCCESS
Passed: 8/8
Failed: 0
============================================================
```

### Manual Test

Test boot pipeline without starting Grace:

```powershell
.\.venv\Scripts\python.exe backend\boot_pipeline.py
```

### View Last Boot Report

```powershell
Get-Content logs\last_boot_report.txt
```

Example report:
```
================================================================================
GRACE BOOT PIPELINE REPORT
================================================================================
Timestamp: 2025-11-09T18:30:15.123456
Success: YES
Stages Passed: 8/8
Stages Failed: 0

1. Preflight Gate
----------------------------------------
Success: True

2. Schema Sync & Secrets
----------------------------------------
Success: True
Fixes Applied: Applied verification_events migration

... etc ...
```

---

## Critical Stages

Stages marked **⚠️ CRITICAL** will abort the boot if they fail:

- **Stage 1**: Preflight Gate
- **Stage 2**: Schema Sync (partial)
- **Stage 3**: Core Services
- **Stage 5**: Codec Validation (partial)

Non-critical stages will log warnings and continue.

---

## Startup Playbooks

Registered automatically during Stage 4:

| Playbook | Description | Risk | Tier |
|----------|-------------|------|------|
| fix_unicode_logging | UTF-8 console setup | low | tier_1 |
| apply_pending_migrations | Run schema updates | medium | tier_2 |
| verify_async_subscriptions | Check await usage | low | tier_1 |
| unlock_database | Remove DB locks | low | tier_1 |
| fix_circular_imports | Resolve import loops | high | tier_3 |
| create_default_env | Generate .env file | low | tier_1 |

---

## Metrics Published

Boot pipeline publishes startup metrics:

- `startup.preflight_status` → pass/fail
- `startup.validation_errors` → count
- `startup.schema_mismatches` → count
- `startup.boot_pipeline_stage` → 1-8
- `startup.tests_passed` → count
- `startup.console_encoding` → utf-8/cp1252/ascii

These feed into proactive intelligence for anomaly detection.

---

## Integration with Self-Healing

After successful boot, the main self-healing loop takes over:

1. **Observe-only mode** (default): Detects issues, logs only
2. **Execute mode** (`SELF_HEAL_EXECUTE=true`): Actually fixes issues

Boot playbooks are registered and available for runtime use.

---

## Troubleshooting

### Pipeline Fails at Stage 1

**Symptoms**: Database missing or schema corrupted

**Fix**:
```powershell
# Delete and recreate database
Remove-Item backend\grace.db -Force
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Pipeline Fails at Stage 5

**Symptoms**: UTF-8 encoding not working

**Fix**:
```powershell
# Run PowerShell in UTF-8 mode
chcp 65001
$env:PYTHONIOENCODING = "utf-8"
.\GRACE.ps1
```

### Pipeline Warns About Secrets

**Symptoms**: Missing SECRET_KEY or DATABASE_URL

**Fix**:
```powershell
# Add to .env file
notepad .env

# Add these lines:
SECRET_KEY=<random-string>
DATABASE_URL=sqlite+aiosqlite:///./backend/grace.db
```

---

## Future Enhancements

1. **ML-Based Prediction**: Predict likely failures based on code changes
2. **Auto-Rollback**: Automatic rollback after N consecutive failures
3. **Startup Health Score**: Track success rate over time
4. **Distributed Boot**: Run stages in parallel where safe
5. **Cloud Integration**: Upload boot reports to central monitoring
6. **A/B Testing**: Try different fix strategies and learn which works best

---

## See Also

- [STARTUP_HEALING.md](file:///c:/Users/aaron/grace_2/STARTUP_HEALING.md) - Legacy startup healer
- [PERSISTENT_BLOCKERS_FIXED.md](file:///c:/Users/aaron/grace_2/PERSISTENT_BLOCKERS_FIXED.md) - Historical fixes
- [DISABLE_SELF_HEAL.md](file:///c:/Users/aaron/grace_2/DISABLE_SELF_HEAL.md) - Runtime self-healing control
