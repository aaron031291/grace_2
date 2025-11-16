# Domain-Grouped Port Architecture - RECOMMENDED

## Concept

**Group APIs by domain, each domain gets one port**

Benefits:
- ✅ Fixed positions (easy debugging)
- ✅ Domain isolation (crash doesn't affect others)
- ✅ Cryptographic tracking (provable request paths)
- ✅ Manageable (10 domain ports vs 100 API ports)
- ✅ Clear organization (know where everything is)

## Port Allocation

```
Main API:     8000  (Gateway/Router)
Kernels:      8100-8149  (Individual isolation)
Domains:      8200-8209  (Grouped APIs)
```

## Domain Definitions

### Port 8200: Core Domain
**Purpose:** Authentication, health, system basics

**APIs:**
1. /auth - Authentication & authorization
2. /health - System health checks
3. /operator-dashboard - Operator interface
4. /control-api - System control
5. /startup-dashboard - Startup monitoring
6. /presence-api - System presence
7. /system-dashboard - System overview
8. /meta-focus - Meta-level operations
9. /secrets-api - Secrets management
10. /secrets-consent-api - Consent for secrets

**Kernel Dependencies:**
- Governance Kernel (8110)
- Crypto Kernel (8111)

**Cryptographic Key:** `core_domain_key`

---

### Port 8201: Memory & Knowledge Domain
**Purpose:** All memory, knowledge, and data storage

**APIs:**
1. /memory-api - Memory operations
2. /memory-tables-api - Memory table management
3. /memory-workspace-api - Workspace management
4. /memory-files-api - File memory
5. /memory-events-api - Event memory
6. /knowledge - Knowledge base
7. /librarian-api - Librarian services
8. /book-dashboard - Book management
9. /vector-api - Vector storage
10. /memory-fusion-api - Memory fusion

**Kernel Dependencies:**
- Librarian Kernel (8130)
- Message Bus (8100)
- Immutable Log (8101)

**Cryptographic Key:** `memory_domain_key`

---

### Port 8202: AI & Intelligence Domain
**Purpose:** All AI/ML services and agents

**APIs:**
1. /chat - Chat interface
2. /autonomous-agent-api - Autonomous agents
3. /ml-dashboard-api - ML monitoring
4. /ml-systems-api - ML systems
5. /agentic-api - Agentic capabilities
6. /coding-agent-api - Coding assistance
7. /multimodal-api - Multimodal processing
8. /speech-api - Speech processing
9. /voice-notes-api - Voice notes
10. /copilot-api - Copilot features

**Kernel Dependencies:**
- Coding Agent Kernel (8132)
- Learning Kernel (8133)
- Research Kernel (8134)

**Cryptographic Key:** `ai_domain_key`

---

### Port 8203: Governance & Security Domain
**Purpose:** Governance, trust, security, compliance

**APIs:**
1. /governance - Governance operations
2. /trust-framework-api - Trust framework
3. /guardian-api - Guardian services
4. /immutable-api - Immutable logging
5. /trust-api - Trust operations
6. /verification-api - Verification
7. /constitutional-api - Constitutional rules
8. /policy-engine - Policy management
9. /compliance-monitor - Compliance tracking
10. /audit-trail - Audit logging

**Kernel Dependencies:**
- Governance Kernel (8110)
- Crypto Kernel (8111)
- Trust Framework Kernel (8112)
- Policy Engine (8113)
- Compliance Monitor (8114)
- Audit Trail (8115)

**Cryptographic Key:** `governance_domain_key`

---

### Port 8204: Execution & Control Domain
**Purpose:** Task execution, workflows, scheduling

**APIs:**
1. /execution-api - Task execution
2. /mission-control-api - Mission control
3. /kernels-api - Kernel management
4. /kernel-ports - Port management
5. /executor - Execution engine
6. /tasks - Task management
7. /scheduler-observability - Scheduler monitoring
8. /workflow-engine - Workflow management
9. /concurrent-api - Concurrent operations
10. /subagent-bridge - Subagent coordination

**Kernel Dependencies:**
- Scheduler Kernel (8120)
- Task Executor (8121)
- Workflow Engine (8122)
- State Machine (8123)

**Cryptographic Key:** `execution_domain_key`

---

### Port 8205: Monitoring & Telemetry Domain
**Purpose:** Observability, metrics, telemetry

**APIs:**
1. /telemetry-api - Telemetry collection
2. /metrics - Metrics endpoints
3. /observability-api - Observability
4. /learning-visibility-api - Learning visibility
5. /alerts-api - Alert management
6. /telemetry-ws - Telemetry WebSocket
7. /activity-stream - Activity tracking
8. /agent-timeline - Agent timeline
9. /history - Historical data
10. /metrics-aggregator - Metric aggregation

**Kernel Dependencies:**
- Telemetry Service (8140)
- Metrics Aggregator (8141)
- Alert Service (8142)

**Cryptographic Key:** `monitoring_domain_key`

---

### Port 8206: Integration & External Domain
**Purpose:** External integrations, remote access

**APIs:**
1. /remote-access-api - Remote access
2. /integration-api - Integration services
3. /external-api-routes - External APIs
4. /remote-session-api - Remote sessions
5. /remote-ingestion-api - Remote ingestion
6. /pc-access-api - PC access
7. /integrations-api - Integration management
8. /plugin-routes - Plugin system
9. /websocket-routes - WebSocket endpoints
10. /terminal-ws - Terminal WebSocket

**Kernel Dependencies:**
- Integration services

**Cryptographic Key:** `integration_domain_key`

---

### Port 8207: Data & Processing Domain
**Purpose:** Data ingestion, processing, transformation

**APIs:**
1. /ingestion-api - Data ingestion
2. /ingestion-bridge-api - Ingestion bridge
3. /auto-ingestion-api - Auto ingestion
4. /ingest - Ingest operations
5. /ingest-fast - Fast ingest
6. /ingest-minimal - Minimal ingest
7. /temporal-api - Temporal data
8. /causal-api - Causal analysis
9. /chunked-upload-api - Chunked uploads
10. /file-organizer-api - File organization

**Kernel Dependencies:**
- Data processing kernels

**Cryptographic Key:** `data_domain_key`

---

### Port 8208: Self-Healing & Diagnostics Domain
**Purpose:** Self-healing, diagnostics, health

**APIs:**
1. /self-healing-api - Self-healing
2. /network-healer - Network healing
3. /healing-dashboard - Healing dashboard
4. /self-heal-debug - Healing debug
5. /health-unified - Unified health
6. /health-routes - Health routes
7. /code-healing-api - Code healing
8. /playbooks - Playbook management
9. /incidents - Incident tracking
10. /issues - Issue management

**Kernel Dependencies:**
- Self-Healing Kernel (8131)

**Cryptographic Key:** `healing_domain_key`

---

### Port 8209: Development & Debug Domain
**Purpose:** Development tools, testing, debugging

**APIs:**
1. /sandbox - Sandbox environment
2. /test-endpoint - Testing
3. /meta-api - Meta operations
4. /evaluation - Evaluation tools
5. /reflections - Reflection APIs
6. /summaries - Summary generation
7. /goals - Goal tracking
8. /causal-graph-api - Causal graphs
9. /htm-management - HTM management
10. /schema-proposals-api - Schema proposals

**Kernel Dependencies:**
- Development tools

**Cryptographic Key:** `dev_domain_key`

---

## Request Flow with Cryptographic Tracking

### Example: User Authentication

```
1. User → Main API (8000)
   Request: POST /auth/login
   Signature: sign(request, main_api_key)
   
2. Main API → Core Domain (8200)
   Routes to: http://localhost:8200/auth/login
   Signature: sign(request, core_domain_key)
   
3. Core Domain → Governance Kernel (8110)
   Verifies with: http://localhost:8110/verify
   Signature: sign(verification, governance_key)
   
4. Response Path (with signatures)
   Governance → Core Domain → Main API → User
   
5. Cryptographic Proof
   Complete audit trail with verifiable signatures
   Can prove EXACTLY what happened, when, where
```

### Tracking Chain
```json
{
  "request_id": "req_12345",
  "cryptographic_chain": [
    {
      "hop": 1,
      "port": 8000,
      "component": "main_api",
      "timestamp": "2025-01-16T10:30:00Z",
      "signature": "abc123...",
      "verified": true
    },
    {
      "hop": 2,
      "port": 8200,
      "component": "core_domain",
      "timestamp": "2025-01-16T10:30:00.050Z",
      "signature": "def456...",
      "verified": true
    },
    {
      "hop": 3,
      "port": 8110,
      "component": "governance_kernel",
      "timestamp": "2025-01-16T10:30:00.100Z",
      "signature": "ghi789...",
      "verified": true
    }
  ],
  "tamper_proof": true,
  "full_audit_trail": true
}
```

## Debugging Benefits

### Scenario: Chat feature broken

**Before (all on 8000):**
```bash
# Where's the issue?
# Could be anywhere in 100+ routes
# Have to search logs
# Hard to isolate
```

**After (domain-grouped):**
```bash
# Chat is in AI Domain (8202)
curl http://localhost:8202/health
# → Shows AI domain is down

# Check AI domain logs specifically
tail -f logs/domain_8202_ai.log

# Restart just AI domain
curl -X POST http://localhost:8000/network-healer/heal \
  -d '{"component_name": "ai_domain", "port": 8202}'

# FIXED! Other domains never affected.
```

## Network Healing for Domains

```python
# Network healing works at domain level
issue = NetworkIssue(
    component_name="ai_domain",
    port=8202,
    issue_type="domain_unresponsive",
    severity="high"
)

# Healing playbooks:
# 1. Diagnose which APIs in domain are failing
# 2. Restart entire domain
# 3. Or restart individual APIs within domain
# 4. Verify domain health
```

## Deployment

### Development
```bash
# Start main API (gateway)
python serve.py  # Port 8000

# Start domain servers
python start_domain.py core 8200
python start_domain.py memory 8201
python start_domain.py ai 8202
# etc.

# Start kernel servers
# (each on dedicated port)
```

### Production
```bash
# Load balancer → Main API
nginx → localhost:8000

# Internal domain network
localhost:8200-8209  # Not exposed

# Internal kernel network  
localhost:8100-8149  # Not exposed
```

## Complexity Comparison

| Architecture | Ports | Debug Time | Crypto Tracking | Complexity |
|--------------|-------|-----------|-----------------|------------|
| All-in-One | 1 | Hours | Hard | Low |
| Every API | 100+ | Minutes | Perfect | Very High |
| **Domain-Grouped** | **10** | **Minutes** | **Perfect** | **Medium** |
| Kernels Only | 20 | Medium | Medium | Medium |

## Recommendation

**This is the SWEET SPOT:**

✅ **Fixed positions** - Know where everything is  
✅ **Quick debugging** - Port tells you the domain  
✅ **Cryptographic tracking** - Full audit trail  
✅ **Domain isolation** - One domain crash ≠ all down  
✅ **Manageable** - 10 domains vs 100 APIs  
✅ **Scalable** - Can scale domains independently  

**Start with this architecture!**
