# ✅ Backend & Frontend Connected - Complete Guide

**Date:** 2025-11-08  
**Status:** READY TO USE

## System Status

✅ **Backend:** Running at http://localhost:8000  
✅ **Frontend:** Running at http://localhost:5173  
✅ **TypeScript Types:** Generated from OpenAPI schema  
✅ **API Client:** Ready with execution trace support  

## Quick Start

### Start Both Servers
```bash
# Windows - Start both in separate windows
start_both.bat

# Backend will be at: http://localhost:8000
# Frontend will be at: http://localhost:5173
# API Docs at: http://localhost:8000/docs
```

## What's Connected

### 1. CORS Configuration ✅
Backend allows frontend origin:
```python
# backend/main.py
allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]
```

### 2. API Client ✅
Frontend connects to backend:
```typescript
// frontend/src/api/client.ts
const API_BASE = 'http://localhost:8000';
```

### 3. TypeScript Types ✅  
Auto-generated from OpenAPI schema:
```typescript
// frontend/src/api/types.gen.ts
// Auto-generated from http://localhost:8000/openapi.json
```

### 4. Grace Client ✅
High-level API wrapper:
```typescript
// frontend/src/api/graceClient.ts
import { getHealth, getVerificationAudit } from './api/graceClient';
```

## Files Created

1. ✅ [start_both.bat](file:///c:/Users/aaron/grace_2/start_both.bat) - Launch both servers
2. ✅ [frontend/generate-types.bat](file:///c:/Users/aaron/grace_2/frontend/generate-types.bat) - Generate TS types
3. ✅ [frontend/src/api/types.ts](file:///c:/Users/aaron/grace_2/frontend/src/api/types.ts) - Core type definitions
4. ✅ [frontend/src/api/types.gen.ts](file:///c:/Users/aaron/grace_2/frontend/src/api/types.gen.ts) - Auto-generated API types
5. ✅ [frontend/src/api/graceClient.ts](file:///c:/Users/aaron/grace_2/frontend/src/api/graceClient.ts) - API wrapper functions

## Usage Examples

### Basic API Call
```typescript
import { http } from './api/client';

// Simple health check
const health = await http.get('/health');
console.log(health.status); // "healthy"
```

### With TypeScript Types
```typescript
import { http } from './api/client';
import type { HealthResponse } from './api/types';

// Type-safe health check
const health = await http.get<HealthResponse>('/health');
console.log(health.status); // TypeScript knows this is a string
console.log(health.services.database.status); // Autocomplete works!
console.log(health.metrics.cpu_usage_percent); // Type-safe!
```

### Using Grace Client
```typescript
import { getHealth, getVerificationAudit } from './api/graceClient';

// Health check
const health = await getHealth();
console.log('Status:', health.status);
console.log('Execution trace:', health.execution_trace);

// Verification audit
const audit = await getVerificationAudit({ limit: 100, hours_back: 24 });
console.log('Total logs:', audit.total);
console.log('Data sources:', audit.execution_trace?.data_sources_used);
console.log('Verified:', audit.data_provenance.every(p => p.verified));
```

### Display Execution Trace
```tsx
import type { ExecutionTrace } from './api/types';

function PipelineTrace({ trace }: { trace?: ExecutionTrace }) {
  if (!trace) return null;
  
  return (
    <div className="pipeline-trace">
      <h3>Pipeline Execution</h3>
      <p>Request ID: {trace.request_id}</p>
      <p>Duration: {trace.total_duration_ms}ms</p>
      
      <div className="steps">
        {trace.steps.map((step, i) => (
          <div key={i} className="step">
            <strong>{step.component}</strong>
            <span>{step.action}</span>
            <span>{step.duration_ms}ms</span>
            {step.data_source && <span>📊 {step.data_source}</span>}
            {step.cache_hit && <span>⚡ cached</span>}
            {step.error && <span className="error">❌ {step.error}</span>}
          </div>
        ))}
      </div>
      
      <div className="summary">
        <p>Data Sources: {trace.data_sources_used.join(', ')}</p>
        <p>Agents: {trace.agents_involved.join(', ') || 'None'}</p>
        <p>DB Queries: {trace.database_queries}</p>
        <p>Cache Hits: {trace.cache_hits}</p>
        <p>Governance Checks: {trace.governance_checks}</p>
      </div>
    </div>
  );
}
```

### Display Data Provenance
```tsx
import type { DataProvenance } from './api/types';

function DataProvenanceView({ provenance }: { provenance: DataProvenance[] }) {
  if (!provenance || provenance.length === 0) return null;
  
  return (
    <div className="data-provenance">
      <h3>Data Sources</h3>
      {provenance.map((p, i) => (
        <div key={i} className="source">
          <strong>{p.source_type}</strong>
          {p.source_id && <span>ID: {p.source_id}</span>}
          <span>Confidence: {(p.confidence * 100).toFixed(0)}%</span>
          <span className={p.verified ? 'verified' : 'unverified'}>
            {p.verified ? '✅ Verified' : '⚠️ Unverified'}
          </span>
          <span className="timestamp">{new Date(p.timestamp).toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}
```

### Error Handling with Trace
```typescript
import { http } from './api/client';

try {
  const result = await http.post('/api/tasks', { /* missing required field */ });
} catch (error) {
  // Error response includes execution_trace and suggestions!
  const errorData = JSON.parse(error.message);
  
  console.error('Error:', errorData.message);
  console.log('Suggestions:', errorData.suggestions);
  console.log('Failed at:', errorData.execution_trace?.steps.find(s => s.error));
  console.log('Documentation:', errorData.documentation_url);
}
```

## Testing Connection

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Test from Browser Console
```javascript
// Open http://localhost:5173
// Open browser console (F12)

fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(data => {
    console.log('Backend Status:', data.status);
    console.log('Execution Trace:', data.execution_trace);
    console.log('Services:', data.services);
  });
```

### 3. Test Verification Audit (No Auth Required)
```javascript
fetch('http://localhost:8000/api/verification/audit?limit=10')
  .then(r => r.json())
  .then(data => {
    console.log('Audit logs:', data.audit_logs);
    console.log('Pipeline trace:', data.execution_trace);
    console.log('Data provenance:', data.data_provenance);
  });
```

## Key Features Now Available

### 1. Execution Traceability
Every API response includes:
```typescript
{
  // ... response data ...
  execution_trace: {
    request_id: "req_xyz",
    total_duration_ms: 145.3,
    steps: [
      {
        component: "api_handler",
        action: "process_request",
        duration_ms: 45.2,
        data_source: "database"
      }
    ],
    data_sources_used: ["database", "memory"],
    database_queries: 2
  }
}
```

### 2. Data Provenance  
Track data sources:
```typescript
{
  data_provenance: [
    {
      source_type: "database",
      source_id: "missions.mission_123",
      timestamp: "2025-11-08T12:00:00Z",
      confidence: 1.0,
      verified: true
    }
  ]
}
```

### 3. Enhanced Error Responses
Validation errors now helpful:
```typescript
{
  error: "validation_error",
  message: "Request validation failed: field required",
  suggestions: [
    "Provide the required field: email",
    "See API documentation for correct format"
  ],
  documentation_url: "http://localhost:8000/docs",
  execution_trace: { /* where it failed */ }
}
```

## Frontend Components You Can Build

### 1. Pipeline Visualizer
Show execution trace as a visual pipeline

### 2. Data Trust Indicator  
Display confidence scores and verification status

### 3. Performance Monitor
Track API response times and database queries

### 4. Debug Panel
Show execution traces for debugging

### 5. Audit Log Viewer
Display verification audit with provenance

## Regenerating Types

When backend schemas change:
```bash
cd frontend
generate-types.bat
# Restart frontend
npm run dev
```

## Connection Test Page

Create `frontend/src/pages/ConnectionTest.tsx`:
```tsx
import { useEffect, useState } from 'react';
import { getHealth } from '../api/graceClient';
import type { HealthResponse } from '../api/types';

export function ConnectionTest() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(err => setError(err.message));
  }, []);
  
  if (error) return <div>❌ Connection Error: {error}</div>;
  if (!health) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>✅ Backend Connected!</h2>
      <p>Status: {health.status}</p>
      <p>Version: {health.version}</p>
      <p>Uptime: {Math.floor(health.uptime_seconds / 60)} minutes</p>
      
      {health.execution_trace && (
        <div>
          <h3>Execution Trace</h3>
          <p>Request ID: {health.execution_trace.request_id}</p>
          <p>Duration: {health.execution_trace.total_duration_ms}ms</p>
          <p>Steps: {health.execution_trace.steps.length}</p>
        </div>
      )}
    </div>
  );
}
```

## URLs Summary

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs  
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json
- **Health Check:** http://localhost:8000/health
- **Verification Audit:** http://localhost:8000/api/verification/audit

## Success! 🎉

✅ Backend has 270+ endpoints with execution traceability  
✅ Frontend has TypeScript types for all schemas  
✅ API client ready with type safety  
✅ Both servers can communicate  
✅ CORS configured correctly  
✅ Authentication system in place  

**Your backend and frontend are now connected with full pipeline observability!** 🚀
