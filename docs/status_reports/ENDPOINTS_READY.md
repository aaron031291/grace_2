# Backend Endpoints - Ready for Console

All backend endpoints have been exposed and configured for the Grace Console frontend.

## ✅ Vault API (`/api/vault/*`)

**File:** `backend/routes/vault_api.py`  
**Registered in:** `backend/main.py` (line 68)

### Endpoints:
- `POST /api/vault/secrets` - Create/store a secret
- `GET /api/vault/secrets` - List secrets (metadata only)
- `GET /api/vault/secrets/{name}` - Get secret value
- `DELETE /api/vault/secrets/{name}` - Revoke/delete secret
- `GET /api/vault/health` - Health check

### Frontend Service:
- **File:** `frontend/src/services/vaultApi.ts`
- **Features:** Graceful 404 handling, proper auth headers, error handling

---

## ✅ Mission Control API (`/mission-control/*`)

**File:** `backend/routes/mission_control_api.py`  
**Registered in:** `backend/main.py` (already included)

### Endpoints:
- `GET /mission-control/missions` - List missions with filtering
- `GET /mission-control/missions/{mission_id}` - Get mission details
- `POST /mission-control/missions/{mission_id}/execute` - Execute mission
- `GET /mission-control/status` - System status
- `GET /mission-control/subsystems` - Subsystem health

### Frontend Service:
- **File:** `frontend/src/services/missionApi.ts`
- **Features:** Graceful 404 handling, returns empty array if endpoint missing

---

## ✅ Logs API (`/api/logs/*`)

**File:** `backend/routes/logs_api.py`  
**Registered in:** `backend/main.py` (already included)

### Endpoints:
- `GET /api/logs/recent` - Get recent logs with filtering
  - Query params: `limit`, `level`, `domain`, `search`
- `GET /api/logs/governance` - Get governance-specific logs (NEW)
  - Query params: `limit`, `level`, `search`
- `GET /api/logs/domains` - List available log domains
- `GET /api/logs/levels` - List available log levels
- `WS /api/logs/stream` - WebSocket for real-time log streaming
- `GET /api/logs/health` - Health check

### Frontend Service:
- **File:** `frontend/src/services/logsApi.ts` (NEW)
- **Features:** 
  - Graceful 404 handling
  - WebSocket connection support
  - Returns empty arrays if endpoints missing
  - Proper error logging

---

## ✅ Ingestion API (`/api/ingest/*`)

**File:** `backend/routes/ingest.py`  
**Registered in:** `backend/main.py` (line 65)

### Endpoints:
- `POST /api/ingest/upload` - Upload and ingest file (NEW)
- `POST /api/ingest/file` - Upload and ingest file
- `POST /api/ingest/text` - Ingest text content
- `POST /api/ingest/url` - Ingest from URL
- `GET /api/ingest/artifacts` - List artifacts

---

## Frontend Integration

### Graceful Error Handling

All frontend API services now include graceful 404 handling:

1. **Vault API** - Returns empty arrays/objects if endpoint missing
2. **Mission API** - Returns `{ total: 0, missions: [] }` if endpoint missing
3. **Logs API** - Returns `{ logs: [], total: 0 }` if endpoint missing

### Console Logs

All services log warnings when endpoints are missing:
```javascript
console.warn('[Vault API] listSecrets endpoint not available (404)');
console.warn('[Mission API] Missions endpoint not available (404)');
console.warn('[Logs API] /api/logs/recent endpoint not available (404)');
```

This allows the console to work even if some endpoints aren't ready, while giving clear feedback about what's missing.

---

## Testing

### Quick Test Commands

```bash
# Test vault endpoint
curl http://localhost:8017/api/vault/secrets -H "Authorization: Bearer dev-token"

# Test mission control
curl http://localhost:8017/mission-control/missions -H "Authorization: Bearer dev-token"

# Test logs
curl "http://localhost:8017/api/logs/recent?limit=10"

# Test governance logs
curl "http://localhost:8017/api/logs/governance?limit=10"

# Test health checks
curl http://localhost:8017/api/vault/health
curl http://localhost:8017/api/logs/health
```

---

## Next Steps

1. **Start the backend:** `python serve.py`
2. **Start the frontend:** `cd frontend && npm run dev`
3. **Open console:** Navigate to frontend URL
4. **Test features:**
   - Open Vault panel - should show secrets interface
   - Open Tasks panel - should show missions
   - Open Logs panel - should show recent logs
   - Check browser console for any 404 warnings

If any endpoint returns 404, the UI will show "Endpoint missing" or an empty state, making it clear what needs to be implemented.
