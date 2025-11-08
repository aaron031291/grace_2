# Connecting Backend and Frontend

## Quick Start

### Option 1: Start Both Servers Together
```bash
# Windows
start_both.bat

# This starts:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:5173
```

### Option 2: Start Manually

**Terminal 1 - Backend:**
```bash
cd backend
..\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## TypeScript Types

### Generate Types from Backend Schemas

```bash
# Option 1: Use the generator script
cd frontend
generate-types.bat

# Option 2: Manual
curl http://localhost:8000/openapi.json -o src/api/openapi.json
npx openapi-typescript src/api/openapi.json -o src/api/types.gen.ts
```

### Use Types in Frontend

```typescript
import { http } from './api/client';
import type { 
  HealthResponse, 
  ExecutionTrace, 
  DataProvenance,
  VerificationAuditResponse 
} from './api/types';

// Health check with execution trace
const health = await http.get<HealthResponse>('/health');
console.log('Status:', health.status);
console.log('Execution trace:', health.execution_trace);
console.log('Data sources:', health.execution_trace?.data_sources_used);

// Verification audit with traceability
const audit = await http.get<VerificationAuditResponse>('/api/verification/audit', {
  query: { limit: 100, hours_back: 24 }
});
console.log('Audit logs:', audit.audit_logs);
console.log('Pipeline steps:', audit.execution_trace?.steps);
console.log('Data provenance:', audit.data_provenance);
```

## Backend-Frontend Connection

### CORS Configuration

Backend is configured to allow frontend:
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Client Configuration

Frontend automatically connects to backend:
```typescript
// frontend/src/api/client.ts
const API_BASE = 'http://localhost:8000';  // Default

// Set custom base URL if needed
export const api = {
  base: API_BASE
};
```

### Authentication

```typescript
import { setAuthToken, http } from './api/client';

// Login
const { access_token } = await http.post('/api/auth/login', {
  username: 'user',
  password: 'password'
});

// Set token for future requests
setAuthToken(access_token);

// Now all requests include: Authorization: Bearer <token>
const tasks = await http.get('/api/tasks');
```

## Testing Connection

### 1. Test Backend
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

### 2. Test Frontend → Backend
Open browser to `http://localhost:5173` and check console:
```javascript
// In browser console
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
// Should show health response with execution_trace
```

### 3. Test API with Execution Traces
```bash
# Test verification audit (no auth)
curl http://localhost:8000/api/verification/audit?limit=10

# Should return JSON with execution_trace and data_provenance fields
```

## New Features Available

### All Responses Include Traceability

Every API response now has:

```typescript
interface AnyResponse {
  // ... response-specific fields ...
  
  execution_trace?: {
    request_id: string;
    total_duration_ms: number;
    steps: Array<{
      component: string;
      action: string;
      duration_ms: number;
      data_source?: string;
    }>;
    data_sources_used: string[];
    agents_involved: string[];
    database_queries: number;
  };
  
  data_provenance: Array<{
    source_type: string;
    timestamp: string;
    confidence: number;
    verified: boolean;
  }>;
}
```

### Frontend Can Display:

1. **Pipeline Visualization**
   - Show which components handled the request
   - Display timing for each step
   - Highlight slow operations

2. **Data Source Tracking**
   - Show where data came from
   - Display confidence scores
   - Show verification status

3. **Performance Monitoring**
   - Track API response times
   - Identify bottlenecks
   - Monitor database query counts

4. **Debug Information**
   - Request IDs for support
   - Complete execution traces
   - Data provenance chains

## Example: Display Execution Trace

```tsx
import type { ExecutionTrace } from './api/types';

function ExecutionTraceView({ trace }: { trace?: ExecutionTrace }) {
  if (!trace) return <div>No trace available</div>;
  
  return (
    <div>
      <h3>Request: {trace.request_id}</h3>
      <p>Total Duration: {trace.total_duration_ms}ms</p>
      
      <h4>Pipeline Steps:</h4>
      {trace.steps.map((step, i) => (
        <div key={i}>
          {step.step_number}. {step.component} → {step.action}
          <span>({step.duration_ms}ms)</span>
          {step.data_source && <span>from {step.data_source}</span>}
        </div>
      ))}
      
      <h4>Summary:</h4>
      <ul>
        <li>Data sources: {trace.data_sources_used.join(', ')}</li>
        <li>Agents: {trace.agents_involved.join(', ')}</li>
        <li>DB queries: {trace.database_queries}</li>
        <li>Cache hits: {trace.cache_hits}</li>
      </ul>
    </div>
  );
}
```

## Troubleshooting

### Backend not responding
```bash
# Check if running
curl http://localhost:8000/health

# Restart if needed
cd backend
..\\.venv\\Scripts\\python.exe -m uvicorn main:app --reload
```

### Frontend can't connect
```bash
# Check CORS errors in browser console
# Verify backend allows: http://localhost:5173

# Check frontend is running
# Should see: Local: http://localhost:5173
```

### Types not updating
```bash
# Regenerate types
cd frontend
generate-types.bat

# Restart frontend
npm run dev
```

## Next Steps

1. ✅ Backend running: http://localhost:8000
2. ✅ Frontend configured with API client
3. ✅ TypeScript types ready
4. 🔄 Run `start_both.bat` to launch both
5. 🔄 Test connection in browser
6. 🔄 Update frontend UI to display execution traces

**Ready to connect! Run `start_both.bat` to launch the full system.** 🚀
