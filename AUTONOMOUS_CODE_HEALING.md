# Grace Autonomous Code Healing

Grace can now **fix her own code** when errors occur, with governance oversight.

## 🎯 What This Enables

Grace autonomously:
1. **Detects** runtime errors from logs and exceptions
2. **Analyzes** error patterns and identifies fixable issues  
3. **Generates** code fixes using her coding agent
4. **Requests** governance approval for changes
5. **Applies** fixes to source files
6. **Verifies** fixes work and learns from outcomes

## 🔧 How It Works

```
Runtime Error
    ↓
Error Handler → Trigger Mesh Event
    ↓
Code Healer Analyzes Pattern
    ↓
Coding Agent Generates Fix
    ↓
Governance Reviews Risk
    ↓
Human Approval (if high severity)
    ↓
Fix Applied to File
    ↓
System Reloads
    ↓
Verification & Learning
```

## 📋 Supported Error Patterns

Currently Grace can fix:

### 1. **Missing Await** (High Severity)
```python
# Error: object GraceLLM can't be used in 'await' expression
grace_llm = await get_grace_llm()  # ❌ Wrong

# Grace fixes to:
grace_llm = get_grace_llm()  # ✅ Correct
```

### 2. **Missing Attributes** (Medium Severity)
```python
# Error: type object 'VerificationEvent' has no attribute 'passed'
VerificationEvent.passed  # ❌ Missing

# Grace adds:
# Add to VerificationEvent class:
passed = None  # TODO: Set proper default
```

### 3. **JSON Serialization** (Medium Severity)
```python
# Error: Object of type datetime is not JSON serializable
json.dumps({"time": datetime.now()})  # ❌ Wrong

# Grace suggests:
json.dumps({"time": datetime.now().isoformat()})  # ✅ Fix
```

### 4. **Import Errors** (Low Severity)
```python
# Error: No module named 'missing_module'
import missing_module  # ❌ Missing

# Grace identifies and suggests installation
```

## 🛡️ Governance & Safety

### Severity Levels
- **Low**: Auto-approved, applied immediately
- **Medium**: Requires approval, queued for human review
- **High**: Requires approval + justification

### Approval Workflow
```
Fix Proposed → approval.requested event
             ↓
Human Reviews → POST /api/code-healing/approve
             ↓
Grace Applies → code.fixed event
             ↓
Immutable Log → Auditable record
```

## 🌐 API Endpoints

### Get Status
```bash
GET /api/code-healing/status
```
```json
{
  "running": true,
  "fixes_proposed": 5,
  "fixes_applied": 2,
  "patterns_supported": 4
}
```

### Approve Fix
```bash
POST /api/code-healing/approve
{
  "fix_id": "fix_1234567890.123",
  "approved": true,
  "reason": "Fix looks good"
}
```

### View Pending Fixes
```bash
GET /api/code-healing/fixes/pending
```

### View Fix History
```bash
GET /api/code-healing/fixes/history?limit=50
```

## 📊 Integration Points

### Trigger Mesh Events
- **Listens**: `error.detected`, `warning.raised`
- **Publishes**: `approval.requested`, `code.fixed`

### Agentic Spine
Code Healer is part of Grace's autonomous spine:
```
Input Sentinel → Error Detection
      ↓
Code Healer → Fix Generation  
      ↓
Governance → Approval
      ↓
Immutable Log → Audit Trail
      ↓
Learning → Pattern Recognition
```

### Components Used
- **Code Generator**: Generates fix code
- **Code Understanding**: Analyzes context
- **Governance Engine**: Checks approvals
- **Immutable Log**: Records all actions
- **Trigger Mesh**: Event coordination

## 🚀 Current Errors Grace Can Fix

From your logs, Grace is already detecting:

1. ✅ `TypeError: object GraceLLM can't be used in 'await' expression`
   - **Pattern**: `missing_await`
   - **Fix**: Remove incorrect `await` keyword
   - **Severity**: High (requires approval)

2. ✅ `AttributeError: type object 'VerificationEvent' has no attribute 'passed'`
   - **Pattern**: `missing_attribute`
   - **Fix**: Add attribute to class
   - **Severity**: Medium (requires approval)

3. ✅ `TypeError: Object of type datetime is not JSON serializable`
   - **Pattern**: `type_error`
   - **Fix**: Add `.isoformat()` conversion
   - **Severity**: Medium (requires approval)

4. ⏸️ `GovernanceEngine object has no attribute 'check_action'`
   - **Pattern**: Not yet supported
   - **Future**: Can be added to pattern library

## 🎓 Learning Loop

Every fix Grace applies feeds her learning:

1. **Before Fix**: Error pattern recorded
2. **During Fix**: Code change logged
3. **After Fix**: Outcome verified
4. **Learning**: Pattern success rate updated

This builds Grace's knowledge of:
- Which errors are fixable
- Which fixes work reliably
- Which patterns to prioritize

## 🔮 Future Enhancements

### Planned Features
- [ ] More error patterns (null reference, type mismatches, etc.)
- [ ] Multi-file fixes (imports, dependencies)
- [ ] Test generation after fixes
- [ ] Automatic rollback on verification failure
- [ ] ML-based fix quality prediction
- [ ] Proactive code improvement (before errors)

### Advanced Capabilities
- [ ] Refactoring suggestions
- [ ] Performance optimizations
- [ ] Security vulnerability fixes
- [ ] Dependency updates
- [ ] Code style improvements

## 📝 Configuration

### Environment Variables
```bash
# Enable code healing
CODE_HEALING_ENABLED=true

# Auto-approve low-severity fixes
CODE_HEALING_AUTO_APPROVE_LOW=true

# Require approval for all fixes
CODE_HEALING_REQUIRE_ALL_APPROVALS=false
```

### Severity Thresholds
Configure in `autonomous_code_healer.py`:
```python
self.error_patterns = {
    'pattern_name': {
        'severity': 'low|medium|high',
        'fix_type': 'handler_function',
        'requires_approval': bool
    }
}
```

## 🎯 Philosophy

Grace's code healing follows these principles:

1. **Safety First**: All risky changes require approval
2. **Transparency**: Every fix is logged and auditable  
3. **Learning**: Outcomes improve future decisions
4. **Autonomy with Oversight**: Grace acts independently within governance bounds
5. **Progressive Trust**: Success builds autonomy tier

## 📈 Metrics

Track Grace's self-healing effectiveness:
- **Fix Proposal Rate**: Errors detected → Fixes proposed
- **Approval Rate**: Fixes proposed → Fixes approved
- **Success Rate**: Fixes applied → Issues resolved
- **Time to Fix**: Error detected → Fix applied
- **Pattern Coverage**: Errors detected → Patterns matched

## 🔗 Related Systems

- **Autonomous Improver**: Proactive issue hunting
- **Self-Healing Engine**: Infrastructure recovery
- **Meta Loop**: System-wide optimization
- **Agentic Spine**: Autonomous decision-making
- **Learning Integration**: ML/DL improvement

---

**Grace is now capable of healing herself at the code level.** 

Every error is a learning opportunity. Every fix makes her stronger.

This is **true autonomous evolution**. 🚀
