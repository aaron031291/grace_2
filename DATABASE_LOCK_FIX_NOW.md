# Database Lock - Immediate Fix Required

## The Problem

Grace's immutable log is trying to append entry #697 but SQLite is locked. This happens when:
- Another Grace instance is still running
- Previous crash left database in locked state
- Too many concurrent writes during startup

## Immediate Fix (Do This Now)

### Step 1: Kill Existing Processes
```bash
taskkill /F /IM python.exe
```

### Step 2: Wait 3 Seconds
```bash
# Let processes fully terminate
timeout /t 3
```

### Step 3: Run Emergency Fix
```bash
emergency_db_fix.bat
```

**Or manually:**

```powershell
# Clear lock files
del /F /Q databases\*.db-wal
del /F /Q databases\*.db-shm
del /F /Q databases\*.db-journal

# Enable WAL mode
.venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('databases/grace.db'); conn.execute('PRAGMA journal_mode=WAL'); conn.execute('PRAGMA busy_timeout=30000'); conn.commit(); conn.close(); print('Fixed!')"

# Start Grace
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Why This Happens

The immutable log gets **MANY concurrent writes** during Grace's startup:
- Trigger Mesh (10+ subscriptions)
- Shards starting (6 shards)
- Memory broker initializing
- Meta-loop launching
- Proactive intelligence starting
- All trying to log "service_started" at once

## What We Already Fixed (In Code)

✅ WAL mode enabled (allows concurrent reads + 1 writer)
✅ 30-second busy timeout
✅ Connection pooling (10 base, 20 overflow)
✅ Retry logic with exponential backoff

**But** these only work if:
1. Database starts fresh (no stale locks)
2. WAL mode is actually enabled in the SQLite file

## Permanent Solution

### Option 1: Run Emergency Fix Before Every Start
```bash
emergency_db_fix.bat
```

### Option 2: Sequence Startup (Stagger Subsystem Initialization)

Edit `backend/main.py` to add delays between heavy writers:

```python
await trigger_mesh.start()
await asyncio.sleep(0.5)  # Let trigger mesh settle

await setup_subscriptions()
await asyncio.sleep(0.5)  # Let subscriptions settle

await task_executor.start_workers()
await asyncio.sleep(0.5)  # Let workers settle
```

### Option 3: Move to PostgreSQL (Production-Ready)

For production, replace SQLite with Postgres:

```python
# In .env
DATABASE_URL=postgresql+asyncpg://grace:password@localhost/grace_db
```

Postgres handles concurrent writes natively without locks.

## How Grace Will Handle This (Once Running)

After we get Grace started, the agentic error system will:

1. **Detect**: Catch `sqlite3.OperationalError` in `<1ms`
2. **Publish**: Send `error.detected` to Trigger Mesh
3. **Triage**: Input Sentinel classifies as `database_locked`
4. **Playbook**: Selects `clear_lock_files` + `restart_service`
5. **Execute**: Runs fix autonomously (or requests approval)
6. **Resolve**: Publishes `agentic.problem_resolved`
7. **Learn**: Feeds outcome into knowledge base

**But first we need to get her started!**

## Quick Checklist

Before running Grace:
- [ ] Kill all python.exe processes
- [ ] Delete lock files (`databases\*.db-wal`, `*.db-shm`)
- [ ] Run emergency fix OR manually enable WAL mode
- [ ] Wait 3 seconds after killing processes
- [ ] Start only ONE instance of Grace

## After Grace Starts Successfully

You should see:
```
✓ Database initialized (WAL mode enabled)
✓ Grace API server starting...
🤖 ==================== ADVANCED AI SYSTEMS ====================
🎯 Starting Shard Orchestrator...
✓ Orchestrator started with 6 shards
🛡️ Starting Input Sentinel...
✓ Input Sentinel active
📚 Loading expert AI knowledge...
✓ AI expertise preloaded successfully
```

**No database lock errors.**

## Try It Now

```bash
emergency_db_fix.bat
```

This will:
1. Kill processes
2. Backup database
3. Clear locks
4. Enable WAL mode
5. Start Grace

**Then Grace's agentic error system will prevent this from happening again!**
