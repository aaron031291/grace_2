# Grace Rebuild - Clean Architecture

Modern implementation of Grace with proper async support, clean separation of concerns, and persistent memory.

## Backend Structure

```
backend/
├── __init__.py
├── main.py              # FastAPI app + startup
├── models.py            # SQLAlchemy models (User, ChatMessage)
├── memory.py            # PersistentMemory class
├── grace.py             # GraceAutonomous core
├── auth.py              # JWT auth utilities
└── routes/
    ├── __init__.py
    ├── auth_routes.py   # /api/auth/register, /api/auth/login
    └── chat.py          # /api/chat
```

## Setup

### Backend

```bash
cd grace_rebuild
py -m pip install -r requirements.txt
```

### Run Backend

```bash
uvicorn backend.main:app --reload
```

Server runs at: http://localhost:8000

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Chat (requires token)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d "{\"message\":\"Hello Grace!\"}"
```

## Frontend (Next Step)

Will be created as a separate Vite + React + TypeScript app that connects to this backend.

## Key Features

- ✅ Async SQLAlchemy with SQLite
- ✅ JWT authentication
- ✅ Persistent chat memory
- ✅ GraceAutonomous with deterministic responses
- ✅ Clean route separation
- ✅ CORS enabled for frontend
