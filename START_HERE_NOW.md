# 🚀 START HERE - Grace Backend + Frontend

## 🎯 You Have Module Loading Errors? Run This:

```bash
START_GRACE_COMPLETE.bat
```

Wait 30 seconds, then open: http://localhost:5173

**That's it!** ✅

---

## 📋 What Just Happened?

The script:
1. ✅ Stopped old processes
2. ✅ Cleared Vite cache (fixes module errors)
3. ✅ Started backend (port 8000)
4. ✅ Started frontend (port 5173)

---

## 🌐 Access Points

| What | URL | Status |
|------|-----|--------|
| **Grace UI** | http://localhost:5173 | Your main interface |
| **API Server** | http://localhost:8000 | Backend services |
| **API Docs** | http://localhost:8000/docs | Interactive API explorer |
| **Health** | http://localhost:8000/health | System status |

---

## ✅ Verify It's Working

### 1. Open Browser
http://localhost:5173

### 2. Check Console (F12)
Should see:
- ✅ `[CONFIG] {...}` message
- ✅ No red module loading errors
- ✅ UI renders

### 3. Test API Connection
In browser console (F12):
```javascript
fetch('/api/metrics/summary').then(r => r.json()).then(console.log)
```
Should return data, not error.

---

## 🔧 Common Issues

### "Module Loading Failed"
**Fix**: You're here! Run `START_GRACE_COMPLETE.bat`

### "Port Already in Use"
**Fix**:
```bash
# Find what's using the port
netstat -ano | findstr :5173
# or
netstat -ano | findstr :8000

# Kill it (use PID from above)
taskkill /PID <PID> /F

# Try again
START_GRACE_COMPLETE.bat
```

### "Cannot Connect to Backend"
**Fix**: Make sure backend is running
```bash
# Check if backend is running
netstat -ano | findstr :8000

# If not, start it
python server.py
```

---

## 📖 Next Steps

### Explore the UI
- **System Overview** - See system status, missions, incidents
- **Mission Control** - Manage autonomous missions
- **Learning Hub** - View learning progress
- **Chat** - Interact with Grace
- **Memory Explorer** - Browse ingested knowledge

### Test the API
Open http://localhost:8000/docs to see all 180+ API endpoints

### Read the Docs
- **[QUICK_FIX.md](QUICK_FIX.md)** - Quick troubleshooting
- **[BACKEND_UI_INTEGRATION.md](BACKEND_UI_INTEGRATION.md)** - How backend connects to UI
- **[API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)** - API endpoint reference
- **[FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md)** - Detailed troubleshooting

---

## 🎓 Development

### Start Both Services
```bash
START_GRACE_COMPLETE.bat
```

### Start Individually
```bash
# Backend only
python server.py

# Frontend only
FRONTEND_ONLY.bat
```

### Restart Just Frontend
```bash
RESTART_FRONTEND.bat
```

---

## 📊 Architecture

```
┌─────────────────────────────────┐
│   Frontend (React + Vite)       │
│   http://localhost:5173         │
│                                 │
│   • 30+ API Clients             │
│   • React Components            │
│   • Vite Proxy (/api/*)         │
└────────────┬────────────────────┘
             │
             │ HTTP Proxy
             ▼
┌─────────────────────────────────┐
│   Backend (FastAPI)             │
│   http://localhost:8000         │
│                                 │
│   • 180+ API Routes             │
│   • CORS Enabled                │
│   • Guardian, Self-Healing,     │
│     Learning, Mission Control   │
└─────────────────────────────────┘
```

---

## ⚡ Quick Commands

```bash
# Start everything (recommended)
START_GRACE_COMPLETE.bat

# Just frontend
FRONTEND_ONLY.bat

# Test connection
TEST_INTEGRATION.bat

# View API docs
start http://localhost:8000/docs

# View UI
start http://localhost:5173
```

---

## 🎉 Success Checklist

When everything works:
- ✅ Backend running (see "GRACE IS READY" message)
- ✅ Frontend running (see "VITE ready" message)
- ✅ http://localhost:5173 loads
- ✅ No module errors in browser console
- ✅ UI displays properly
- ✅ API calls work (test in Network tab)

---

## 🆘 Still Having Problems?

1. **Complete reset**:
   ```bash
   # Stop everything
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe
   
   # Clear caches
   cd frontend
   rmdir /s /q node_modules\.vite
   cd ..
   
   # Restart
   START_GRACE_COMPLETE.bat
   ```

2. **Check logs**:
   - Backend: Look at the terminal running `server.py`
   - Frontend: Look at the terminal running Vite
   - Browser: Open DevTools (F12) → Console tab

3. **Read the docs**:
   - [QUICK_FIX.md](QUICK_FIX.md) - Fast solutions
   - [FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md) - Detailed help

---

**Ready? Run this now:**
```bash
START_GRACE_COMPLETE.bat
```

Then open http://localhost:5173 and start using Grace! 🚀
