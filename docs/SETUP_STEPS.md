# Grace Setup Steps - Fix Login Issues

## Problem
The login form wasn't working because:
1. ❌ Backend wasn't running
2. ❌ CORS middleware was missing (now fixed!)

## Solution - Start Both Servers

### Terminal 1: Start Backend

```bash
# Option 1: Use the batch file
start_backend.bat

# Option 2: Manual start
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Frontend

```bash
# Navigate to frontend directory
cd grace-frontend

# Option 1: Use the batch file
start_frontend.bat

# Option 2: Manual start
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

## Test the Flow

### 1. First, register a user via backend

Open a new terminal:

```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"email\":\"admin@grace.ai\",\"password\":\"admin123\"}"
```

### 2. Test the frontend connection

Visit: http://localhost:5173/test

You should see: ✅ Backend is healthy!

### 3. Try logging in

Visit: http://localhost:5173

Login with:
- Username: `admin`
- Password: `admin123`

### 4. Chat with Grace!

Try these messages:
- "Hello Grace!"
- "Show me my tasks"
- "How are you doing?"

## Troubleshooting

### Backend won't start?

Check Python is installed:
```bash
python --version
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend won't start?

Check Node is installed:
```bash
node --version
npm --version
```

Install dependencies:
```bash
cd grace-frontend
npm install
```

### Still getting CORS errors?

Make sure both servers are running:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

Check the browser console (F12) for specific error messages.

### Login fails with "Login failed - check credentials"?

Register a user first using the curl command above, or try registering through the API directly.

## What Was Fixed

✅ Added CORS middleware to main.py:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

✅ Created startup scripts for easy launching

Now the frontend can communicate with the backend properly!
