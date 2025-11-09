# Coding Agent Endpoints - All Available

## ✅ Coding Agent IS Active!

**Base Path:** `/api/code`  
**Tag:** `coding_agent`  
**Status:** Registered in main.py line 532  
**Auth:** Required for all endpoints  

---

## Available Endpoints (16 total)

### 1. Parse Codebase
**POST** `/api/code/parse`
- Parse entire codebase
- Extract structure, functions, classes
- Build code graph

### 2. Analyze Context
**POST** `/api/code/context`
- Analyze code context at cursor
- Get relevant symbols
- Understand current file

### 3. Get Suggestions
**POST** `/api/code/suggestions`
- Code completion suggestions
- Context-aware recommendations

### 4. Understand Intent
**POST** `/api/code/intent`
- Parse coding intent from description
- Plan implementation

### 5. Generate Function
**POST** `/api/code/generate/function`
- Generate function from description
- Use learned patterns

### 6. Generate Class
**POST** `/api/code/generate/class`
- Generate class structure
- Apply best practices

### 7. Generate Module
**POST** `/api/code/generate/module`
- Generate complete module
- Multiple functions/classes

### 8. Create Task
**POST** `/api/code/tasks`
- Create coding task
- Plan implementation

### 9. Get Task Progress
**GET** `/api/code/tasks/{task_id}`
- Check task progress
- View results

### 10. Find Related Code
**POST** `/api/code/related`
- Find related code sections
- Semantic code search

### 11. Get Patterns
**GET** `/api/code/patterns`
- View learned code patterns
- Common solutions

### 12. Create Orchestration Plan
**POST** `/api/code/orchestrate/plan`
- Plan complex coding task
- Multi-step orchestration

### 13. Execute Orchestration
**POST** `/api/code/orchestrate/execute`
- Execute coding plan
- Generate full solution

### 14. Code Understanding
**POST** `/api/code/understand`
- Deep code analysis
- Explain code behavior

### 15. Code Refactor
**POST** `/api/code/refactor`
- Suggest refactoring
- Improve code quality

### 16. Code Status
**GET** `/api/code/status`
- Get coding agent status
- View metrics

---

## Why You Don't See It

### Issue: Authentication Required
All coding agent endpoints require auth token:
```bash
curl http://localhost:8000/api/code/parse
# Returns: {"detail":"Not authenticated"}
```

### Solution: Use Auth Token
```bash
# 1. Login first
curl -X POST http://localhost:8000/api/auth/login \
  -d '{"username":"admin","password":"admin123"}'
# Response: {"access_token":"xxx","token_type":"bearer"}

# 2. Use token
curl -X POST http://localhost:8000/api/code/parse \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"code":"def test(): pass","language":"python"}'
```

---

## Access via Frontend

The GraceOrb interface should handle auth automatically.

### Through Code Kernel:
```typescript
// Use the Code Kernel (no direct auth needed)
const response = await http.post('/kernel/code', {
  intent: "Parse this Python code and explain it",
  context: { code: "def hello(): return 'world'" }
});

// Kernel handles:
// - Auth
// - Calling /api/code/parse internally
// - Returning results
```

---

## Verification

### Check Registration:
```bash
# Check main.py line 532
findstr "coding_agent_api" backend\main.py
# Output: app.include_router(coding_agent_api.router)
```

### Check Routes:
```powershell
# List all coding agent routes
python -c "from backend.main import app; routes = [r for r in app.routes if 'code' in str(r.path)]; print('\n'.join([f'{r.path}' for r in routes]))"
```

---

## Solution: Use Code Kernel Instead

The **Code Kernel** wraps all coding agent functionality with intelligent orchestration:

```bash
# Code Kernel (no auth barrier)
curl -X POST http://localhost:8000/kernel/code \
  -d '{"intent":"Generate a REST API endpoint for users"}'

# Kernel internally calls:
# - /api/code/intent (with system auth)
# - /api/code/generate/* (with system auth)
# - /api/sandbox/run (with system auth)
# Returns intelligent response
```

---

## All 16 Coding Agent Endpoints ARE Active

✅ Registered in main.py  
✅ Available at `/api/code/*`  
✅ Visible in API docs (tag: `coding_agent`)  
✅ Require authentication  
✅ Accessible via Code Kernel  

**The coding agent is running - just use the Code Kernel or authenticate!** 🎯
