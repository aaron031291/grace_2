# Grace IDE Architecture

## 📁 Directory Structure

```
grace_rebuild/
├── backend/              # Core Grace services
├── grace-frontend/       # Chat & Dashboard UI
├── grace_ide/           # IDE-specific modules
│   ├── api/
│   │   ├── websocket.py      # Real-time communication
│   │   ├── handlers.py       # Message routing
│   │   ├── execution.py      # Multi-language runner
│   │   ├── security.py       # Static analysis
│   │   └── file_ops.py       # File management
│   ├── components/
│   │   ├── module_builder.py
│   │   ├── memory.py
│   │   └── semantic.py
│   ├── utils/
│   │   ├── logging.py
│   │   ├── rate_limit.py
│   │   └── permissions.py
│   └── docs/
├── sandbox/             # Code execution workspace
└── tests/              # Test suite
```

## ⚡ WebSocket Architecture

### Connection Flow
```
Client → ws://localhost:8000/ide/ws?token=JWT
  → Authenticate
  → Create WebSocketClient
  → Register in IDEWebSocketManager
  → Listen for messages
  → Dispatch to handlers
  → Broadcast events via Trigger Mesh
```

### Message Types

**File Operations:**
```json
{
  "type": "file.read",
  "path": "example.py"
}

{
  "type": "file.write",
  "path": "example.py",
  "content": "print('hello')"
}

{
  "type": "file.list"
}
```

**Code Execution:**
```json
{
  "type": "execute.run",
  "command": "python example.py",
  "language": "python",
  "file_name": "example.py"
}
```

**Security Scanning:**
```json
{
  "type": "security.scan",
  "path": "example.py",
  "content": "..."
}
```

**Memory Search:**
```json
{
  "type": "memory.search",
  "query": "security protocols",
  "limit": 5
}
```

## 🔐 Security Integration

### Every IDE Operation
```
User action
  → WebSocket message
  → Governance check
  → Hunter scan
  → Execute if allowed
  → Log immutably
  → Broadcast event
```

### Static Analysis
- Dangerous pattern detection (eval, exec, rm -rf)
- Secret exposure scanning
- Dependency vulnerability checks
- Risk score calculation (0-10)

### Recommendations
- **Risk 8-10:** CRITICAL - Block execution
- **Risk 5-7:** HIGH - Review required
- **Risk 2-4:** MEDIUM - Caution
- **Risk 0-1:** LOW - Safe

## 🚀 Multi-Language Support

### Supported Languages
- **Python** - python / python3
- **JavaScript** - node
- **TypeScript** - ts-node
- **Bash/Shell** - bash / sh

### Adding New Languages
```python
# In execution.py
LANGUAGE_RUNNERS = {
    "rust": "cargo run",
    "go": "go run",
    "java": "java",
}
```

## 🔄 Integration Points

### With Backend Services
- **Sandbox Manager** - File operations
- **Governance** - Policy enforcement
- **Hunter** - Threat detection
- **Remedy Engine** - Auto-fix suggestions
- **Trigger Mesh** - Event broadcasting

### With Frontend
- **Monaco Editor** - Code editing
- **WebSocket Client** - Real-time communication
- **Issue Panel** - Auto-fix display
- **Console** - Execution output

## 📊 Current Features

✅ Real-time WebSocket communication
✅ Multi-language code execution
✅ Static security analysis
✅ Governed file operations
✅ Integrated with all Grace subsystems
✅ Complete audit trail
✅ Auto-fix suggestions

## 🎯 Usage

### Via Frontend IDE
1. Click **💻 IDE** button
2. Write code in Monaco
3. Click **▶ Run**
4. WebSocket sends execution request
5. Backend processes (governed)
6. Results streamed back
7. Issues detected automatically
8. One-click fixes available

### Via WebSocket Directly
```javascript
const ws = new WebSocket(`ws://localhost:8000/ide/ws?token=${token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.send(JSON.stringify({
  type: 'execute.run',
  command: 'python test.py'
}));
```

Grace IDE is fully integrated and production-ready! 💻🚀
