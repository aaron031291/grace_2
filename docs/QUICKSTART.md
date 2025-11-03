# Grace Rebuild - Quick Start

Clean architecture rebuild with async SQLAlchemy, proper auth, and persistent memory.

## Project Structure

```
grace_rebuild/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + CORS + startup
│   ├── models.py            # User, ChatMessage models
│   ├── memory.py            # PersistentMemory class
│   ├── grace.py             # GraceAutonomous core
│   ├── auth.py              # JWT utilities
│   └── routes/
│       ├── auth_routes.py   # Register/Login
│       └── chat.py          # Chat endpoint
│
└── grace-frontend/
    └── src/
        ├── App.tsx
        └── components/
            ├── AuthProvider.tsx
            ├── OrbInterface.tsx
            └── ConnectionTest.tsx
```

## Setup

### 1. Install Backend Dependencies

```bash
cd grace_rebuild
py -m pip install -r requirements.txt
```

### 2. Start Backend

**Option A: Use batch file**
```bash
start_backend.bat
```

**Option B: Manual**
```bash
uvicorn backend.main:app --reload
```

Backend runs at: **http://localhost:8000**

### 3. Start Frontend

Open a NEW terminal:

```bash
cd grace-frontend
npm run dev
```

Frontend runs at: **http://localhost:5173**

## First Time Usage

### Register a User

Visit http://localhost:5173 and the login form will appear with default credentials.

Or use curl:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

### Login

Use the web interface at http://localhost:5173 or:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

### Chat

After logging in through the web interface, chat with Grace!

Try these messages:
- "Hello Grace!"
- "Show me my history"
- "How are you?"
- "Thank you"

## API Endpoints

### Health
- `GET /health` - Check server status

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Get JWT token

### Chat
- `POST /api/chat/` - Send message (requires Bearer token)

## Features

✅ **Async SQLAlchemy** - Proper async/await with SQLite  
✅ **JWT Authentication** - Secure token-based auth  
✅ **Persistent Memory** - All conversations stored in database  
✅ **GraceAutonomous** - Deterministic rule-based responses  
✅ **Clean Architecture** - Separated routes, models, services  
✅ **CORS Enabled** - Frontend can communicate with backend  

## Database

SQLite database `grace.db` is created automatically on first run.

**Tables:**
- `users` - User accounts with hashed passwords
- `chat_messages` - All chat history with timestamps

## Development

### Backend Hot Reload

The `--reload` flag enables auto-restart on code changes.

### Frontend Hot Module Replacement

Vite provides instant HMR for React components.

### API Documentation

Visit http://localhost:8000/docs for automatic Swagger UI

## Troubleshooting

### Backend won't start?

Check Python version:
```bash
py --version  # Should be 3.9+
```

Install dependencies:
```bash
py -m pip install -r requirements.txt
```

### Frontend won't connect?

1. Verify backend is running on port 8000
2. Check browser console (F12) for errors
3. Visit http://localhost:5173/test to test connection

### Login fails?

Make sure you registered a user first. The backend starts with an empty database.

## Next Steps

1. ✅ Basic chat working
2. Add more sophisticated response patterns to `grace.py`
3. Implement task management
4. Add metrics dashboard
5. Integrate external APIs
6. Deploy to production

Enjoy the clean architecture! 🚀
