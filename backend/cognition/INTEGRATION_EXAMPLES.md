# Integration Examples - Wiring Feedback Pipeline

Examples of integrating FeedbackIntegrator into existing GRACE components.

---

## Example 1: Reflection Service Integration

### Before (reflection.py)
```python
async def generate_reflection(self):
    # ... generate reflection ...
    
    reflection = Reflection(
        summary=summary,
        insight=insight,
        confidence=0.5
    )
    session.add(reflection)
    await session.commit()
    print(f"✓ Generated reflection: {summary}")
```

### After (reflection.py)
```python
from .cognition.integration_helpers import integrate_reflection_output

async def generate_reflection(self):
    # ... generate reflection ...
    
    # Store in database (existing)
    reflection = Reflection(
        summary=summary,
        insight=insight,
        confidence=0.5
    )
    session.add(reflection)
    await session.commit()
    
    # Integrate into feedback pipeline (NEW)
    memory_ref = await integrate_reflection_output(
        loop_id=f"reflection_{datetime.utcnow().timestamp()}",
        reflection_summary=summary,
        insight=insight,
        confidence=0.7,
        metadata={
            'top_words': top_words,
            'user_msgs': user_msgs,
            'grace_msgs': grace_msgs
        }
    )
    
    if memory_ref:
        print(f"✓ Generated reflection: {summary} → {memory_ref}")
    else:
        print(f"✓ Generated reflection: {summary} (governance blocked storage)")
```

---

## Example 2: Meta-Loop Engine Integration

### Patch for meta_loop.py
```python
# Add import at top
from .cognition.integration_helpers import integrate_meta_loop_output

# In analyze_meta_patterns() or similar function
async def analyze_meta_patterns(self):
    # ... existing meta-loop analysis ...
    
    # After analysis completes
    memory_ref = await integrate_meta_loop_output(
        loop_id=f"meta_{self.cycle_id}",
        analysis_result={
            'patterns': patterns,
            'anomalies': anomalies,
            'recommendations': recommendations
        },
        confidence=self.calculate_confidence(),
        anomalies=anomalies,
        patterns=patterns,
        metadata={
            'cycle': self.cycle_number,
            'analysis_type': 'meta_pattern',
            'duration_ms': processing_time
        }
    )
    
    return memory_ref
```

---

## Example 3: Causal Analyzer Integration

### Patch for causal_analyzer.py
```python
from .cognition.integration_helpers import integrate_causal_analysis
from .cognition import OutputType

async def analyze_causality(self, start_time, end_time):
    # ... build causal graph ...
    
    graph = CausalGraph()
    await graph.build_from_events(start_time, end_time)
    influential = graph.get_most_influential_events(limit=10)
    
    # Extract insights
    insights = []
    for event in influential:
        insights.append(f"Event {event['event_type']} influences {event['downstream_count']} events")
    
    # Integrate
    memory_ref = await integrate_causal_analysis(
        loop_id=f"causal_{datetime.utcnow().timestamp()}",
        causal_graph=graph.to_dict(),
        insights=insights,
        confidence=0.8,
        influential_events=influential,
        metadata={
            'time_window': f"{start_time} to {end_time}",
            'total_events': len(graph.nodes),
            'edge_count': len(graph.edges)
        }
    )
    
    return memory_ref
```

---

## Example 4: Code Generator Integration

### New specialist using feedback pipeline
```python
from cognition import GraceLoopOutput, OutputType, feedback_integrator

class CodeGenerator:
    async def generate_code(self, task_description, language="python"):
        # ... code generation logic ...
        
        generated_code = "..."
        
        # Create standardized output
        output = GraceLoopOutput(
            loop_id=f"codegen_{uuid.uuid4()}",
            component="code_generator",
            output_type=OutputType.GENERATION,
            result=generated_code,
            confidence=self.estimate_confidence(),
            importance=0.7,
            metadata={
                'language': language,
                'task': task_description,
                'lines': generated_code.count('\n')
            }
        )
        
        # Add citations if using knowledge
        if self.knowledge_used:
            output.add_citation(
                source="code_patterns_db",
                confidence=0.85,
                excerpt="Similar pattern from repository X"
            )
        
        # Check for issues
        if self.syntax_check_failed:
            output.add_error("Syntax validation failed")
        if self.has_warnings:
            output.add_warning("Unused imports detected")
        
        # Integrate through feedback pipeline
        memory_ref = await feedback_integrator.integrate(output)
        
        return {
            'code': generated_code,
            'memory_ref': memory_ref,
            'confidence': output.confidence
        }
```

---

## Example 5: Using Auto-Integration Decorator

### Automatic integration wrapper
```python
from cognition.integration_helpers import auto_integrate
from cognition import OutputType

@auto_integrate(
    component_name="decision_maker",
    output_type=OutputType.DECISION,
    importance=0.8
)
async def make_critical_decision(input_data):
    # ... decision logic ...
    
    decision = "Approve deployment"
    confidence = 0.9
    
    # Return dict with required fields
    return {
        'loop_id': f"decision_{datetime.utcnow().timestamp()}",
        'result': decision,
        'confidence': confidence,
        'evidence': [
            "All tests passed",
            "Performance benchmarks met",
            "Security scan clean"
        ],
        'metadata': {
            'deployment_target': 'production',
            'risk_level': 'medium'
        }
    }

# Usage
result = await make_critical_decision(input_data)
print(f"Decision: {result['result']}")
print(f"Stored as: {result['memory_ref']}")
```

---

## Example 6: Hunter Integration

### Patch for hunter.py
```python
from cognition import GraceLoopOutput, OutputType, feedback_integrator

async def inspect(self, actor, action, resource, payload):
    # ... existing inspection logic ...
    
    # After inspection completes
    output = GraceLoopOutput(
        loop_id=f"hunter_{uuid.uuid4()}",
        component="hunter",
        output_type=OutputType.OBSERVATION,
        result={
            'verdict': verdict,
            'violations': violations,
            'risk_score': risk_score
        },
        confidence=0.95,  # Hunter is high-confidence
        importance=0.9,  # Security observations are important
        metadata={
            'actor': actor,
            'action': action,
            'resource': resource
        }
    )
    
    # Add violations as errors
    for violation in violations:
        output.add_error(f"Policy violation: {violation}")
    
    # Integrate
    memory_ref = await feedback_integrator.integrate(output)
    
    # Hunter violations should always escalate
    if violations and not memory_ref:
        # Escalation already handled by feedback_integrator
        await self.alert_security_team(violations)
```

---

## Example 7: Parliament Voting Integration

### Patch for parliament_engine.py
```python
from cognition.integration_helpers import integrate_specialist_output
from cognition import OutputType

async def conduct_vote(self, proposal):
    # ... voting logic ...
    
    # After vote completes
    memory_ref = await integrate_specialist_output(
        specialist_name="parliament",
        loop_id=f"parliament_vote_{proposal.id}",
        result={
            'proposal': proposal.description,
            'outcome': outcome,
            'votes': vote_tallies,
            'consensus_strength': consensus_score
        },
        output_type=OutputType.DECISION,
        confidence=consensus_score,
        importance=0.95,  # Parliament decisions are critical
        evidence=[
            f"Delegate votes: {vote_tallies}",
            f"Quorum met: {quorum_met}",
            f"Threshold: {threshold}"
        ],
        metadata={
            'proposal_id': proposal.id,
            'delegate_count': len(delegates),
            'voting_duration_ms': duration
        }
    )
    
    return outcome, memory_ref
```

---

## Example 8: Subscribing to Feedback Events

### Event handlers for downstream consumers
```python
from trigger_mesh import trigger_mesh

async def on_feedback_recorded(event):
    """Handle FeedbackRecorded events"""
    payload = event.payload
    
    print(f"✓ Feedback recorded: {payload['component']} → {payload['memory_ref']}")
    print(f"  Trust: {payload['trust_score']:.2f}")
    print(f"  Compliance: {payload['compliance_score']:.2f}")
    
    # Trigger downstream actions
    if payload['trust_score'] > 0.9:
        # High-trust outputs might trigger additional processing
        await trigger_advanced_analysis(payload['memory_ref'])

async def on_constitutional_violation(event):
    """Handle ConstitutionalViolation events"""
    payload = event.payload
    
    print(f"⚠ Constitutional violation: {payload['component']}")
    print(f"  Severity: {payload['severity']}")
    print(f"  Reason: {payload['reason']}")
    
    # Alert monitoring systems
    await alert_compliance_team(payload)

async def on_governance_escalation(event):
    """Handle GovernanceEscalation events"""
    payload = event.payload
    
    print(f"📋 Escalation required: {payload['component']}")
    print(f"  Reason: {payload['escalation_reason']}")
    
    # Create Parliament ticket
    ticket = await create_parliament_ticket(payload)
    payload['parliament_ticket_id'] = ticket.id

# Wire up subscriptions
trigger_mesh.subscribe("cognition.feedback_recorded", on_feedback_recorded)
trigger_mesh.subscribe("governance.constitutional_violation", on_constitutional_violation)
trigger_mesh.subscribe("governance.escalation_required", on_governance_escalation)
```

---

## Complete Integration Workflow

```python
# 1. Component produces output
result = await my_specialist.process(input_data)

# 2. Create GraceLoopOutput
from cognition import GraceLoopOutput, OutputType

output = GraceLoopOutput(
    loop_id=f"specialist_{timestamp}",
    component="my_specialist",
    output_type=OutputType.REASONING,
    result=result,
    confidence=0.8,
    importance=0.6
)

# 3. Add metadata
output.add_citation("source", 0.9, "Evidence")
output.evidence.append("Observation X")

# 4. Integrate
from cognition import feedback_integrator

memory_ref = await feedback_integrator.integrate(output)

# 5. Handle result
if memory_ref:
    # Success - output stored
    return {'success': True, 'memory_ref': memory_ref}
else:
    # Blocked by governance
    return {'success': False, 'reason': 'constitutional_block'}
```

---

## Testing Your Integration

```python
# test_my_specialist_integration.py
import pytest
from cognition import feedback_integrator

@pytest.mark.asyncio
async def test_my_specialist_integration():
    # Run your specialist
    result = await my_specialist.process(test_input)
    
    # Should produce GraceLoopOutput
    assert hasattr(result, 'loop_id')
    assert hasattr(result, 'component')
    
    # Should integrate
    memory_ref = await feedback_integrator.integrate(result)
    
    # Should return memory ref
    assert memory_ref is not None
    assert memory_ref.startswith('mem_')
```

---

**All specialists → One pipeline → Constitutional governance → Auditable memory**
