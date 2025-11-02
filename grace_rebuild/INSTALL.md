# Grace Installation Guide

## 📦 Quick Install

### Option 1: Using pip (Recommended)
```bash
pip install grace-ai
grace install
grace start
```

### Option 2: Docker (Production)
```bash
docker-compose up -d
```

### Option 3: Manual (Development)
```bash
git clone https://github.com/yourusername/grace
cd grace
python grace_cli.py install
python grace_cli.py start
```

## 🔧 Requirements

### System Requirements
- Python 3.11+
- Node.js 18+
- 4GB RAM minimum
- 10GB disk space

### For Docker
- Docker 20.10+
- Docker Compose 2.0+

## 📋 Step-by-Step Installation

### 1. Install Python Dependencies
```bash
cd grace_rebuild
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd grace-frontend
npm install
```

### 3. Initialize Database
```bash
python reset_db.py
```

### 4. Start Services
```bash
# Terminal 1: Backend
python -m uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd grace-frontend
npm run dev
```

## 🐳 Docker Deployment

### Build and Start
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

## 🚀 Using the CLI

### Install Grace
```bash
python grace_cli.py install
```

### Start All Services
```bash
python grace_cli.py start
```

### Check Status
```bash
python grace_cli.py status
```

### Reset Sandbox
```bash
python grace_cli.py sandbox reset
```

### Upgrade
```bash
python grace_cli.py upgrade
```

## 🔐 First-Time Setup

### 1. Create Admin User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_secure_password"}'
```

### 2. Login
Visit http://localhost:5173 and login with your credentials

### 3. Explore
- 💬 **Chat** - Talk with Grace
- 📊 **Dashboard** - View metrics and system status
- 📁 **Memory** - Browse knowledge base

## 🎯 Post-Installation

### Verify Installation
1. Backend health: http://localhost:8000/health
2. API docs: http://localhost:8000/docs
3. Frontend: http://localhost:5173
4. Run tests: `pytest tests/ -v`

### Configure (Optional)
Create `.env` file:
```
DATABASE_URL=sqlite+aiosqlite:///./grace.db
SECRET_KEY=your-secret-key-here
REFLECTION_INTERVAL=10
META_LOOP_INTERVAL=300
```

### Seed Knowledge Base
```bash
curl -X POST http://localhost:8000/api/memory/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "path": "security/protocols.md",
    "content": "# Security Protocols\n...",
    "domain": "security",
    "category": "policy"
  }'
```

## 🔄 Upgrading

### From v0.x to v1.0
```bash
python grace_cli.py upgrade
# Or: git pull && pip install -U -r requirements.txt
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Check logs
python -m uvicorn backend.main:app --log-level debug
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear node_modules
rm -rf grace-frontend/node_modules
cd grace-frontend && npm install
```

### Database errors
```bash
# Reset database
python reset_db.py

# Or manually delete
rm grace.db
python reset_db.py
```

### Port conflicts
```bash
# Change backend port
uvicorn backend.main:app --port 8001

# Change frontend port  
cd grace-frontend
npm run dev -- --port 5174
```

## 📚 Next Steps

1. Read [QUICKSTART.md](QUICKSTART.md) for usage guide
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Explore [META_LOOPS.md](META_LOOPS.md) for self-optimization
4. Check [SELF_HEALING.md](SELF_HEALING.md) for monitoring

## 🆘 Support

- Issues: https://github.com/yourusername/grace/issues
- Docs: http://localhost:8000/docs
- Community: [Discord/Forum link]

Grace is now ready to run! 🚀🤖
