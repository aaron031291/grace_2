# Business Automation System - Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                      LEAD SOURCES                                 │
│  Upwork │ Website │ Referrals │ LinkedIn │ Cold Email            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                  CLIENT PIPELINE (CRM)                            │
│                                                                   │
│  capture_lead(source, data)                                       │
│    ├─> Create Client record                                      │
│    ├─> Create Lead record                                        │
│    ├─> Create Interaction record                                 │
│    ├─> WebSocket broadcast                                       │
│    └─> Audit log                                                 │
│                                                                   │
│  LEAD → QUALIFIED → PROPOSAL → NEGOTIATION → CONTRACT            │
│  → ACTIVE → DELIVERED → PAID → REPEAT                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│              AI CONSULTING ENGINE (ML)                            │
│                                                                   │
│  qualify_lead(client_data)                                        │
│    ├─> Extract features (13 dimensions)                          │
│    ├─> ML scoring (0-100)                                        │
│    ├─> Governance check                                          │
│    ├─> Hunter scan                                               │
│    └─> Auto-qualify if >70                                       │
│                                                                   │
│  generate_proposal(requirements, budget)                          │
│    ├─> Grace Architect generates text                            │
│    ├─> Parse deliverables                                        │
│    ├─> Estimate timeline                                         │
│    ├─> Calculate pricing                                         │
│    └─> Hunter scan output                                        │
│                                                                   │
│  create_project_plan(proposal)                                    │
│    ├─> Create Project record                                     │
│    ├─> Generate milestones                                       │
│    └─> Audit log                                                 │
│                                                                   │
│  deliver_project(project_id, spec)                                │
│    ├─> Parliament vote if >$5K                                   │
│    ├─> Grace Architect builds                                    │
│    ├─> Track progress                                            │
│    └─> Update project status                                     │
│                                                                   │
│  collect_payment(project_id)                                      │
│    ├─> Generate invoice                                          │
│    ├─> Stripe integration                                        │
│    └─> Audit log                                                 │
│                                                                   │
│  track_client_satisfaction(project_id)                            │
│    ├─> NPS scoring                                               │
│    ├─> Category classification                                   │
│    └─> Follow-up recommendations                                 │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                               │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Governance  │  │    Hunter    │  │  Parliament  │          │
│  │   Policies   │  │   Security   │  │    Voting    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Grace     │  │ Verification │  │  WebSocket   │          │
│  │  Architect   │  │    Engine    │  │  Broadcasts  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │  Immutable   │  │   Stripe     │                             │
│  │  Audit Log   │  │   Payment    │                             │
│  └──────────────┘  └──────────────┘                             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DATA LAYER (SQLAlchemy)                        │
│                                                                   │
│  Client ──┬─> Lead ──> Project ──> Invoice                       │
│           │                                                       │
│           └─> Interaction                                         │
│                                                                   │
│  Relationships:                                                   │
│  - Client: 1-to-many Leads, Projects, Interactions               │
│  - Project: 1-to-many Invoices                                   │
│  - Lead: Many-to-1 Client                                        │
└──────────────────────────────────────────────────────────────────┘
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                 │
│                                                                  │
│  FastAPI Router (/api/business/*)                               │
│  ├─ POST /leads                    # Capture lead               │
│  ├─ POST /leads/{id}/qualify       # Qualify with ML            │
│  ├─ POST /leads/{id}/stage         # Move pipeline              │
│  ├─ GET  /leads/{id}/predict       # Predict close              │
│  ├─ GET  /leads/{id}/next-action   # AI suggestion              │
│  ├─ POST /proposals/generate       # Auto-generate              │
│  ├─ POST /projects/deliver         # Grace Architect            │
│  ├─ POST /projects/{id}/payment    # Invoice                    │
│  ├─ GET  /projects/{id}/satisfaction # NPS                      │
│  ├─ GET  /pipeline                 # Metrics                    │
│  └─ GET  /revenue                  # Revenue stats              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
│                                                                  │
│  ┌───────────────────────────┐   ┌───────────────────────────┐ │
│  │  AIConsultingEngine       │   │  ClientPipeline           │ │
│  │                           │   │                           │ │
│  │ • qualify_lead()          │   │ • capture_lead()          │ │
│  │ • generate_proposal()     │   │ • qualify_lead()          │ │
│  │ • create_project_plan()   │   │ • move_to_stage()         │ │
│  │ • deliver_project()       │   │ • get_pipeline_metrics()  │ │
│  │ • collect_payment()       │   │ • predict_close_rate()    │ │
│  │ • track_satisfaction()    │   │ • suggest_next_action()   │ │
│  └───────────────────────────┘   └───────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ML LAYER                                    │
│                                                                  │
│  Lead Scoring Classifier (Random Forest)                        │
│  ├─ Feature extraction (13 features)                            │
│  ├─ Score calculation (0-100)                                   │
│  ├─ Qualification threshold (>70)                               │
│  └─ Recommendation engine                                       │
│                                                                  │
│  Close Rate Predictor                                           │
│  ├─ Probability estimation                                      │
│  ├─ Days-to-close forecast                                      │
│  ├─ Confidence scoring                                          │
│  └─ Factor analysis                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Lead Capture Flow

```
User/System
    │
    ▼
POST /api/business/leads
    │
    ▼
ClientPipeline.capture_lead()
    │
    ├─> Governance check
    │
    ├─> Create Client (if new)
    │   └─> INSERT INTO business_clients
    │
    ├─> Create Lead
    │   └─> INSERT INTO business_leads
    │
    ├─> Create Interaction
    │   └─> INSERT INTO business_interactions
    │
    ├─> Audit log
    │   └─> ImmutableLog.log()
    │
    ├─> WebSocket broadcast
    │   └─> ws_manager.broadcast()
    │
    └─> Return {client_id, lead_id, stage}
```

### Qualification Flow

```
POST /api/business/leads/{id}/qualify
    │
    ▼
ClientPipeline.qualify_lead()
    │
    ├─> Fetch Lead + Client
    │   └─> SELECT FROM business_leads JOIN business_clients
    │
    ├─> AIConsultingEngine.qualify_lead()
    │   │
    │   ├─> Governance check
    │   │
    │   ├─> Extract features
    │   │   ├─ has_company
    │   │   ├─ has_budget
    │   │   ├─ industry
    │   │   ├─ source
    │   │   └─ ... (13 total)
    │   │
    │   ├─> Calculate score
    │   │   ├─ Base: 50
    │   │   ├─ Budget bonus: +0 to +20
    │   │   ├─ Industry bonus: +0 to +15
    │   │   ├─ Source bonus: +0 to +20
    │   │   └─ Requirements bonus: +0 to +10
    │   │
    │   ├─> Hunter scan
    │   │
    │   └─> Audit log
    │
    ├─> Update Lead
    │   └─> UPDATE business_leads SET score, stage, probability
    │
    ├─> WebSocket broadcast
    │
    └─> Return {score, qualified, recommendation}
```

### Proposal Generation Flow

```
POST /api/business/proposals/generate
    │
    ▼
AIConsultingEngine.generate_proposal()
    │
    ├─> Governance check
    │
    ├─> Fetch Client
    │   └─> SELECT FROM business_clients
    │
    ├─> Generate with Grace Architect
    │   └─> architect.generate_code()
    │
    ├─> Parse deliverables
    │   └─> Extract from generated text
    │
    ├─> Estimate timeline
    │   ├─ Sum estimated hours
    │   └─ Calculate weeks
    │
    ├─> Calculate pricing
    │   ├─ Hourly rate × hours
    │   ├─ Apply budget constraint
    │   └─ Calculate discount
    │
    ├─> Hunter scan
    │
    ├─> Audit log
    │
    └─> create_project_plan()
        │
        ├─> Create Project
        │   └─> INSERT INTO business_projects
        │
        ├─> Generate milestones
        │
        └─> Return {proposal, project_plan}
```

### Project Delivery Flow

```
POST /api/business/projects/deliver
    │
    ▼
AIConsultingEngine.deliver_project()
    │
    ├─> Fetch Project
    │   └─> SELECT FROM business_projects
    │
    ├─> If budget > $5K:
    │   └─> Parliament vote
    │       ├─> parliament.create_session()
    │       └─> Check approval
    │
    ├─> Grace Architect build
    │   └─> architect.execute_task()
    │
    ├─> Update Project
    │   └─> UPDATE business_projects SET
    │       ├─ grace_architect_used = True
    │       ├─ automated_delivery = True
    │       ├─ status = 'in_progress'
    │       └─ progress = 50.0
    │
    ├─> Audit log
    │
    └─> Return {project_id, delivery_result, status}
```

### Payment Collection Flow

```
POST /api/business/projects/{id}/payment
    │
    ▼
AIConsultingEngine.collect_payment()
    │
    ├─> Fetch Project
    │   └─> SELECT FROM business_projects
    │
    ├─> Generate invoice number
    │   └─> INV-{date}-{random}
    │
    ├─> Create Invoice
    │   └─> INSERT INTO business_invoices
    │       ├─ project_id
    │       ├─ invoice_number
    │       ├─ amount
    │       ├─ status = 'issued'
    │       ├─ issued_at
    │       ├─ due_at
    │       └─ payment_method
    │
    ├─> Audit log
    │
    └─> Return {invoice_id, invoice_number, payment_link}
```

## Database Schema

```sql
-- Client entity
CREATE TABLE business_clients (
    id INTEGER PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    email VARCHAR(256) NOT NULL,
    company VARCHAR(256),
    industry VARCHAR(128),
    budget_range VARCHAR(64),
    source VARCHAR(64) NOT NULL,
    country VARCHAR(64),
    timezone VARCHAR(64),
    preferred_contact VARCHAR(64) DEFAULT 'email',
    lifetime_value FLOAT DEFAULT 0.0,
    total_projects INTEGER DEFAULT 0,
    satisfaction_score FLOAT,
    status VARCHAR(32) DEFAULT 'active',
    notes TEXT,
    metadata JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Lead/opportunity
CREATE TABLE business_leads (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES business_clients(id),
    score FLOAT DEFAULT 0.0,
    stage VARCHAR(32) DEFAULT 'LEAD',
    probability FLOAT DEFAULT 0.0,
    value_estimate FLOAT DEFAULT 0.0,
    project_type VARCHAR(128),
    requirements TEXT,
    timeline VARCHAR(128),
    budget FLOAT,
    qualification_data JSON DEFAULT '{}',
    ml_features JSON DEFAULT '{}',
    qualified_at TIMESTAMP,
    converted_at TIMESTAMP,
    lost_at TIMESTAMP,
    lost_reason VARCHAR(256),
    next_action VARCHAR(256),
    next_action_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Project
CREATE TABLE business_projects (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES business_clients(id),
    lead_id INTEGER REFERENCES business_leads(id),
    title VARCHAR(256) NOT NULL,
    description TEXT,
    scope TEXT NOT NULL,
    deliverables JSON DEFAULT '[]',
    timeline VARCHAR(128),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    budget FLOAT NOT NULL,
    actual_cost FLOAT DEFAULT 0.0,
    status VARCHAR(32) DEFAULT 'proposed',
    progress FLOAT DEFAULT 0.0,
    proposal_generated BOOLEAN DEFAULT FALSE,
    proposal_approved BOOLEAN DEFAULT FALSE,
    contract_signed BOOLEAN DEFAULT FALSE,
    grace_architect_used BOOLEAN DEFAULT FALSE,
    automated_delivery BOOLEAN DEFAULT FALSE,
    nps_score INTEGER,
    client_feedback TEXT,
    metadata JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Interaction
CREATE TABLE business_interactions (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES business_clients(id),
    project_id INTEGER REFERENCES business_projects(id),
    interaction_type VARCHAR(64) NOT NULL,
    channel VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    sentiment FLOAT,
    automated BOOLEAN DEFAULT FALSE,
    grace_generated BOOLEAN DEFAULT FALSE,
    human_approved BOOLEAN DEFAULT FALSE,
    metadata JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Invoice
CREATE TABLE business_invoices (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES business_projects(id),
    invoice_number VARCHAR(64) UNIQUE NOT NULL,
    amount FLOAT NOT NULL,
    status VARCHAR(32) DEFAULT 'draft',
    issued_at TIMESTAMP,
    due_at TIMESTAMP,
    paid_at TIMESTAMP,
    payment_method VARCHAR(64),
    transaction_id VARCHAR(256),
    stripe_invoice_id VARCHAR(256),
    stripe_payment_intent VARCHAR(256),
    notes TEXT,
    metadata JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## Security & Governance

### Governance Checks
Every sensitive operation checked:
```python
await governance_engine.check_policy(
    action="qualify_lead",
    context={"client": email}
)
```

### Hunter Scanning
All client data scanned:
```python
await hunter.scan_data(
    data_type="client_qualification",
    data={...}
)
```

### Parliament Voting
High-value projects require approval:
```python
if project.budget > 5000:
    vote = await parliament.create_session(...)
    if not vote["approved"]:
        raise ValueError("Rejected")
```

### Verification
All operations verified:
```python
self.verification = VerificationEngine()
```

### Audit Trail
Immutable logging:
```python
await self.audit.log(
    action="lead_qualified",
    user="ai_consulting_engine",
    details={...}
)
```

## Performance

### Async Operations
All I/O is async:
```python
async with async_session() as session:
    result = await session.execute(...)
```

### Database Indexes
```sql
CREATE INDEX idx_leads_stage ON business_leads(stage);
CREATE INDEX idx_leads_score ON business_leads(score);
CREATE INDEX idx_projects_status ON business_projects(status);
CREATE INDEX idx_invoices_status ON business_invoices(status);
```

### Caching Strategy
- Client data: 1 hour
- Pipeline metrics: 5 minutes
- ML predictions: 30 minutes

## Scalability

### Horizontal Scaling
- Stateless API layer
- Database connection pooling
- WebSocket distributed via Redis

### Load Distribution
- ML inference: Separate service
- Grace Architect: Queue-based
- Payment processing: Async webhooks

## Monitoring

### Metrics Tracked
- Lead capture rate
- Qualification accuracy
- Conversion rates by stage
- Revenue per channel
- Client satisfaction trends
- System performance

### Alerts
- Low qualification rates
- Stuck pipeline stages
- Payment failures
- Client satisfaction drops
- System errors

## Future Enhancements

### Phase 2: Advanced ML
- Deep learning lead scoring
- Churn prediction
- Lifetime value estimation
- Optimal pricing models

### Phase 3: Full Automation
- Chatbot client communication
- Auto-contract generation
- Self-service portal
- Auto-upsell engine

### Phase 4: Business Empire
- Multi-tenant SaaS
- White-label platform
- AI consulting marketplace
- Franchise model
