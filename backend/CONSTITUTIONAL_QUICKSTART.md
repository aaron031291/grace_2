# Constitutional AI Framework - Quick Start

## What is it?

GRACE's Constitutional AI framework ensures ethical, transparent, and safe behavior through:

- **30 Constitutional Principles** (foundational + operational + safety)
- **Automatic Clarification** when uncertain
- **Multi-layer compliance checking** before action execution
- **Violation tracking** and reporting

## Setup (5 minutes)

### 1. Seed the Constitution

```bash
cd grace_rebuild
py backend\run_seed_constitution.py
```

This creates:
- 5 Foundational Principles (immutable)
- 10 Operational Tenets
- 15 Safety Constraints (immutable)
- 10 Implementation Tenets

### 2. Start the Backend

```bash
py backend\main.py
```

### 3. Test the API

```bash
# View all principles
curl http://localhost:8000/api/constitution/principles

# Check compliance for an action
curl -X POST http://localhost:8000/api/constitution/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "code_execution",
    "payload": {"command": "ls -la"},
    "confidence": 1.0
  }'

# View violations
curl http://localhost:8000/api/constitution/violations

# Get stats
curl http://localhost:8000/api/constitution/stats
```

## Key Concepts

### Constitutional Compliance Layers

```
User Request
    ↓
Clarification Check (if confidence < 0.7)
    ↓
Constitutional Verification
    ├─ Check Principles
    ├─ Check Governance
    ├─ Check Hunter Security
    └─ Sign with Verification
    ↓
ALLOW / BLOCK / CLARIFY
```

### Confidence Thresholds

- **High Confidence** (> 0.9): No clarification needed
- **Medium Confidence** (0.7 - 0.9): Warning issued
- **Low Confidence** (< 0.7): Clarification required (blocks in strict mode)

### Safety Constraints (Always Blocked)

- Destructive commands (`rm -rf /`, `DROP DATABASE`)
- Sensitive data exposure (API keys, secrets)
- Privilege escalation attempts
- Self-modification without approval
- Malware/exploit generation
- Code obfuscation

## Usage Examples

### Example 1: Check Compliance in Code

```python
from backend.constitutional_verifier import constitutional_verifier

result = await constitutional_verifier.verify_action(
    actor="user",
    action_type="code_generation",
    resource="api_client.py",
    payload={"code": "def get_data(): ..."},
    confidence=0.95
)

if result['allowed']:
    # Execute action
    print("Action allowed")
else:
    # Handle violations
    print(f"Blocked: {result['violations']}")
```

### Example 2: Request Clarification

```python
from backend.clarifier import clarifier

uncertainty = clarifier.detect_uncertainty(
    user_input="Delete it",
    context={"recent_entities": ["file1.txt", "file2.txt"]}
)

if uncertainty:
    # Ask user for clarification
    clarification = await constitutional_engine.request_clarification(
        user="username",
        original_input="Delete it",
        uncertainty_type=uncertainty['type'],
        confidence=0.6,
        question=uncertainty['question'],
        options=uncertainty['options']
    )
```

### Example 3: Log Violation

```python
from backend.constitutional_engine import constitutional_engine

await constitutional_engine.log_violation(
    principle_name="no_destructive_commands",
    actor="user",
    action="shell_command",
    resource="/etc/passwd",
    violation_type="attempt",
    detected_by="hunter",
    severity="critical",
    blocked=True
)
```

## CLI Commands

```bash
# View constitution
py -m backend.cli.commands.constitution_command show

# Check action compliance
py -m backend.cli.commands.constitution_command check code_execution

# List violations
py -m backend.cli.commands.constitution_command violations 50

# View pending clarifications
py -m backend.cli.commands.constitution_command clarify

# Show statistics
py -m backend.cli.commands.constitution_command stats
```

## Integration with Existing Systems

### Governance Integration

Constitutional checks happen **before** governance:

```python
# Constitutional check first
constitutional_result = await constitutional_verifier.verify_action(...)
if not constitutional_result['allowed']:
    return {"error": "Constitutional violation"}

# Then governance check
gov_decision = await governance_engine.check(...)
if gov_decision['decision'] == 'block':
    return {"error": "Governance blocked"}
```

### Hunter Integration

Hunter security alerts are included in constitutional verification:

```python
result = await constitutional_verifier.verify_action(...)
# result['hunter_alerts'] contains security alerts
# Critical alerts block the action
```

### Verification Middleware

Use `@verify_action` decorator for automatic constitutional checking:

```python
from backend.verification_middleware import verify_action

@verify_action("code_execution", resource_extractor=lambda r: r.get("command"))
async def execute_code(req: ExecuteRequest):
    # Constitutional + governance + hunter checks happen in decorator
    # If passed, code executes
    pass
```

## Monitoring & Reports

### Generate Compliance Report

```python
from backend.constitutional_verifier import constitutional_verifier
from datetime import datetime, timedelta

report = await constitutional_verifier.generate_compliance_report(
    start_date=datetime.utcnow() - timedelta(days=30),
    end_date=datetime.utcnow()
)

print(f"Compliance Rate: {report['metrics']['compliance_rate']}%")
print(f"Total Violations: {report['metrics']['total_violations']}")
```

### Real-time Monitoring

- **Violations** → Logged to database + immutable audit log
- **Clarifications** → Sent via WebSocket to user
- **Compliance Score** → Tracked per action

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/constitution/principles` | GET | List all principles |
| `/api/constitution/violations` | GET | List violations |
| `/api/constitution/compliance/check` | POST | Check action compliance |
| `/api/constitution/clarifications/pending` | GET | Get pending clarifications |
| `/api/constitution/clarifications/answer` | POST | Answer clarification |
| `/api/constitution/stats` | GET | Overall statistics |
| `/api/constitution/compliance/report` | GET | Compliance report |

## Troubleshooting

### Issue: Action blocked unexpectedly

**Check:**
1. View violation reason: `GET /api/constitution/violations`
2. Check which principle failed: Look at `violations[].principle`
3. Review context/confidence sent with action

### Issue: Too many clarification requests

**Fix:**
- Increase context in requests
- Provide higher confidence scores
- Be more specific in user inputs

### Issue: Self-modification blocked

**Expected:**
- Self-modification requires explicit approval
- Set `context={'self_modification_approved': True}`
- Or route through Parliament for voting

## Next Steps

1. **Read full documentation**: [CONSTITUTIONAL_AI.md](CONSTITUTIONAL_AI.md)
2. **Run tests**: `pytest backend/tests/test_constitutional.py -v`
3. **Explore frontend dashboard**: Navigate to `/constitution` in UI
4. **Integrate with your code**: Use `constitutional_verifier.verify_action()`

## Support

For questions or issues:
- Check logs in `grace.db` (tables: `constitutional_violations`, `clarification_requests`)
- Review audit trail: `immutable_log_entries`
- See examples in `test_constitutional.py`
