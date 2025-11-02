# Grace CLI - Quick Start Guide

Get up and running with Grace CLI in 5 minutes.

## Prerequisites

- Python 3.9+
- Grace backend running at http://localhost:8000

## 3-Step Installation

### Step 1: Install Dependencies

```bash
cd grace_rebuild/cli
pip install -r requirements.txt
```

### Step 2: Start Backend

```bash
# In a separate terminal
cd grace_rebuild
python -m uvicorn backend.main:app --reload
```

Verify it's running: http://localhost:8000/health

### Step 3: Run CLI

```bash
python enhanced_grace_cli.py
```

## First Time Setup

1. **Create Account**
   - Choose "register"
   - Enter username (e.g., "alice")
   - Enter password

2. **Login**
   - CLI automatically logs you in
   - Token saved securely

3. **Ready!**
   - You're now at the main menu

## 5-Minute Tour

### 1. Chat with Grace (30 seconds)

```
Choice: 1
You: Hello Grace, what can you do?
Grace: [responds with capabilities]
Type 'exit' to return
```

### 2. Create a Task (30 seconds)

```
Choice: 2
Select: Create new task
Title: Test Grace CLI
Priority: medium
✓ Task created!
```

### 3. Ingest Knowledge (1 minute)

```
Choice: 3
Select: Ingest URL
URL: https://en.wikipedia.org/wiki/Artificial_intelligence
Trust score: [press Enter for auto]
✓ Successfully ingested!
```

### 4. View Security (30 seconds)

```
Choice: 4
[See security dashboard with alerts]
```

### 5. Browse Files (30 seconds)

```
Choice: 7
[Navigate directory tree]
Open file: README.md
[View with syntax highlighting]
```

## Common Commands

| Action | Steps |
|--------|-------|
| Chat | Menu → 1 → Type message |
| Create Task | Menu → 2 → Create new task |
| Search Knowledge | Menu → 3 → Search |
| View Alerts | Menu → 4 |
| Check Audit Log | Menu → 6 |
| Browse Files | Menu → 7 |
| Settings | Menu → 10 |
| Help | Menu → 11 |
| Exit | Menu → 12 |

## Testing the CLI

```bash
# Run all tests
python -m pytest tests/ -v

# Windows users
run_tests.bat
```

Expected: All tests pass ✅

## Configuration

Edit `~/.grace/config.yaml` to customize:

```yaml
backend_url: http://localhost:8000
theme: dark
auto_login: true  # Enable auto-login
```

## Troubleshooting

### "Backend not available"

**Fix**: Start the backend
```bash
cd grace_rebuild
python -m uvicorn backend.main:app --reload
```

### "Module not found"

**Fix**: Install dependencies
```bash
pip install -r requirements.txt
```

### "Authentication failed"

**Fix**: Re-register
1. Delete `~/.grace/config.yaml`
2. Restart CLI
3. Choose "register"

## Next Steps

- **Explore all commands** - Try each menu item
- **Read full docs** - See [README.md](README.md)
- **Create a plugin** - Copy [example_github_plugin.py](example_github_plugin.py)
- **Customize settings** - Menu → Settings

## Getting Help

- Type `11` for help menu
- Read [README.md](README.md) for full documentation
- Check [INSTALL.md](INSTALL.md) for installation issues

## Pro Tips

1. **Auto-login**: Set `auto_login: true` in config
2. **Voice**: Install PyAudio for voice commands
3. **Plugins**: Add custom commands in `~/.grace/plugins/`
4. **Workspace**: CLI remembers your last working directory
5. **History**: Chat history is saved

## Example Session

```
┌───────────────────────────────────────┐
│        GRACE AI - Terminal Interface   │
│                                        │
│        Governance • Reflection         │
│        Autonomy • Cognition • Ethics   │
└───────────────────────────────────────┘

✓ Connected to Grace backend
✓ Logged in as alice

Grace AI - Main Menu

 1. 💬 Chat with Grace
 2. 📋 Task Management
 3. 📚 Knowledge Base
 4. 🛡️ Security Alerts
 5. ⚖️ Governance
 6. 🔍 Verification Logs
 7. 💻 File Explorer
 8. 🎤 Voice Interface
 9. 🔌 Plugins
10. ⚙️ Settings
11. ❓ Help
12. 🚪 Exit

Choice: 1

You: Hello!
Grace: Hello! I'm Grace, your AI assistant...

You: exit

Choice: 12
Goodbye! Grace CLI shutting down...
```

Happy exploring with Grace! 🚀
