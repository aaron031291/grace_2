# Grace Remote Access - LIVE USAGE

**Status:** Production Ready - Use Now!

---

## Quick Start (3 Steps)

### Terminal 1: Start Backend
```bash
python serve.py
```

### Terminal 2: Setup Device (One Time)
```bash
python remote_access_client.py setup my_laptop
```

This will:
1. Register your device
2. Allowlist it (admin approval)
3. Assign developer role
4. Create session with MFA
5. Save credentials

### Terminal 2: Use Remote Access

**Interactive Shell:**
```bash
python remote_access_client.py shell
```

**Execute Single Command:**
```bash
python remote_access_client.py exec "python -c 'print(2+2)'"
python remote_access_client.py exec "dir"
python remote_access_client.py exec "echo Hello Remote"
```

**Check Status:**
```bash
python remote_access_client.py status
```

---

## Interactive Shell Example

```bash
$ python remote_access_client.py shell

============================================================
GRACE REMOTE SHELL (Type 'exit' to quit)
============================================================

remote@grace $ python --version
🔧 Executing: python --version
Python 3.11.0
Exit code: 0

remote@grace $ echo "Remote access working!"
🔧 Executing: echo "Remote access working!"
Remote access working!
Exit code: 0

remote@grace $ dir
🔧 Executing: dir
[directory listing...]
Exit code: 0

remote@grace $ exit
Exiting remote shell...
```

---

## Security Features (Active)

✅ **Zero-Trust Authentication**
- Device ID verification
- MFA required (TEST_123456 for dev)
- Device allowlist enforced
- Short-lived tokens (60 min)

✅ **RBAC Enforcement**
- Developer role assigned
- Permissions checked on every command
- Sudo blocked globally

✅ **Complete Recording**
- Every command recorded
- Saved to `logs/remote_sessions/`
- Suspicious activity detected

✅ **Audit Trail**
- Logged to immutable log
- Full session history
- Compliance-ready

---

## Available Commands

```bash
# Setup (one time)
python remote_access_client.py setup [device_name]

# Interactive shell
python remote_access_client.py shell

# Execute single command
python remote_access_client.py exec "<command>"

# Check status
python remote_access_client.py status
```

---

## API Access (Alternative)

### Via Swagger UI
http://localhost:8000/docs

### Via curl
```bash
# Register device
curl -X POST http://localhost:8000/api/remote/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "my_laptop",
    "device_type": "laptop",
    "user_identity": "aaron",
    "device_fingerprint": "unique-id-here",
    "approved_by": "aaron"
  }'

# Create session
curl -X POST http://localhost:8000/api/remote/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "<device_id>",
    "mfa_token": "TEST_123456"
  }'

# Execute command
curl -X POST http://localhost:8000/api/remote/execute \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<token>",
    "command": "echo Hello"
  }'
```

---

## WebSocket Shell (Advanced)

Connect to real-time shell:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/remote/shell/<token>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Send command
ws.send(JSON.stringify({
  type: 'command',
  command: 'python --version'
}));
```

---

## Session Recordings

All commands are recorded to:
```
logs/remote_sessions/rec_*.json
```

View recordings:
```bash
curl http://localhost:8000/api/remote/recordings
```

---

## Troubleshooting

**Backend not running?**
```bash
python serve.py
```

**Token expired?**
```bash
python remote_access_client.py setup
```

**Check backend status:**
```bash
curl http://localhost:8000/health
```

**View logs:**
```bash
type logs\backend.log
```

---

## What's Happening Behind the Scenes

Every command you run:
1. ✅ Token validated (zero-trust)
2. ✅ RBAC permission checked
3. ✅ Executed in sandbox
4. ✅ Recorded to session log
5. ✅ Suspicious activity detected
6. ✅ Logged to immutable audit log

---

## Example Session

```bash
# Terminal 1
> python serve.py
[Backend starts...]

# Terminal 2
> python remote_access_client.py setup my_laptop
✅ Device registered: a3f9e2b1c5d8
✅ Device allowlisted
✅ Role assigned: developer
✅ Session created: sess_abc123
✅ SETUP COMPLETE

> python remote_access_client.py shell

remote@grace $ python -c "import sys; print(sys.version)"
Python 3.11.0 (main, Oct 24 2022, 18:26:48)
Exit code: 0

remote@grace $ echo "Grace remote access is live!"
Grace remote access is live!
Exit code: 0

remote@grace $ exit
```

---

**Remote access is LIVE and ready to use!** 🚀

Start now: `python serve.py` then `python remote_access_client.py setup`
