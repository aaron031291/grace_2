# IDE Auto-Fix & Security Implementation

## 📋 Overview

Complete implementation of security scanning, auto-fix, and quarantine features for Grace IDE.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Grace IDE                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │         SecurityPanel.tsx (UI)                   │   │
│  │  - Scan results visualization                    │   │
│  │  - Fix suggestions with buttons                  │   │
│  │  - Quarantine file list                          │   │
│  └────────────┬─────────────────────────────────────┘   │
│               │ WebSocket Messages                       │
│  ┌────────────▼─────────────────────────────────────┐   │
│  │      IDE WebSocket Handler                       │   │
│  │  Commands: scan, fix, quarantine, restore       │   │
│  └────────────┬─────────────────────────────────────┘   │
└───────────────┼──────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────┐
│                  Backend Services                         │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ ide_security.py  │  │  auto_fix.py     │             │
│  │ - scan_file()    │  │ - apply_fix()    │             │
│  │ - scan_code()    │  │ - Strategies:    │             │
│  │ - Hunter rules   │  │   • SQL sanitize │             │
│  │ - Pattern match  │  │   • XSS escape   │             │
│  └──────────────────┘  │   • Path fix     │             │
│                        │   • Remove eval  │             │
│  ┌──────────────────┐  │   • Type hints   │             │
│  │auto_quarantine.py│  │   • Format code  │             │
│  │ - quarantine()   │  └──────────────────┘             │
│  │ - restore()      │                                    │
│  │ - list()         │  ┌──────────────────┐             │
│  │ - delete()       │  │  hunter.py       │             │
│  │ - Governance ✓   │  │  governance.py   │             │
│  └──────────────────┘  └──────────────────┘             │
└───────────────────────────────────────────────────────────┘
```

## 📁 Files Created

### Backend Services

#### 1. `backend/ide_security.py`
**SecurityScanner class** - Scans files and code for security issues

**Features:**
- Pattern-based detection (SQL injection, XSS, path traversal, etc.)
- Hunter rule integration
- Language detection
- Line-by-line scanning
- Severity classification (critical, high, medium, low)

**Methods:**
```python
scan_file(file_path: str) -> List[Dict]
  - Scans physical file for security issues
  - Returns: List of issues with line numbers, severity, suggestions

scan_code(code_string: str, language: str) -> List[Dict]
  - Scans code string inline
  - Detects: SQL injection, XSS, dangerous imports, path traversal,
             hardcoded secrets, command injection
  - Returns: [{rule_name, severity, line_number, issue, suggestion, code_snippet}]
```

**Detection Patterns:**
- SQL Injection: `execute("..." + var)`, `.format()` in queries
- XSS: `innerHTML =`, `document.write()`, `eval()`
- Dangerous Imports: `eval`, `exec`, `__import__`
- Path Traversal: `../`, `..\\`, unsafe `open()`
- Hardcoded Secrets: password/api_key/token in code
- Command Injection: `os.system()`, `subprocess.call(shell=True)`

---

#### 2. `backend/auto_fix.py`
**AutoFix class** - Applies automated security fixes

**Fix Strategies:**

**a) `remove_dangerous_imports()`**
- Removes: `import eval`, `import exec`, `__import__`
- Action: Comments out with `# REMOVED (security):`

**b) `sanitize_sql()`**
- Detects: String concatenation in SQL queries
- Fix: Converts to parameterized queries
- Example:
  ```python
  # Before
  cursor.execute("SELECT * FROM users WHERE id=" + user_id)
  
  # After
  cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
  ```

**c) `escape_xss()`**
- JavaScript: Replaces `.innerHTML =` with `.textContent =`
- Python: Adds `html.escape()` to template variables
- Adds required imports automatically

**d) `fix_path_traversal()`**
- Wraps file paths with `os.path.normpath(os.path.abspath())`
- Validates paths before use
- Adds `import os` if needed

**e) `add_type_hints()`**
- Adds Python type annotations to functions
- Imports `from typing import Any`
- Example:
  ```python
  # Before
  def process(data, count):
  
  # After
  def process(data: Any, count: Any) -> Any:
  ```

**f) `format_code()`**
- Python: Uses `black` formatter
- JavaScript/TypeScript: Uses `prettier`
- Gracefully skips if formatter unavailable

**Method:**
```python
apply_fix(file_path: str, fix_type: str) -> Dict
  - Returns: {success, changes_made, new_content, file_path}
```

---

#### 3. `backend/auto_quarantine.py`
**QuarantineManager class** - Manages file quarantine/restoration

**Features:**
- Moves dangerous files to `.quarantine/` directory
- Maintains JSON manifest of quarantined files
- Governance integration for restore/delete
- Immutable audit logging
- File hash verification

**Methods:**

**a) `quarantine_file(file_path, reason, actor)`**
```python
- Copies file to .quarantine/
- Removes original
- Generates unique quarantine ID: Q20250102_143022_malicious.py
- Logs to audit trail
- Returns: {success, quarantine_id, quarantine_path, reason}
```

**b) `list_quarantined(status=None)`**
```python
- Lists all quarantined files
- Filters by status: 'quarantined', 'restored', 'deleted'
- Returns: [{quarantine_id, original_path, reason, status, ...}]
```

**c) `restore_file(quarantine_id, actor)`**
```python
- Requires governance approval
- Restores file to original location
- Updates manifest status
- Logs restoration
- Returns: {success, restored_to} OR {requires_approval: true}
```

**d) `delete_quarantined(quarantine_id, actor)`**
```python
- Requires governance approval
- Permanently deletes quarantined file
- Updates manifest
- Logs deletion
- Returns: {success, quarantine_id, status}
```

**e) `get_quarantine_info(quarantine_id)`**
```python
- Returns detailed metadata
- Includes: file_hash, file_size, timestamps, actor
```

**Manifest Structure:**
```json
{
  "Q20250102_143022_malicious.py": {
    "original_path": "/path/to/original/file.py",
    "quarantine_path": ".quarantine/Q20250102_143022_malicious.py",
    "reason": "Detected eval() usage - critical security threat",
    "actor": "hunter_system",
    "quarantined_at": "2025-01-02T14:30:22.123456",
    "status": "quarantined",
    "file_size": 2048,
    "file_hash": "a1b2c3d4..."
  }
}
```

---

#### 4. `grace_ide/api/handlers.py` (Updated)
**WebSocket command handlers**

**New Commands:**

**a) `security.scan`**
```json
Request: {
  "type": "security.scan",
  "file_path": "/path/to/file.py"
  OR "content": "code string", "language": "python"
}

Response: {
  "type": "security.scan_results",
  "issues": [...],
  "total_issues": 5,
  "critical": 2,
  "high": 1,
  "medium": 2,
  "low": 0
}
```

**b) `security.fix`**
```json
Request: {
  "type": "security.fix",
  "file_path": "/path/to/file.py",
  "fix_type": "sanitize_sql"
}

Response: {
  "type": "security.fix_applied",
  "success": true,
  "changes_made": ["Fixed SQL injection...", "Added parameterization"],
  "new_content": "..."
}
```

**c) `security.quarantine`**
```json
Request: {
  "type": "security.quarantine",
  "file_path": "/path/to/malicious.py",
  "reason": "Critical threat detected"
}

Response: {
  "type": "security.quarantined",
  "success": true,
  "quarantine_id": "Q20250102_143022_malicious.py",
  "quarantine_path": ".quarantine/..."
}
```

**d) `security.list_quarantined`**
```json
Request: {
  "type": "security.list_quarantined",
  "status": "quarantined"  // optional
}

Response: {
  "type": "security.quarantine_list",
  "files": [...],
  "total": 5
}
```

**e) `security.restore`**
```json
Request: {
  "type": "security.restore",
  "quarantine_id": "Q20250102_143022_malicious.py"
}

Response: {
  "type": "security.restore_result",
  "success": true,
  "restored_to": "/original/path/file.py"
  OR "requires_approval": true
}
```

---

### Frontend Components

#### 5. `grace_ide/components/SecurityPanel.tsx`
**React security UI component**

**Features:**

**Tab 1: Scan Results**
- Scan current file button
- Issue statistics (critical/high/medium/low counts)
- Detailed issue cards with:
  - Severity badge with color coding
  - Rule name and line number
  - Issue description
  - Code snippet
  - Fix suggestion
  - "Apply Fix" buttons per issue type
  - "Quarantine File" for critical issues
- Quick fixes section:
  - Format Code
  - Add Type Hints

**Tab 2: Quarantine Management**
- List all quarantined files
- Show metadata: size, date, reason, status
- Restore button (with governance check)
- Delete button (with confirmation)
- Status badges

**Props:**
```typescript
interface SecurityPanelProps {
  websocket: WebSocket | null;
  currentFile?: string;
}
```

**State Management:**
```typescript
const [issues, setIssues] = useState<SecurityIssue[]>([]);
const [quarantinedFiles, setQuarantinedFiles] = useState<QuarantinedFile[]>([]);
const [scanning, setScanning] = useState(false);
const [activeTab, setActiveTab] = useState<'scan' | 'quarantine'>('scan');
```

**UI Elements:**
- Color-coded severity badges (red/orange/yellow/blue)
- Responsive grid layout
- Dark theme compatible
- Smooth transitions and hover effects

---

#### 6. `grace_ide/components/SecurityPanel.css`
**Styling for security panel**

**Features:**
- Dark theme (#1e1e1e background)
- Color-coded severity:
  - Critical: #ff4444 (red)
  - High: #ff8800 (orange)
  - Medium: #ffbb00 (yellow)
  - Low: #4488ff (blue)
- Card-based layout
- Hover animations
- Responsive grid for statistics
- Professional button styles

---

### Tests

#### 7. `tests/test_ide_security.py`
**Comprehensive test suite**

**Test Cases:**

**Test 1: Security Scanner**
- Scans code with SQL injection, eval, exec
- Verifies detection of multiple issue types
- Validates severity classification
- Checks line number accuracy

**Test 2: Auto-Fix**
- Creates file with dangerous imports
- Applies `remove_dangerous_imports` fix
- Verifies changes made
- Confirms dangerous code removed/commented

**Test 3: Quarantine System**
- Creates malicious file
- Quarantines file
- Verifies original removed
- Lists quarantined files
- Tests restoration (governance required)

**Test 4: XSS Fix**
- Creates JavaScript with innerHTML
- Applies `escape_xss` fix
- Verifies innerHTML → textContent conversion

**Test 5: Path Traversal Fix**
- Creates code with `../` paths
- Applies `fix_path_traversal`
- Verifies `os.path.normpath()` added

**Test 6: Full Workflow**
1. Scan malicious file
2. Detect critical issues
3. Apply auto-fix
4. Re-scan to verify
5. Quarantine if still dangerous
6. Complete audit trail

---

## 🔄 Integration Flow

### 1. File Upload → Hunter Scan
```
User uploads file.py
    ↓
IDE WebSocket receives file
    ↓
SecurityScanner.scan_file()
    ↓
Hunter rules applied
    ↓
Issues detected → Display in SecurityPanel
```

### 2. Apply Fix Workflow
```
User clicks "Apply Fix" button
    ↓
WebSocket sends: {type: "security.fix", fix_type: "sanitize_sql"}
    ↓
Governance check (file_write permission)
    ↓
AutoFix.apply_fix()
    ↓
File modified with fixes
    ↓
Response: {success, changes_made, new_content}
    ↓
UI shows changes
    ↓
Auto re-scan to verify
```

### 3. Quarantine Workflow
```
Critical threat detected
    ↓
User clicks "Quarantine File"
    ↓
QuarantineManager.quarantine_file()
    ↓
File moved to .quarantine/
    ↓
Original removed
    ↓
Audit log entry created
    ↓
Manifest updated
    ↓
UI refreshes quarantine list
```

### 4. Restore Workflow
```
User clicks "Restore" in quarantine tab
    ↓
Governance approval check
    ↓
If approved:
  - File copied back to original location
  - Manifest status = "restored"
  - Audit log updated
If requires review:
  - Approval request created
  - User notified
```

---

## 🔒 Security Features

### Governance Integration
- All file modifications require governance approval
- Restore operations need explicit authorization
- Delete operations are logged immutably
- Policy enforcement: `auto_fix`, `restore_quarantined_file`, `delete_quarantined_file`

### Audit Trail
- Every quarantine logged with actor, timestamp, reason
- All restorations tracked
- File hashes stored for integrity verification
- Immutable log entries

### Hunter Integration
- Uses existing Hunter security rules
- ML severity prediction (if enabled)
- Real-time threat detection
- Automatic alert creation

---

## 📊 Detection Capabilities

| Threat Type          | Detection Method           | Auto-Fix Available |
|---------------------|----------------------------|-------------------|
| SQL Injection       | Pattern + Hunter rules     | ✅ Yes            |
| XSS                 | Pattern matching           | ✅ Yes            |
| Command Injection   | os.system, eval detection  | ✅ Partial        |
| Path Traversal      | ../ detection              | ✅ Yes            |
| Dangerous Imports   | eval, exec, __import__     | ✅ Yes            |
| Hardcoded Secrets   | Regex patterns             | ⚠️ Manual         |
| Type Safety         | Missing type hints         | ✅ Yes            |
| Code Formatting     | Style violations           | ✅ Yes            |

---

## 🎯 Usage Example

### From IDE UI:

1. **Open file in IDE**
2. **Click "Scan Current File"** in SecurityPanel
3. **View detected issues** with severity colors
4. **Click "Apply Fix"** for specific issues
5. **Review changes** in diff view
6. **Re-scan** to verify fixes
7. **If critical threat remains:** Click "Quarantine File"

### Via WebSocket:

```javascript
// Scan file
ws.send(JSON.stringify({
  type: 'security.scan',
  file_path: '/sandbox/user/script.py'
}));

// Apply fix
ws.send(JSON.stringify({
  type: 'security.fix',
  file_path: '/sandbox/user/script.py',
  fix_type: 'sanitize_sql'
}));

// Quarantine
ws.send(JSON.stringify({
  type: 'security.quarantine',
  file_path: '/sandbox/user/malicious.py',
  reason: 'Eval usage detected'
}));
```

---

## 🧪 Testing

Run test suite:
```bash
cd grace_rebuild
python tests/test_ide_security.py
```

Expected output:
```
============================================================
IDE SECURITY SYSTEM TEST SUITE
============================================================

[TEST 1] Testing Security Scanner...
✓ Found 5 security issues
  - CRITICAL: sql_injection (Line 7)
  - CRITICAL: dangerous_imports (Line 11)
...

[TEST 6] Testing Full Workflow...
→ Step 1: Scanning file...
  Found 4 issues
→ Step 2: Attempting auto-fix...
  Fix applied: True
→ Step 3: Re-scanning after fix...
  Issues remaining: 2
→ Step 4: Quarantining...
  ✓ File quarantined: Q20250102_143022_malicious.py

============================================================
TEST SUMMARY
============================================================
✓ PASS: Security Scanner
✓ PASS: Auto-Fix
✓ PASS: Quarantine System
✓ PASS: XSS Fix
✓ PASS: Path Traversal Fix
✓ PASS: Full Workflow

Passed: 6/6

🎉 ALL TESTS PASSED!
```

---

## 📈 Benefits

1. **Automated Security** - Catches vulnerabilities before execution
2. **Developer Friendly** - One-click fixes with clear suggestions
3. **Governance Compliant** - All operations logged and approved
4. **Hunter Integration** - Leverages existing security framework
5. **Quarantine Safety** - Isolates threats without data loss
6. **Audit Trail** - Complete forensic record
7. **Extensible** - Easy to add new detection patterns and fixes

---

## 🚀 Next Steps

1. **Add More Patterns** - Expand detection rules
2. **ML Enhancement** - Train models on fix success rates
3. **IDE Integration** - Add inline warnings in code editor
4. **Diff Preview** - Show before/after for fixes
5. **Batch Operations** - Scan/fix entire projects
6. **Custom Rules** - Allow users to define detection patterns
7. **Fix Validation** - Re-scan automatically after fix

---

## 📝 Summary

✅ **SecurityScanner** - Pattern + Hunter rule-based scanning  
✅ **AutoFix** - 6 automated fix strategies  
✅ **QuarantineManager** - File isolation with governance  
✅ **SecurityPanel** - React UI with scan/quarantine tabs  
✅ **WebSocket Integration** - Real-time scan/fix/quarantine  
✅ **Test Suite** - 6 comprehensive tests  
✅ **Governance Integration** - Policy enforcement  
✅ **Audit Logging** - Immutable trail  

**Status: ✅ FULLY IMPLEMENTED & READY FOR TESTING**
