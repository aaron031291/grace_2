# Task Registry Integration Guide

## Overview

The **Task Registry** is Grace's unified task tracking system. Every subsystem reports tasks here, creating a single source of truth for all work across the system.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Task Registry                             │
│  Single Source of Truth for All Subsystem Tasks             │
│                                                              │
│  • Time tracking (started, completed, duration)             │
│  • Resource usage (CPU, memory, disk, network, storage)     │
│  • Verification enforcement                                  │
│  • Forecasting & anomaly detection                          │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────────┐          ┌──────────┐        ┌──────────┐
    │Healing │          │Learning  │        │ ML/DL    │
    │Playbook│          │Missions  │        │Pipeline  │
    └────────┘          └──────────┘        └──────────┘
         │                    │                    │
         │                    │                    │
    ┌────────┐          ┌──────────┐        ┌──────────┐
    │Coding  │          │   RAG    │        │  Chaos   │
    │Agent   │          │  Index   │        │Campaign  │
    └────────┘          └──────────┘        └──────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                        Message Bus
                     (task.* events)
```

## For Subsystem Developers

### Quick Start with TaskReporter

```python
from backend.utilities.task_reporter import TaskReporter

# 1. Create reporter for your subsystem
reporter = TaskReporter(
    subsystem='healing',      # Your subsystem name
    task_type='playbook'      # Your default task type
)

# 2. Start a task
task_id = await reporter.start_task(
    title="Fix port collision",
    created_by="guardian",
    description="Cleanup port 8000",
    priority=8,
    sla_hours=1.0  # Must complete within 1 hour
)

# 3. Do your work...
result = await run_playbook()

# 4. Complete the task (auto-calculates resource usage)
await reporter.complete_task(
    task_id=task_id,
    success=result.success,
    verification_passed=result.verified
)
```

### Manual Resource Reporting

```python
# If you track resources yourself
await reporter.complete_task(
    task_id=task_id,
    success=True,
    verification_passed=True,
    resource_usage={
        'cpu_seconds': 12.5,
        'memory_peak_mb': 250.0,
        'disk_read_mb': 100.0,
        'disk_write_mb': 50.0,
        'storage_delta_mb': 25.0
    }
)
```

### ML/DL Pipeline Integration

```python
from backend.utilities.task_reporter import TaskReporter

reporter = TaskReporter(subsystem='ml_pipeline', task_type='training_job')

task_id = await reporter.start_task(
    title=f"Train {model_name}",
    created_by="automated_training",
    priority=6
)

# Train model...
result = await train_model()

# Report with ML metrics
await reporter.complete_task(
    task_id=task_id,
    success=result.success,
    verification_passed=result.validation_passed,
    ml_metrics={
        'dataset_size_mb': 500.0,
        'vectors_processed': 100000,
        'tokens_processed': 5000000,
        'model_size_mb': 150.0,
        'epochs_completed': 10
    }
)
```

### RAG Index Building

```python
reporter = TaskReporter(subsystem='rag', task_type='index_build')

task_id = await reporter.start_task(
    title="Rebuild FAISS index",
    created_by="rag_service"
)

# Build index...
result = await rebuild_index()

await reporter.complete_task(
    task_id=task_id,
    success=True,
    verification_passed=True,
    ml_metrics={
        'vectors_processed': result.vector_count,
        'dataset_size_mb': result.total_size_mb
    },
    result_metadata={
        'index_type': 'faiss',
        'dimensions': 1536,
        'total_vectors': result.vector_count
    }
)
```

## Event Bus Integration

Subsystems can also emit events directly to the message bus:

```python
from backend.core.message_bus import message_bus

# Task created
await message_bus.publish('task.created', {
    'task_id': 'healing_playbook_12345',
    'task_type': 'playbook',
    'subsystem': 'healing',
    'title': 'Fix port collision',
    'created_by': 'guardian',
    'metadata': {'playbook_id': 'port_collision_fixer'}
})

# Task started
await message_bus.publish('task.started', {
    'task_id': 'healing_playbook_12345'
})

# Task completed
await message_bus.publish('task.completed', {
    'task_id': 'healing_playbook_12345',
    'success': True,
    'verification_passed': True,
    'resource_usage': {'cpu_seconds': 2.5}
})
```

The Task Registry automatically subscribes to these events and updates the database.

## Subsystems That Should Report

### Currently Integrated
- ✅ Message Bus events (auto-captured)
- ✅ Mission Control events (backward compatible)

### Should Be Integrated

1. **Self-Healing Playbooks**
   ```python
   # In guardian_playbooks.py or healing_orchestrator.py
   from backend.utilities.task_reporter import TaskReporter
   
   reporter = TaskReporter(subsystem='healing', task_type='playbook')
   
   async def execute_playbook(playbook_id):
       task_id = await reporter.start_task(
           title=f"Playbook: {playbook_id}",
           created_by="guardian"
       )
       
       result = await run_playbook(playbook_id)
       
       await reporter.complete_task(
           task_id=task_id,
           success=result.success,
           verification_passed=result.verification_passed
       )
   ```

2. **Coding Agent Work Orders**
   ```python
   # In elite_coding_agent.py
   reporter = TaskReporter(subsystem='coding_agent', task_type='work_order')
   
   async def execute_work_order(order):
       task_id = await reporter.start_task(
           title=order.title,
           created_by=order.requester
       )
       
       result = await implement_fix(order)
       
       await reporter.complete_task(
           task_id=task_id,
           success=result.tests_passed,
           verification_passed=result.tests_passed
       )
   ```

3. **Learning Missions**
   ```python
   # In learning_mission_launcher.py
   reporter = TaskReporter(subsystem='learning', task_type='mission')
   
   async def launch_mission(mission):
       task_id = await reporter.start_task(
           title=mission.title,
           created_by="learning_triage_agent"
       )
       
       result = await execute_mission(mission)
       
       await reporter.complete_task(
           task_id=task_id,
           success=result.success,
           verification_passed=result.score > 0.7
       )
   ```

4. **ML/DL Training Jobs**
   ```python
   # In automated_ml_training.py
   reporter = TaskReporter(subsystem='ml_pipeline', task_type='training_job')
   
   async def train_model(model_config):
       task_id = await reporter.start_task(
           title=f"Train {model_config.name}",
           created_by="automated_trainer"
       )
       
       result = await train(model_config)
       
       await reporter.complete_task(
           task_id=task_id,
           success=result.converged,
           verification_passed=result.validation_acc > 0.8,
           ml_metrics={
               'dataset_size_mb': result.dataset_size,
               'epochs_completed': result.epochs,
               'model_size_mb': result.model_size
           }
       )
   ```

5. **RAG Index Operations**
   ```python
   # In rag_service.py
   reporter = TaskReporter(subsystem='rag', task_type='index_operation')
   
   async def rebuild_index():
       task_id = await reporter.start_task(
           title="Rebuild FAISS index",
           created_by="rag_maintenance"
       )
       
       result = await build_faiss_index()
       
       await reporter.complete_task(
           task_id=task_id,
           success=True,
           verification_passed=result.health_check_passed,
           ml_metrics={'vectors_processed': result.vector_count}
       )
   ```

6. **Remote Access Operations**
   ```python
   # In remote_computer_access.py
   reporter = TaskReporter(subsystem='remote_access', task_type='pc_operation')
   
   async def execute_command(cmd):
       task_id = await reporter.start_task(
           title=f"Execute: {cmd[:50]}",
           created_by="firefox_agent"
       )
       
       result = await run_command(cmd)
       
       await reporter.complete_task(
           task_id=task_id,
           success=result.exit_code == 0,
           verification_passed=True
       )
   ```

7. **Chaos Campaigns**
   ```python
   # In chaos_runner.py
   reporter = TaskReporter(subsystem='chaos', task_type='campaign')
   
   async def run_campaign(campaign):
       task_id = await reporter.start_task(
           title=f"Chaos: {campaign.name}",
           created_by="chaos_orchestrator",
           priority=3  # Lower priority
       )
       
       result = await execute_campaign(campaign)
       
       await reporter.complete_task(
           task_id=task_id,
           success=result.system_recovered,
           verification_passed=result.all_checks_passed
       )
   ```

## API Endpoints

### Query Tasks
```bash
# All active tasks
curl http://localhost:8000/api/task-registry/tasks?status=active

# Healing subsystem tasks
curl http://localhost:8000/api/task-registry/tasks?subsystem=healing

# Completed missions
curl http://localhost:8000/api/task-registry/tasks?subsystem=learning&status=completed

# Specific task details
curl http://localhost:8000/api/task-registry/task/healing_playbook_abc123
```

### Subsystem Status
```bash
# Get status for a subsystem
curl http://localhost:8000/api/task-registry/subsystem/healing

# List all subsystems
curl http://localhost:8000/api/task-registry/subsystems
```

### Forecasting
```bash
# Forecast how long a task will take
curl "http://localhost:8000/api/task-registry/forecast?subsystem=healing&task_type=playbook"

# Returns:
{
  "forecast": {
    "avg_seconds": 15.2,
    "min_seconds": 5.1,
    "max_seconds": 45.8,
    "p95_seconds": 38.5,
    "sample_size": 47,
    "confidence": "high"
  }
}
```

### Anomaly Detection
```bash
# Detect tasks that took too long or used too many resources
curl http://localhost:8000/api/task-registry/metrics/anomalies

# For specific subsystem
curl http://localhost:8000/api/task-registry/metrics/anomalies?subsystem=ml_pipeline
```

### Statistics
```bash
# Overall registry stats
curl http://localhost:8000/api/task-registry/stats
```

## Benefits

### For Operators
- 📊 Single dashboard showing all work across all subsystems
- 🔍 Query "what tasks are currently open in the learning subsystem?"
- 📈 See resource usage trends and forecasts
- 🚨 Detect anomalies (tasks taking 3x longer than normal)

### For Guardian
- ✅ Enforce verification on all task completions
- 📋 See which subsystems have open tasks
- ⏰ Track SLA compliance
- 🔄 Detect stuck tasks or infinite loops

### For Subsystems
- 📝 Easy integration with TaskReporter helper
- 📊 Automatic resource tracking
- 🎯 Forecasting for better scheduling
- 📉 Anomaly alerts when tasks behave unusually

### For Grace (World Model)
- 🧠 Learn from completed tasks (what worked, what failed)
- 🔮 Predict task durations before committing
- 📚 Feed task metadata into RAG for knowledge
- 🎓 ML models can train on task patterns

## Database Schema

### task_registry table
- Identity: task_id, task_type, subsystem
- Timing: started_at, completed_at, duration_seconds
- Resources: cpu_seconds, memory_mb, disk_mb, network_mb, storage_delta_mb
- ML: dataset_size_mb, vectors_processed, tokens_processed, epochs_completed
- Verification: verification_status, verification_passes, verification_failures
- SLA: sla_deadline, sla_met

### task_resource_snapshots table
- Periodic snapshots during long tasks
- Tracks resource usage over time
- Enables progress monitoring

### subsystem_task_metrics table
- Aggregate statistics per subsystem/task_type
- avg/min/max/p95 duration
- Success rates, verification pass rates
- Anomaly thresholds

## Message Bus Events

The registry subscribes to:
- `task.created` - New task registered
- `task.started` - Task execution began
- `task.updated` - Task status changed
- `task.completed` - Task finished successfully
- `task.failed` - Task failed
- `mission.*` - Backward compatibility with existing mission events

## Integration Checklist

For each subsystem:

- [ ] Import TaskReporter
- [ ] Create reporter instance with subsystem name
- [ ] Call `start_task()` when work begins
- [ ] Call `complete_task()` when work finishes
- [ ] Report resource usage (or let it auto-calculate)
- [ ] Include verification status
- [ ] Add ML metrics if applicable

## Example: Healing Orchestrator Integration

```python
# In healing_orchestrator.py

from backend.utilities.task_reporter import TaskReporter

class HealingOrchestrator:
    def __init__(self):
        self.reporter = TaskReporter(
            subsystem='healing',
            task_type='playbook'
        )
    
    async def execute_playbook(self, playbook_id, context):
        # Start task
        task_id = await self.reporter.start_task(
            title=f"Playbook: {playbook_id}",
            created_by="guardian",
            description=context.get('error', 'Unknown issue'),
            priority=context.get('priority', 5)
        )
        
        # Execute
        try:
            result = await self._run_playbook(playbook_id, context)
            
            # Complete with verification
            await self.reporter.complete_task(
                task_id=task_id,
                success=result.success,
                verification_passed=result.verification_passed,
                result_metadata={
                    'playbook_id': playbook_id,
                    'actions_taken': result.actions_taken,
                    'escalated': result.status == 'escalated'
                }
            )
            
            return result
            
        except Exception as e:
            # Report failure
            await self.reporter.fail_task(
                task_id=task_id,
                error_message=str(e)
            )
            raise
```

## Governance Integration

The Task Registry is a Unified Logic component with full governance:

```python
# Registered in server.py boot sequence
from backend.services.task_registry import task_registry
await task_registry.start()

# Guardian can query and enforce
from backend.core.guardian import guardian

# Check for tasks exceeding SLA
overdue_tasks = await task_registry.query_tasks(status='active')
for task in overdue_tasks:
    if task.sla_deadline and now > task.sla_deadline:
        await guardian.escalate_sla_violation(task)

# Detect stuck tasks
stuck_tasks = await find_tasks_active_longer_than('1h')
for task in stuck_tasks:
    await guardian.investigate_stuck_task(task)
```

## Immutable Log Integration

All task events are logged:

```python
# Automatically logged:
- task_registered
- task_started
- task_completed
- task_failed

# Queryable:
SELECT * FROM immutable_log
WHERE action LIKE 'task_%'
ORDER BY timestamp DESC;
```

## World Model / RAG Integration

Task metadata flows into the world model:

```python
# Task completions automatically indexed
# Grace learns:
- "Healing playbooks for port collisions typically take 15s"
- "ML training jobs for sentiment models average 2.5 hours"
- "RAG index rebuilds use 500MB storage delta"

# Used for:
- Better mission scoring
- Resource allocation
- Predictive scheduling
- Anomaly detection
```

## Dashboard Queries

```python
# Get subsystem overview
GET /api/task-registry/subsystem/healing

# Returns:
{
  "subsystem": "healing",
  "task_counts": {
    "active": 2,
    "pending": 5,
    "completed": 143
  },
  "metrics": [
    {
      "task_type": "playbook",
      "avg_duration_seconds": 15.2,
      "success_rate": 0.95,
      "total_completed": 140
    }
  ]
}

# Detect anomalies
GET /api/task-registry/metrics/anomalies?subsystem=ml_pipeline

# Returns tasks taking >3x longer than baseline
```

## Migration Path

### Phase 1: Start Registry (✅ Done)
- Task Registry starts on boot
- Subscribes to message bus
- API endpoints available

### Phase 2: Healing Integration
- Update `healing_orchestrator.py` to use TaskReporter
- All playbook executions tracked
- Resource usage captured

### Phase 3: Learning Integration
- Update `learning_mission_launcher.py`
- Update `learning_triage_agent.py`
- Mission lifecycle fully tracked

### Phase 4: ML/DL Integration
- Training jobs report to registry
- Embedding batches tracked
- Resource forecasting for model training

### Phase 5: RAG Integration
- Index builds tracked
- Refresh operations measured
- Storage growth monitored

### Phase 6: Complete Coverage
- Coding agent work orders
- Remote access operations
- Chaos campaigns
- Every subsystem reports

## Monitoring

```bash
# Watch task events
tail -f logs/grace.log | grep "TASK-REGISTRY"

# Query open tasks
curl http://localhost:8000/api/task-registry/tasks?status=active

# Monitor specific subsystem
curl http://localhost:8000/api/task-registry/subsystem/healing

# Check for anomalies
curl http://localhost:8000/api/task-registry/metrics/anomalies
```

## Next Steps

1. **Integrate healing orchestrator** - Add TaskReporter to playbook execution
2. **Integrate learning missions** - Report mission lifecycle
3. **Add verification hooks** - Enforce verification before marking complete
4. **Enable forecasting** - Use historical data for scheduling
5. **Build dashboard** - Web UI showing all subsystem tasks

The foundation is ready - now wire each subsystem to report their work!
