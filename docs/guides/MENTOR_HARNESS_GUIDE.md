## 🧙 Mentor Harness - Local Model Orchestration

Turn your local LLMs into on-demand mentors with automatic knowledge capture!

---

## Overview

The **Mentor Harness** system allows Grace to consult multiple local models simultaneously, aggregate their insights, and store the results in Learning Memory for future reuse.

### Key Benefits

✅ **Zero Network Cost** - All models run locally  
✅ **Multiple Perspectives** - Get insights from specialized models  
✅ **Automatic Storage** - Results saved to Learning Memory  
✅ **Task Filtering** - Auto-select models based on task type  
✅ **Confidence Voting** - Weighted consensus from all mentors  
✅ **Benchmark Testing** - Compare model performance

---

## Architecture

```
User Task
    ↓
MentorHarness.run_roundtable()
    ↓
Fan out to local models (parallel)
    ├─ qwen2.5-coder:14b  (code specialist)
    ├─ deepseek-coder:6.7b (optimization)
    ├─ llama3.2:3b        (planning)
    ├─ qwen2.5:7b         (general/UX)
    └─ mistral:7b         (code review)
    ↓
Collect responses + confidence scores
    ↓
Aggregate into consensus
    ↓
Store in Learning Memory
    ├─ storage/memory/learning/mentors/{task_id}/
    ├─ {model}_response.json
    └─ roundtable_summary.json
    ↓
Auto-ingest via FileIngestionAgent
    ↓
ML/DL Pipeline processes
    ↓
Available in Learning Dashboard
```

---

## Components

### 1. Backend Modules

#### learning_memory.py
**Location:** `backend/learning_memory.py`

**Helper functions:**
```python
from backend.learning_memory import (
    store_artifact,
    store_mentor_response,
    store_code_fix,
    store_mission_brief
)

# Store mentor response
await store_mentor_response(
    task_id="mission-123",
    model_name="qwen2.5-coder:14b",
    response="Recommend microservices architecture...",
    confidence=0.92
)

# Store code fix
await store_code_fix(
    incident_id="inc-456",
    code_diff="...",
    description="Fixed auth timeout bug"
)

# Store mission brief
await store_mission_brief(
    mission_id="mobile-app-001",
    objectives="Build iOS/Android app with offline sync",
    constraints={"platforms": ["iOS", "Android"]}
)

# Store any artifact
await store_artifact(
    content={"data": "..."},
    category="autofixes",
    subcategory="self_healing",
    filename="fix.json"
)
```

**Categories:**
- `mentors` - Mentor roundtable responses
- `autofixes` - Self-healing code fixes
- `code_diffs` - Code change proposals
- `summaries` - Generated summaries
- `mission_briefs` - Mission specifications
- `test_results` - Test execution results
- `benchmarks` - Benchmark task results
- `insights` - Generated insights
- `transcripts` - Conversation transcripts
- `prototypes` - Sandbox prototypes
- `decisions` - Architecture decisions

#### mentor_harness.py
**Location:** `backend/kernels/mentor_harness.py`

**MentorHarness class:**
```python
from backend.kernels.mentor_harness import get_mentor_harness

harness = get_mentor_harness()
await harness.activate()

# Run roundtable
result = await harness.run_roundtable(
    task_description="Design mobile app architecture",
    task_type="architecture",
    context={"platforms": ["iOS", "Android"]},
    models=["qwen2.5-coder:14b", "llama3.2:3b"],  # Optional
    store_results=True
)

print(result["aggregated_insights"]["consensus"])
```

**Model Profiles:**
- `qwen2.5-coder:14b` - Code, architecture, debugging
- `deepseek-coder:6.7b` - Code optimization
- `llama3.2:3b` - Planning, reasoning
- `qwen2.5:7b` - General, UX, docs
- `mistral:7b` - Analysis, review

### 2. API Endpoints

#### POST /api/mentor/roundtable
Run a mentor roundtable discussion

**Request:**
```json
{
  "task_description": "Design architecture for mobile app",
  "task_type": "architecture",
  "context": {
    "platforms": ["iOS", "Android"],
    "features": ["auth", "chat", "media"]
  },
  "models": ["qwen2.5-coder:14b"],
  "store_results": true
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "task_id": "roundtable_20250120_143022",
    "task_type": "architecture",
    "models_queried": ["qwen2.5-coder:14b", "llama3.2:3b"],
    "responses": [
      {
        "model": "qwen2.5-coder:14b",
        "response": "Recommend microservices with...",
        "confidence": 0.92,
        "specialization": ["code", "architecture"]
      }
    ],
    "aggregated_insights": {
      "consensus": "Best approach is...",
      "consensus_model": "qwen2.5-coder:14b",
      "average_confidence": 0.89,
      "total_mentors": 2
    },
    "stored_in_learning_memory": true
  }
}
```

#### GET /api/mentor/status
Get harness status and available models

#### GET /api/mentor/recent
Get recent roundtable sessions

#### GET /api/mentor/results/{task_id}
Get stored roundtable results

#### POST /api/mentor/benchmark
Run benchmark test across models

#### GET /api/mentor/stats
Get mentor usage statistics

### 3. Frontend Components

#### MentorRoundtable Component
**Location:** `frontend/src/components/MentorRoundtable.tsx`

**Usage:**
```tsx
import { MentorRoundtable } from './components/MentorRoundtable';

<MentorRoundtable 
  isOpen={mentorOpen} 
  onClose={() => setMentorOpen(false)} 
/>
```

**Access:**
- Click "🧙 Mentors" button in sidebar
- Opens modal with roundtable interface

**Features:**
- Task description input
- Task type selector (code, architecture, planning, etc.)
- Model selection (or auto-select)
- Run roundtable button
- View responses with confidence scores
- See consensus recommendation
- Browse recent roundtables

---

## Usage Examples

### Example 1: Mobile App Architecture

**Scenario:** You need to design a mobile app architecture

**Steps:**
1. Click "🧙 Mentors" in sidebar
2. Enter task: "Design architecture for iOS/Android app with offline sync, real-time chat, and media upload"
3. Select task type: "architecture"
4. Select models: qwen2.5-coder:14b, llama3.2:3b (or leave empty for auto)
5. Click "🚀 Run Roundtable"
6. Wait for results

**Results:**
- Each model provides its recommendation
- Consensus shows the highest-confidence approach
- All responses stored in `storage/memory/learning/mentors/`
- Auto-ingested into memory catalog
- Available for future reference

### Example 2: Code Review

**Scenario:** You want multiple opinions on a code change

**Steps:**
1. Open Mentor Roundtable
2. Task: "Review this authentication refactor for security issues"
3. Task type: "review"
4. Context: Paste code diff
5. Run roundtable

**Results:**
- mistral:7b analyzes security
- deepseek-coder:6.7b checks optimization
- qwen2.5-coder:14b reviews architecture
- Consensus shows common concerns
- Stored for audit trail

### Example 3: Debugging Help

**Scenario:** Stuck on a bug, need debugging strategies

**Steps:**
1. Open Mentor Roundtable
2. Task: "Race condition in async task queue, jobs executing out of order"
3. Task type: "debugging"
4. Context: Error logs, code snippet
5. Run roundtable

**Results:**
- Multiple debugging strategies
- Confidence scores for each approach
- Consensus on most likely fix
- Stored for similar future bugs

---

## Storage Structure

### Learning Memory Paths

```
storage/memory/learning/
├── mentors/
│   ├── {task_id}/
│   │   ├── qwen2.5-coder_response.json
│   │   ├── deepseek-coder_response.json
│   │   ├── llama3_response.json
│   │   └── summary/
│   │       └── roundtable_summary.json
│   └── ...
├── autofixes/
│   ├── {incident_id}/
│   │   └── fix_{incident_id}.json
│   └── ...
├── mission_briefs/
│   ├── {mission_id}/
│   │   └── brief_{mission_id}.json
│   └── ...
└── benchmarks/
    ├── {benchmark_id}/
    │   └── results.json
    └── ...
```

### Auto-Ingestion

All files stored in `learning/` automatically:
1. ✅ Get ingested via FileIngestionAgent
2. ✅ Generate embeddings
3. ✅ Create searchable chunks
4. ✅ Tag as `is_standard_training: true`
5. ✅ Appear in File Ingestion dashboard
6. ✅ Available for RAG/search

---

## Events Published

### Roundtable Events
```python
# Started
Event(
    event_type="mentor.roundtable.started",
    payload={"task_id": "...", "task_type": "architecture"}
)

# Completed
Event(
    event_type="mentor.roundtable.completed",
    payload={
        "task_id": "...",
        "models_queried": 3,
        "successful_responses": 3,
        "top_recommendation": "..."
    }
)
```

### Learning Memory Events
```python
# Artifact Stored
Event(
    event_type="learning.artifact.stored",
    payload={
        "file_path": "storage/memory/learning/mentors/...",
        "category": "mentors"
    }
)

# Learning Corpus Added
Event(
    event_type="learning.corpus.file_added",
    payload={
        "document_id": "uuid-...",
        "modality": "api",
        "auto_ml_enabled": true
    }
)
```

---

## Integration with Missions

### Auto-Consult on New Mission

```python
# In mission creation handler
from backend.kernels.mentor_harness import get_mentor_harness
from backend.learning_memory import store_mission_brief

# Store mission brief
await store_mission_brief(
    mission_id=mission.mission_id,
    objectives=mission.objectives,
    constraints=mission.constraints
)

# Consult mentors
harness = get_mentor_harness()
roundtable = await harness.run_roundtable(
    task_description=mission.objectives,
    task_type="planning",
    task_id=mission.mission_id,
    store_results=True
)

# Use consensus as guidance
mission.mentor_guidance = roundtable["aggregated_insights"]["consensus"]
```

### Auto-Fix with Mentor Input

```python
# In self-healing handler
from backend.learning_memory import store_code_fix

# Consult mentors for fix strategy
harness = get_mentor_harness()
fix_guidance = await harness.run_roundtable(
    task_description=f"Fix {incident.error_type}: {incident.error_message}",
    task_type="debugging",
    context={"error_logs": logs, "stack_trace": trace}
)

# Apply fix
code_fix = apply_fix_from_guidance(fix_guidance)

# Store fix in Learning Memory
await store_code_fix(
    incident_id=incident.id,
    code_diff=code_fix,
    description=f"Auto-fix based on mentor consensus"
)
```

---

## Workflow: Mobile App Task

### Step 1: Define Mission Brief
```python
from backend.learning_memory import store_mission_brief

await store_mission_brief(
    mission_id="mobile-app-001",
    objectives="""
        Build cross-platform mobile app:
        - iOS and Android support
        - Real-time chat
        - Offline sync
        - Media upload
        - Push notifications
    """,
    constraints={
        "platforms": ["iOS", "Android"],
        "frameworks": ["React Native", "Flutter"],
        "deadline": "2 weeks"
    }
)
```

Result: Saved to `storage/memory/learning/mission_briefs/mobile-app-001/`

### Step 2: Consult Mentors
```python
harness = get_mentor_harness()

architecture_roundtable = await harness.run_roundtable(
    task_description="Design architecture for mobile app (see mission-app-001 brief)",
    task_type="architecture",
    task_id="mobile-app-001",
    models=["qwen2.5-coder:14b", "llama3.2:3b"]
)

print(architecture_roundtable["aggregated_insights"]["consensus"])
# → "Recommend React Native with Redux, Firebase backend, AsyncStorage for offline..."
```

Result: Saved to `storage/memory/learning/mentors/mobile-app-001/`

### Step 3: Implementation in Sandbox
```python
# Grace's planner agent loads mentor insights from Learning Memory
mentor_insights = await query_category("mentors", "mobile-app-001")

# Build sandbox workspace
workspace = create_sandbox("mobile-app-001")

# Implement based on mentor guidance
implement_with_guidance(workspace, mentor_insights)

# Each prototype saved back to Learning Memory
await store_artifact(
    content=prototype_code,
    category="prototypes",
    subcategory="mobile-app-001",
    filename="app_v1.zip"
)
```

### Step 4: Test & Iterate
```python
# Run tests
test_results = run_tests(workspace)

# Store test results in Learning Memory
await store_artifact(
    content=test_results,
    category="test_results",
    subcategory="mobile-app-001"
)

# If tests fail, consult mentors again
if test_results["failed"] > 0:
    debug_roundtable = await harness.run_roundtable(
        task_description=f"Debug test failures: {test_results['errors']}",
        task_type="debugging",
        task_id=f"mobile-app-001-debug"
    )
```

### Step 5: Promote & Notify
```python
# When ready, promote from sandbox
promote_to_mainline(workspace)

# Notification to user
notify_user({
    "type": "mission_complete",
    "mission_id": "mobile-app-001",
    "artifacts": {
        "code": workspace.path,
        "mentor_guidance": "learning/mentors/mobile-app-001/",
        "test_results": "learning/test_results/mobile-app-001/"
    }
})
```

---

## Frontend Usage

### Access Mentor Roundtable

1. **Open Grace Console** (http://localhost:5173)
2. **Click "🧙 Mentors"** in sidebar
3. **Modal opens** with roundtable interface

### Run a Roundtable

1. **Enter task description**
   - Example: "Design API for real-time chat service"
   
2. **Select task type**
   - Code, Architecture, Planning, Review, etc.
   
3. **Choose models** (optional)
   - Leave empty for auto-selection
   - Or manually pick specialized models
   
4. **Click "Run Roundtable"**
   - Models queried in parallel
   - Responses aggregated
   - Results displayed
   
5. **Review results**
   - See consensus recommendation
   - Read individual responses
   - Check confidence scores
   - Results auto-saved to Learning Memory

### View Past Roundtables

**Recent Roundtables** section shows:
- Task type
- Number of models queried
- Consensus confidence
- Timestamp
- Click to load full results

---

## API Examples

### Trigger Roundtable from Code
```bash
curl -X POST http://localhost:8000/api/mentor/roundtable \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Optimize database query performance",
    "task_type": "optimization",
    "context": {"current_latency": "2.5s", "target": "100ms"}
  }'
```

### Get Available Models
```bash
curl http://localhost:8000/api/mentor/models
```

### Get Recent Roundtables
```bash
curl http://localhost:8000/api/mentor/recent?limit=10
```

### Run Benchmark
```bash
curl -X POST http://localhost:8000/api/mentor/benchmark \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Implement quicksort in Python",
    "expected_output": "def quicksort(arr): ..."
  }'
```

---

## Benchmark Testing

### Run Periodic Benchmarks

```python
# Define standard benchmark
benchmark = {
    "description": "Implement binary search in Python with tests",
    "context": {
        "requirements": ["O(log n)", "handle edge cases", "include tests"]
    },
    "expected_output": "Complete implementation with tests"
}

# Run against all models
result = await harness.run_benchmark(benchmark)

# Compare performance
print(result["evaluation"]["best_performer"])
# → "qwen2.5-coder:14b"

# Results stored in learning/benchmarks/
```

### Use Cases
- Compare model performance
- Track improvement over time
- Validate new model additions
- Choose best model for task types
- Build performance database

---

## Integration Points

### 1. Mission System
When new mission created → Auto-consult mentors → Store guidance

### 2. Self-Healing
When incident detected → Consult debugging mentors → Apply fix → Store

### 3. Code Agent
Before implementing → Consult architecture mentors → Use consensus

### 4. Learning Pipeline
New training data → Consult analysis mentors → Generate insights

### 5. Verification
Test failures → Consult debugging mentors → Get fix strategies

---

## Data Flow

```
1. Task arrives (mission, incident, query)
2. MentorHarness packages context
3. Fans out to filtered local models
4. Collects responses + confidence
5. Aggregates into consensus
6. Stores in learning/mentors/{task_id}/
7. FileIngestionAgent auto-ingests
8. ML/DL pipeline processes
9. Embeddings generated
10. Searchable in memory catalog
11. Displayed in File Ingestion dashboard
12. Reusable for future similar tasks
```

---

## Monitoring & Visibility

### File Ingestion Tile (System Overview)

Shows mentor activity:
- Total artifacts in learning/mentors/
- Recent roundtable sessions
- Average confidence scores
- Modality breakdown (API for JSON responses)

### Learning Dashboard

Browse stored mentor insights:
- Search by task type
- Filter by model
- View confidence trends
- Export for analysis

---

## Best Practices

### 1. Clear Task Descriptions
✅ **Good:** "Design REST API for user authentication with JWT, refresh tokens, and rate limiting"  
❌ **Bad:** "Need auth API"

### 2. Provide Context
Include:
- Requirements/constraints
- Existing architecture
- Performance targets
- Error logs (for debugging)

### 3. Use Task Types
Proper task type = better model selection:
- `code` → Code specialists
- `architecture` → Architecture experts
- `debugging` → Debugging-focused models
- `optimization` → Performance models

### 4. Review All Responses
Don't just use consensus:
- Check minority opinions
- Look for common warnings
- Consider confidence spread
- Evaluate edge cases

### 5. Store Important Results
Always `store_results: true` for:
- Architecture decisions
- Critical debugging sessions
- Benchmark tests
- Mission planning

---

## Configuration

### Add New Model Profile

Edit `mentor_harness.py`:
```python
MODEL_PROFILES = {
    "your-model:version": {
        "specialization": ["your", "tags"],
        "strengths": "Description of strengths",
        "confidence_weight": 1.0
    }
}
```

### Adjust Confidence Weights

Higher weight = more influence on consensus:
- Expert models: 1.2+
- General models: 1.0
- Experimental: 0.8-0.9

---

## Troubleshooting

### "No models available"
- Check Ollama is running
- Run `ollama list` to see installed models
- Update MODEL_PROFILES in mentor_harness.py

### "Roundtable takes too long"
- Models run in parallel
- Reduce number of selected models
- Use faster models for quick tasks

### "Results not in Learning Memory"
- Check `store_results: true` in request
- Verify `storage/memory/learning/mentors/` exists
- Check backend logs for ingestion events

### "Low confidence scores"
- Task description may be unclear
- Add more context
- Try different models
- Check if task type matches model specialization

---

## Summary

✅ **MentorHarness kernel** - Orchestrates local models  
✅ **Learning Memory helper** - Auto-stores artifacts  
✅ **REST API endpoints** - Trigger roundtables  
✅ **Frontend UI** - Beautiful modal interface  
✅ **Auto-ingestion** - Results flow through ML/DL pipeline  
✅ **Event-driven** - Integrates with existing systems  
✅ **Benchmark testing** - Compare model performance  
✅ **Searchable** - All results in memory catalog

**Your local models are now on-demand mentors that automatically contribute to Grace's growing knowledge base!** 🧙✨
