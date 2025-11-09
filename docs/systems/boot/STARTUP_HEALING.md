# Startup Self-Healing System

Grace now runs **self-healing checks BEFORE booting** to fix common startup issues automatically.

## What It Checks

### 1. Database Connectivity
- ✅ Database file exists
- ✅ Database is not locked
- 🔧 Auto-fix: Creates database if missing, unlocks if locked

### 2. Database Schema
- ✅ `verification_events` has `passed` column
- ✅ `playbooks` has `risk_level` and `autonomy_tier` columns
- 🔧 Auto-fix: Runs migrations if schema outdated

### 3. Port Availability
- ✅ Port 8000 (backend) is available
- ⚠️ Warns if port already in use

### 4. File Permissions
- ✅ `logs/`, `storage/`, `ml_artifacts/` directories exist
- ✅ Write permissions on critical directories
- 🔧 Auto-fix: Creates missing directories

### 5. Environment Variables
- ✅ `SECRET_KEY` is set
- ✅ `DATABASE_URL` is set
- ⚠️ Warns if critical vars missing

### 6. Dependencies
- ✅ Critical packages installed (fastapi, sqlalchemy, uvicorn)
- ⚠️ Warns if packages missing

### 7. Circular Imports
- ✅ `VerificationEvent` has `passed` attribute
- ✅ `Playbook` has `risk_level` attribute
- ⚠️ Detects circular import issues

### 8. Log Directory
- ✅ Logs directory writable
- 🔧 Auto-fix: Creates log directory if missing

## How It Works

When you run `.\GRACE.ps1`, it:

1. **Runs self-healing first** (`backend/startup_healer.py`)
2. Checks all critical systems
3. **Auto-fixes** issues it can handle
4. Reports issues that need manual intervention
5. Then starts Grace normally

## Example Output

```
============================================================
GRACE STARTUP SELF-HEALING
============================================================
Time: 2025-11-09 18:30:00

[CHECK] Database connectivity... [OK]
[CHECK] Database schema... [ISSUE] playbooks missing risk_level
  [FIX] Applying fix...
  [OK] Fixed!
[CHECK] Port availability... [OK]
[CHECK] File permissions... [OK]
[CHECK] Environment variables... [OK]
[CHECK] Dependencies... [OK]
[CHECK] Circular imports... [OK]
[CHECK] Log directory... [OK]

============================================================
Issues found: 1
Fixes applied: 1
============================================================

[INFO] Applied fixes. Grace should start cleanly now.
```

## Startup Playbooks

The healer has built-in "playbooks" for common issues:

| Issue | Auto-Fix |
|-------|----------|
| Database missing | Creates & initializes |
| Database locked | Removes lock files |
| Schema outdated | Runs migrations |
| Missing directories | Creates them |
| Import errors | Detects & reports |

## Manual Run

Test startup healing without booting Grace:

```powershell
.\.venv\Scripts\python.exe backend\startup_healer.py
```

## Disable Startup Healing

If you want to skip pre-flight checks, edit `GRACE.ps1` and comment out lines 144-151:

```powershell
# .venv\Scripts\python.exe backend\startup_healer.py
```

## Add Your Own Checks

Edit `backend/startup_healer.py` and add to the `checks` list:

```python
checks = [
    # ... existing checks ...
    ("Your check name", self._your_check_function),
]
```

Then implement the check function:

```python
async def _your_check_function(self):
    """Check something critical"""
    if problem_detected:
        return {
            "ok": False,
            "issue": "Description of problem",
            "fix": lambda: self._fix_function()  # Optional auto-fix
        }
    return {"ok": True}
```

## Benefits

✅ **Catches issues before they crash Grace**  
✅ **Auto-fixes common problems** (locked DB, missing schema, etc.)  
✅ **Faster debugging** - knows exactly what's wrong  
✅ **Prevents cascading failures** - fixes root causes first  
✅ **Learns from past boots** - can add new checks as issues arise  

## Next Steps

The startup healer can be enhanced with:
- ML-based issue prediction
- Historical startup failure analysis
- Auto-rollback on repeated failures
- Integration with main self-healing playbooks
