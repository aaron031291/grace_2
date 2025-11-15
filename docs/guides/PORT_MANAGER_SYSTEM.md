# Port Manager & Watchdog System

## Problem Solved

**Before:** Port conflicts crashed Grace  
**After:** Managed port range 8000-8100 with full tracking

---

## How It Works

### 1. Port Manager
Manages ports 8000-8100:
- ✅ Auto-allocates next available port
- ✅ Tracks metadata (who, what, when, why)
- ✅ Registers process IDs
- ✅ Logs all allocations/releases
- ✅ Persists state across restarts

### 2. Watchdog
Monitors all allocated ports:
- ✅ Health checks every 30 seconds
- ✅ Detects crashed services
- ✅ Cleans up stale allocations
- ✅ Pings health endpoints
- ✅ Tracks request/error counts

### 3. Audit Trail
Complete logging:
- ✅ Port allocations → `logs/port_manager/allocations_YYYYMMDD.jsonl`
- ✅ Port registry → `databases/port_registry/port_registry.json`
- ✅ Health checks → Application logs
- ✅ All metadata preserved

---

## Port Allocation Metadata

When Grace allocates a port, it tracks:

```json
{
  "port": 8000,
  "service_name": "grace_backend",
  "started_by": "serve.py",
  "purpose": "Main Grace API server with remote access and learning",
  "pid": 12345,
  "allocated_at": "2025-11-15T14:30:00Z",
  "last_health_check": "2025-11-15T14:35:00Z",
  "health_status": "active",
  "request_count": 1247,
  "error_count": 3
}
```

**Full context for every port!**

---

## Usage

### Automatic (In serve.py)

Grace automatically:
1. Allocates port from 8000-8100
2. Tries preferred port (8000) first
3. Falls back to next available
4. Registers PID
5. Starts watchdog
6. Logs everything
7. Releases on shutdown

### View Port Status

**Command line:**
```bash
python scripts/utilities/check_ports.py
```

**Output:**
```
======================================================================
GRACE PORT MANAGER STATUS
======================================================================

Port Range: 8000-8100
Total Ports Available: 101
Allocated: 1
Available: 100

======================================================================
ALLOCATED PORTS
======================================================================

Port 8000: grace_backend
  Started by: serve.py
  Purpose: Main Grace API server with remote access and learning
  PID: 12345
  Status: active
  Allocated: 2025-11-15T14:30:00Z
  Requests: 1247
  Errors: 3

======================================================================
WATCHDOG STATUS
======================================================================

Running: True
Check Interval: 30s
Checks Performed: 42
Issues Detected: 0
Stale Cleaned: 0
Monitored Ports: 1
```

### API Endpoints

**Get status:**
```bash
GET /api/ports/status
```

**Get all allocations:**
```bash
GET /api/ports/allocations
```

**Get specific port:**
```bash
GET /api/ports/allocations/8000
```

**Trigger health check:**
```bash
POST /api/ports/health-check
```

**Get watchdog status:**
```bash
GET /api/ports/watchdog/status
```

---

## Watchdog Features

### Automatic Health Checks
Every 30 seconds, the watchdog:
1. Checks if port is listening
2. Checks if process is alive
3. Pings health endpoint
4. Updates status
5. Cleans up dead services

### Issue Detection
Detects:
- ✅ Crashed processes (PID no longer exists)
- ✅ Non-responsive ports (not listening)
- ✅ Failed health checks
- ✅ Stale allocations

### Automatic Cleanup
- Dead services → Port released automatically
- Stale PIDs → Cleaned up
- No manual intervention needed

---

## Logs & Audit Trail

### Allocation Logs
**Location:** `logs/port_manager/allocations_YYYYMMDD.jsonl`

**Format:**
```json
{"timestamp": "2025-11-15T14:30:00Z", "action": "allocate", "port": 8000, "service_name": "grace_backend", "started_by": "serve.py", "purpose": "Main Grace API server"}
{"timestamp": "2025-11-15T16:45:00Z", "action": "release", "port": 8000, "service_name": "grace_backend", "duration_seconds": 8100, "request_count": 1247, "error_count": 3}
```

### Port Registry
**Location:** `databases/port_registry/port_registry.json`

**Format:**
```json
{
  "allocations": {
    "8000": {
      "port": 8000,
      "service_name": "grace_backend",
      "started_by": "serve.py",
      "purpose": "Main Grace API server",
      "pid": 12345,
      "allocated_at": "2025-11-15T14:30:00Z",
      "health_status": "active"
    }
  },
  "last_updated": "2025-11-15T14:35:00Z"
}
```

---

## Benefits

✅ **No more port conflicts** - 101 ports available  
✅ **Auto-allocation** - Grace finds free port automatically  
✅ **Full tracking** - Who, what, when, why for every port  
✅ **Health monitoring** - Watchdog checks every 30s  
✅ **Auto-cleanup** - Dead services cleaned automatically  
✅ **Complete audit** - All logs preserved  
✅ **Multi-service ready** - Can run multiple Grace instances  

---

## Example: Multiple Grace Services

You can run multiple Grace services simultaneously:

**Terminal 1:** Main Grace
```bash
python serve.py
# Allocates port 8000
```

**Terminal 2:** Learning-only Grace
```bash
python serve.py
# Allocates port 8001
```

**Terminal 3:** Remote-access-only Grace
```bash
python serve.py
# Allocates port 8002
```

All tracked, all monitored, all logged!

---

## Watchdog in Action

```
[PORT-WATCHDOG] Started (checking every 30s)
[PORT-WATCHDOG] Monitoring ports 8000-8100

# 30 seconds later...
[PORT-WATCHDOG] Health check: 1 active, 0 dead, 0 issues

# If a service crashes...
[PORT-WATCHDOG] Port 8001 (grace_learning): dead
[PORT-WATCHDOG] Cleaning up stale port 8001
[PORT-MANAGER] Released port 8001
```

**Automatic recovery!**

---

## Integration with serve.py

When you run `python serve.py`:

```
Allocating port from managed range (8000-8100)...
✅ Allocated port 8000
   Service: grace_backend
   Watchdog: Active (monitors health every 30s)

GRACE IS READY
📡 API: http://localhost:8000
```

Then:
- Port 8000 tracked in registry
- PID registered
- Watchdog monitoring
- All logged
- Auto-cleanup on shutdown

---

## Summary

**The Solution:**
- ✅ Manages ports 8000-8100 (101 ports)
- ✅ Tracks who/what/when/why/where
- ✅ Watchdog monitors health (30s interval)
- ✅ Auto-cleanup of dead services
- ✅ Complete audit trail
- ✅ API for monitoring

**No more port conflicts!**

**View status:** `python scripts/utilities/check_ports.py`

**API:** `/api/ports/status`
