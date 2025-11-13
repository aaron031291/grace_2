## Librarian Kernel - Integration Checklist

### 1. Install Dependencies

```bash
pip install watchdog  # For filesystem watching
```

### 2. Register API Routes

Edit `serve.py` or main FastAPI application:

```python
from backend.routes import librarian_api, chunked_upload_api

app.include_router(librarian_api.router)
app.include_router(chunked_upload_api.router)
```

### 3. Run Schema Loaders

```bash
# Generate ORM models for new tables
python backend/memory_tables/schema_loader.py

# Should process:
# - memory_upload_manifest.yaml
# - memory_trusted_sources.yaml (from previous implementation)
```

### 4. Initialize Kernel on Startup

Add to `serve.py` startup event:

```python
from backend.kernels.librarian_kernel import LibrarianKernel
from backend.kernels.event_bus import get_event_bus
from backend.memory_tables.registry import table_registry

@app.on_event("startup")
async def startup_event():
    # Initialize event bus
    event_bus = get_event_bus(registry=table_registry)
    
    # Start Librarian kernel
    from backend.routes.librarian_api import _librarian_kernel
    if _librarian_kernel:
        await _librarian_kernel.start()
        print("✅ Librarian Kernel started")
```

### 5. Add UI Panel

Edit `frontend/src/App.tsx` or `MemoryStudioPanel.tsx`:

```typescript
import { LibrarianPanel } from './panels/LibrarianPanel';

// Add tab
<Tab label="Librarian">
  <LibrarianPanel />
</Tab>
```

### 6. Test Endpoints

```bash
# Test kernel control
curl -X POST http://localhost:8000/api/librarian/start
curl http://localhost:8000/api/librarian/status

# Test chunked upload
curl -X POST http://localhost:8000/api/memory/uploads/start \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.pdf",
    "file_size": 1048576,
    "checksum": "abc123",
    "target_folder": "storage/uploads"
  }'
```

### 7. Verify File Watching

```bash
# Create a test file
echo "test content" > grace_training/test.txt

# Check kernel status
curl http://localhost:8000/api/librarian/status
# Should show schema_queue: 1
```

### 8. Test Agent Spawning

```bash
# Manually spawn an agent
curl -X POST http://localhost:8000/api/librarian/spawn-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "schema_scout",
    "task_data": {"path": "grace_training/test.txt"}
  }'

# Check active agents
curl http://localhost:8000/api/librarian/status
# Should show active_agents: 1
```

### 9. Monitor Logs

```bash
# Watch kernel logs
tail -f logs/grace.log | grep -i "librarian\|kernel\|agent"

# Should see:
# - Kernel started
# - File events
# - Agent spawns
# - Job completions
```

### 10. Production Considerations

- [ ] Configure malware scanning (integrate ClamAV)
- [ ] Set up proper file permissions for watched directories
- [ ] Configure upload storage path and cleanup policy
- [ ] Set environment variables for kernel tuning
- [ ] Enable HTTPS for chunked uploads
- [ ] Set up monitoring/alerting for kernel health
- [ ] Configure backup for upload manifests
- [ ] Add rate limiting on upload endpoints

---

## Quick Start Commands

```bash
# 1. Install deps
pip install watchdog

# 2. Run schema loader
python backend/memory_tables/schema_loader.py

# 3. Start server (kernel auto-starts)
python serve.py

# 4. Open UI
# Navigate to Librarian tab in Memory Studio

# 5. Test upload
# Use UI or curl to start chunked upload

# 6. Monitor
curl http://localhost:8000/api/librarian/status
```

---

## Troubleshooting

### Watchdog not installed
```bash
pip install watchdog
```

### Kernel won't start
- Check logs for ImportError
- Verify table_registry initialized
- Ensure watch directories exist

### Agents not spawning
- Check max_concurrent_agents config
- Verify queue has items
- Look for import errors in agent modules

### Upload fails
- Verify storage/upload_chunks directory exists
- Check disk space
- Verify checksum format (SHA-256 hex)

---

**Next**: See [LIBRARIAN_KERNEL_COMPLETE.md](file:///c:/Users/aaron/grace_2/LIBRARIAN_KERNEL_COMPLETE.md) for full documentation
