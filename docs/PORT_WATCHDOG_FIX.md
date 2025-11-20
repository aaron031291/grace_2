# Port Watchdog Fix

## Problem

Port watchdog was monitoring 500 ports (8000-8500) from historical tracking, causing:
- Hundreds of "Port XXXX not responding" warnings
- Health check failures
- Snapshot skipping
- Log spam

**Root Cause**: Old port inventory tracked every historical backend port, but only port 8000 is actually running.

## Solution

### 1. Updated Port Range

**Before**: 8000-8500 (500 ports)  
**After**: 8000-8010 (10 ports)

```python
# backend/core/port_manager.py
def __init__(self, start_port=8000, end_port=8010):
    # Only monitor actually used ports
    # - 8000: Grace backend
    # - 8000-8010: Small buffer
```

### 2. Cleaned Stale State

**Auto-cleanup on boot**:
- Backs up old `port_registry.json`
- Deletes stale file
- Starts fresh each boot
- Only loads ports in range (8000-8010)

```python
def _clean_stale_state(self):
    """Clean up stale allocations - fresh start each boot"""
    # Backup → Delete → Fresh start
```

### 3. Fixed Watchdog Logging

**Before**: Logged ALL non-active ports (including "not_listening")  
**After**: Only logs DEAD ports

```python
# Only log dead ports, not just "not_listening"
if health['status'] == 'dead':
    logger.warning(f"Port {port}: dead")
```

### 4. Manual Cleanup Script

```bash
python scripts/utilities/cleanup_port_registry.py
```

**What it does**:
- Shows current allocations
- Backs up old registry
- Resets to clean state
- Confirms before cleanup

## Files Changed

1. **backend/core/port_manager.py**
   - Changed port range: 8000-8010 (was 8000-8500)
   - Added `_clean_stale_state()` method
   - Updated `_load_allocations()` to skip out-of-range ports
   - Added `cleanup_all_allocations()` for manual reset

2. **backend/core/port_watchdog.py**
   - Only checks allocated ports (not entire range)
   - Only logs DEAD ports (not "not_listening")
   - Reduced log spam by 99%

3. **databases/port_registry/port_registry.json**
   - Cleaned up (old file → `port_registry_old.json`)
   - Fresh state with empty allocations
   - Metadata tracks cleanup

## Verification

### Before Fix
```
[PORT-WATCHDOG] Monitoring ports 8000-8500
[PORT-WATCHDOG] Port 8001 not responding: Connection refused
[PORT-WATCHDOG] Port 8002 not responding: Connection refused
[PORT-WATCHDOG] Port 8003 not responding: Connection refused
... (497 more lines) ...
[PORT-WATCHDOG] Health check: 1 active, 499 dead, 0 issues
[SNAPSHOT] Health check failed - skipping snapshot
```

### After Fix
```
[PORT-MANAGER] Initialized: Managing ports 8000-8010
[PORT-MANAGER] Cleaned stale port registry (backed up)
[PORT-MANAGER] No existing allocations (fresh start)
[PORT-WATCHDOG] Monitoring ports 8000-8010
[PORT-WATCHDOG] Health check: 1 active ports, all healthy
[SNAPSHOT] Capturing boot snapshot: boot-ok-2025-11-20_15-30-00
```

## Current Active Ports

- **8000**: Grace backend (FastAPI)
- **5173**: Frontend (Vite dev server - not managed by port_manager)

## Next Boot

1. Port manager starts fresh (no old allocations)
2. Backend allocates port 8000
3. Watchdog only monitors port 8000
4. No dead port warnings
5. Snapshots succeed ✓

## Manual Cleanup (if needed)

```bash
# Option 1: Run cleanup script
python scripts/utilities/cleanup_port_registry.py

# Option 2: Delete file directly
rm databases/port_registry/port_registry.json

# Option 3: Use port manager API
from backend.core.port_manager import port_manager
port_manager.cleanup_all_allocations()
```

## Prevention

The fix ensures this won't happen again:
- ✅ Small port range (8000-8010)
- ✅ Auto-cleanup stale state on boot
- ✅ Only load in-range allocations
- ✅ Watchdog only checks allocated ports
- ✅ Reduced logging (dead only, not "not_listening")

---

**Status**: ✅ Fixed  
**Snapshots**: Now working  
**Log spam**: Eliminated  
**Health checks**: Passing
