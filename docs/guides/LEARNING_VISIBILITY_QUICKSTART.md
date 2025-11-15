# Grace Learning Visibility - Quick Start 🚀

Monitor what Grace learns from the web with complete traceability!

## 🎯 What You Get

✅ **Real-time monitoring** of Grace's learning activities  
✅ **Full source URL logging** for every piece of data  
✅ **Automatic validation** to ensure learning integrity  
✅ **Live dashboard** showing current learning status  
✅ **Detailed reports** with complete audit trails  

---

## ⚡ 30-Second Setup

### 1. Start Grace
```bash
python serve.py
```

### 2. Run the Demo
```bash
python test_learning_visibility.py
```

That's it! The system will:
- Create a learning session
- Absorb data from 4 different sources
- Validate all activities
- Show you the results

---

## 📊 Monitor in Real-Time

### Launch Dashboard
```bash
python learning_dashboard.py
```

You'll see:
- **Active sessions** with goals and progress
- **Recent activities** with source URLs
- **Validation scores** for each activity
- **Learning velocity** (activities per hour)
- **Source breakdown** (web, GitHub, APIs, etc.)

**Updates every 3 seconds automatically!**

---

## 📝 Generate Reports

### Full Validation Report
```bash
python learning_validation_report.py
```

Creates:
- `reports/learning_validation/validation_report_TIMESTAMP.md` (Markdown)
- `reports/learning_validation/validation_report_TIMESTAMP.json` (JSON)

### Quick Summary
```bash
python learning_validation_report.py --summary-only
```

---

## 🔍 API Access

### Check Status
```bash
curl http://localhost:8001/api/learning/status
```

### Get Analytics
```bash
curl http://localhost:8001/api/learning/analytics
```

### View API Docs
Visit: http://localhost:8001/docs

---

## 📚 What Gets Logged

Every learning activity records:

```json
{
  "source_url": "https://example.com/tutorial",
  "source_type": "web_scrape",
  "timestamp": "2025-11-15T21:49:45Z",
  "data_size": "45.5 KB",
  "validation_score": "95%",
  "status": "validated"
}
```

**Logs stored in:** `logs/learning_activities/`

---

## 🎓 Example Use Cases

### Use Case 1: Audit Compliance
**Question:** "Where did Grace learn about Python web scraping?"

**Answer:**
```bash
# Generate report
python learning_validation_report.py

# Check the markdown file for complete source URLs
cat reports/learning_validation/validation_report_*.md
```

### Use Case 2: Quality Control
**Question:** "Is Grace learning accurate data?"

**Answer:**
```bash
# Watch the dashboard
python learning_dashboard.py

# Look for validation scores (should be >80%)
# Check for failed activities and review them
```

### Use Case 3: Performance Monitoring
**Question:** "How fast is Grace learning?"

**Answer:**
```bash
# View API analytics
curl http://localhost:8001/api/learning/analytics | jq '.data.learning_velocity'

# Shows: activities per hour, MB per hour
```

---

## 🔧 Key Features

### Source Traceability
- ✅ Every URL is logged
- ✅ Timestamps for each access
- ✅ SHA-256 hashes for integrity
- ✅ Complete audit trail

### Validation
- ✅ Automatic data verification
- ✅ Integrity checks (hash validation)
- ✅ Size and format validation
- ✅ Source accessibility verification
- ✅ Scoring (0-100%)

### Real-time Monitoring
- ✅ Live dashboard (3s refresh)
- ✅ Activity feed with URLs
- ✅ Validation status indicators
- ✅ System health alerts
- ✅ Learning velocity metrics

### Reports
- ✅ Markdown reports (human-readable)
- ✅ JSON exports (machine-readable)
- ✅ Complete source URL lists
- ✅ Analytics and metrics
- ✅ Performance statistics

---

## 📁 File Structure

```
grace_2/
├── backend/
│   ├── remote_access/
│   │   └── learning_tracker.py         # Core tracking engine
│   └── routes/
│       └── learning_visibility_api.py  # REST API
├── logs/
│   └── learning_activities/
│       ├── activities.jsonl            # All activities
│       ├── sessions.json               # Learning sessions
│       └── metrics.json                # Aggregated metrics
├── reports/
│   └── learning_validation/
│       ├── validation_report_*.md      # Markdown reports
│       └── validation_report_*.json    # JSON reports
├── learning_dashboard.py               # Real-time dashboard
├── learning_validation_report.py       # Report generator
└── test_learning_visibility.py         # Test suite
```

---

## 🚨 Troubleshooting

### Dashboard shows "CONNECTION ERROR"
```bash
# Make sure backend is running
python serve.py

# Check if port 8001 is available
curl http://localhost:8001/health
```

### No activities showing
```bash
# Run the test to generate sample data
python test_learning_visibility.py
```

### API not responding
```bash
# Check backend logs
tail -f logs/backend.log

# Verify API is registered
curl http://localhost:8001/docs
```

---

## 📖 Learn More

- **Full Documentation:** [`LEARNING_VISIBILITY_COMPLETE.md`](./LEARNING_VISIBILITY_COMPLETE.md)
- **API Documentation:** http://localhost:8001/docs
- **Remote Access Setup:** [`REMOTE_ACCESS_COMPLETE_FINAL.md`](./REMOTE_ACCESS_COMPLETE_FINAL.md)

---

## ✅ Quick Checklist

- [ ] Backend running (`python serve.py`)
- [ ] Test completed (`python test_learning_visibility.py`)
- [ ] Dashboard launched (`python learning_dashboard.py`)
- [ ] Reports generated (`python learning_validation_report.py`)
- [ ] Logs directory exists (`logs/learning_activities/`)
- [ ] API accessible (`http://localhost:8001/docs`)

---

## 🎉 You're Ready!

You now have **complete visibility** into Grace's learning activities with:
- **Real-time monitoring**
- **Source URL traceability**
- **Automatic validation**
- **Comprehensive reports**

**Start monitoring:** `python learning_dashboard.py` 🚀