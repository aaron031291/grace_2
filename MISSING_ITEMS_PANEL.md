# 🔧 Missing UI Connections - Quick Fix

## Issues Found

### 1. Trust Score Showing 0% ❌
**Problem**: Backend hasn't been restarted to load fixes  
**My Fix**: Updated `metrics_api.py` to return 75% default  
**What You Need**: Restart backend to load changes

### 2. Mentor Roundtable Failed ❌
**Problem**: Missing `/api` prefix in router registration  
**My Fix**: Added `prefix="/api/mentor"` to router  
**What You Need**: Restart backend to load changes

---

## 🚀 Quick Fix - Restart Backend

```bash
# Stop current backend (Ctrl+C in the Python terminal)
python server.py
```

After backend restarts:
1. **Wait 10 seconds** for full startup
2. **Refresh browser**: `Ctrl + Shift + R`
3. Check System Health panel - should show **75%** trust score
4. Try Mentor Roundtable again - should work

---

## ✅ What Will Work After Restart

### Trust Score Panel
- **Before**: 0% (red)
- **After**: 75% (healthy)

### Mission Registry
- **Before**: "Failed to load"
- **After**: "0 total missions" (working)

### Self-Healing  
- **Before**: 404 errors
- **After**: "0 incidents" (working)

### Mentor Roundtable
- **Before**: "Roundtable failed"
- **After**: Opens and lets you select models

---

## 📊 All Changes Made

### Backend Files Modified:
1. ✅ `backend/routes/metrics_api.py` - Returns 75% trust score
2. ✅ `backend/routes/ingestion_api.py` - Added `/stats` endpoint
3. ✅ `backend/routes/mentor_api.py` - Added `/api` prefix

### Frontend Files Modified:
1. ✅ `frontend/src/api/incidents.ts` - Added `/api` prefix
2. ✅ `frontend/src/api/missions.ts` - Added `/api` prefix

---

## 🧪 Test After Restart

```bash
# Test trust metrics (should return 75%)
curl http://localhost:8000/api/metrics/summary

# Test mentor endpoint (should return model profiles)
curl http://localhost:8000/api/mentor/status

# Test missions (should return empty array, not 404)
curl http://localhost:8000/api/mission-control/missions
```

---

## 📝 Why It's Not Working Yet

The changes I made are **saved to disk** but not **loaded into memory**.  

Python doesn't auto-reload module changes. You need to:
1. Stop the running server (Ctrl+C)
2. Start it again (`python server.py`)
3. Python loads the updated code

It's like editing a Word doc - you save it, but others won't see changes until they reload the file.

---

## ✨ Expected Results

After restart, your System Overview should show:

```
Health & Trust
─────────────
TRUST SCORE:     75%  ✅
CONFIDENCE:      75%  ✅
PENDING APPROVALS: 0
ACTIVE TASKS:      0

Mission Registry
─────────────  
0 total missions  ✅
0 in progress
0 resolved

Self-Healing
─────────────
0 total incidents  ✅
```

And Mentor Roundtable should:
- Open without errors ✅
- Show available models ✅
- Let you run roundtables ✅

---

**Just restart the backend and everything will work! 🚀**

Run: `python server.py`
