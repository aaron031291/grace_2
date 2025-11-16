# Port Watchdog Fix - Complete

## Problem Identified

**Port watchdog was checking dead allocations from previous crashes:**
- Ports 8001-8013 allocated by old Grace instances
- Those instances crashed
- Allocations persisted to disk
- Watchdog kept checking empty ports
- Created noise in logs

---

## Solution Implemented

### 1. ✅ Auto-Cleanup in Port Manager

**File:** `backend/core/port_manager.py`

**Changes:**
- Auto-detects stale allocations (not responding > 2 minutes)
- Cleans up dead processes automatically
- Only reports active/dead (filters noise)

### 2. ✅ Pre-Boot Cleanup in serve.py

**File:** `serve.py`

**Changes:**
- Cleans stale ports BEFORE Guardian boots
- Prevents watchdog from checking dead allocations
- Shows cleanup summary

### 3. ✅ API Endpoint for Manual Cleanup

**File:** `backend/routes/port_manager_api.py`

**New endpoint:**
```bash
POST /api/ports/cleanup-stale
```

Cleans all dead/stale ports on demand.

### 4. ✅ Utility Scripts

**cleanup_stale_ports.py** - Interactive cleanup tool
**CLEAN_START.cmd** - Start Grace with automatic cleanup

---

## How It Works Now

### On Grace Startup

```
1. [PRE-BOOT] Cleanup stale port allocations
   Scans: 17 allocations
   Finds: 15 stale
   Cleans: 15 ports
   [OK] Cleaned 15 stale port allocations

2. [CHUNK 0] Guardian Kernel Boot
   Allocates: Port 8000
   [OK] Guardian: Online
   [OK] Port: 8000
   [OK] Network: healthy
   [OK] Watchdog: Active

3. Port Watchdog starts
   Monitors: Port 8000 only
   Status: Active ✓
   No noise!
```

---

## Testing

### Start Grace Cleanly
```bash
python serve.py
```

**Expected output:**
```
[PRE-BOOT] Cleaning up stale port allocations...
  [OK] Cleaned 15 stale port allocations

[CHUNK 0] Guardian Kernel Boot...
  [OK] Guardian: Online
  [OK] Port: 8000
  [OK] Watchdog: Active

[PORT-WATCHDOG] Health check: 1 active, 0 dead, 0 issues
```

**No more noise!** ✓

### Manual Cleanup (If Needed)
```bash
# Interactive cleanup
python cleanup_stale_ports.py

# Or via API
curl -X POST http://localhost:8000/api/ports/cleanup-stale
```

---

## What Changed

### Port Manager Behavior

**Before:**
- Kept all allocations forever
- Checked every port every time
- Logged warnings for dead ports
- Manual cleanup only

**After:**
- ✅ Auto-detects stale allocations
- ✅ Auto-cleans after 2 minutes
- ✅ Only reports active/dead
- ✅ Filters noise
- ✅ Pre-boot cleanup

### Watchdog Behavior

**Before:**
```
[PORT-WATCHDOG] Health check: 0 active, 2 dead, 17 issues
[PORT-WATCHDOG] Port 8001: not_listening
[PORT-WATCHDOG] Port 8002: not_listening
[PORT-WATCHDOG] Port 8003: not_listening
... (15 more lines of noise)
```

**After:**
```
[PORT-WATCHDOG] Health check: 1 active, 0 dead, 0 issues
```

Clean! ✓

---

## Files Modified

1. **backend/core/port_manager.py**
   - Enhanced health_check_all() with auto-cleanup
   - Filters noise from reports
   - Auto-cleans stale allocations

2. **serve.py**
   - Added pre-boot cleanup step
   - Clears stale ports before Guardian starts

3. **backend/routes/port_manager_api.py**
   - Added /cleanup-stale endpoint

---

## Files Created

1. **cleanup_stale_ports.py** - Interactive cleanup utility
2. **CLEAN_START.cmd** - Clean startup script
3. **PORT_WATCHDOG_FIX_COMPLETE.md** - This file

---

## Telemetry & Metrics

### What Happens Now

**On startup:**
1. Stale ports cleaned automatically
2. Guardian allocates ONE port
3. Watchdog monitors ONLY that port
4. Health endpoint responds: `http://localhost:8000/health`
5. Metrics flow properly

### Getting Full Telemetry

**Current setup (Main API only):**
- ✅ Health: `http://localhost:8000/health`
- ✅ Metrics: Available through infrastructure APIs
- ✅ Port status: `GET /api/ports/status`
- ✅ Network stats: `GET /api/ports/network/stats`

**Future (When kernels deployed):**
- Each kernel on 8100-8149 with /health and /metrics
- Service discovery auto-finds them
- Watchdog monitors all
- Full distributed telemetry

---

## Start Grace Now

```bash
# Clean start (recommended first time)
CLEAN_START.cmd

# Or normal start
python serve.py
```

**Should see:**
```
[PRE-BOOT] Cleaning up stale port allocations...
  [OK] Cleaned X stale port allocations
  
[CHUNK 0] Guardian Kernel Boot...
  [OK] Guardian: Online
  [OK] Port: 8000
  [OK] Watchdog: Active
  
[PORT-WATCHDOG] Health check: 1 active, 0 dead, 0 issues
```

**CLEAN! No noise, proper monitoring!** ✓
