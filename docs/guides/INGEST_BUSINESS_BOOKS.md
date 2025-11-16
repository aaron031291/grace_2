# Ingest Your 13 Business Intelligence Books 📚

You have **13 valuable business/marketing books** ready to ingest!

## 📖 Books Detected:

1. **Dotcom Secrets** (3.2 MB) - Digital marketing funnel strategies
2. **The Lean Startup** by Eric Ries (595 KB) - Startup methodology
3. **Traffic Secrets 1** (4.3 MB) - Traffic generation strategies
4. **Facilitators Guide: 5 Dysfunctions** (16.7 MB) - Team dynamics
5. **Principles of Corporate Finance** 14th Ed (12.3 MB) - Finance fundamentals
6. **$100M Fast Cash Playbook** (1.4 MB) - Sales strategies
7. **$100M Lead Nurture Playbook** (663 KB) - Lead nurturing
8. **$100M Goated Ads Playbook** (1.9 MB) - Advertising strategies
9. **$100M Closing Playbook** (8.9 MB) - Sales closing techniques
10. **+ 4 more books**

**Total Knowledge:** ~50+ MB of business intelligence!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Make sure backend is running

```bash
# Check if running
curl http://localhost:8000/health

# If not, start it
python serve.py
```

### Step 2: Run batch ingestion

```bash
python scripts/ingest_pdf_batch.py "business intelligence"
```

### Step 3: Query what you learned

```bash
# See all books
python query_book.py

# Search specific topics
python query_book.py "marketing"
python query_book.py "startup"
python query_book.py "sales"
```

---

## 📊 What Will Happen

### During Ingestion:
1. ⬆️ **Upload each PDF** (one at a time)
2. 📄 **Extract text** from PDF pages
3. ✂️ **Chunk content** into manageable pieces
4. 🧠 **Generate embeddings** for semantic search
5. 💾 **Store in knowledge base** with metadata
6. 📝 **Generate summary** of key concepts

### You'll See:
- Progress for each book (1/13, 2/13, etc.)
- Upload status (successful/failed)
- Document IDs for tracking
- Estimated time remaining

### Expected Time:
- **Small books** (~1 MB): 30-60 seconds
- **Large books** (~15 MB): 2-5 minutes
- **Total for 13 books**: ~15-30 minutes

---

## 🔍 After Ingestion

### Check What Was Ingested

```bash
# View all books
python query_book.py

# Search for specific content
python query_book.py "traffic secrets"
python query_book.py "lean startup"
python query_book.py "$100M"
```

### Use the Knowledge

```bash
# Ask Grace about marketing
curl -X POST http://localhost:8000/api/librarian/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the best traffic generation strategies?", "top_k": 5}'

# Ask about sales
curl -X POST http://localhost:8000/api/librarian/search \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I close more sales?", "top_k": 5}'

# Ask about startups
curl -X POST http://localhost:8000/api/librarian/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Lean startup principles", "top_k": 5}'
```

### Check System Stats

```bash
# Book statistics
curl http://localhost:8000/api/books/stats

# Recent activity
curl http://localhost:8000/api/books/activity

# Self-healing (rate limit handling)
curl http://localhost:8000/api/self-healing/stats
```

---

## ⚡ Advanced Options

### Custom Delay Between Uploads

```bash
# Faster (3 second delay) - might hit rate limits more
python scripts/ingest_pdf_batch.py "business intelligence" --delay 3

# Slower (10 second delay) - safer for rate limits
python scripts/ingest_pdf_batch.py "business intelligence" --delay 10
```

### Ingest Specific Books Only

```bash
# Create a subset folder
mkdir "business intelligence/priority"
# Copy specific PDFs there
# Then ingest just those
python scripts/ingest_pdf_batch.py "business intelligence/priority"
```

---

## 🚨 Troubleshooting

### Backend Not Running

```bash
# Start backend
python serve.py

# Verify it's running
curl http://localhost:8000/health
```

### PDFs Not Found

```bash
# List files in directory
dir "business intelligence\*.pdf"

# Check you're in the right location
cd c:\Users\aaron\grace_2
```

### Upload Fails

**If you see errors:**
1. Check backend logs: `powershell "Get-Content logs\orchestrator.log -Tail 50"`
2. Verify PDF isn't corrupted
3. Check file permissions
4. Try uploading one file manually first

### Rate Limits

**Expected behavior:**
- Grace will hit OpenAI rate limits during embedding
- Self-healing will automatically back off and retry
- You'll see delays but it will complete

**Watch self-healing work:**
```bash
# Monitor in real-time
powershell "Get-Content logs\orchestrator.log -Tail 50 -Wait"
```

---

## 📈 What You'll Build

After ingesting all 13 books, you'll have:

✅ **Complete business intelligence knowledge base**  
✅ **Semantic search across all books**  
✅ **Summaries of key concepts**  
✅ **Connections between ideas**  
✅ **Trust-scored sources**  

### Example Queries:

**Marketing:**
- "What is a marketing funnel?"
- "How do I generate traffic?"
- "Best advertising strategies"

**Sales:**
- "How to close more deals"
- "Lead nurturing strategies"
- "Sales objection handling"

**Business:**
- "Lean startup methodology"
- "Corporate finance principles"
- "Team building strategies"

---

## 🎯 Next Steps After Ingestion

1. **Query the knowledge**
   ```bash
   python query_book.py
   ```

2. **Test semantic search**
   ```bash
   curl -X POST http://localhost:8000/api/librarian/search \
     -H "Content-Type: application/json" \
     -d '{"query": "your question here", "top_k": 5}'
   ```

3. **Build on it**
   - Add more books/PDFs
   - Create custom queries
   - Build a chat interface
   - Export summaries

---

## 💡 Pro Tips

1. **Let it run** - Don't interrupt during ingestion
2. **Monitor logs** - Watch self-healing handle rate limits
3. **Verify after** - Use `query_book.py` to confirm
4. **Start small** - Test with 1-2 books first if unsure
5. **Be patient** - Large books take time to process

---

**Ready to build your business intelligence knowledge base? Run the command!** 🚀

```bash
python scripts/ingest_pdf_batch.py "business intelligence"
```
