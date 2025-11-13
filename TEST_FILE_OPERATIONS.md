# File Operations Fix Guide

## Changes Made

### 1. ✅ Renamed Tab
- "Trusted Sources" → "Trusted Data Sources"

### 2. ✅ Fixed API Endpoints
**Create File**:
- Endpoint: `/api/memory/files/create`
- Param: `is_directory: false` (was `is_folder`)

**Create Folder**:
- Endpoint: `/api/memory/files/create`
- Param: `is_directory: true`

**Upload File**:
- FormData field: `target_path` (was `path`)

### 3. ✅ Added Console Logging
All operations now log:
- Current path
- Target path
- Response data
- Error details

### 4. ✅ Path Normalization
```typescript
// Building new path
const newPath = currentPath 
  ? `/${currentPath}/${name}`.replace(/\/+/g, '/') 
  : `/${name}`;

// Example:
// currentPath = "business intellinagce"
// name = "test.txt"
// newPath = "/business intellinagce/test.txt"
```

---

## How to Test

### 1. Open Browser Console
```
F12 → Console tab
```

### 2. Navigate to Subfolder
```
Double-click "business intellinagce"
Watch console for:
  "Navigating to: business intellinagce"
  "Loaded folder: business intellinagce"
```

### 3. Create File
```
Click "New File"
Enter: "test.txt"
Watch console for:
  "Creating file at: /business intellinagce/test.txt"
  "Current path: business intellinagce"
  "Create file response: {success: true, ...}"
```

### 4. Check Result
```
Should see alert: "✅ Created test.txt in business intellinagce"
File should appear in the folder list
```

### 5. Upload File
```
Click "Upload"
Select a file
Watch console for:
  "Uploading to: /business intellinagce"
  "Upload response: {success: true, ...}"
```

---

## If Still Not Working

### Debug Steps

1. **Check Console Logs**:
   - Look for error messages
   - Check path values
   - Verify API response

2. **Check Network Tab** (F12 → Network):
   - See actual API call
   - Check request parameters
   - View response body

3. **Common Issues**:

**Issue**: "Path already exists"
- **Fix**: File/folder name is duplicate

**Issue**: "Access denied"
- **Fix**: Security check failed, path issue

**Issue**: File appears in root instead of subfolder
- **Check**: Console log shows correct `newPath`
- **Check**: Network tab shows correct parameter

---

## Backend API Reference

### POST /api/memory/files/create
**Parameters**:
- `path`: Full path like `/business intellinagce/test.txt`
- `is_directory`: `true` for folder, `false` for file

**Returns**:
```json
{
  "success": true,
  "path": "/business intellinagce/test.txt",
  "type": "file"
}
```

### POST /api/memory/files/upload
**FormData**:
- `file`: File object
- `target_path`: Directory path like `/business intellinagce`

**Returns**:
```json
{
  "success": true,
  "path": "/business intellinagce/filename.pdf",
  "name": "filename.pdf",
  "size": 12345
}
```

---

## Current Path Format

**Storage**:
- `currentPath` = `"business intellinagce"` (no leading slash)

**API Calls**:
- Create: `path = "/business intellinagce/test.txt"` (with leading slash)
- Upload: `target_path = "/business intellinagce"` (with leading slash)
- Load: `path = "business intellinagce"` or `"/"` (no leading slash or just slash)

**This is intentional** - internal state has no slash, API calls add it.

---

## Expected Behavior

✅ **Create File in Root**:
- currentPath = `""`
- newPath = `/test.txt`
- Creates at: `grace_training/test.txt`

✅ **Create File in Subfolder**:
- currentPath = `"business intellinagce"`
- newPath = `/business intellinagce/test.txt`
- Creates at: `grace_training/business intellinagce/test.txt`

✅ **Upload to Subfolder**:
- currentPath = `"business intellinagce"`
- target_path = `/business intellinagce`
- Uploads to: `grace_training/business intellinagce/`

---

## Next Steps

1. **Refresh browser**: `F5`
2. **Open console**: `F12`
3. **Navigate to subfolder**
4. **Try creating file** - watch console logs
5. **If error**: Share console output

**The fix is deployed, test it now!**
