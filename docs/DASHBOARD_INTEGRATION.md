# Quick Integration Guide: GRACE Telemetry Dashboards

## Step 1: Register Backend Routes

Add to your FastAPI application (e.g., `serve.py` or main app file):

```python
from backend.routes import telemetry_api, telemetry_ws

# Register routers
app.include_router(telemetry_api.router)
app.include_router(telemetry_ws.router)

# Start WebSocket broadcaster
@app.on_event("startup")
async def startup_telemetry():
    from backend.routes.telemetry_ws import start_telemetry_broadcaster
    await start_telemetry_broadcaster()

@app.on_event("shutdown")
async def shutdown_telemetry():
    from backend.routes.telemetry_ws import stop_telemetry_broadcaster
    await stop_telemetry_broadcaster()
```

## Step 2: Verify Database Models

Ensure these models exist or create stub implementations:

### Required Models:
- `backend.kernels.kernel_registry.KernelRegistry`
- `backend.memory_services.htm_queue.HTMQueue`
- `backend.crypto.crypto_health.CryptoHealthMonitor`
- `backend.learning_systems.learning_loop.LearningLoop`
- `backend.models.IngestionJob`
- `backend.models.HTMTask`
- `backend.models.Agent`
- `backend.models.Intent`
- `backend.models.PlaybookExecution`
- `backend.models.PolicySuggestion`
- `backend.models.SecretVault`
- `backend.models.Recording`
- `backend.models.RemoteAccessSession`

### If Models Don't Exist:

Create stub classes that return empty data:

```python
# backend/kernels/kernel_registry.py
class KernelRegistry:
    async def get_all_kernels(self):
        return []
    
    async def start_kernel(self, kernel_id: str):
        pass
    
    async def stop_kernel(self, kernel_id: str):
        pass
    
    async def restart_kernel(self, kernel_id: str):
        pass
    
    async def run_stress_test(self, kernel_id: str):
        pass
    
    async def get_kernel_logs(self, kernel_id: str, lines: int = 100):
        return []

# backend/memory_services/htm_queue.py
class HTMQueue:
    async def get_queue_metrics(self):
        return {
            "depth": 0,
            "pending": 0,
            "active": 0,
            "completed_today": 0,
            "failed_today": 0,
            "avg_wait_time": 0,
            "p95_duration": 0,
            "avg_size_mb": 0,
            "sla_breaches": 0,
            "tasks": []
        }

# backend/crypto/crypto_health.py
class CryptoHealthMonitor:
    async def get_health_status(self):
        return {
            "status": "healthy",
            "signatures_validated": 0,
            "signature_failures": 0,
            "key_rotation_due": False,
            "last_key_rotation": None,
            "encrypted_items": 0,
            "components": {}
        }

# backend/learning_systems/learning_loop.py
class LearningLoop:
    async def get_recent_retrospectives(self, limit: int = 20):
        return []
```

## Step 3: Frontend Integration

### Option A: Use Unified Dashboard (Recommended)

In your main app file (e.g., `frontend/src/App.tsx`):

```tsx
import { UnifiedDashboard } from './pages/UnifiedDashboard';

function App() {
  return <UnifiedDashboard />;
}
```

### Option B: Use Individual Dashboards

```tsx
import { Layer1OpsConsole } from './pages/Layer1OpsConsole';
import { Layer2HTMConsole } from './pages/Layer2HTMConsole';
import { Layer3IntentLearning } from './pages/Layer3IntentLearning';
import { Layer4DevOSView } from './pages/Layer4DevOSView';

function App() {
  const [view, setView] = useState('ops');
  
  return (
    <div>
      {view === 'ops' && <Layer1OpsConsole />}
      {view === 'htm' && <Layer2HTMConsole />}
      {view === 'learning' && <Layer3IntentLearning />}
      {view === 'dev' && <Layer4DevOSView />}
    </div>
  );
}
```

## Step 4: Start Services

### Backend:
```bash
cd backend
python serve.py
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Step 5: Verify Installation

1. **Check Backend API**:
   - Visit `http://localhost:8000/docs`
   - Verify `/api/telemetry/*` endpoints appear

2. **Check WebSocket**:
   - Open browser dev tools → Network → WS tab
   - Verify connection to `ws://localhost:8000/ws/telemetry`

3. **Check Dashboards**:
   - Visit frontend (usually `http://localhost:5173`)
   - Navigate through Layer 1-4 views
   - Verify data loads (or shows "no data" gracefully)

## Step 6: Connect Real Data

Replace stub implementations with real system integrations:

### Example: Connect Real Kernel Data

```python
# backend/kernels/kernel_registry.py
class KernelRegistry:
    async def get_all_kernels(self):
        # Query actual kernel status from your system
        async with get_session() as session:
            result = await session.execute(select(Kernel))
            return result.scalars().all()
```

### Example: Connect Real HTM Queue

```python
# backend/memory_services/htm_queue.py
class HTMQueue:
    async def get_queue_metrics(self):
        async with get_session() as session:
            # Query real HTM task metrics
            result = await session.execute(
                select(
                    func.count(HTMTask.id).label("depth"),
                    func.sum(func.cast(HTMTask.status == "pending", int)).label("pending"),
                    func.sum(func.cast(HTMTask.status == "active", int)).label("active")
                )
            )
            stats = result.first()
            return {
                "depth": stats.depth or 0,
                "pending": stats.pending or 0,
                "active": stats.active or 0,
                # ... add more metrics
            }
```

## Step 7: Test with Stress Suite

### Run a Kernel Stress Test:

**Option 1 - From UI**:
1. Open Layer 1 Ops Console
2. Find a kernel in the table
3. Click **⚡ Stress** button
4. Watch metrics update in real-time

**Option 2 - From API**:
```bash
curl -X POST "http://localhost:8000/api/telemetry/kernels/{kernel_id}/control?action=stress"
```

### Verify Dashboard Updates:

- **Layer 1**: Stress scores increase
- **Layer 2**: HTM queue depth grows
- **Layer 3**: New intents may be created
- **Layer 4**: System logs activity

---

## Troubleshooting

### "Module not found" errors:
- Ensure all dashboard files are in `frontend/src/pages/`
- Check import paths match file locations

### "API endpoint not found":
- Verify `telemetry_api.router` is registered in app
- Check FastAPI app is running on correct port
- Review `http://localhost:8000/docs` for available endpoints

### Empty dashboards:
- Check browser console for API errors
- Verify `API_BASE` constant in dashboard components
- Ensure CORS is configured correctly
- Check database has sample data

### WebSocket not connecting:
- Verify `telemetry_ws.router` is registered
- Ensure `start_telemetry_broadcaster()` is called on startup
- Check firewall/proxy allows WebSocket connections

---

## Next Steps

1. **Customize Views**: Modify dashboard components to match your needs
2. **Add Metrics**: Extend telemetry API with additional endpoints
3. **Set Alerts**: Add threshold alerts for critical metrics
4. **Deploy**: Configure for production (auth, SSL, scaling)
5. **Monitor**: Set up logging and error tracking

For detailed documentation, see [TELEMETRY_DASHBOARD_GUIDE.md](./TELEMETRY_DASHBOARD_GUIDE.md)
