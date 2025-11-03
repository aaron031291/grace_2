# Feedback Pipeline - Classes 6-7

**Constitutional Governance & Deterministic Write Path**

---

## 🎯 Overview

The Feedback Pipeline is GRACE's deterministic write path ensuring all specialist outputs:
1. **Pass constitutional validation** (GovernancePrimeDirective)
2. **Receive trust scoring** (MemoryScoreModel simulation)
3. **Get stored in memory** (LoopMemoryBank)
4. **Emit integration events** (trigger_mesh)

**One pipeline. Zero exceptions. Complete auditability.**

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ALL SPECIALIST OUTPUTS                    │
│  Reflection │ Meta-Loop │ Causal │ Hunter │ Parliament      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  GraceLoopOutput     │  ◄─── Universal schema
              │  (Standard Format)   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────────────┐
              │  GovernancePrimeDirective    │
              │  Constitutional Validation   │
              └──────────┬───────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    [BLOCK]          [ESCALATE]         [GO/DEGRADE]
        │                │                │
        ▼                ▼                ▼
     Reject      → Parliament     ┌──────────────┐
                                  │ Trust Scoring │
                                  └──────┬────────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │ Memory Store │
                                  └──────┬────────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │ Event Emit   │
                                  └──────────────┘
```

---

## 🏛️ Class 6: GovernancePrimeDirective

**Purpose**: Constitutional gate preventing violations before execution

### Core Responsibilities

1. **Validate constitutional compliance**
   - Check against 30 constitutional principles
   - Enforce safety constraints
   - Detect policy violations

2. **Issue governance verdicts**
   - `GO`: Full approval
   - `BLOCK`: Denied
   - `DEGRADE`: Allowed with reduced trust
   - `ESCALATE`: Requires human/Parliament review

3. **Attach governance tags**
   - `requires_human_review`
   - `restricted_context`
   - `export_controls`
   - `high_risk`

4. **Determine remediation actions**
   - `REDACT`: Remove sensitive info
   - `DOWNGRADE`: Reduce trust
   - `BLOCK`: Prevent execution
   - `ESCALATE`: Send to Parliament

### API

```python
from cognition import governance_prime_directive, GraceLoopOutput

# Validate output
verdict = await governance_prime_directive.validate_against_constitution(output)

# Check decision
if verdict.is_approved():
    print(f"Compliance: {verdict.compliance_score:.2%}")
elif verdict.needs_escalation():
    print(f"Escalate: {verdict.reason}")
else:
    print(f"Blocked: {verdict.reason}")

# Get explanation
explanation = governance_prime_directive.explain(verdict)
print(explanation)
```

### GovernanceVerdict Schema

```python
@dataclass
class GovernanceVerdict:
    decision: GovernanceDecision  # GO, BLOCK, DEGRADE, ESCALATE
    tags: List[str]
    remediation_actions: List[RemediationAction]
    reason: str
    constitutional_checks: List[int]  # Principle IDs
    compliance_score: float  # 0.0-1.0
    severity: str  # info, warning, critical
    requires_approval: bool
    safe_to_store: bool
```

---

## 🔄 Class 7: FeedbackIntegrator

**Purpose**: Deterministic write path for all loop outputs

### Processing Flow

```
1. Receive GraceLoopOutput
   ↓
2. Constitutional Validation
   ├─ BLOCK → Emit violation event → Return None
   ├─ ESCALATE → Emit escalation event → Continue
   └─ GO/DEGRADE → Continue
   ↓
3. Compute Trust Score
   - Base from confidence
   - Adjust for compliance
   - Boost from evidence
   - Penalize for errors
   ↓
4. Store in Memory (if approved)
   - Call LoopMemoryBank.store()
   - Get memory reference
   ↓
5. Emit Events
   - FeedbackRecorded
   - TrustScoreUpdated
   - ConstitutionalViolation (if blocked)
   - GovernanceEscalation (if escalated)
   ↓
6. Return memory_ref or None
```

### API

```python
from cognition import feedback_integrator, GraceLoopOutput, OutputType

# Create output
output = GraceLoopOutput(
    loop_id="reflection_001",
    component="reflection",
    output_type=OutputType.REFLECTION,
    result={"summary": "User engagement increased", "insight": "..."},
    confidence=0.85,
    importance=0.7
)

# Integrate
memory_ref = await feedback_integrator.integrate(output)

if memory_ref:
    print(f"Stored: {memory_ref}")
else:
    print("Blocked by governance")
```

### Trust Scoring Algorithm

```python
trust_score = (
    confidence * 0.4 +           # 40% from confidence
    compliance * 0.3 +           # 30% from constitutional compliance
    evidence_quality * 0.2 +     # 20% from citation quality
    quality_score * 0.1          # 10% from explicit quality
) - error_penalty - warning_penalty

if verdict.decision == DEGRADE:
    trust_score *= 0.8  # 20% reduction
```

---

## 📡 Events Emitted

### 1. FeedbackRecorded
```python
{
    'loop_id': 'reflection_001',
    'component': 'reflection',
    'memory_ref': 'mem_...',
    'trust_score': 0.82,
    'compliance_score': 0.95,
    'timestamp': '2025-01-15T10:30:00Z'
}
```

### 2. ConstitutionalViolation
```python
{
    'loop_id': 'action_005',
    'violation_type': 'safety_constraint',
    'principle_ids': [3, 7, 15],
    'severity': 'critical',
    'action_blocked': True
}
```

### 3. TrustScoreUpdated
```python
{
    'loop_id': 'causal_012',
    'trust_score': 0.88,
    'confidence': 0.85,
    'evidence_quality': 0.92
}
```

### 4. GovernanceEscalation
```python
{
    'loop_id': 'decision_007',
    'escalation_reason': 'Low confidence requires review',
    'verdict': {...},
    'parliament_ticket_id': 'ticket_123'
}
```

---

## 🔌 Integration Points

### 1. Reflection Service

```python
# In reflection.py
from cognition.integration_helpers import integrate_reflection_output

async def generate_reflection(self):
    # ... existing reflection logic ...
    
    # Integration point
    memory_ref = await integrate_reflection_output(
        loop_id=f"reflection_{datetime.utcnow().timestamp()}",
        reflection_summary=summary,
        insight=insight,
        confidence=0.7,
        metadata={'top_words': top_words}
    )
    
    if memory_ref:
        print(f"✓ Reflection stored: {memory_ref}")
```

### 2. Meta-Loop Engine

```python
# In meta_loop.py
from cognition.integration_helpers import integrate_meta_loop_output

async def analyze_loop(self):
    # ... meta-loop analysis ...
    
    memory_ref = await integrate_meta_loop_output(
        loop_id=f"meta_{analysis_id}",
        analysis_result=result,
        confidence=0.8,
        anomalies=anomalies,
        patterns=patterns,
        metadata={'cycle': cycle_number}
    )
```

### 3. Causal Analyzer

```python
# In causal_analyzer.py
from cognition.integration_helpers import integrate_causal_analysis

async def analyze_causality(self):
    # ... causal analysis ...
    
    memory_ref = await integrate_causal_analysis(
        loop_id=f"causal_{analysis_id}",
        causal_graph=graph_data,
        insights=insights,
        confidence=0.75,
        influential_events=top_events
    )
```

### 4. Generic Specialist

```python
# Any specialist
from cognition.integration_helpers import integrate_specialist_output
from cognition import OutputType

memory_ref = await integrate_specialist_output(
    specialist_name="code_generator",
    loop_id=f"codegen_{task_id}",
    result=generated_code,
    output_type=OutputType.GENERATION,
    confidence=0.9,
    importance=0.7,
    warnings=["Unused import detected"]
)
```

---

## 🧪 Testing

```bash
# Run feedback pipeline tests
cd grace_rebuild/backend
pytest tests/test_feedback_pipeline.py -v

# Test categories
# - Constitutional validation
# - Trust computation
# - Memory storage
# - Event emission
# - End-to-end pipeline
```

### Test Coverage

- ✅ Approve compliant outputs
- ✅ Block non-compliant outputs
- ✅ Escalate low-confidence outputs
- ✅ Degrade outputs with errors
- ✅ Detect sensitive content
- ✅ Compute trust scores accurately
- ✅ Apply trust degradation
- ✅ Boost trust for evidence quality
- ✅ Emit all event types
- ✅ End-to-end pipeline flow

---

## 📊 Metrics

### Governance Metrics
- **Total validations**: Count of outputs validated
- **Approval rate**: % of GO decisions
- **Block rate**: % of BLOCK decisions
- **Escalation rate**: % requiring review
- **Average compliance score**: Mean compliance across outputs

### Trust Metrics
- **Average trust score**: Mean trust across all outputs
- **Trust distribution**: Histogram of trust scores
- **Evidence quality**: Average citation confidence
- **Error penalty impact**: Trust reduction from errors

### Storage Metrics
- **Storage rate**: % of outputs stored in memory
- **Average importance**: Mean importance of stored memories
- **Memory growth rate**: Memories/hour

---

## 🔒 Constitutional Enforcement

### Non-Negotiable Principles

1. **Safety** - No destructive actions (rm -rf, DROP TABLE, etc.)
2. **Legality** - No illegal operations
3. **Sovereignty** - User control always maintained
4. **Transparency** - Uncertainty disclosed
5. **Privacy** - No sensitive data exposure

### Compliance Thresholds

- **Safety-critical operations**: 90% compliance required
- **Legal operations**: 95% compliance required
- **High-risk tagging**: <85% compliance
- **Clarification request**: <70% confidence

---

## 🎯 Integration Checklist

- [x] GovernancePrimeDirective implemented
- [x] FeedbackIntegrator implemented
- [x] Event definitions created
- [x] Integration helpers provided
- [x] Tests written and passing
- [ ] Wire into reflection.py
- [ ] Wire into meta_loop.py
- [ ] Wire into causal_analyzer.py
- [ ] Wire into all specialists
- [ ] Monitor event emissions
- [ ] Validate constitutional coverage

---

## 🚀 Quick Start

```python
# 1. Import components
from cognition import (
    GraceLoopOutput,
    OutputType,
    feedback_integrator,
    governance_prime_directive
)

# 2. Create output
output = GraceLoopOutput(
    loop_id="my_loop_001",
    component="my_component",
    output_type=OutputType.DECISION,
    result="My decision result",
    confidence=0.85,
    importance=0.7
)

# 3. Add evidence
output.add_citation("source_1", 0.9, "Supporting evidence")
output.evidence.append("Observed pattern X")

# 4. Integrate
memory_ref = await feedback_integrator.integrate(output)

# 5. Handle result
if memory_ref:
    print(f"✓ Integrated: {memory_ref}")
else:
    print("✗ Blocked by governance")
```

---

## 📝 Summary

**Classes 6-7 deliver:**

✅ **Constitutional gate** enforcing ethical AI  
✅ **Trust scoring** for all outputs  
✅ **Deterministic write path** - one pipeline, zero exceptions  
✅ **Event-driven integration** with trigger_mesh  
✅ **Complete auditability** via immutable_log  
✅ **Parliament escalation** for uncertain cases  

**Every output validated. Every action governed. Every decision audited.**

This is Constitutional AI in production. 🏛️⚖️
