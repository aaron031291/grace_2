# Grace Complete Pipeline - Deployment Checklist

## ✅ Pre-Deployment Verification

### Core Systems
- [x] Memory Tables schema registry
- [x] 5 pre-built table schemas (documents, codebases, datasets, media, insights)
- [x] Content analysis pipeline (4 extractors)
- [x] Schema inference agent (LLM-powered)
- [x] Auto-ingestion service
- [x] Learning integration bridge
- [x] 20 API endpoints
- [x] Unified Logic Hub integration
- [x] Clarity Framework integration
- [x] Orchestrator integration

### Dependencies
- [x] sqlmodel added to pyproject.toml
- [x] PyYAML available
- [x] SQLAlchemy 2.0+
- [x] FastAPI routes configured
- [ ] Optional: PyPDF2 for advanced PDF extraction
- [ ] Optional: ffmpeg for video/audio processing
- [ ] Optional: Tesseract for OCR

### Database
- [x] SQLite default configuration
- [x] PostgreSQL support ready
- [x] Auto-initialization on startup
- [x] Migration support
- [x] Index creation

### File Structure
```
backend/
├── memory_tables/
│   ├── __init__.py ✓
│   ├── registry.py ✓
│   ├── models.py ✓
│   ├── schema_agent.py ✓
│   ├── content_pipeline.py ✓
│   ├── auto_ingestion.py ✓
│   ├── learning_integration.py ✓
│   ├── initialization.py ✓
│   └── schema/
│       ├── documents.yaml ✓
│       ├── codebases.yaml ✓
│       ├── datasets.yaml ✓
│       ├── media.yaml ✓
│       └── insights.yaml ✓
├── routes/
│   ├── memory_tables_api.py ✓
│   └── auto_ingestion_api.py ✓
└── unified_grace_orchestrator.py ✓ (updated)
```

---

## 🚀 Deployment Steps

### Step 1: Install Dependencies

```bash
# Install core dependencies
pip install sqlmodel>=0.0.14 sqlalchemy>=2.0.0 pyyaml>=6.0

# Or use project setup
pip install -e .
```

### Step 2: Initialize Directories

```bash
# Create required directories
mkdir -p databases
mkdir -p logs
mkdir -p training_data
mkdir -p storage/uploads
mkdir -p grace_training
```

### Step 3: Verify Installation

```bash
# Run test script
python test_complete_pipeline.py
```

**Expected output:**
```
✅ ALL TESTS PASSED

Complete pipeline verified:
  • Schema registry ✓
  • Content analysis ✓
  • Schema inference ✓
  • Table operations ✓
  • Learning integration ✓
  • Auto-ingestion ✓

🎉 Grace is ready to learn from the real world!
```

### Step 4: Start Grace

```bash
# Start the orchestrator
python backend/unified_grace_orchestrator.py
```

**Check logs:**
```
🗄️ Initializing Memory Tables system...
✅ Loaded 5 table schemas
✅ Database initialized: sqlite:///databases/memory_tables.db
📊 Active tables: memory_documents, memory_codebases, ...
✅ Memory Tables system started
```

### Step 5: Enable Auto-Ingestion

```bash
curl -X POST http://localhost:8001/api/auto-ingest/start \
  -H "Content-Type: application/json" \
  -d '{
    "folders": ["training_data", "storage/uploads"],
    "auto_approve_low_risk": true
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Auto-ingestion started",
  "stats": {
    "running": true,
    "watch_folders": ["training_data", "storage/uploads"]
  }
}
```

### Step 6: Verify APIs

```bash
# Test memory tables API
curl http://localhost:8001/api/memory/tables/

# Test auto-ingest API
curl http://localhost:8001/api/auto-ingest/status

# Test learning report
curl http://localhost:8001/api/memory/tables/learning-report
```

---

## 🧪 Testing the Complete Flow

### Upload Test File

```bash
# Create test file
echo "# Test Document

This is a test of Grace's learning pipeline.

Key topics: testing, automation, learning" > training_data/test.md
```

### Verify Processing

```bash
# Check auto-ingest status (wait 10 seconds)
sleep 10
curl http://localhost:8001/api/auto-ingest/status

# Query memory_documents table
curl "http://localhost:8001/api/memory/tables/memory_documents/rows?limit=5"
```

**Expected:**
- File detected and processed
- Row inserted into memory_documents
- `file_path`: "training_data/test.md"
- `title`: extracted from content
- `token_count`: > 0

---

## 📊 Monitoring

### Health Checks

```bash
# Overall health
curl http://localhost:8001/health

# System status
curl http://localhost:8001/api/status

# Auto-ingestion status
curl http://localhost:8001/api/auto-ingest/status

# Table statistics
curl http://localhost:8001/api/memory/tables/stats

# Learning report
curl http://localhost:8001/api/memory/tables/learning-report
```

### Log Files

```bash
# Check orchestrator logs
tail -f logs/orchestrator.log

# Look for these messages:
# ✅ Memory Tables system started
# 🔍 Auto-ingestion started
# 📄 Processing new file: ...
# ✅ Successfully ingested: ...
```

---

## 🔧 Configuration

### Database URL

```bash
# Default (SQLite)
export MEMORY_TABLES_DB_URL="sqlite:///databases/memory_tables.db"

# PostgreSQL
export MEMORY_TABLES_DB_URL="postgresql://user:pass@localhost/grace_memory"
```

### Watch Folders

```python
# In auto_ingestion.py or via API
folders = [
    "training_data",
    "storage/uploads",
    "grace_training",
    # Add custom folders
    "business_data",
    "research_papers"
]
```

### Polling Interval

```python
# In auto_ingestion.py _watch_loop
await asyncio.sleep(5)  # Default: 5 seconds

# Adjust as needed:
# - Real-time: 1 second
# - Moderate: 5-10 seconds
# - Low-overhead: 30+ seconds
```

---

## 🛡️ Security

### Approval Settings

```python
# Auto-approve low risk (existing tables)
auto_approve_low_risk = True

# Require approval for medium risk (new tables)
require_approval_medium = True

# Require approval for high risk (schema changes)
require_approval_high = True
```

### File Validation

```python
# In auto_ingestion.py _scan_folder
# Skips:
# - Hidden files (starts with .)
# - Temp files (.tmp, .lock, .bak)
# - System files (starts with ~)
```

### Path Validation

```python
# In memory_tables_api.py
# Validates:
# - File exists before processing
# - No directory traversal
# - Absolute paths only
```

---

## 🚨 Troubleshooting

### Issue: Tables not created

**Check:**
```bash
# Verify schemas loaded
ls backend/memory_tables/schema/

# Check logs
grep "Loaded.*schemas" logs/orchestrator.log
```

**Fix:**
```bash
# Ensure YAML files are valid
python -c "import yaml; yaml.safe_load(open('backend/memory_tables/schema/documents.yaml'))"
```

### Issue: Auto-ingestion not detecting files

**Check:**
```bash
# Verify service is running
curl http://localhost:8001/api/auto-ingest/status

# Check watch folders exist
ls -la training_data/
```

**Fix:**
```bash
# Restart service
curl -X POST http://localhost:8001/api/auto-ingest/stop
curl -X POST http://localhost:8001/api/auto-ingest/start
```

### Issue: Files not inserting

**Check:**
```bash
# Check pending approvals
curl http://localhost:8001/api/auto-ingest/pending

# Check failed ingestions
curl http://localhost:8001/api/auto-ingest/insights/failed
```

**Fix:**
```bash
# Approve pending
curl -X POST http://localhost:8001/api/auto-ingest/approve \
  -d '{"approval_id": "upd_xxx", "approved": true}'
```

---

## 📈 Performance Tuning

### Database

```python
# Use PostgreSQL for production
DB_URL = "postgresql://grace:password@localhost/grace_memory"

# Enable connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(DB_URL, poolclass=QueuePool, pool_size=20)
```

### Concurrent Processing

```python
# Process multiple files in parallel
# In auto_ingestion.py _scan_folder
tasks = [self._process_file(file) for file in new_files]
await asyncio.gather(*tasks, return_exceptions=True)
```

### Caching

```python
# Cache schema lookups
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_schema(table_name):
    return table_registry.get_schema(table_name)
```

---

## ✅ Post-Deployment Verification

### Smoke Tests

```bash
# 1. Upload a test file
cp README.md training_data/

# 2. Wait 10 seconds
sleep 10

# 3. Verify it was processed
curl "http://localhost:8001/api/memory/tables/memory_documents/rows" | grep "README"

# 4. Check learning report
curl http://localhost:8001/api/memory/tables/learning-report
```

### Load Test

```bash
# Upload 100 files
for i in {1..100}; do
    echo "Test document $i" > training_data/test_$i.txt
done

# Wait and check
sleep 60
curl http://localhost:8001/api/auto-ingest/status
# → Should show processed_files_count: 100+
```

---

## 🎉 Production Ready Checklist

- [ ] All tests pass (`python test_complete_pipeline.py`)
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Orchestrator starts without errors
- [ ] Auto-ingestion service starts
- [ ] Test file processes successfully
- [ ] APIs respond correctly
- [ ] Logs show expected messages
- [ ] Approval workflow works
- [ ] Learning report generates
- [ ] Cross-domain query works
- [ ] Failed ingestions logged
- [ ] Performance acceptable
- [ ] Security settings configured
- [ ] Monitoring setup
- [ ] Backup strategy in place

---

## 📚 Documentation

- **MEMORY_TABLES_COMPLETE.md** - Full technical spec
- **MEMORY_TABLES_QUICKSTART.md** - User guide
- **MEMORY_TABLES_INTEGRATION.md** - Integration details
- **AUTO_INGESTION_COMPLETE.md** - Auto-ingestion guide
- **FULL_PIPELINE_GUIDE.md** - Complete workflow
- **This file** - Deployment checklist

---

## 🚀 Launch Command

```bash
# Start Grace with auto-ingestion
python backend/unified_grace_orchestrator.py &

# Enable auto-ingestion
curl -X POST http://localhost:8001/api/auto-ingest/start \
  -d '{"folders": ["training_data"], "auto_approve_low_risk": true}'

# Monitor
tail -f logs/orchestrator.log
```

**Grace is now learning autonomously from real-world data!** 🎉
