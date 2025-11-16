# 🚀 Grace - Quick Start Guide

## Start Grace in 3 Steps

### Step 1: Run the Startup Script
```bash
START_GRACE_WITH_WEB_LEARNING.bat
```

### Step 2: Wait for Boot Completion
Look for these messages:
```
[OK] Self-heal runner started (learning capture enabled)
[OK] Google search service initialized (unrestricted web learning enabled)
[OK] Closed-loop learning active (execution feedback to knowledge)
```

### Step 3: Access Grace
- **API**: http://localhost:8000 (or dynamically allocated port shown in console)
- **Frontend**: http://localhost:5173
- **Docs**: http://localhost:8000/docs

---

## 🌐 Test Internet Learning

### Quick Test - Search the Web
```bash
curl -X POST http://localhost:8000/api/web-learning/search ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"latest AI breakthroughs 2025\", \"num_results\": 5}"
```

### Learn a New Topic
```bash
curl -X POST http://localhost:8000/api/web-learning/learn-topic ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"rust programming\", \"max_sources\": 10, \"save_to_knowledge\": true}"
```

### Check Learning Stats
```bash
curl http://localhost:8000/api/web-learning/stats
```

---

## ✅ What Grace Can Do Now

- ✅ Search Google/DuckDuckGo for any topic
- ✅ Learn autonomously from the internet
- ✅ Explore any domain freely (programming, science, business, etc.)
- ✅ Capture all learning to database
- ✅ Filter sources by trust score
- ✅ Track KPIs and performance metrics
- ✅ Manage whitelist dynamically
- ✅ Run background research sessions

---

## 🛡️ Governance is Active

All web learning is governed by:
- **Trust scoring**: 0.0-1.0 scale
- **Whitelist management**: Dynamic domain approval
- **Approval checks**: Governance framework validation
- **KPI tracking**: Success rates, trust scores, blocks
- **Immutable logging**: All actions recorded

**Grace learns freely but safely!** 🎯

---

## 📖 Full Documentation

- [STARTUP_SUMMARY.md](STARTUP_SUMMARY.md) - Complete feature documentation
- [INTERNET_ACCESS.md](INTERNET_ACCESS.md) - Internet learning details
- [README.md](README.md) - Project overview

---

**That's it! Grace is ready to learn from the internet.** 🚀
