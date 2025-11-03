# 🔮 Transcendence IDE WebSocket - Quick Reference

## Files Created

| File | Purpose |
|------|---------|
| `backend/ide_websocket_handler.py` | Backend handler (10 operations) |
| `grace_ide/static/websocket_client.js` | Frontend client |
| `tests/test_ide_websocket.py` | Test suite |
| `grace_ide/static/test_ide.html` | Browser test UI |

## 10 Handler Operations

```python
# File Operations
file_open(path)                    # Load file
file_save(path, content)           # Save with verification
file_create(path, content)         # Create new
file_delete(path)                  # Delete with approval
file_rename(old_path, new_path)    # Rename
directory_list()                   # Get file tree

# Code & Security
code_execute(language, code)       # Run in sandbox
security_scan(file_path)           # Hunter + analysis
auto_fix(file_path, issue)         # Automated repairs
auto_quarantine(file_path)         # Isolate threats
```

## Frontend Quick Start

```javascript
// Connect
const client = new IDEWebSocketClient(token);
const ide = new IDEManager(client);
await client.connect();

// File ops
await ide.openFile('test.py');
await ide.saveFile('test.py', code);
await ide.createFile('new.py', code);
await ide.deleteFile('old.py');
await ide.renameFile('old.py', 'new.py');
const tree = await ide.refreshFileTree();

// Execute
const result = await ide.runCode('python', code);

// Security
const scan = await ide.scanFile('test.py');
await ide.fixIssue('test.py', 'issue');
await ide.quarantineFile('bad.py');
```

## Backend Quick Start

```python
from backend.ide_websocket_handler import ide_ws_handler

# Handle message
message = {"type": "file_save", "path": "test.py", "content": "..."}
result = await ide_ws_handler.handle_message("user", message)
```

## Message Types

**Requests**: `file_open`, `file_save`, `file_create`, `file_delete`, `file_rename`, `directory_list`, `code_execute`, `security_scan`, `auto_fix`, `auto_quarantine`

**Responses**: `file_opened`, `file_saved`, `file_created`, `file_deleted`, `file_renamed`, `directory_tree`, `execution_result`, `security_scan_result`, `auto_fix_applied`, `file_quarantined`, `error`

## Testing

```bash
# Run tests
pytest tests/test_ide_websocket.py -v

# Validate
python validate_ide_integration.py

# Browser test
http://localhost:8000/static/test_ide.html
```

## Security Layers

1. **JWT Authentication** - Token validation
2. **Path Validation** - Escape prevention
3. **Governance** - Policy enforcement
4. **Hunter** - Threat detection
5. **Sandbox** - Isolated execution
6. **Verification** - Cryptographic proof

## Integration Points

- ✅ Sandbox Manager - File ops + execution
- ✅ Governance - Policy + audit
- ✅ Hunter - Security scanning
- ✅ Verification - Proof + envelopes
- ✅ WebSocket Manager - Connections
- ✅ Security Engine - Static analysis
- ✅ Execution Engine - Multi-language

## Common Patterns

### Save File with Checks
```javascript
try {
  const result = await ide.saveFile(path, content);
  if (result.status === 'pending') {
    alert('Requires approval');
  } else {
    alert('Saved! Verified: ' + result.verified);
  }
} catch (error) {
  alert('Blocked: ' + error.message);
}
```

### Execute Code Safely
```javascript
try {
  const result = await ide.runCode('python', code);
  console.log(result.stdout);
  console.log('Verified:', result.verified);
} catch (error) {
  alert('Execution blocked: ' + error.message);
}
```

### Scan Before Execute
```javascript
const scan = await ide.scanFile('script.py');
if (scan.riskScore > 5) {
  await ide.quarantineFile('script.py');
} else {
  await ide.runCode('python', null, 'script.py');
}
```

## Diagnostics

```bash
# Check files exist
ls -la backend/ide_websocket_handler.py
ls -la grace_ide/static/websocket_client.js

# Check no errors
python -m py_compile backend/ide_websocket_handler.py

# Run validation
python validate_ide_integration.py
```

## Troubleshooting

**Connection Failed**: Check JWT token validity
**Execution Blocked**: Check governance policies + Hunter rules
**File Not Found**: Verify path is in sandbox
**Timeout**: Check execution timeout settings (10s default)
**Verification Failed**: Check verification_integration setup

## Status

✅ **COMPLETE** - All 10 handlers implemented
✅ **TESTED** - Full test suite + browser tests
✅ **DOCUMENTED** - 3 docs + checklist + quick ref
✅ **SECURED** - 6-layer security architecture
✅ **INTEGRATED** - 7 system integration points

**Ready for deployment! 🚀**
