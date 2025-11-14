# GRACE Telemetry Dashboard System

## Overview

The GRACE telemetry dashboard system provides comprehensive multi-layer observability across all system components. It consists of 4 specialized views, unified API endpoints, and real-time WebSocket streaming.

---

## Architecture

### Layer 1: Operations Console (Ops)
**Purpose**: Real-time kernel status, boot/stress metrics, ingestion throughput, crypto health

**Features**:
- Live kernel status monitoring (active/idle/error states)
- Boot time metrics and stress scores
- Kernel control actions (start/stop/restart/stress test)
- Crypto health monitoring (signature validation, encryption status)
- Ingestion throughput metrics (jobs processed, MB/hour)
- Kernel log viewer

**API Endpoints**:
- `GET /api/telemetry/kernels/status` - Kernel metrics
- `GET /api/telemetry/crypto/health` - Crypto health
- `GET /api/telemetry/ingestion/throughput` - Ingestion stats
- `POST /api/telemetry/kernels/{id}/control` - Control kernels
- `GET /api/telemetry/kernels/{id}/logs` - Fetch logs

---

### Layer 2: HTM Console
**Purpose**: Task queue management with timing, size, and SLA tracking

**Features**:
- Real-time HTM queue status (depth, pending, active, completed)
- Task filtering by origin (filesystem, remote, Hunter)
- Task filtering by status (pending, active, completed, failed)
- Timing metrics (avg wait time, P95 duration)
- Size distribution charts
- Workload perception (active agents, auto-escalations)
- SLA breach tracking

**API Endpoints**:
- `GET /api/telemetry/htm/queue` - Queue metrics
- `GET /api/telemetry/htm/tasks` - Task list with filters
- `GET /api/telemetry/htm/workload` - Workload perception

---

### Layer 3: Intent & Learning
**Purpose**: Agentic brain goals, learning retrospectives, playbook success rates

**Features**:
- Active intent tracking with completion status
- Link intents to generated HTM tasks
- Learning retrospectives (insights & improvements)
- Playbook success rate analytics
- AI-generated policy suggestions with confidence scores
- Evidence-based recommendations

**API Endpoints**:
- `GET /api/telemetry/intent/active` - Active intents
- `GET /api/telemetry/learning/retrospectives` - Learning cycles
- `GET /api/telemetry/learning/playbooks` - Playbook stats
- `GET /api/telemetry/learning/policy_suggestions` - Policy AI

---

### Layer 4: Dev/OS View
**Purpose**: Secrets management, recording workflows, deployment status

**Features**:
- Secrets vault status (encrypted items, health)
- Secret storage with consent workflows
- Recording ingestion management
- Remote access session logs
- Deployment status & health checks
- Automated test/stress run triggers

**API Endpoints**:
- `GET /api/telemetry/secrets/status` - Vault status
- `GET /api/telemetry/recordings/pending` - Pending recordings
- `GET /api/telemetry/remote_access/sessions` - Session logs
- `GET /api/telemetry/deployment/status` - Deployment info
- `POST /api/secrets/store` - Store secret with consent
- `POST /api/recording/ingest/{id}` - Trigger ingestion

---

## Real-Time Updates

### WebSocket Streaming
**Endpoint**: `ws://localhost:8000/ws/telemetry`

**Message Format**:
```json
{
  "timestamp": "2025-11-14T10:30:00Z",
  "kernels": {
    "total": 5,
    "active": 3,
    "idle": 2,
    "errors": 0
  },
  "htm": {
    "queue_depth": 12,
    "pending": 8,
    "active": 4
  },
  "crypto": {
    "status": "healthy",
    "signatures_validated": 1234,
    "signature_failures": 2
  }
}
```

**Client Heartbeat**: Send `"ping"` to keep connection alive; receive `{"type": "pong"}`

---

## Installation & Setup

### Backend Setup

1. **Register Routes** (add to your FastAPI app):
```python
from backend.routes import telemetry_api, telemetry_ws

app.include_router(telemetry_api.router)
app.include_router(telemetry_ws.router)

# Start WebSocket broadcaster on startup
@app.on_event("startup")
async def startup():
    await telemetry_ws.start_telemetry_broadcaster()

@app.on_event("shutdown")
async def shutdown():
    await telemetry_ws.stop_telemetry_broadcaster()
```

2. **Database Models Required**:
Ensure these models exist in your database:
- `KernelStatus`
- `IngestionJob`
- `HTMTask`
- `Agent`
- `Intent`
- `PlaybookExecution`
- `PolicySuggestion`
- `SecretVault`
- `Recording`
- `RemoteAccessSession`

---

### Frontend Setup

1. **Install Dependencies**:
```bash
cd frontend
npm install axios
```

2. **Import Dashboards**:
```tsx
import { UnifiedDashboard } from './pages/UnifiedDashboard';

function App() {
  return <UnifiedDashboard />;
}
```

3. **Configure API Base URL**:
Update `API_BASE` in each dashboard component to match your backend URL (default: `http://localhost:8000`)

---

## Usage Guide

### Accessing Dashboards

Navigate to your frontend and use the top navigation to switch between layers:

- **Layer 1 (🎛️ Ops Console)**: Monitor kernel health, control kernels, view crypto status
- **Layer 2 (📊 HTM Queue)**: Track task queues, filter by origin/status, analyze workload
- **Layer 3 (🧠 Learning)**: Review active intents, learning retrospectives, policy suggestions
- **Layer 4 (⚙️ Dev/OS)**: Manage secrets, trigger recordings, view deployment status

### Auto-Refresh

Each dashboard supports auto-refresh toggle:
- Layer 1 & 2: 5-second refresh
- Layer 3 & 4: 10-second refresh

### Kernel Controls (Layer 1)

Available actions per kernel:
- **↻ Restart**: Restart kernel
- **■ Stop**: Stop kernel
- **⚡ Stress**: Run stress test
- **📋 Logs**: View kernel logs

### Task Filtering (Layer 2)

Filter HTM tasks by:
- **Origin**: `all`, `filesystem`, `remote`, `hunter`
- **Status**: `all`, `pending`, `active`, `completed`, `failed`

### Secret Storage (Layer 4)

1. Click **+ Add Secret**
2. Enter secret name, value, and category
3. Review consent modal
4. Confirm to encrypt and store

Secret categories:
- `api_key`
- `password`
- `token`
- `certificate`

### Recording Ingestion (Layer 4)

For each pending recording:
1. View filename, type, size, and creation date
2. Click **Ingest** to trigger processing
3. Recording will be transcribed and indexed

---

## Stress Testing Integration

### Running Stress Tests

**From Layer 1 Console**:
- Select a kernel → click **⚡ Stress** button

**From Layer 4 Dev/OS**:
- Click **⚡ Run Stress Test** in Deployment section

**Verification**:
After stress test:
1. Check Layer 1 for updated stress scores
2. Verify Layer 2 shows increased HTM task activity
3. Monitor crypto health in Layer 1

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     GRACE System                             │
│  ┌─────────────┐  ┌──────────┐  ┌─────────────┐            │
│  │   Kernels   │  │ HTM Queue│  │  Learning   │            │
│  │             │  │          │  │   Loops     │            │
│  └─────┬───────┘  └────┬─────┘  └──────┬──────┘            │
│        │               │               │                    │
└────────┼───────────────┼───────────────┼────────────────────┘
         │               │               │
         ▼               ▼               ▼
┌────────────────────────────────────────────────────────────┐
│              Telemetry API Layer                           │
│   /api/telemetry/kernels/*                                 │
│   /api/telemetry/htm/*                                     │
│   /api/telemetry/learning/*                                │
│   /ws/telemetry (WebSocket)                                │
└────────────────┬───────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│              Frontend Dashboards                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Layer 1  │  │ Layer 2  │  │ Layer 3  │  │ Layer 4  │  │
│  │   Ops    │  │   HTM    │  │ Learning │  │  Dev/OS  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Dashboard Not Loading

1. Verify backend is running: `http://localhost:8000/docs`
2. Check CORS settings in FastAPI
3. Verify API_BASE URL in frontend components
4. Check browser console for errors

### WebSocket Connection Fails

1. Ensure WebSocket broadcaster is started in app startup
2. Check firewall settings for WS connections
3. Verify route is registered: `app.include_router(telemetry_ws.router)`

### Missing Data

1. Verify database models exist
2. Check that services (KernelRegistry, HTMQueue, etc.) are initialized
3. Run migrations if models were recently added
4. Check backend logs for API errors

### Performance Issues

1. Disable auto-refresh if experiencing lag
2. Reduce WebSocket broadcast frequency (default: 2s)
3. Limit task query results (default: 100)
4. Use filters to narrow result sets

---

## Extending the System

### Adding New Metrics

1. **Backend**: Add endpoint to `telemetry_api.py`
2. **WebSocket**: Update `gather_telemetry()` in `telemetry_ws.py`
3. **Frontend**: Add state and fetch logic to relevant dashboard component
4. **UI**: Create visualization components (cards, charts, tables)

### Creating New Dashboard Layers

1. Create new component: `frontend/src/pages/Layer5CustomView.tsx`
2. Add CSS: `frontend/src/pages/Layer5CustomView.css`
3. Register in `UnifiedDashboard.tsx` navigation
4. Add corresponding API endpoints in `telemetry_api.py`

---

## Production Considerations

### Security

- **Secrets**: Never expose secret values in API responses (use masked display)
- **Authentication**: Add auth middleware to telemetry endpoints
- **CORS**: Configure allowed origins for production
- **Rate Limiting**: Add rate limits to prevent API abuse

### Performance

- **Caching**: Cache frequently accessed metrics (Redis)
- **Pagination**: Implement pagination for large datasets
- **Indexing**: Add database indexes on frequently queried fields
- **WebSocket Scaling**: Use Redis pub/sub for multi-instance deployments

### Monitoring

- **Telemetry Metrics**: Monitor the telemetry system itself
- **Error Tracking**: Log API errors and WebSocket disconnections
- **Alerting**: Set up alerts for critical threshold breaches
- **Audit Logs**: Track all control actions (kernel restarts, secret storage)

---

## Support

For issues or feature requests, consult:
- GRACE system documentation
- Backend API docs: `http://localhost:8000/docs`
- Frontend component source code
- System architecture diagrams

---

**Version**: 1.0.0  
**Last Updated**: November 14, 2025  
**Maintained By**: GRACE Platform Team
