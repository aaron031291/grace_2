# Quick Integration Guide - Feedback Pipeline

**3-Step Integration for Any GRACE Component**

---

## Option 1: Use Helper Functions (Recommended)

### Step 1: Import Helper
```python
from cognition.integration_helpers import integrate_specialist_output
from cognition import OutputType
```

### Step 2: Call at End of Processing
```python
memory_ref = await integrate_specialist_output(
    specialist_name="your_component_name",
    loop_id=f"component_{timestamp}",
    result=your_output_data,
    output_type=OutputType.REASONING,  # or DECISION, ACTION, etc.
    confidence=0.85,
    importance=0.7
)
```

### Step 3: Handle Result
```python
if memory_ref:
    print(f"✓ Stored: {memory_ref}")
else:
    print("✗ Governance blocked")
```

---

## Option 2: Direct Pipeline Use

### Step 1: Import Pipeline
```python
from cognition import GraceLoopOutput, OutputType, feedback_integrator
```

### Step 2: Create Output
```python
output = GraceLoopOutput(
    loop_id="my_loop_001",
    component="my_component",
    output_type=OutputType.DECISION,
    result=my_result_data,
    confidence=0.85,
    importance=0.7
)

# Add optional metadata
output.add_citation("source", 0.9, "Evidence")
output.add_warning("Minor issue detected")
```

### Step 3: Integrate
```python
memory_ref = await feedback_integrator.integrate(output)
```

---

## Specific Component Helpers

### Reflection Integration
```python
from cognition.integration_helpers import integrate_reflection_output

memory_ref = await integrate_reflection_output(
    loop_id=f"reflection_{timestamp}",
    reflection_summary=summary,
    insight=insight,
    confidence=0.7,
    metadata={'top_words': top_words}
)
```

### Meta-Loop Integration
```python
from cognition.integration_helpers import integrate_meta_loop_output

memory_ref = await integrate_meta_loop_output(
    loop_id=f"meta_{analysis_id}",
    analysis_result=result_dict,
    confidence=0.8,
    anomalies=detected_anomalies,
    patterns=discovered_patterns,
    metadata={'cycle': cycle_number}
)
```

### Causal Analysis Integration
```python
from cognition.integration_helpers import integrate_causal_analysis

memory_ref = await integrate_causal_analysis(
    loop_id=f"causal_{analysis_id}",
    causal_graph=graph_data,
    insights=insights_list,
    confidence=0.75,
    influential_events=top_events
)
```

---

## OutputType Options

```python
from cognition import OutputType

OutputType.REASONING      # Logical reasoning/analysis
OutputType.DECISION       # Decision/judgment
OutputType.OBSERVATION    # Observation/monitoring
OutputType.ACTION         # Action/command
OutputType.REFLECTION     # Self-reflection
OutputType.PREDICTION     # Future prediction
OutputType.GENERATION     # Code/content generation
```

---

## Event Subscriptions

### Subscribe to Feedback Events
```python
from trigger_mesh import trigger_mesh

async def on_feedback(event):
    print(f"Feedback recorded: {event.payload['memory_ref']}")
    print(f"Trust score: {event.payload['trust_score']}")

trigger_mesh.subscribe("cognition.feedback_recorded", on_feedback)
```

### Subscribe to Violations
```python
async def on_violation(event):
    print(f"⚠ Violation: {event.payload['reason']}")
    print(f"Severity: {event.payload['severity']}")

trigger_mesh.subscribe("governance.constitutional_violation", on_violation)
```

---

## Full Example: Code Generator

```python
from cognition import GraceLoopOutput, OutputType, feedback_integrator

class CodeGenerator:
    async def generate(self, task_description):
        # 1. Generate code
        code = self.generate_code(task_description)
        
        # 2. Create output
        output = GraceLoopOutput(
            loop_id=f"codegen_{datetime.utcnow().timestamp()}",
            component="code_generator",
            output_type=OutputType.GENERATION,
            result=code,
            confidence=self.estimate_confidence(),
            importance=0.7
        )
        
        # 3. Add metadata
        if self.syntax_errors:
            output.add_error("Syntax validation failed")
        if self.warnings:
            output.add_warning("Unused imports detected")
        
        # 4. Integrate
        memory_ref = await feedback_integrator.integrate(output)
        
        # 5. Return with reference
        return {
            'code': code,
            'memory_ref': memory_ref,
            'confidence': output.confidence
        }
```

---

## Troubleshooting

### Output Blocked?
Check the constitutional compliance:
```python
from cognition import governance_prime_directive

verdict = await governance_prime_directive.validate_against_constitution(output)
explanation = governance_prime_directive.explain(verdict)
print(explanation)
```

### Low Trust Score?
Improve by:
- Adding high-quality citations
- Increasing confidence
- Reducing errors/warnings
- Providing evidence

### Need Escalation?
Outputs with <70% confidence automatically escalate to Parliament for review.

---

## Testing Your Integration

```python
import pytest
from cognition import feedback_integrator

@pytest.mark.asyncio
async def test_my_integration():
    # Create test output
    output = create_test_output()
    
    # Integrate
    memory_ref = await feedback_integrator.integrate(output)
    
    # Verify
    assert memory_ref is not None
    assert memory_ref.startswith('mem_')
```

---

## Summary

**Three lines to integrate any component:**

```python
from cognition.integration_helpers import integrate_specialist_output
from cognition import OutputType

memory_ref = await integrate_specialist_output(
    specialist_name="my_component",
    loop_id=f"my_{timestamp}",
    result=my_output,
    output_type=OutputType.DECISION,
    confidence=0.85
)
```

**That's it!** Constitutional validation, trust scoring, memory storage, and event emission all handled automatically.
