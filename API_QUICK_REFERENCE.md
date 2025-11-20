# API Quick Reference

## 🚀 Starting Services

```bash
# Start both backend and frontend
python server.py

# Or manually:
# Terminal 1
python server.py

# Terminal 2  
cd frontend && npm run dev
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React UI |
| Backend | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health | http://localhost:8000/health | Health check |

## 📡 Key API Endpoints

### Chat & Communication
```bash
POST   /api/chat                    # Send message
GET    /api/chat/sessions          # List sessions
GET    /api/chat/history/{id}      # Get history
```

### Metrics & Monitoring
```bash
GET    /api/metrics/summary        # System metrics
GET    /api/metrics/health         # Health status
```

### Mission Control
```bash
GET    /api/mission-control/missions           # List missions
POST   /api/mission-control/execute/{id}       # Execute mission
GET    /api/mission-control/status             # Mission status
```

### Self-Healing
```bash
GET    /api/self-healing/stats                 # Statistics
GET    /api/self-healing/incidents             # Recent incidents
POST   /api/self-healing/trigger               # Trigger healing
```

### Guardian (Network Healing)
```bash
GET    /api/guardian/status                    # Guardian status
GET    /api/guardian/healer/stats              # Network healing stats
POST   /api/guardian/healer/scan               # Trigger network scan
GET    /api/guardian/playbooks                 # List playbooks
```

### Learning System
```bash
GET    /api/learning/status                    # Learning status
GET    /api/learning/outcomes                  # Learning outcomes
POST   /api/learning/request                   # Request learning
GET    /api/learning/domains                   # List domains
```

### Snapshots
```bash
GET    /api/snapshots/list                     # List snapshots
POST   /api/snapshots/create                   # Create snapshot
POST   /api/snapshots/restore/{id}             # Restore snapshot
GET    /api/snapshots/stats                    # Snapshot statistics
```

### Memory & Knowledge
```bash
GET    /api/memory/files/ingestions            # List ingested files
GET    /api/memory/search                      # Search memory
POST   /api/memory/upload                      # Upload file
```

### Tasks
```bash
GET    /api/tasks                              # List tasks
POST   /api/tasks/create                       # Create task
PUT    /api/tasks/{id}                         # Update task
DELETE /api/tasks/{id}                         # Delete task
```

### Governance & Approvals
```bash
GET    /api/governance/pending                 # Pending approvals
POST   /api/governance/approve/{id}            # Approve action
POST   /api/governance/reject/{id}             # Reject action
GET    /api/governance/stats                   # Governance stats
```

### Chaos Engineering
```bash
GET    /api/chaos/status                       # Chaos status
POST   /api/chaos/campaign/start               # Start campaign
POST   /api/chaos/campaign/stop                # Stop campaign
GET    /api/chaos/campaigns                    # List campaigns
```

## 🔧 Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Get metrics
curl http://localhost:8000/api/metrics/summary

# List missions
curl http://localhost:8000/api/mission-control/missions

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Grace"}'

# Trigger self-healing scan
curl -X POST http://localhost:8000/api/self-healing/trigger

# Get learning status
curl http://localhost:8000/api/learning/status
```

## 💻 Using in Frontend

### Example: Fetch Metrics
```typescript
import { API_BASE_URL } from '../config';

async function getMetrics() {
  const response = await fetch(`${API_BASE_URL}/api/metrics/summary`);
  if (!response.ok) throw new Error('Failed to fetch metrics');
  return response.json();
}
```

### Example: Send Chat Message
```typescript
import { API_BASE_URL } from '../config';

async function sendMessage(message: string) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) throw new Error('Failed to send message');
  return response.json();
}
```

### Example: Using Existing API Clients
```typescript
import { MissionControlAPI } from '../api/missions';
import { IncidentsAPI } from '../api/incidents';
import { SnapshotAPI } from '../api/snapshots';

// Use pre-built API clients
const missions = await MissionControlAPI.listMissions();
const stats = await IncidentsAPI.getStats();
const snapshots = await SnapshotAPI.listSnapshots();
```

## 🎨 Pre-built API Clients

Located in `frontend/src/api/`:

- `chat.ts` - Chat API
- `missions.ts` - Mission Control API
- `snapshots.ts` - Snapshot API
- `incidents.ts` - Self-Healing API
- `chaos.ts` - Chaos Engineering API
- `learning.ts` - Learning API
- `memory.ts` - Memory API
- `tasks.ts` - Task API
- `trust.ts` - Trust Framework API
- `governance.ts` - Governance API
- `comprehensive.ts` - Comprehensive metrics
- And 20+ more...

## 🐛 Troubleshooting

### CORS Error
```
✅ Already configured - no action needed
Backend allows all origins
```

### 404 Not Found
```
1. Check route is registered in backend/main.py
2. Verify endpoint path starts with /api
3. Restart backend server
```

### Connection Refused
```
1. Ensure backend is running: python server.py
2. Check port 8000 is not blocked
3. Verify VITE_BACKEND_URL in .env.local
```

### Proxy Error in Development
```
1. Check vite.config.ts proxy config
2. Ensure backend URL is http://localhost:8000
3. Restart Vite dev server
```

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (React + Vite)         │
│              Port 5173                  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Components & Pages             │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │   API Clients (TypeScript)       │  │
│  │   - missions.ts                  │  │
│  │   - incidents.ts                 │  │
│  │   - snapshots.ts                 │  │
│  │   - 30+ more...                  │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │   Vite Proxy (/api/*)            │  │
│  └──────────┬───────────────────────┘  │
└─────────────┼───────────────────────────┘
              │
              │ HTTP
              │
┌─────────────▼───────────────────────────┐
│      Backend (FastAPI)                  │
│           Port 8000                     │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   CORS Middleware                │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │   Routes (180+ endpoints)        │  │
│  │   - chat_api.py                  │  │
│  │   - mission_control_api.py       │  │
│  │   - self_healing_api.py          │  │
│  │   - 180+ more...                 │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │   Core Services                  │  │
│  │   - Guardian                     │  │
│  │   - Self-Healing                 │  │
│  │   - Learning System              │  │
│  │   - Mission Control              │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## ✅ Integration Checklist

- ✅ Backend running on port 8000
- ✅ Frontend running on port 5173
- ✅ CORS configured (allow all origins)
- ✅ Vite proxy configured (/api -> :8000)
- ✅ API clients created (30+ files)
- ✅ Backend routes registered (180+ endpoints)
- ✅ Environment variables configured
- ✅ Health check endpoint working

## 📝 Quick Commands

```bash
# Start everything
python server.py

# Test backend health
curl http://localhost:8000/health

# View API docs
start http://localhost:8000/docs

# View frontend
start http://localhost:5173

# Run integration test
TEST_INTEGRATION.bat
```

---

**Status: ✅ Fully integrated and ready to use!**
