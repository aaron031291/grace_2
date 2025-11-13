# 🔄 RESTART & TEST - Make Features Visible

## The Problem

The features exist in code but aren't showing in UI because:
1. ❌ Backend routes not registered (just fixed!)
2. ❌ Frontend not rebuilt with new components
3. ❌ Old cached version still running

## The Solution: RESTART EVERYTHING

### Step 1: Stop All Running Processes
```bash
# Kill Python (backend)
taskkill /F /IM python.exe

# Kill Node (frontend)  
taskkill /F /IM node.exe

# Wait 5 seconds for processes to fully stop
```

### Step 2: Restart Backend (with new routes!)
```bash
cd c:\Users\aaron\grace_2

# Start backend
python serve.py
```

**Watch for this line:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Leave this terminal open!**

### Step 3: Restart Frontend (rebuild with new components)
```bash
# New terminal
cd c:\Users\aaron\grace_2\frontend

# Clear cache and rebuild
npm run dev
```

**Watch for:**
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

**Leave this terminal open!**

### Step 4: Hard Refresh Browser
```
1. Open http://localhost:5173
2. Press: Ctrl + Shift + R (hard refresh)
3. Or: F12 → Network tab → Check "Disable cache" → Refresh
```

---

## ✅ Verify Features Are Now Visible

### Test 1: Check Backend Routes
```bash
# In new terminal:
curl http://localhost:8000/api/books/stats

# Expected: JSON response with stats (or empty if no books)
# NOT: 404 or non-JSON response
```

### Test 2: Check Frontend Components

**Open browser:** http://localhost:5173

**Look for:**
- [ ] Memory Studio link in navigation
- [ ] Click it → Should see tabs including "📚 Books" and "🗂️ Organizer"
- [ ] Bottom-right corner: Purple "Librarian Co-pilot" button
- [ ] Press Ctrl+K: Command palette should open

### Test 3: File Organizer (Undo Feature!)

**Navigate:** Memory Studio → 🗂️ Organizer tab

**Should see:**
- Left panel: "Organization Suggestions" (may be empty)
- Right panel: "Recent Operations" (may be empty initially)
- Footer: "Scan for Unorganized Files" button

**To create an operation:**
```bash
# Create a test file
echo "test content" > grace_training\test_file.txt

# In UI:
1. Organizer tab → Click "Scan for Unorganized Files"
2. Wait 2-3 seconds
3. Left panel should show suggestion for test_file.txt
4. Click "Apply"
5. Right panel should show operation with YELLOW "UNDO" button
```

### Test 4: Books Tab

**Navigate:** Memory Studio → 📚 Books tab

**Should see:**
- Stats bar with 6 metrics (all zeros if no books yet)
- 4 sub-tabs: Library, Progress, Flashcards, Verify
- Instructions to drop books

### Test 5: Co-pilot

**Find:** Bottom-right corner

**Should see:**
- Purple button labeled "Librarian Co-pilot"
- Click it → Chat interface expands
- Quick action buttons visible
- Can type questions

---

## 🐛 If Features Still Not Visible

### Check 1: Backend Routes Registered?
```bash
curl http://localhost:8000/docs

# Scroll to find:
# - /api/books/stats
# - /api/books/recent
# - /api/librarian/file-operations
# - /api/librarian/organization-suggestions

# If missing: Routes not registered
```

**Fix:**
```bash
# Make sure these lines are in backend/main.py:
from backend.routes import book_dashboard, file_organizer_api
app.include_router(book_dashboard.router, prefix="/api/books")
app.include_router(file_organizer_api.router, prefix="/api/librarian")

# Restart: taskkill /F /IM python.exe
# Then: python serve.py
```

### Check 2: Frontend Components Imported?
```
F12 → Console → Look for errors like:
- "Failed to fetch"
- "Component not found"
- "Module not found"
```

**Fix:**
```bash
cd frontend
npm install  # Reinstall dependencies
npm run dev  # Rebuild
```

### Check 3: CORS Issues?
```
F12 → Console → Look for:
"Access to fetch blocked by CORS policy"
```

**Fix:** In backend/main.py, ensure CORS is configured:
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

---

## 📝 Quick Restart Checklist

Before claiming nothing works:

- [ ] Killed all Python processes
- [ ] Killed all Node processes
- [ ] Restarted backend: `python serve.py`
- [ ] Restarted frontend: `npm run dev`
- [ ] Hard refreshed browser: Ctrl+Shift+R
- [ ] Checked browser console for errors (F12)
- [ ] Checked backend terminal for errors
- [ ] Tested API directly: `curl http://localhost:8000/api/books/stats`

---

## 🎯 What Should Work After Restart

### In Browser (http://localhost:5173):

**Top Navigation:**
- Should see "Memory Studio" link

**After clicking Memory Studio:**
- Should see tabs: Overview, Workspace, Pipelines, Dashboard, Grace, Librarian, **📚 Books**, **🗂️ Organizer**

**In Organizer Tab:**
- Two panels side by side
- Right panel: "Recent Operations"
- Yellow "Undo" button (after file operations)

**Bottom-Right:**
- Purple "Librarian Co-pilot" button

**Top-Right:**
- Notification toasts (after events)

**Anywhere:**
- Press Ctrl+K → Command palette opens

---

## 🔥 NUCLEAR OPTION (If Nothing Works)

```bash
# 1. Kill everything
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# 2. Clean frontend
cd frontend
rmdir /S /Q dist
rmdir /S /Q node_modules\.vite
npm install

# 3. Clean backend cache
cd ..
rmdir /S /Q backend\__pycache__
del /S /Q backend\*.pyc

# 4. Restart from scratch
python serve.py                    # Terminal 1
cd frontend && npm run dev         # Terminal 2

# 5. Browser
# Close all tabs
# Open new: http://localhost:5173
# Hard refresh: Ctrl+Shift+R
```

---

## ✅ SUCCESS CRITERIA

**You'll know it's working when:**
1. Memory Studio loads
2. You see "📚 Books" and "🗂️ Organizer" tabs
3. Purple co-pilot button visible bottom-right
4. Clicking Organizer tab shows two panels
5. Creating a file operation shows "Undo" button

**Screenshot this and confirm!**

---

## 🆘 If STILL Not Working

Share:
1. Backend terminal output (last 20 lines)
2. Frontend terminal output (any errors?)
3. Browser console (F12 → Console tab → screenshot)
4. What you see when you click Memory Studio

I'll debug from there.

---

**NOW: Kill all processes and restart!** 🔄

```bash
taskkill /F /IM python.exe && taskkill /F /IM node.exe
# Wait 5 seconds
python serve.py                    # Terminal 1
cd frontend && npm run dev         # Terminal 2  
# Open browser, hard refresh
```
