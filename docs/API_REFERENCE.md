# Grace API Reference - Version 2.2.0

**Base URL**: `http://localhost:8000`  
**Documentation**: `http://localhost:8000/docs`  
**Version Info**: `GET /version`

## Core Endpoints

### Health & Version
- `GET /health` - System health check
- `GET /version` - Detailed version and progress info

---

## Guardian API (`/api/guardian`)

**Self-healing and playbook management**

### Endpoints
- `GET /stats` - Comprehensive Guardian statistics
- `GET /healer/stats` - Last 5 healing runs with summary
- `GET /playbooks` - List all 13 playbooks with success rates
- `GET /mttr/by-issue-type` - MTTR breakdown by issue type
- `GET /mttr/by-playbook` - MTTR breakdown by playbook
- `GET /failures/recent?limit=10` - Recent healing failures

### Response Example
```json
{
  "mttr": {
    "mttr_seconds": 85.3,
    "mttr_minutes": 1.42,
    "success_rate_percent": 94.2,
    "target_met": true
  }
}
```

---

## Learning API (`/api/learning`)

**Knowledge gap detection and autonomous learning**

### Endpoints
- `GET /gaps` - Get prioritized knowledge gaps
- `POST /gaps/detect?lookback_hours=24` - Trigger gap detection
- `POST /record-query` - Record query for gap analysis
  ```json
  {
    "query": "How does self-healing work?",
    "domain": "core",
    "confidence": 0.65,
    "retrieved_docs": 2
  }
  ```
- `GET /stats` - Learning system statistics

### Response Example
```json
{
  "total_gaps": 5,
  "gaps": [{
    "gap_id": "gap_core_healing_20251117",
    "domain": "core",
    "topic": "healing",
    "confidence_score": 0.65,
    "priority": "high",
    "suggested_sources": ["docs.grace-ai.dev/core", "web_search: healing core"]
  }]
}
```

---

## Coding Pipeline API (`/api/coding`)

**Autonomous software development**

### Endpoints
- `POST /tasks` - Create coding task
  ```json
  {
    "description": "Add user authentication",
    "repository": "github.com/user/repo",
    "branch": "main"
  }
  ```
- `GET /tasks/{task_id}` - Get task status
- `GET /stats` - Pipeline statistics

### Pipeline Stages
1. **Fetch Context** - Codebase analysis
2. **Propose Diff** - Code changes
3. **Run Tests** - Unit/integration/lint
4. **Collect Diagnostics** - Errors/warnings
5. **Request Approval** - Governance gate
6. **Merge** - With verification
7. **Observe** - Post-merge metrics

---

## Enterprise API (`/api/enterprise`)

### Tenancy
- `POST /tenants?name=Acme&tier=pro` - Create tenant
- `GET /tenants/{tenant_id}` - Get tenant stats and quota usage

**Tiers**: Free, Starter, Pro, Enterprise

### Billing
- `POST /billing/subscriptions` - Create subscription
  ```json
  {
    "tenant_id": "tenant_abc123",
    "plan_id": "pro",
    "cycle": "monthly"
  }
  ```
- `POST /billing/usage` - Record metered usage
- `POST /billing/invoices/{tenant_id}` - Generate invoice

**Plans**:
- Free: $0/mo
- Starter: $29/mo
- Pro: $99/mo
- Enterprise: $499/mo

### Users & RBAC
- `POST /users` - Create user with roles
  ```json
  {
    "email": "user@example.com",
    "tenant_id": "tenant_abc123",
    "roles": ["developer", "approver"]
  }
  ```
- `GET /users/{user_id}/permissions` - Get user permissions

**Roles**: Viewer, Developer, Approver, Admin  
**Permissions**: 14 granular permissions (knowledge:read, playbooks:execute, etc.)

### Product Templates
- `GET /templates?category=website` - List templates
- `POST /products/instantiate` - Instantiate product
  ```json
  {
    "template_id": "landing_page",
    "tenant_id": "tenant_abc123",
    "config": {}
  }
  ```

**Available Templates**:
1. Landing Page Builder (15min setup)
2. Sales Funnel System (25min setup)
3. CRM System (30min setup)
4. AI Developer Tools (20min setup)

### Observability
- `GET /observability/golden-signals` - Latency/Traffic/Errors/Saturation

**Metrics**:
- Latency: P50, P95, P99 (target: P95 < 200ms)
- Traffic: RPS, total requests
- Errors: Error rate (target: < 1%)
- Saturation: CPU, memory, disk (targets: < 80/85/90%)

### Disaster Recovery
- `POST /dr/backup?backup_type=incremental` - Create backup
- `POST /dr/restore/{backup_id}` - Restore from backup
- `GET /dr/stats` - DR statistics and RTO/RPO compliance

**Objectives**:
- RTO (Recovery Time): 15 minutes
- RPO (Recovery Point): 60 minutes

---

## System Metrics

### Current Performance
- **API Endpoints**: 31 new + 294 existing = 325 total
- **Playbooks**: 13 (all with verify/rollback/dry_run)
- **MTTR**: Target < 120 seconds
- **RAG Precision@5**: 0.60 (target 0.85)
- **Version**: 2.2.0
- **Progress**: 93%

### SLO Targets
- API P95 latency: < 200ms
- Error rate: < 1%
- Uptime: 99.9%
- MTTR: < 2 minutes

---

## Authentication

**API Key** (Header):
```
X-API-Key: gk_your_api_key_here
```

**JWT** (Coming soon):
```
Authorization: Bearer {jwt_token}
```

---

## Rate Limits

**Default**: 60 requests/minute, burst 10

**Headers**:
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Limit`: Total limit
- `X-Response-Time`: Response time in ms

**Tiers**:
- Free: 1,000 API calls/day
- Starter: 10,000 API calls/day
- Pro: 100,000 API calls/day
- Enterprise: Unlimited

---

## Error Responses

**Standard Error Format**:
```json
{
  "detail": "Error message here",
  "status_code": 400
}
```

**Common Status Codes**:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden (quota/permission)
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

---

**Last Updated**: 2025-11-17  
**Version**: 2.2.0  
**Status**: Production Ready (Backend)
