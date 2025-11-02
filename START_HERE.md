# START HERE - Grace Backend Not Running

You're seeing "localhost refused to connect" because **the backend server is NOT running**.

## Step-by-Step Instructions

### Step 1: Open a terminal in the grace_2 folder

Right-click in the folder → "Open in Terminal" or use Command Prompt/PowerShell

### Step 2: Install dependencies

Run this command (copy and paste):

```bash
python3 -m pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt python-multipart
```

Wait for it to finish installing.

### Step 3: Start the backend server

Run this command:

```bash
python3 main.py
```

You should see output like:
```
Starting Grace API server...
Visit: http://localhost:8000/health
Docs: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**KEEP THIS TERMINAL OPEN** - the server needs to stay running!

### Step 4: Test the backend

Open a NEW terminal and run:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status":"healthy","message":"Grace API is running"}
```

### Step 5: Register a user

In the same terminal, run:

```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin123\"}"
```

### Step 6: Start the frontend (in a SECOND terminal)

Open a NEW terminal, then:

```bash
cd grace-frontend
npm run dev
```

### Step 7: Open browser

Go to: http://localhost:5173

Login with:
- Username: `admin`
- Password: `admin123`

## Quick Checklist

- [ ] Backend terminal is open and running `python3 main.py`
- [ ] You see "Uvicorn running on http://0.0.0.0:8000"
- [ ] You registered a user with curl
- [ ] Frontend terminal is open and running `npm run dev`
- [ ] Browser is at http://localhost:5173

## Still not working?

Tell me:
1. What happens when you run `python3 main.py`?
2. Do you see any error messages?
3. Copy and paste the exact error here
