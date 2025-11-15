# GRACE Dashboard MVP - Quick Start Guide

**Get the dashboard running in 30 minutes**

---

## Prerequisites

- Python 3.9+ (backend)
- Node.js 16+ (frontend)
- Backend already running on `http://localhost:8000`

---

## Step 1: Register Backend Routes (5 minutes)

Edit your main FastAPI app file (e.g., `serve.py` or `main.py`):

```python
from backend.routes import (
    telemetry_api,
    kernels_api,
    copilot_api,
    htm_management,
    intent_management
)

# Register routers
app.include_router(telemetry_api.router)
app.include_router(kernels_api.router)
app.include_router(copilot_api.router)
app.include_router(htm_management.router)
app.include_router(intent_management.router)
```

Restart your backend:
```bash
python serve.py
```

Verify endpoints at: `http://localhost:8000/docs`

---

## Step 2: Install Frontend Dependencies (2 minutes)

```bash
cd frontend
npm install axios
```

---

## Step 3: Update Frontend Entry Point (2 minutes)

Edit `frontend/src/main.tsx`:

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { AppMVP } from './App.MVP.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppMVP />
  </React.StrictMode>,
)
```

---

## Step 4: Start Frontend (1 minute)

```bash
npm run dev
```

Visit: `http://localhost:5173`

---

## Step 5: Test the Dashboard (5 minutes)

### Test Layer 1

1. **View Telemetry Cards**
   - See kernel metrics (Total, Active, Idle, Errors, Boot Time)
   - Verify numbers update every 5 seconds

2. **Test Quick Actions**
   - Click [⚡ Run Boot Stress] → Should trigger stress test
   - Click [🔐 Check Crypto Status] → Metrics refresh

3. **Expand Kernel Terminal**
   - Click [▼] on "Memory Kernel"
   - See console section expand
   - See logs appear (polling every 5s)
   - Click [Export] to download logs

4. **Control Kernel**
   - Click [↻ Restart] button
   - See confirmation/toast
   - Verify kernel status updates

5. **Test Co-Pilot**
   - Look at right rail → See Grace avatar
   - See 3 mock notifications
   - Click action button in notification
   - Type "help" in chat input
   - See Grace respond

---

## Verify Everything Works

### Backend Health Check

Visit `http://localhost:8000/docs` and test:

✅ `GET /api/kernels/layer1/status` → Returns 7 kernels  
✅ `POST /api/kernels/{id}/action` → Test with action="restart"  
✅ `GET /api/telemetry/kernels/status` → Returns metrics  
✅ `POST /api/copilot/chat/send` → Returns Grace response  
✅ `GET /api/copilot/notifications` → Returns notifications

---

### Frontend Component Check

Open browser console, verify:

✅ No JavaScript errors  
✅ API calls succeed (Network tab)  
✅ Kernel terminals render (7 visible)  
✅ Co-pilot pane visible on right  
✅ Notifications show (3 cards)  
✅ Chat input functional

---

## Troubleshooting

### Backend Issues

**Problem**: Endpoints not found (404)  
**Solution**: Verify routes registered in `serve.py`, restart backend

**Problem**: CORS errors  
**Solution**: Add CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problem**: WebSocket not connecting  
**Solution**: For MVP, WebSocket is disabled (using polling instead)

---

### Frontend Issues

**Problem**: Components not found  
**Solution**: Verify files exist:
- `frontend/src/components/KernelTerminal.tsx`
- `frontend/src/components/CoPilotPane.tsx`
- `frontend/src/pages/Layer1DashboardMVP.tsx`
- `frontend/src/App.MVP.tsx`

**Problem**: API calls fail  
**Solution**: Check `API_BASE` constant in components matches backend URL

**Problem**: Blank screen  
**Solution**: Check browser console for errors, verify main.tsx imports correctly

---

## What You Should See

### Layer 1 Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│ GRACE Dashboard   [🎛️ Layer 1] [📊 Layer 2] ...            │
├──────────────────────────────────────┬──────────────────────┤
│ 🎛️ Layer 1: Operations Console       │ Grace Co-Pilot      │
│                                      │ [🟢 Ready]           │
│ Kernel Overview                      ├──────────────────────┤
│ ┌─────┬─────┬─────┬─────┬──────┐    │ Notifications (3)    │
│ │Total│Active│Idle│Error│ Boot │    │ ┌──────────────────┐ │
│ │  7  │  5  │  2 │  0  │1250ms│    │ │🔴 Kernel crashed │ │
│ └─────┴─────┴─────┴─────┴──────┘    │ │  [Restart][Logs] │ │
│                                      │ └──────────────────┘ │
│ [⚡ Run Stress][🗑️ Flush][🔐 Check] │ ...                  │
│                                      ├──────────────────────┤
│ Core Execution Kernels               │ Chat                 │
│ ┌────────────────────────────────┐   │ ┌──────────────────┐ │
│ │[Memory Kernel]────[●]Active[▼]│   │ │You: help         │ │
│ │ Uptime: 3h 25m | Tasks: 45    │   │ │Grace: I can help │ │
│ │ [▶][■][↻][⚙][📋]              │   │ │with...           │ │
│ └────────────────────────────────┘   │ └──────────────────┘ │
│ [Librarian Kernel]                   │ Input                │
│ [Governance Kernel]                  │ [Ask Grace...]       │
│ [Verification Kernel]                │ [Send]               │
│ [Self-Healing Kernel]                ├──────────────────────┤
│ [Ingestion Kernel]                   │ Quick Actions        │
│ [Crypto Kernel]                      │ [Restart All]        │
└──────────────────────────────────────┴──────────────────────┘
```

---

## Next Steps After MVP

### Immediate Enhancements (Week 4)
- [ ] Build Layer 2-4 dashboards (similar to Layer 1)
- [ ] Add WebSocket for real-time logs (replace polling)
- [ ] Enhance Grace chat with better pattern matching
- [ ] Add loading spinners to all actions
- [ ] Add error toasts for failed actions

### Medium-Term (Weeks 5-6)
- [ ] Integrate Grace's LLM (OpenAI/Anthropic)
- [ ] Add voice input support
- [ ] Build visual playbook editor
- [ ] Add drag-drop priority queue
- [ ] Implement advanced charts

### Long-Term (Weeks 7-8)
- [ ] Mobile responsive design
- [ ] Screenshot capture
- [ ] File upload analysis
- [ ] Advanced telemetry dashboards
- [ ] User preferences & themes

---

## MVP Success Metrics

**Must Work**:
- ✅ All 4 layers accessible via nav
- ✅ Layer 1 shows 7 kernel terminals
- ✅ Kernel terminals expand/collapse
- ✅ Logs display (via polling)
- ✅ Restart action works
- ✅ Co-pilot shows notifications
- ✅ Co-pilot chat responds to "help"
- ✅ Quick actions execute

**Performance**:
- Page load: < 3 seconds
- Action response: < 2 seconds
- Polling overhead: < 5% CPU
- No memory leaks after 10 minutes

---

## File Manifest (MVP)

### Backend (5 files)
```
backend/routes/
├── telemetry_api.py          ✅ Existing (26 endpoints)
├── kernels_api.py            ✅ Built (8 endpoints)
├── copilot_api.py            ✅ Built (7 endpoints)
├── htm_management.py         ✅ Built (7 endpoints)
└── intent_management.py      ✅ Built (3 endpoints)
```

### Frontend (7 files)
```
frontend/src/
├── components/
│   ├── KernelTerminal.tsx    ✅ Built
│   ├── KernelTerminal.css    ✅ Built
│   ├── CoPilotPane.tsx       ✅ Built
│   └── CoPilotPane.css       ✅ Built
├── pages/
│   ├── Layer1DashboardMVP.tsx  ✅ Built
│   └── Layer1DashboardMVP.css  ✅ Built
├── App.MVP.tsx               ✅ Built
└── App.MVP.css               ✅ Built
```

**Total**: 12 files ready to run

---

## Known Limitations (MVP)

1. **WebSocket**: Using polling instead (5s interval)
2. **Grace Intelligence**: Basic pattern matching (no LLM yet)
3. **Multi-Modal**: Text-only (no voice/file/screenshot)
4. **Layers 2-4**: Placeholder pages (build similar to Layer 1)
5. **Charts**: Tables only (no visual charts)
6. **Mobile**: Desktop-only (no responsive design)
7. **Themes**: Dark theme only
8. **Low-Code**: Simple forms (no visual editors)

**These will be added post-MVP**

---

## MVP Deployment Checklist

- [ ] Backend routes registered
- [ ] Backend running on port 8000
- [ ] Frontend dependencies installed
- [ ] Frontend `main.tsx` updated to use `AppMVP`
- [ ] Frontend running on port 5173
- [ ] CORS configured
- [ ] All endpoints return 200 OK
- [ ] Layer 1 dashboard loads
- [ ] Kernel terminals work
- [ ] Co-pilot pane visible
- [ ] Actions execute without errors

**Once checked, MVP is live!** 🚀

---

## Support

**Issues?** Check:
1. [MVP_IMPLEMENTATION_PLAN.md](./MVP_IMPLEMENTATION_PLAN.md) - Full MVP spec
2. [KERNEL_LAYER_MAPPING.md](./docs/KERNEL_LAYER_MAPPING.md) - Kernel assignments
3. Browser console for JavaScript errors
4. Backend logs for API errors
5. Network tab for failed requests

**Questions?** Review full documentation in `docs/` folder.

**🎊 GRACE Dashboard MVP: Ready to Run! 🎊**
