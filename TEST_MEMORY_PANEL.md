# Memory Panel - Quick Test Guide

## ✅ Step-by-Step Testing

### 1. Start/Restart Frontend
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 2. Open Browser
Navigate to: http://localhost:5173

### 3. Login (if needed)
- Username: `admin`
- Password: `admin123`

### 4. Click Memory Button
Look for "📁 Memory" in the top navigation and click it.

### 5. Verify Layout
You should see:
- **Left panel:** File tree with buttons at bottom
- **Right panel:** Empty editor or selected file content
- **Header:** "Memory Workspace" with file count

### 6. Test Create File
1. Click "+ File" button (purple)
2. Enter filename: `hello.md`
3. Type in editor: `# Hello World`
4. Notice "● Modified" indicator appears
5. Click "Save" button (green)
6. Verify indicator disappears

### 7. Test Create Folder
1. Click "+ Folder" button (gray)
2. Enter folder name: `notes`
3. Verify folder appears in tree with 📁 icon

### 8. Test Upload
1. Click "↑ Upload" button (blue)
2. Select any text file from your computer
3. Verify file appears in tree

### 9. Test Edit
1. Click on a file in the tree
2. Monaco editor loads the content
3. Make changes
4. See "● Modified" indicator
5. Click "Save"

### 10. Test Delete
1. Select a file
2. Click "🗑️ Delete" button (red)
3. Confirm in dialog
4. Verify file is removed from tree

---

## ✅ Expected Behavior

### When You First Load
- File tree shows empty `grace_training` folder
- Or shows existing files if any
- Status shows: "0 files • 0.00 MB" (or current count)

### When You Create a File
- Prompt appears asking for filename
- File appears in tree immediately
- Editor switches to new file (empty)
- Can type and save

### When You Edit a File
- Monaco editor loads with syntax highlighting
- File info shows in header (name, modified date)
- "● Modified" appears when you type
- Save button turns green when dirty

### When You Save
- "Saving..." appears briefly
- File is persisted to backend
- "● Modified" indicator disappears
- Tree refreshes

### When You Delete
- Confirmation dialog appears
- File/folder is removed
- Tree refreshes
- Editor clears if deleted file was selected

---

## 🔍 Visual Checklist

Look for these elements:

**Left Panel:**
- [ ] "Memory Workspace" header in purple
- [ ] File count and size display
- [ ] File tree with icons (📁 folders, 📄 files)
- [ ] Four buttons at bottom (File, Folder, Upload, Refresh)

**Right Panel (when file selected):**
- [ ] File name in header
- [ ] Modified date
- [ ] "● Modified" indicator (when editing)
- [ ] Monaco editor with dark theme
- [ ] Save button (green when dirty)
- [ ] Delete button (red)

**Right Panel (when nothing selected):**
- [ ] Large folder icon 📁
- [ ] "Select a file to edit" message

---

## 🐛 Common Issues

### Issue: Memory button does nothing
**Fix:** Check browser console for errors. Hard refresh (Ctrl+Shift+R).

### Issue: File tree shows "Loading..."
**Fix:** 
- Check backend is running on port 8000
- Test: http://localhost:8000/api/memory/files
- Should return JSON (may require auth)

### Issue: Can't save files
**Fix:**
- Check `grace_training/` folder exists in backend root
- Check write permissions
- Check authentication token is valid

### Issue: Monaco editor is blank
**Fix:**
- Check `@monaco-editor/react` is installed
- Run: `npm install` in frontend folder
- Restart dev server

### Issue: Buttons don't work
**Fix:**
- Check browser console for JavaScript errors
- Verify all API endpoints are returning 200/422 (not 404)
- Run: `python check_api_routes.py` to verify backend

---

## 📊 Success Indicators

### You know it's working when:

1. ✅ Memory panel loads without errors
2. ✅ File tree displays (even if empty)
3. ✅ Can create a test file
4. ✅ Monaco editor shows with syntax highlighting
5. ✅ Can save the file
6. ✅ Can refresh and see the file persists
7. ✅ Status shows updated file count
8. ✅ Can delete the test file

---

## 🎥 Test Script (Copy & Paste)

Run this sequence to fully test:

```
1. Click "📁 Memory"
2. Click "+ File"
3. Enter: test.md
4. Type: # Test File
5. Click "Save"
6. Click "🔄 Refresh"
7. Click on "test.md" in tree
8. Verify content loads
9. Edit content
10. Click "Save"
11. Click "🗑️ Delete"
12. Confirm deletion
13. Verify tree is empty
```

If all steps work → **SUCCESS!** ✅

---

## 📞 Still Having Issues?

### Check Backend API
```bash
python check_api_routes.py
```

All should show `[ OK ]`:
```
[ OK ] GET /api/memory/status
[ OK ] GET /api/memory/files
[ OK ] GET /api/memory/file
[ OK ] POST /api/memory/file
[ OK ] POST /api/memory/folder
```

### Check Frontend Build
```bash
cd frontend
npm run build
```

Should complete without TypeScript errors.

### Check Browser Console
Press F12 → Console tab
Look for:
- ❌ Red errors (fix these first)
- ⚠️ Yellow warnings (usually safe to ignore)

### Check Network Tab
Press F12 → Network tab
Filter: XHR
Look for:
- `/api/memory/files` → Status 200
- `/api/memory/status` → Status 200

If 404 → Backend routes not registered
If 401/403 → Authentication issue
If 500 → Backend error (check backend console)

---

## 🎉 Ready to Use!

Once all tests pass, you can:

1. **Create training data files** for Grace
2. **Organize knowledge** into folders
3. **Edit markdown documentation**
4. **Upload existing files**
5. **Manage Grace's corpus**

All changes are immediately persisted to `grace_training/` directory!

---

**Happy coding!** 🚀
