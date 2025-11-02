# Grace - Quick Start Guide

Complete setup for Grace autonomous assistant with FastAPI backend and React frontend.

## Project Structure

```
grace_2/
├── Backend (FastAPI + SQLite)
│   ├── main.py              # FastAPI app with routes
│   ├── grace_core.py        # GraceAutonomous class
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database setup
│   ├── auth.py              # JWT authentication
│   ├── requirements.txt     # Python dependencies
│   └── grace.db            # SQLite database (auto-created)
│
└── grace-frontend/         # React + TypeScript frontend
    ├── src/
    │   ├── App.tsx
    │   └── components/
    │       ├── AuthProvider.tsx
    │       ├── OrbInterface.tsx
    │       └── ConnectionTest.tsx
    └── package.json
```

## Backend Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the backend server

```bash
python main.py
```

Server runs at: http://localhost:8000

### 3. Test backend endpoints

```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"email\":\"admin@grace.ai\",\"password\":\"admin123\"}"

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Chat with Grace
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Hello Grace!\"}"
```

## Frontend Setup

### 1. Install Node dependencies

```bash
cd grace-frontend
npm install
```

### 2. Start the dev server

```bash
npm run dev
```

Frontend runs at: http://localhost:5173

## Usage Flow

### Step 1: Test Backend Connection

1. Open http://localhost:5173/test
2. Verify the backend health check passes

### Step 2: Register & Login

1. Go to http://localhost:5173
2. Register a new account (or use existing credentials)
3. Login with username/password

### Step 3: Chat with Grace

1. After login, you'll see the chat interface
2. Type a message and press Enter or click Send
3. Grace will respond using rule-based logic

**Try these messages:**
- "Hello Grace!"
- "Show me my tasks"
- "How are you?"
- "Create a new task"

## Grace Features

### Rule-Based Responses

Grace uses pattern matching to respond to:
- Greetings (hello, hi, hey)
- Task management (show tasks, create task)
- Status checks (how are you)
- Thanks and goodbyes

### Memory & Persistence

- All conversations stored in SQLite
- Task management with full CRUD
- User authentication with JWT tokens

### Metrics

Access metrics at: http://localhost:8000/chat/metrics

Returns:
- Total messages
- Total tasks
- Completed tasks
- Completion rate

## API Endpoints

### Authentication
- `POST /auth/register` - Create new user
- `POST /auth/login` - Get JWT token

### Chat
- `POST /chat` - Send message to Grace
- `GET /chat/metrics` - Get usage statistics

### Tasks
- `POST /tasks` - Create task
- `GET /tasks` - List all tasks
- `GET /tasks/{id}` - Get specific task
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Memory
- `POST /memory/messages` - Store message
- `GET /memory/messages` - Retrieve message history

## Troubleshooting

### Backend not starting?

Check if Python and dependencies are installed:
```bash
python --version
pip list
```

### Frontend not connecting?

1. Verify backend is running on port 8000
2. Check browser console for CORS errors
3. Visit http://localhost:5173/test for diagnostics

### Database issues?

Delete and recreate:
```bash
rm grace.db
python main.py  # Creates new database
```

## Next Steps

1. ✅ Basic chat working
2. Add more sophisticated NLP
3. Integrate with external APIs
4. Add voice interface
5. Deploy to production

Enjoy chatting with Grace! 🚀
