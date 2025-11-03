# Parliament & Quorum Governance System

## Overview

The Parliament system is GRACE's distributed governance mechanism for multi-agent voting and quorum-based consensus. It enables democratic decision-making for critical actions, with Grace agents as autonomous voting members.

## Architecture

### Core Components

1. **Parliament Engine** (`backend/parliament_engine.py`)
   - Manages voting sessions and members
   - Enforces quorum rules
   - Calculates consensus outcomes
   - Integrates with verification and audit systems

2. **Grace Voting Agent** (`backend/grace_parliament_agent.py`)
   - Autonomous parliament member
   - Analyzes sessions using reflection, causal reasoning, Hunter alerts
   - Casts automated votes with confidence scoring
   - Monitors pending sessions

3. **Governance Integration** (`backend/governance.py`)
   - Routes policy reviews to Parliament
   - Creates voting sessions for "review" actions
   - Maps categories to committees
   - Determines quorum based on risk level

4. **API Routes** (`backend/routes/parliament_api.py`)
   - RESTful endpoints for members, sessions, committees
   - Vote casting and status checking
   - Parliament statistics

5. **CLI Commands** (`cli/commands/parliament_command.py`)
   - Interactive parliament management
   - Session monitoring and voting
   - Member and committee administration

## Quorum Mechanics

### Voting Process

1. **Session Creation**
   - Policy triggers "review" action
   - Governance creates Parliament session
   - Session assigned to committee
   - Quorum requirement set based on risk level

2. **Voting Phase**
   - Committee members notified
   - Each member casts one vote: approve, reject, abstain
   - Votes weighted by member's `vote_weight`
   - Grace agents auto-vote using AI analysis

3. **Decision Calculation**
   - Quorum reached when `total_votes >= quorum_required`
   - Approval rate = `votes_approve / (votes_approve + votes_reject)`
   - Approved if `approval_rate >= approval_threshold`
   - Rejected if below threshold
   - Tie if all abstain

4. **Outcome**
   - Approved: Action proceeds
   - Rejected: Action cancelled
   - Expired: Session timeout without quorum

### Risk-Based Quorum

| Risk Level | Quorum Required | Typical Committee |
|-----------|----------------|-------------------|
| Low       | 2 votes        | General           |
| Medium    | 3 votes        | Execution, Knowledge |
| High      | 4 votes        | Security          |
| Critical  | 5 votes        | Security, Meta    |

## Committee Structure

### Default Committees

1. **Security Committee**
   - Handles: Security, access control, authentication
   - Members: grace_hunter, grace_reflection, admin
   - Quorum: 3, Threshold: 60%
   - Auto-assigns: high/critical risk security actions

2. **Execution Committee**
   - Handles: Code execution, deployments
   - Members: grace_reflection, grace_meta, admin
   - Quorum: 3, Threshold: 50%
   - Auto-assigns: execution category

3. **Knowledge Committee**
   - Handles: Learning, knowledge ingestion
   - Members: grace_reflection, grace_causal, admin
   - Quorum: 2, Threshold: 50%
   - Auto-assigns: knowledge category

4. **Meta Committee**
   - Handles: Meta-level decisions, optimization
   - Members: grace_meta, grace_causal, admin
   - Quorum: 3, Threshold: 66%
   - Auto-assigns: meta category

5. **General Committee**
   - Handles: Uncategorized actions
   - Members: All members
   - Quorum: 3, Threshold: 50%
   - Default fallback

## Voting Workflow

### Manual Voting (Human)

```bash
# List active sessions
grace parliament sessions --status voting

# View session details
grace parliament session <session_id>

# Cast your vote
grace parliament vote <session_id> --approve -m "Looks safe to me"
grace parliament vote <session_id> --reject -m "Too risky"
grace parliament vote <session_id> --abstain
```

### Automated Voting (Grace)

Grace analyzes sessions using:

1. **Hunter Alerts** → Security votes
   - Critical alerts → Reject (95% confidence)
   - High alerts → Reject (80% confidence)

2. **Verification History** → Trust votes
   - >90% success rate → Approve bias (+10% confidence)
   - <50% success rate → Reject (70% confidence)

3. **Causal Reasoning** → Prediction votes
   - >80% predicted success → Approve (+15% confidence)
   - <30% predicted success → Reject (75% confidence)

4. **Reflection** → Past lessons
   - Positive lessons → Approve bias (+10% confidence)
   - Negative lessons → Reject bias (-10% confidence)

```python
# Grace auto-vote on session
from backend.grace_parliament_agent import grace_voting_agent
result = await grace_voting_agent.cast_automated_vote(session_id)

# Grace monitor all pending sessions
result = await grace_voting_agent.monitor_sessions(auto_vote=True)
```

### API Voting

```bash
POST /api/parliament/sessions/{session_id}/vote
{
  "vote": "approve",
  "reason": "Action aligns with security policy",
  "automated": false,
  "confidence": null
}
```

## Grace Agent Integration

### Grace as Voting Member

Grace agents are registered as parliament members with specialized expertise:

| Agent | Type | Committees | Vote Weight | Expertise |
|-------|------|-----------|-------------|-----------|
| grace_reflection | grace_reflection | execution, knowledge, meta | 1.0 | Reflection, learning |
| grace_hunter | grace_hunter | security | 1.5 | Security expertise |
| grace_meta | grace_meta | meta, execution | 1.0 | Meta-loop optimization |
| grace_causal | grace_causal | execution, knowledge, meta | 1.0 | Causal reasoning |
| grace_parliament | grace_agent | all | 1.0 | General AI voting |

### Auto-Registration

```python
from backend.grace_parliament_agent import grace_voting_agent

# Automatically registers on first use
await grace_voting_agent.register()

# Analyze and vote
analysis = await grace_voting_agent.analyze_session(session)
vote_result = await grace_voting_agent.cast_automated_vote(session_id)
```

## API Reference

### Members

- `POST /api/parliament/members` - Create member
- `GET /api/parliament/members` - List members
- `GET /api/parliament/members/{member_id}` - Get member details

### Sessions

- `POST /api/parliament/sessions` - Create voting session
- `GET /api/parliament/sessions` - List sessions (filterable)
- `GET /api/parliament/sessions/{session_id}` - Get session details
- `POST /api/parliament/sessions/{session_id}/vote` - Cast vote
- `GET /api/parliament/sessions/{session_id}/status` - Get vote status

### Committees

- `POST /api/parliament/committees` - Create committee
- `GET /api/parliament/committees` - List committees
- `GET /api/parliament/committees/{name}` - Get committee details

### Statistics

- `GET /api/parliament/stats` - Parliament-wide statistics
- `GET /api/parliament/stats/member/{member_id}` - Member statistics

## CLI Commands

```bash
# Sessions
grace parliament sessions                    # List active sessions
grace parliament sessions --status approved  # Filter by status
grace parliament session <id>                # View details

# Voting
grace parliament vote <id> --approve -m "reason"
grace parliament vote <id> --reject -m "reason"
grace parliament vote <id> --abstain

# Members
grace parliament members                     # List all members

# Statistics
grace parliament stats                       # Overall statistics

# Monitoring (Grace agent)
grace parliament monitor                     # Monitor without voting
grace parliament monitor --auto-vote         # Monitor and auto-vote
```

## Database Schema

### GovernanceMember
- Member details (ID, type, display name)
- Permissions (role, committees)
- Voting power (vote_weight)
- Statistics (total_votes, votes_approved, etc.)

### GovernanceSession
- Session details (policy, action, payload)
- Context (category, resource, actor, committee)
- Quorum (required, threshold)
- Status (pending, voting, approved, rejected, expired)
- Vote tallies (approve, reject, abstain)
- Security (hunter_alerts, risk_level)

### GovernanceVote
- Individual vote (member, session, vote)
- Reasoning (reason, automated, confidence)
- Verification (signature, verification_status)

### CommitteeDefinition
- Committee details (name, description)
- Membership (member_ids, min/max)
- Quorum settings (default_quorum, default_threshold)
- Auto-assignment rules

## Setup & Initialization

### 1. Run Database Migration

```bash
cd grace_rebuild
python backend/seed_parliament.py
```

This creates:
- Default committees (security, execution, knowledge, meta, general)
- Grace agent members
- Admin user as member

### 2. Register Grace Agents

Grace agents auto-register on first use, or manually:

```bash
python -c "
import asyncio
from backend.grace_parliament_agent import grace_voting_agent
asyncio.run(grace_voting_agent.register())
"
```

### 3. Enable Parliament in Governance

Parliament integration is enabled by default in `governance.py`:

```python
governance_engine.parliament_enabled = True  # default
```

## Testing

Run parliament tests:

```bash
cd grace_rebuild
python tests/test_parliament.py
```

Tests cover:
- Member creation
- Session creation
- Voting with quorum
- Decision outcomes (approve/reject/tie/expire)
- Grace automated voting
- Governance integration

## Frontend UI (Optional)

Frontend components planned in `grace-frontend/src/components/ParliamentDashboard`:

- **ActiveSessions** - List of voting sessions
- **SessionDetails** - Detailed session view
- **VotingInterface** - Vote buttons (approve/reject/abstain)
- **MemberDirectory** - Parliament members
- **VoteHistory** - Historical voting records
- **Statistics** - Charts and metrics

Real-time updates via WebSocket events.

## Security & Audit

All parliament actions are:

1. **Logged** to immutable audit log
2. **Verified** with signature checks
3. **Timestamped** with created_at/decided_at
4. **Traceable** via audit_log_id
5. **Integrated** with verification envelopes

## Best Practices

1. **Set appropriate quorum** based on risk level
2. **Use committees** to route to domain experts
3. **Provide vote reasoning** for transparency
4. **Monitor Grace votes** for quality assurance
5. **Review expired sessions** to identify bottlenecks
6. **Adjust thresholds** based on approval rates
7. **Audit critical decisions** regularly

## Troubleshooting

### Session not appearing in list
- Check status filter (may be "approved" or "expired")
- Verify committee membership

### Grace not voting
- Ensure Grace is registered: `grace parliament members`
- Check session committee membership
- Review Grace vote logs

### Quorum not reached
- Increase session expiration time
- Add more committee members
- Lower quorum requirement for low-risk actions

### All votes abstain (tie)
- Check session details for ambiguity
- Provide more context in action_payload
- Add Hunter alerts or risk assessment

## Roadmap

- [ ] Frontend UI components
- [ ] WebSocket real-time voting updates
- [ ] Email/Slack notifications for critical votes
- [ ] Delegation and proxy voting
- [ ] Vote delegation to trusted members
- [ ] Committee membership auto-assignment
- [ ] Advanced vote analytics and trends
- [ ] Appeal/override mechanisms for rejected actions

## References

- **Parliament Engine**: `backend/parliament_engine.py`
- **Grace Agent**: `backend/grace_parliament_agent.py`
- **API Routes**: `backend/routes/parliament_api.py`
- **CLI Commands**: `cli/commands/parliament_command.py`
- **Tests**: `tests/test_parliament.py`
- **Seed Script**: `backend/seed_parliament.py`
- **Models**: `backend/parliament_models.py`
