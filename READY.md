# ✅ Grace is Ready!

## 🚀 Start Command

```bash
python serve.py
```

That's it! Everything runs from this single command.

---

## 📋 What Happens on Startup

When you run `python serve.py`, Grace automatically initializes:

### Core Systems
- ✅ Guardian kernel (networking, ports, diagnostics)
- ✅ Message bus & immutable log
- ✅ 21 LLM models (categorized by specialty)
- ✅ FastAPI application
- ✅ Databases (grace.db + others)

### Learning & Intelligence
- ✅ **Self-heal runner** → Captures all learning to database
- ✅ **Closed-loop learning** → Integrates execution outcomes
- ✅ **Google search service** → Internet access (DuckDuckGo fallback)
- ✅ **Safe web scraper** → Governed web crawling
- ✅ **RAG mesh** → Knowledge retrieval
- ✅ **World model** → Grace's self-knowledge

### Governance & Safety
- ✅ **Trust framework** → Domain trust scoring (0.0-1.0)
- ✅ **Whitelist management** → Loads from `grace_training/documents/whitelist.txt`
- ✅ **Constitutional engine** → Ethical constraints
- ✅ **Governance framework** → Approval workflows
- ✅ **KPI tracking** → Performance metrics

---

## 🌐 Internet Learning Features

All available immediately after startup:

### Search the Web
```bash
POST http://localhost:8000/api/web-learning/search
{
  "query": "latest AI research",
  "num_results": 5
}
```

### Learn a Topic
```bash
POST http://localhost:8000/api/web-learning/learn-topic
{
  "topic": "quantum computing",
  "save_to_knowledge": true
}
```

### Explore Domain
```bash
GET http://localhost:8000/api/web-learning/explore/programming
```

### Check Stats
```bash
GET http://localhost:8000/api/web-learning/stats
```

### Manage Whitelist
```bash
POST http://localhost:8000/api/web-learning/whitelist/add?domain=example.com
GET http://localhost:8000/api/web-learning/whitelist
```

---

## 📊 Startup Verification

Look for these messages in console:

```
[OK] Self-heal runner started (learning capture enabled)
[OK] Safe web scraper initialized (internet access enabled)
[OK] Google search service initialized (unrestricted web learning enabled)
[OK] Closed-loop learning active (execution feedback to knowledge)
```

If you see all these, **Grace is fully operational** with:
- ✅ Internet access
- ✅ Learning capture
- ✅ Governance active
- ✅ Trust scoring enabled

---

## 🎯 Quick Test

After startup, verify internet learning works:

```bash
# Windows
curl -X POST http://localhost:8000/api/web-learning/search -H "Content-Type: application/json" -d "{\"query\": \"python tutorials\"}"

# Or visit in browser
http://localhost:8000/docs
```

---

## 📖 Configuration (Optional)

No configuration required! Defaults work out of the box:
- ✅ DuckDuckGo search (no API key needed)
- ✅ Trust scoring active
- ✅ Whitelist loaded
- ✅ Learning capture enabled

### Optional: Add Google API (Better Search Quality)

Edit `.env`:
```bash
GOOGLE_SEARCH_API_KEY=your_key
GOOGLE_SEARCH_ENGINE_ID=your_id
```

---

## 🐛 Troubleshooting

### Missing Dependencies
```bash
pip install aiohttp httpx beautifulsoup4
```

### Port Already in Use
Grace auto-allocates available port. Check console for:
```
[OK] Port: 8123  # or whatever port was allocated
```

### Learning Not Captured
Verify message appears:
```
[OK] Self-heal runner started (learning capture enabled)
```

If missing, check `backend/main.py` line ~207

---

## 📚 Full Documentation

- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Complete Guide**: [STARTUP_SUMMARY.md](STARTUP_SUMMARY.md)
- **Internet Access**: [INTERNET_ACCESS.md](INTERNET_ACCESS.md)

---

## ✨ Summary

**One command starts everything:**

```bash
python serve.py
```

Grace boots with:
- 🌐 Full internet access (governed)
- 🧠 Autonomous learning (continuous)
- 📊 KPI tracking (real-time)
- 🛡️ Trust framework (safety)
- 💾 Learning capture (persistent)
- 🔍 Knowledge integration (RAG)

**That's it! Grace is ready to learn from the internet.** 🚀
