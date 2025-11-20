# Fix: OpenAI API Key Not Set ❌ → ✅

## Error Message

```
[FAIL] Boot function failed: The api_key client option must be set either 
by passing api_key to the client or by setting the OPENAI_API_KEY 
environment variable
```

---

## Quick Fix (5 Minutes)

### Option 1: Set in .env File (Recommended)

```bash
# 1. Copy the example file
copy .env.example .env

# 2. Open .env in a text editor
notepad .env

# 3. Add your OpenAI API key:
OPENAI_API_KEY=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

OPENAI_MODEL=gpt-4o

# 4. Save and close

# 5. Restart Grace
python server.py
```

### Option 2: Set Environment Variable

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-actual-key-here
python server.py
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-actual-key-here"
python server.py
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-actual-key-here
python server.py
```

---

## Get OpenAI API Key

### 1. Go to OpenAI Platform
https://platform.openai.com/api-keys

### 2. Sign In
Use your OpenAI account

### 3. Create New Key
- Click "Create new secret key"
- Name it "Grace"
- Copy the key (starts with `sk-`)

### 4. Add to .env
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

⚠️ **Important:** Never commit the .env file to git! It's already in .gitignore.

---

## Verify Setup

### Check .env File Exists

```bash
# Windows
dir .env

# Linux/Mac
ls -la .env
```

Should show `.env` file in the root directory.

### Check Key is Set

**Windows:**
```cmd
findstr OPENAI_API_KEY .env
```

**Linux/Mac:**
```bash
grep OPENAI_API_KEY .env
```

Should show:
```
OPENAI_API_KEY=sk-...
```

### Test Backend Starts

```bash
python server.py
```

Should see:
```
[INFO] Starting Grace API v2.0.0
[INFO] Chat API enabled ✅
[INFO] OpenAI Reasoner initialized ✅
...
[INFO] Server running on http://localhost:8000
```

**No more errors!** ✅

---

## Complete .env Template

```bash
# Minimum required
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# Recommended for development
SEARCH_PROVIDER=mock
DISABLE_AUTH=true

# Optional
SECRET_KEY=change-me-in-production
VITE_BACKEND_URL=http://localhost:8000
```

---

## Still Having Issues?

### Issue 1: "ModuleNotFoundError: openai"

**Fix:**
```bash
pip install openai
```

### Issue 2: ".env file not found"

**Fix:**
```bash
# Create new .env file
echo OPENAI_API_KEY=sk-your-key-here > .env
```

### Issue 3: "Invalid API key"

**Fix:**
- Verify key starts with `sk-`
- Check for extra spaces or quotes
- Generate new key at https://platform.openai.com/api-keys

### Issue 4: Key is set but still failing

**Fix:**
```bash
# Verify environment variable
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# Should print your key
# If None, the .env is not being loaded
```

---

## After Setup

### Test Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Grace!"}'
```

Should return:
```json
{
  "reply": "Hello! I'm Grace...",
  "confidence": 0.95,
  "citations": [...],
  ...
}
```

### Start Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 and chat with Grace! 🎉

---

## Security Notes

⚠️ **Never share your API key**  
⚠️ **Never commit .env to git** (already in .gitignore)  
⚠️ **Rotate keys regularly**  
⚠️ **Use separate keys for dev/prod**

---

**After following this guide, Grace should boot successfully!**
