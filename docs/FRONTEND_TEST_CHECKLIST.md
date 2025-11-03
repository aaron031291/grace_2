# Frontend Integration Test Checklist

## 🧪 Pre-Test Setup
- [ ] Backend running: `py -m uvicorn backend.main:app --reload`
- [ ] Frontend running: `cd grace-frontend && npm run dev`
- [ ] Database fresh: `py reset_db.py`
- [ ] Browser: http://localhost:5173

## ✅ Test Sequence

### 1. Login Flow
- [ ] Login page displays
- [ ] Enter: `admin` / `admin123`
- [ ] Click Login button
- [ ] Successfully redirected to chat
- [ ] No console errors

### 2. Chat Interface
- [ ] Chat input visible
- [ ] Type: "Hello Grace"
- [ ] Click Send
- [ ] Message appears on right (You)
- [ ] Grace responds on left
- [ ] Response is: "Hello! I'm Grace..."

### 3. Dashboard View
- [ ] Click "📊 Dashboard" button
- [ ] Page loads without white screen
- [ ] See 3 metric cards (Messages, Users, Reflections)
- [ ] See "System Monitor" section with 4 components
- [ ] See "Background Tasks" section
- [ ] See "Reflections" and "Tasks" lists
- [ ] Click "← Chat" to return

### 4. IDE View
- [ ] Click "💻 IDE" button
- [ ] Three panels visible (Files | Editor | Console)
- [ ] Monaco editor loads (dark theme)
- [ ] Write: `print("Hello from Grace!")`
- [ ] Click "💾 Save"
- [ ] Click "▶ Run"
- [ ] Console shows output
- [ ] No errors in browser console

### 5. Memory Browser
- [ ] Click "📁 Memory" button
- [ ] Three panels visible (Tree | Content | Audit)
- [ ] Tree structure displays
- [ ] Click "← Back" returns to chat

### 6. Hunter Dashboard
- [ ] Click "🛡️ Hunter" button
- [ ] Two panels visible (Alerts | Rules)
- [ ] "No security alerts" message (expected)
- [ ] Rules list shows (may be empty)
- [ ] Click "← Back" returns to chat

## 🔍 Advanced Features

### Knowledge Ingestion (Console test)
```bash
# Get token first (from login)
curl -X POST http://localhost:8000/api/ingest/text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Test","content":"Testing knowledge","domain":"test"}'
```
- [ ] Returns: `{"status":"ingested","artifact_id":1}`

### Trust Score Check
```bash
curl "http://localhost:8000/api/trust/score?url=https://python.org"
```
- [ ] Returns: `{"trust_score":95.0,"auto_approve":true}`

### Health Status
```bash
curl http://localhost:8000/api/health/status
```
- [ ] Returns: `{"system_mode":"normal","checks":[...]}`

## ❌ Known Issues to Check For

### If you see these, they're known:
- **White screen** - Hard refresh (Ctrl+Shift+R)
- **"Not authenticated"** - Logout and login again
- **Empty data** - Normal for fresh database
- **Console warnings** - Browser extension noise (ignore)

### These are actual bugs:
- **Can't send chat** - Token issue
- **Dashboard crashes** - Data format mismatch
- **IDE won't run code** - Sandbox issue
- **Buttons do nothing** - Navigation broken

## 📝 Report Format

For each section, note:
```
✅ WORKS: [Feature name]
❌ BROKEN: [Feature name] - [Error message]
⚠️ PARTIAL: [Feature name] - [What works/doesn't]
```

## 🎯 Success Criteria

**Minimum (Ready for dev use):**
- 4/6 views working (Chat, Dashboard, IDE basics, one other)
- No critical console errors
- Can send chat messages
- Can view metrics

**Good (Ready for testing):**
- 5/6 views working
- All navigation works
- IDE can execute code
- Dashboard shows real data

**Excellent (Ready for demo):**
- 6/6 views working perfectly
- All features functional
- No console errors
- Smooth experience

Take your time testing! Grace's backend is solid - just need to verify the UI matches. 🚀
