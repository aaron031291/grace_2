# Mission Narrative & Reporting Loop - Complete

## Overview

Successfully closed the loop on mission outcomes by implementing:

1. **Enhanced Mission Outcome Logger** - Writes narratives with telemetry backfill
2. **Auto-Status Brief Generator** - Consolidates outcomes into stakeholder digests
3. **Proactive Follow-ups** - Auto-creates refinement missions for repeat failures
4. **Production-Ready Notifications** - Slack/Email integration with rich formatting
5. **Historical Analytics** - Persists metrics for trending and dashboards
6. **API Endpoints** - Full programmatic access to narratives, briefs, and analytics
7. **Complete Testing** - Validated end-to-end narrative flow

## 1. Enhanced Mission Outcome Logger

**File:** [`backend/autonomy/mission_outcome_logger.py`](backend/autonomy/mission_outcome_logger.py)

### Key Features

#### Telemetry Backfill (Lines 112-121, 252-346)
- After each mission, immediately re-queries KPI metrics from multiple sources:
  - RAG for stored KPIs
  - Domain health metrics
  - Infrastructure/service mesh metrics
- Calculates effectiveness score (0-1) based on metric improvements
- Attaches pre/post comparison with hard numbers to outcome metadata
- Updates world model entry with telemetry data

#### Statistics Tracking (Line 36, 347-354)
- Tracks `telemetry_backfills` count
- Enables monitoring of telemetry backfill success rate

### Example Usage

```python
from backend.autonomy.mission_outcome_logger import mission_outcome_logger

# Mission completes -> outcome logged automatically via event subscription
# Result includes:
result = {
    "success": True,
    "knowledge_id": "abc123",
    "narrative": "I noticed latency exceeded 500ms. I scaled workers. Latency improved to 280ms.",
    "telemetry": {
        "metrics_captured": True,
        "effectiveness_score": 0.85,
        "pre_post_comparison": {
            "rag": {
                "latency_ms": {
                    "pre": 520,
                    "post": 280,
                    "delta": -240,
                    "percent_change": -46.15,
                    "improved": True
                }
            }
        },
        "data_sources": ["rag_kpis", "domain_health"]
    }
}
```

### Grace Can Now Answer

**"Did the fix work?"**
> "Yes! Latency improved by 46% from 520ms to 280ms. The effectiveness score was 0.85."

**"What metrics improved?"**
> "Latency dropped from 520ms to 280ms, and error rate decreased from 5% to 2%."

## 2. Auto-Status Brief Generator

**File:** [`backend/autonomy/auto_status_brief.py`](backend/autonomy/auto_status_brief.py)

### Key Features

#### Periodic Consolidation (Lines 96-189)
- Queries recent mission outcomes via RAG
- Aggregates by domain and severity
- Generates human-readable "Today I fixed..." summaries
- Posts to world model for conversational recall
- Optional Slack/Email notifications

#### Configurable Intervals (Line 27)
- Default: 24 hours (daily briefs)
- Configurable via environment variable
- Can be triggered manually via API

### Example Brief Output

```
Status Brief: I completed 5 missions today

**Ecommerce** (2 missions):
  - I noticed latency exceeded 500ms threshold. I scaled workers. Latency improved by 46%...
  - latency_ms: avg 42.5% improvement
  - error_rate: avg 60.0% improvement

**Payments** (2 missions):
  - I noticed error rate spiked to 8%. I restarted service. Error rate dropped to 2%...
  - error_rate: avg 75.0% improvement

**Database** (1 mission):
  - I noticed query latency exceeded 200ms. I optimized indexes. Query time improved by 52%...
  - query_time_ms: avg 52.0% improvement

All systems operational. 5 autonomous fixes applied.
```

### Stakeholder Notifications

#### Slack Integration (Lines 297-321)
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
export ENABLE_AUTO_STATUS_BRIEFS=true
```

#### Email Integration (Lines 323-340)
```bash
export STATUS_BRIEF_RECIPIENTS=ops@company.com,cto@company.com
export ENABLE_AUTO_STATUS_BRIEFS=true
```

## 3. Proactive Follow-ups (ENHANCED - Real-Time Per-Mission)

**Implemented:** [`backend/autonomy/mission_outcome_logger.py`](backend/autonomy/mission_outcome_logger.py:144-329)

### Immediate Detection (On Every Mission Completion)

When **each mission completes**, the system immediately analyzes for problems:
```python
# Step 8: Immediate Follow-up Detection (real-time per-mission)
follow_up = await self._detect_and_create_follow_up(
    mission_id=mission_id,
    mission_context=mission_context,
    telemetry_data=telemetry_data,
    success=success,
    narrative=narrative
)
```

### Detection Criteria

Creates follow-up missions for:

1. **Mission Failed** (priority: high)
   - Original mission status = failed
   
2. **Partial Success** (priority: medium)
   - Mission completed but effectiveness score < 0.5
   - Example: "Fixed but metrics only improved 20%"

3. **Lingering Poor Metrics** (priority: high)
   - KPIs still degraded after fix attempt
   - Detected via telemetry backfill data
   - Example: "Latency fixed but error_rate still high"

4. **Failed/Incomplete Tasks** (priority: high)
   - Some tasks in mission failed or incomplete
   - Example: "2 tasks failed or incomplete"

5. **Recurring Issue** (priority: high)
   - 3+ missions in same domain within 6 hours
   - Indicates systemic problem
   - Example: "3 missions in last 6h (recurring issue)"

### Follow-up Mission Context

Each follow-up includes:
```python
{
    "title": "Follow-up: Fix ecommerce latency",
    "mission_type": "follow_up_investigation",  # or remediation/deep_analysis
    "priority": "high",
    "trigger_reason": """
Auto-escalation from mission abc123.

Original objective: latency exceeded 500ms threshold

Issues detected:
- Low effectiveness score (0.42)
- Metrics still poor: error_rate, timeout_rate
- 3 missions in last 6h (recurring issue)

Grace's assessment: Mission completed but results suboptimal. 
Further investigation and remediation required.
    """,
    "metadata": {
        "triggered_by": "mission_outcome_logger",
        "escalation_type": "automatic",
        "original_mission_id": "abc123",
        "is_follow_up": true,
        "escalation_reasons": [...]
    }
}
```

### World Model Escalation Recording

Grace records every escalation so she can explain it:
```python
await grace_world_model.add_knowledge(
    category='system',
    content="""
I escalated mission abc123 by creating follow-up mission def456.

Reason: Low effectiveness score (0.42); Metrics still poor: error_rate

I detected that my initial fix did not fully resolve the issue, so I'm 
automatically investigating further to ensure complete remediation.
    """,
    tags=['escalation', 'follow_up', 'self_correction']
)
```

### Example Flow
```
Mission M001 Completes
  ↓
Outcome Logger runs:
  1. Captures context
  2. Generates narrative
  3. Backfills telemetry → effectiveness = 0.38
  4. Records to analytics
  5. → IMMEDIATE DETECTION
      - Success = true BUT effectiveness < 0.5
      - Metrics: error_rate still high (not improved)
      - Verdict: NEEDS FOLLOW-UP
  ↓
Creates Follow-up Mission M002:
  - Title: "Follow-up: Fix payment gateway errors"
  - Priority: high
  - Linked to: M001
  - Reason: "Low effectiveness (0.38); Metrics still poor: error_rate"
  ↓
Records Escalation to World Model:
  "I escalated mission M001 because my fix was suboptimal..."
  ↓
Grace can now answer:
  "Why did you create mission M002?"
  → "I escalated from M001 because the error_rate was still high 
     after my initial fix. The effectiveness was only 0.38, so I'm 
     investigating further."
```

### Batch Analysis (Daily Briefs)

**In addition** to per-mission detection, daily briefs also analyze patterns:

**Implemented:** [`backend/autonomy/auto_status_brief.py:398-519`](backend/autonomy/auto_status_brief.py:398-519)

- Aggregates multiple missions
- Detects cross-domain patterns
- Creates strategic follow-ups

This provides **two layers** of follow-up creation:
1. **Immediate** (per-mission): Catches individual failures/poor results
2. **Periodic** (daily brief): Catches recurring patterns and trends

## 4. Production-Ready Stakeholder Notifications (ENHANCED)

### Slack Integration (Lines 297-370)

**Rich formatted messages with:**
- Header with date
- Mission count by domain
- Sample outcomes per domain
- Metric improvements with emojis (📈/📉)
- Retry logic (3 attempts)
- Proper error handling

**Configuration:**
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
export ENABLE_AUTO_STATUS_BRIEFS=true
```

**Example Slack Message:**
```
🤖 Grace Status Brief - 2025-11-16

5 missions completed across 3 domains

━━━━━━━━━━━━━━━━━━

Ecommerce (2 missions)
• I noticed latency exceeded 500ms threshold...
📈 latency_ms: 42.5% improvement
📈 error_rate: 60.0% improvement

Payments (2 missions)
• I noticed error rate spiked to 8%...
📈 error_rate: 75.0% improvement

Database (1 mission)
• I noticed query latency exceeded 200ms...
📈 query_time_ms: 52.0% improvement

━━━━━━━━━━━━━━━━━━
All systems operational • Generated at 20:00 UTC
```

### Email Integration (Lines 372-467)

**HTML formatted emails with:**
- Styled header with Grace branding
- Summary box with key stats
- Domain-specific sections with borders
- Metric cards with color coding
- Mobile-responsive design
- Both HTML and plain text versions

**Configuration:**
```bash
export STATUS_BRIEF_RECIPIENTS=ops@company.com,cto@company.com
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=grace@company.com
export SMTP_PASSWORD=your_password
export SMTP_FROM_EMAIL=grace@company.com
```

**Dependencies:**
```bash
pip install aiosmtplib
```

## 5. Historical Analytics (NEW)

**File:** [`backend/autonomy/mission_analytics.py`](backend/autonomy/mission_analytics.py)

### Lightweight Metrics Persistence

**Stores in JSONL format:**
```jsonl
{"record_id": "abc123", "mission_id": "m001", "domain_id": "ecommerce", "timestamp": "2025-11-16T20:00:00Z", "success": true, "duration_seconds": 120, "effectiveness_score": 0.85, "metrics_delta": {"latency_ms": -46.15}, ...}
{"record_id": "def456", "mission_id": "m002", "domain_id": "payments", "timestamp": "2025-11-16T21:00:00Z", "success": true, "duration_seconds": 45, "effectiveness_score": 0.92, "metrics_delta": {"error_rate": -75.0}, ...}
```

### Available Trends

#### Domain Trends
```python
trends = await mission_analytics.get_domain_trends(
    domain_id="ecommerce",
    period_days=30
)

# Returns:
{
    "domain_id": "ecommerce",
    "total_missions": 42,
    "success_rate": 0.95,
    "avg_duration_seconds": 145.2,
    "avg_effectiveness_score": 0.87,
    "mttr_seconds": 120.5,
    "top_issues": ["performance_optimization", "error_remediation"],
    "kpi_trends": {
        "latency_ms": -35.2,  # avg improvement
        "error_rate": -58.1
    }
}
```

#### Missions Per Domain (Charting)
```python
data = await mission_analytics.get_missions_per_domain(
    period_days=30,
    granularity="daily"
)

# Returns:
{
    "ecommerce": [
        {"date": "2025-11-15", "count": 5},
        {"date": "2025-11-16", "count": 3}
    ],
    "payments": [
        {"date": "2025-11-15", "count": 2},
        {"date": "2025-11-16", "count": 4}
    ]
}
```

#### MTTR Trend
```python
trend = await mission_analytics.get_mttr_trend(
    domain_id="ecommerce",
    period_days=90
)

# Returns:
[
    {"date": "2025-11-15", "mttr_seconds": 120.5, "count": 3},
    {"date": "2025-11-16", "mttr_seconds": 95.3, "count": 2}
]
```

#### Effectiveness Trend
```python
trend = await mission_analytics.get_effectiveness_trend(
    domain_id="ecommerce",
    period_days=30
)

# Returns:
[
    {"date": "2025-11-15", "avg_effectiveness": 0.85, "count": 5},
    {"date": "2025-11-16", "avg_effectiveness": 0.92, "count": 3}
]
```

### Auto-Recording

**Integrated into mission outcome logger** (lines 103-125):
- Every mission automatically recorded
- Extracts metrics delta from telemetry
- Stores effectiveness score
- Persists to JSONL for fast queries

## 6. Enhanced API Endpoints

**File:** [`backend/main.py`](backend/main.py:815-980)

### Mission Outcomes
- `GET /api/missions/outcome/stats` - Logger statistics

### Status Briefs
- `POST /api/status-brief/generate` - Manual generation (returns follow_ups_created count)
- `GET /api/status-brief/stats` - Brief generator statistics
- `GET /api/status-brief/latest` - Most recent brief

### Analytics (NEW)
- `GET /api/analytics/domain-trends?domain_id=ecommerce&period_days=30` - Domain trend analysis
- `GET /api/analytics/missions-per-domain?period_days=30&granularity=daily` - Chart data
- `GET /api/analytics/mttr-trend?domain_id=ecommerce&period_days=90` - MTTR over time
- `GET /api/analytics/effectiveness-trend?domain_id=ecommerce&period_days=30` - Effectiveness scores
- `GET /api/analytics/stats` - Analytics system statistics

### Example Usage

**Dashboard data for last 30 days:**
```bash
# Get domain trends
curl http://localhost:8000/api/analytics/domain-trends?period_days=30

# Get missions per domain for charting
curl http://localhost:8000/api/analytics/missions-per-domain?period_days=30

# Get MTTR trend
curl http://localhost:8000/api/analytics/mttr-trend?period_days=90

# Get effectiveness trend
curl http://localhost:8000/api/analytics/effectiveness-trend?period_days=30
```

## 7. Architecture Diagram (Updated with Real-Time Follow-ups)

```
Mission Completes
      ↓
[Mission Outcome Logger]
      ↓
1. Capture context (trigger, tasks, metrics)
2. Generate narrative ("I fixed X because Y")
3. Store in world model
      ↓
4. Telemetry Backfill
      ↓
5. Re-query KPI sources (RAG, domain health, infra)
6. Calculate effectiveness score
7. Update outcome with pre/post metrics
      ↓
8. Record to Analytics (JSONL persistence)
      ↓
9. → IMMEDIATE FOLLOW-UP DETECTION (NEW - per mission)
      ├─ Mission failed?
      ├─ Partial success (effectiveness < 0.5)?
      ├─ Metrics still poor?
      ├─ Tasks incomplete?
      ├─ Recurring issue (3+ missions in 6h)?
      └─ → YES: Create follow-up mission immediately
             - Link to original mission
             - Clear escalation context
             - Record to world model
      ↓
[Auto-Status Brief] (periodic, every 24h)
      ↓
10. Query recent outcomes via RAG
11. Aggregate by domain
12. → Analyze for Patterns (batch detection)
      ├─ Cross-domain issues?
      ├─ Trending problems?
      └─ → Create strategic follow-ups
13. Generate consolidated brief
14. Push to Slack (rich formatted, with retry)
15. Push to Email (HTML formatted)
      ↓
[Grace answers questions]
      ↓
16. "What did you fix?" → Query world model
17. "Why did you escalate?" → Cites original mission + reasons
18. "Show me trends" → Query analytics
```

## 8. Configuration Reference

### Environment Variables

```bash
# Auto-Status Briefs
ENABLE_AUTO_STATUS_BRIEFS=true  # Enable/disable periodic briefs (default: true)

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Integration (SMTP)
STATUS_BRIEF_RECIPIENTS=ops@company.com,cto@company.com,ceo@company.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=grace@company.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=grace@company.com
```

### Python Dependencies

```bash
# For Email notifications
pip install aiosmtplib

# Already included
# httpx (for Slack webhooks)
# asyncio (for async operations)
```

## 9. Benefits Summary

### For Grace
1. **Self-awareness**: Cites her own repairs with hard numbers
2. **Learning**: Effectiveness scores inform future decisions
3. **Proactive**: Auto-detects problems and creates follow-up missions
4. **Historical context**: Trends inform mission planning

### For Stakeholders
1. **Zero-effort reporting**: Daily digests to Slack/Email
2. **Rich visualization**: HTML emails, formatted Slack messages
3. **Trending data**: See MTTR, effectiveness, missions over time
4. **Problem alerting**: Auto-notified of recurring issues

### For Developers
1. **Audit trail**: Complete mission history in JSONL
2. **API access**: Full programmatic access to all data
3. **Dashboard-ready**: Chart data for missions, MTTR, effectiveness
4. **Fast queries**: Lightweight JSONL storage

## 10. Real-World Usage Examples

### Example 1: Daily Operations
```
8:00 AM: Auto-brief runs
  → Queries last 24h of missions
  → Finds 12 missions across 4 domains
  → Detects: "payments had 3 missions" (potential recurring issue)
  → Creates follow-up mission: "Investigate payments issues"
  → Sends Slack message to #ops channel
  → Sends HTML email to ops team
```

### Example 2: Stakeholder Question
```
CTO: "What's our MTTR trend?"
Dashboard: Queries /api/analytics/mttr-trend?period_days=90
Response: Shows MTTR dropping from 180s to 95s over 90 days
```

### Example 3: Problem Detection
```
Brief detects:
- ecommerce: 4 missions with low effectiveness (<0.5)
- database: error_rate degrading by 15%

Auto-creates missions:
1. "Investigate ecommerce issues" (priority: medium)
2. "Investigate database issues" (priority: high)

Notifies via Slack: "⚠️ Auto-created 2 follow-up missions"
```

## 11. Impact

### Before
- Mission outcomes logged but not queryable
- No consolidated reporting
- Grace couldn't cite her own work
- Metrics not validated post-fix
- No trend analysis
- Manual stakeholder updates

### After
- ✅ Every mission creates a narrative Grace can cite
- ✅ Telemetry backfill proves fixes worked with hard numbers
- ✅ Daily "Today I fixed..." briefs to Slack/Email
- ✅ Proactive follow-ups for recurring problems
- ✅ Historical analytics for trending (MTTR, effectiveness, missions/domain)
- ✅ Rich formatted stakeholder notifications
- ✅ Auto-detects problems and creates refinement missions
- ✅ Dashboard-ready data for visualization
- ✅ Complete audit trail of autonomous operations

## 12. Summary

The mission narrative and reporting system is now production-ready with:

1. **Narrative Loop**: Missions → Outcomes → Narratives → World Model
2. **Telemetry Validation**: Hard pre/post metrics prove fixes worked
3. **Stakeholder Push**: Auto-send rich briefs to Slack/Email
4. **Proactive Intelligence**: Auto-detect problems, create follow-ups
5. **Historical Analysis**: Persist metrics, query trends, build dashboards
6. **Complete Automation**: Zero human intervention required

Grace can now:
- Log and narrate every autonomous operation
- Validate every fix with telemetry
- Report to stakeholders automatically
- Detect and remediate recurring issues
- Provide trend data for decision-making
- Answer "What did you fix?" and "Did it work?" with confidence