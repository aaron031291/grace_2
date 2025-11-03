# Parliament System - Quick Start Guide

## Installation

### 1. Seed Parliament Database

```bash
# Windows
seed_parliament.bat

# Linux/Mac
python backend/seed_parliament.py
```

This creates:
- ✅ Default committees (security, execution, knowledge, meta, general)
- ✅ Grace agent members (grace_reflection, grace_hunter, grace_meta, grace_causal, grace_parliament)
- ✅ Admin user as member

### 2. Run Tests

```bash
# Windows
test_parliament.bat

# Linux/Mac
python tests/test_parliament.py
```

## Quick Usage

### CLI Commands

```bash
# List active voting sessions
grace parliament sessions

# View specific session
grace parliament session <session_id>

# Cast your vote
grace parliament vote <session_id> --approve -m "Reason"
grace parliament vote <session_id> --reject -m "Reason"
grace parliament vote <session_id> --abstain

# View members
grace parliament members

# View statistics
grace parliament stats

# Grace monitoring
grace parliament monitor --auto-vote
```

### Python API

```python
from backend.parliament_engine import parliament_engine
from backend.grace_parliament_agent import grace_voting_agent

# Create a voting session
session = await parliament_engine.create_session(
    policy_name="critical_action",
    action_type="execute",
    action_payload={"command": "deploy to production"},
    actor="admin",
    category="execution",
    resource="production_server",
    committee="security",
    quorum_required=3,
    approval_threshold=0.66,
    risk_level="high"
)

# Grace auto-votes
result = await grace_voting_agent.cast_automated_vote(session["session_id"])

# Cast manual vote
vote = await parliament_engine.cast_vote(
    session_id=session["session_id"],
    member_id="admin",
    vote="approve",
    reason="Tested and verified"
)

# Check result
if vote["decision"]["status"] == "approved":
    print("✅ Action approved!")
elif vote["decision"]["status"] == "rejected":
    print("❌ Action rejected")
else:
    print(f"⏳ Voting continues ({vote['decision']['votes_needed']} more votes)")
```

### REST API

```bash
# List sessions
curl http://localhost:8000/api/parliament/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get session details
curl http://localhost:8000/api/parliament/sessions/{session_id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Cast vote
curl -X POST http://localhost:8000/api/parliament/sessions/{session_id}/vote \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vote": "approve",
    "reason": "Action looks safe",
    "automated": false
  }'

# Get statistics
curl http://localhost:8000/api/parliament/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Integration with Governance

Parliament automatically activates when governance policies return "review":

```python
from backend.governance import governance_engine

# This will trigger parliament voting if policy requires "review"
result = await governance_engine.check(
    actor="admin",
    action="execute",
    resource="critical_system",
    payload={"command": "dangerous operation"}
)

if result["decision"] == "parliament_pending":
    print(f"🏛️ Parliament session created: {result['parliament_session_id']}")
    # Grace will auto-vote
    # Human members should vote via CLI or UI
```

## Typical Workflow

1. **Action Triggers Governance**
   - User or system attempts action
   - Governance policy requires "review"

2. **Parliament Session Created**
   - Session assigned to appropriate committee
   - Quorum set based on risk level
   - Hunter alerts attached if relevant

3. **Grace Auto-Votes**
   - Analyzes using reflection, causal, Hunter, verification
   - Casts vote with confidence score
   - Provides reasoning

4. **Human Members Vote**
   - Notified of new session
   - Review details and Hunter alerts
   - Cast votes via CLI or UI

5. **Quorum Reached**
   - Decision calculated automatically
   - Action proceeds if approved
   - Action cancelled if rejected

6. **Audit Trail**
   - All votes logged immutably
   - Verification envelopes created
   - Audit log entries preserved

## Example Scenarios

### Scenario 1: Security Action (High Risk)

```python
# Dangerous command detected
session = await parliament_engine.create_session(
    policy_name="dangerous_command_policy",
    action_type="execute",
    action_payload={"command": "rm -rf /"},
    actor="suspicious_user",
    category="security",
    resource="filesystem",
    committee="security",
    quorum_required=4,  # High quorum for critical
    approval_threshold=0.75,  # 75% approval needed
    hunter_alerts=[
        {"severity": "critical", "rule_name": "Dangerous filesystem operation"}
    ],
    risk_level="critical"
)

# Grace auto-rejects due to critical alert
# Result: Rejected (95% confidence)
```

### Scenario 2: Deployment (Medium Risk)

```python
# Production deployment
session = await parliament_engine.create_session(
    policy_name="production_deployment",
    action_type="deploy",
    action_payload={"service": "api", "version": "v2.0"},
    actor="admin",
    category="execution",
    resource="production",
    committee="execution",
    quorum_required=3,
    approval_threshold=0.66,  # 2/3 approval
    risk_level="medium"
)

# Grace analyzes past deployments
# If high success rate: Approves
# If low success rate: Rejects
# Members vote based on testing
```

### Scenario 3: Knowledge Ingestion (Low Risk)

```python
# Learn from new source
session = await parliament_engine.create_session(
    policy_name="trusted_source_learning",
    action_type="ingest",
    action_payload={"source": "documentation.com", "type": "api_docs"},
    actor="admin",
    category="knowledge",
    resource="knowledge_base",
    committee="knowledge",
    quorum_required=2,
    approval_threshold=0.5,
    risk_level="low"
)

# Grace checks verification history
# If trusted source: Approves
# Quick approval with low quorum
```

## Monitoring & Maintenance

```bash
# Check parliament health
grace parliament stats

# Monitor pending sessions
grace parliament sessions --status voting

# Grace auto-voting
grace parliament monitor --auto-vote

# Review member activity
grace parliament members
```

## Troubleshooting

**Sessions not appearing?**
- Check status filter
- Verify committee membership
- Check database: `select * from governance_sessions;`

**Grace not voting?**
- Ensure seeded: `python backend/seed_parliament.py`
- Check registration: `grace parliament members`
- Look for grace_parliament in member list

**Quorum not reached?**
- Add more committee members
- Lower quorum for low-risk actions
- Increase session expiration time

**Need to override?**
- Admin can force-approve via governance
- Or add "override" member with high vote_weight

## Next Steps

- [ ] Add email/Slack notifications for critical votes
- [ ] Create frontend UI (ParliamentDashboard.svelte)
- [ ] WebSocket real-time updates
- [ ] Vote delegation/proxy system
- [ ] Advanced analytics dashboard
- [ ] Appeal/override mechanisms

## Documentation

- Full docs: `PARLIAMENT_SYSTEM.md`
- API reference: http://localhost:8000/docs#/parliament
- Tests: `tests/test_parliament.py`
- Models: `backend/parliament_models.py`
- Engine: `backend/parliament_engine.py`
- Grace agent: `backend/grace_parliament_agent.py`
