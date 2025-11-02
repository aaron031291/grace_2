# Grace Testing & Verification Guide

## What's Been Added

✅ **Metrics Endpoint** - `/api/metrics/summary` and `/api/metrics/user/{username}`
✅ **Reflection Loop** - Background task that analyzes conversations every 2 minutes
✅ **Reflections API** - `/api/reflections/` to view Grace's self-observations
✅ **Pytest Suite** - Comprehensive tests for all endpoints

## Test Memory Persistence

### 1. Chat with Grace and ask for history

In the UI at http://localhost:5173, send these messages:
1. "Hello Grace!"
2. "How are you?"
3. "Show me my history"

Grace should respond with your last 5 interactions from the database!

### 2. Test via API

```bash
# Login first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Copy the token from response, then:
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d "{\"message\":\"show me my history\"}"
```

## Test Metrics Endpoint

### Get overall metrics

```bash
curl http://localhost:8000/api/metrics/summary
```

Response:
```json
{
  "total_messages": 10,
  "active_users": 1,
  "registered_users": 1
}
```

### Get user-specific stats

```bash
curl http://localhost:8000/api/metrics/user/admin
```

Response:
```json
{
  "username": "admin",
  "total_messages": 10,
  "grace_responses": 5,
  "user_messages": 5
}
```

## Test Reflection System

The reflection engine runs every 2 minutes automatically and analyzes conversation patterns.

### View your reflections

```bash
# Login and get token first
curl http://localhost:8000/api/reflections/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Trigger immediate reflection

```bash
curl -X POST http://localhost:8000/api/reflections/trigger \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
{
  "status": "created",
  "reflection": "Reflection: User 'admin' has been discussing 'hello' frequently (3 times in recent messages). Total messages analyzed: 10"
}
```

## Run Automated Tests

### Install test dependencies

```bash
py -m pip install pytest pytest-asyncio httpx
```

### Run all tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_chat.py::test_health_check PASSED
tests/test_chat.py::test_register PASSED
tests/test_chat.py::test_login PASSED
tests/test_chat.py::test_chat_basic PASSED
tests/test_chat.py::test_chat_history PASSED
tests/test_chat.py::test_metrics PASSED
```

### Run with coverage

```bash
py -m pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html
```

## How the Reflection Loop Works

1. **Background Task**: Runs every 2 minutes (configurable)
2. **Analyzes**: Last 10 messages per user
3. **Identifies**: Common topics (tasks, history, greetings, etc.)
4. **Stores**: Reflection notes in `reflections` table
5. **Serves**: Via `/api/reflections/` endpoint

### Example Reflection Output

After chatting for a while, Grace creates observations like:
- "User 'admin' has been discussing 'task' frequently (5 times in recent messages)"
- "User 'admin' has been discussing 'history' frequently (3 times in recent messages)"

These can later be used to:
- Suggest proactive actions
- Identify user patterns
- Improve response quality
- Surface in dashboards

## Database Schema

### Tables Created

1. **users** - User accounts
2. **chat_messages** - All conversation history
3. **reflections** - Grace's self-observations

### View database

```bash
py -m pip install sqlite-web
sqlite_web grace.db
```

Visit http://localhost:8080 to browse the database.

## API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Create user
- `POST /api/auth/login` - Get JWT token

### Chat
- `POST /api/chat/` - Send message (requires auth)

### Metrics
- `GET /api/metrics/summary` - Overall stats
- `GET /api/metrics/user/{username}` - User-specific stats

### Reflections
- `GET /api/reflections/` - View reflections (requires auth)
- `POST /api/reflections/trigger` - Force immediate reflection (requires auth)

### System
- `GET /health` - Health check
- `GET /docs` - Auto-generated API docs

## Next Steps

1. ✅ Memory persistence verified
2. ✅ Metrics tracking
3. ✅ Reflection loop running
4. ✅ Test suite ready

**Now you can:**
- Add more sophisticated reflection patterns
- Create a dashboard to visualize metrics
- Implement task management based on reflections
- Add causal reasoning to the reflection loop
- Build recursive self-improvement cycles

The foundation is solid for advanced autonomous features! 🚀
