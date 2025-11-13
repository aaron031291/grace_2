# Upload a Book & Watch the Magic 🎯

Your system is **running and ready**! Here's how to upload a book and watch the full integration flow.

## ✅ System Status

```
✅ Backend: http://localhost:8000 (healthy)
✅ Self-Healing: 147 incidents tracked, 94% success rate
✅ Model Registry: Ready
✅ Librarian: Ready
```

## 📚 Option 1: Upload via cURL (Fastest)

### Step 1: Get a book

```bash
# Download Frankenstein (public domain, ~78KB)
curl https://www.gutenberg.org/cache/epub/84/pg84.txt -o frankenstein.txt

# Or use any .txt file you have
```

### Step 2: Upload it

```bash
curl -X POST http://localhost:8000/api/books/upload \
  -F "file=@frankenstein.txt" \
  -F "title=Frankenstein" \
  -F "author=Mary Shelley" \
  -F "trust_level=high"
```

### Step 3: Watch the activity

```bash
# Monitor book stats
curl http://localhost:8000/api/books/stats

# Check recent activity  
curl http://localhost:8000/api/books/activity

# View recent books
curl http://localhost:8000/api/books/recent

# Check self-healing (will show rate limit handling)
curl http://localhost:8000/api/self-healing/stats
```

## 🌐 Option 2: Upload via Swagger UI

1. Open: http://localhost:8000/docs
2. Find `/api/books/upload` endpoint
3. Click "Try it out"
4. Upload your file
5. Click "Execute"

## 📊 Option 3: Upload via Frontend (if running)

1. Open: http://localhost:3000
2. Navigate to "Book Ingestion"
3. Click "Upload Book"
4. Select file
5. Watch real-time progress

## 🔍 What to Watch For

### 1. Immediate Response
```json
{
  "status": "processing",
  "document_id": "doc_abc123",
  "title": "Frankenstein",
  "chunks_to_process": 150
}
```

### 2. Rate Limit Hit (Expected!)
Check logs:
```bash
powershell "Get-Content logs\orchestrator.log -Tail 50"
```

Look for:
- ⚠️ `Rate limit detected (429)`
- 🔧 `Self-healing triggered: api_backoff`
- ⏸️ `Backing off for X seconds`
- ✅ `Retry successful`

### 3. Incident Created
```bash
curl http://localhost:8000/api/incidents | python -m json.tool
```

Should show incident with:
- Source: `book_ingestion`
- Type: `rate_limit`
- Status: `resolved`
- Resolution time: ~8 seconds

### 4. Flashcard Generated
```bash
curl http://localhost:8000/api/librarian/flashcards | python -m json.tool
```

Should include:
```json
{
  "front": "What happened during book ingestion at [timestamp]?",
  "back": "Hit OpenAI rate limit, self-healing triggered api_backoff, recovered in 8s"
}
```

### 5. Trust Metrics Updated
```bash
curl http://localhost:8000/api/librarian/trust-metrics
```

OpenAI trust score should reflect the rate limit and recovery.

## 🎬 Full Integration Flow Demo

### Create Sample Book

```bash
# Create a test book
cat > test_book.txt << 'EOF'
# The Autonomous AI Operating System

Chapter 1: Introduction

Grace is an autonomous AI operating system that manages itself.
When things go wrong, Grace detects, diagnoses, and fixes problems
automatically. No human intervention required.

Chapter 2: Self-Healing

The self-healing kernel monitors all operations. When a rate limit
is hit, Grace backs off exponentially and retries. When a model
degrades, Grace triggers automatic rollback.

Chapter 3: Knowledge Retention

Every incident becomes a flashcard. Every recovery updates trust
metrics. Grace learns from every experience, compounding knowledge
over time.

[... add 100 more paragraphs for realistic chunking ...]
EOF
```

### Upload & Monitor

```bash
# Terminal 1: Upload
curl -X POST http://localhost:8000/api/books/upload \
  -F "file=@test_book.txt" \
  -F "title=The Autonomous AI OS" \
  -F "author=Grace Team"

# Terminal 2: Monitor logs
powershell "Get-Content logs\orchestrator.log -Tail 50 -Wait"

# Terminal 3: Check stats every 5 seconds
while true; do
  curl -s http://localhost:8000/api/books/stats
  sleep 5
done
```

## 🚨 Troubleshooting

### Upload fails
```bash
# Check backend is running
curl http://localhost:8000/health

# Check logs
powershell "Get-Content logs\orchestrator.log -Tail 50"
```

### No rate limit hit
- Normal for small books
- Rate limits typically hit after ~50 API calls
- Use a larger book (10,000+ words)

### Self-healing not visible
```bash
# Check self-healing is active
curl http://localhost:8000/api/self-healing/stats

# Check playbooks exist
curl http://localhost:8000/api/self-healing/playbooks
```

## 📈 Expected Metrics

After uploading 1 book (~100 pages):

```json
{
  "total_books": 1,
  "total_chunks": 150,
  "self_healing_incidents": 2,
  "auto_resolved": 2,
  "flashcards_generated": 2,
  "trust_score_openai": 0.92
}
```

## 🎯 Success Criteria

You'll know it worked when:

✅ Book appears in `/api/books/recent`  
✅ Chunks processed in `/api/books/stats`  
✅ Rate limit handled in self-healing stats  
✅ Incident created and auto-resolved  
✅ Flashcard generated for the rate limit  
✅ Trust metrics updated  

## 💡 Next Steps

After successful upload:

1. **Query the knowledge**
   ```bash
   curl -X POST http://localhost:8000/api/librarian/search \
     -H "Content-Type: application/json" \
     -d '{"query": "What is self-healing?", "top_k": 5}'
   ```

2. **View the flashcards**
   ```bash
   curl http://localhost:8000/api/librarian/flashcards
   ```

3. **Check trust metrics**
   ```bash
   curl http://localhost:8000/api/librarian/trust-metrics
   ```

4. **Simulate model degradation**
   ```bash
   python scripts/populate_model_registry.py
   python scripts/simulate_model_degradation.py fraud_detector_v1
   ```

---

**Ready to upload! Pick an option above and watch Grace work! 🚀**
