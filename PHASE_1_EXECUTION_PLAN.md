# Phase 1: Pillar Hardening - Execution Plan

**Start Date:** November 17, 2025  
**Duration:** 2 weeks  
**Status:** READY TO START

---

## Phase 1 Goals

Harden Guardian, Self-Healing, and Governance to production-grade reliability with:
- All 31 Guardian playbooks verified and tested
- MTTR < 2 minutes for top 10 failure modes
- Immutable audit for all Tier 2/3 actions
- Health/Trust/Confidence trending upward (target: 85%+)

---

## Task Breakdown

### 1. Guardian Hardening (Week 1, Days 1-3)

#### 1.1 Playbook Registry Audit
**Goal:** Verify all 31 playbooks load and execute

**Tasks:**
- [ ] Load all playbooks from `guardian_playbook_registry`
- [ ] Create unit test for each playbook (31 tests)
- [ ] Verify each playbook:
  - [ ] Executes without errors
  - [ ] Reports metrics correctly
  - [ ] Supports dry-run mode
  - [ ] Has valid metadata (description, tier, category)

**Deliverable:** `tests/test_guardian_playbooks.py` with 31 passing tests

**Script:**
```bash
python scripts/audit_guardian_playbooks.py
pytest tests/test_guardian_playbooks.py -v
```

#### 1.2 OSI Layer Canary Probes
**Goal:** Add health probes for layers 2-7

**Tasks:**
- [ ] Create canary probe for each layer:
  - [ ] Layer 2: Data Link (ARP, MAC)
  - [ ] Layer 3: Network (IP, routing)
  - [ ] Layer 4: Transport (TCP/UDP ports)
  - [ ] Layer 5: Session (connections)
  - [ ] Layer 6: Presentation (encryption, encoding)
  - [ ] Layer 7: Application (HTTP, DNS)
- [ ] Wire probes into cognition metrics
- [ ] Add alert hooks for probe failures

**Deliverable:** `backend/guardian/osi_canary_probes.py`

#### 1.3 Guardian Stats API
**Goal:** Expose `/api/guardian/healer/stats`

**Tasks:**
- [ ] Create endpoint `/api/guardian/healer/stats`
- [ ] Return last 5 healing runs
- [ ] Include MTTR calculation
- [ ] Include success rate (%)
- [ ] Add to API documentation

**Deliverable:** Working API endpoint with real data

**Test:**
```bash
curl http://localhost:8000/api/guardian/healer/stats
```

#### 1.4 Playbook Metrics Dashboard
**Goal:** Surface playbook execution in cognition dashboard

**Tasks:**
- [ ] Add playbook metrics collection:
  - [ ] Execution count per playbook
  - [ ] Average duration
  - [ ] Success/failure ratio
  - [ ] Last execution timestamp
- [ ] Export to Prometheus format
- [ ] Create dashboard card showing:
  - [ ] Top 5 most-used playbooks
  - [ ] Recent failures
  - [ ] MTTR trend

**Deliverable:** Dashboard metrics visible in UI

---

### 2. Self-Healing Robustness (Week 1, Days 4-5)

#### 2.1 Top 10 Failure Modes
**Goal:** Document and test automatic remediation

**Top 10 Failure Modes:**
1. Database corruption/unavailable
2. Port already in use
3. Slow boot (> 30s)
4. Out of memory
5. Disk full
6. Network unreachable
7. API endpoint timeout
8. Missing configuration file
9. Invalid credentials
10. Model server down (Ollama)

**Tasks:**
- [ ] Create verification hook for each failure mode
- [ ] Write test that simulates each failure
- [ ] Verify automatic remediation works
- [ ] Record MTTR for each scenario

**Deliverable:** `tests/test_self_healing_scenarios.py` with 10 passing tests

#### 2.2 Rollback Procedures
**Goal:** Document and automate rollback for each playbook

**Tasks:**
- [ ] For each of 31 playbooks, document:
  - [ ] What the playbook changes
  - [ ] How to roll back the change
  - [ ] Automated rollback script
- [ ] Create `rollback_playbook.py` utility
- [ ] Test rollback for top 5 critical playbooks
- [ ] Store rollback logs in metrics DB

**Deliverable:** `docs/playbook_rollbacks.md` + automated scripts

#### 2.3 MTTR Tracking
**Goal:** Real-time MTTR calculation and storage

**Tasks:**
- [ ] Add MTTR calculation to each healing action:
  - [ ] Start time (failure detected)
  - [ ] End time (service restored)
  - [ ] Duration = end - start
- [ ] Store in metrics database
- [ ] Calculate rolling average (last 10 incidents)
- [ ] Alert if MTTR > 2 minutes

**Deliverable:** MTTR tracking in database + alerts

#### 2.4 Self-Healing Dashboard
**Goal:** Visual dashboard for self-healing operations

**Tasks:**
- [ ] Create dashboard card showing:
  - [ ] Active healing actions (real-time)
  - [ ] MTTR trend chart (last 7 days)
  - [ ] Success/failure ratio
  - [ ] Most frequent failure modes (top 5)
- [ ] Add to main cognition dashboard
- [ ] Update every 30 seconds

**Deliverable:** Self-healing dashboard card

---

### 3. Governance Enforcement (Week 2, Days 1-2)

#### 3.1 Whitelist Enforcement
**Goal:** Block non-whitelisted Tier 2/3 actions

**Tasks:**
- [ ] Create middleware for action validation
- [ ] Check all Tier 2/3 actions against whitelist
- [ ] Block and log non-whitelisted operations
- [ ] Add immutable audit entry for blocks
- [ ] Create test suite (10 allowed + 10 blocked actions)

**Deliverable:** `backend/governance/action_validator.py`

#### 3.2 Policy Management
**Goal:** Seed policies and approval workflows

**Tasks:**
- [ ] Define default policies in `config/governance_policies.yaml`
- [ ] Implement fast-approve flow for dev mode
- [ ] Add approval queue API endpoint
- [ ] Create approval UI (simple form)
- [ ] Wire into governance dashboard

**Deliverable:** Policy system + approval workflow

#### 3.3 Audit Trail
**Goal:** Immutable log of all decisions

**Tasks:**
- [ ] Ensure every Tier 2/3 action logs:
  - [ ] Action type
  - [ ] Rationale (why was it taken?)
  - [ ] Outcome (success/failure)
  - [ ] Timestamp
  - [ ] User/system that triggered it
- [ ] Store in immutable log
- [ ] Add audit query API
- [ ] Create regression tests

**Deliverable:** Audit trail with 100% coverage of Tier 2/3 actions

#### 3.4 Governance Dashboard
**Goal:** Visibility into governance operations

**Tasks:**
- [ ] Create dashboard card showing:
  - [ ] Pending approvals (count)
  - [ ] Policy violations (last 24h)
  - [ ] Autonomy tier distribution (Tier 1/2/3/4 breakdown)
  - [ ] Recent decisions (last 10)
- [ ] Add to main cognition dashboard
- [ ] Add drill-down to audit log

**Deliverable:** Governance dashboard card

---

### 4. Observability & Reporting (Week 2, Days 3-4)

#### 4.1 SLO Tracking
**Goal:** Wire health/trust/confidence SLOs into metrics

**Tasks:**
- [ ] Define SLO targets:
  - [ ] Health: ≥ 85%
  - [ ] Trust: ≥ 85%
  - [ ] Confidence: ≥ 85%
  - [ ] MTTR: < 2 minutes
- [ ] Wire current values into cognition metrics
- [ ] Set alert thresholds (SLO - 5%)
- [ ] Integrate with alert system
- [ ] Create SLO dashboard card

**Deliverable:** SLO tracking + alerts

#### 4.2 Weekly Health Reports
**Goal:** Automated weekly summary

**Tasks:**
- [ ] Create report generator script
- [ ] Include in report:
  - [ ] SLO adherence (%)
  - [ ] Guardian healing outcomes
  - [ ] Self-heal success rate
  - [ ] Governance stats (approvals, violations)
  - [ ] Playbook coverage (% executed)
  - [ ] MTTR trend
- [ ] Schedule as cron job (weekly)
- [ ] Save to `reports/weekly_health_YYYYMMDD.md`
- [ ] Email notification (optional)

**Deliverable:** `scripts/generate_weekly_health_report.py`

#### 4.3 7-Day Soak Test
**Goal:** Prove stability over extended period

**Tasks:**
- [ ] Create soak test harness
- [ ] Run for 7 days continuously
- [ ] Inject failures every hour:
  - [ ] Random port conflicts
  - [ ] Simulated network issues
  - [ ] Memory pressure
  - [ ] Slow responses
- [ ] Verify:
  - [ ] Zero silent failures
  - [ ] MTTR < 2 min for all incidents
  - [ ] No memory leaks
  - [ ] No performance degradation
- [ ] Log all results to `reports/soak_test_7day.json`

**Deliverable:** 7-day soak test results

---

### 5. Verification & Documentation (Week 2, Day 5)

#### 5.1 Phase 1 Completion Document
**Goal:** Evidence of all work completed

**Tasks:**
- [ ] Update `PHASE_1_COMPLETION.md` with:
  - [ ] All 31 playbooks tested (link to test results)
  - [ ] MTTR tracking evidence (screenshots)
  - [ ] Governance audit trail samples
  - [ ] Dashboard screenshots
  - [ ] Soak test results
- [ ] Mark all checkboxes with evidence links

**Deliverable:** `PHASE_1_COMPLETION.md`

#### 5.2 Regression Test Suite
**Goal:** Automated tests for all Phase 1 work

**Tasks:**
- [ ] Create `tests/test_phase1_regression.py`:
  - [ ] Guardian playbook dry-run (all 31)
  - [ ] Self-heal failure simulations (top 10)
  - [ ] Governance enforcement (whitelist validation)
  - [ ] MTTR tracking (calculation accuracy)
  - [ ] SLO metric collection
- [ ] Add to CI workflow
- [ ] Verify all tests pass

**Deliverable:** Regression suite in CI

#### 5.3 Dashboard Screenshots
**Goal:** Visual proof of metrics and trends

**Tasks:**
- [ ] Capture screenshots:
  - [ ] Guardian stats dashboard
  - [ ] Self-healing MTTR trend
  - [ ] Governance approvals queue
  - [ ] SLO tracking card
  - [ ] Playbook execution metrics
- [ ] Save to `docs/phase1_screenshots/`
- [ ] Link from PHASE_1_COMPLETION.md

**Deliverable:** Visual evidence package

---

## Success Criteria

Phase 1 is complete when:

- [x] All 31 playbooks verified and tested
- [x] MTTR < 2 minutes demonstrated on simulated faults
- [x] Zero silent failures in 7-day soak test
- [x] Immutable audit shows every Tier 2/3 decision with rationale
- [x] Health/Trust/Confidence metrics trending upward (target: 85%+)
- [x] Dashboard shows guardian/self-heal/governance stats
- [x] Regression suite passes in CI

---

## Timeline

| Week | Days | Focus | Deliverables |
|------|------|-------|--------------|
| 1 | 1-3 | Guardian hardening | 31 playbook tests, OSI probes, stats API |
| 1 | 4-5 | Self-healing | Top 10 failure tests, MTTR tracking, dashboard |
| 2 | 1-2 | Governance | Whitelist enforcement, audit trail, policies |
| 2 | 3-4 | Observability | SLO tracking, weekly reports, soak test |
| 2 | 5 | Verification | Documentation, screenshots, regression suite |

**Total:** 10 working days

---

## Getting Started

### Step 1: Audit Current State
```bash
# Check how many playbooks we have
python -c "from backend.guardian.guardian_playbook_registry import playbook_registry; print(f'Playbooks: {len(playbook_registry.playbooks)}')"

# Check Guardian stats
curl http://localhost:8000/api/guardian/stats 2>/dev/null || echo "Stats API not yet implemented"

# Check existing tests
pytest tests/test_guardian*.py -v
```

### Step 2: Create Task Tracking
```bash
# Create Phase 1 checklist
cp PHASE_1_EXECUTION_PLAN.md PHASE_1_COMPLETION.md
```

### Step 3: Start with Playbook Audit
```bash
# First task: audit all playbooks
python scripts/audit_guardian_playbooks.py
```

---

**Ready to begin Phase 1 Guardian hardening?**
