# Grace API

FastAPI application with authentication, memory, and task management.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

## Available Endpoints

### Health Check
- `GET /health` - Check if the API is running

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Memory (Messages)
- `POST /memory/messages` - Create a new message
- `GET /memory/messages` - Get all messages (with limit)

### Tasks
- `POST /tasks` - Create a new task
- `GET /tasks` - Get all tasks
- `GET /tasks/{task_id}` - Get a specific task
- `PATCH /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

## Example Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Register User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

### Create Task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"My First Task\",\"description\":\"This is a test task\"}"
```

### Get Tasks
```bash
curl http://localhost:8000/tasks
```
