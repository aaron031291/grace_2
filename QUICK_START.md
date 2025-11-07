# Quick Start - Grace AI System

## ✅ Database Lock Fixed!

The database is now ready:
- ✅ Lock files cleared
- ✅ WAL mode enabled
- ✅ 30-second timeout configured
- ✅ Database backed up

## Start Grace Now

### Terminal 1: Backend
```bash
start_grace_clean.bat
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

## Access Grace

- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **Frontend**: http://localhost:5173
- **GPT Chat**: http://localhost:5173 → Login → Click "⚡ GPT Chat"

**Login**: `admin` / `admin123`

## You Should See

```
✓ Database initialized (WAL mode enabled)
✓ Trigger Mesh started
✓ All systems started

🤖 ==================== ADVANCED AI SYSTEMS ====================
🎯 Starting Shard Orchestrator...
  ✓ Initialized 6 shards
✓ Orchestrator started with 6 shards

🛡️ Starting Input Sentinel...
✓ Input Sentinel active - monitoring errors in real-time

📚 Loading expert AI knowledge into Grace...
✓ AI expertise preloaded successfully

GRACE AGENTIC SPINE - AUTONOMOUS ACTIVATION
✓ GRACE is now autonomous
```

## Test Grace's Capabilities

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

### 2. View Autonomy Status
```bash
curl http://localhost:8000/api/autonomy/status
```

### 3. Check Shard Status
```bash
curl http://localhost:8000/api/autonomy/shards/status
```

### 4. Use GPT Chat UI
- Go to http://localhost:5173
- Login with admin/admin123
- Click "⚡ GPT Chat"
- Press `/` to see slash commands
- Try: `/self_heal`, `/meta`, `/status`

## What Grace Can Do Now

✅ Instant error detection & autonomous resolution  
✅ Multi-agent parallel execution (6 shards)  
✅ Expert AI knowledge (5 packs, ~100 entities)  
✅ 3-tier governed autonomy  
✅ Git commit workflow with approval  
✅ Continuous learning from every interaction  
✅ Modern GPT-style UI  
✅ Full audit trail & provenance  

## If You See Database Lock Again

```bash
# Quick fix
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"
powershell -Command "Start-Sleep -Seconds 2"
powershell -Command "Remove-Item databases\*.db-wal, databases\*.db-shm -ErrorAction SilentlyContinue"

# Then restart
start_grace_clean.bat
```

## Next Steps

1. **Start Grace** with `start_grace_clean.bat`
2. **Open Frontend** at http://localhost:5173
3. **Test GPT Chat** - Try slash commands
4. **Watch Activity Feed** - See autonomous actions
5. **Submit Tasks** - Test shard orchestration
6. **Trigger Errors** - See agentic resolution

**Grace is ready to run! 🚀**
