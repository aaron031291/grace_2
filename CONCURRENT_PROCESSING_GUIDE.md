# Concurrent Processing & Background Tasks - Librarian Kernel

## Overview

The Librarian Kernel is designed for **concurrent background processing** of multiple tasks simultaneously. When books (or any files) are detected, the Librarian spawns specialist sub-agents that run in parallel, processing multiple books at once without blocking the UI.

## Architecture

### Background Coordinator Loop

The **coordinator loop** runs on a background asyncio task and continuously:
1. Monitors 3 separate queues (schema, ingestion, trust audit)
2. Checks resource limits (max concurrent agents)
3. Spawns sub-agents when capacity is available
4. Processes multiple items from each queue concurrently

**Location**: [backend/kernels/librarian_kernel.py](file:///c:/Users/aaron/grace_2/backend/kernels/librarian_kernel.py) → `_coordinator_loop()`

```python
async def _coordinator_loop(self):
    while self._running:
        # Check capacity per queue type
        max_schema_agents = 2      # Up to 2 schema agents
        max_ingestion_agents = 3   # Up to 3 books ingesting simultaneously
        max_trust_agents = 2       # Up to 2 verification jobs
        
        # Spawn multiple agents concurrently
        while (schema_queue.not_empty and 
               schema_agents < max_schema_agents):
            spawn_agent('schema_scout')  # Runs in background
        
        while (ingestion_queue.not_empty and 
               ingestion_agents < max_ingestion_agents):
            spawn_agent('ingestion_runner')  # Parallel processing
```

### Resource Limits (Configurable)

**Per-Queue Concurrency:**
- `max_schema_agents`: 2 (default) - How many schema proposals can run simultaneously
- `max_ingestion_agents`: 3 (default) - **How many books can process at once**
- `max_trust_agents`: 2 (default) - How many verification jobs concurrently
- `max_concurrent_agents`: 5 (default) - Total cap across all types

**Configure in**: `backend/kernels/librarian_kernel.py` → `self.config`

```python
self.config = {
    'max_concurrent_agents': 5,
    'max_schema_agents': 2,
    'max_ingestion_agents': 3,  # Increase to 5 for faster bulk processing
    'max_trust_agents': 2
}
```

## Workflow: Drop 14 Books

Here's what happens when you drop 14 books into `grace_training/documents/books/`:

### 1. File Detection (Immediate)
```
FileSystemWatcher detects:
- book_1.pdf
- book_2.pdf
- ...
- book_14.pdf
```

Each file triggers:
- Event: `file.created` with `is_book=true`
- Queued to: `schema_queue` AND `ingestion_queue`

### 2. Concurrent Schema Proposals
```
Coordinator spawns up to 2 schema agents concurrently:

Agent schema_scout_1 → Analyzing book_1.pdf
Agent schema_scout_2 → Analyzing book_2.pdf
(as soon as one finishes, book_3.pdf starts)
```

Each schema agent:
- Analyzes file type, location, metadata
- Proposes `memory_documents` entry
- Auto-approves if confidence >= 0.85
- Logs to `memory_librarian_log`

### 3. Parallel Book Ingestion
```
Coordinator spawns up to 3 ingestion agents at once:

Agent ingestion_runner_1 → Processing book_1.pdf (chapter 1/10)
Agent ingestion_runner_2 → Processing book_3.pdf (extracting text)
Agent ingestion_runner_3 → Processing book_5.pdf (generating embeddings)
```

Each ingestion agent runs independently:
- Extracts metadata
- Extracts text (can take minutes for large PDFs)
- Detects chapters
- Creates chunks (stored in DB)
- Triggers ML embedding pipeline
- Generates summaries

**All 3 run simultaneously in background tasks!**

### 4. Automatic Verification
```
As each book completes ingestion:

Agent trust_auditor_1 → Verifying book_1.pdf (3 tests)
Agent trust_auditor_2 → Verifying book_3.pdf (checking chunks)
```

Verification includes:
- Test 1: Extraction quality (chunks exist?)
- Test 2: Comprehension (insights generated?)
- Test 3: Chunk consistency (no gaps?)
- Calculate trust score
- Update `memory_documents.trust_score`

### 5. Dashboard Updates

Progress is visible via:
- `/api/books/stats` - Real-time counts
- `/api/books/recent` - Latest completions
- `/api/books/activity` - Agent activity stream
- Librarian logs - Detailed events

## Sub-Agent Lifecycle

Every sub-agent follows this pattern:

### 1. Spawn (BaseKernel)
```python
agent_id = await kernel.spawn_agent(
    agent_type='ingestion_runner',
    task_data={'path': 'book_1.pdf', 'type': 'book_ingestion'},
    priority='high'
)
```

Creates:
- Unique `agent_id` (e.g., `ingestion_runner_1731513600.123`)
- Entry in `memory_sub_agents` table
- Background `asyncio.create_task()`

### 2. Execute (Background)
```python
async def _run_agent(agent_id, agent):
    # Runs in separate async task
    result = await agent.execute()
    
    # Logs to memory_sub_agents
    await _log_agent_completion(agent_id, success, result)
```

The agent runs completely independently:
- Does NOT block the coordinator loop
- Does NOT block other agents
- Does NOT block the UI/API

### 3. Completion
- Logs task completion to `memory_sub_agents`
- Updates status: `'idle'` or `'error'`
- Publishes event: `agent.completed` or `agent.failed`
- Auto-cleans up (removed from `_sub_agents` dict)

## Logging & Transparency

### memory_sub_agents Table

Every agent is tracked:
```sql
SELECT agent_id, agent_type, status, current_task, tasks_completed
FROM memory_sub_agents
WHERE agent_type IN ('schema_scout', 'ingestion_runner', 'trust_auditor')
ORDER BY last_active_at DESC;
```

Fields:
- `agent_id`: Unique identifier
- `agent_type`: `schema_scout`, `ingestion_runner`, `trust_auditor`
- `status`: `active`, `running`, `idle`, `error`, `terminated`
- `current_task`: What the agent is currently doing
- `tasks_completed`: Count of successful tasks
- `tasks_failed`: Count of failed tasks
- `success_rate`: `tasks_completed / (completed + failed)`
- `trust_score`: Agent's own trust score (updated over time)

### memory_librarian_log Table

All actions are logged:
```sql
SELECT action_type, target_path, details, timestamp
FROM memory_librarian_log
WHERE action_type IN ('schema_proposal', 'ingestion_launch', 'trust_update')
ORDER BY timestamp DESC
LIMIT 100;
```

Logged events:
- `schema_proposal` - When schema is proposed
- `schema_approval` - When proposal is approved/rejected
- `ingestion_launch` - When ingestion starts
- `ingestion_complete` - When ingestion finishes
- `trust_update` - When trust score changes
- `automation_rule_executed` - When automation triggers

## Example: Processing 14 Books

### Timeline (Concurrent Processing)

**T+0s**: Drop 14 books
```
FileSystemWatcher: 14 files detected
Queue status:
  schema_queue: 14 items
  ingestion_queue: 14 items
```

**T+1s**: Schema agents start
```
Active agents:
  schema_scout_1 → book_1.pdf
  schema_scout_2 → book_2.pdf
```

**T+2s**: First schema completes, next starts
```
Completed: schema_scout_1 (book_1 approved)
Active agents:
  schema_scout_2 → book_2.pdf
  schema_scout_3 → book_3.pdf
```

**T+5s**: Ingestion begins (concurrent)
```
Active agents:
  schema_scout_4 → book_5.pdf
  ingestion_runner_1 → book_1.pdf (extracting text)
  ingestion_runner_2 → book_2.pdf (extracting text)
  ingestion_runner_3 → book_3.pdf (extracting text)
```

**T+60s**: First book completes, verification starts
```
Completed: ingestion_runner_1 (book_1)
Active agents:
  ingestion_runner_2 → book_2.pdf (chunking)
  ingestion_runner_3 → book_3.pdf (embedding)
  ingestion_runner_4 → book_4.pdf (extracting)
  trust_auditor_1 → book_1.pdf (verifying)
```

**T+300s**: Multiple books done, more processing
```
Queue status:
  ingestion_queue: 8 remaining
  trust_audit_queue: 6 pending

Active agents:
  ingestion_runner_7 → book_9.pdf
  ingestion_runner_8 → book_10.pdf
  ingestion_runner_9 → book_11.pdf
  trust_auditor_3 → book_5.pdf
  trust_auditor_4 → book_6.pdf
```

**T+600s**: All done
```
Completed: 14 books
  Total agents spawned: 42
    - 14 schema_scout
    - 14 ingestion_runner
    - 14 trust_auditor
  Average processing time: 60s per book
  Total wall time: 10 minutes (vs. 14 hours sequential!)
```

## Monitoring Active Work

### Get Queue Status
```python
GET /api/librarian/status

Response:
{
  "status": "active",
  "queues": {
    "schema": 5,        # 5 items waiting
    "ingestion": 8,     # 8 books queuing
    "trust_audit": 3    # 3 pending verification
  },
  "active_agents": {
    "schema_scout": 2,
    "ingestion_runner": 3,
    "trust_auditor": 1
  },
  "capacity": {
    "total": "6/5",  # Over capacity (finishing up)
    "available": 0
  }
}
```

### View Active Agents
```python
GET /api/librarian/agents

Response:
[
  {
    "agent_id": "ingestion_runner_1731513600.123",
    "type": "ingestion_runner",
    "status": "running",
    "current_task": "Processing book_3.pdf",
    "started_at": "2024-11-13T10:30:00Z",
    "runtime_sec": 45
  },
  ...
]
```

### Watch Progress
```python
GET /api/books/activity?limit=20

Response:
[
  {
    "timestamp": "2024-11-13T10:30:45Z",
    "action": "ingestion_complete",
    "target": "book_1.pdf",
    "details": {"chunks": 120, "insights": 15}
  },
  {
    "timestamp": "2024-11-13T10:30:30Z",
    "action": "ingestion_launch",
    "target": "book_3.pdf",
    "details": {"pipeline": "book_ingestion", "priority": "high"}
  },
  ...
]
```

## Performance Tuning

### For Faster Bulk Processing

Increase concurrency limits:
```python
# In librarian_kernel.py
self.config = {
    'max_concurrent_agents': 10,      # Up from 5
    'max_schema_agents': 3,           # Up from 2
    'max_ingestion_agents': 5,        # Up from 3 (5 books at once!)
    'max_trust_agents': 2             # Keep at 2
}
```

**Warning**: Higher concurrency = more CPU/memory usage. Monitor system resources.

### For Resource-Constrained Systems

Lower limits:
```python
self.config = {
    'max_concurrent_agents': 3,
    'max_schema_agents': 1,
    'max_ingestion_agents': 1,        # Process one book at a time
    'max_trust_agents': 1
}
```

### For Prioritization

Adjust queue processing in coordinator loop:
```python
# Process ingestion before schema (books first)
if not self.ingestion_queue.empty():
    # Spawn ingestion agents first
    
if not self.schema_queue.empty():
    # Then schema
```

## API Endpoints

### Trigger Manual Ingestion
```python
POST /api/librarian/ingest
{
  "file_path": "grace_training/documents/books/my_book.pdf",
  "priority": "high"  # Jump the queue
}
```

### Pause Processing
```python
POST /api/librarian/pause
# Stops spawning new agents, lets current ones finish
```

### Resume Processing
```python
POST /api/librarian/resume
```

### Get Sub-Agent Fleet Stats
```python
GET /api/librarian/agents/stats

Response:
{
  "total_spawned": 156,
  "currently_active": 4,
  "total_completed": 148,
  "total_failed": 4,
  "success_rate": 0.973,
  "by_type": {
    "schema_scout": {"spawned": 52, "success_rate": 1.0},
    "ingestion_runner": {"spawned": 52, "success_rate": 0.96},
    "trust_auditor": {"spawned": 52, "success_rate": 0.95}
  }
}
```

## Key Takeaways

✅ **Concurrent**: Up to 3 books ingest simultaneously  
✅ **Background**: All processing happens asynchronously  
✅ **Non-blocking**: UI remains responsive  
✅ **Logged**: Full transparency in `memory_sub_agents`  
✅ **Monitored**: Real-time dashboard tracking  
✅ **Configurable**: Adjust limits for your hardware  
✅ **Automatic**: Just drop files, Librarian handles the rest  

## Summary

The Librarian's concurrent processing system is production-ready for bulk ingestion. Drop your 14 books, and the system will:
1. Detect all 14 instantly
2. Queue them for processing
3. Run 3 at a time through ingestion
4. Verify each one after completion
5. Log everything to `memory_sub_agents` and `memory_librarian_log`
6. Update the dashboard in real-time

You can monitor progress via the API or dashboard while Grace learns from all the books simultaneously. The whole process is autonomous, parallel, and fully auditable.
