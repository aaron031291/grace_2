# 🔧 FIX: Script Not Found

## ⚠️ Error: ".\RUN_GRACE.ps1 is not recognized"

This means you're not in the right directory!

---

## ✅ SOLUTION - Copy These Commands:

### Step 1: Check Where You Are
```
pwd
```

### Step 2: Navigate to Grace Directory
```
cd C:\Users\aaron\grace_2
```

### Step 3: Verify Files Exist
```
dir *.ps1
```

You should see: `RUN_GRACE.ps1`, `START_BACKEND_SIMPLE.ps1`, etc.

### Step 4: Now Run It
```
.\RUN_GRACE.ps1
```

---

## 📝 Or Just Copy This Whole Block:

```powershell
cd C:\Users\aaron\grace_2
dir *.ps1
.\RUN_GRACE.ps1
```

---

## 🔍 Alternative: Use Full Path

```powershell
C:\Users\aaron\grace_2\RUN_GRACE.ps1
```

---

## ⚡ ONE-LINER (Just Copy This):

```powershell
Set-Location C:\Users\aaron\grace_2; if (Test-Path .\RUN_GRACE.ps1) { .\RUN_GRACE.ps1 } else { Write-Host "ERROR: RUN_GRACE.ps1 not found in current directory!" -ForegroundColor Red; Write-Host "Current location: $(Get-Location)" -ForegroundColor Yellow }
```

This will:
1. Go to the right directory
2. Check if file exists
3. Run it OR show you where you are

---

## 🎯 SIMPLEST FIX:

Just copy & paste this:

```
cd C:\Users\aaron\grace_2
```

Then:

```
.\RUN_GRACE.ps1
```

**That's it!** 🚀
