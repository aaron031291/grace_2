# Grace AI Coding Agent - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Seed Grace's Memory (1 min)
```bash
cd grace_rebuild/backend
python seed_code_memory.py
```

### Step 2: Start Server (30 sec)
```bash
run_coding_agent_demo.bat
```
Or:
```bash
python -m uvicorn main:app --reload
```

### Step 3: Try It! (1 min)
Visit: http://localhost:8000/docs

---

## 📋 Common Tasks

### Generate a Function
```bash
POST /api/code/generate/function
{
  "name": "calculate_tax",
  "description": "Calculate tax amount",
  "parameters": [
    {"name": "price", "type": "float"},
    {"name": "tax_rate", "type": "float"}
  ],
  "return_type": "float"
}
```

### Generate a Class
```bash
POST /api/code/generate/class
{
  "name": "UserService",
  "description": "Handle user operations",
  "attributes": [{"name": "db", "type": "Database"}],
  "methods": [
    {
      "name": "get_user",
      "params": [{"name": "user_id", "type": "int"}],
      "return_type": "User"
    }
  ]
}
```

### Generate Tests
```bash
POST /api/code/generate/tests
{
  "code": "def my_function():\n    return True",
  "framework": "pytest"
}
```

### Search Patterns
```bash
GET /api/code/patterns?query=authentication&limit=5
```

### Submit a Task
```bash
POST /api/code/task
{
  "description": "implement user login with JWT authentication"
}
```

### Get Suggestions
```bash
POST /api/code/suggest
{
  "file_path": "backend/api.py",
  "cursor_position": {"line": 45, "column": 10}
}
```

---

## 🔑 API Authentication

All endpoints require JWT token:

```bash
# 1. Login first
POST /api/auth/login
{
  "username": "your_username",
  "password": "your_password"
}

# 2. Use token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/code/patterns?query=test
```

---

## 💡 Quick Tips

1. **Seed Often** - Run `seed_code_memory.py` to keep patterns fresh
2. **Be Specific** - Detailed descriptions = better code
3. **Review Output** - Always review generated code
4. **Track Tasks** - Use `/task/{id}/progress` to monitor
5. **Use Context** - Provide file/framework info for better results

---

## 📊 Check Status

### Pattern Count
```sql
SELECT COUNT(*) FROM code_patterns;
```

### Top Patterns
```bash
GET /api/code/patterns?query=&limit=10
```

### Task Progress
```bash
GET /api/code/task/{task_id}/progress
```

---

## 🐛 Troubleshooting

**No patterns found?**
→ Run `seed_code_memory.py`

**Server won't start?**
→ Check if port 8000 is free

**Bad code quality?**
→ Provide more detailed specs

**Auth error?**
→ Get fresh JWT token from `/api/auth/login`

---

## 📚 More Info

- Full Docs: `CODING_AGENT.md`
- Status Report: `CODING_AGENT_STATUS.md`
- Tests: `tests/test_coding_agent.py`
- API Docs: http://localhost:8000/docs

---

## 🎯 Example Workflow

```python
# 1. Understand intent
intent = await code_understanding.understand_intent(
    "add password reset to user API"
)

# 2. Get patterns
patterns = await code_memory.recall_patterns(
    intent="password reset",
    limit=5
)

# 3. Generate code
func = await code_generator.generate_function({
    'name': 'reset_password',
    'description': 'Reset user password',
    'parameters': [
        {'name': 'email', 'type': 'str'},
        {'name': 'new_password', 'type': 'str'}
    ]
})

# 4. Generate tests
tests = await code_generator.generate_tests(
    code=func['code'],
    framework='pytest'
)

# 5. Verify
scan = await hunter.scan_code_snippet(func['code'])
```

Done! 🎉
