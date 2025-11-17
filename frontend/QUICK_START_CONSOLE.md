# Grace Console - Quick Start Guide

## 🚀 Start the Console (2 Steps)

### Step 1: Ensure Backend is Running

Your backend appears to be running based on the logs. If not:

```bash
cd c:\Users\aaron\grace_2
python serve.py
```

Backend should show:
```
Uvicorn running on http://0.0.0.0:8017
```

### Step 2: Start Frontend

```bash
cd c:\Users\aaron\grace_2\frontend
npm run dev
```

Or double-click: `START_CONSOLE.bat`

**Frontend URL:** http://localhost:5173

## 🎯 Features Available

### 1. **💬 Chat**
- Conversation with Grace
- File attachments
- Citation pills (clickable)
- 3 modes: Chat | World Model | RAG
- Model selection (qwen2.5, deepseek, etc.)

### 2. **📊 Workspace**
- Dynamic tabs for missions, dashboards, artifacts
- Open/close/switch tabs
- Type-based rendering
- 8 workspace types available

### 3. **🧠 Memory Explorer**
- Browse knowledge artifacts
- 9 categories with filtering
- Upload: File (drag-drop), Text, Voice
- Re-ingest, download, delete actions
- Content preview
- Linked missions

### 4. **⚖️ Governance**
- Pending approval requests
- Approve/Reject with reasons
- "Discuss with Grace" for context
- Approval history
- Audit log viewer

### 5. **🔧 MCP Tools**
- Browse MCP resources
- View resource content
- Invoke MCP tools
- Execute with JSON parameters

### 6. **🎯 Tasks (Sidebar)**
- Mission control Kanban
- Status columns (Open, In Progress, etc.)
- Execute missions
- View details

### 7. **📋 Logs (Bottom)**
- Real-time system logs
- Filter by level/domain
- Search messages
- Auto-refresh 3s

## 🧪 Quick Tests

### Test 1: Chat with Citation
```
1. Click "💬 Chat"
2. Type: "Show me mission ABC-123"
3. Grace responds with [mission:abc] citation
4. Click citation pill
5. ✓ Workspace tab opens with mission detail
```

### Test 2: Upload Knowledge
```
1. Click "🧠 Memory"
2. Click "+ Add Knowledge"
3. Select "📝 Text" tab
4. Paste some text, add title
5. Click "Ingest Text"
6. ✓ Progress bar shows status
7. ✓ New artifact appears in list
```

### Test 3: Approve Request
```
1. Click "⚖️ Governance"
2. See pending approvals (if any)
3. Click an approval
4. Click "🤔 Discuss with Grace"
5. ✓ Grace provides context
6. Click "✅ Approve"
7. Enter reason
8. ✓ Logged to audit
```

### Test 4: MCP Tools
```
1. Click "🔧 MCP"
2. Click a resource (grace://self)
3. ✓ Content displays
4. Click a tool
5. Enter parameters: {"question": "test"}
6. Click "Execute Tool"
7. ✓ Result displays
```

### Test 5: World Model Query
```
1. Click "💬 Chat"
2. Click "🧠 World Model" mode
3. Type: /ask How is the CRM health?
4. ✓ Grace queries world model
5. ✓ Response with citations
```

## 🔧 Configuration

### Environment Variables

Create `frontend/.env`:
```bash
VITE_API_BASE=http://localhost:8017
```

Or use default (http://localhost:8017)

### Auth Token

Set in localStorage (auto-set to dev-token):
```javascript
localStorage.setItem('token', 'dev-token');
localStorage.setItem('user_id', 'aaron');
```

## 📊 Panel Navigation

Click buttons in header to switch panels:
- **💬 Chat** - Main chat interface
- **📊 Workspace** - Dynamic workspace tabs
- **🧠 Memory** - Knowledge management
- **⚖️ Governance** - Approvals & audit
- **🔧 MCP** - MCP tools & resources
- **🎯 Tasks** - Mission control
- **📋 Logs** - System logs

## 🎨 Features Showcase

### Dynamic Workspaces
- Click any mission → Opens in workspace tab
- Click citation → Opens relevant workspace
- Multiple tabs open simultaneously
- Click × to close tabs

### Multi-Modal Upload
- File: Drag & drop or click to browse
- Text: Paste directly with title
- Voice: Record audio with transcription

### Smart Filtering
- Memory: Category, status, tags, search
- Tasks: Severity, subsystem, status
- Logs: Level, domain, search

### Real-Time Updates
- Logs refresh every 3 seconds
- Tasks refresh every 30 seconds
- Governance refresh every 10 seconds

## 🐛 Troubleshooting

### Frontend won't start
```bash
cd frontend
npm install
npm run dev
```

### Can't connect to API
Check backend port in logs:
```
Uvicorn running on http://0.0.0.0:8017
```

Update `frontend/src/services/*.ts`:
```typescript
const API_BASE = 'http://localhost:8017'; // or 8000
```

### CORS errors
Backend already has CORS enabled (`allow_origins=["*"]`)

### 401 Unauthorized
```javascript
localStorage.setItem('token', 'dev-token');
```

## 📚 Documentation

All guides in `frontend/`:
- `GRACE_CONSOLE_COMPLETE.md` - Complete overview
- `INTEGRATION_GUIDE.md` - How to add panels
- `DATA_HOOKS_GUIDE.md` - Hook architecture
- `TASK_MANAGER_GUIDE.md` - Task manager details
- `CHAT_INTEGRATION_GUIDE.md` - Chat features
- `WORKSPACE_SYSTEM_GUIDE.md` - Workspace system
- `COMPLETE_MEMORY_EXPLORER.md` - Memory explorer
- `VERIFICATION_CHECKLIST.md` - API verification
- `FINAL_IMPLEMENTATION_SUMMARY.md` - Feature summary
- `QUICK_START_CONSOLE.md` - This file

## 🎉 Conclusion

**The Grace Console is 100% complete and ready to use!**

All 7 panels implemented:
✅ Chat (with world model & model selection)  
✅ Workspace (dynamic tabs)  
✅ Memory (3-panel explorer)  
✅ Governance (approvals & audit)  
✅ MCP Tools (protocol interface)  
✅ Tasks (Kanban board)  
✅ Logs (real-time viewer)  

Start the frontend and explore! 🚀
