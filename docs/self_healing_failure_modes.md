# Self-Healing: Top 10 Failure Modes

**Phase 1: Self-Healing Robustness**  
**Created:** November 17, 2025

---

## Overview

This document defines the top 10 failure modes that Grace's self-healing system must detect and automatically remediate. Each failure mode includes:
- Description
- Detection method
- Automatic remediation steps
- Rollback procedure
- MTTR target

---

## Failure Mode 1: Database Corruption/Unavailable

### Description
SQLite database files become corrupted or locked, preventing access to critical data (world model, metrics, audit logs).

### Detection
- SQLite error: "database disk image is malformed"
- Connection timeouts
- File lock errors
- Read/write failures

### Automatic Remediation
1. **Backup current database** (even if corrupted)
2. **Check for .db-shm and .db-wal files** (WAL mode artifacts)
3. **Try SQLite integrity check**: `PRAGMA integrity_check`
4. **If recoverable:**
   - Close all connections
   - Run `PRAGMA wal_checkpoint(TRUNCATE)`
   - Reopen connections
5. **If unrecoverable:**
   - Restore from last known good backup
   - Alert user to potential data loss

### Rollback Procedure
- Restore from pre-remediation backup
- Revert to previous database file

### MTTR Target
**< 60 seconds** (includes backup and restore)

### Test Scenario
```python
# Corrupt database file
with open('databases/grace.db', 'ab') as f:
    f.write(b'\x00' * 1024)  # Append null bytes

# Verify auto-remediation triggers
```

---

## Failure Mode 2: Port Already in Use

### Description
Grace attempts to bind to its configured port, but another process is already using it.

### Detection
- OSError: "Address already in use" (Linux/Mac)
- OSError: "[WinError 10048]" (Windows)
- Port bind failure during boot

### Automatic Remediation
1. **Identify process using port**: `lsof -i :PORT` or `netstat -ano | findstr PORT`
2. **Check if it's a stale Grace process**:
   - Compare PID with port_manager registry
   - If stale, kill process
3. **If external process:**
   - Try next available port (8000 → 8001 → 8002... up to 8100)
   - Update port_manager registry
   - Update client configurations
4. **If all ports exhausted:**
   - Alert user
   - Log failure

### Rollback Procedure
- Release newly allocated port
- Restore original port preference

### MTTR Target
**< 10 seconds**

### Test Scenario
```python
# Occupy port 8000
import socket
sock = socket.socket()
sock.bind(('0.0.0.0', 8000))
sock.listen(1)

# Verify Grace auto-moves to 8001
```

---

## Failure Mode 3: Slow Boot (> 30 seconds)

### Description
Grace takes longer than 30 seconds to complete boot sequence.

### Detection
- Boot timer exceeds 30s threshold
- Chunks hang during execution
- Import timeouts

### Automatic Remediation
1. **Identify slow chunk**: Log timestamps per chunk
2. **Common causes:**
   - Network calls during boot (violate OFFLINE_MODE)
   - Heavy DB migrations
   - Model loading (Ollama not ready)
3. **Auto-fixes:**
   - Skip non-critical chunks (mark as degraded)
   - Defer heavy operations to background tasks
   - Cache expensive imports
4. **Alert user to investigate slow chunk**

### Rollback Procedure
- Re-enable skipped chunks
- Restore normal boot sequence

### MTTR Target
**< 5 seconds** (detection + skip)

### Test Scenario
```python
# Inject artificial delay in chunk
async def slow_chunk():
    await asyncio.sleep(35)  # Simulate 35s delay
    
# Verify timeout detection and skip
```

---

## Failure Mode 4: Out of Memory

### Description
Grace exhausts available RAM, causing OOM errors or system swapping.

### Detection
- MemoryError exceptions
- `psutil.virtual_memory().percent > 95%`
- System swap usage high
- Process RSS exceeds threshold (e.g., 4GB)

### Automatic Remediation
1. **Immediate actions:**
   - Clear in-memory caches
   - Release unused data structures
   - Trigger garbage collection (`gc.collect()`)
2. **Reduce memory footprint:**
   - Limit concurrent tasks
   - Flush buffered logs to disk
   - Unload unused models
3. **If still critical:**
   - Enter "low memory mode"
   - Disable non-essential services
   - Alert user

### Rollback Procedure
- Re-enable disabled services
- Restore cache sizes
- Exit low memory mode

### MTTR Target
**< 30 seconds**

### Test Scenario
```python
# Allocate large memory chunk
big_list = [0] * (10**9)  # ~8GB

# Verify OOM detection and cleanup
```

---

## Failure Mode 5: Disk Full

### Description
File system runs out of space, preventing logs, database writes, or artifact storage.

### Detection
- OSError: "No space left on device"
- `shutil.disk_usage().free < 100MB`
- Write failures

### Automatic Remediation
1. **Identify space hogs:**
   - Old log files (> 7 days)
   - Snapshot backups
   - Temporary files
2. **Cleanup actions:**
   - Rotate and compress old logs
   - Delete oldest snapshots (keep last 10)
   - Clear temp directories
3. **If still low:**
   - Move artifacts to secondary storage
   - Alert user to free space

### Rollback Procedure
- Restore deleted logs/snapshots from backup
- Re-expand storage if externally freed

### MTTR Target
**< 45 seconds**

### Test Scenario
```python
# Fill disk to threshold
with open('/tmp/bigfile', 'wb') as f:
    f.write(b'\x00' * (disk_free - 50MB))

# Verify cleanup triggers
```

---

## Failure Mode 6: Network Unreachable

### Description
External network becomes unavailable (e.g., DNS failure, internet down, firewall block).

### Detection
- DNS resolution failures
- Connection timeouts to external APIs
- Ping to 8.8.8.8 fails
- OSI Layer 3/4 probes fail

### Automatic Remediation
1. **Enter offline mode automatically**:
   - Set `OFFLINE_MODE=true`
   - Disable external API calls
   - Use cached data
2. **Retry with backoff:**
   - Ping every 10s → 30s → 60s
   - Once network restored, exit offline mode
3. **Log all blocked operations for retry**

### Rollback Procedure
- Exit offline mode
- Retry queued operations
- Resume normal network operations

### MTTR Target
**< 5 seconds** (enter offline mode)  
**Auto-recovery when network returns**

### Test Scenario
```python
# Simulate network failure
mock_dns_failure()

# Verify offline mode activation
```

---

## Failure Mode 7: API Endpoint Timeout

### Description
Critical API endpoints become unresponsive or slow (> 30s response time).

### Detection
- Request timeout exceptions
- Response time > 30s
- Multiple consecutive failures (3+ in a row)

### Automatic Remediation
1. **Circuit breaker pattern:**
   - After 3 failures, mark endpoint as "open" (degraded)
   - Route traffic to backup endpoint (if available)
   - Retry primary endpoint every 60s
2. **Reduce timeout threshold** (30s → 10s → 5s)
3. **Cache last successful response** (serve stale data with warning)
4. **Alert monitoring system**

### Rollback Procedure
- Close circuit breaker
- Restore normal timeout
- Re-enable primary endpoint

### MTTR Target
**< 15 seconds** (circuit breaker activation)

### Test Scenario
```python
# Mock slow endpoint
@app.get("/slow")
async def slow_endpoint():
    await asyncio.sleep(35)
    return {"data": "slow"}

# Verify circuit breaker triggers
```

---

## Failure Mode 8: Missing Configuration File

### Description
Required configuration files (e.g., `config/governance_policies.yaml`) are missing or corrupted.

### Detection
- FileNotFoundError
- YAML parse errors
- Schema validation failures

### Automatic Remediation
1. **Check for backup config**: `.bak` or versioned file
2. **If no backup, use default config**:
   - Load embedded defaults from code
   - Write default config to disk
   - Log warning to user
3. **Validate new config against schema**
4. **Alert user to review defaults**

### Rollback Procedure
- Restore user's original config
- Merge with defaults if needed

### MTTR Target
**< 10 seconds**

### Test Scenario
```python
# Delete config file
os.remove('config/governance_policies.yaml')

# Verify default config generation
```

---

## Failure Mode 9: Invalid Credentials

### Description
API keys, tokens, or passwords become invalid or expired.

### Detection
- 401 Unauthorized responses
- 403 Forbidden responses
- Token expiration errors
- Authentication failures

### Automatic Remediation
1. **Check for token refresh capability**:
   - If OAuth2, attempt token refresh
   - If API key, check for backup key
2. **Degrade gracefully**:
   - Disable affected service
   - Use cached data
   - Log "authentication required" event
3. **Alert user to update credentials**
4. **Do NOT attempt brute force or retry excessively**

### Rollback Procedure
- Re-enable service after credential update
- Clear authentication error state

### MTTR Target
**< 5 seconds** (detection + graceful degradation)  
**Manual intervention required for fix**

### Test Scenario
```python
# Invalidate API key
config.api_key = "invalid_key_xxx"

# Verify graceful degradation
```

---

## Failure Mode 10: Model Server Down (Ollama)

### Description
Ollama model server is not running or unreachable.

### Detection
- Connection refused to `localhost:11434`
- API errors from Ollama
- Model inference timeouts

### Automatic Remediation
1. **Attempt to start Ollama**:
   - Run `ollama serve` in background
   - Wait up to 10s for startup
2. **If startup fails:**
   - Check if Ollama is installed
   - Log installation instructions
3. **Degrade AI features:**
   - Disable model-dependent endpoints
   - Use rule-based fallbacks
   - Serve cached model responses
4. **Alert user**

### Rollback Procedure
- Re-enable AI features
- Restore model endpoints
- Clear degraded state

### MTTR Target
**< 20 seconds** (includes Ollama startup)

### Test Scenario
```python
# Stop Ollama
subprocess.run(["pkill", "ollama"])

# Verify auto-restart attempt
```

---

## Summary Table

| # | Failure Mode | MTTR Target | Criticality | Auto-Remediation |
|---|--------------|-------------|-------------|------------------|
| 1 | Database Corruption | < 60s | CRITICAL | Backup + Restore |
| 2 | Port In Use | < 10s | HIGH | Port rotation |
| 3 | Slow Boot | < 5s | MEDIUM | Skip slow chunks |
| 4 | Out of Memory | < 30s | HIGH | Cache cleanup |
| 5 | Disk Full | < 45s | HIGH | Log rotation |
| 6 | Network Unreachable | < 5s | MEDIUM | Offline mode |
| 7 | API Timeout | < 15s | MEDIUM | Circuit breaker |
| 8 | Missing Config | < 10s | MEDIUM | Default config |
| 9 | Invalid Credentials | < 5s | LOW | Graceful degrade |
| 10 | Ollama Down | < 20s | MEDIUM | Auto-restart |

**Average MTTR Target:** < 20 seconds  
**Phase 1 Goal:** < 2 minutes (120s) for all failure modes

---

## Next Steps

1. **Implement detection** for each failure mode
2. **Write remediation playbooks** (automated scripts)
3. **Create test scenarios** (simulate each failure)
4. **Measure actual MTTR** (run tests, record times)
5. **Optimize slow remediations** (target < 2 min)
6. **Document in Guardian playbook registry**

---

**Document Status:** DRAFT  
**Last Updated:** November 17, 2025  
**Owner:** Phase 1 Self-Healing Team
