# 🔄 Restart Backend to Load Memory API

## Issue
The new memory API routes were created but the backend server needs to restart to load them.

## Solution

### Option 1: Restart Grace Completely
```powershell
# Stop Grace (Ctrl+C in the terminal running it)
# Then restart:
.\GRACE.ps1
```

### Option 2: Restart Just the Backend
```powershell
# Stop the backend process
# Then run:
python backend/main.py
```

### Option 3: Use the Universal Restart
```powershell
.\grace-universal.ps1
```

## Verify It's Working

After restart, test the endpoints:

```bash
# Test file tree
curl http://localhost:8000/api/memory/files

# Test status
curl http://localhost:8000/api/memory/status

# Test tables list
curl http://localhost:8000/api/memory/tables/list
```

You should see JSON responses instead of 500 errors.

## What Was Added

The memory API routes are already registered in `backend/main.py` line 560:
```python
app.include_router(memory_api.router)
```

The routes just created:
- ✅ GET /api/memory/files
- ✅ GET /api/memory/files/content
- ✅ POST /api/memory/files/content
- ✅ POST /api/memory/files/upload
- ✅ POST /api/memory/files/create
- ✅ DELETE /api/memory/files/delete
- ✅ GET /api/memory/tables/list
- ✅ GET /api/memory/tables/{table}/schema
- ✅ GET /api/memory/tables/{table}/rows
- ✅ POST /api/memory/tables/{table}/rows
- ✅ PUT /api/memory/tables/{table}/rows/{id}
- ✅ DELETE /api/memory/tables/{table}/rows/{id}
- ✅ GET /api/memory/schemas/pending
- ✅ POST /api/memory/schemas/approve
- ✅ GET /api/memory/status

**Once you restart the backend, all these endpoints will be live! 🚀**
