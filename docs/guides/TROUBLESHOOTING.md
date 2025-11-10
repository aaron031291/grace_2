# 🔧 Grace Black Screen Troubleshooting

## Issue: Black Screen on http://localhost:5173

### Quick Diagnosis

**Open this test page first:**
http://localhost:5173/test.html

This will show if:
- ✅ Frontend server is working
- ✅ Backend API is responding
- ⚠️ React app has an error

---

## Most Likely Cause: JavaScript Error

### Step 1: Open Browser DevTools
1. Go to **http://localhost:5173**
2. Press **F12** (or right-click → Inspect)
3. Click the **Console** tab
4. Look for RED error messages

### Step 2: Common Errors & Fixes

#### Error: "Unexpected token" or "Syntax error"
**Cause:** HunterDashboard.tsx still has syntax issues
**Check:** Look at the "Grace Frontend" terminal window for build errors

#### Error: "Failed to fetch" or "Network error"
**Cause:** Backend not accessible
**Fix:** Check backend is running at http://localhost:8000/health

#### Error: "Cannot read property of undefined"
**Cause:** Missing or incorrect prop
**Fix:** Check browser console for specific component name

#### Error: Module not found
**Cause:** Missing dependency or import error
**Fix:** Check the specific module mentioned

---

## Step 3: Check Terminal Windows

### Frontend Terminal (Grace Frontend)
Should show:
```
VITE v7.x.x ready in XXXms
➜  Local:   http://localhost:5173/
```

**If you see errors:**
- Copy the error message
- Tell me what it says

### Backend Terminal (Grace Backend)
Should show:
```
✓ Database initialized
✓ Grace API server starting
```

**If you see errors:**
- Copy the error message  
- Tell me what it says

---

## Step 4: Nuclear Option - Fresh Start

If nothing else works:

```bash
# Kill everything
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Wait 5 seconds

# Start backend
cd C:\Users\aaron\grace_2
.venv\Scripts\activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# In NEW terminal, start frontend
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

---

## What to Check Now:

1. **Open http://localhost:5173/test.html**
   - Does this page work?
   - Does it show backend is OK?

2. **Open browser DevTools (F12) on http://localhost:5173**
   - What error appears in the Console tab?

3. **Check both terminal windows**
   - Any red error messages?

---

## Tell Me:

1. **What do you see at http://localhost:5173/test.html?**
2. **When you press F12 on http://localhost:5173, what errors are in the Console?**
3. **Do the terminal windows show any errors?**

This will help me fix the exact issue! 🔍
