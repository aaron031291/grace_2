# AI Consulting Automation System

Complete business automation for AI consulting with client pipeline, ML-driven lead scoring, automated proposal generation, and Grace Architect delivery.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   CLIENT ACQUISITION                         │
├─────────────────────────────────────────────────────────────┤
│  Upwork │ Website │ Referrals │ LinkedIn │ Cold Outreach   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               LEAD QUALIFICATION (ML)                        │
│  • Feature extraction                                        │
│  • ML scoring (0-100)                                        │
│  • Auto-qualify >70                                          │
│  • Recommendation engine                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  SALES PIPELINE                              │
│  LEAD → QUALIFIED → PROPOSAL → NEGOTIATION → CONTRACT       │
│  → ACTIVE → DELIVERED → PAID → REPEAT                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            PROPOSAL GENERATION (Grace)                       │
│  • Auto-generate proposals                                   │
│  • Parse deliverables                                        │
│  • Estimate timeline                                         │
│  • Calculate pricing                                         │
│  • Parliament approval >$5K                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          PROJECT DELIVERY (Grace Architect)                  │
│  • Automated code generation                                 │
│  • Build systems                                             │
│  • Deploy solutions                                          │
│  • Track progress                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PAYMENT & SATISFACTION                          │
│  • Invoice generation                                        │
│  • Stripe integration                                        │
│  • NPS tracking                                              │
│  • Client satisfaction scoring                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. AI Consulting Engine (`ai_consulting_engine.py`)

**Core Methods:**
- `qualify_lead(client_data)` - ML classifier scores leads 0-100
- `generate_proposal(requirements)` - Auto-generate consulting proposals
- `create_project_plan(proposal)` - Break down into deliverables
- `deliver_project(spec)` - Use Grace Architect to build
- `collect_payment(project_id)` - Stripe integration point
- `track_client_satisfaction(project_id)` - NPS scoring

**Features:**
- Governance-verified operations
- Hunter scanning on all client data
- Parliament approval for projects >$5K
- Immutable audit logging

### 2. Client Pipeline (`client_pipeline.py`)

**Pipeline Stages:**
1. **LEAD** - Captured from source
2. **QUALIFIED** - ML score >70
3. **PROPOSAL** - Auto-generated proposal sent
4. **NEGOTIATION** - Grace handles via chat, you approve
5. **CONTRACT** - Auto-generated, requires signature
6. **ACTIVE** - Project in progress
7. **DELIVERED** - Completed, awaiting payment
8. **PAID** - Revenue received
9. **REPEAT** - Upsell opportunities

**Core Methods:**
- `capture_lead(source, data)` - Store new lead
- `qualify_lead(lead_id)` - ML scoring
- `move_to_stage(lead_id, new_stage)` - Pipeline progression
- `get_pipeline_metrics()` - Conversion rates per stage
- `predict_close_rate(lead_id)` - ML prediction
- `suggest_next_action(lead_id)` - Grace recommends action

**Features:**
- WebSocket real-time updates
- ML-based close predictions
- Automated action suggestions
- Full funnel analytics

### 3. Database Models (`models.py`)

**Client** - Company/person entity
- Contact info, industry, budget
- Lifetime value tracking
- Satisfaction scores

**Lead** - Sales opportunity
- ML score, stage, probability
- Value estimation
- Next action tracking

**Project** - Active engagement
- Scope, deliverables, timeline
- Budget vs actual cost
- Grace Architect integration
- NPS feedback

**Interaction** - Client communication
- Type, channel, content
- Sentiment analysis
- Automated vs human-generated

**Invoice** - Payment tracking
- Status, amounts, dates
- Stripe integration fields
- Transaction tracking

### 4. API Endpoints (`api.py`)

```python
POST   /api/business/leads                    # Capture lead
POST   /api/business/leads/{id}/qualify       # Qualify lead
POST   /api/business/leads/{id}/stage         # Move stage
GET    /api/business/leads/{id}/predict       # Predict close
GET    /api/business/leads/{id}/next-action   # Get recommendation
POST   /api/business/proposals/generate       # Generate proposal
POST   /api/business/projects/deliver         # Deliver project
POST   /api/business/projects/{id}/payment    # Collect payment
GET    /api/business/projects/{id}/satisfaction # Track NPS
GET    /api/business/pipeline                 # Pipeline metrics
GET    /api/business/revenue                  # Revenue stats
```

## Usage Examples

### 1. Capture Lead from Upwork

```python
from backend.transcendence.business import ClientPipeline

pipeline = ClientPipeline()

lead = await pipeline.capture_lead(
    source="upwork",
    data={
        "name": "John Doe",
        "email": "john@example.com",
        "company": "Acme Corp",
        "industry": "technology",
        "budget": 15000,
        "requirements": "Need ML consulting for customer churn prediction",
        "timeline": "2 months"
    }
)
# Returns: {"client_id": 1, "lead_id": 1, "stage": "LEAD"}
```

### 2. Qualify Lead with ML

```python
qual = await pipeline.qualify_lead(lead_id=1)
# Returns: {
#   "score": 85,
#   "qualified": True,
#   "stage": "QUALIFIED",
#   "recommendation": "HIGH_PRIORITY - Auto-approve and fast-track"
# }
```

### 3. Generate Proposal

```python
from backend.transcendence.business import AIConsultingEngine

engine = AIConsultingEngine()
await engine.initialize()

proposal = await engine.generate_proposal(
    requirements="Build ML-based fraud detection system",
    client_id=1,
    budget=20000
)

# Auto-generates:
# - Executive summary
# - Scope of work
# - Deliverables breakdown
# - Timeline estimation
# - Pricing calculation
```

### 4. Deliver Project with Grace Architect

```python
result = await engine.deliver_project(
    project_id=1,
    spec={
        "description": "ML fraud detection system",
        "requirements": ["data ingestion", "model training", "API deployment"],
        "tech_stack": ["python", "fastapi", "scikit-learn"]
    }
)
# Grace Architect builds the entire system
# Parliament approves if budget >$5K
```

### 5. Track Pipeline Metrics

```python
metrics = await pipeline.get_pipeline_metrics()
# Returns:
# {
#   "total_leads": 150,
#   "converted": 45,
#   "conversion_rate": 30.0,
#   "pipeline_value": 250000,
#   "revenue": 180000,
#   "stage_counts": {...},
#   "funnel_conversion": {...}
# }
```

### 6. Get Grace's Action Recommendation

```python
action = await pipeline.suggest_next_action(lead_id=1)
# Returns:
# {
#   "current_stage": "QUALIFIED",
#   "suggestion": {
#     "action": "Generate and send proposal",
#     "priority": "high",
#     "automated": True,
#     "approval_needed": False
#   },
#   "can_automate": True
# }
```

## ML Features for Lead Scoring

The system extracts these features for ML scoring:

- **has_company** - Business entity vs individual
- **has_budget** - Budget specified
- **budget_range** - Dollar amount category
- **industry** - Technology, finance, healthcare (bonus points)
- **source** - Referral/repeat (high value) vs cold (low value)
- **requirements_length** - Detail level
- **timeline_urgency** - Immediate vs long-term
- **has_previous_projects** - Repeat client bonus

**Scoring Logic:**
- Base: 50 points
- Budget >$10K: +20
- Budget >$5K: +10
- Has company: +10
- Premium industry: +15
- Referral/repeat: +20
- Detailed requirements: +10
- **>70 = Auto-qualified**

## Integration Points

### Governance
All client operations checked against governance policies:
```python
await governance_engine.check_policy(
    action="qualify_lead",
    context={"client": client_data.get("email")}
)
```

### Hunter
All client data scanned for security:
```python
await hunter.scan_data(
    data_type="client_qualification",
    data={"score": score, "features": features}
)
```

### Parliament
Projects >$5K require voting approval:
```python
vote_result = await parliament.create_session(
    title=f"Approve Project Delivery - #{project_id}",
    description=f"Budget: ${project.budget}",
    quorum_percentage=0.6,
    required_committees=["governance", "finance"]
)
```

### Grace Architect
Automated project delivery:
```python
result = await architect.execute_task(
    task_type="build_project",
    task_data=build_spec
)
```

### WebSocket
Real-time pipeline updates:
```python
await ws_manager.broadcast({
    "type": "lead_qualified",
    "lead_id": lead_id,
    "score": score,
    "qualified": qualified
})
```

## Testing

```bash
# Run all business automation tests
pytest tests/test_business_engines.py -v

# Test specific functionality
pytest tests/test_business_engines.py::test_lead_qualification -v
pytest tests/test_business_engines.py::test_proposal_generation -v
pytest tests/test_business_engines.py::test_end_to_end_lead_to_paid -v
```

## API Usage

### Capture Lead via API

```bash
curl -X POST http://localhost:8000/api/business/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@startup.com",
    "company": "Startup Inc",
    "industry": "finance",
    "budget": 12000,
    "requirements": "ML pipeline for risk scoring",
    "source": "website"
  }'
```

### Generate Proposal

```bash
curl -X POST http://localhost:8000/api/business/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "requirements": "Build real-time ML fraud detection",
    "budget": 25000
  }'
```

### Get Pipeline Metrics

```bash
curl http://localhost:8000/api/business/pipeline
```

## Revenue Tracking

The system tracks:
- **Pipeline value** - Sum of all active lead estimates
- **Total revenue** - Completed and paid projects
- **Conversion rate** - % of leads that become paid
- **Average deal size** - Revenue / converted leads
- **Forecasted monthly** - Pipeline value × conversion rate

## Deployment

1. **Initialize Database:**
```python
from backend.models import engine, Base
from backend.transcendence.business.models import Client, Lead, Project, Invoice

async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

2. **Wire into FastAPI:**
```python
from backend.transcendence.business.api import router
app.include_router(router)
```

3. **Start Accepting Leads:**
- Add lead capture forms to website
- Connect Upwork webhooks
- Set up referral tracking
- Configure email integration

## Roadmap

### Phase 1: ✅ Core Automation
- Lead capture and qualification
- Pipeline management
- Proposal generation
- Payment tracking

### Phase 2: 🚧 Advanced ML
- Deep learning lead scoring
- Churn prediction
- Lifetime value estimation
- Optimal pricing models

### Phase 3: 📋 Full Automation
- Chatbot client communication
- Automated contract generation
- Self-service client portal
- Auto-upsell engine

### Phase 4: 💰 Business Empire
- Multi-tenant SaaS
- White-label consulting platform
- AI consulting marketplace
- Franchise model

## License

Part of Grace AI System - Autonomous AI Consulting Platform
