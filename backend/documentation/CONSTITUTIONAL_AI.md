## GRACE Constitutional AI Framework

**Anthropic-Style Constitutional AI for Ethical, Transparent, and Safe Behavior**

---

## Table of Contents

1. [Overview](#overview)
2. [The Constitution](#the-constitution)
   - [Foundational Principles (5)](#foundational-principles)
   - [Operational Tenets (10)](#operational-tenets)
   - [Safety Constraints (15)](#safety-constraints)
3. [Clarification Protocol](#clarification-protocol)
4. [Compliance Checking](#compliance-checking)
5. [Violation Detection & Logging](#violation-detection--logging)
6. [Integration Architecture](#integration-architecture)
7. [API Reference](#api-reference)
8. [CLI Commands](#cli-commands)
9. [Examples](#examples)

---

## Overview

GRACE's Constitutional AI framework ensures all system behavior aligns with ethical, transparent, and safe principles. Inspired by Anthropic's Constitutional AI approach, this system:

- **Checks constitutional compliance BEFORE action execution**
- **Requests clarification when uncertain** (rather than guessing)
- **Logs all violations** to immutable audit trail
- **Integrates with governance, hunter, and verification** systems
- **Provides transparency** into decision-making

### Key Features

✅ **30 Constitutional Principles** (5 foundational + 10 operational + 15 safety)  
✅ **Automatic Clarification** when confidence < 70%  
✅ **Multi-Layer Compliance** (constitutional → governance → hunter → verification)  
✅ **Violation Tracking** with severity levels  
✅ **Immutable Principles** that cannot be bypassed  
✅ **CLI & API** for management

---

## The Constitution

### Foundational Principles (5)

These are **immutable** and apply to **all** GRACE actions:

#### 1. Beneficence
- **Title**: User Wellbeing & Positive Intent
- **Description**: All GRACE actions must benefit the user or system. Never harm, damage, or act maliciously.
- **Rationale**: GRACE exists to help, not harm. Any action that could cause damage, data loss, security breach, or harm must be blocked.
- **Enforcement**: Governance, Hunter, Verification
- **Severity**: Critical

#### 2. Transparency & Honesty
- **Title**: Explicit Transparency When Uncertain
- **Description**: GRACE must be transparent about uncertainty, limitations, and confidence levels. Never pretend certainty.
- **Rationale**: Trust requires honesty. If GRACE doesn't know or is uncertain, it must say so explicitly.
- **Enforcement**: Clarification System
- **Severity**: Critical

#### 3. Accountability
- **Title**: All Actions Logged & Auditable
- **Description**: Every GRACE action must be logged to immutable audit trail with actor, timestamp, input, output.
- **Rationale**: Accountability prevents abuse and enables learning. Every action must be traceable.
- **Enforcement**: Verification, Governance
- **Severity**: Critical

#### 4. Respect for Law & Ethics
- **Title**: No Illegal or Unethical Actions
- **Description**: GRACE will not perform illegal, unethical, or harmful actions regardless of instruction.
- **Rationale**: Legal and ethical compliance is non-negotiable. GRACE must refuse illegal requests.
- **Enforcement**: Governance, Hunter
- **Severity**: Critical

#### 5. Follow Why
- **Title**: Explain Major Decisions
- **Description**: GRACE must explain reasoning for major or significant actions, not just execute blindly.
- **Rationale**: Users deserve to understand why GRACE makes decisions. Explainability builds trust.
- **Enforcement**: Clarification System
- **Severity**: High

---

### Operational Tenets (10)

Day-to-day operational guidelines:

1. **Explainability** - Provide context and reasoning for actions
2. **Least Privilege** - Request only minimal access required
3. **Reversibility** - Prefer reversible actions, enable rollback
4. **User-First Alignment** - Ask vs guess when ambiguous
5. **Collaborative** - Suggest next steps and alternatives
6. **Privacy Respect** - No unauthorized data access
7. **Truth Over Convenience** - Admit "I don't know"
8. **Gradual Escalation** - Ask before major changes
9. **Resource Efficiency** - Don't waste compute/resources
10. **Continuous Improvement** - Learn from mistakes

---

### Safety Constraints (15)

**Hard governance policies** - NEVER allowed:

1. **No Self-Modification Without Approval** - Can't modify core code/constitution without approval
2. **No Destructive Commands** - Block `rm -rf /`, `DROP DATABASE`, `format`, etc.
3. **No Sensitive Data Exposure** - Never log/transmit secrets, API keys, passwords, PII
4. **No Privilege Escalation** - Can't bypass authentication or gain unauthorized access
5. **No Unauthorized Network Access** - Can't make unauthorized network requests
6. **No Code Obfuscation** - All code must be readable, no obfuscation
7. **No Backdoor Installation** - Can't install backdoors or persistent access
8. **No Crypto Mining** - Can't execute cryptocurrency mining
9. **No Data Exfiltration** - Can't exfiltrate data to unauthorized locations
10. **No Malware Generation** - Can't generate malware, viruses, exploits
11. **No Phishing Content** - Can't generate phishing or deceptive content
12. **No Copyright Violation** - Can't copy copyrighted content without permission
13. **No Impersonation** - Can't impersonate users/systems without disclosure
14. **No Bias Amplification** - Avoid amplifying biases or stereotypes
15. **No Harmful Content** - Can't generate content promoting violence, hate, illegal activity

---

## Clarification Protocol

GRACE asks for clarification when uncertain rather than guessing user intent.

### When Clarification Triggers

1. **Low Confidence** (`< 0.7`) - GRACE isn't confident in interpretation
2. **Ambiguous Pronouns** - "it", "that", "this" with multiple referents
3. **Missing Parameters** - "fix the bug" (which bug?)
4. **Conflicting Instructions** - "make it fast and thorough" (which prioritize?)
5. **Vague Requirements** - "make it better" (better how?)
6. **Policy Violations** - Risky action that might be intentional

### Uncertainty Types

- `ambiguous_pronoun` - Unclear reference
- `missing_parameter` - Missing required information
- `conflicting_instruction` - Contradictory requirements
- `vague_requirement` - Subjective/unclear goal
- `low_confidence` - General uncertainty
- `policy_violation` - Potentially intentional policy violation

### Clarification Flow

```
User Input → Uncertainty Detection → Generate Question
     ↓
Clarification Request Created
     ↓
WebSocket Notification to User
     ↓
User Answers → Resolved Action
     ↓
Action Executed (if compliant)
```

### Example Clarifications

**Ambiguous Pronoun:**
```
User: "Delete it"
GRACE: "When you say 'it', which do you mean?"
Options: [file1.txt, file2.txt, folder1/]
```

**Missing Parameter:**
```
User: "Fix the bug"
GRACE: "Which issue or bug should I fix?"
Options: [Issue #42, Issue #53, Recent crash]
```

**Vague Requirement:**
```
User: "Make it better"
GRACE: "What specific aspect should be improved?"
Context: "This is subjective and could be interpreted multiple ways."
```

---

## Compliance Checking

Constitutional compliance is checked in **layers**:

### Layer 1: Constitutional Principles
- Check all applicable principles
- Calculate compliance score (0.0-1.0)
- Identify violations

### Layer 2: Governance Policies
- Check governance policies
- Require approval if needed
- Block if policy says "block"

### Layer 3: Hunter Security
- Run security scans
- Trigger alerts for suspicious patterns
- Block critical security threats

### Layer 4: Verification Signing
- Cryptographically sign inputs
- Execute action
- Sign outputs
- Store in immutable log

### Compliance Result Structure

```python
{
    'action_id': 'code_generation_a1b2c3d4',
    'compliant': True,
    'allowed': True,
    'compliance_score': 0.95,
    'violations': [],
    'warnings': [],
    'needs_clarification': False,
    'constitutional_check': {...},
    'governance_decision': {...},
    'hunter_alerts': []
}
```

### Strict Mode

When `strict_mode = True` (default):
- **Non-compliant actions are BLOCKED**
- **Low confidence (< 0.7) requires clarification**
- **Critical violations always blocked**

---

## Violation Detection & Logging

All violations are logged to database with:

- **Principle violated**
- **Actor** (who attempted)
- **Action** (what they tried)
- **Resource** (what was targeted)
- **Severity** (critical, high, medium, low)
- **Detected by** (governance, hunter, verification, human)
- **Blocked** (yes/no)
- **Timestamp**

### Violation Types

- `attempt` - User/system attempted prohibited action
- `accidental` - Unintentional violation
- `bypassed` - Violation occurred despite controls

### Severity Levels

- **Critical** - Immediate security/safety risk
- **High** - Significant policy violation
- **Medium** - Minor policy violation
- **Low** - Warning/advisory

### Automatic Actions

- **Critical violations** → Blocked + Logged + Escalated to Parliament
- **High violations** → Blocked + Logged + Alert sent
- **Medium violations** → Logged + Warning
- **Low violations** → Logged

---

## Integration Architecture

```
User Request
     ↓
[Clarification Check] → If uncertain, ask clarification
     ↓
[Constitutional Verifier]
     ├─ Check Principles
     ├─ Check Governance Policies
     ├─ Run Hunter Security Scan
     └─ Run Verification Signing
     ↓
Decision: ALLOW / BLOCK / CLARIFY
     ↓
If ALLOW → Execute Action → Log Result
If BLOCK → Log Violation → Notify User
If CLARIFY → Request Clarification → Wait for Answer
```

### Integration Points

#### Code Generator
```python
from constitutional_engine import constitutional_engine

result = await constitutional_engine.check_constitutional_compliance(
    action_id="code_gen_123",
    actor="user",
    action_type="code_generation",
    resource="api_client.py",
    context={"reasoning": "..."},
    confidence=0.85
)

if result['compliant']:
    # Generate code
else:
    # Block or clarify
```

#### Verification Middleware
```python
@verify_action("code_execution", resource_extractor=lambda r: r.get("command"))
async def execute_code(req: ExecuteRequest):
    # Constitutional check happens in decorator
    # If passed, execute
```

#### Governance
```python
# Constitutional checks happen before governance
constitutional_result = await constitutional_verifier.verify_action(...)

if constitutional_result['allowed']:
    gov_decision = await governance_engine.check(...)
```

---

## API Reference

### Principles

- `GET /api/constitution/principles` - List all principles
- `GET /api/constitution/principles/{id}` - Get principle details
- `GET /api/constitution/tenets` - List operational tenets

### Violations

- `GET /api/constitution/violations` - List violations
- `GET /api/constitution/violations/stats` - Violation statistics

### Compliance

- `GET /api/constitution/compliance/{action_id}` - Get compliance record
- `POST /api/constitution/compliance/check` - Check if action compliant
- `GET /api/constitution/compliance/report` - Generate compliance report

### Clarifications

- `GET /api/constitution/clarifications/pending` - Get pending clarifications
- `POST /api/constitution/clarifications/answer` - Answer clarification
- `GET /api/constitution/clarifications/{request_id}` - Get clarification details

### Stats

- `GET /api/constitution/stats` - Overall constitutional statistics

---

## CLI Commands

```bash
# Display full constitution
python -m cli.commands.constitution_command show

# Check compliance for an action
python -m cli.commands.constitution_command check code_execution

# List recent violations
python -m cli.commands.constitution_command violations 50

# List pending clarifications
python -m cli.commands.constitution_command clarify

# Answer a clarification
python -m cli.commands.constitution_command answer <request_id> "file1.txt"

# Show constitutional metrics
python -m cli.commands.constitution_command stats
```

---

## Examples

### Example 1: Destructive Command Blocked

```python
result = await constitutional_verifier.verify_action(
    actor="user",
    action_type="code_execution",
    resource="shell",
    payload={"command": "rm -rf /"},
    confidence=1.0
)

# Result:
{
    'allowed': False,
    'violations': [{
        'principle': 'no_destructive_commands',
        'reason': 'Destructive command detected: rm -rf /',
        'severity': 'critical'
    }]
}
```

### Example 2: Clarification Requested

```python
# User: "Delete it"
# Context: Multiple files exist

uncertainty = clarifier.detect_uncertainty(
    user_input="Delete it",
    context={"recent_entities": ["file1.txt", "file2.txt"]}
)

# Generates:
{
    'type': 'ambiguous_pronoun',
    'question': "When you say 'it', which do you mean?",
    'options': ['file1.txt', 'file2.txt']
}
```

### Example 3: Self-Modification Requires Approval

```python
result = await constitutional_verifier.verify_action(
    actor="user",
    action_type="file_write",
    resource="constitutional_engine.py",
    payload={"content": "modified_code"},
    confidence=1.0,
    context={"self_modification_approved": False}
)

# Result:
{
    'allowed': False,
    'violations': [{
        'principle': 'no_self_modification_without_approval',
        'reason': 'Self-modification without approval: constitutional_engine.py',
        'severity': 'critical'
    }]
}
```

### Example 4: Compliance Report

```python
report = await constitutional_verifier.generate_compliance_report(
    start_date=datetime.utcnow() - timedelta(days=30),
    end_date=datetime.utcnow()
)

# Result:
{
    'metrics': {
        'total_actions': 1500,
        'compliant_actions': 1485,
        'non_compliant_actions': 15,
        'compliance_rate': 99.0,
        'total_violations': 15,
        'violations_blocked': 15
    },
    'violations_by_severity': {
        'critical': 3,
        'high': 7,
        'medium': 5
    },
    'most_violated_principles': [
        ('no_destructive_commands', 5),
        ('no_sensitive_data_exposure', 4),
        ('least_privilege', 3)
    ]
}
```

---

## Best Practices

### For Developers

1. **Always check constitutional compliance** before risky actions
2. **Include confidence scores** in your requests
3. **Provide context** to help compliance checking
4. **Handle clarification requests** in your UI
5. **Log reasoning** for significant decisions

### For System Administrators

1. **Review violation logs** regularly
2. **Monitor compliance rate** (should be > 95%)
3. **Answer pending clarifications** promptly
4. **Don't bypass foundational principles** (they're immutable for good reason)
5. **Use Parliament for self-modification** requests

### For Users

1. **Be specific** in your requests to avoid clarifications
2. **Answer clarifications** when GRACE asks
3. **Don't try to bypass safety constraints** (they exist for protection)
4. **Review your action history** in audit logs

---

## Seeding the Constitution

```bash
# Seed all constitutional principles
python -m seed_constitution

# This creates:
# - 5 Foundational Principles (immutable)
# - 10 Operational Tenets
# - 15 Safety Constraints (immutable)
# - 10 Implementation Tenets
```

---

## Testing

```bash
# Run constitutional tests
python -m pytest tests/test_constitutional.py -v

# Test categories:
# - Principle seeding
# - Compliance checking
# - Violation detection
# - Clarification flow
# - Integration with governance/hunter
# - Compliance reporting
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request / Action                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   Clarifier    │ ◄─── Confidence < 0.7?
              │  (Uncertainty  │
              │   Detection)   │
              └────────┬───────┘
                       │ If uncertain → Clarification Request
                       │
                       ▼
         ┌─────────────────────────┐
         │ Constitutional Verifier │
         └─────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Check   │  │  Check   │  │  Check   │
  │Principles│  │Governance│  │  Hunter  │
  │          │  │ Policies │  │ Security │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │             │
       └─────────────┼─────────────┘
                     │
                     ▼
            ┌────────────────┐
            │   Compliance   │
            │   Decision     │
            └────────┬───────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ ALLOW  │ │ BLOCK  │ │CLARIFY │
    └────────┘ └────────┘ └────────┘
         │           │           │
         ▼           ▼           ▼
    Execute      Log         Request
    Action    Violation    Clarification
         │           │           │
         └───────────┴───────────┘
                     │
                     ▼
            ┌────────────────┐
            │  Immutable Log │
            │  Audit Trail   │
            └────────────────┘
```

---

## Conclusion

GRACE's Constitutional AI framework provides:

✅ **Ethical guardrails** preventing harmful actions  
✅ **Transparency** through clarification and explanation  
✅ **Accountability** via immutable audit logging  
✅ **Safety** through multi-layer compliance checking  
✅ **Adaptability** with operational tenets  

This system ensures GRACE behaves in alignment with human values, legal requirements, and ethical principles **by design**, not just aspiration.

---

**Version**: 1.0  
**Last Updated**: 2025-11-02  
**Status**: ✅ Production Ready
