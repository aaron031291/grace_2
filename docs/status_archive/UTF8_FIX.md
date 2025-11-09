# UTF-8 Encoding Fix for Windows Console ✅

**Issue**: Windows console defaults to CP1252, causing emoji/unicode errors in logs.

## Fixes Applied

### 1. Code-Level Fix (Permanent) ✅
**File**: `backend/main.py` (lines 1-7)

```python
# Force UTF-8 encoding for Windows console (before any logging)
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except AttributeError:
    pass
```

This ensures UTF-8 encoding regardless of console settings.

### 2. Boot Script Fix ✅
**Files**: `GRACE.ps1` (lines 7-8), `BOOT_GRACE_REAL.ps1` (lines 7-8)

Added at the top of both scripts:
```powershell
# Set UTF-8 encoding for console
chcp 65001 > $null
$env:PYTHONIOENCODING = "utf-8"
```

## Verification

After restart, emojis should display correctly:
- ✅ Checkmarks
- 🔍 Magnifying glass
- ⚠️ Warning signs
- 🚀 Rockets

## Manual Override (if needed)

If you need to set UTF-8 manually in PowerShell:

```powershell
chcp 65001 > $null
$env:PYTHONIOENCODING = "utf-8"
.\GRACE.ps1
```

## Create Permanent PowerShell Profile

To make UTF-8 default for all PowerShell sessions:

```powershell
# Edit PowerShell profile
notepad $PROFILE

# Add these lines:
chcp 65001 > $null
$env:PYTHONIOENCODING = "utf-8"
```

## Why This Matters

Without UTF-8 encoding:
- Logs fail with `UnicodeEncodeError: 'charmap' codec can't encode character`
- Startup scripts crash when printing emojis
- Verification scripts fail

With UTF-8 encoding:
- All unicode characters display properly
- Logs are readable and colorful
- Scripts run without encoding errors
