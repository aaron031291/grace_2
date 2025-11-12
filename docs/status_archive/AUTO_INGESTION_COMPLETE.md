# Auto-Ingestion Pipeline - COMPLETE ✅

## 🎯 Full Data Flow Wired

Grace now has a **complete, autonomous learning pipeline** that automatically processes files from upload to knowledge:

```
📁 File Upload
    ↓
🔍 Content Analysis (multi-format extraction)
    ↓
🧠 Schema Inference (LLM proposes table)
    ↓
🛡️ Unified Logic Hub (governance & approval)
    ↓
💾 Table Population (structured storage)
    ↓
📚 Learning Integration (ingestion & training)
    ↓
🎓 Knowledge Available (queryable, actionable)
```

---

## 🏗️ Components

### 1. Auto-Ingestion Service (`auto_ingestion.py`)

**What it does:**
- Monitors folders (`training_data/`, `storage/uploads/`, etc.)
- Detects new files automatically
- Processes through complete pipeline
- Handles approvals
- Logs failures

**Key features:**
- ✅ File watching with 5-second polling
- ✅ Duplicate detection (path + mtime + size hash)
- ✅ Skips hidden/temp files
- ✅ Pending approvals queue
- ✅ Manual approval/rejection
- ✅ Failed ingestion tracking

### 2. API Routes (`auto_ingestion_api.py`)

**Endpoints:**
```
POST   /api/auto-ingest/start        - Start watching folders
POST   /api/auto-ingest/stop         - Stop service
GET    /api/auto-ingest/status       - Get current status
GET    /api/auto-ingest/pending      - List pending approvals
POST   /api/auto-ingest/approve      - Approve/reject ingestion
POST   /api/auto-ingest/process-file - Manually process a file
GET    /api/auto-ingest/insights/failed - Get failed attempts
```

### 3. Learning Integration (`learning_integration.py`)

**Bridges tables to learning:**
- ✅ Sync rows to ingestion pipeline
- ✅ Extract insights from tables
- ✅ Cross-domain queries
- ✅ Trust score updates
- ✅ Learning status reports

**New API endpoints:**
```
POST   /api/memory/tables/sync-to-learning/{table}/{row_id}
POST   /api/memory/tables/update-trust-scores/{table}
POST   /api/memory/tables/cross-domain-query
GET    /api/memory/tables/learning-report
```

---

## 🚀 How to Use

### Start Auto-Ingestion

```bash
# Start watching default folders
curl -X POST http://localhost:8001/api/auto-ingest/start

# Start watching custom folders
curl -X POST http://localhost:8001/api/auto-ingest/start \
  -H "Content-Type: application/json" \
  -d '{
    "folders": ["training_data", "my_data", "documents"],
    "auto_approve_low_risk": true
  }'
```

### Check Status

```bash
curl http://localhost:8001/api/auto-ingest/status
```

**Response:**
```json
{
  "success": true,
  "status": "running",
  "stats": {
    "running": true,
    "watch_folders": ["training_data", "storage/uploads"],
    "processed_files_count": 127,
    "pending_approvals_count": 3
  }
}
```

### Handle Pending Approvals

```bash
# List pending
curl http://localhost:8001/api/auto-ingest/pending
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "pending_approvals": {
    "upd_abc123": {
      "file_path": "training_data/new_schema_candidate.pdf",
      "analysis": {...},
      "proposal": {
        "action": "create_new",
        "table_name": "memory_contracts",
        "confidence": 0.85
      },
      "timestamp": "2025-01-12T15:30:00Z"
    }
  }
}
```

```bash
# Approve
curl -X POST http://localhost:8001/api/auto-ingest/approve \
  -d '{
    "approval_id": "upd_abc123",
    "approved": true
  }'

# Reject
curl -X POST http://localhost:8001/api/auto-ingest/approve \
  -d '{
    "approval_id": "upd_abc123",
    "approved": false,
    "reason": "Not needed right now"
  }'
```

### Cross-Domain Query

```bash
curl -X POST http://localhost:8001/api/memory/tables/cross-domain-query \
  -H "Content-Type: application/json" \
  -d '{
    "documents": {"source_type": "report"},
    "codebases": {"languages": ["python"]},
    "datasets": {"dataset_name": "customers"}
  }'
```

**Response:**
```json
{
  "success": true,
  "results": {
    "documents": [{...}, {...}],
    "codebases": [{...}],
    "datasets": [{...}]
  },
  "total_rows": 15
}
```

### Learning Report

```bash
curl http://localhost:8001/api/memory/tables/learning-report
```

**Response:**
```json
{
  "success": true,
  "report": {
    "timestamp": "2025-01-12T16:00:00Z",
    "tables": {
      "memory_documents": {
        "total_rows": 89,
        "synced_rows": 75,
        "avg_trust_score": 0.73,
        "sync_percentage": 84.3
      }
    },
    "summary": {
      "total_tables": 5,
      "total_rows": 247,
      "overall_avg_trust": 0.71
    }
  }
}
```

---

## 🔄 Complete Pipeline Example

### Scenario: Upload Business Plan PDF

```
1. User drops "business_plan_2025.pdf" into training_data/

2. Auto-Ingestion Service detects it (within 5 seconds)

3. Content Pipeline analyzes:
   - Type: document
   - Features: 15,000 tokens, 25 sections, business domain
   - Extracted: title, author, key topics

4. Schema Agent proposes:
   - Action: use_existing
   - Table: memory_documents
   - Confidence: 0.92
   - Reason: "Standard business document"

5. Unified Logic Hub evaluates:
   - Risk level: low (existing table)
   - Auto-approved: yes
   - Logged: upd_20250112_160001

6. Table Population:
   - Inserts row into memory_documents
   - Fields populated: id, file_path, title, summary, key_topics, trust_score, etc.
   - Returns: row_id = a3f1e2c4-...

7. Learning Integration:
   - Syncs to ingestion pipeline
   - Updates trust score (0.7 initially)
   - Publishes clarity event: "file_ingested"

8. Result:
   - Document is queryable via API
   - Grace can reason over content
   - Available for cross-domain queries
   - Feeds into learning systems
```

**All automatic, zero manual work.**

---

## 🛡️ Governance Flow

### Low Risk (Auto-Approved)
- Using existing table
- Standard file types
- No schema changes

**Flow:**
```
Upload → Analyze → Propose → Auto-Approve → Insert → Learn
```

### Medium Risk (Approval Required)
- New table creation
- Schema extension
- Large batch operations

**Flow:**
```
Upload → Analyze → Propose → Pending Approval
  ↓ (User approves via UI/API)
Approve → Insert → Learn
```

### High Risk (Multi-Approval)
- System schema changes
- Critical data modifications
- Policy updates

**Flow:**
```
Upload → Analyze → Propose → Queue for Review
  ↓ (Admin approves)
Approve → Insert → Learn
```

---

## 📊 Integration with Existing Systems

### Unified Logic Hub
```python
# Every ingestion goes through Logic Hub
update_result = await unified_logic_hub.submit_update(
    update_type="auto_ingestion",
    component_targets=["memory_tables", "ingestion"],
    content={...},
    risk_level="low|medium|high"
)
```

### Clarity Framework
```python
# Events published automatically
await clarity_manifest.publish_event(
    event_type="file_ingested",
    component_id="auto_ingestion",
    data={...}
)
```

### Memory Fusion
```python
# Rows sync to long-term storage
registry.update_row(table_name, row_id, {
    'last_synced_at': datetime.now()
})
```

---

## 🎯 Use Cases

### 1. Autonomous Business Intelligence

```bash
# Start watching
curl -X POST http://localhost:8001/api/auto-ingest/start \
  -d '{"folders": ["business_data"]}'

# Drop files into business_data/:
# - market_research.pdf
# - competitor_analysis.xlsx
# - strategy_presentation.pptx
# - customer_data.csv

# Grace automatically:
# - Analyzes each file
# - Populates appropriate tables
# - Builds cross-domain knowledge graph
# - Available for queries immediately
```

### 2. Continuous Learning Agent

```python
# Enable auto-ingestion in autonomous mode
await auto_ingestion_service.start(folders=["training_data"])

# Grace continuously learns from:
# - New documents (→ memory_documents)
# - Code repositories (→ memory_codebases)
# - Datasets (→ memory_datasets)
# - Media files (→ memory_media)

# Query learned knowledge:
report = await learning_bridge.generate_learning_report()
# → Shows growth over time, trust scores, sync status
```

### 3. Business Plan Generator

```python
# After ingesting market data, code, and datasets:

# Query all business-related knowledge
results = await learning_bridge.cross_domain_query({
    'documents': {'source_type': 'report'},
    'codebases': {'languages': ['python']},
    'datasets': {'dataset_name': 'market_trends'}
})

# Grace synthesizes:
# - Market insights from documents
# - Technical patterns from code
# - Data trends from datasets
# → Generates comprehensive business plan
```

---

## 🔧 Configuration

### Watch Folders

```python
# Default folders (auto-created):
- training_data/
- storage/uploads/
- grace_training/

# Add custom folders:
await auto_ingestion_service.start(folders=[
    "my_documents",
    "research_papers",
    "code_repos"
])
```

### Auto-Approval Settings

```python
# Auto-approve low risk operations
{
  "auto_approve_low_risk": true,  # Existing tables
  "require_approval_medium": true,  # New tables
  "require_approval_high": true   # Schema changes
}
```

### Polling Interval

```python
# In auto_ingestion.py
await asyncio.sleep(5)  # Check every 5 seconds

# Adjust as needed:
await asyncio.sleep(1)   # More responsive (higher load)
await asyncio.sleep(30)  # Less frequent (lower load)
```

---

## 📈 Monitoring

### Check Processed Files

```python
stats = auto_ingestion_service.get_stats()
# → {'processed_files_count': 127, ...}
```

### View Failed Ingestions

```bash
curl http://localhost:8001/api/auto-ingest/insights/failed
```

### Learning Status

```bash
curl http://localhost:8001/api/memory/tables/learning-report
```

---

## 🎉 What This Enables

### For Users
- ✅ Drop files → Grace learns automatically
- ✅ No manual processing
- ✅ Transparent governance
- ✅ Full audit trail

### For Grace
- ✅ Continuous autonomous learning
- ✅ Multi-domain knowledge building
- ✅ Cross-domain reasoning
- ✅ Real-world data → Business insights

### For Developers
- ✅ Clean pipeline architecture
- ✅ Extensible extractors
- ✅ Well-governed workflows
- ✅ Observable & debuggable

---

## 🚀 Next Steps

1. **UI Dashboard** - Visual approval queue, learning metrics
2. **Advanced Extractors** - PyPDF2, ffmpeg, Tesseract
3. **LLM Enhancement** - Better schema proposals, summaries
4. **Real-time Sync** - WebSocket updates for UI
5. **Federation** - Sync across Grace instances

---

**Status:** ✅ PRODUCTION READY  
**Version:** 1.0.0  
**Integration:** Complete - Upload → Learn pipeline fully wired  

**Grace can now learn from any data, automatically, continuously, and autonomously.**
