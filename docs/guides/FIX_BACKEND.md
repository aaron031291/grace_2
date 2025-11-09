# 🔧 FIX BACKEND NOT WORKING

## ⚠️ Common Issue: Don't Copy the ```powershell``` Part!

**WRONG (includes code block markers):**
```
```powershell
cd C:\Users\aaron\grace_2
.\RUN_GRACE.ps1
```
```

**RIGHT (just the commands):**
```
cd C:\Users\aaron\grace_2
.\RUN_GRACE.ps1
```

---

## ✅ STEP-BY-STEP FIX

### Step 1: Navigate to Directory
Copy and paste THIS (one line at a time):

```
cd C:\Users\aaron\grace_2
```

Press Enter.

### Step 2: Check You're in Right Place
```
dir
```

You should see files like: `RUN_GRACE.ps1`, `backend/`, `frontend/`

### Step 3: Run Grace
```
.\RUN_GRACE.ps1
```

---

## 🚨 If That Doesn't Work:

### Fix 1: Enable PowerShell Scripts
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try again:
```
.\RUN_GRACE.ps1
```

### Fix 2: Check Python Exists
```
python --version
```

Should show Python 3.10 or higher.

### Fix 3: Check Virtual Environment
```
Test-Path .venv
```

Should return `True`. If not:
```
python -m venv .venv
```

### Fix 4: Install Dependencies
```
.venv\Scripts\pip install -r backend\requirements.txt
```

### Fix 5: Check .env File
```
Test-Path .env
```

If False:
```
Copy-Item .env.example .env
notepad .env
```

Add your API keys.

---

## 🎯 Manual Start (If Script Fails)

### Step 1: Activate Virtual Environment
```
.venv\Scripts\Activate.ps1
```

### Step 2: Start Backend Manually
```
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Test It Works
Open new PowerShell window:
```
curl http://localhost:8000/health
```

---

## 🔍 Diagnostic Commands

Run these to find the issue:

```
# Check current directory
pwd

# Check Python
python --version

# Check virtual environment exists
Test-Path .venv\Scripts\python.exe

# Check backend folder exists
Test-Path backend\main.py

# Check requirements file
Test-Path backend\requirements.txt

# List installed packages
.venv\Scripts\pip list
```

---

## ⚡ Quick Fix Command

Copy ALL of this at once:

```
cd C:\Users\aaron\grace_2
if (-not (Test-Path .venv)) { python -m venv .venv }
.venv\Scripts\pip install -r backend\requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\RUN_GRACE.ps1
```

---

## 📝 What Error Did You Get?

### Error: "cannot be loaded because running scripts is disabled"
**Fix:**
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "python: command not found"
**Fix:** Install Python from python.org, then restart PowerShell

### Error: "ModuleNotFoundError"
**Fix:**
```
.venv\Scripts\pip install -r backend\requirements.txt
```

### Error: "Port 8000 already in use"
**Fix:**
```
# Find what's using it
netstat -ano | findstr :8000

# Or use different port
.\BOOT_GRACE_COMPLETE_E2E.ps1 -BackendPort 9000
```

### Error: ".env file not found"
**Fix:**
```
Copy-Item .env.example .env
notepad .env
```

---

## 🆘 Still Not Working?

Share the EXACT error message you see, and I'll help!

Run this and share the output:
```
cd C:\Users\aaron\grace_2
python --version
Test-Path .venv
Test-Path backend\main.py
Get-Content logs\backend.log -Tail 20
```
