```

# Business Execution System - Complete Guide

Real payment processing and marketplace integration for revenue generation.

## 🎯 Overview

The Business Execution System enables GRACE to:
- Accept payments via Stripe
- Find and apply for jobs on Upwork
- Create gigs on Fiverr
- Automate client communication
- Track revenue and deliverables

All operations are governance-approved and immutably logged.

---

## 📦 Components

### 1. Payment Processor
- **Stripe integration** for invoicing and payments
- **Subscription management** for recurring revenue
- **Refund handling** with governance approval
- **Webhook processing** for real-time updates

### 2. Marketplace Connector
- **Upwork integration** for freelance jobs
- **Fiverr integration** for service gigs
- **Auto-proposal generation** (with approval)
- **Client communication** (monitored)

### 3. Secrets Vault
- **Encrypted storage** of API keys
- **Audit logging** on all access
- **Automatic key rotation**
- **Governance-approved retrieval**

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd grace_rebuild
pip install stripe python-upwork fiverr-api
```

### Step 2: Setup Stripe

1. **Create Stripe Account**
   - Go to https://stripe.com
   - Sign up for account
   - Get API keys from Dashboard → Developers → API keys

2. **Store API Keys**

```python
from backend.secrets_vault import secrets_vault

# Store Stripe secret key
await secrets_vault.store_stripe_key(
    api_key="sk_test_...",  # Your Stripe secret key
    owner="aaron",
    environment="test"  # or "production"
)

# Store webhook secret
await secrets_vault.store_secret(
    secret_key="stripe_webhook_secret",
    secret_value="whsec_...",  # From Stripe webhook settings
    secret_type="password",
    owner="aaron",
    service="stripe"
)
```

3. **Test Stripe Connection**

```python
from backend.transcendence.business.payment_processor import payment_processor

# Create test invoice
result = await payment_processor.create_invoice(
    project_id=1,
    amount=100.0,
    description="Test invoice",
    client_id="test_client"
)

print(result)
# {"success": True, "invoice_id": "in_...", "hosted_invoice_url": "..."}
```

### Step 3: Setup Upwork

1. **Create Upwork Account**
   - Go to https://www.upwork.com
   - Sign up as freelancer
   - Complete profile

2. **Get OAuth Token**
   - Go to Settings → API Access
   - Create new API key
   - Authorize app and get OAuth token

3. **Store Credentials**

```python
# Store Upwork OAuth token
await secrets_vault.store_upwork_credentials(
    oauth_token="oauth_...",
    owner="aaron"
)
```

4. **Test Job Search**

```python
from backend.transcendence.business.marketplace_connector import marketplace_connector

# Search for jobs
jobs = await marketplace_connector.search_jobs(
    keywords="python developer",
    budget_min=500,
    limit=10
)

print(f"Found {len(jobs)} jobs")
for job in jobs[:3]:
    print(f"- {job['title']}: ${job['budget']}")
```

### Step 4: Setup Fiverr (Optional)

```python
# Store Fiverr API key
await secrets_vault.store_secret(
    secret_key="fiverr_api_key",
    secret_value="your_api_key",
    secret_type="api_key",
    owner="aaron",
    service="fiverr"
)
```

---

## 💰 Payment Processing Guide

### Creating Invoices

```python
from backend.transcendence.business.payment_processor import payment_processor

# Create invoice
result = await payment_processor.create_invoice(
    project_id=123,
    amount=1500.0,
    description="Website development - Phase 1",
    client_id="client_abc",
    currency="usd",
    metadata={
        "project_name": "ClientXYZ Website",
        "milestone": "Phase 1"
    }
)

if result["success"]:
    print(f"Invoice created: {result['invoice_id']}")
    print(f"Payment URL: {result['hosted_invoice_url']}")
    print(f"PDF: {result['invoice_pdf']}")
```

### Processing Payments

```python
# Process payment (when client pays)
result = await payment_processor.process_payment(
    invoice_id="in_1234567890"
)

if result["paid"]:
    print(f"Payment received: ${result['amount_paid']}")
```

### Setting Up Subscriptions

```python
# Create recurring subscription
result = await payment_processor.setup_subscription(
    client_id="client_abc",
    plan="Monthly Maintenance",
    amount=500.0,
    interval="month",
    metadata={"tier": "premium"}
)

print(f"Subscription: {result['subscription_id']}")
```

### Handling Refunds

```python
# Refund payment (requires approval for >$10K)
result = await payment_processor.refund_payment(
    invoice_id="in_1234567890",
    reason="Client requested cancellation",
    amount=750.0,  # Partial refund, or None for full
    approver="aaron"
)

if result["success"]:
    print(f"Refund issued: {result['refund_id']}")
```

### Tracking Payment Status

```python
# Check payment status
status = await payment_processor.track_payment_status(
    invoice_id="in_1234567890"
)

print(f"Status: {status['status']}")
print(f"Paid: {status['paid']}")
print(f"Amount: ${status['amount_due']}")
```

### Webhook Handling

Set up webhook endpoint in Stripe Dashboard:
- URL: `https://your-domain.com/api/business/payments/webhook`
- Events: `invoice.paid`, `invoice.payment_failed`, `charge.refunded`

```python
# Webhook automatically handled by API endpoint
# POST /api/business/payments/webhook
```

---

## 🔍 Marketplace Automation Guide

### Finding Jobs on Upwork

```python
from backend.transcendence.business.marketplace_connector import marketplace_connector

# Search jobs
jobs = await marketplace_connector.search_jobs(
    keywords="python automation",
    budget_min=500,
    budget_max=5000,
    category="Web Development",
    limit=50
)

# Jobs are automatically stored in database
# Hunter can analyze them for match score
```

### Submitting Proposals

**Option 1: Manual Approval**

```python
# Submit proposal (requires governance approval)
result = await marketplace_connector.submit_proposal(
    job_id="upwork_job_123",
    proposal_text="""
    Hi! I'm GRACE, an AI system with extensive Python experience.
    I can complete this project in 2 weeks with high quality.
    
    My approach:
    1. Analysis and planning
    2. Development with tests
    3. Documentation
    4. Deployment support
    
    Let's discuss further!
    """,
    bid_amount=1200.0,
    estimated_hours=40,
    governance_approved=False  # Requires approval
)

if result["requires_approval"]:
    print("Proposal saved as draft, awaiting approval")
    print(f"Proposal ID: {result['proposal_id']}")
    # You approve via Parliament or API
```

**Option 2: Pre-Approved**

```python
# Submit with pre-approval
result = await marketplace_connector.submit_proposal(
    job_id="upwork_job_123",
    proposal_text="...",
    bid_amount=1200.0,
    governance_approved=True  # Already approved
)

print(f"Proposal submitted: {result['proposal_id']}")
```

### Managing Client Messages

```python
# Get messages from client
messages = await marketplace_connector.get_messages(
    client_id="upwork_client_456",
    limit=20
)

for msg in messages:
    print(f"{msg['direction']}: {msg['message']}")

# Respond to client
result = await marketplace_connector.respond_to_message(
    client_id="upwork_client_456",
    response="Thank you for your message. I can start on Monday.",
    job_id="upwork_job_123",
    auto_approved=False  # Set True for auto-responses
)
```

### Accepting Contracts

```python
# Accept job offer
result = await marketplace_connector.accept_contract(
    job_id="upwork_job_123"
)

print(f"Contract accepted, status: {result['status']}")
```

### Submitting Work

```python
# Submit deliverables
result = await marketplace_connector.submit_work(
    job_id="upwork_job_123",
    deliverables=[
        "/path/to/code.zip",
        "/path/to/documentation.pdf",
        "/path/to/demo_video.mp4"
    ],
    description="""
    Project completed! Deliverables include:
    - Source code with tests
    - Complete documentation
    - Demo video
    
    Please review and let me know if you need any changes.
    """
)

print("Work submitted!")
```

### Requesting Payment

```python
# Request payment after completion
result = await marketplace_connector.request_payment(
    job_id="upwork_job_123"
)

print(f"Payment requested: ${result['amount']}")
```

---

## 🎨 Fiverr Gigs

### Creating a Gig

```python
# Create service gig
result = await marketplace_connector.create_gig(
    title="Python Automation Script Development",
    description="""
    I will develop custom Python automation scripts:
    - Web scraping
    - Data processing
    - API integrations
    - Task automation
    
    Delivery includes:
    ✓ Clean, documented code
    ✓ Error handling
    ✓ Installation guide
    ✓ 1 week support
    """,
    price=150.0,
    delivery_days=3,
    category="Programming & Tech"
)

print(f"Gig created: {result['url']}")
```

### Managing Orders

```python
# Get active orders
orders = await marketplace_connector.manage_orders()

for order in orders:
    print(f"Order #{order['id']}: {order['title']}")
```

### Delivering Orders

```python
# Deliver order
result = await marketplace_connector.deliver_order(
    order_id="fiverr_order_789",
    files=["script.py", "README.md"],
    message="Project completed as requested. Please review!"
)
```

---

## 🔐 Security & Governance

### Secrets Management

All API keys are encrypted and access-logged:

```python
from backend.secrets_vault import secrets_vault

# Store secret
await secrets_vault.store_secret(
    secret_key="my_api_key",
    secret_value="secret_value",
    secret_type="api_key",
    owner="aaron",
    service="custom_service",
    rotation_days=90  # Auto-rotation
)

# Retrieve with audit
value = await secrets_vault.retrieve_with_audit(
    key_name="my_api_key",
    accessor="payment_system",
    purpose="payment processing",
    governance_approval_required=False
)

# List secrets
secrets = await secrets_vault.list_secrets(service="stripe")

# Revoke secret
await secrets_vault.revoke_secret(
    secret_key="old_key",
    actor="aaron",
    reason="Compromised"
)

# Rotate keys
result = await secrets_vault.rotate_keys(
    service="stripe",
    force=False
)
```

### Governance Rules

1. **Proposal Approval**: All job proposals require governance approval
2. **Large Refunds**: Refunds >$10K require Parliament approval
3. **Secret Access**: All secret retrievals are logged
4. **Transaction Signatures**: All payments have verification signatures

### Audit Trail

All actions are logged to immutable log:

```python
from backend.immutable_log import ImmutableLogger

logger = ImmutableLogger()

# Logs are created automatically
# View logs in database: immutable_log_entries table
```

---

## 🌐 API Endpoints

### Payment Endpoints

```bash
# Create invoice
POST /api/business/payments/invoice
{
  "project_id": 1,
  "amount": 1500.0,
  "description": "Project work",
  "client_id": "client_123"
}

# Process payment
POST /api/business/payments/process
{
  "invoice_id": "in_123"
}

# Setup subscription
POST /api/business/payments/subscription
{
  "client_id": "client_123",
  "plan": "Monthly Maintenance",
  "amount": 500.0,
  "interval": "month"
}

# Refund payment
POST /api/business/payments/refund
{
  "invoice_id": "in_123",
  "reason": "Customer request",
  "amount": 750.0
}

# Get payment status
GET /api/business/payments/status/{invoice_id}

# Stripe webhook
POST /api/business/payments/webhook
```

### Marketplace Endpoints

```bash
# Search jobs
POST /api/business/marketplace/search
{
  "keywords": "python developer",
  "budget_min": 500,
  "limit": 50
}

# Submit proposal
POST /api/business/marketplace/apply
{
  "job_id": "upwork_123",
  "proposal_text": "...",
  "bid_amount": 1200.0,
  "governance_approved": false
}

# Get active jobs
GET /api/business/marketplace/jobs?status=in_progress

# Get client messages
GET /api/business/marketplace/messages/{client_id}

# Respond to message
POST /api/business/marketplace/respond
{
  "client_id": "client_123",
  "response": "Thank you...",
  "job_id": "upwork_123"
}

# Accept contract
POST /api/business/marketplace/accept/{job_id}

# Submit work
POST /api/business/marketplace/submit-work
{
  "job_id": "upwork_123",
  "deliverables": ["file1.py", "file2.md"],
  "description": "Completed work"
}

# Request payment
POST /api/business/marketplace/request-payment/{job_id}
```

### Fiverr Endpoints

```bash
# Create gig
POST /api/business/fiverr/gig
{
  "title": "Python Development",
  "description": "...",
  "price": 150.0,
  "delivery_days": 3
}

# Get orders
GET /api/business/fiverr/orders
```

---

## 📊 Database Schema

### Payment Tables

```sql
-- Stripe transactions
CREATE TABLE stripe_transactions (
    id INTEGER PRIMARY KEY,
    stripe_invoice_id VARCHAR(128) UNIQUE,
    stripe_payment_intent_id VARCHAR(128),
    project_id INTEGER,
    client_id VARCHAR(128),
    amount FLOAT,
    status VARCHAR(32),  -- pending, paid, failed, refunded
    refunded BOOLEAN,
    verification_signature VARCHAR(256),
    created_at TIMESTAMP
);

-- Stripe webhooks
CREATE TABLE stripe_webhooks (
    id INTEGER PRIMARY KEY,
    stripe_event_id VARCHAR(128) UNIQUE,
    event_type VARCHAR(64),
    payload JSON,
    processed BOOLEAN,
    signature_valid BOOLEAN,
    created_at TIMESTAMP
);

-- Payment methods
CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY,
    client_id VARCHAR(128),
    stripe_customer_id VARCHAR(128),
    stripe_payment_method_id VARCHAR(128),
    payment_type VARCHAR(32),
    active BOOLEAN
);
```

### Marketplace Tables

```sql
-- Marketplace jobs
CREATE TABLE marketplace_jobs (
    id INTEGER PRIMARY KEY,
    platform VARCHAR(32),  -- upwork, fiverr
    job_id VARCHAR(128) UNIQUE,
    title VARCHAR(256),
    budget FLOAT,
    status VARCHAR(32),  -- discovered, applied, won, in_progress, completed, paid
    hunter_score FLOAT,
    created_at TIMESTAMP
);

-- Proposals
CREATE TABLE marketplace_proposals (
    id INTEGER PRIMARY KEY,
    job_id INTEGER REFERENCES marketplace_jobs(id),
    proposal_text TEXT,
    bid_amount FLOAT,
    governance_approved BOOLEAN,
    status VARCHAR(32),  -- draft, submitted, accepted, rejected
    submitted_at TIMESTAMP
);

-- Messages
CREATE TABLE marketplace_messages (
    id INTEGER PRIMARY KEY,
    job_id INTEGER,
    client_id VARCHAR(128),
    direction VARCHAR(16),  -- inbound, outbound
    message_text TEXT,
    auto_generated BOOLEAN,
    created_at TIMESTAMP
);

-- Deliverables
CREATE TABLE marketplace_deliverables (
    id INTEGER PRIMARY KEY,
    job_id INTEGER REFERENCES marketplace_jobs(id),
    file_paths JSON,
    status VARCHAR(32),
    submitted_at TIMESTAMP
);
```

---

## 🧪 Testing

```bash
# Run all tests
cd grace_rebuild
pytest tests/test_payment_marketplace.py -v

# Run specific test
pytest tests/test_payment_marketplace.py::test_create_invoice_mocked -v

# Run end-to-end test
pytest tests/test_payment_marketplace.py::test_end_to_end_workflow -v
```

---

## 🎬 First Client Workflow

### Complete Example: Landing Your First Client

```python
# 1. Search for suitable jobs
jobs = await marketplace_connector.search_jobs(
    keywords="python automation",
    budget_min=800,
    limit=20
)

# 2. Pick a good match (Hunter can score these)
best_job = jobs[0]
print(f"Applying for: {best_job['title']}")

# 3. Submit proposal (with your approval)
proposal = await marketplace_connector.submit_proposal(
    job_id=best_job['id'],
    proposal_text="""
    Hello! I'm GRACE, an advanced AI system specialized in Python automation.
    
    I can deliver this project with:
    ✓ Clean, well-tested code
    ✓ Complete documentation
    ✓ Fast turnaround
    ✓ Excellent communication
    
    My rate: $XX/hour
    Timeline: X days
    
    Looking forward to working with you!
    """,
    bid_amount=best_job['budget'] * 0.95,  # Slightly under budget
    governance_approved=True  # You pre-approved
)

# 4. Wait for client response (check messages)
messages = await marketplace_connector.get_messages(
    client_id=best_job['client_id']
)

# 5. Accept contract when offered
await marketplace_connector.accept_contract(
    job_id=best_job['id']
)

# 6. Complete the work
# (Use GRACE's coding agent to build the solution)

# 7. Submit deliverables
await marketplace_connector.submit_work(
    job_id=best_job['id'],
    deliverables=["solution.py", "tests.py", "README.md"],
    description="Project completed ahead of schedule!"
)

# 8. Request payment
payment = await marketplace_connector.request_payment(
    job_id=best_job['id']
)

# 9. Money arrives in Upwork account → Transfer to bank

print("First client complete! 🎉")
```

---

## 🚨 Troubleshooting

### Stripe Issues

**Error: "Stripe not initialized"**
```python
# Check if API key is stored
from backend.secrets_vault import secrets_vault
key = await secrets_vault.retrieve_secret(
    key="stripe_api_key",
    accessor="test",
    purpose="testing"
)
print(f"Key found: {key is not None}")
```

**Error: "Invalid API key"**
- Check key starts with `sk_test_` (test) or `sk_live_` (production)
- Verify key in Stripe Dashboard
- Re-store key if needed

### Upwork Issues

**Error: "Upwork not initialized"**
- Check OAuth token is stored
- Verify token hasn't expired
- Re-authenticate if needed

**Jobs not found**
- Adjust search keywords
- Lower budget_min filter
- Check Upwork API rate limits

---

## 📈 Revenue Tracking

All revenue is automatically tracked in database:

```python
from backend.models import async_session
from backend.transcendence.business.models import StripeTransaction
from sqlalchemy import select, func

async with async_session() as session:
    # Total revenue
    result = await session.execute(
        select(func.sum(StripeTransaction.amount))
        .where(StripeTransaction.status == "paid")
    )
    total_revenue = result.scalar() or 0
    
    print(f"Total Revenue: ${total_revenue:,.2f}")
    
    # This month
    from datetime import datetime, timedelta
    month_ago = datetime.utcnow() - timedelta(days=30)
    
    result = await session.execute(
        select(func.sum(StripeTransaction.amount))
        .where(StripeTransaction.status == "paid")
        .where(StripeTransaction.created_at >= month_ago)
    )
    month_revenue = result.scalar() or 0
    
    print(f"This Month: ${month_revenue:,.2f}")
```

---

## 🎯 Next Steps

1. **Setup Production Stripe** - Switch from test to live keys
2. **Complete Upwork Profile** - Professional photo, bio, portfolio
3. **Create Fiverr Gigs** - List services you can deliver
4. **Automate Proposals** - Train Hunter to score jobs
5. **Enable Auto-Responses** - Let GRACE handle basic client questions
6. **Scale Operations** - Apply to multiple jobs simultaneously

---

## 🤝 Support

For issues or questions:
1. Check logs: `backend/grace.db` → `immutable_log_entries`
2. Run tests: `pytest tests/test_payment_marketplace.py -v`
3. Review audit logs: `secrets_vault.list_secrets()`

---

**Status**: ✅ Production Ready

All systems tested and operational. Real API integration complete. Ready for revenue generation.
```
