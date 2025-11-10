# Grace - Quick Access Guide

## 🚀 IMMEDIATE ACCESS

### Frontend (Web UI)
Open your browser: **http://localhost:5173**

Expected: React frontend with Grace dashboard

---

### Backend API
Open your browser: **http://localhost:8000/docs**

Expected: FastAPI Swagger UI with all endpoints

Health check: **http://localhost:8000/health**

---

### CLI (Command Line Interface)

**Option 1: Enhanced Interactive CLI**
```bash
cd cli
.venv\Scripts\python enhanced_grace_cli.py
```

**Option 2: Unified Domain CLI**
```bash
cd cli
.venv\Scripts\python grace_unified.py --help
```

**Option 3: Windows Batch Launcher**
```bash
cd cli
grace.bat
```

---

## 📋 CLI Quick Commands

### Interactive Mode (Recommended for Testing)
```bash
cd C:\Users\aaron\grace_2\cli
python enhanced_grace_cli.py
```

**First Time:**
1. Register new account (username/password)
2. Auto-login
3. Choose from menu:
   - `1` - Chat with Grace
   - `2` - Task Management
   - `3` - Knowledge Base
   - `4` - Security Alerts
   - `7` - File Explorer

---

### Domain CLI Mode (Advanced)
```bash
cd C:\Users\aaron\grace_2\cli

# View cognition dashboard
python grace_unified.py cognition

# Check readiness
python grace_unified.py readiness

# Chat with Grace
python grace_unified.py core heartbeat

# Knowledge ingestion
python grace_unified.py knowledge search "artificial intelligence"

# Security scan
python grace_unified.py security alerts
```

---

## 🔧 Services Status Check

### Check if Backend is Running
```bash
curl http://localhost:8000/health
```
Expected response: `{"status": "ok", ...}`

### Check if Frontend is Running
```bash
curl http://localhost:5173
```
Expected: HTML response

### Check Ports
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

---

## 🎯 Testing Grace Functionality

### 1. Web UI Test (EASIEST)
1. Open **http://localhost:5173**
2. Login/register
3. Explore dashboards:
   - Knowledge ingestion
   - Meta loop monitoring
   - Security alerts
   - Business metrics
   - Transcendence IDE

### 2. API Test
1. Open **http://localhost:8000/docs**
2. Try endpoints:
   - `GET /health` - Health check
   - `POST /api/auth/register` - Create account
   - `POST /api/auth/login` - Get token
   - `GET /api/cognition/metrics` - View metrics

### 3. CLI Test
```bash
cd C:\Users\aaron\grace_2\cli
python enhanced_grace_cli.py

# Interactive session:
# 1. Register (username: test, password: test123)
# 2. Main menu -> 1 (Chat)
# 3. Type: "Hello Grace, what can you do?"
# 4. Type: exit
# 5. Main menu -> 3 (Knowledge)
# 6. Ingest URL or search
```

---

## 🐛 Troubleshooting

### Backend Not Responding
```bash
# Check if running
tasklist | findstr python

# Restart backend
cd C:\Users\aaron\grace_2
.venv\Scripts\activate
uvicorn backend.main:app --reload
```

### Frontend Not Responding
```bash
# Check if running
tasklist | findstr node

# Restart frontend
cd C:\Users\aaron\grace_2\frontend
npm run dev
```

### CLI Errors
```bash
# Install CLI dependencies
cd C:\Users\aaron\grace_2\cli
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

---

## 📊 Grace Features to Test

### Knowledge System
- Ingest URLs, PDFs, text
- Search knowledge base
- View trust scores
- Business intelligence queries

### Agentic Capabilities
- Task planning
- Code generation
- Memory search
- Transcendence IDE

### Governance & Meta Loop
- Approval workflows
- Meta-loop recommendations
- Constitutional AI
- Parliament decisions

### Security (Hunter)
- Security rule management
- Alert monitoring
- Quarantine system
- Threat detection

### Observability
- Cognition metrics
- Health monitoring
- Performance dashboards
- Self-healing logs

---

## 🎬 Recommended Test Sequence

1. **Verify Services Running**
   - Check http://localhost:8000/health
   - Check http://localhost:5173

2. **Test Frontend**
   - Register account
   - Navigate dashboards
   - Try knowledge ingestion

3. **Test CLI**
   - Run `python enhanced_grace_cli.py`
   - Chat with Grace
   - Browse files

4. **Test Integration**
   - Ingest knowledge via CLI
   - View in web dashboard
   - Check cognition metrics

---

## 💡 Pro Tips

1. **Keep terminals open** - Backend and frontend need to stay running
2. **Use web UI first** - Easiest way to see everything
3. **Check /docs** - Interactive API documentation
4. **Monitor logs** - Watch backend terminal for activity
5. **Start simple** - Try health check, then chat, then advanced features

---

## 🚨 If Nothing Works

### Nuclear Option - Fresh Start
```bash
# Kill all services
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Restart backend
cd C:\Users\aaron\grace_2
.venv\Scripts\activate
uvicorn backend.main:app --reload

# In new terminal - Restart frontend
cd C:\Users\aaron\grace_2\frontend
npm run dev

# Wait 10 seconds, then try http://localhost:5173
```

---

**Ready to test? Start here:** http://localhost:5173
