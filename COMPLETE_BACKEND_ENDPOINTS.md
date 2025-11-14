# Complete Backend API Endpoints

## All 25 Endpoints Added to backend/main.py

### Core System (5)
- `GET /` - Root
- `GET /health` - Health check
- `GET /api/health` - Detailed health with all layers
- `GET /api/status` - System status
- `GET /api/control/state` - Control plane (19 kernels)

### Clarity Framework (3)
- `GET /api/clarity/status` - Framework status
- `GET /api/clarity/components` - All 19 components
- `GET /api/clarity/events` - Event log

### Ingestion (4)
- `GET /api/ingestion/status` - Orchestrator status
- `GET /api/ingestion/tasks` - Task list
- `POST /api/ingestion/start` - Start task
- `POST /api/ingestion/stop/{task_id}` - Stop task

### Memory & Files (1)
- `GET /api/memory/files` - File browser

### Security (1)
- `GET /api/hunter/alerts` - Security alerts

### Kernels & Telemetry (5)
- `GET /api/kernels/layer1/status` - Layer 1 kernels
- `GET /api/telemetry/kernels/status` - All 19 kernels with metrics
- `GET /api/telemetry/crypto/health` - Crypto health
- `GET /api/telemetry/ingestion/throughput` - Throughput
- `GET /api/telemetry/kernels/{id}/logs` - Kernel logs

### Self-Healing (6) ⭐ NEW - For buttons to work
- `GET /api/self-healing/stats` - Statistics
- `GET /api/self-healing/incidents` - Incident list
- `POST /api/self-healing/incidents/{id}/acknowledge` - Acknowledge one
- `POST /api/self-healing/acknowledge-all` - Acknowledge all high
- `GET /api/self-healing/export` - Export report
- `GET /api/monitoring/incidents` - Monitoring incidents

## Button Mapping

| Button | Endpoint |
|--------|----------|
| **Acknowledge All High** | POST /api/self-healing/acknowledge-all?severity=high |
| **Export Report** | GET /api/self-healing/export |
| **View Logs** | GET /api/telemetry/kernels/{kernel_id}/logs |

## Restart Required

The backend must be restarted to load all 25 endpoints:

```bash
cd C:\Users\aaron\grace_2
python serve.py
```

Or use: `restart_backend.cmd`

After restart, all buttons will work!
