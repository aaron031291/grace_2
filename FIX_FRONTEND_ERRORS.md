# Fix Frontend Module Loading Errors

## 🔴 Problem
You're seeing errors like:
```
Loading failed for the module with source "http://localhost:5173/@vite/client"
Loading failed for the module with source "http://localhost:5173/src/components/..."
```

## ✅ Solution

### Quick Fix (Recommended)

1. **Stop the frontend server** (Ctrl+C in the terminal)
2. **Run the restart script**:
   ```bash
   RESTART_FRONTEND.bat
   ```

### Manual Fix

1. **Stop frontend server** (Ctrl+C)

2. **Clear Vite cache**:
   ```bash
   cd frontend
   rmdir /s /q node_modules\.vite
   ```

3. **Restart dev server**:
   ```bash
   npm run dev
   ```

4. **Refresh browser** (Ctrl+F5)

---

## 🔍 Root Causes & Solutions

### Cause 1: Vite Cache Issues
**Symptoms**: Modules fail to load, stale imports  
**Solution**:
```bash
cd frontend
rmdir /s /q node_modules\.vite
npm run dev
```

### Cause 2: Frontend Server Not Running
**Symptoms**: All modules fail to load  
**Solution**:
```bash
# Check if running
netstat -ano | findstr :5173

# Start if not running
cd frontend
npm run dev
```

### Cause 3: Port Already in Use
**Symptoms**: Server won't start on 5173  
**Solution**:
```bash
# Kill process using port 5173
netstat -ano | findstr :5173
# Note the PID (last column)
taskkill /PID <PID> /F

# Or use different port
set PORT=5174
npm run dev
```

### Cause 4: Missing Dependencies
**Symptoms**: Specific modules not found  
**Solution**:
```bash
cd frontend
npm install
npm run dev
```

### Cause 5: TypeScript Build Errors
**Symptoms**: Components fail to compile  
**Solution**:
```bash
cd frontend
npx tsc --noEmit
# Fix any errors shown
npm run dev
```

---

## 🚀 Best Practice Startup Sequence

### Option 1: Use server.py (Recommended)
```bash
python server.py
```
This automatically:
- Starts backend on port 8000
- Starts frontend on port 5173
- Manages both processes

### Option 2: Manual Startup
```bash
# Terminal 1 - Backend
python server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🧪 Verify It's Working

### Check 1: Frontend Server Running
Open browser to: http://localhost:5173  
You should see the Grace UI (might be loading or showing errors)

### Check 2: Check Browser Console (F12)
Look for:
- ✅ No module loading errors
- ✅ No network errors
- ⚠️ Any red errors indicate issues

### Check 3: Check Network Tab
- Open browser DevTools (F12)
- Go to Network tab
- Refresh page (Ctrl+F5)
- All requests should be green (200 status)

### Check 4: Test API Connection
In browser console (F12):
```javascript
fetch('/api/metrics/summary')
  .then(r => r.json())
  .then(console.log)
```
Should return metrics data, not an error.

---

## 🐛 Still Having Issues?

### 1. Complete Reset
```bash
# Stop all
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Grace*"
taskkill /F /IM node.exe

# Clear everything
cd frontend
rmdir /s /q node_modules\.vite
rmdir /s /q dist

# Reinstall
npm install

# Restart
cd ..
python server.py
```

### 2. Check for Port Conflicts
```bash
# Check what's using ports
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# Kill conflicting processes
taskkill /PID <PID> /F
```

### 3. Clear Browser Cache
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### 4. Check Firewall
- Ensure ports 5173 and 8000 are not blocked
- Temporarily disable firewall to test

---

## 📊 Diagnostic Commands

```bash
# Check if frontend server is running
netstat -ano | findstr :5173

# Check if backend server is running  
netstat -ano | findstr :8000

# Test TypeScript compilation
cd frontend
npx tsc --noEmit

# Test build
npm run build

# Check dependencies
npm list --depth=0
```

---

## ✅ Success Checklist

When everything is working, you should see:

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ No module loading errors in browser console
- ✅ UI loads and renders
- ✅ API calls work (check Network tab)
- ✅ No red errors in browser console

---

## 🎯 Quick Commands

```bash
# Restart everything
python server.py

# Just restart frontend
RESTART_FRONTEND.bat

# Clear cache and restart
cd frontend && rmdir /s /q node_modules\.vite && npm run dev

# Check for errors
cd frontend && npx tsc --noEmit
```

---

## 📞 Common Error Messages

### "Failed to fetch dynamically imported module"
**Fix**: Clear Vite cache
```bash
cd frontend
rmdir /s /q node_modules\.vite
npm run dev
```

### "Cannot GET /src/..."
**Fix**: Vite dev server not running
```bash
cd frontend
npm run dev
```

### "EADDRINUSE: address already in use"
**Fix**: Port 5173 is taken
```bash
netstat -ano | findstr :5173
taskkill /PID <PID> /F
npm run dev
```

---

**Current Status**: TypeScript compiles ✅, Dependencies installed ✅  
**Next Step**: Restart frontend with `RESTART_FRONTEND.bat`
