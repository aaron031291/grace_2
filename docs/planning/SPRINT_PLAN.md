# GRACE Self-Healing Sprint Plan

## 📍 Starting Position

**Foundation Complete:**
- ✅ Agentic architecture (memory broker, meta coordination, intelligent triggers)
- ✅ Trust core integration
- ✅ Complete documentation (6 docs)
- ✅ Two domains in observe mode (Core, Self-Healing)
- ✅ **Session 1 Complete:** Observability endpoints

**System Status:**
- Runs successfully in observe-only mode
- Meta loop coordinates every 2 minutes
- Self-healing predictor analyzes trends
- All access governed and logged

**Key Observability/Governance Gaps:**
- ⏳ Change window enforcement (Session 2)
- ⏳ Runner timeout watchdog (Session 2)
- ⏳ Parameter bounds validation (Session 2)
- ⏳ Duplicate request prevention (Session 2)
- ⏳ Testing & verification (Session 3)

---

## 🏃 Sprint 1: Core Completion (Weeks 1-2)

**Goal:** Self-healing goes from "architected" to "production-ready"

### ✅ Session 1: Observability Endpoints (COMPLETE)
**Duration:** 2-3 hours  
**Status:** ✅ **DONE**

**Delivered:**
- ✅ GET /api/self_heal/learning (aggregates with 24h/7d buckets)
- ✅ GET /api/self_heal/scheduler_counters (real-time observability)
- ✅ GET /api/meta/focus (health distress summary)
- ✅ Bonus endpoints: /learning/outcomes, /scheduler_health, /meta/cycles
- ✅ Feature-gated registration
- ✅ Test guide (TEST_NEW_ENDPOINTS.md)

**Outcome:** Full visibility into meta loop, scheduler, and learning.

---

### ⏳ Session 2: Governance Hardening (NEXT)
**Duration:** 2-3 hours  
**Status:** Ready to start

**Tasks:**

#### 1. Change Window Enforcement ⏰
```python
# In runner._tick() before execution
def _is_outside_change_window(now: datetime) -> bool:
    # Weekdays 09:00-18:00 local time
    local = now.astimezone()
    wk = local.weekday()  # 0=Mon
    hr = local.hour
    return not ((wk <= 4) and (9 <= hr < 18))

# Block execution
if _is_outside_change_window(now):
    impact = get_impact_from_diagnosis(run.diagnosis)
    if impact in {"medium", "high", "critical"}:
        # Require explicit approval
        if not has_override_approval(run):
            await abort_run(run, "blocked_change_window")
            return
```

#### 2. Runner Timeout Watchdog ⏱️
```python
# In runner._tick()
from ..settings import settings

timeout_seconds = settings.SELF_HEAL_RUN_TIMEOUT_MIN * 60

try:
    await asyncio.wait_for(
        self._execute_playbook_run(run),
        timeout=timeout_seconds
    )
except asyncio.TimeoutError:
    run.status = "aborted"
    run.ended_at = datetime.now(timezone.utc)
    
    # Create learning entry for timeout
    session.add(LearningLog(
        service=run.service,
        diagnosis=run.diagnosis,
        action=json.dumps({"status": "aborted", "reason": "timeout"}),
        outcome=json.dumps({"result": "timeout", "timeout_min": settings.SELF_HEAL_RUN_TIMEOUT_MIN})
    ))
```

#### 3. Parameter Bounds Validation 🔒
```python
# In runner._execute_action()
PARAMETER_BOUNDS = {
    "scale_instances": {
        "min_delta": {"type": int, "min": -3, "max": 3}
    },
    "set_logging_level": {
        "level": {"type": str, "allowed": ["DEBUG", "INFO", "WARN", "ERROR"]},
        "ttl_min": {"type": int, "min": 1, "max": 120}
    },
    "toggle_flag": {
        "flag": {"type": str, "pattern": r"^[a-z_]+$"},
        "state": {"type": bool}
    }
}

def validate_parameters(action: str, params: Dict) -> Tuple[bool, str]:
    bounds = PARAMETER_BOUNDS.get(action)
    if not bounds:
        return True, "no_validation"
    
    for key, rules in bounds.items():
        if key not in params:
            continue
        
        value = params[key]
        
        # Type check
        if not isinstance(value, rules.get("type")):
            return False, f"Invalid type for {key}"
        
        # Min/max for numbers
        if "min" in rules and value < rules["min"]:
            return False, f"{key} below minimum"
        if "max" in rules and value > rules["max"]:
            return False, f"{key} exceeds maximum"
        
        # Allowed values
        if "allowed" in rules and value not in rules["allowed"]:
            return False, f"{key} not in allowed values"
    
    return True, "validated"
```

#### 4. Duplicate Request Prevention 🚫
```python
# In scheduler._tick() before creating ApprovalRequest
async def _has_recent_approval_request(session, run_id: int, service: str, diag_code: str, minutes: int = 10) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    
    result = await session.execute(
        select(ApprovalRequest)
        .join(PlaybookRun, ApprovalRequest.event_id == PlaybookRun.id)
        .where(
            PlaybookRun.service == service,
            PlaybookRun.diagnosis.contains(diag_code),
            ApprovalRequest.created_at >= cutoff
        )
    )
    
    return result.scalar_one_or_none() is not None

# Use it:
if not await self._has_recent_approval_request(session, run.id, svc.name, diag_code):
    await self._create_approval_request(session, run, reason=...)
```

**Deliverables:**
- ✅ Change window hard enforcement
- ✅ Global timeout watchdog
- ✅ Parameter validation
- ✅ Duplicate prevention
- ✅ AuditLog expansion (all transitions)

**Outcome:** Production-safe governance and guardrails.

---

### ⏳ Session 3: Testing & Verification
**Duration:** 2 hours  
**Status:** Planned

**Tasks:**

#### 1. Run Backend Smoke Test
```bash
python backend/minimal_backend.py
# Verify: All systems start without errors
# Check: Logs show meta loop cycles
# Confirm: Endpoints respond
```

#### 2. Run CLI Smoke Test
```bash
python scripts/cli_test.py smoke
# Expected: All tests pass
```

#### 3. Run Health Smoke Test
```bash
python scripts/health_smoke.py
# Expected: Scheduler creates proposals (observe-only)
# Verify: PlaybookRun rows in DB with status="proposed"
```

#### 4. Verify Alembic Migrations
```bash
alembic current
alembic history
# Expected: Single head, no conflicts
```

#### 5. Test Approval Flow (Manual)
```python
# 1. Find a proposed run
run = await session.execute(
    select(PlaybookRun).where(PlaybookRun.status == "proposed")
).scalar_one()

# 2. Approve it
run.status = "approved"
await session.commit()

# 3. Watch runner execute (if SELF_HEAL_EXECUTE=True)
# 4. Verify outcome in learning endpoint
```

#### 6. Test Rollback Scenario
```python
# Simulate verification failure
# Expected: Runner rolls back, creates incident, logs outcome
```

**Deliverables:**
- ✅ All smoke tests pass
- ✅ Migrations verified
- ✅ Approval flow tested
- ✅ Rollback tested
- ✅ Endpoints spot-checked

**Outcome:** Confidence to enable execute mode.

---

## 🏃 Sprint 2: Domain Expansion (Weeks 3-4)

**Goal:** 6 of 10 domains live with repeatable pattern

### Session 4: Knowledge Domain
**Duration:** 3-4 hours

**Tasks:**
1. Create `backend/domains/knowledge_domain_adapter.py`
2. Define telemetry (ingestion_rate, search_queries, trust_scores, graph_size)
3. Define health nodes (knowledge_graph, search_index, trust_scorer, ingestion_pipeline)
4. Define playbooks (rebuild_index, refresh_sources, update_trust_scores, compact_graph)
5. Implement adapter methods (collect_metrics, execute_action, verify_state)
6. Register with agent_core
7. Test memory integration (episodic: search history, semantic: facts, procedural: rebuild procedures)

**Deliverable:** Knowledge domain fully integrated

### Session 5: Security Domain
**Duration:** 3-4 hours

**Tasks:**
1. Create `backend/domains/security_domain_adapter.py`
2. Define telemetry (threats_detected, quarantine_rate, false_positives, alert_velocity)
3. Define health nodes (threat_detector, quarantine_service, alert_system, hunter_engine)
4. Define playbooks (isolate_threat, expand_quarantine, rollback_permissions, tune_sensitivity)
5. Implement adapter
6. Test cross-domain memory (learn from knowledge threat patterns)

**Deliverable:** Security domain (Hunter) integrated

### Session 6: ML Domain
**Duration:** 3-4 hours

**Tasks:**
1. Create `backend/domains/ml_domain_adapter.py`
2. Define telemetry (training_jobs, model_accuracy, drift_detected, inference_latency)
3. Define health nodes (training_cluster, model_registry, inference_service, auto_retrain)
4. Define playbooks (retrain_model, rollback_deployment, scale_inference, checkpoint_recovery)
5. Implement adapter
6. Test memory (training history, hyperparameters, model results)

**Deliverable:** ML domain integrated, feeds back into intelligence

### Session 7: Temporal Domain
**Duration:** 2-3 hours

**Tasks:**
1. Create `backend/domains/temporal_domain_adapter.py`
2. Define telemetry (predictions_made, prediction_accuracy, simulations_run, causal_inferences)
3. Define health nodes (causal_graph, forecaster, simulator)
4. Define playbooks (rebuild_causal_graph, retrain_forecaster, invalidate_cache)
5. Implement adapter

**Deliverable:** Temporal domain for causal reasoning

### Session 8: Cross-Domain Testing
**Duration:** 2 hours

**Tasks:**
1. Test cross-domain memory requests
2. Test meta loop coordinates all 6 domains
3. Test knowledge → security cross-domain learning
4. Verify domain isolation
5. Check governance on cross-domain access

**Deliverable:** 6 domains working together

**Sprint 2 Outcome:** 60% of domains complete, pattern established for remaining 4.

---

## 🏃 Sprint 3: Intelligence Boost (Weeks 5-6)

**Goal:** GRACE learns, predicts, and explains autonomously

### Session 9: Adaptive Playbook Ranking
**Duration:** 3-4 hours

**Implementation:**
```python
# backend/ml_playbook_ranker.py

class AdaptivePlaybookRanker:
    # Thompson Sampling per (service, diagnosis)
    # Features: time_of_day, load, blast_radius, recent_success
    # Train on LearningLog outcomes
    # Return ranked playbooks with confidence
```

**Integration:**
- ML advisor in meta_coordinated_healing uses this
- Replaces static playbook selection
- Learns from every execution

**Deliverable:** Playbook success rate improves >10%

### Session 10: Anomaly Forecasting
**Duration:** 4-6 hours

**Implementation:**
```python
# backend/ml_forecaster.py

Models:
- LSTM per metric (latency, errors, CPU, memory)
- Prophet for seasonality
- Exponential smoothing baseline

# Predict value at t+15min with confidence interval
# If predicted > threshold + (2 * std_dev) → trigger
```

**Integration:**
- Proactive_intelligence uses forecaster
- Publishes predictions to intelligent_triggers
- Meta loop decides whether to act

**Deliverable:** Anomaly prediction accuracy >75%

### Session 11: Root Cause Inference
**Duration:** 4-6 hours

**Implementation:**
```python
# backend/ml_root_cause.py

# Bayesian Network from immutable log
# P(symptom | root_cause)
# Counterfactual: "What if we hadn't acted?"
# Ranked root causes by posterior probability
```

**Integration:**
- ML root_cause advisor uses this
- Feeds to meta loop
- Improves diagnosis accuracy

**Deliverable:** Root cause identification >80% accurate

### Session 12: Cross-Domain Pattern Learning
**Duration:** 3-4 hours

**Implementation:**
```python
# backend/cross_domain_learner.py

# Association rules: "A → B within 10min"
# Temporal patterns across domains
# Correlation detection
# Prediction rules for meta loop
```

**Deliverable:** Cross-domain patterns detected and used

**Sprint 3 Outcome:** Self-learning GRACE with predictive capabilities.

---

## 🏃 Sprint 4: Production Hardening (Weeks 7-8)

**Goal:** Enterprise-grade reliability and security

### Session 13-14: Testing Suite
**Duration:** 4-6 hours

**Unit Tests:**
```python
tests/
├── test_agentic_memory.py (memory broker)
├── test_meta_coordination.py (meta loop)
├── test_intelligent_triggers.py (trigger manager)
├── test_domain_adapters.py (all domains)
├── test_immutable_log.py (signatures, replay)
└── test_trust_integration.py (governance)
```

**Integration Tests:**
```python
tests/integration/
├── test_self_heal_flow.py (end-to-end healing)
├── test_cross_domain_memory.py (domain isolation)
├── test_autonomous_approval.py (trust decisions)
└── test_meta_loop_cycle.py (full cycle)
```

**Coverage Target:** >80%

### Session 15-16: Scaling & Distribution
**Duration:** 4-6 hours

**Distributed State:**
```python
# Replace in-memory with distributed

1. Agentic Memory → Redis
   - working_memory → Redis hashes
   - access_patterns → Redis sorted sets
   
2. Immutable Log → PostgreSQL
   - Proper indexing
   - Replication support
   
3. Meta Coordination → Leader Election
   - etcd/Consul for leader election
   - Single active meta loop
   - Failover support
```

### Session 17-18: Security Hardening
**Duration:** 4-6 hours

**Security Layers:**
```python
1. Cryptographic Signatures
   - Ed25519 keypairs
   - Signature verification
   - Key rotation

2. Secrets Management
   - HashiCorp Vault integration
   - Encrypted credentials
   
3. Network Security
   - mTLS between domains
   - Certificate management
   
4. Access Control
   - Fine-grained RBAC
   - Privilege audit
```

### Session 19-20: Monitoring & Alerts
**Duration:** 4-6 hours

**Observability Stack:**
```python
1. Prometheus Metrics
   - Meta loop cycle duration
   - Memory access latency
   - Autonomous approval rate
   
2. Grafana Dashboards
   - System health overview
   - Domain activity
   - Self-healing outcomes
   
3. Alerting
   - Meta loop failures
   - High rejection rates
   - Immutable log corruption
   
4. SLOs
   - 99.9% meta loop uptime
   - <100ms memory p99
   - >90% self-heal success
```

**Sprint 4 Outcome:** Production-grade, secure, scalable GRACE.

---

## 🌐 Federation & Integrations (Parallel/Ongoing)

**As needs arise, integrate external systems**

### Integration Set 1: Infrastructure
- **Kubernetes** - Monitor pods, scale deployments, rollback releases
- **AWS/Azure/GCP** - Cloud resource management, auto-scaling
- **Terraform** - Infrastructure as code execution

### Integration Set 2: Observability
- **Prometheus** - Pull metrics, push GRACE metrics
- **Datadog** - Event correlation, APM integration
- **Grafana** - Dashboards and visualization

### Integration Set 3: Collaboration
- **Slack/Teams** - Approval workflows, incident notifications
- **PagerDuty** - Incident escalation
- **Jira** - Ticket creation and tracking

**Approach:** Build per business need, 1-2 sessions per integration

---

## 📊 Sprint Progress Tracking

### Sprint 1: Core Completion
- ✅ **Session 1:** Observability endpoints (DONE)
- ⏳ **Session 2:** Governance hardening (NEXT - 2-3 hours)
- ⏳ **Session 3:** Testing & verification (2 hours)

**Progress:** 33% complete

### Sprint 2: Domain Expansion  
- ⏳ **Session 4:** Knowledge domain (3-4 hours)
- ⏳ **Session 5:** Security domain (3-4 hours)
- ⏳ **Session 6:** ML domain (3-4 hours)
- ⏳ **Session 7:** Temporal domain (2-3 hours)
- ⏳ **Session 8:** Cross-domain testing (2 hours)

**Progress:** 0% (starts after Sprint 1)

### Sprint 3: Intelligence Boost
- ⏳ **Session 9:** Adaptive playbook ranking (3-4 hours)
- ⏳ **Session 10:** Anomaly forecasting (4-6 hours)
- ⏳ **Session 11:** Root cause inference (4-6 hours)
- ⏳ **Session 12:** Cross-domain patterns (3-4 hours)

**Progress:** 0% (starts after Sprint 2)

### Sprint 4: Production Hardening
- ⏳ **Session 13-14:** Testing suite (4-6 hours)
- ⏳ **Session 15-16:** Scaling (4-6 hours)
- ⏳ **Session 17-18:** Security (4-6 hours)
- ⏳ **Session 19-20:** Monitoring (4-6 hours)

**Progress:** 0% (starts after Sprint 3)

---

## ⏭️ **What's Next**

### **Immediate Next: Sprint 1, Session 2**

When ready, just say: **"Let's do Session 2"**

I'll implement:
1. Change window enforcement
2. Runner timeout watchdog
3. Parameter bounds validation
4. Duplicate request prevention

**Duration:** 2-3 hours  
**Outcome:** Production-safe governance

---

### **After Session 2: Sprint 1, Session 3**

Testing & verification to complete Sprint 1.

**Then:** Choose your path:
- Continue with Sprint 2 (domain expansion)
- Jump to Sprint 3 (intelligence boost)
- Start Sprint 4 (production prep)
- Add federation integrations

---

## 🎯 **Recommended Flow**

**Linear Progression:**
Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4

**Parallel Approach:**
- Sprint 1 + Sprint 2 in parallel (observability + domains)
- Then Sprint 3 (intelligence needs domains)
- Then Sprint 4 (production needs intelligence)

**Agile Approach:**
- Complete 1-2 sessions, pause and reassess
- Pivot based on business priorities
- Add integrations as needed

---

## 📈 **Success Milestones**

### Sprint 1 Complete ✓
- ✅ Learning analytics live
- ✅ Scheduler transparent
- ✅ Meta focus visible
- ✅ Change windows enforced
- ✅ All tests pass

### Sprint 2 Complete ✓
- ✅ 6 domains integrated
- ✅ Cross-domain memory working
- ✅ Meta loop coordinates all
- ✅ Pattern established for remaining 4

### Sprint 3 Complete ✓
- ✅ Playbooks rank adaptively
- ✅ Anomalies predicted 15min ahead
- ✅ Root causes identified accurately
- ✅ Cross-domain patterns detected

### Sprint 4 Complete ✓
- ✅ Test coverage >80%
- ✅ Production-grade infrastructure
- ✅ Security hardened
- ✅ Full monitoring/alerting

---

## 🚀 **You Are Here**

```
Sprint 1 [▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░] 33%
├─ Session 1 ✅ DONE
├─ Session 2 ⏳ NEXT (ready to start)
└─ Session 3 ⏳ Planned

Sprint 2 [░░░░░░░░░░░░░░░░░░░░] 0%
Sprint 3 [░░░░░░░░░░░░░░░░░░░░] 0%
Sprint 4 [░░░░░░░░░░░░░░░░░░░░] 0%
```

**Next command:** *"Let's do Session 2"* when you're ready! 🎯
