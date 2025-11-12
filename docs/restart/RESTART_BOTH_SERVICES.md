# 🔄 Restart Both Services to See New Features

## ⚠️ Restart Required

New UI dashboards and API endpoints won't work until you restart:

### 1. Restart Backend

**In the terminal running the backend (port 8000):**
1. Press `Ctrl+C` to stop
2. Run: `python serve.py`
3. Wait for "Uvicorn running on http://0.0.0.0:8000"

### 2. Restart Frontend  

**In the terminal running the frontend (port 5173):**
1. Press `Ctrl+C` to stop
2. Run: `npm run dev`
3. Wait for "Local: http://localhost:5173/"

## ✅ After Restart

### New Dashboards Available at localhost:5173

Click these tabs in the nav bar:
- **🔍 Clarity** - Clarity Framework (components, events, mesh)
- **🧠 LLM** - LLM system status and configuration
- **💡 Intel** - Intelligence kernel status
- **📥 Ingest** - Knowledge ingestion with START/STOP controls
- **🎓 Learn** - Continuous learning loop status

### New API Endpoints at localhost:8000

```bash
# LLM
curl http://localhost:8000/api/llm/status

# Intelligence
curl http://localhost:8000/api/intelligence/status

# Ingestion
curl http://localhost:8000/api/ingestion/status
curl http://localhost:8000/api/ingestion/tasks
curl -X POST "http://localhost:8000/api/ingestion/start?task_type=github&source=https://github.com/test/repo"

# Learning
curl http://localhost:8000/api/learning/status

# Clarity
curl http://localhost:8000/api/clarity/status
curl http://localhost:8000/api/clarity/components
curl http://localhost:8000/api/clarity/events?limit=50
```

## 🎨 What You'll See

### Clarity Dashboard
- Event bus stats (total events, subscribers)
- Component manifest (registered components, trust levels)
- Trigger mesh configuration (23 events)
- Real-time event history

### Ingestion Dashboard
- Active task counters
- Start new ingestion form (GitHub/Reddit/YouTube/Web)
- Live progress bars for running tasks
- Stop task buttons
- Available modules display

### LLM Dashboard
- LLM status (operational/stub)
- Model information
- Availability indicators
- Stub mode warnings

### Intelligence Dashboard
- Kernel status
- Operational mode
- About section

### Learning Dashboard  
- Learning system status
- Component availability
- Learning types overview (Mission, Healing, Code, Patterns)

## 🔧 Quick Restart Commands

```powershell
# Backend
python serve.py

# Frontend
cd frontend
npm run dev
```

## ✅ Verification

After restart, test one endpoint:
```bash
curl http://localhost:8000/api/ingestion/status
```

Should return JSON with `component_type: "ingestion_orchestrator"` instead of 404.

**All UI components are created and ready - just restart to activate! 🚀**
