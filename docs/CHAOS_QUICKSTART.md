# Chaos Engineering - Quick Start

## Status

✅ **Chaos Agent**: Ready  
✅ **RBAC Account**: chaos_agent_service created  
✅ **Governance**: Configured (auto-approve staging)  
✅ **Configuration**: chaos_config.json enabled  

---

## Start Grace

```bash
python server.py
```

Expected output:
```
[CHUNK 6.9] Chaos Engineering Agent...
  [OK] Chaos Agent: Ready (ENABLED)
  [OK] Component profiles: 8
  [OK] Configuration loaded from chaos_config.json
  [OK]   Enabled: True
  [OK]   Environment: staging
  [OK]   Auto-run: False
```

---

## Run Your First Chaos Campaign

### Option 1: Via API

```bash
# Start a chaos campaign
curl -X POST http://localhost:8000/api/chaos/run \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "staging",
    "approved_by": "admin"
  }'

Response:
{
  "campaign_id": "chaos_abc123",
  "status": "started",
  "environment": "staging"
}

# Monitor the campaign
curl http://localhost:8000/api/chaos/campaigns/chaos_abc123
```

### Option 2: Via Python

```python
import asyncio
from backend.chaos.chaos_agent import chaos_agent

async def run_chaos():
    await chaos_agent.start()
    
    # Run campaign
    campaign_id = await chaos_agent.run_campaign(
        environment='staging',
        approved_by='admin'
    )
    
    print(f"Campaign started: {campaign_id}")

asyncio.run(run_chaos())
```

---

## What Will Happen

### 1. Governance Approval
```
[APPROVAL-ENGINE] Processing request: chaos_abc123
[APPROVAL-ENGINE]   Resource: staging_db
[APPROVAL-ENGINE]   Risk score: 0.40
[APPROVAL-ENGINE] ✅ Auto-approved (risk < 0.7)
```

### 2. Component Selection
```
[CHAOS-AGENT] Auto-selected 3 components (lowest resilience):
  • backend_api (resilience: 0.0 - never tested)
  • rag_pipeline (resilience: 0.0)
  • remote_access (resilience: 0.0)
```

### 3. Stress Testing
```
[CHAOS-AGENT] Testing Backend API with 7 patterns
  → sql_injection: 3/3 blocked ✓
  → rate_limit_breach: Rate limiter activated ✓
  → payload_overflow: Rejected 15MB ✓
  → burst_traffic: Circuit breaker triggered ✓
  → slowloris: Timeout enforced ✓
  → xss_attack: Blocked ✓
  → auth_bypass: Auth required ✓

[CHAOS-AGENT] Backend API resilience: 100% (7/7 passed)
```

### 4. Failure Detection & Healing
```
[CHAOS-AGENT] Testing RAG Pipeline with 5 patterns
  → malformed_data: Rejected ✓
  → burst_traffic: Timeout after 500 (FAILED) ✗
  → null_injection: Handled ✓

[CHAOS-AGENT] 🚨 Raising healing task for: rag_pipeline
[HEALING] Issue: RAG pipeline failed burst_traffic
[HEALING] Executing playbook: install_circuit_breaker
[HEALING] ✅ Remediation successful
```

### 5. Learning Feedback
```
[LEARNING-TRIAGE] Event received: chaos.test.completed
[LEARNING-TRIAGE] Cluster: rag:medium:failure
[RAG] Stored: "rag_pipeline burst_traffic pattern"
```

---

## View Results

### Dashboard
```bash
curl http://localhost:8000/api/chaos/campaigns

{
  "campaigns": [{
    "campaign_id": "chaos_abc123",
    "status": "completed",
    "tests_run": 15,
    "tests_passed": 14,
    "tests_failed": 1,
    "healing_tasks_raised": 1
  }]
}
```

### Resilience Rankings
```bash
curl http://localhost:8000/api/chaos/resilience

{
  "rankings": [
    {
      "rank": 1,
      "component_name": "Backend API",
      "resilience_score": 1.00,
      "test_count": 7
    },
    {
      "rank": 2,
      "component_name": "RAG Pipeline",
      "resilience_score": 0.80,
      "test_count": 5
    }
  ]
}
```

---

## Safety Controls

### Emergency Halt
```bash
curl -X POST http://localhost:8000/api/chaos/halt

[CHAOS-AGENT] 🛑 Guardian halted chaos agent
```

### Production Requires Approval
```bash
curl -X POST http://localhost:8000/api/chaos/run \
  -d '{
    "environment": "production",
    "approved_by": "admin"
  }'

[APPROVAL-ENGINE] Risk score: 0.90 (production)
[APPROVAL-ENGINE] ⚠️ Escalated to Guardian
```

### Guardian Override
Guardian can halt any campaign via message bus.

---

## Configuration

Edit `config/chaos_config.json`:

```json
{
  "chaos_enabled": true,
  "environment": "staging",
  "auto_run": false,
  "blast_radius_limit": 3
}
```

**Settings**:
- `chaos_enabled`: Enable/disable chaos entirely
- `environment`: staging, shadow, or production
- `auto_run`: Auto-run campaigns (use with caution)
- `blast_radius_limit`: Max components per campaign

---

## Best Practices

### Start Small
```bash
# Test 1 component first
POST /api/chaos/run
{
  "target_components": ["backend_api"],
  "environment": "staging",
  "approved_by": "admin"
}
```

### Review Results
```bash
# Check what failed
GET /api/chaos/campaigns/chaos_abc123

# Review healing tasks
GET /api/learning-feedback/missions

# Check resilience improvements
GET /api/chaos/resilience
```

### Iterative Improvement
1. Run chaos campaign
2. Review failures
3. Let healing fix issues
4. Rerun campaign
5. Verify resilience improved

---

**Chaos Engineering**: APPROVED & READY ✅  
**Default Environment**: Staging (safe) ✅  
**Guardian Control**: Active ✅  
**Service Account**: chaos_agent_service (read, execute) ✅
