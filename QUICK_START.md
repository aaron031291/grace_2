# Grace Quick Start Guide

## Starting Grace

### Option 1: Both Backend + Frontend (Recommended)
```batch
start_both.bat
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Option 2: Backend Only
```batch
restart_backend.bat
```

## Chat with Grace

### In Terminal (Direct)

**Windows CMD:**
```batch
chat_with_grace.bat
```

**PowerShell:**
```powershell
.\chat_with_grace.ps1
```

**Or use full path in PowerShell:**
```powershell
C:\Users\aaron\grace_2\chat_with_grace.bat
```

### In Web Browser
1. Start backend: `start_both.bat`
2. Open: http://localhost:5173
3. Use the chat interface

## View System Logs

### See Last 50 Entries from All Systems

**Windows CMD:**
```batch
view_logs.bat
```

**PowerShell:**
```powershell
.\view_logs.ps1
```

This shows:
- 📋 Backend logs
- 🔒 Immutable log (with crypto)
- 🧠 Memory storage
- 🎯 Meta-loop decisions
- 🔐 Cryptographic chain integrity

## Common Issues

### "Term not recognized" in PowerShell

**Problem:**
```
chat_with_grace.bat: The term 'chat_with_grace.bat' is not recognized
```

**Solutions:**

1. **Use `.bat` with `.\` prefix:**
   ```powershell
   .\chat_with_grace.bat
   ```

2. **Or use the PowerShell version:**
   ```powershell
   .\chat_with_grace.ps1
   ```

3. **Or use full path:**
   ```powershell
   C:\Users\aaron\grace_2\chat_with_grace.bat
   ```

4. **Or use CMD instead:**
   ```batch
   cmd
   chat_with_grace.bat
   ```

### Backend Not Running

If you see errors about connection:
1. Make sure backend is running: `start_both.bat`
2. Check http://localhost:8000/health
3. Wait ~30 seconds for full startup

### Virtual Environment Issues

If Python dependencies are missing:
```batch
cd C:\Users\aaron\grace_2
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

## Monitoring Grace

### Health Check
```
http://localhost:8000/health
```

### API Documentation
```
http://localhost:8000/docs
```

### Code Healing Status
```bash
curl http://localhost:8000/api/code-healing/status
```

### Autonomous Systems Status
```bash
curl http://localhost:8000/api/autonomous/improver/status
```

## File Locations

- **Backend Logs**: `logs/backend.log`
- **Database**: `backend/grace.db`
- **Immutable Log**: In database (encrypted)
- **Memory**: In database (with embeddings)
- **Configuration**: `.env`, `config/`

## Grace's Capabilities

When you chat with Grace, she can:
- Generate and analyze code
- Access her memory
- Learn from conversations
- Self-heal from errors
- Execute with governance
- Make autonomous decisions

## Next Steps

1. Start backend: `start_both.bat`
2. Chat with Grace: `.\chat_with_grace.ps1`
3. Ask Grace about her capabilities
4. View logs: `.\view_logs.ps1`
5. Check her autonomous healing: http://localhost:8000/api/code-healing/status

---

**Tip:** Open 2 terminals - one for backend, one for chat with Grace!
