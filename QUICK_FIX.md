# 🔧 Quick Fix - Frontend Module Loading Errors

## The Problem
You're seeing these errors in the browser console:
```
Loading failed for the module with source "http://localhost:5173/@vite/client"
Loading failed for the module with source "http://localhost:5173/src/components/..."
```

## ✅ The Solution (2 Minutes)

### Step 1: Stop Everything
Press `Ctrl+C` in all terminal windows running Grace

### Step 2: Run This
```bash
START_GRACE_COMPLETE.bat
```

That's it! The script will:
- Clean up old processes
- Clear Vite cache
- Start backend
- Start frontend
- Open in new windows

### Alternative: Just Restart Frontend
If backend is fine, just run:
```bash
FRONTEND_ONLY.bat
```

---

## 🎯 What Happened?

The module loading errors happen because:
1. **Vite cache got stale** - Old module references cached
2. **Frontend server had issues** - Needs clean restart
3. **Hot module replacement failed** - HMR state corrupted

**Solution**: Clear cache + fresh start = ✅

---

## 📊 After Restarting

### You Should See:

**Backend Terminal:**
```
[GUARDIAN] BOOT COMPLETE
  ✓ Port: 8000
  ✓ Network: Healthy
  
GRACE IS READY
Backend:  http://localhost:8000
Frontend: http://localhost:5173
```

**Frontend Terminal:**
```
VITE v7.1.7  ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Browser:**
- No red errors in console (F12)
- UI loads and displays
- Components render properly

---

## 🧪 Test It Works

### Test 1: Open Browser
http://localhost:5173

### Test 2: Check Console (F12)
Should see:
```
[CONFIG] {API_BASE_URL: '', WS_BASE_URL: 'ws://localhost:5173', ...}
```
No module loading errors!

### Test 3: Test API
In browser console:
```javascript
fetch('/api/metrics/summary')
  .then(r => r.json())
  .then(console.log)
```
Should return data, not error.

---

## 🚨 If Still Broken

### Nuclear Option (Complete Reset)
```bash
# Stop everything
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Clear all caches
cd frontend
rmdir /s /q node_modules\.vite
rmdir /s /q dist

# Restart
cd ..
START_GRACE_COMPLETE.bat
```

### Check for Port Conflicts
```bash
netstat -ano | findstr :5173
netstat -ano | findstr :8000
```
If either port is in use, kill that process:
```bash
taskkill /PID <PID> /F
```

---

## ✨ Scripts Available

| Script | Purpose |
|--------|---------|
| `START_GRACE_COMPLETE.bat` | Clean start of everything |
| `FRONTEND_ONLY.bat` | Just restart frontend |
| `RESTART_FRONTEND.bat` | Frontend with cache clear |
| `TEST_INTEGRATION.bat` | Test backend-frontend connection |

---

## 📚 More Help

- **Full troubleshooting**: [FIX_FRONTEND_ERRORS.md](FIX_FRONTEND_ERRORS.md)
- **Integration guide**: [BACKEND_UI_INTEGRATION.md](BACKEND_UI_INTEGRATION.md)
- **API reference**: [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)

---

**TL;DR**: Run `START_GRACE_COMPLETE.bat` and wait 30 seconds. Problem solved! 🎉
