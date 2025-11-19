# Frontend Quick Start Guide

## 🚀 Start the System

### Step 1: Start Backend

```bash
python server.py
```

Wait for:
```
[INFO] Server running on http://localhost:8000
```

### Step 2: Start Frontend (New Terminal)

```bash
cd frontend
npm install  # First time only
npm run dev
```

Wait for:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### Step 3: Open in Browser

Open: **http://localhost:5173**

---

## ✅ Verify Integration

### Test Chat

1. Type in chat box: `hi grace`
2. Should see OpenAI response with confidence score
3. Check for citations if RAG context available

### Test Remote Access

1. Click **🔒 Remote Access** in sidebar
2. Button should show **⏳ Loading...**
3. Then change to **🔓 Remote Active**
4. Click again to disconnect

### Test Screen Share

1. Click **📺 Screen Share**
2. Wait for loading
3. Verify it changes to **📺 Sharing Screen**

### Test Document Upload

1. Click **📄 Upload Docs**
2. Select one or more files
3. See success alert with count

---

## 🔧 Common Issues

### Issue: Chat not responding

**Symptoms:**
- Typing "hi grace" shows error
- Response says "OpenAI API key not configured"

**Fix:**
1. Check `.env` file exists in root directory
2. Add: `OPENAI_API_KEY=sk-your-key-here`
3. Restart backend: `python server.py`

### Issue: Remote Access fails

**Symptoms:**
- Error: "Failed to start remote access"
- Button shows error in sidebar

**Fix:**
1. Check backend logs for errors
2. Verify endpoint exists: `curl http://localhost:8000/api/remote-cockpit/remote/start`
3. Backend may need Remote Access feature enabled

### Issue: CORS errors in browser console

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/chat' from origin 
'http://localhost:5173' has been blocked by CORS policy
```

**Fix:**
1. Backend should have CORS enabled (already configured in main.py)
2. Check Vite proxy in `frontend/vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

### Issue: Frontend won't start

**Symptoms:**
```
npm ERR! Missing script: "dev"
```

**Fix:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 What to Expect

### Chat Panel

- **Message Input**: Type and send messages
- **Response Display**: See Grace's reply with metadata
  - Confidence score (0-100%)
  - Citations (if available)
  - Actions (if any)
- **Error Handling**: Friendly messages when backend fails

### Sidebar Controls

- **Remote Access**: Toggle remote session
  - 🔒 Disconnected
  - ⏳ Loading...
  - 🔓 Connected
  
- **Screen Share**: Toggle screen sharing
  - 📺 Not Sharing
  - ⏳ Loading...
  - 📺 Sharing Screen
  
- **Upload Docs**: Upload files to Grace's knowledge base
  - 📄 Ready
  - ⏳ Uploading...
  - ✅ Success alert

### Error Display

Errors appear in sidebar:
```
⚠️ Remote Access: Failed to start remote access
```

---

## 🎯 Next Steps

After verifying basic integration:

1. **Test End-to-End Flow**
   - Upload a document
   - Ask Grace about it in chat
   - Verify RAG retrieval works

2. **Test Multi-Turn Conversation**
   - Send multiple messages
   - Verify session persistence
   - Check conversation history

3. **Test Error Recovery**
   - Stop backend while frontend running
   - Send message → See error
   - Restart backend → Works again

4. **Test All Features**
   - Background tasks drawer
   - History search
   - Remote cockpit
   - Voice input

---

## 🔍 Debugging

### Check Backend Logs

```bash
python server.py
# Watch console output for errors
```

### Check Browser Console

1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for:
   - Network errors (red)
   - API responses (blue)
   - Console logs

### Check Network Tab

1. Open Developer Tools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Click on request to see:
   - Request payload
   - Response data
   - Status code

### Test API Directly

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"hi\"}"

# Should return JSON with "reply" field
```

---

## 📝 Development Workflow

### Making Changes

1. **Backend Changes**
   - Edit Python files
   - Restart server: `Ctrl+C` then `python server.py`
   
2. **Frontend Changes**
   - Edit TypeScript/React files
   - Vite auto-reloads (no restart needed)
   - Check browser for updates

### Adding New Features

1. **Add Backend Endpoint**
   - Create route in `backend/routes/`
   - Test with curl

2. **Add Frontend API Client**
   - Add function to `frontend/src/api/`
   - Use existing `http` client

3. **Add UI Component**
   - Create component in `frontend/src/components/`
   - Import and use in `AppChat.tsx`

4. **Wire Together**
   - Add button/UI element
   - Call API function on click
   - Handle loading/error states

---

## ✅ Success Indicators

You know everything is working when:

- ✅ Backend starts without errors
- ✅ Frontend dev server running
- ✅ Chat responds with OpenAI
- ✅ Confidence scores shown
- ✅ Remote Access toggles work
- ✅ No CORS errors in console
- ✅ Loading states appear correctly
- ✅ Error messages display properly

---

**Ready to go! Open http://localhost:5173 and start chatting with Grace!** 🎉
