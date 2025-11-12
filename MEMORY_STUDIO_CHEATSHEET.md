# Memory Studio - Quick Reference Cheatsheet 📝

## 🚀 Quick Start (30 seconds)

```bash
# 1. Start servers
python -m uvicorn backend.main:app --reload --port 8000
cd frontend && npm run dev

# 2. Open browser
http://localhost:5173 → Click "📁 Memory"

# 3. You're in!
```

---

## 🎯 3 Main Views

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| **Workspace** | File management | Upload, edit, Grace chat |
| **Pipelines** | Process files | 6 workflows, job monitoring |
| **Dashboard** | Analytics | Metrics, insights, charts |

---

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Save file | `Ctrl+S` |
| Find in file | `Ctrl+F` |
| Hard refresh | `Ctrl+Shift+R` |
| Open console | `F12` |

---

## 🎨 UI Elements

### Workspace Tab
```
Left Panel:   File tree + action buttons
Right Panel:  Monaco editor OR file preview
Chat Panel:   Grace AI (toggle with "Grace" button)
Footer:       Tags, embedding status, metadata
```

### Pipelines Tab
```
Left Panel:   Pipeline library (6 workflows)
Right Panel:  Active jobs with progress bars
Auto-refresh: Every 3 seconds
```

### Dashboard Tab
```
Top Row:      4 metric cards
Middle:       Pipeline usage chart
Bottom:       Recent jobs list
```

---

## 📊 6 Built-in Pipelines

| Pipeline | Input | Output | Use Case |
|----------|-------|--------|----------|
| Text to Embeddings | .txt, .md | Vectors | Search |
| PDF Extraction | .pdf | Text + Vectors | Documents |
| Code Analysis | .py, .js, .ts | Index | Code search |
| Audio Transcription | .mp3, .wav | Transcript | Meetings |
| Image Vision | .jpg, .png | Captions | Images |
| Batch Training | * | Dataset | ML training |

---

## 🤖 Grace Quick Actions

| Button | What It Does |
|--------|--------------|
| **Summarize** | Brief overview of file |
| **Key Points** | Extract main ideas |
| **Improve** | Suggest enhancements |
| **Questions** | Generate quiz questions |

Custom: Type anything in chat input

---

## 📡 Most Used API Endpoints

### Files
```bash
GET  /api/memory/files          # List files
GET  /api/memory/file?path=X    # Read file
POST /api/memory/file           # Save file
POST /api/memory/upload         # Upload file
GET  /api/memory/status         # Get stats
```

### Pipelines
```bash
GET  /api/ingestion/pipelines   # List workflows
POST /api/ingestion/start       # Start pipeline
GET  /api/ingestion/jobs        # List jobs
GET  /api/ingestion/metrics     # Get metrics
```

### Intelligence
```bash
POST /api/ingestion/analyze     # Analyze file
GET  /api/ingestion/insights    # Get insights
GET  /api/ingestion/schedules   # List automations
```

---

## 🏷️ Auto-Generated Tags

| File Type | Auto Tags |
|-----------|-----------|
| `.py` | python, code, script |
| `.md` | markdown, documentation, text |
| `.pdf` | pdf, document, needs-extraction |
| `.jpg` | image, visual, needs-vision |
| `.mp3` | audio, needs-transcription |
| `.json` | json, data, config |

Plus content-based: api, testing, database, machine-learning

---

## 📈 Quality Score Ranges

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100 | High quality | Auto-approve |
| 50-79 | Medium quality | Review recommended |
| 0-49 | Low quality | Fix or reject |

---

## 🔔 Status Icons

| Icon | Status | Color |
|------|--------|-------|
| ✓ | Complete | Green |
| ⚠ | Running | Blue |
| ✗ | Failed | Red |
| ⏸ | Paused | Gray |
| ⌛ | Queued | Yellow |

---

## 🎯 Common Workflows

### Upload & Process
```
1. Drag file to Workspace
2. Click "Pipelines" tab
3. See recommended pipeline
4. Click pipeline to start
5. Watch progress bar
```

### Schedule Automation
```
1. POST /api/ingestion/schedules
2. Set pipeline_id + schedule_type
3. Configure time (hour, minute)
4. Enable schedule
5. Runs automatically
```

### Check Quality
```
1. Upload file
2. POST /api/ingestion/analyze
3. Check quality_score
4. Review recommendations
5. Fix if needed
```

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| 404 errors | Restart backend |
| Blank screen | Hard refresh (Ctrl+Shift+R) |
| Jobs not updating | Wait 3s (auto-refresh) |
| Upload fails | Check file size < 50MB |
| No metrics | Run a pipeline first |

---

## 📁 File Organization

```
grace_training/
  ├── documents/    # PDFs, Word docs
  ├── code/         # Source files
  ├── data/         # JSON, CSV, YAML
  ├── media/        # Images, audio, video
  └── training/     # ML training data
```

---

## 💡 Pro Tips

### Tip 1: Use Templates
```bash
GET /api/ingestion/templates
# Returns pre-made automation configs
```

### Tip 2: Batch Upload
```
Select 10+ files in file picker
All upload with individual progress bars
```

### Tip 3: Quick Analysis
```
Upload → Auto-metadata created
Check footer for tags & status
```

### Tip 4: Monitor Health
```
Dashboard tab shows:
- Success rate
- Failed jobs
- Pipeline usage
```

### Tip 5: Ask Grace Anything
```
Select file → Grace button → Type question
Grace reads file content for context
```

---

## 📊 Metric Cards Explained

| Card | Meaning |
|------|---------|
| **Total Jobs** | All-time pipeline runs |
| **Completed** | Successfully finished |
| **Running** | Currently processing |
| **Failed** | Errors encountered |

---

## 🎨 Color Coding

| Color | Meaning |
|-------|---------|
| Purple (#8b5cf6) | Primary actions, active states |
| Blue (#3b82f6) | Running, info |
| Green (#10b981) | Success, complete |
| Red (#ef4444) | Failed, error, delete |
| Yellow (#f59e0b) | Warning, modified |
| Gray (#6b7280) | Inactive, disabled |

---

## 🔑 Environment Variables

```bash
VITE_API_URL=http://localhost:8000    # Backend URL
GRACE_ENV=development                 # Environment
GRACE_DEBUG=true                      # Debug mode
```

---

## 📞 Getting Help

| Issue | Check |
|-------|-------|
| Features | [MEMORY_STUDIO_COMPLETE.md](file:///c:/Users/aaron/grace_2/MEMORY_STUDIO_COMPLETE.md) |
| Quick Start | [MEMORY_STUDIO_QUICKSTART.md](file:///c:/Users/aaron/grace_2/MEMORY_STUDIO_QUICKSTART.md) |
| Advanced | [MEMORY_STUDIO_ADVANCED.md](file:///c:/Users/aaron/grace_2/MEMORY_STUDIO_ADVANCED.md) |
| Overview | [MEMORY_STUDIO_OVERVIEW.md](file:///c:/Users/aaron/grace_2/MEMORY_STUDIO_OVERVIEW.md) |
| API Docs | http://localhost:8000/docs |

---

## ✅ Health Check

```bash
# Backend
curl http://localhost:8000/api/ingestion/metrics

# Should return JSON, not error

# Frontend
Open http://localhost:5173
# Should see Grace interface
```

---

## 🎯 Success Checklist

- [ ] Backend running (port 8000)
- [ ] Frontend running (port 5173)
- [ ] Can navigate 3 tabs
- [ ] Can upload files
- [ ] Can start pipelines
- [ ] Can see metrics
- [ ] Can chat with Grace

All checked? **You're ready!** 🚀

---

**Print this page for quick reference!**
