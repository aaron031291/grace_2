# QuorumEngine - Trust-Weighted Specialist Consensus

## Overview

The QuorumEngine coordinates multiple specialist components (reflection, hunter, meta, causal, MLDL) to reach consensus on complex decisions through trust-weighted voting.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      QuorumEngine                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Reflection   │  │   Hunter     │  │    Meta      │      │
│  │  Proposal    │  │  Proposal    │  │  Proposal    │ ...  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │   Scoring   │                          │
│                    │   Engine    │                          │
│                    └──────┬──────┘                          │
│                           │                                 │
│           ┌───────────────┼───────────────┐                 │
│           │               │               │                 │
│    ┌──────▼─────┐  ┌──────▼─────┐  ┌──────▼─────┐          │
│    │  Majority  │  │  Softmax   │  │  Min Risk  │          │
│    │   Vote     │  │  Weighted  │  │   Vote     │          │
│    └──────┬─────┘  └──────┬─────┘  └──────┬─────┘          │
│           │               │               │                 │
│           └───────────────┴───────────────┘                 │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │  Consensus  │                          │
│                    │  Decision   │                          │
│                    └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## Decision Strategies

### 1. Majority Vote
Simple highest-score-wins strategy:
- Fastest decision making
- Clear winner selection
- Best for low-risk decisions

### 2. Softmax Weighted
Probabilistic blend with temperature control:
- Smooth score distribution
- Favors highest confidence
- Temperature parameter controls decisiveness
- Best for medium-risk decisions

### 3. Minimum Risk
Safety-first under governance constraints:
- Validates constitutional compliance
- Checks policy constraints
- Risk-adjusts confidence scores
- Best for high-risk decisions
- Mandatory for CRITICAL risk level

### 4. Unanimous
All specialists must agree:
- Highest confidence threshold
- Escalates to Parliament on disagreement
- Best for irreversible actions

## Scoring Components

Each proposal is scored based on:

1. **Trust Score (30%)** - Component reputation
   - Historical reliability
   - Updated via exponential moving average
   - Range: 0.0-1.0

2. **Track Record (25%)** - Past accuracy
   - Last 100 decision outcomes
   - Success rate calculation
   - Component-specific

3. **Recency Weight (15%)** - Recent performance
   - Recent wins count more
   - Temporal decay function
   - Adapts to changing conditions

4. **Confidence (20%)** - Output confidence
   - Self-reported certainty
   - Penalized for low scores in high-risk tasks
   - Range: 0.0-1.0

5. **Governance Bonus (10%)** - Compliance multiplier
   - Constitutional compliance: 1.1x
   - Each compliant policy tag: +5%
   - Non-compliant: 0.5x penalty

## Usage

### Basic Deliberation

```python
from cognition.QuorumEngine import QuorumEngine
from cognition.models import DecisionTask, SpecialistProposal, DecisionStrategy

engine = QuorumEngine()

# Create decision task
task = DecisionTask(
    task_id="decide_deployment",
    description="Should we deploy new model?",
    context={"model_id": "gpt-4", "version": "2.0"},
    strategy=DecisionStrategy.SOFTMAX_WEIGHTED
)

# Add specialist proposals
task.specialist_proposals = [
    reflection_proposal,
    hunter_proposal,
    meta_proposal,
    causal_proposal
]

# Deliberate
decision = engine.deliberate(task)

print(f"Decision: {decision.rationale}")
print(f"Confidence: {decision.confidence:.2f}")
print(f"Winner: {decision.chosen_proposal.component}")
```

### High-Risk Decisions

```python
task = DecisionTask(
    task_id="critical_action",
    description="Execute production change",
    context={},
    strategy=DecisionStrategy.MIN_RISK,
    risk_level=RiskLevel.CRITICAL,
    constraints=['safety_policy', 'data_privacy', 'reversibility']
)

decision = engine.deliberate(task)

if decision.governance_validated:
    execute(decision.chosen_proposal)
else:
    escalate_to_parliament(decision)
```

### Trust Updates

```python
# After executing decision
outcome_success = verify_decision_outcome(decision)

# Update trust scores
engine.update_specialist_trust(
    specialist=decision.chosen_proposal.component,
    outcome_success=outcome_success
)
```

### Decision Explanation

```python
explanation = engine.explain(decision)

# Returns:
{
    'task_id': 'decide_deployment',
    'strategy': 'softmax_weighted',
    'winner': {
        'component': 'reflection',
        'confidence': 0.92,
        'constitutional_compliance': True
    },
    'weights': {
        'reflection': 0.65,
        'hunter': 0.25,
        'meta': 0.10
    },
    'rationale': 'Softmax-weighted consensus: reflection selected...',
    'voting_summary': {
        'winner': 'reflection',
        'probability': 0.65,
        'temperature': 0.5,
        'score_distribution': {...}
    }
}
```

## Integration Points

### 1. With MLDLSpecialist
```python
# Specialist evaluates task
mldl_output = mldl_specialist.evaluate(task)
proposal = SpecialistProposal(
    specialist_name='mldl',
    output=mldl_output,
    trust_score=engine.specialist_trust['mldl'],
    track_record=engine.get_specialist_track_record('mldl'),
    recency_weight=0.9
)
task.specialist_proposals.append(proposal)
```

### 2. With Parliament
```python
decision = engine.deliberate(task)

if decision.voting_summary.get('requires_escalation'):
    # Escalate to Parliament
    parliament_vote = parliament.vote(
        motion=decision.chosen_proposal,
        dissent=decision.dissent
    )
```

### 3. With Governance
```python
# Pre-filter proposals by governance
valid_proposals = [
    p for p in all_proposals
    if governance.verify(p.output).compliant
]
task.specialist_proposals = valid_proposals
decision = engine.deliberate(task)
```

## Decision Task Model

```python
@dataclass
class DecisionTask:
    task_id: str
    description: str
    context: Dict[str, Any]
    specialist_proposals: List[SpecialistProposal]
    constraints: List[str]  # Governance requirements
    risk_level: RiskLevel = RiskLevel.MEDIUM
    deadline: Optional[datetime] = None
    strategy: DecisionStrategy = DecisionStrategy.SOFTMAX_WEIGHTED
```

## Consensus Decision Model

```python
@dataclass
class ConsensusDecision:
    task_id: str
    chosen_proposal: GraceLoopOutput
    rationale: str
    weights: Dict[str, float]
    dissent: List[GraceLoopOutput]
    confidence: float
    governance_validated: bool
    strategy_used: DecisionStrategy
    voting_summary: Dict[str, Any]
```

## Best Practices

1. **Strategy Selection**
   - Use MAJORITY for fast, low-stakes decisions
   - Use SOFTMAX_WEIGHTED for balanced consensus
   - Use MIN_RISK for high-stakes, regulated actions
   - Use UNANIMOUS for irreversible operations

2. **Risk Management**
   - Always set appropriate risk_level
   - Add governance constraints for CRITICAL tasks
   - Review dissenting opinions before execution

3. **Trust Maintenance**
   - Update trust scores after each decision
   - Monitor track records over time
   - Adjust specialist weights based on performance

4. **Transparency**
   - Use explain() for audit trails
   - Log all decisions with full context
   - Track voting patterns over time

## Testing

```bash
cd grace_rebuild/backend
pytest tests/test_quorum_engine.py -v
```

## Metrics

Track these metrics for system health:

- **Consensus Rate**: % of decisions reaching agreement
- **Escalation Rate**: % requiring Parliament intervention
- **Trust Drift**: Change in specialist trust over time
- **Strategy Distribution**: Which strategies are used most
- **Decision Latency**: Time to reach consensus

## Future Enhancements

- [ ] Dynamic strategy selection based on task properties
- [ ] Multi-round deliberation for complex decisions
- [ ] Confidence calibration across specialists
- [ ] Learning-based trust updates
- [ ] Parallel voting with tie-breaking
