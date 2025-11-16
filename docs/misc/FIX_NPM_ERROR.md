# Fix: NPM Error - Wrong Directory

## The Problem

You ran:
```bash
cd C:\Users\aaron\grace_2
npm run dev  ❌ WRONG!
```

**Error:** `package.json` not found because you're in the **root directory**.

## The Solution

You need to be in the **frontend** directory:

```bash
cd C:\Users\aaron\grace_2\frontend
npm run dev  ✅ CORRECT!
```

---

## Quick Fix

**From where you are now:**
```bash
cd frontend
npm run dev
```

**OR start fresh:**
```bash
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

---

## Correct Directory Structure

```
C:\Users\aaron\grace_2\          ← Root (backend code here)
├── backend\
├── frontend\                    ← FRONTEND IS HERE!
│   ├── package.json            ← This is what npm needs!
│   ├── src\
│   ├── node_modules\
│   └── vite.config.ts
├── databases\
└── grace_training\
```

**For backend:** Run from root (`C:\Users\aaron\grace_2`)
**For frontend:** Run from frontend (`C:\Users\aaron\grace_2\frontend`)

---

## Correct Commands

### Terminal 1 (Backend):
```bash
cd C:\Users\aaron\grace_2
python serve.py
```

### Terminal 2 (Frontend):
```bash
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

---

## Now Try This

```bash
cd frontend
npm run dev
```

Should see:
```
VITE vX.X.X ready in XXXms
➜  Local:   http://localhost:5173/
```

Then open: http://localhost:5173

**That's the fix!** 🚀
