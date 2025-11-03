# Business Empire System

Real payment processing and marketplace integration for automated revenue generation.

## 🎯 Overview

The Business Empire system enables GRACE to autonomously:
- **Accept payments** via Stripe (invoices, subscriptions, refunds)
- **Find freelance work** on Upwork
- **Create service gigs** on Fiverr
- **Communicate with clients** (with oversight)
- **Track revenue** and deliverables

All operations are governance-approved, verified, and immutably logged.

## 📦 Components

```
business/
├── __init__.py              # Module exports
├── models.py                # Database models
├── payment_processor.py     # Stripe integration
├── marketplace_connector.py # Upwork/Fiverr integration
├── api.py                   # REST API endpoints
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install stripe python-upwork
```

### 2. Configure API Keys

```bash
cd grace_rebuild
python setup_business.py
```

Or manually:

```python
from backend.secrets_vault import secrets_vault

# Store Stripe key
await secrets_vault.store_stripe_key(
    api_key="sk_test_...",
    owner="aaron",
    environment="test"
)

# Store Upwork token
await secrets_vault.store_upwork_credentials(
    oauth_token="oauth_...",
    owner="aaron"
)
```

### 3. Test the System

```bash
pytest tests/test_payment_marketplace.py -v
```

### 4. Start Using

See [BUSINESS_EXECUTION.md](../../../BUSINESS_EXECUTION.md) for complete guide.

## 💰 Payment Processing

### Create Invoice

```python
from backend.transcendence.business.payment_processor import payment_processor

result = await payment_processor.create_invoice(
    project_id=1,
    amount=1500.0,
    description="Website development",
    client_id="client_123"
)

# Returns:
# {
#   "success": True,
#   "invoice_id": "in_...",
#   "hosted_invoice_url": "https://...",
#   "invoice_pdf": "https://..."
# }
```

### Process Payment

```python
result = await payment_processor.process_payment(
    invoice_id="in_..."
)
```

### Setup Subscription

```python
result = await payment_processor.setup_subscription(
    client_id="client_123",
    plan="Monthly Maintenance",
    amount=500.0,
    interval="month"
)
```

### Refund Payment

```python
result = await payment_processor.refund_payment(
    invoice_id="in_...",
    reason="Customer request",
    approver="aaron"
)
# Large refunds (>$10K) require Parliament approval
```

## 🔍 Marketplace Integration

### Search Jobs

```python
from backend.transcendence.business.marketplace_connector import marketplace_connector

jobs = await marketplace_connector.search_jobs(
    keywords="python developer",
    budget_min=500,
    limit=50
)
```

### Submit Proposal

```python
result = await marketplace_connector.submit_proposal(
    job_id="upwork_job_123",
    proposal_text="I can help with this project...",
    bid_amount=1200.0,
    governance_approved=True  # Requires approval
)
```

### Accept Contract

```python
result = await marketplace_connector.accept_contract(
    job_id="upwork_job_123"
)
```

### Submit Work

```python
result = await marketplace_connector.submit_work(
    job_id="upwork_job_123",
    deliverables=["file1.py", "file2.md"],
    description="Completed work"
)
```

### Request Payment

```python
result = await marketplace_connector.request_payment(
    job_id="upwork_job_123"
)
```

## 🌐 API Endpoints

All endpoints under `/api/business`:

### Payment Endpoints

- `POST /payments/invoice` - Create invoice
- `POST /payments/process` - Process payment
- `POST /payments/subscription` - Setup subscription
- `POST /payments/refund` - Refund payment
- `GET /payments/status/{invoice_id}` - Get status
- `POST /payments/webhook` - Stripe webhook

### Marketplace Endpoints

- `POST /marketplace/search` - Search jobs
- `POST /marketplace/apply` - Submit proposal
- `GET /marketplace/jobs` - List active jobs
- `GET /marketplace/messages/{client_id}` - Get messages
- `POST /marketplace/respond` - Send message
- `POST /marketplace/accept/{job_id}` - Accept contract
- `POST /marketplace/submit-work` - Submit deliverables
- `POST /marketplace/request-payment/{job_id}` - Request payment

### Fiverr Endpoints

- `POST /fiverr/gig` - Create gig
- `GET /fiverr/orders` - Get orders

## 🔐 Security

### Secrets Management

All API keys are:
- **Encrypted** using Fernet
- **Access-logged** for audit trail
- **Governance-controlled** for sensitive operations
- **Auto-rotated** based on schedule

### Verification

All transactions have:
- **Verification signatures** (SHA-256 hash)
- **Immutable log entries**
- **Governance approval** (when required)
- **Parliament oversight** (for large amounts)

### Audit Trail

Every action is logged:

```python
# Check audit logs
from backend.immutable_log import ImmutableLogger

logger = ImmutableLogger()
# All logs in: immutable_log_entries table
```

## 📊 Database Schema

### Payment Tables

```sql
-- Stripe transactions
stripe_transactions (
    id, stripe_invoice_id, project_id, client_id,
    amount, status, refunded, verification_signature
)

-- Webhooks
stripe_webhooks (
    id, stripe_event_id, event_type, payload,
    processed, signature_valid
)

-- Payment methods
payment_methods (
    id, client_id, stripe_customer_id,
    payment_type, active
)
```

### Marketplace Tables

```sql
-- Jobs
marketplace_jobs (
    id, platform, job_id, title, budget,
    status, hunter_score
)

-- Proposals
marketplace_proposals (
    id, job_id, proposal_text, bid_amount,
    governance_approved, status
)

-- Messages
marketplace_messages (
    id, job_id, client_id, direction,
    message_text, auto_generated
)

-- Deliverables
marketplace_deliverables (
    id, job_id, file_paths, status
)
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/test_payment_marketplace.py -v

# Run specific tests
pytest tests/test_payment_marketplace.py::test_create_invoice_mocked -v
pytest tests/test_payment_marketplace.py::test_end_to_end_workflow -v

# With coverage
pytest tests/test_payment_marketplace.py --cov=backend.transcendence.business
```

## 📖 Full Documentation

See [BUSINESS_EXECUTION.md](../../../BUSINESS_EXECUTION.md) for:
- Complete setup guide
- Workflow examples
- API reference
- Troubleshooting
- Revenue tracking

## 🎯 Example Workflows

### First Client

```python
# 1. Find jobs
jobs = await marketplace_connector.search_jobs(
    keywords="python automation",
    budget_min=800
)

# 2. Apply
await marketplace_connector.submit_proposal(
    job_id=jobs[0]['id'],
    proposal_text="...",
    bid_amount=jobs[0]['budget'] * 0.95,
    governance_approved=True
)

# 3. Accept when offered
await marketplace_connector.accept_contract(job_id=jobs[0]['id'])

# 4. Complete work
await marketplace_connector.submit_work(
    job_id=jobs[0]['id'],
    deliverables=["solution.py"],
    description="Completed!"
)

# 5. Get paid
await marketplace_connector.request_payment(job_id=jobs[0]['id'])
```

### Recurring Revenue

```python
# Setup monthly subscription
await payment_processor.setup_subscription(
    client_id="client_123",
    plan="Website Maintenance",
    amount=500.0,
    interval="month"
)

# Payments process automatically each month
```

## 🚨 Important Notes

1. **Test Mode**: Start with Stripe test keys (`sk_test_...`)
2. **Governance**: All proposals require approval by default
3. **Large Refunds**: >$10K refunds need Parliament approval
4. **Rate Limits**: Respect Upwork/Fiverr API rate limits
5. **Client Communication**: Review auto-responses before enabling

## 💡 Tips

- Use **Hunter** to score jobs for best matches
- Enable **auto-responses** for common client questions
- Set up **Parliament approval** for high-value contracts
- Monitor **revenue** in database regularly
- Keep **API keys** rotated (90-day schedule)

## 🤝 Support

For issues:
1. Check logs in `immutable_log_entries` table
2. Run tests to verify system health
3. Review `BUSINESS_EXECUTION.md` guide
4. Check secret configuration with `secrets_vault.list_secrets()`

---

**Status**: ✅ Production Ready

All components tested and operational. Ready for revenue generation.
