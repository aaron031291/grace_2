# Unified Logic - Complete Implementation

## Overview

The Unified Logic is Grace's brain that stitches together all layers and loops into one coherent decision. It synthesizes inputs from Governance, AVN, MLDL Quorum, Learning, and Memory to produce unified decisions.

**This is a production-ready implementation with all three phases complete.**

## Architecture

### Core Components

1. **UnifiedDecisionEngine** ([unified_decision_engine.py](file:///c:/Users/aaron/grace_2/backend/unified_logic/unified_decision_engine.py))
   - Phase 1: Define contracts (inputs/outputs)
   - Phase 2: Aggregation logic with weighted scoring
   - Complete synthesis logic with override rules

2. **DecisionRouter** ([decision_router.py](file:///c:/Users/aaron/grace_2/backend/unified_logic/decision_router.py))
   - Phase 3: Route decisions to consumers
   - Event emission via trigger mesh
   - Parallel routing to all targets

3. **CompleteIntegration** ([complete_integration.py](file:///c:/Users/aaron/grace_2/backend/unified_logic/complete_integration.py))
   - High-level API for decision making
   - Subsystem input collection
   - End-to-end orchestration

## Three-Phase Implementation

### Phase 1: Define Contracts

**Input Contracts:**

```python
@dataclass
class GovernanceInput:
    """Input from Governance system"""
    approved: bool
    approval_id: Optional[str]
    violated_policies: List[str]
    required_approvals: int
    received_approvals: int
    reasoning: str
    trust_score: float

@dataclass
class AVNInput:
    """Input from AVN (health monitoring)"""
    health_state: str  # healthy, degraded, critical
    anomalies_detected: List[Dict[str, Any]]
    severity: str  # none, low, medium, high, critical
    recommended_action: Optional[str]
    confidence: float

@dataclass
class MLDLQuorumInput:
    """Input from MLDL Quorum consensus"""
    consensus_reached: bool
    consensus_action: Optional[str]
    vote_breakdown: Dict[str, int]
    confidence: float
    reasoning: List[str]

@dataclass
class LearningInput:
    """Input from Learning system"""
    insights: List[str]
    pattern_confidence: float
    recommended_adjustments: List[str]
    similar_past_outcomes: List[Dict[str, Any]]

@dataclass
class MemoryInput:
    """Input from Memory system"""
    relevant_context: List[Dict[str, Any]]
    trust_scores: Dict[str, float]
    contradictions_found: List[str]
```

**Output Contract:**

```python
@dataclass
class UnifiedDecision:
    """Complete decision synthesis"""
    # Core decision
    action: DecisionAction  # EXECUTE, PAUSE, REJECT, ESCALATE, RETRY, ROLLBACK
    confidence: float
    
    # Reasoning trail
    reasoning_chain_ids: List[str]
    primary_reasoning: str
    supporting_evidence: List[str]
    
    # Trust & quality
    trust_score: float
    quality_score: float
    
    # Conflicts & issues
    contradictions: List[Dict[str, Any]]
    warnings: List[str]
    
    # Recommendations
    recommended_next_loops: List[str]
    fallback_actions: List[str]
    
    # Component scores (how much each system contributed)
    governance_weight: float
    avn_weight: float
    mldl_weight: float
    learning_weight: float
    memory_weight: float
```

### Phase 2: Aggregation Logic

The synthesis engine uses **weighted scoring with override rules**:

#### Override Rules (in order of priority):

1. **Governance failures override everything**
   - If governance rejects → `DecisionAction.REJECT`
   - Confidence = 0.0
   - No further processing

2. **AVN high-severity anomalies pause or alter actions**
   - If severity = critical → `DecisionAction.PAUSE`
   - If severity = high + recommended_action = rollback → `DecisionAction.ROLLBACK`
   - Otherwise high severity → `DecisionAction.PAUSE`

3. **MLDL consensus drives which action to take**
   - If no consensus → `DecisionAction.ESCALATE` (human review)
   - If consensus → Use consensus_action

4. **Memory contradictions** generate warnings
5. **Learning insights** provide adjustments

#### Weighted Confidence Calculation:

```python
weights = {
    'governance': 1.0,  # Highest weight - veto power
    'avn': 0.8,          # Health is critical
    'mldl': 0.7,         # Consensus matters
    'learning': 0.5,     # Learning adjusts
    'memory': 0.6        # Context informs
}

confidence = (
    gov_score * 1.0 +
    avn_score * 0.8 +
    mldl_score * 0.7 +
    learning_score * 0.5 +
    memory_score * 0.6
) / sum(weights)
```

### Phase 3: Routing

After synthesis, decisions are routed to:

1. **Trigger Mesh** - Emits `UNIFIED_DECISION_READY` event
2. **Autonomous Loop** - For execution (if action = EXECUTE)
3. **UI** - For transparency
4. **Learning Engine** - For feedback
5. **Immutable Log** - For audit trail

## Usage Examples

### Basic Decision Making

```python
from backend.unified_logic.complete_integration import unified_logic

# Make a decision
decision = await unified_logic.make_decision(
    request={
        'actor': 'user_123',
        'action': 'deploy_model',
        'resource': 'ml_model_v2'
    },
    context={
        'environment': 'production',
        'risk_level': 'high'
    }
)

print(f"Decision: {decision.action}")
print(f"Confidence: {decision.confidence}")
print(f"Reasoning: {decision.primary_reasoning}")
```

### Manual Synthesis

```python
from backend.unified_logic.unified_decision_engine import (
    unified_decision_engine,
    GovernanceInput,
    AVNInput,
    MLDLQuorumInput,
    LearningInput,
    MemoryInput
)

# Prepare inputs
governance = GovernanceInput(
    approved=True,
    reasoning="All policies satisfied",
    trust_score=0.95
)

avn = AVNInput(
    health_state="healthy",
    severity="none",
    confidence=1.0
)

mldl = MLDLQuorumInput(
    consensus_reached=True,
    consensus_action="deploy",
    vote_breakdown={'yes': 4, 'no': 1},
    confidence=0.8
)

learning = LearningInput(
    insights=["Similar deployments succeeded in the past"],
    pattern_confidence=0.75
)

memory = MemoryInput(
    relevant_context=[{'deployment': 'v1', 'outcome': 'success'}],
    contradictions_found=[]
)

# Synthesize decision
decision = await unified_decision_engine.synthesize(
    governance_decision=governance,
    avn_state=avn,
    mldl_consensus=mldl,
    learning_insights=learning,
    memory_context=memory
)

print(f"Action: {decision.action}")  # DecisionAction.EXECUTE
print(f"Confidence: {decision.confidence}")  # ~0.85
print(f"Recommended loops: {decision.recommended_next_loops}")
# ['execution_monitor', 'feedback_collection']
```

### Governance Override Example

```python
# Governance rejects - overrides everything else
governance = GovernanceInput(
    approved=False,
    violated_policies=['security_policy_001'],
    reasoning="Deployment violates security requirements"
)

avn = AVNInput(health_state="healthy", confidence=1.0)
mldl = MLDLQuorumInput(consensus_reached=True, confidence=0.9)
learning = LearningInput()
memory = MemoryInput()

decision = await unified_decision_engine.synthesize(
    governance_decision=governance,
    avn_state=avn,
    mldl_consensus=mldl,
    learning_insights=learning,
    memory_context=memory
)

print(decision.action)  # DecisionAction.REJECT
print(decision.confidence)  # 0.0
print(decision.primary_reasoning)  
# "Governance rejected: Deployment violates security requirements"
```

### AVN Critical Anomaly Example

```python
# AVN detects critical issue - pauses action
governance = GovernanceInput(approved=True)

avn = AVNInput(
    health_state="critical",
    anomalies_detected=[
        {'type': 'memory_leak', 'severity': 'critical'},
        {'type': 'cpu_spike', 'severity': 'high'}
    ],
    severity="critical",
    confidence=0.9
)

mldl = MLDLQuorumInput(consensus_reached=True, confidence=0.8)
learning = LearningInput()
memory = MemoryInput()

decision = await unified_decision_engine.synthesize(
    governance_decision=governance,
    avn_state=avn,
    mldl_consensus=mldl,
    learning_insights=learning,
    memory_context=memory
)

print(decision.action)  # DecisionAction.PAUSE
print(decision.primary_reasoning)  
# "Critical health anomalies detected - pausing for safety"
print(decision.recommended_next_loops)
# ['health_assessment', 'anomaly_investigation', 'health_deep_dive']
```

### No Consensus Example

```python
# MLDL no consensus - escalates to human
governance = GovernanceInput(approved=True)
avn = AVNInput(health_state="healthy")

mldl = MLDLQuorumInput(
    consensus_reached=False,
    vote_breakdown={'yes': 2, 'no': 2, 'abstain': 1},
    confidence=0.4
)

learning = LearningInput()
memory = MemoryInput()

decision = await unified_decision_engine.synthesize(
    governance_decision=governance,
    avn_state=avn,
    mldl_consensus=mldl,
    learning_insights=learning,
    memory_context=memory
)

print(decision.action)  # DecisionAction.ESCALATE
print(decision.primary_reasoning)  
# "No quorum consensus - escalating to human review"
print(decision.recommended_next_loops)
# ['human_review', 'consensus_building']
```

## Decision Routing

### Automatic Routing

Decisions are automatically routed after synthesis:

```python
from backend.unified_logic.decision_router import decision_router

# Decision is routed to all consumers in parallel
await decision_router.route(decision)

# Routes to:
# 1. Trigger mesh (UNIFIED_DECISION_READY event)
# 2. Autonomous loop (if action = EXECUTE)
# 3. UI (decision_update event)
# 4. Learning (feedback event)
# 5. Immutable log (audit entry)
```

### Custom Handlers

Register custom handlers for consumers:

```python
from backend.unified_logic.decision_router import decision_router

# Register autonomous loop handler
async def my_autonomous_handler(decision):
    if decision.action == DecisionAction.EXECUTE:
        # Execute the action
        await execute_action(decision)

decision_router.register_autonomous_handler(my_autonomous_handler)

# Register UI handler
async def my_ui_handler(decision):
    await update_dashboard(decision)

decision_router.register_ui_handler(my_ui_handler)

# Register learning handler
async def my_learning_handler(decision):
    await record_decision_feedback(decision)

decision_router.register_learning_handler(my_learning_handler)
```

## Event Integration

### UNIFIED_DECISION_READY Event

Add to [trigger_mesh.yaml](file:///c:/Users/aaron/grace_2/config/trigger_mesh.yaml):

```yaml
- event_type: unified.decision_ready
  description: Unified decision has been synthesized
  publishers:
    - unified_decision_engine
  subscribers:
    - autonomous_loop
    - ui_dashboard
    - learning_engine
    - metrics_collector
  requires_constitutional_validation: false
  min_trust_score: 0.7

- event_type: autonomous.execute_decision
  description: Execute a unified decision
  publishers:
    - unified_decision_engine
  subscribers:
    - autonomous_executor
    - immutable_log
  requires_constitutional_validation: true
  min_trust_score: 0.8

- event_type: ui.decision_update
  description: Update UI with decision
  publishers:
    - unified_decision_engine
  subscribers:
    - frontend_service
    - notification_service
  requires_constitutional_validation: false
  min_trust_score: 0.5

- event_type: learning.decision_feedback
  description: Decision feedback for learning
  publishers:
    - unified_decision_engine
  subscribers:
    - learning_engine
    - pattern_learner
  requires_constitutional_validation: false
  min_trust_score: 0.6
```

## Decision Actions

### Action Types

```python
class DecisionAction(Enum):
    EXECUTE = "execute"      # Execute the proposed action
    PAUSE = "pause"          # Pause for assessment
    REJECT = "reject"        # Reject the action
    ESCALATE = "escalate"    # Escalate to human review
    RETRY = "retry"          # Retry with new inputs
    ROLLBACK = "rollback"    # Rollback to previous state
```

### Recommended Next Loops

Each action suggests next processing loops:

- **EXECUTE** → `['execution_monitor', 'feedback_collection']`
- **PAUSE** → `['health_assessment', 'anomaly_investigation']`
- **REJECT** → `['governance_review', 'policy_clarification']`
- **ESCALATE** → `['human_review', 'consensus_building']`
- **RETRY** → `['state_refresh', 're-evaluation']`
- **ROLLBACK** → `['rollback_execution', 'state_verification']`

### Fallback Actions

Each action has fallbacks if primary fails:

- **EXECUTE** → `['pause', 'retry', 'rollback']`
- **PAUSE** → `['retry', 'escalate']`
- **REJECT** → `['escalate']`
- **ESCALATE** → `['reject']`
- **RETRY** → `['pause', 'escalate']`
- **ROLLBACK** → `['pause', 'escalate']`

## Statistics & Monitoring

```python
from backend.unified_logic.complete_integration import unified_logic

# Get integration stats
stats = unified_logic.get_stats()

# Example output:
{
    'decisions_processed': 523,
    'engine_stats': {
        'decisions_made': 495,
        'decisions_rejected': 18,
        'decisions_escalated': 10,
        'weights': {
            'governance': 1.0,
            'avn': 0.8,
            'mldl': 0.7,
            'learning': 0.5,
            'memory': 0.6
        }
    },
    'router_stats': {
        'routed_decisions': 523,
        'routing_failures': 2,
        'handlers_registered': {
            'autonomous': True,
            'ui': True,
            'learning': True
        }
    }
}
```

## Audit Trail

All decisions are logged to immutable log:

```python
from backend.logging.immutable_log import immutable_log

# Query unified decisions
entries = await immutable_log.get_entries(
    subsystem="unified_logic",
    limit=100
)

# Filter by action type
execute_decisions = [
    e for e in entries 
    if 'UNIFIED_DECISION:EXECUTE' in e['action']
]

# Filter by rejection
rejected_decisions = [
    e for e in entries 
    if 'UNIFIED_DECISION:REJECT' in e['action']
]
```

## Best Practices

### 1. Always Collect All Inputs

Even if some systems are unavailable, collect fallback inputs:

```python
# Good - provides defaults for unavailable systems
decision = await unified_logic.make_decision(request, context)

# The integration handles unavailable systems gracefully
```

### 2. Trust the Override Rules

The synthesis engine's priority is correct:
1. Governance (absolute authority)
2. AVN (safety critical)
3. MLDL (democratic consensus)
4. Learning/Memory (advisory)

### 3. Monitor Decision Patterns

Track which actions are most common:

```python
stats = unified_logic.get_stats()

# High rejection rate might indicate policy issues
if stats['engine_stats']['decisions_rejected'] > stats['engine_stats']['decisions_made'] * 0.1:
    print("⚠ High rejection rate - review governance policies")

# High escalation rate might indicate unclear situations
if stats['engine_stats']['decisions_escalated'] > stats['engine_stats']['decisions_made'] * 0.05:
    print("⚠ High escalation rate - improve consensus mechanisms")
```

### 4. Use Recommended Loops

Always follow recommended next loops:

```python
decision = await unified_logic.make_decision(request)

for loop in decision.recommended_next_loops:
    if loop == 'execution_monitor':
        asyncio.create_task(monitor_execution(decision))
    elif loop == 'feedback_collection':
        asyncio.create_task(collect_feedback(decision))
    # etc.
```

## Summary

The Unified Logic system provides:

1. **Phase 1: Complete contracts** - Well-defined inputs/outputs for all subsystems
2. **Phase 2: Weighted synthesis** - Smart aggregation with override rules
3. **Phase 3: Multi-target routing** - Automatic distribution to all consumers

All three phases are **fully implemented** with:
- ✅ Real synthesis logic (no placeholders)
- ✅ Governance override rules
- ✅ AVN safety checks
- ✅ MLDL consensus integration
- ✅ Learning and memory integration
- ✅ Event emission via trigger mesh
- ✅ Parallel routing to all targets
- ✅ Complete audit logging
- ✅ Fallback actions and recommended loops
- ✅ Statistics and monitoring

The system acts as Grace's central brain, ensuring all subsystems contribute to coherent, well-reasoned decisions with full transparency and auditability.
