# Multi-Agent Shard System

**Distributed Fleet of Autonomous Sub-Agents**

## Overview

GRACE is now a **multi-agent system** - a fleet of autonomous sub-agents (shards) that:

✅ **Operate independently** within their domain/scope  
✅ **Coordinate peer-to-peer** without central command  
✅ **Share common substrate** (trigger mesh, trust cores, ledger)  
✅ **Self-organize** based on capabilities and workload  
✅ **Scale elastically** under meta loop orchestration  
✅ **Maintain identity** with cryptographic signing  

This enables **horizontal scaling**, **fault tolerance**, and **specialized expertise**.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│         SHARED SPINE (Common Substrate)                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Trigger Mesh • Trust Cores • Immutable Ledger       │ │
│  │ Meta Loop • Global Policies • Strategic Goals       │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ Shard A        │  │ Shard B     │  │ Shard C         │
│ (Infra Domain) │  │ (App Domain)│  │ (Preventive)    │
│                │◀─┼─────────────┼─▶│                 │
│ • Sensors      │  │ • Sensors   │  │ • Sensors       │
│ • Health Graph │  │ • Health    │  │ • Forecasting   │
│ • Playbooks    │  │   Graph     │  │ • Capacity      │
│ • Trust        │  │ • Playbooks │  │ • Planning      │
│   Contract     │  │ • Trust     │  │ • Trust         │
└────────────────┘  │   Contract  │  │   Contract      │
                    └─────────────┘  └─────────────────┘
                    
        P2P Mesh: Signed Messages, State Deltas
        Roles: Memory Steward, Ingestion Lead, etc.
        Coordination: Offer/Need/Request/Handoff
```

---

## Shard Types

### 1. Domain Shards
**Purpose:** Own specific domain responsibilities

Examples:
- **Infrastructure Shard** - Manages servers, networks, storage
- **Application Shard** - Manages application services
- **Data Shard** - Manages databases, data pipelines
- **Security Shard** - Manages security monitoring, incident response

### 2. Geographic Shards
**Purpose:** Own specific regions/zones

Examples:
- **US-East Shard** - Manages resources in us-east region
- **EU-West Shard** - Manages resources in eu-west region
- **Multi-region Shard** - Coordinates across regions

### 3. Workload Shards
**Purpose:** Specialized for workload type

Examples:
- **Incident Response Shard** - Reacts to active incidents
- **Preventive Shard** - Proactive forecasting & prevention
- **Capacity Planning Shard** - Long-term capacity optimization
- **Cost Optimization Shard** - Cost reduction strategies

### 4. SWAT Shards
**Purpose:** Temporary specialist teams

Examples:
- **Major Incident SWAT** - Spawned for P0 incidents
- **Chaos Engineering SWAT** - Runs controlled experiments
- **Migration SWAT** - Handles data/service migrations

### 5. Replica Shards
**Purpose:** Fault tolerance and load distribution

Examples:
- **Hot Standby** - Ready to take over immediately
- **Load Balancer** - Distributes work across replicas
- **Geographic Replica** - Region-local processing

---

## Capabilities (Roles)

Shards declare capabilities they can provide:

| Capability | Description |
|------------|-------------|
| `MEMORY_STEWARD` | Manages knowledge graph, memory consolidation |
| `INGESTION_LEAD` | Coordinates data ingestion pipelines |
| `SELF_HEALING` | Autonomous incident resolution |
| `SECURITY_SENTINEL` | Security monitoring & threat response |
| `CAPACITY_PLANNER` | Forecasts and provisions capacity |
| `COST_OPTIMIZER` | Identifies cost savings |
| `COMPLIANCE_AUDITOR` | Monitors policy compliance |

**Roles are not hierarchical** - shards collaborate peer-to-peer based on capabilities.

---

## P2P Communication

### Message Types

**OFFER** - "I can help with X"
```json
{
  "type": "offer",
  "sender": "shard_abc123",
  "capability": "self_healing",
  "load_factor": 0.3
}
```

**NEED** - "I need help with Y"
```json
{
  "type": "need",
  "sender": "shard_def456",
  "need_type": "capacity_planning",
  "urgency": "high"
}
```

**REQUEST** - "Please do X"
```json
{
  "type": "request",
  "sender": "shard_abc123",
  "recipient": "shard_def456",
  "work": {...}
}
```

**STATE_DELTA** - "My state changed"
```json
{
  "type": "state_delta",
  "sender": "shard_abc123",
  "entity_type": "health_node",
  "entity_id": "api-service",
  "operation": "update",
  "changes": {"status": "degraded"}
}
```

**HANDOFF** - "Taking over responsibility"
```json
{
  "type": "handoff",
  "sender": "shard_abc123",
  "task_id": "task_789",
  "task": {...}
}
```

### Signed Messages

All P2P messages are cryptographically signed:

```python
message = P2PMessage(
    message_id="msg_xyz",
    message_type=MessageType.OFFER,
    sender_id="shard_abc123",
    payload={...},
    signature=shard.identity.sign_message(payload)
)
```

Recipients verify signatures before processing.

---

## State Sharing

### Global State (Shared Across All Shards)

- **Policies** - Trust rules, governance policies
- **Strategic Goals** - System-wide objectives
- **Identity Registry** - Shard identities & capabilities
- **Critical Ledgers** - Audit trail, compliance records

### Local State (Shard-Private)

- **Domain Observations** - Metrics, events specific to shard's scope
- **Workload Queue** - Pending tasks
- **Active Tasks** - Currently executing work
- **Peer Cache** - Known peer shards

### State Deltas (Selectively Shared)

When local state changes that others need to know:

```python
delta = StateDelta(
    entity_type="health_node",
    entity_id="api-service",
    operation="update",
    changes={"status": "degraded", "latency_p95": 850},
    version=42
)

await shard.publish_state_delta(delta)
```

### CRDT-Like Reconciliation

State deltas merge using last-write-wins with timestamps:

```python
def merge(self, other: StateDelta) -> StateDelta:
    if self.timestamp > other.timestamp:
        return self  # Keep newer
    else:
        return other
```

---

## Shard Lifecycle

### 1. Spawning

```python
from backend.multi_agent_shards import shard_coordinator, ShardType, ShardScope, CapabilityType

# Spawn infrastructure shard
shard = await shard_coordinator.spawn_shard(
    shard_type=ShardType.DOMAIN,
    scope=ShardScope(domain="infrastructure"),
    capabilities=[
        CapabilityType.SELF_HEALING,
        CapabilityType.CAPACITY_PLANNER
    ]
)
```

### 2. Initialization

1. Generate cryptographic identity (public/private keys)
2. Subscribe to relevant events from trigger mesh
3. Register with peer shards
4. Start processing loops (workload, messages, heartbeat)
5. Publish readiness to shard registry

### 3. Operation

**Workload Processing:**
- Receives events from trigger mesh
- Checks if event is in scope
- Adds to workload queue
- Executes work or offloads to peer

**P2P Coordination:**
- Processes peer messages
- Responds to offers/needs
- Shares state deltas
- Negotiates task handoffs

**Health Monitoring:**
- Sends heartbeat every 30s
- Reports metrics (load, latency, tasks)
- Updates status (active/idle/overloaded)

### 4. Retiring

1. Mark status as RETIRING
2. Hand off active tasks to peers
3. Publish final state deltas
4. Unsubscribe from event streams
5. Mark status as TERMINATED

---

## Meta Loop as Conductor

The meta loop orchestrates the shard fleet:

### Load Balancing

When shard becomes overloaded:
```python
if shard.status == ShardStatus.OVERLOADED:
    # Spawn replica to help
    await coordinator.spawn_shard(
        shard_type=ShardType.REPLICA,
        scope=shard.scope,
        capabilities=shard.identity.capabilities
    )
```

### Elastic Scaling

**Scale Up:**
- Traffic spike detected → Spawn additional shards
- New domain added → Spawn domain shard
- Major incident → Spawn SWAT shard

**Scale Down:**
- Load drops → Retire idle replicas
- Incident resolved → Retire SWAT shard
- Domain removed → Retire domain shard

### Conflict Resolution

When two shards race on same issue:
```python
# Shard A and Shard B both try to scale api-service
# Meta loop detects conflict, designates winner
winner = meta_loop.resolve_conflict([shard_a, shard_b])
# Loser backs off, winner continues
```

### Role Rebalancing

Meta loop can reassign capabilities:
```python
# Infrastructure shard overloaded with capacity planning
# Meta loop spawns dedicated capacity planner shard
await meta_loop.rebalance_roles(
    from_shard="shard_infra",
    capability=CapabilityType.CAPACITY_PLANNER,
    to_shard="shard_new_capacity"
)
```

---

## Security & Identity

### Per-Shard Identity

Each shard has cryptographic identity:

```python
class ShardIdentity:
    shard_id: str           # Unique identifier
    public_key: str         # For verification
    private_key: str        # For signing
    capabilities: List      # What it can do
    trust_level: int        # 1-10 trust rating
```

### Message Signing

All P2P messages signed:
```python
signature = shard.identity.sign_message(json.dumps(payload))
```

### Verification

Recipients verify before processing:
```python
if not shard.identity.verify_signature(message, signature, sender_key):
    # Reject invalid message
    return
```

### Trust Boundaries

Cross-shard actions require mutual verification:
```python
# Shard A requests Shard B to delete data
# Shard B verifies Shard A has authority
if not await trust_core.verify_authority(shard_a, "data_deletion"):
    # Reject request
    return
```

---

## Example: Multi-Shard Incident Response

### Scenario: API Latency Spike

```
1. DETECTION (Infrastructure Shard)
   ├─ Monitors infrastructure metrics
   ├─ Detects API latency degraded
   └─ Publishes STATE_DELTA to peers

2. COORDINATION (App Shard receives delta)
   ├─ App shard owns API service
   ├─ Sends NEED: "capacity_planning"
   └─ Broadcasts to peer shards

3. OFFER (Preventive Shard responds)
   ├─ Preventive shard has CAPACITY_PLANNER capability
   ├─ Low load factor (0.3)
   └─ Sends OFFER: "I can help"

4. DELEGATION (App Shard → Preventive Shard)
   ├─ App shard sends REQUEST with work
   └─ Preventive shard adds to workload

5. EXECUTION (Preventive Shard)
   ├─ Analyzes capacity needs
   ├─ Plans scaling directive
   ├─ Executes via autonomous planner
   └─ Publishes STATE_DELTA: "scaled to 15 instances"

6. VERIFICATION (Infrastructure Shard)
   ├─ Sees STATE_DELTA
   ├─ Confirms latency normalized
   └─ Marks incident resolved

7. LEARNING (All Shards)
   └─ Record outcome to shared learning system
```

**Result:** Multi-shard collaboration resolved incident faster than single agent could.

---

## Fleet Status API

### Get Fleet Overview

```python
status = await shard_coordinator.get_fleet_status()
```

**Response:**
```json
{
  "total_shards": 5,
  "shards": [
    {
      "shard_id": "shard_abc123",
      "type": "domain",
      "status": "active",
      "metrics": {
        "tasks_completed": 142,
        "load_factor": 0.45,
        "avg_latency_seconds": 2.3
      },
      "active_tasks": 3
    }
  ]
}
```

---

## Benefits

### Horizontal Scalability
- Add shards to handle more load
- No single bottleneck
- Linear scaling characteristics

### Fault Tolerance
- Shard failure doesn't bring down system
- Peers take over responsibilities
- Replica shards provide redundancy

### Specialized Expertise
- Shards can specialize deeply
- Domain experts handle domain issues
- Better decisions through specialization

### Geographic Distribution
- Shards colocated with resources
- Lower latency for local decisions
- Regulatory compliance (data residency)

### Elastic Resource Usage
- Spawn shards when needed
- Retire when idle
- Pay only for active shards

---

## Configuration

### Default Fleet

By default, spawns:
- **Infrastructure Domain Shard** (self-healing, capacity planning)
- **Application Domain Shard** (self-healing, ingestion)
- **Preventive Workload Shard** (capacity planning)

### Custom Shard

```python
await shard_coordinator.spawn_shard(
    shard_type=ShardType.WORKLOAD,
    scope=ShardScope(
        workload_type="cost_optimization",
        policy_constraints={"max_cost_per_action": 100}
    ),
    capabilities=[CapabilityType.COST_OPTIMIZER]
)
```

---

## Monitoring

### Per-Shard Metrics
- Tasks completed/failed
- Average latency
- Load factor (0.0-1.0)
- Uptime

### Fleet Metrics
- Total shards active
- Overall throughput
- P2P message volume
- State delta propagation latency

### Health Checks
Each shard sends heartbeat every 30s with status and metrics.

---

## Files

- `backend/multi_agent_shards.py` - Shard system implementation
- `backend/grace_spine_integration.py` - Integration with spine
- `docs/MULTI_AGENT_SHARDS.md` - This documentation

---

## Summary

The Multi-Agent Shard System transforms GRACE into a **distributed fleet**:

✅ **Multiple autonomous sub-agents** operating in parallel  
✅ **Peer-to-peer coordination** without hierarchy  
✅ **Shared spine** (trigger mesh, trust, ledger) as substrate  
✅ **Role-based capabilities** for specialized expertise  
✅ **State reconciliation** via CRDTs  
✅ **Meta loop orchestration** for elastic scaling  
✅ **Cryptographic identity** for secure P2P  
✅ **Fault tolerance** through redundancy  

**GRACE is now a multi-agent swarm, not a single agent.**
