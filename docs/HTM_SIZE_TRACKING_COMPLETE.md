# HTM Size Tracking Implementation Complete

## Overview

Extended HTM (Hierarchical Task Manager) to track payload sizes alongside timing data, enabling bandwidth-aware scheduling and data volume analysis.

**Key Insight**: HTM can now reason about both **how long** and **how heavy** each task is, enabling smarter resource allocation and bottleneck identification.

---

## Components Delivered

### 1. Database Schema Extensions ([htm_models.py](file:///c:/Users/aaron/grace_2/backend/models/htm_models.py))

#### HTMTask - Added Fields:
```python
# Data volume metrics
data_size_bytes = Column(Integer, nullable=True)  # Total payload size
input_count = Column(Integer, nullable=True)  # Number of items processed
output_size_bytes = Column(Integer, nullable=True)  # Result data size

# Throughput metrics (calculated)
bytes_per_second = Column(Float, nullable=True)
items_per_second = Column(Float, nullable=True)
```

#### HTMTaskAttempt - Added Fields:
```python
# Data volume (per attempt)
data_size_bytes = Column(Integer, nullable=True)
input_count = Column(Integer, nullable=True)
```

#### HTMMetrics - Added Fields:
```python
# Data volume metrics
total_data_bytes = Column(Integer, default=0)
total_input_count = Column(Integer, default=0)
avg_data_size_bytes = Column(Float, default=0.0)

# Data volume percentiles
p50_data_size_bytes = Column(Integer, default=0)
p95_data_size_bytes = Column(Integer, default=0)
p99_data_size_bytes = Column(Integer, default=0)

# Throughput metrics
avg_bytes_per_second = Column(Float, default=0.0)
avg_items_per_second = Column(Float, default=0.0)
p95_bytes_per_second = Column(Float, default=0.0)
```

---

### 2. Size Tracking Utilities ([htm_size_tracker.py](file:///c:/Users/aaron/grace_2/backend/core/htm_size_tracker.py))

#### Size Formatting:
```python
format_bytes(1536000)  # → "1.46 MB"
parse_bytes("1.5 GB")  # → 1610612736
```

#### Task Classification:
```python
class TaskSizeClass:
    TINY     # < 1 KB
    SMALL    # 1 KB - 1 MB
    MEDIUM   # 1 MB - 100 MB
    LARGE    # 100 MB - 1 GB
    HUGE     # 1 GB - 10 GB
    MASSIVE  # > 10 GB

classify_task_size(5242880)  # 5 MB → TaskSizeClass.MEDIUM
```

#### Throughput Calculation:
```python
calculate_throughput(
    data_size_bytes=10 * 1024 ** 2,  # 10 MB
    execution_time_ms=2000             # 2 seconds
)  # → 5242880.0 bytes/sec (5 MB/s)
```

#### Payload Size Calculators:
```python
# For files
total_bytes, file_count = PayloadSizeCalculator.for_files([
    "/path/to/file1.pdf",
    "/path/to/file2.pdf"
])

# For text
text_bytes = PayloadSizeCalculator.for_text("Hello world")

# For embeddings
embedding_bytes = PayloadSizeCalculator.for_embeddings(
    num_vectors=1000,
    dimensions=1536  # OpenAI ada-002
)

# For ingestion job
metrics = PayloadSizeCalculator.for_ingestion_job(
    file_paths=[...],
    include_embeddings=True
)
# {
#   "input_size_bytes": 52428800,
#   "input_count": 5,
#   "estimated_output_bytes": 307200,
#   "size_class": "large"
# }
```

#### Size Recommendations:
```python
recommendations = get_size_recommendations(
    data_size_bytes=500 * 1024 ** 2,  # 500 MB
    task_type="ingestion"
)
# {
#   "size_class": "large",
#   "recommended_worker": "heavy",
#   "suggested_timeout_ms": 600000,  # 10 min
#   "batch_recommended": False,
#   "warnings": ["Large payload - consider chunking"]
# }
```

---

### 3. Size Metrics Aggregator ([htm_size_metrics.py](file:///c:/Users/aaron/grace_2/backend/core/htm_size_metrics.py))

#### Automatic Aggregation:
- Runs every 5 minutes
- Calculates size statistics from completed tasks
- Publishes to message bus (`htm.size.stats`)

#### Metrics Provided:
```python
{
    "total_bytes_processed": 10737418240,  # 10 GB
    "total_data_processed_human": "10.0 GB",
    "total_items_processed": 1250,
    "avg_task_size_bytes": 8589934.59,
    "avg_task_size_human": "8.19 MB",
    "median_task_size_bytes": 5242880,
    "p95_task_size_bytes": 52428800,
    "p95_task_size_human": "50.0 MB",
    "p99_task_size_bytes": 104857600,
    "avg_throughput_bytes_per_sec": 2621440.0,
    "p95_throughput_bytes_per_sec": 5242880.0,
    "size_distribution": {
        "tiny": 250,
        "small": 500,
        "medium": 400,
        "large": 90,
        "huge": 10
    },
    "by_task_type": {
        "ingestion": {
            "count": 800,
            "total_bytes": 8589934592,
            "avg_bytes": 10737418.24,
            "total_human": "8.0 GB",
            "avg_human": "10.24 MB"
        }
    }
}
```

#### Analysis API:
```python
analysis = await htm_size_metrics.get_size_analysis(
    task_type="ingestion",
    hours=24
)
# Returns comprehensive statistics + recommendations
```

---

### 4. Size-Aware Scheduler ([htm_size_aware_scheduler.py](file:///c:/Users/aaron/grace_2/backend/core/htm_size_aware_scheduler.py))

#### Worker Profiles:
```python
# Register workers with capacity
htm_size_scheduler.register_worker(
    worker_id="heavy_worker_1",
    worker_type="heavy",
    max_concurrent=2,
    max_data_gb=50.0
)

# Worker types:
# - light: Handles tiny/small tasks (< 1 MB)
# - standard: Handles small/medium/large (up to 1 GB)
# - heavy: Handles large/huge/massive (up to 50 GB)
```

#### Intelligent Scheduling:
```python
schedule = await htm_size_scheduler.schedule_task(
    task_id="task_123",
    task_type="ingestion",
    data_size_bytes=500 * 1024 ** 2,  # 500 MB
    priority="normal"
)

# Returns scheduling decision:
{
    "worker_id": "heavy_worker_1",
    "schedule_now": True,
    "recommended_delay_seconds": 0,
    "should_batch": False,
    "reasoning": "Assigned to heavy worker (utilization: 45.2%)",
    "worker_type": "heavy",
    "current_utilization": 0.452
}
```

#### Scheduling Strategies:

**1. Size-Based Routing:**
- Tiny/small tasks → light workers
- Medium tasks → standard workers
- Large/huge/massive → heavy workers

**2. Off-Peak Scheduling:**
```python
# Huge/massive tasks delayed until off-peak (10 PM - 6 AM UTC)
if size_class == TaskSizeClass.MASSIVE and not is_off_peak():
    return {
        "schedule_now": False,
        "recommended_delay_seconds": seconds_until_offpeak,
        "reasoning": "Large task - schedule during off-peak hours"
    }
```

**3. Batching:**
```python
# Tiny tasks batched together
if size_class == TaskSizeClass.TINY:
    return {
        "should_batch": True,
        "batch_window_seconds": 300,  # Wait 5 min
        "max_batch_size": 50
    }
```

**4. Load Balancing:**
- Prefer workers with lowest utilization
- Respect max bandwidth per worker
- Avoid overloading single worker

---

### 5. Dashboard Integration ([htm_dashboard_api.py](file:///c:/Users/aaron/grace_2/backend/routes/htm_dashboard_api.py))

#### Enhanced Stats Endpoint:
**GET /api/htm/dashboard/stats**
```json
{
  "total_tasks": 1247,
  "completed_tasks": 1100,
  
  "avg_execution_time_ms": 1250,
  "p95_execution_ms": 3400,
  
  "total_bytes_processed": 10737418240,
  "total_bytes_processed_human": "10.0 GB",
  "total_items_processed": 5000,
  "avg_task_size_bytes": 9761095.67,
  "avg_task_size_human": "9.31 MB",
  "p95_task_size_bytes": 52428800,
  "p95_task_size_human": "50.0 MB",
  
  "avg_throughput_bytes_per_sec": 2621440.0,
  "avg_throughput_human": "2.5 MB/s",
  "p95_throughput_bytes_per_sec": 5242880.0,
  "p95_throughput_human": "5.0 MB/s",
  
  "sla_compliance_rate": 0.94
}
```

#### Size Analysis Endpoint:
**GET /api/htm/dashboard/size/analysis?task_type=ingestion&hours=24**
```json
{
  "analysis_period_hours": 24,
  "task_type": "ingestion",
  "size_statistics": {
    "count": 800,
    "total_bytes": 8589934592,
    "total_human": "8.0 GB",
    "mean_bytes": 10737418.24,
    "mean_human": "10.24 MB",
    "median_bytes": 5242880,
    "p95_bytes": 52428800,
    "stdev_bytes": 15728640.5
  },
  "throughput_statistics": {
    "mean_bytes_per_sec": 2621440.0,
    "mean_human": "2.5 MB/s",
    "p95_bytes_per_sec": 5242880.0,
    "p95_human": "5.0 MB/s"
  },
  "size_distribution": {
    "tiny": 50,
    "small": 200,
    "medium": 400,
    "large": 140,
    "huge": 10
  },
  "recommendations": [
    {
      "type": "low_throughput",
      "message": "Low average throughput: 2.5 MB/s",
      "suggestion": "Investigate bottlenecks in processing pipeline"
    }
  ]
}
```

#### Heavy Tasks Endpoint:
**GET /api/htm/dashboard/size/heavy?min_size_mb=100&limit=20**
```json
[
  {
    "task_id": "task_456",
    "task_type": "ingestion",
    "data_size_bytes": 524288000,
    "data_size_human": "500.0 MB",
    "size_class": "large",
    "input_count": 50,
    "execution_time_ms": 120000,
    "bytes_per_second": 4369066.67,
    "throughput_human": "4.17 MB/s",
    "status": "completed"
  }
]
```

#### Size Distribution Endpoint:
**GET /api/htm/dashboard/size/distribution**
```json
{
  "distribution": {
    "tiny": 250,
    "small": 500,
    "medium": 400,
    "large": 90,
    "huge": 10,
    "massive": 0
  },
  "by_task_type": {
    "ingestion": {"count": 800, "total_bytes": 8589934592},
    "embedding": {"count": 300, "total_bytes": 1073741824},
    "analysis": {"count": 150, "total_bytes": 524288000}
  }
}
```

---

## Usage Examples

### 1. Ingestion Task with Size Tracking:
```python
from backend.core.htm_size_tracker import get_ingestion_size

# Calculate payload size
size_info = get_ingestion_size([
    "/uploads/document1.pdf",
    "/uploads/document2.pdf"
])

# Create task with size data
task = HTMTask(
    task_id="ingest_123",
    task_type="ingestion",
    domain="documents",
    data_size_bytes=size_info.data_size_bytes,
    input_count=size_info.input_count,
    payload={
        "files": [...],
        "size_class": size_info.get_size_class().value
    }
)

# Get scheduling recommendation
schedule = await htm_size_scheduler.schedule_task(
    task_id="ingest_123",
    task_type="ingestion",
    data_size_bytes=size_info.data_size_bytes,
    priority="normal"
)

if schedule["schedule_now"]:
    # Assign to recommended worker
    task.assigned_worker = schedule["worker_id"]
else:
    # Delay or batch
    if schedule["should_batch"]:
        # Add to batch queue
        await add_to_batch(task_id)
    else:
        # Schedule for later
        await schedule_delayed(task_id, schedule["recommended_delay_seconds"])
```

### 2. Complete Task with Throughput:
```python
from backend.core.htm_size_tracker import calculate_throughput

# On task completion
task.finished_at = datetime.now(timezone.utc)
task.execution_time_ms = (task.finished_at - task.started_at).total_seconds() * 1000

# Calculate throughput
task.bytes_per_second = calculate_throughput(
    task.data_size_bytes,
    task.execution_time_ms
)

if task.input_count:
    task.items_per_second = calculate_items_throughput(
        task.input_count,
        task.execution_time_ms
    )

# Save to database
await session.commit()
```

### 3. Monitor Bandwidth Utilization:
```python
# Get scheduler stats
stats = await htm_size_scheduler.get_scheduling_stats()

print(f"Overall utilization: {stats['overall_utilization']:.1%}")
print(f"Total capacity: {stats['total_capacity']}")
print(f"Current load: {stats['total_load']}")

for worker in stats['workers']:
    print(f"  {worker['worker_id']}: {worker['utilization']:.1%} ({worker['current_load']} / {worker['capacity']})")
```

### 4. Batch Small Tasks:
```python
# Get tasks eligible for batching
batch_ids = await htm_size_scheduler.get_batched_tasks(
    max_batch_size=50,
    max_total_bytes=100 * 1024 ** 2  # 100 MB
)

# Process batch together
if batch_ids:
    result = await process_batch(batch_ids)
```

---

## Integration Points

### Message Bus Events:
```python
# Size metrics published periodically
{
    "topic": "htm.size.stats",
    "payload": {
        "total_bytes_processed": ...,
        "avg_task_size_bytes": ...,
        "avg_throughput_bytes_per_sec": ...,
        "size_distribution": {...}
    }
}
```

### Startup Integration:
```python
# backend/main.py

from backend.core.htm_size_metrics import htm_size_metrics
from backend.core.htm_size_scheduler import htm_size_scheduler

async def startup():
    # Start size metrics aggregation
    await htm_size_metrics.start()
    
    # Register workers
    htm_size_scheduler.register_worker("heavy_worker_1", "heavy", max_data_gb=50.0)
    
    print("[HTM] Size tracking enabled")
```

---

## Performance Insights

### Before (Time-Only):
```
Task slow? Could be:
- Agent performance issue
- Network latency
- Complex computation
- Large data volume ❌ Unknown
```

### After (Time + Size):
```
Task slow + large payload = Bandwidth bottleneck
Task slow + small payload = Agent performance issue
Task fast + huge payload = Excellent throughput
```

### Actionable Metrics:
1. **Bytes per second** - Identify throughput bottlenecks
2. **Size distribution** - Plan worker capacity
3. **Heavy tasks** - Route to specialized workers
4. **Off-peak scheduling** - Optimize resource usage

---

## Files Created/Modified

### Core Implementation:
- ✅ `backend/models/htm_models.py` (modified) - Added size fields
- ✅ `backend/core/htm_size_tracker.py` (new) - Size utilities
- ✅ `backend/core/htm_size_metrics.py` (new) - Metrics aggregator
- ✅ `backend/core/htm_size_aware_scheduler.py` (new) - Smart scheduling

### Dashboard:
- ✅ `backend/routes/htm_dashboard_api.py` (modified) - Size metrics endpoints

### Documentation:
- ✅ `docs/HTM_SIZE_TRACKING_COMPLETE.md` (this file)

---

## Database Migration

Add size fields to existing HTM tasks:

```sql
-- Add to htm_tasks table
ALTER TABLE htm_tasks ADD COLUMN data_size_bytes INTEGER;
ALTER TABLE htm_tasks ADD COLUMN input_count INTEGER;
ALTER TABLE htm_tasks ADD COLUMN output_size_bytes INTEGER;
ALTER TABLE htm_tasks ADD COLUMN bytes_per_second FLOAT;
ALTER TABLE htm_tasks ADD COLUMN items_per_second FLOAT;

-- Add to htm_task_attempts table
ALTER TABLE htm_task_attempts ADD COLUMN data_size_bytes INTEGER;
ALTER TABLE htm_task_attempts ADD COLUMN input_count INTEGER;

-- Add to htm_metrics table
ALTER TABLE htm_metrics ADD COLUMN total_data_bytes INTEGER DEFAULT 0;
ALTER TABLE htm_metrics ADD COLUMN total_input_count INTEGER DEFAULT 0;
ALTER TABLE htm_metrics ADD COLUMN avg_data_size_bytes FLOAT DEFAULT 0.0;
ALTER TABLE htm_metrics ADD COLUMN avg_input_count FLOAT DEFAULT 0.0;
ALTER TABLE htm_metrics ADD COLUMN p50_data_size_bytes INTEGER DEFAULT 0;
ALTER TABLE htm_metrics ADD COLUMN p95_data_size_bytes INTEGER DEFAULT 0;
ALTER TABLE htm_metrics ADD COLUMN p99_data_size_bytes INTEGER DEFAULT 0;
ALTER TABLE htm_metrics ADD COLUMN avg_bytes_per_second FLOAT DEFAULT 0.0;
ALTER TABLE htm_metrics ADD COLUMN avg_items_per_second FLOAT DEFAULT 0.0;
ALTER TABLE htm_metrics ADD COLUMN p95_bytes_per_second FLOAT DEFAULT 0.0;
```

---

## Next Steps (Optional Enhancements)

1. **Historical Trending**: Chart size/throughput over time
2. **Predictive Sizing**: ML model to estimate task size from metadata
3. **Dynamic Worker Scaling**: Auto-scale workers based on queue size distribution
4. **Storage Optimization**: Identify tasks producing excessive output
5. **Network Optimization**: Detect slow network transfers vs slow processing
6. **Cost Attribution**: Calculate storage/bandwidth costs per task type

---

**Status**: ✅ Complete  
**Date**: 2025-11-14  
**Features**: Size tracking, throughput metrics, size-aware scheduling, bandwidth monitoring  
**Integration**: Dashboard, metrics aggregation, load balancing  
**Quality**: Comprehensive utilities, smart recommendations, actionable insights
