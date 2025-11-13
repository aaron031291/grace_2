# Memory Panel Setup & Verification Guide

## ✅ What's Been Created

### Frontend Components
- ✅ `frontend/src/api/memory.ts` - API client for memory endpoints
- ✅ `frontend/src/components/memory/FileTree.tsx` - File explorer tree
- ✅ `frontend/src/components/memory/SchemaReviewModal.tsx` - Schema approval modal
- ✅ `frontend/src/components/memory/MemoryPanel.tsx` - Main memory panel
- ✅ `frontend/src/components/memory/MemoryPanel.css` - Styling

### Backend API
- ✅ `backend/routes/memory_files_api.py` - File operations router
- ✅ Router registered in `unified_grace_orchestrator.py`

### Test Scripts
- ✅ `test_memory_api.py` - Comprehensive API tests
- ✅ `test_memory_panel.py` - Quick verification script

### Training Data
- ✅ 55+ comprehensive training files in `grace_training/`
- ✅ Internal operational structure with 20 subdirectories

---

## 🚀 Quick Start

### 1. Start the Backend
```bash
python serve.py
```

You should see:
```
✅ Memory Files API router included
```

### 2. Verify Backend API
```bash
python test_memory_panel.py
```

All tests should pass (7/7).

### 3. Start the Frontend
```bash
cd frontend
npm run dev
```

### 4. Access Memory Panel
1. Open http://localhost:5173
2. Login (admin/admin123)
3. Click "📁 Memory" button in nav
4. You should see the Memory Panel with file tree

---

## 🔍 Verification Checklist

### Backend Verification

**Test 1: Check if routes are registered**
```bash
curl http://localhost:8000/api/memory/files/list?path=/
```
Expected: JSON array of folders

**Test 2: Create a test file**
```bash
curl -X POST http://localhost:8000/api/memory/files/create \
  -H "Content-Type: application/json" \
  -d "{\"path\": \"test.txt\", \"content\": \"hello\"}"
```
Expected: `{"success": true, ...}`

**Test 3: Get file content**
```bash
curl "http://localhost:8000/api/memory/files/content?path=test.txt"
```
Expected: JSON with content

**Test 4: List tables**
```bash
curl http://localhost:8000/api/memory/tables/list
```
Expected: Array of table names

### Frontend Verification

**Check 1: Component Renders**
- Navigate to Memory tab
- Should see file tree on left
- Should see "Select a file..." message on right

**Check 2: File Tree Works**
- Click on `grace_training` folder
- Should expand and show subfolders
- Click on a `.md` file
- Should show content in editor

**Check 3: File Operations**
- Click "📄" button to create new file
- Enter name, should create file
- Click "📁" button to create folder
- Enter name, should create folder
- Right-click on file → Delete
- Should remove file from tree

**Check 4: Edit and Save**
- Select a file
- Modify content in editor
- "● Unsaved changes" should appear
- Click "💾 Save"
- Should show success toast

**Check 5: Schema Review (if available)**
- Click "📋 Schema Reviews" button
- If pending schemas exist, modal should open
- Can approve/reject schemas

**Check 6: Upload File**
- Click "📤 Upload" button
- Select a file
- Should upload and appear in tree

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution**: Run TypeScript build to verify imports
```bash
cd frontend
npm run build
```

Fix any import errors (use `type` keyword for type imports).

### Issue: Backend returns 404 for /api/memory/files/list

**Check 1**: Verify router is registered
```bash
# Look for "Memory Files API router included" in backend logs
```

**Check 2**: Restart backend
```bash
# Stop (Ctrl+C) and restart
python serve.py
```

**Check 3**: Check if routes file exists
```bash
ls backend/routes/memory_files_api.py
```

### Issue: File tree doesn't show any files

**Solution 1**: Check watch folders exist
```bash
ls grace_training  # Should exist with files
ls storage        # Should exist
```

**Solution 2**: Check backend logs for errors

**Solution 3**: Open browser DevTools Console and check for errors

### Issue: Clicking file doesn't load content

**Check 1**: Open browser Network tab
- Should see request to `/api/memory/files/content?path=...`
- Should return 200 with JSON

**Check 2**: Check browser console for errors

**Check 3**: Verify file path is correct (Windows paths vs Unix)

### Issue: Save button doesn't work

**Check 1**: Ensure you've modified the content (dirty flag)

**Check 2**: Check Network tab for PUT request

**Check 3**: Check for CORS errors in console

### Issue: Schema Review modal is empty

This is normal if no schemas are pending. To test:
1. Upload a CSV file
2. Wait for auto-ingestion to process it
3. Should create a schema proposal
4. Check modal again

---

## 🔧 Configuration

### Backend - Watch Folders
Edit `backend/routes/memory_files_api.py`:

```python
WATCH_FOLDERS = [
    Path("grace_training"),
    Path("storage"),
    Path("docs"),
    Path("exports"),
    # Add your folders here
]
```

### Frontend - API Base URL
Edit `frontend/src/api/memory.ts`:

```typescript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

For production, set `VITE_API_URL` environment variable.

---

## 📊 Expected Behavior

### On First Load
1. Memory Panel renders
2. File tree shows watch folders (grace_training, storage, docs, exports)
3. Right panel shows "Select a file..."
4. Schema Review button shows (0) pending

### After Selecting a File
1. File content loads in editor
2. If file has linked table rows, they appear below editor
3. File path shown in header
4. Save button available

### After Editing
1. "● Unsaved changes" appears
2. Save button becomes active
3. Click save → Success toast appears
4. Dirty indicator disappears

### After Upload
1. File appears in tree
2. Auto-ingestion processes it (if supported format)
3. May create schema proposal
4. Schema Review counter updates

---

## 🎯 Next Steps

1. **Test the setup**:
   ```bash
   python test_memory_panel.py
   ```

2. **Start services**:
   ```bash
   # Terminal 1: Backend
   python serve.py
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

3. **Access app**: http://localhost:5173

4. **Verify functionality**: Follow checklist above

5. **Check for errors**: Browser DevTools → Console and Network tabs

---

## 📝 Notes

- The Memory Panel integrates with your existing memory tables system
- File changes trigger auto-ingestion if configured
- Schema proposals require the schema inference agent to be running
- Linked table rows only appear for files that have been ingested

## 🆘 Need Help?

If issues persist:
1. Check backend logs for errors
2. Check browser console for React errors
3. Verify all endpoints return 200 with `test_memory_panel.py`
4. Ensure database is running and tables are created
