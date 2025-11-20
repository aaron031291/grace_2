# Frontend Integration - Complete Guide

## 🚨 HAVING MODULE LOADING ERRORS?

### **→ SEE [START_HERE_NOW.md](START_HERE_NOW.md) ←**

Run this one command:
```bash
START_GRACE_COMPLETE.bat
```
Problem solved! ✅

---

## 📚 Documentation Index

### Quick Start & Fixes
| File | Purpose | When to Use |
|------|---------|-------------|
| **[START_HERE_NOW.md](START_HERE_NOW.md)** | Start here if you have errors | First stop for any issues |
| **[QUICK_FIX.md](QUICK_FIX.md)** | 2-minute fix for module errors | Module loading errors |
| **[FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md)** | Detailed troubleshooting | Persistent issues |

### Integration Guides
| File | Purpose | When to Use |
|------|---------|-------------|
| **[BACKEND_UI_INTEGRATION.md](BACKEND_UI_INTEGRATION.md)** | Complete integration guide | Adding new features |
| **[API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)** | API endpoint reference | Using APIs |
| **[INTEGRATION_STATUS.md](INTEGRATION_STATUS.md)** | Current integration status | Overview of what's connected |

### Startup Scripts
| Script | Purpose | When to Use |
|--------|---------|-------------|
| **START_GRACE_COMPLETE.bat** | Start everything fresh | Clean start, fixes cache issues |
| **FRONTEND_ONLY.bat** | Just start frontend | Backend already running |
| **RESTART_FRONTEND.bat** | Restart frontend with cache clear | Frontend issues only |
| **TEST_INTEGRATION.bat** | Test backend-frontend connection | Verify integration |

---

## 🎯 Common Scenarios

### Scenario 1: "I just cloned the repo"
```bash
START_GRACE_COMPLETE.bat
```
Opens on http://localhost:5173

### Scenario 2: "I'm seeing module loading errors"
```bash
START_GRACE_COMPLETE.bat
```
Clears cache and restarts everything.

### Scenario 3: "Backend works, frontend broken"
```bash
FRONTEND_ONLY.bat
```
Restarts just the frontend.

### Scenario 4: "I want to add a new API endpoint"
Read: [BACKEND_UI_INTEGRATION.md](BACKEND_UI_INTEGRATION.md) → "How to Add New API Endpoints"

### Scenario 5: "I need API endpoint URLs"
Read: [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)

### Scenario 6: "Nothing works, total reset needed"
See: [FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md) → "Complete Reset"

---

## 🏗️ Architecture Overview

```
Grace System
│
├── Backend (FastAPI)
│   ├── Port: 8000
│   ├── Routes: 180+ endpoints
│   ├── Services: Guardian, Self-Healing, Learning, etc.
│   └── API Docs: http://localhost:8000/docs
│
└── Frontend (React + Vite)
    ├── Port: 5173
    ├── API Clients: 30+ TypeScript files
    ├── Components: UI components
    ├── Proxy: /api/* → http://localhost:8000
    └── UI: http://localhost:5173
```

---

## ✅ Integration Checklist

Your system has:
- ✅ Backend with 180+ API routes
- ✅ Frontend with 30+ API clients
- ✅ CORS configured
- ✅ Vite proxy configured
- ✅ TypeScript types
- ✅ Environment config
- ✅ Health checks
- ✅ API documentation

---

## 🔧 Key Files

### Backend
- `backend/main.py` - Registers all routes
- `backend/routes/*_api.py` - 180+ route files
- `server.py` - Main entry point

### Frontend
- `frontend/src/api/*.ts` - 30+ API clients
- `frontend/src/config.ts` - API configuration
- `frontend/vite.config.ts` - Proxy configuration
- `frontend/src/main.tsx` - App entry point

---

## 🚀 Development Workflow

### 1. Start System
```bash
START_GRACE_COMPLETE.bat
```

### 2. Open Browser
http://localhost:5173

### 3. Open DevTools
Press F12 to see console and network activity

### 4. Make Changes
- Backend: Edit `backend/routes/*.py`
- Frontend: Edit `frontend/src/**/*.tsx`
- Changes hot-reload automatically

### 5. Test
- Backend: http://localhost:8000/docs
- Frontend: Browser + DevTools
- API: Use browser console or curl

---

## 📊 Available APIs

### Chat & Communication
- `/api/chat` - Chat with Grace
- `/api/chat/sessions` - Chat sessions
- `/api/chat/history/{id}` - Chat history

### System Monitoring
- `/api/metrics/summary` - System metrics
- `/api/metrics/health` - Health status
- `/api/guardian/status` - Guardian status

### Mission Control
- `/api/mission-control/missions` - List missions
- `/api/mission-control/execute/{id}` - Execute mission

### Self-Healing
- `/api/self-healing/stats` - Healing stats
- `/api/self-healing/incidents` - Incidents

### Learning
- `/api/learning/status` - Learning status
- `/api/learning/outcomes` - Outcomes

**See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) for complete list**

---

## 🐛 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Module loading errors | [QUICK_FIX.md](QUICK_FIX.md) |
| Port conflicts | [FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md#cause-3-port-already-in-use) |
| CORS errors | [FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md#issue-cors-error) |
| Frontend won't start | Run `FRONTEND_ONLY.bat` |
| Backend won't start | Check port 8000: `netstat -ano \| findstr :8000` |
| Cache issues | Run `START_GRACE_COMPLETE.bat` |

---

## 🎓 Learning Resources

### New to Grace?
1. Start: [START_HERE_NOW.md](START_HERE_NOW.md)
2. Explore: http://localhost:5173
3. Read: [INTEGRATION_STATUS.md](INTEGRATION_STATUS.md)

### Want to Add Features?
1. Read: [BACKEND_UI_INTEGRATION.md](BACKEND_UI_INTEGRATION.md)
2. Reference: [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
3. Test: `TEST_INTEGRATION.bat`

### Having Issues?
1. Quick: [QUICK_FIX.md](QUICK_FIX.md)
2. Detailed: [FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md)
3. Reset: Run `START_GRACE_COMPLETE.bat`

---

## ✨ Success Indicators

When everything works:
- ✅ Backend shows "GRACE IS READY"
- ✅ Frontend shows "VITE ready"
- ✅ Browser shows UI at http://localhost:5173
- ✅ No red errors in console (F12)
- ✅ API calls work (test in Network tab)

---

## 🆘 Emergency Contacts

**Stuck?**
1. Read [START_HERE_NOW.md](START_HERE_NOW.md)
2. Try `START_GRACE_COMPLETE.bat`
3. Check [FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md)

**Still stuck?**
- Check browser console (F12)
- Check backend terminal for errors
- Check frontend terminal for errors
- Try complete reset (see FIX_FRONTEND_ERRORS.md)

---

**Current Status**: ✅ Backend and Frontend fully integrated and ready!

**Next Step**: Run `START_GRACE_COMPLETE.bat` and open http://localhost:5173
