# Agent Lifecycle Management System - COMPLETE ✅

**Date:** 2025-11-12  
**Status:** ✅ ALL TESTS PASSED (8/8)  
**Architecture:** BaseComponent + Clarity Contracts

---

## Executive Summary

Successfully implemented a **production-ready agent lifecycle management system** where sub-agents are defined as BaseComponents with full clarity contracts. Grace can now spawn agents on-demand, execute jobs, monitor performance, and terminate agents when finished—all with complete audit trails and revocation capabilities.

### **Key Features**

✅ **BaseComponent Integration** - All agents inherit clarity contracts  
✅ **Manifest Registration** - Registered in clarity manifest on spawn  
✅ **Schema Entries** - Tracked in `memory_sub_agents` table  
✅ **Trust Metrics** - Computed and updated based on performance  
✅ **Job-Based Lifecycle** - Spawn → Execute → Terminate  
✅ **Heartbeat Monitoring** - Alive signals every 30s  
✅ **Revocation System** - Untrusted agents can be revoked  
✅ **Job Queue** - Async job processing with concurrency control  
✅ **Full Audit Trail** - All actions logged in clarity manifest  

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              AGENT LIFECYCLE MANAGER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   JOB QUEUE   │───▶│   SPAWNER   │───▶│ ACTIVE AGENTS   │  │
│  └───────────────┘    └─────────────┘    └─────────────────┘  │
│                                                    │             │
│                                                    ↓             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              BaseAgentComponent                          │  │
│  │  • Manifest (clarity registration)                       │  │
│  │  • Schema (memory_sub_agents entry)                      │  │
│  │  • Trust Metrics (computed from performance)             │  │
│  │  • Heartbeat (alive signal)                              │  │
│  │  • Constraints (resource limits, permissions)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                        │                                         │
│         ┌──────────────┼──────────────┐                         │
│         ↓              ↓               ↓                         │
│  ┌──────────┐   ┌────────────┐  ┌─────────────┐               │
│  │ Schema   │   │ Ingestion  │  │ Cross-Domain│               │
│  │ Inference│   │  Agent     │  │  Learning   │               │
│  └──────────┘   └────────────┘  └─────────────┘               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         MONITORING & REVOCATION                          │  │
│  │  • Health checks (trust, heartbeat)                      │  │
│  │  • Idle cleanup (10 min timeout)                         │  │
│  │  • Lifetime limits (60 min max)                          │  │
│  │  • Trust threshold (revoke if <0.3)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## BaseAgentComponent

All agents inherit from `BaseAgentComponent` which provides:

### **Clarity Contracts**

1. **Manifest Entry** - Registered in clarity manifest
   ```python
   {
     'component_id': 'schema_inference_a1b2c3d4',
     'component_type': 'sub_agent',
     'name': 'Schema Inference Agent',
     'capabilities': ['file_analysis', 'schema_inference'],
     'mission': 'Analyze files and infer optimal schema',
     'constraints': {'read_only': True},
     'registered_at': '2025-11-12T10:00:00Z',
     'status': 'active'
   }
   ```

2. **Schema Entry** - Row in `memory_sub_agents` table
   - agent_id, agent_name, agent_type
   - mission, capabilities, constraints
   - status, current_task
   - tasks_completed, tasks_failed, success_rate
   - trust_score, last_active_at
   - heartbeat_interval_sec
   - governance_stamp

3. **Trust Metrics** - Computed from:
   - Initial trust based on constraints
   - Updated based on job success/failure
   - Formula: `trust = 0.7 * success_rate + 0.3 * previous_trust`

4. **Heartbeat** - Alive signal sent every cycle

5. **Constraints** - Resource limits and permissions
   - `read_only` - Cannot modify data
   - `requires_approval` - Changes need approval
   - `max_file_size_mb` - File size limit
   - `requires_governance` - Governance checks
   - `auto_approve_threshold` - Auto-approve if confidence ≥ threshold

### **Lifecycle Methods**

```python
class BaseAgentComponent:
    async def initialize():
        """Register manifest + schema + compute trust"""
    
    async def execute_job(job):
        """Execute job and track results"""
    
    async def heartbeat():
        """Send alive signal"""
    
    async def terminate():
        """Graceful shutdown + deregister"""
    
    async def get_status():
        """Get current status"""
```

---

## Built-In Agent Types

### 1. SchemaInferenceAgent ✅

**Purpose:** Analyze files and infer optimal schema structure

**Capabilities:**
- `file_analysis` - Extract content from files
- `content_extraction` - Parse documents, code, data
- `schema_inference` - LLM-powered table recommendation
- `field_extraction` - Extract structured fields

**Constraints:**
- `read_only: true` - Cannot modify tables
- `max_file_size_mb: 100` - 100MB limit
- `requires_approval: true` - Proposals need approval

**Job Example:**
```python
job = {
    'file_path': 'training_data/document.pdf',
    'job_type': 'schema_inference'
}

result = await agent_lifecycle_manager.execute_job(
    'schema_inference',
    job
)

# Result:
# {
#   'job_id': 'abc123',
#   'success': True,
#   'result': {
#     'analysis': {...},
#     'proposal': {
#       'table_name': 'memory_documents',
#       'confidence': 0.95,
#       'extracted_fields': {...}
#     }
#   },
#   'duration_ms': 1500
# }
```

### 2. IngestionAgent ✅

**Purpose:** Ingest analyzed data into memory tables

**Capabilities:**
- `table_insertion` - Insert rows
- `data_validation` - Validate before insert
- `trust_computation` - Compute trust scores
- `contradiction_check` - Check for conflicts

**Constraints:**
- `requires_governance: true` - All inserts approved
- `auto_approve_threshold: 0.90` - Auto if ≥90% confidence
- `max_batch_size: 100` - Max rows per batch

**Job Example:**
```python
job = {
    'table_name': 'memory_documents',
    'row_data': {
        'file_path': 'doc.pdf',
        'title': 'My Document',
        'source_type': 'upload',
        'summary': 'Document summary',
        'key_topics': {'ai': 1},
        'token_count': 500,
        'risk_level': 'low'
    }
}

result = await agent_lifecycle_manager.execute_job(
    'ingestion',
    job
)

# Result:
# {
#   'success': True,
#   'row_id': 'uuid-here',
#   'trust_score': 0.87,
#   'table_name': 'memory_documents'
# }
```

### 3. CrossDomainLearningAgent ✅

**Purpose:** Perform cross-domain learning across tables

**Capabilities:**
- `cross_table_query` - Query multiple tables
- `pattern_extraction` - Find patterns
- `insight_generation` - Generate insights
- `knowledge_synthesis` - Synthesize knowledge

**Constraints:**
- `read_only: true` - No modifications
- `max_tables: 10` - Query up to 10 tables
- `max_rows_per_table: 1000` - 1000 rows max

**Job Example:**
```python
job = {
    'query_spec': {
        'documents': {},
        'codebases': {},
        'prompts': {}
    }
}

result = await agent_lifecycle_manager.execute_job(
    'cross_domain_learning',
    job
)

# Result:
# {
#   'success': True,
#   'results': {...},
#   'patterns': {
#     'total_rows': 150,
#     'tables_queried': 3
#   }
# }
```

---

## Agent Lifecycle Manager

### **Spawn Agent**

```python
from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager

# Spawn specific agent type
agent = await agent_lifecycle_manager.spawn_agent('schema_inference')

# Agent automatically:
# 1. Registers in clarity manifest
# 2. Creates entry in memory_sub_agents
# 3. Computes initial trust score
# 4. Sets status to 'idle'
```

### **Execute Job**

```python
# Option 1: One-time execution (spawn + execute + terminate)
result = await agent_lifecycle_manager.execute_job(
    'ingestion',
    job,
    reuse_agent=False  # Terminate after job
)

# Option 2: Reuse agent (spawn once, execute many)
result = await agent_lifecycle_manager.execute_job(
    'schema_inference',
    job,
    reuse_agent=True  # Keep agent alive
)
```

### **Job Queue (Async)**

```python
# Submit jobs to queue
job_id1 = await agent_lifecycle_manager.submit_job_to_queue('ingestion', job1)
job_id2 = await agent_lifecycle_manager.submit_job_to_queue('ingestion', job2)
job_id3 = await agent_lifecycle_manager.submit_job_to_queue('ingestion', job3)

# Process queue with concurrency control
await agent_lifecycle_manager.process_job_queue(max_concurrent=5)

# Jobs processed asynchronously with agent pooling
```

### **Terminate Agent**

```python
await agent_lifecycle_manager.terminate_agent(agent_id)

# Agent automatically:
# 1. Updates status to 'offline'
# 2. Deregisters from clarity manifest
# 3. Logs termination event
# 4. Final stats recorded
```

### **Revoke Agent**

```python
await agent_lifecycle_manager.revoke_agent(
    agent_id,
    reason="Trust score too low"
)

# Agent is:
# 1. Added to revoked list
# 2. Immediately terminated
# 3. Logged in clarity manifest
# 4. Cannot be reused
```

---

## Monitoring & Lifecycle

### **Automatic Monitoring**

```python
# Start monitoring (runs every 30s)
await agent_lifecycle_manager.start_monitoring()

# Monitors:
# 1. Heartbeat (revoke if missed >2 min)
# 2. Trust score (revoke if <0.3)
# 3. Idle time (terminate if idle >10 min)
# 4. Lifetime (terminate if >60 min)
```

### **Health Checks**

Every 30 seconds, the monitor checks:

1. **Heartbeat** - Agent still alive?
   - If missed >2 minutes → Warning logged
   - Agent sends heartbeat automatically

2. **Trust Score** - Performance acceptable?
   - If trust <0.3 → Agent revoked
   - Trust updated after each job

3. **Idle Time** - Agent doing work?
   - If idle >10 minutes → Terminated
   - Saves resources

4. **Lifetime** - Agent too old?
   - If alive >60 minutes → Terminated
   - Prevents resource leaks

### **Get Metrics**

```python
metrics = await agent_lifecycle_manager.get_metrics()

# {
#   'active_agents': 5,
#   'revoked_agents': 1,
#   'agents_by_type': {
#     'SchemaInferenceAgent': 2,
#     'IngestionAgent': 3
#   },
#   'total_jobs_executed': 47,
#   'average_trust_score': 0.85,
#   'pending_jobs': 3,
#   'completed_jobs': 44
# }
```

### **Get Agent Status**

```python
status = await agent_lifecycle_manager.get_agent_status(agent_id)

# {
#   'agent_id': 'schema_inference_a1b2c3d4',
#   'agent_name': 'Schema Inference Agent a1b2c3d4',
#   'agent_type': 'specialist',
#   'status': 'busy',
#   'current_job': 'job_xyz789',
#   'jobs_completed': 12,
#   'jobs_failed': 1,
#   'success_rate': 0.923,
#   'trust_score': 0.89,
#   'last_heartbeat': '2025-11-12T10:30:00Z',
#   'uptime_seconds': 1847,
#   'metrics': {
#     'spawned_at': '2025-11-12T10:00:00Z',
#     'last_job_at': '2025-11-12T10:29:45Z',
#     'jobs_executed': 13
#   },
#   'is_revoked': False
# }
```

---

## API Endpoints

### Agent Lifecycle

```bash
# Spawn agent
POST /api/agent-lifecycle/spawn
Body: {"agent_type": "schema_inference", "instance_id": "optional"}

# Execute job
POST /api/agent-lifecycle/execute-job
Body: {
  "agent_type": "ingestion",
  "job": {...},
  "reuse_agent": false
}

# Submit to queue
POST /api/agent-lifecycle/submit-job
Body: {"agent_type": "ingestion", "job": {...}}

# Process queue
POST /api/agent-lifecycle/process-queue?max_concurrent=5

# Terminate agent
POST /api/agent-lifecycle/terminate/{agent_id}

# Revoke agent
POST /api/agent-lifecycle/revoke
Body: {"agent_id": "...", "reason": "..."}
```

### Monitoring

```bash
# Get all agents
GET /api/agent-lifecycle/agents

# Get specific agent
GET /api/agent-lifecycle/agents/{agent_id}

# Get metrics
GET /api/agent-lifecycle/metrics

# Start/stop monitoring
POST /api/agent-lifecycle/monitoring/start
POST /api/agent-lifecycle/monitoring/stop
```

---

## Usage Examples

### Example 1: Process Files On-Demand

```python
from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager

# Start monitoring
await agent_lifecycle_manager.start_monitoring()

# Process a file
file_path = "training_data/document.pdf"

# Step 1: Infer schema
schema_job = {'file_path': file_path}
schema_result = await agent_lifecycle_manager.execute_job(
    'schema_inference',
    schema_job
)

# Step 2: Ingest if confident
if schema_result['result']['confidence'] >= 0.8:
    ingestion_job = {
        'table_name': schema_result['result']['recommended_table'],
        'row_data': schema_result['result']['proposal']['extracted_fields']
    }
    
    ingestion_result = await agent_lifecycle_manager.execute_job(
        'ingestion',
        ingestion_job
    )
    
    print(f"Ingested to {ingestion_result['result']['table_name']}")
    print(f"Trust score: {ingestion_result['result']['trust_score']:.2f}")
```

### Example 2: Batch Processing with Queue

```python
# Submit batch of files to queue
for file_path in file_list:
    job = {'file_path': file_path}
    job_id = await agent_lifecycle_manager.submit_job_to_queue(
        'schema_inference',
        job
    )
    print(f"Queued: {job_id}")

# Process with concurrency
await agent_lifecycle_manager.process_job_queue(max_concurrent=10)

# Agents spawned as needed, auto-terminated when idle
```

### Example 3: Monitor Agent Health

```python
# Get all active agents
agents = await agent_lifecycle_manager.get_all_agents()

for agent in agents:
    print(f"{agent['agent_name']}:")
    print(f"  Status: {agent['status']}")
    print(f"  Jobs: {agent['jobs_completed']}/{agent['jobs_completed'] + agent['jobs_failed']}")
    print(f"  Success: {agent['success_rate']:.1%}")
    print(f"  Trust: {agent['trust_score']:.2f}")
    
    # Revoke if trust too low
    if agent['trust_score'] < 0.4:
        await agent_lifecycle_manager.revoke_agent(
            agent['agent_id'],
            f"Trust score {agent['trust_score']:.2f} below threshold"
        )
```

---

## Trust Score Computation

### Initial Trust

Based on constraints:
- Base: 0.5
- +0.1 if `read_only`
- +0.1 if `requires_approval`
- +0.05 if `max_file_size_mb` set
- +0.1 if specialized (≤3 capabilities)
- -0.1 if `orchestrator` type

### Updated After Each Job

```python
total_jobs = jobs_completed + jobs_failed
success_rate = jobs_completed / total_jobs

# Exponential moving average
new_trust = (0.7 * success_rate) + (0.3 * previous_trust)
trust_score = clamp(new_trust, 0.0, 1.0)
```

### Revocation Threshold

If `trust_score < 0.3` → Agent revoked automatically

---

## Testing Results

**Test Suite:** `test_agent_lifecycle.py`  
**Status:** ✅ ALL 8 TESTS PASSED

1. ✅ Spawn Schema Inference Agent (BaseComponent)
2. ✅ Execute Job (schema inference)
3. ✅ Spawn and Execute Ingestion Agent
4. ✅ Execute Cross-Domain Learning Job
5. ✅ Job Queue System (async processing)
6. ✅ Agent Lifecycle Monitoring
7. ✅ Agent Termination
8. ✅ Clarity Contract Integration

```bash
python test_agent_lifecycle.py
# SUCCESS: AGENT LIFECYCLE SYSTEM OPERATIONAL
```

---

## Production Deployment

### 1. Start Lifecycle Manager

```python
from backend.agents.agent_lifecycle_manager import agent_lifecycle_manager

await agent_lifecycle_manager.start_monitoring()
```

### 2. Process Files

Files dropped → Auto-detected → Jobs queued → Agents spawned → Executed → Terminated

### 3. Monitor

```bash
# Get metrics
curl http://localhost:8000/api/agent-lifecycle/metrics

# Get active agents
curl http://localhost:8000/api/agent-lifecycle/agents

# Revoke if needed
curl -X POST http://localhost:8000/api/agent-lifecycle/revoke \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "...", "reason": "..."}'
```

---

## Summary

✅ **COMPLETE AGENT LIFECYCLE SYSTEM**

**What We Built:**
- 🧬 **BaseComponent** architecture with clarity contracts
- 📋 **3 specialized agents** (schema, ingestion, learning)
- 🔄 **Job-based lifecycle** (spawn → execute → terminate)
- 📊 **Full monitoring** (health, trust, heartbeat)
- ⛔ **Revocation system** (untrusted agents blocked)
- 📥 **Job queue** (async processing)
- 🔍 **Audit trail** (all actions in clarity manifest)

**Capabilities:**
- Spawn agents on-demand
- Execute jobs through agents
- Monitor agent health
- Terminate when finished
- Revoke misbehaving agents
- Full clarity integration

**Status:** PRODUCTION-READY 🚀
