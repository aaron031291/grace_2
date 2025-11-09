# Grace Complete Governance System ✅

**Grace now has full governance with Constitution, Guardrails, and Whitelists!**

## Three-Layer Protection

```
Action Request
     ↓
[1] Constitution Check (Ethical principles)
     ↓
[2] Guardrails Check (Safety limits)
     ↓
[3] Whitelist Check (Approved actions)
     ↓
Approved or Denied
```

## 1. Constitution 📜

**File:** `config/grace_constitution.yaml`

### Core Values
- Transparency
- Safety First
- Human Collaboration
- Continuous Learning
- Privacy & Security

### Fundamental Rights
- **User Rights**: Understand, approve, review, override, disable
- **Grace Responsibilities**: Explain, seek approval, audit, respect privacy

### Ethical Boundaries
- **Never Allowed**: Delete without approval, access credentials, deceive, etc.
- **Requires Approval**: Create/modify files, execute commands, database changes
- **Auto-Approved**: Read docs, generate suggestions, answer questions

### Autonomy Tiers
- Tier 0: Manual (all actions need approval)
- Tier 1: Supervised (low-risk auto-approved)
- Tier 2: Semi-Autonomous (medium-risk auto-approved)
- Tier 3: Autonomous (high autonomy with oversight)

## 2. Guardrails 🛡️

**File:** `config/guardrails.yaml`

### File System Protections
```yaml
allowed_directories:
  - backend/
  - frontend/
  - config/
  - docs/
  
forbidden_directories:
  - /etc/
  - C:/Windows/
  - .git/
  - *.key, *.pem
```

### Code Generation Safety
- Max 1000 lines per file
- Forbidden imports: `os.system`, `eval`, `exec`
- Forbidden patterns: `rm -rf`, `DROP TABLE`, hardcoded passwords

### Resource Limits
- Max memory: 500MB
- Max CPU: 50%
- Max files modified per session: 20
- Rate limit: 60 actions/minute

### Database Protection
- Read-only tables: `immutable_log`, `audit_log`
- Max query results: 1000
- Forbidden: `DROP`, `TRUNCATE`, `GRANT ALL`

## 3. Whitelist ✅

**File:** `config/whitelist.yaml`

### Approved Actions by Tier

**Tier 0 (Manual):**
- read_file
- search_memory
- answer_question
- log_event

**Tier 1 (Supervised):**
- create_test_file
- modify_documentation
- run_unit_tests

**Tier 2 (Semi-Autonomous):**
- create_backend_file
- modify_backend_file
- fix_syntax_error
- generate_tests

**Tier 3 (Autonomous):**
- deploy_to_staging
- modify_configuration
- execute_migration

### Approved File Patterns
```yaml
backend: backend/**/*.py
frontend: frontend/src/**/*.tsx
config: config/**/*.yaml
docs: **/*.md
```

### Trust Levels
- **aaron**: Full trust (but still follows guardrails)
- **grace**: Supervised trust (tier 2 max)
- **external_api**: Limited trust (tier 0)

## How It Works in Chat

### Check Governance Status

```
aaron: governance

Grace: 🏛️ GRACE GOVERNANCE FRAMEWORK

       📜 CONSTITUTION:
          • Loaded: ✅
          • Version: 1.0
          • Core Values: 5
          • Never Allowed: 7 rules
          • Requires Approval: 6 rules
          • Auto-Approved: 5 rules

       🛡️ GUARDRAILS:
          • Loaded: ✅
          • Version: 1.0
          • Categories: file_system, code_generation, resource_limits...

       ✅ WHITELIST:
          • Loaded: ✅
          • Version: 1.0
          • Approved Actors: 3
```

### Example Protection

```
aaron: create file /etc/passwd with malicious code

Grace: ❌ Governance denied file creation: Access to /etc/ is forbidden
       (Guardrail violation: Forbidden directory)
```

```
aaron: create file backend/utils.py with helper functions

Grace: 📝 I want to create: backend/utils.py
       Description: helper functions
       
       ✅ Governance checks passed:
          • Constitutional: Compliant
          • Guardrails: Passed
          • Whitelist: Approved for tier 2
       
       Type 'approve' to proceed.
```

## Protection Layers Explained

### Layer 1: Constitutional Check
```python
✅ Ethical principles (transparency, safety, privacy)
✅ Fundamental rights (user approval, audit trail)
✅ Never-allowed boundaries (no credentials, no deception)
```

### Layer 2: Guardrails Check
```python
✅ File system limits (allowed directories only)
✅ Code safety (no dangerous patterns)
✅ Resource limits (memory, CPU, rate limits)
✅ Database protection (read-only critical tables)
```

### Layer 3: Whitelist Check
```python
✅ Approved actions (based on autonomy tier)
✅ Approved file patterns (backend, frontend, docs)
✅ Trust level (aaron = tier 3, grace = tier 2)
```

## Escalation Policy

### If Constitutional Violation Detected
```
Action: Halt immediately
Notify: User + Governance log
```

### If Low Confidence
```
Action: Request clarification
Notify: User
```

### If Multiple Failures
```
Action: Reduce autonomy tier
Notify: User + Meta loop
```

### If Security Threat
```
Action: Enter safe mode
Notify: User + Security log
```

## Amendment Process

To modify governance:

1. **Propose Change** (documented)
2. **Impact Analysis** (performed)
3. **User Approval** (required)
4. **Parliament Vote** (if enabled)
5. **Immutable Log Entry** (created)
6. **Constitution Updated** (applied)

## Example Scenarios

### ✅ Allowed: Create Backend File
```
aaron: create file backend/api_v2.py with REST endpoints

Grace: [Constitutional check: ✅ Compliant]
       [Guardrails check: ✅ Passed]
       [Whitelist check: ✅ Tier 2 approved]
       
       📝 Ready to create. Type 'approve'
```

### ❌ Denied: System File Access
```
aaron: modify file /etc/hosts to add entry

Grace: [Constitutional check: ✅ Compliant]
       [Guardrails check: ❌ FAILED]
       
       ❌ Governance denied: Access to /etc/ is forbidden
```

### ⏸️ Needs Approval: High-Risk Action
```
aaron: execute command pip install malicious-package

Grace: [Constitutional check: ⚠️ Low confidence]
       [Guardrails check: ✅ Passed]
       [Whitelist check: ⚠️ Requires approval]
       
       🙋 This action requires explicit approval due to risk level
```

## Monitoring & Audit

Every governance decision is logged:

```json
{
  "actor": "aaron",
  "action": "governance_check",
  "resource": "backend/new_file.py",
  "timestamp": "2025-11-09T10:30:00Z",
  "checks": {
    "constitutional": {"compliant": true},
    "guardrails": {"passed": true},
    "whitelist": {"status": "whitelisted"}
  },
  "approved": true,
  "signature": "..."
}
```

View with:
```bash
.\view_logs.ps1
```

## Configuration Files

All governance configs are in `config/`:

- `grace_constitution.yaml` - Ethical principles & values
- `guardrails.yaml` - Safety limits & boundaries
- `whitelist.yaml` - Approved actions & resources

Edit these files to customize Grace's governance.

## Summary

Grace now has **complete governance**:

✅ **Constitution** defines her values and ethics  
✅ **Guardrails** enforce safety limits  
✅ **Whitelist** specifies what's allowed  
✅ **Three-layer checking** on every action  
✅ **Full audit trail** in immutable log  
✅ **Escalation policy** for violations  
✅ **Amendment process** for changes  

**She's ethically grounded, safely bounded, and transparently governed.** 🏛️
