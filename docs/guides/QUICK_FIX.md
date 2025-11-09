# ⚡ QUICK FIX - Missing Dependencies

## 🔧 The Error You're Seeing:

```
ModuleNotFoundError: No module named 'aiohttp'
```

## ✅ The Fix:

### Stop the current process (press Ctrl+C), then run:

```
.\INSTALL_DEPENDENCIES.ps1
```

This will install all required Python packages (takes 2-5 minutes).

### Then start backend again:

```
.\START_BACKEND_SIMPLE.ps1
```

---

## 📝 Or Manual Install:

```
.venv\Scripts\pip install -r backend\requirements.txt
```

Then:

```
.\START_BACKEND_SIMPLE.ps1
```

---

## 🎯 What Should Happen:

After installing dependencies, you'll see:
- ✓ Dependencies installed
- INFO: Uvicorn running on http://0.0.0.0:8000
- INFO: Application startup complete

Then backend is ready! 🎉
