# Meta-Loop UI - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Start Backend & Frontend
```bash
# Terminal 1
cd grace_rebuild
start_backend.bat

# Terminal 2
cd grace_rebuild/grace-frontend
npm run dev
```

### 2. Access UI
- Open: http://localhost:5173
- Login: `admin` / `admin123`
- Click: **🧠 Meta-Loop** button

### 3. Create Test Data
```bash
curl -X POST http://localhost:8000/api/meta/test/create-samples
```

### 4. Test Complete Workflow

#### View Pending (3 recommendations should appear)
- ✅ See risk levels: LOW, MEDIUM, HIGH
- ✅ Check predicted impacts
- ✅ Read reasoning

#### Approve One
- ✅ Click "Approve & Apply" on LOW risk item
- ✅ Watch it move to Applied tab
- ✅ Counter decreases

#### View Applied
- ✅ Switch to "Applied" tab
- ✅ See the approved change
- ✅ View before/after values

#### Check Performance
- ✅ Switch to "Performance" tab
- ✅ View metrics (once data available)

## 📂 File Locations

**Frontend:**
- `grace-frontend/src/components/MetaLoopDashboard.tsx`
- `grace-frontend/src/components/RecommendationCard.tsx`

**Backend:**
- `backend/routes/meta_api.py`
- `backend/meta_loop_approval.py`

## 🔗 Key API Endpoints

```
GET  /api/meta/recommendations/pending   - List pending
GET  /api/meta/recommendations/applied   - List applied
POST /api/meta/recommendations/{id}/approve
POST /api/meta/recommendations/{id}/reject
POST /api/meta/changes/{id}/rollback
GET  /api/meta/performance               - Analytics
POST /api/meta/test/create-samples       - Generate test data
```

## 📊 UI Tabs

**⏳ Pending** - Recommendations awaiting approval
- Shows: type, current→proposed, risk, impact, reasoning
- Actions: Approve, Reject

**✅ Applied** - History of approved changes
- Shows: before/after metrics, improvement %, rollback option
- Actions: Rollback (if degraded)

**📈 Performance** - Analytics & trends
- Shows: acceptance rate, avg improvement, effectiveness charts
- Actions: None (read-only)

## 🎨 Risk Colors

- 🟢 **LOW** - Safe to approve
- 🟡 **MEDIUM** - Review carefully
- 🔴 **HIGH** - Requires caution

## ✅ Success Indicators

All working if you see:
1. ✅ 3 pending recommendations
2. ✅ Risk badges colored correctly
3. ✅ Approve button works
4. ✅ Item moves to Applied tab
5. ✅ Counters update automatically

## 📖 Full Documentation

- **User Guide:** `META_LOOP_UI_GUIDE.md`
- **UI Mockups:** `META_LOOP_UI_MOCKUP.md`
- **Implementation:** `META_LOOP_UI_COMPLETE.md`

## 🆘 Troubleshooting

**No recommendations?**
→ Run: `curl -X POST http://localhost:8000/api/meta/test/create-samples`

**Approve doesn't work?**
→ Check browser console, verify backend running

**Charts empty?**
→ Normal - need applied changes with metrics first

**WebSocket errors?**
→ Ignore - UI falls back to polling automatically

---

**Status:** ✅ Fully Implemented & Working
**Framework:** React + TypeScript + FastAPI
**Ready:** For production use
