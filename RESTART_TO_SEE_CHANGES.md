# 🔄 Server Restart Required

## Current Issue

The backend server is running with OLD CODE that:
- ❌ Still requires auth on /api/verification/audit (403 errors)
- ❌ Doesn't include execution_trace in responses yet
- ❌ Doesn't include data_provenance yet

## Solution: Restart Backend

### Option 1: Use Restart Script
```bash
restart_backend.bat
```

### Option 2: Manual Restart
```bash
# 1. Kill existing Python processes
taskkill /F /IM python.exe

# 2. Start fresh
cd backend
..\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: If server has --reload flag
The server might auto-reload, wait 5-10 seconds and test:
```bash
curl http://localhost:8000/api/verification/audit?limit=5
# Should return 200 OK (no auth) with execution_trace
```

## Verify Changes Applied

After restart, test:

### 1. Health endpoint should include execution_trace
```bash
curl http://localhost:8000/health | findstr "execution_trace"
# Should see: "execution_trace":{"request_id":...
```

### 2. Audit endpoint should work without auth
```bash
curl http://localhost:8000/api/verification/audit?limit=5
# Should return 200 OK, not 403
# Should include audit_logs, execution_trace, data_provenance
```

### 3. Validation errors should be enhanced
```bash
curl -X GET "http://localhost:8000/api/verification/audit?limit=invalid"
# Should return 422 with execution_trace and suggestions
```

## What Will Work After Restart

✅ No auth required on monitoring endpoints  
✅ All responses include execution_trace  
✅ All responses include data_provenance  
✅ Validation errors include helpful suggestions  
✅ Frontend can display pipeline traces  
✅ API docs show proper schemas (not "string")  

## Then Test Frontend

Once backend is restarted:

1. **Go to frontend:** http://localhost:5173
2. **Open browser console** (F12)
3. **Run test:**
```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(data => {
    console.log('✅ Connected!');
    console.log('Execution trace:', data.execution_trace);
    console.log('Data provenance:', data.data_provenance);
  });
```

## Files Ready to Use

- ✅ [start_both.bat](file:///c:/Users/aaron/grace_2/start_both.bat) - Start both servers
- ✅ [restart_backend.bat](file:///c:/Users/aaron/grace_2/restart_backend.bat) - Restart backend only
- ✅ [frontend/src/pages/ConnectionTestPage.tsx](file:///c:/Users/aaron/grace_2/frontend/src/pages/ConnectionTestPage.tsx) - Test UI
- ✅ [frontend/src/api/graceClient.ts](file:///c:/Users/aaron/grace_2/frontend/src/api/graceClient.ts) - Type-safe API client
- ✅ [frontend/src/api/types.gen.ts](file:///c:/Users/aaron/grace_2/frontend/src/api/types.gen.ts) - Auto-generated types

**Restart the backend server to see all the changes!** 🔄
