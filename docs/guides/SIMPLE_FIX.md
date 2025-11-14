# SIMPLE FIX - Make Features Work Right Now

## DO THIS NOW:

### 1. Stop Backend (if running)
```bash
# In terminal running python serve.py, press Ctrl+C
# OR
taskkill /F /IM python.exe
```

### 2. Start Backend
```bash
cd c:\Users\aaron\grace_2
python serve.py
```

### 3. Watch for These Lines:
```
Attempting to load book system routes...
✅ Test router registered: /api/test and /api/books/test
✅ Book dashboard router registered: /api/books/*
✅ File organizer router registered: /api/librarian/*
```

**If you see ERROR instead:** Tell me the exact error message

### 4. Test Routes Work
```bash
# New terminal:
curl http://localhost:8000/api/test

# Should return:
# {"status":"working","message":"If you see this, routes are registered correctly!"}
```

### 5. Test Book Route
```bash
curl http://localhost:8000/api/books/test

# Should return:
# {"total_books":0,"message":"Books route is working"}
```

---

## IF ROUTES WORK (you see JSON responses):

### Then Restart Frontend:
```bash
cd frontend
npm run dev
```

### Then Test UI:
1. Open http://localhost:5173
2. Hard refresh: Ctrl+Shift+R
3. Click "Memory Studio"
4. Should see: Overview, Workspace, Pipelines, Dashboard, Grace, Librarian, **📚 Books**, **🗂️ Organizer**
5. Click "🗂️ Organizer" → Should show panels
6. Bottom-right → Should show purple co-pilot button

---

## IF ROUTES DON'T WORK:

Send me:
1. The exact error from `python serve.py` terminal
2. The response from `curl http://localhost:8000/api/test`
3. Screenshot of what you see in browser

I'll debug from there.

---

**TL;DR:**
```bash
# Stop everything
taskkill /F /IM python.exe

# Start backend
python serve.py

# Watch for ✅ Book dashboard router registered

# Test
curl http://localhost:8000/api/test

# If JSON response → SUCCESS! Now restart frontend
```
