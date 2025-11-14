# Testing & Initialization Guide

## Quick Start (3 Steps)

### Step 1: Initialize Database
```bash
cd c:/Users/aaron/grace_2
python scripts/init_book_system.py
```

**This will:**
- ✅ Create all 8 required database tables
- ✅ Create indexes for performance
- ✅ Set up directory structure
- ✅ Create README files

**Expected output:**
```
Creating book system tables...
✓ Created memory_documents
✓ Created memory_document_chunks
✓ Created memory_insights
✓ Created memory_verification_suites
✓ Created memory_librarian_log
✓ Created memory_sub_agents
✓ Created memory_file_operations
✓ Created memory_file_organization_rules

Creating indexes...
✓ Created indexes

✓ All tables created successfully!

Creating directory structure...
✓ Created grace_training/documents/books/
✓ Created grace_training/business/
...

🚀 System ready!
```

---

### Step 2: Run E2E Tests
```bash
python tests/test_book_ingestion_e2e.py
```

**This will test:**
1. ✅ Database initialization and table schemas
2. ✅ Schema agent (file analysis and approval)
3. ✅ Book ingestion agent (extraction, chunking, insights)
4. ✅ Verification engine (trust scoring)
5. ✅ File organizer (domain detection, undo system)
6. ✅ Query functionality (retrieve book data)

**Expected output:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║              GRACE BOOK INGESTION SYSTEM - E2E TEST SUITE                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
                          TEST 1: Database Initialization
================================================================================

Step 1: Initializing database...
✓ Database initialized
Step 2: Verifying required tables...
✓ Table 'memory_documents' exists
✓ Table 'memory_document_chunks' exists
...
✓ Database initialization test PASSED

================================================================================
                          TEST 2: Schema Agent
================================================================================

Step 1: Created test file: grace_training/documents/books/test_book.pdf
✓ Schema agent activated
Step 2: Analyzing test file...
ℹ Proposed table: memory_documents
ℹ Confidence: 0.9
ℹ Reasoning: File in books directory, PDF format
Step 3: Submitting to unified logic...
ℹ Decision status: approved
✓ Schema proposal APPROVED
✓ Schema agent test PASSED

... (more tests)

================================================================================
                                TEST SUMMARY
================================================================================

  DATABASE            : PASSED
  SCHEMA              : PASSED
  INGESTION           : PASSED
  VERIFICATION        : PASSED
  ORGANIZER           : PASSED
  QUERY               : PASSED

Overall: 6/6 tests passed

✓ ALL TESTS PASSED! System is ready for production.
```

---

### Step 3: Verify Data
```bash
# Check database directly
sqlite3 databases/memory_fusion.db

# Run these queries:
SELECT COUNT(*) FROM memory_documents;
SELECT COUNT(*) FROM memory_document_chunks;
SELECT COUNT(*) FROM memory_insights;
SELECT * FROM memory_documents LIMIT 1;
```

**Expected results:**
```sql
-- After E2E test, you should see:
SELECT COUNT(*) FROM memory_documents;        -- 1
SELECT COUNT(*) FROM memory_document_chunks;  -- 1 (placeholder chunk)
SELECT COUNT(*) FROM memory_insights;         -- 1 (summary)

SELECT * FROM memory_documents LIMIT 1;
-- document_id | title            | author      | source_type | trust_score
-- book_abc123 | Test Startup ... | Test Author | book        | 1.0
```

---

## Manual Testing (Optional)

### Test Book Ingestion Manually

1. **Create a test PDF:**
```bash
# Create a simple test file
echo "%PDF-1.4
Test book content about startups and business.
Chapter 1: Introduction
This is a test book for Grace's ingestion system." > grace_training/documents/books/manual_test.pdf
```

2. **Start backend:**
```bash
python serve.py
```

3. **Trigger ingestion via API:**
```bash
curl -X POST http://localhost:8000/api/librarian/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "grace_training/documents/books/manual_test.pdf",
    "pipeline": "book_ingestion",
    "priority": "high"
  }'
```

4. **Check progress:**
```bash
# Get stats
curl http://localhost:8000/api/books/stats

# Get recent books
curl http://localhost:8000/api/books/recent

# Get activity
curl http://localhost:8000/api/books/activity
```

---

## Troubleshooting

### Issue: Tables not created
**Symptoms:** E2E test fails on "Table 'X' MISSING"

**Solution:**
```bash
# Re-run initialization
python scripts/init_book_system.py

# If still fails, manually check database
sqlite3 databases/memory_fusion.db
.tables
```

---

### Issue: Import errors
**Symptoms:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
```bash
# Make sure you're in the right directory
cd c:/Users/aaron/grace_2

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Run with explicit path
PYTHONPATH=. python tests/test_book_ingestion_e2e.py
```

---

### Issue: Database locked
**Symptoms:** `database is locked`

**Solution:**
```bash
# Stop any running backend
# Kill Python processes
taskkill /F /IM python.exe

# Re-run test
python tests/test_book_ingestion_e2e.py
```

---

### Issue: Test file not found
**Symptoms:** `FileNotFoundError: test_book.pdf`

**Solution:**
```bash
# Ensure directories exist
mkdir -p grace_training/documents/books

# Re-run initialization
python scripts/init_book_system.py
```

---

## What Each Test Does

### TEST 1: Database Initialization
- Creates database connection
- Verifies 8 tables exist
- Checks schema columns
- **Pass criteria:** All tables exist with correct columns

### TEST 2: Schema Agent
- Creates dummy PDF file
- Analyzes file (domain detection)
- Proposes schema (memory_documents)
- Submits to unified logic
- **Pass criteria:** Proposal approved (confidence >= 0.85)

### TEST 3: Book Ingestion
- Creates test book with metadata
- Runs full ingestion pipeline
- Extracts, chunks, generates insights
- Saves to database
- **Pass criteria:** Document ID returned, data saved

### TEST 4: Verification
- Runs 3 verification tests on book
- Calculates trust score
- Updates database
- Logs to verification_suites
- **Pass criteria:** Trust score >= 0.5, all tests run

### TEST 5: File Organizer
- Creates misplaced file
- Analyzes domain
- Suggests organization
- Moves file, tests undo
- **Pass criteria:** File moved and restored successfully

### TEST 6: Query Book Data
- Queries document from database
- Fetches chunks, insights, verifications
- Displays all data
- **Pass criteria:** All data retrieved successfully

---

## Expected Database State After Tests

```
memory_documents: 1 row
├─ document_id: book_*
├─ title: "Test Startup Book"
├─ author: "Test Author"
├─ trust_score: 1.0 (100%)

memory_document_chunks: 1 row
├─ document_id: book_*
├─ chunk_index: 0
├─ content: "[Text content from...]"

memory_insights: 1 row
├─ document_id: book_*
├─ insight_type: "summary"
├─ content: "Summary of Test Startup Book..."

memory_verification_suites: 1 row
├─ document_id: book_*
├─ verification_type: "book_comprehensive"
├─ trust_score: 1.0

memory_librarian_log: 5+ rows
├─ schema_proposal
├─ schema_approval
├─ ingestion_launch
├─ ingestion_complete
├─ trust_update

memory_sub_agents: 3+ rows
├─ schema_scout_*
├─ ingestion_runner_*
├─ trust_auditor_*

memory_file_operations: 1+ rows
├─ operation_type: "move"
├─ can_undo: true
├─ undone: true (after test)

memory_file_organization_rules: 0-1 rows
(May have learned rule from organizer test)
```

---

## Cleanup After Testing

```bash
# Remove test files
rm grace_training/documents/books/test_book.pdf
rm grace_training/documents/books/test_book.meta.json
rm grace_training/misplaced_book.pdf

# Optional: Reset database
rm databases/memory_fusion.db
python scripts/init_book_system.py
```

---

## Next Steps After Successful Tests

1. ✅ **Tests pass?** → System is ready!

2. **Drop your first real book:**
   ```bash
   cp ~/Downloads/your_book.pdf grace_training/documents/books/
   ```

3. **Start the full system:**
   ```bash
   # Terminal 1: Backend
   python serve.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

4. **Open UI:**
   ```
   http://localhost:5173
   → Memory Studio → 📚 Books
   ```

5. **Watch it work:**
   - Notification: "📚 Book Detected"
   - Progress tab: Real-time ingestion
   - Stats updating live
   - Notification: "✅ Ingestion Complete"
   - Click book → "Summarize" → Query Grace!

---

## Performance Benchmarks

**Expected timing (on average hardware):**
- Database init: < 1 second
- Schema test: < 2 seconds
- Ingestion test: 5-10 seconds (placeholder implementation)
- Verification: < 1 second
- Organizer test: < 2 seconds
- Query test: < 1 second

**Total E2E test time: ~15-20 seconds**

If tests take longer:
- Check: Is database on SSD?
- Check: Python version (3.9+ recommended)
- Check: No other processes using database

---

## Success Checklist

Before declaring victory:
- [ ] `python scripts/init_book_system.py` runs without errors
- [ ] `python tests/test_book_ingestion_e2e.py` shows "6/6 tests passed"
- [ ] Database contains test data (verify with sqlite3)
- [ ] Directories created (`grace_training/documents/books/` exists)
- [ ] Backend starts: `python serve.py` (no errors)
- [ ] Frontend starts: `cd frontend && npm run dev` (compiles)
- [ ] UI loads: http://localhost:5173 (Memory Studio → Books tab visible)

**All checked?** 🎉 You're ready to drop your 14 books and demo Grace!

---

## Quick Reference Commands

```bash
# Full setup from scratch
python scripts/init_book_system.py
python tests/test_book_ingestion_e2e.py

# Start system
python serve.py                    # Terminal 1
cd frontend && npm run dev         # Terminal 2

# Check system
curl http://localhost:8000/api/books/stats
curl http://localhost:8000/api/librarian/status

# Database inspection
sqlite3 databases/memory_fusion.db ".tables"
sqlite3 databases/memory_fusion.db "SELECT COUNT(*) FROM memory_documents;"

# Cleanup
rm -rf grace_training/documents/books/*.pdf
rm databases/memory_fusion.db
```

Good luck! 🚀📚🤖
