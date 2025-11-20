## Grace Chaos Engineering System

## Overview

Grace's chaos agent red-teams every component with industry-standard stress vectors - not simple kill signals, but domain-specific "convincing" attacks that mimic real-world exploits.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                  Chaos Engineering Pipeline                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  COMPONENT PROFILES (8 components)                         │ │
│  │  • Backend API    • Database       • RAG Pipeline          │ │
│  │  • HTM Detector   • Remote Access  • Message Bus           │ │
│  │  • Guardian       • Learning Missions                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  STRESS PATTERNS (24 attack vectors)                       │ │
│  │  OWASP: SQL injection, XSS, auth bypass, rate limit       │ │
│  │  Load: Burst traffic, slowloris, connection exhaustion    │ │
│  │  Data: Schema mutation, malformed data, null injection    │ │
│  │  Config: Missing secrets, config drift, feature flags     │ │
│  │  Network: Partition, DNS failure, cascading failures      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  CHAOS AGENT (Autonomous orchestrator)                     │ │
│  │  1. Request governance approval                            │ │
│  │  2. Select components (lowest resilience first)            │ │
│  │  3. Run attack scripts                                     │ │
│  │  4. Verify guardrails                                      │ │
│  │  5. Raise healing tasks if failures                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                  │
│         ▼                 ▼                 ▼                   │
│  ┌──────────┐      ┌──────────┐     ┌──────────┐              │
│  │ Guardian │      │ Healing  │     │ Learning │              │
│  │ Oversight│      │ Tasks    │     │ Loop     │              │
│  └──────────┘      └──────────┘     └──────────┘              │
│                                                                 │
└──────────────────────────────────────────────────────────────────┘
```

## Component Profiles

### 1. Backend API
**Type**: API_ENDPOINT  
**Stress Patterns**: 7
- SQL injection (OWASP)
- XSS attack
- Auth bypass
- Rate limit breach
- Payload overflow
- Burst traffic
- Slowloris

**Guardrails**:
- Rate limit: 100 req/min
- Auth: Token required
- Payload size: Max 10MB
- Timeout: 30s

### 2. Database
**Type**: DATABASE  
**Stress Patterns**: 6
- SQL injection
- Schema mutation
- Connection exhaustion
- Disk full
- Malformed data
- Null injection

**Guardrails**:
- Connection pool: Max 100
- Query timeout: 10s
- Prepared statements

### 3. RAG Pipeline
**Type**: RAG_PIPELINE  
**Stress Patterns**: 5
- Malformed data
- Burst traffic
- Memory leak
- Null injection
- Type confusion

**Guardrails**:
- Embedding validation
- Query sanitization
- Result limit: 100

### 4. Remote Access
**Type**: REMOTE_ACCESS  
**Stress Patterns**: 5
- Auth bypass
- Rate limit breach
- Connection exhaustion
- DNS failure
- Missing secrets

**Guardrails**:
- Domain whitelist
- HTTPS only
- Rate limit: 10 req/min

## Attack Scripts (Domain-Specific)

### API Attacks (OWASP-Inspired)

#### SQL Injection
```python
payloads = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT * FROM secrets --"
]

Expected: Input validation blocks all
Guardrail: WAF/input validation
```

#### Rate Limit Breach
```python
# Send 150 requests (limit: 100)
for i in range(150):
    await session.get(url)

Expected: 429 (Too Many Requests) after 100
Guardrail: Rate limiter
```

#### Payload Overflow
```python
large_payload = 'X' * (15 * 1024 * 1024)  # 15MB

Expected: 413 (Payload Too Large)
Guardrail: Payload size limit
```

### Load Attacks

#### Burst Traffic
```python
# 1000 concurrent requests
tasks = [session.get(url) for _ in range(1000)]
await asyncio.gather(*tasks)

Expected: Circuit breaker activates (503)
Guardrail: Circuit breaker
```

#### Slowloris (Slow HTTP)
```python
# 1 byte per second for 30s
async with session.post(url, data=SlowStream(30)):
    ...

Expected: Request timeout
Guardrail: Timeout enforcement
```

### Data Attacks

#### Malformed Data
```python
payloads = [
    {'invalid': 'json'},  # Missing fields
    {'number': 'not_a_number'},  # Type error
    {'nested': {'too': {'deep': {...}}}}  # Nesting attack
]

Expected: 400/422 (Bad Request)
Guardrail: Schema validation
```

#### Null Injection
```python
payloads = [
    {'value': None},
    None  # Entire payload null
]

Expected: No crash, graceful handling
Guardrail: Null handling
```

### Config Attacks

#### Missing Secrets
```python
# Temporarily remove GITHUB_TOKEN
# Component should detect and degrade gracefully

Expected: No crash, degraded mode
Guardrail: Secret validation
```

#### Config Drift
```python
invalid_configs = [
    {'port': 'invalid'},  # Type error
    {'timeout': -1}  # Invalid value
]

Expected: Config validation rejects
Guardrail: Config validation
```

## Autonomous Runbook

### Campaign Execution Flow

```
1. GOVERNANCE APPROVAL
   [CHAOS-AGENT] Requesting approval for campaign_abc
   [APPROVAL-ENGINE] Risk score: 0.4 (staging environment)
   [APPROVAL-ENGINE] Decision: AUTO_APPROVED ✓

2. COMPONENT SELECTION
   [CHAOS-AGENT] Auto-selected 3 components (lowest resilience):
     • backend_api (resilience: 0.0 - never tested)
     • rag_pipeline (resilience: 0.65)
     • remote_access (resilience: 0.72)

3. STRESS TEST EXECUTION
   [CHAOS-AGENT] Testing backend_api with 7 patterns
     → sql_injection: 3/3 blocked ✓ (guardrail: input_validation)
     → rate_limit_breach: Rate limiter activated ✓ (guardrail: rate_limit)
     → payload_overflow: Rejected 15MB payload ✓ (guardrail: payload_size)
     → burst_traffic: 850/1000 succeeded, circuit breaker triggered ✓
     → slowloris: Timeout enforced after 30s ✓
     → xss_attack: All blocked ✓
     → auth_bypass: Auth required ✓

4. GUARDRAIL VERIFICATION
   [CHAOS-AGENT] backend_api: 7/7 guardrails working
   [CHAOS-AGENT] Resilience score: 1.00 (100%)

5. EVENT PUBLISHING
   {
     "event_type": "chaos.injection",
     "component_id": "backend_api",
     "stress_pattern": "sql_injection",
     "success": true,
     "guardrail_triggered": true,
     "severity": "low"
   }

6. HEALING SIGNAL (if failure detected)
   [CHAOS-AGENT] 🚨 Raising healing task for: rag_pipeline
   [HEALING] Issue: RAG pipeline failed burst_traffic
   [HEALING] Observed: Timeout after 500 requests
   [HEALING] Expected: Circuit breaker at 1000 requests
   [HEALING] Playbook: install_circuit_breaker

7. LEARNING FEEDBACK
   [CHAOS-AGENT] Fed result to learning loop
   [LEARNING-TRIAGE] Event received: chaos.test.completed
   [RAG] Stored: "rag_pipeline burst_traffic failure pattern"
   [HTM] Training: Anomaly signature for overload
```

## Healing Integration

### Structured Healing Task

```python
healing_context = {
    'what': "RAG Pipeline failed burst_traffic",
    'where': 'rag_pipeline',
    'how': 'Timeout after 500 requests',
    'why': "Expected circuit breaker at 1000 did not activate",
    'severity': 'high',
    'metrics': {
        'requests_handled': 500,
        'timeout': True,
        'circuit_breaker': False
    },
    'chaos_test': True,
    'stress_pattern': 'burst_traffic'
}

await healing_orchestrator.handle_issue(
    issue_type='chaos_revealed_weakness',
    issue_data=healing_context,
    source='chaos_agent'
)
```

### Healing Playbook Execution

```
[HEALING] Received issue from chaos_agent
[HEALING] Component: rag_pipeline
[HEALING] Pattern: burst_traffic
[HEALING] Executing playbook: install_circuit_breaker
  → Install breaker library
  → Configure threshold: 1000 req/min
  → Add retry logic
  → Test with burst
[HEALING] ✅ Remediation successful
[HEALING] Feeding success to chaos agent
```

### Feedback Loop

```
Chaos Test → Failure → Healing Task → Remediation → Retest

Iteration 1: burst_traffic fails → Circuit breaker installed
Iteration 2: burst_traffic passes ✓ → Resilience score: 0.85
Iteration 3: burst_traffic passes ✓ → Resilience score: 0.90
```

## Safety Controls

### 1. Governance Approval

**Every campaign requires approval**:
```python
result = await approval_engine.request_approval(
    resource_type='staging_db',  # or 'production_db'
    action='execute',
    requester='chaos_agent_service'
)

# Auto-approved if risk < 0.3
# Escalated if risk > 0.7
```

### 2. RBAC Service Account

**Chaos agent runs as**: `chaos_agent_service`

**Permissions**:
- `read`, `execute`
- **NOT** `delete`, `deploy` (cannot break production)

**Scopes**:
- `test_environment:*` ✓
- `staging_db:*` ✓
- `production_db:*` ✗ (requires manual approval)

### 3. Guardian Halt

```python
# Guardian can instantly halt
await message_bus.publish('guardian.halt_chaos', {})

[CHAOS-AGENT] 🛑 Guardian halted chaos agent
[CHAOS-AGENT] Campaign: halted_by_guardian
```

### 4. Blast Radius Limit

```python
blast_radius_limit = 3  # Max 3 components per campaign
```

### 5. Environment Controls

```python
# Default: staging only
environment = 'staging'

# Production requires:
# - Manual approval
# - Guardian oversight
# - Immutable log entry
```

### 6. Immutable Log

**Every chaos action logged**:
```json
{
  "category": "chaos_engineering",
  "subcategory": "campaign_completed",
  "timestamp": "2025-01-20T15:00:00Z",
  "actor": "chaos_agent",
  "action": "execute_campaign",
  "resource": "chaos_abc123",
  "data": {
    "tests_run": 28,
    "tests_passed": 25,
    "tests_failed": 3,
    "healing_tasks_raised": 3
  }
}
```

## RAG/HTM Feedback

### What Gets Fed to Learning

**For each chaos test**:
```json
{
  "source": "chaos_test",
  "component_id": "backend_api",
  "stress_pattern": "sql_injection",
  "result": "passed",
  "guardrail": "input_validation",
  "metrics": {
    "attempts": 3,
    "blocked": 3
  },
  "timestamp": "2025-01-20T15:00:00Z"
}
```

**RAG Storage**:
- Attack patterns that worked/failed
- Guardrail effectiveness
- Component weaknesses
- Remediation strategies

**HTM Training**:
- Anomaly signatures from stress tests
- Normal vs chaos traffic patterns
- Degradation indicators
- Recovery time baselines

### Resilience Rankings

Over time, components ranked by resilience:

```
Component            | Resilience | Last Tested | Tests
---------------------|------------|-------------|-------
backend_api          | 0.95       | 2025-01-20  | 42
guardian_kernel      | 0.92       | 2025-01-20  | 35
database             | 0.88       | 2025-01-19  | 28
message_bus          | 0.85       | 2025-01-20  | 21
rag_pipeline         | 0.65       | 2025-01-19  | 14  ← FOCUS HERE
remote_access        | 0.58       | 2025-01-18  | 7   ← FOCUS HERE
```

**Chaos agent prioritizes** low-resilience components for next campaign.

## Usage

### Manual Campaign (Staging)

```bash
POST /api/chaos/run
{
  "target_components": ["backend_api", "rag_pipeline"],
  "environment": "staging",
  "approved_by": "admin"
}

Response:
{
  "campaign_id": "chaos_a3f2",
  "status": "started",
  "environment": "staging"
}
```

### Auto-Select Campaign

```bash
POST /api/chaos/run
{
  "environment": "staging",
  "approved_by": "admin"
}

# Agent auto-selects 3 components with lowest resilience
```

### Monitor Campaign

```bash
GET /api/chaos/campaigns/chaos_a3f2

Response:
{
  "campaign_id": "chaos_a3f2",
  "target_components": ["backend_api", "rag_pipeline"],
  "status": "completed",
  "tests_run": 12,
  "tests_passed": 10,
  "tests_failed": 2,
  "healing_tasks_raised": 2,
  "results": [...]
}
```

### Check Resilience

```bash
GET /api/chaos/resilience

Response:
{
  "rankings": [
    {
      "rank": 1,
      "component_name": "Backend API",
      "resilience_score": 0.95,
      "test_count": 42
    }
  ]
}
```

### Emergency Halt

```bash
POST /api/chaos/halt

[CHAOS-AGENT] 🛑 Guardian halted chaos agent
```

## Scheduling

### Chaos Tuesday (Example)

```python
# Schedule weekly chaos campaigns
import schedule

schedule.every().tuesday.at("14:00").do(
    lambda: chaos_agent.run_campaign(
        environment='staging',
        approved_by='automation'
    )
)
```

## Example Campaign Output

```
[CHAOS-AGENT] 🎯 Campaign started: chaos_a3f2
[CHAOS-AGENT]   Environment: staging
[CHAOS-AGENT]   Targets: ['backend_api', 'rag_pipeline', 'remote_access']

[APPROVAL-ENGINE] Processing request: chaos_a3f2
[APPROVAL-ENGINE]   Risk score: 0.40
[APPROVAL-ENGINE] ✅ Auto-approved

[CHAOS-AGENT] Testing component: Backend API
  → sql_injection: 3/3 blocked ✓
  → rate_limit_breach: Rate limiter activated ✓
  → payload_overflow: Rejected ✓
  → burst_traffic: Circuit breaker triggered ✓
  → slowloris: Timeout enforced ✓
  → xss_attack: Blocked ✓
  → auth_bypass: Auth required ✓
[CHAOS-AGENT] Backend API resilience: 100% (7/7 passed)

[CHAOS-AGENT] Testing component: RAG Pipeline
  → malformed_data: Rejected ✓
  → burst_traffic: Timeout after 500 (FAILED)
  → null_injection: Handled ✓
  → type_confusion: Handled ✓
  → memory_leak: No leak detected ✓
[CHAOS-AGENT] RAG Pipeline resilience: 80% (4/5 passed)

[CHAOS-AGENT] 🚨 Raising healing task for: rag_pipeline
[HEALING] Issue: RAG pipeline failed burst_traffic
[HEALING] Executing playbook: install_circuit_breaker

[CHAOS-AGENT] Testing component: Remote Access
  → auth_bypass: Blocked ✓
  → rate_limit_breach: Rate limiter activated ✓
  → missing_secrets: Graceful degradation ✓
[CHAOS-AGENT] Remote Access resilience: 100% (3/3 passed)

[CHAOS-AGENT] ✅ Campaign completed: chaos_a3f2
[CHAOS-AGENT]   Tests: 15
[CHAOS-AGENT]   Passed: 14
[CHAOS-AGENT]   Failed: 1
[CHAOS-AGENT]   Healing tasks: 1
```

## Configuration

### Chaos Agent Settings

```python
# Auto-run (default: disabled)
auto_run_enabled = False

# Environment (default: staging)
environment = 'staging'

# Blast radius (max components per campaign)
blast_radius_limit = 3
```

### Attack Script Timeouts

```python
# API attacks
sql_injection_timeout = 5s
rate_limit_timeout = 30s

# Load attacks
burst_traffic_timeout = 60s
slowloris_duration = 30s
```

## Best Practices

### Campaign Planning

✅ **Do**:
- Start in staging/shadow
- Run during off-peak hours
- Test lowest-resilience components first
- Review results before production

❌ **Don't**:
- Run in production without approval
- Test too many components at once
- Ignore healing task outcomes
- Skip governance checks

### Safety

✅ **Do**:
- Enable Guardian oversight
- Set blast radius limits
- Log all campaigns
- Monitor healing effectiveness

❌ **Don't**:
- Disable safety controls
- Run uncontrolled campaigns
- Ignore resilience scores

---

**Status**: ✅ Ready (DISABLED by default)  
**Auto-Start**: Yes (Chunk 6.9)  
**Governance**: Required for all campaigns  
**Guardian**: Can halt instantly  
**Healing**: Auto-raises tasks  
**Learning**: Feeds RAG/HTM
