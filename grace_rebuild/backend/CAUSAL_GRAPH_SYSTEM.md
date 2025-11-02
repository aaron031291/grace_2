# Causal Graph System

Complete implementation of causal graph construction and reasoning for Grace.

## Overview

The causal graph system builds directed graphs from event logs to understand cause-effect relationships across the system. It enables:
- **Root cause analysis** - trace errors/failures to originating events
- **Impact prediction** - identify which events have the most influence
- **Pattern detection** - find recurring causal sequences
- **Feedback loop detection** - identify reinforcing/balancing cycles
- **Optimization recommendations** - suggest improvements based on causal evidence

## Architecture

### Components

1. **causal_graph.py** - Core graph construction and analysis
   - `CausalNode` - represents events (messages, tasks, executions, alerts)
   - `CausalEdge` - represents causal relationships with strength (0.0-1.0)
   - `CausalGraph` - builds and analyzes the graph

2. **causal_analyzer.py** - High-level analysis
   - Task completion analysis
   - Error chain tracing
   - Optimization path finding
   - Feedback loop analysis

3. **causal_graph_api.py** - REST API endpoints
   - Graph construction
   - Causal queries (causes/effects/paths)
   - Influence scoring
   - Visualization export

4. **Integrations**
   - `reflection.py` - uses causal insights in reflections
   - `meta_loop.py` - optimizes based on causal analysis
   - `hunter.py` - traces security events to root cause

## Causal Inference Methods

### 1. Temporal Ordering
Events occurring in sequence within a time window are considered potentially causal.
```
A happens at 10:00
B happens at 10:02
→ A might cause B (with decay based on time gap)
```

### 2. Correlation Strength
If A→B happens X% of the time when A occurs, assign confidence based on frequency.
```
message_user → task_created occurs 80% of time
→ Strong causal link (0.8 confidence)
```

### 3. Pattern Recognition
Detect recurring sequences across users and time.
```
question → helpful_response → task_created
Appears 10 times → Reinforces causal links
```

### 4. Domain Knowledge
Explicit relationships from system design.
```
task_created → task_completed (task lifecycle)
user_message → grace_response (conversation flow)
```

### Confidence Scoring
- **1.0** - Certain (explicit relationships, e.g., task lifecycle)
- **0.7-0.9** - High confidence (strong temporal/pattern evidence)
- **0.4-0.6** - Medium confidence (correlation, weak pattern)
- **0.1-0.3** - Low confidence (temporal only, weak correlation)
- **0.0** - No relationship

## API Endpoints

### Build Graph
```http
POST /api/causal/build-graph
{
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-02T00:00:00",
  "user": "optional_user_filter",
  "days_back": 7
}
```

### Find Causes
```http
GET /api/causal/causes/123?event_type=task_created&max_depth=3&days_back=7
```
Returns all events that led to this one (backward search).

### Find Effects
```http
GET /api/causal/effects/123?event_type=message_user&max_depth=3
```
Returns all events caused by this one (forward search).

### Find Path
```http
POST /api/causal/path
{
  "event_a_id": 10,
  "event_a_type": "message_user",
  "event_b_id": 25,
  "event_b_type": "task_created"
}
```
Finds causal chain between two events.

### Get Influential Events
```http
GET /api/causal/influence?limit=10&days_back=7
```
Returns events with highest influence scores.

### Detect Cycles
```http
GET /api/causal/cycles?days_back=7&user=alice
```
Finds feedback loops in the system.

### Visualization Data
```http
GET /api/causal/visualize?days_back=7&prune_threshold=0.3
```
Exports graph in D3.js/Cytoscape format.

### Analysis Endpoints

#### Task Completion Analysis
```http
GET /api/causal/analyze/task-completion?user=alice&days=7
```
Returns patterns in task completion vs failure.

#### Error Chain Analysis
```http
GET /api/causal/analyze/error-chains?days=7
```
Traces errors to root causes.

#### Optimization Analysis
```http
GET /api/causal/analyze/optimization?metric=task_completion&days=7
```
Finds best ways to improve a metric.

#### Feedback Loop Analysis
```http
GET /api/causal/analyze/feedback-loops?days=7
```
Detects and analyzes reinforcing/balancing loops.

## Integration Examples

### Reflection System
```python
# In reflection.py
from .causal_graph import CausalGraph

graph = CausalGraph()
await graph.build_from_events(start, end)
influential = graph.get_most_influential_events(limit=3)
# Include in reflection insight
```

### Meta-Loop
```python
# In meta_loop.py
from .causal_analyzer import causal_analyzer

analysis = await causal_analyzer.analyze_task_completion(days=1)
# Use recommendations to adjust thresholds
```

### Hunter (Security)
```python
# In hunter.py
from .causal_graph import CausalGraph

causes = graph.find_causes(security_event_id, "security_event")
# Trace security alert to originating event
```

## Usage Examples

### Example 1: Trace Task to User Question
```python
from causal_graph import CausalGraph

graph = CausalGraph()
await graph.build_from_events(start_date, end_date, user="alice")

# Find what caused task creation
causes = graph.find_causes(task_id=42, event_type="task_created", max_depth=3)
# Returns: message_user → message_assistant → task_created
```

### Example 2: Find Most Influential Events
```python
influential = graph.get_most_influential_events(limit=10)
# Returns events ranked by:
# - Number of direct effects
# - Total causal strength
# - Number of indirect effects
```

### Example 3: Detect Feedback Loops
```python
cycles = graph.detect_cycles()
# Identifies loops like:
# task_created → reflection → learning → task_created
```

### Example 4: Optimize Task Completion
```python
from causal_analyzer import causal_analyzer

analysis = await causal_analyzer.analyze_task_completion(user="alice", days=7)
# Returns:
# - Completion patterns (what leads to completion)
# - Failure patterns (what leads to abandonment)
# - Actionable recommendations
```

### Example 5: Root Cause Analysis
```python
error_analysis = await causal_analyzer.analyze_error_chains(days=7)
# Traces errors through multiple causal layers to root cause
# Common root causes ranked by frequency
```

## Graph Visualization

Export graph for visualization libraries:

```python
viz_data = graph.export_for_visualization()
```

Returns JSON:
```json
{
  "nodes": [
    {
      "id": "message_user_123",
      "event_id": 123,
      "event_type": "message_user",
      "timestamp": "2024-01-15T10:30:00",
      "user": "alice",
      "influence": 4.5,
      "metadata": {"content": "How do I..."}
    }
  ],
  "edges": [
    {
      "source": "message_user_123",
      "target": "message_assistant_124",
      "strength": 0.95,
      "relationship_type": "triggers",
      "evidence": ["event_type: question"]
    }
  ],
  "stats": {
    "total_nodes": 150,
    "total_edges": 230,
    "avg_edge_strength": 0.67
  }
}
```

Use with D3.js:
```javascript
d3.json('/api/causal/visualize?days_back=7').then(data => {
  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.edges).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-100))
    .force("center", d3.forceCenter(width/2, height/2));
});
```

## Performance Considerations

### Graph Pruning
Remove weak edges to focus on strong causal relationships:
```python
graph.prune_weak_edges(threshold=0.3)
# Removes edges with strength < 0.3
```

### Time Window
Limit analysis to recent events:
```python
# Last 7 days (default)
await graph.build_from_events(start, end, days_back=7)

# Last 24 hours (faster)
await graph.build_from_events(start, end, days_back=1)
```

### User Filtering
Analyze per-user to reduce graph size:
```python
await graph.build_from_events(start, end, user="alice")
```

## Test Coverage

Run comprehensive tests:
```bash
cd grace_rebuild/backend
python test_causal_system.py
```

Tests verify:
- ✓ Graph construction from events
- ✓ Causal inference (causes & effects)
- ✓ Influence calculation
- ✓ Feedback loop detection
- ✓ Path finding between events
- ✓ Task completion analysis
- ✓ Optimization recommendations
- ✓ Visualization data export
- ✓ Meta-loop integration

## Test Scenario

The test creates:
1. User asks: "How do I improve code quality?"
2. Grace responds with suggestions
3. User creates task: "Add unit tests to project"
4. User completes task
5. System auto-generates related task

Then verifies:
- Causal graph correctly links user question → response → task creation
- Influence scores identify key events
- Task completion analysis finds patterns
- Optimization provides recommendations
- Meta-loop uses insights to improve system

## Future Enhancements

1. **Machine Learning Integration**
   - Train models to predict causal strength
   - Anomaly detection in causal patterns
   - Automated threshold tuning

2. **Real-time Graph Updates**
   - Incremental graph construction
   - Stream processing for live events
   - WebSocket updates to frontend

3. **Advanced Analysis**
   - Counterfactual reasoning ("what if" scenarios)
   - Intervention analysis (A/B test insights)
   - Long-term trend prediction

4. **Visualization Improvements**
   - Interactive graph explorer
   - Time-series animation
   - Cluster detection (event groups)

## Related Files

- `causal.py` - Original event logging (extends this)
- `reflection.py` - Uses causal insights
- `meta_loop.py` - Optimizes with causal analysis
- `hunter.py` - Security event tracing
- `models.py` - CausalEvent database model

## Summary

The causal graph system provides Grace with the ability to understand cause-effect relationships across all events. This enables:
- **Better insights** through root cause analysis
- **Smarter optimization** via evidence-based recommendations
- **Proactive improvement** by identifying high-impact events
- **System stability** through feedback loop detection

All analysis is accessible via REST API and integrated into reflection, meta-loop, and security systems.
