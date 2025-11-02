# Grace Monitoring & Observability

## 📊 Built-in Monitoring

### Health Endpoints
```bash
# Overall health
GET /health
Response: {"status": "ok", "message": "Grace API is running"}

# Detailed component health
GET /api/health/status
Response: {
  "system_mode": "normal",
  "checks": [...],
  "actions": [...]
}

# System mode
GET /api/health/mode
Response: {"mode": "normal", "reason": "", "changed_at": "..."}
```

### Metrics Endpoints
```bash
# Summary metrics
GET /api/metrics/summary
Response: {
  "total_messages": 100,
  "active_users": 5,
  "registered_users": 10
}

# User-specific
GET /api/metrics/user/{username}

# Causal patterns
GET /api/causal/patterns (requires auth)
```

### Immutable Audit Log
```bash
# Query log
GET /api/log/entries?subsystem=governance&limit=100

# Verify integrity
GET /api/log/verify
Response: {"valid": true, "entries_verified": 1234}
```

## 🔔 Alerting

### Built-in Alerts

**Self-Healing Alerts:**
- Component failures logged to `healing_actions`
- Query: `GET /api/health/status` → check `actions[]`

**Hunter Security Alerts:**
- Threat detection logged to `security_events`
- Query: `GET /api/hunter/alerts?status=open`

**Governance Approvals:**
- Pending approvals in `approval_requests`
- Query: `GET /api/governance/approvals`

### External Monitoring Integration

**Prometheus (Future):**
```python
# Add to backend/main.py
from prometheus_client import Counter, Histogram, generate_latest

requests_total = Counter('grace_requests_total', 'Total requests')
request_duration = Histogram('grace_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

**Datadog/New Relic:**
```python
# Add middleware
from ddtrace import tracer

app.add_middleware(DatadogMiddleware)
```

## 📈 Key Metrics to Monitor

### Performance
- **Request latency** - p50, p95, p99
- **Database query time** - Watch for slow queries
- **Reflection loop duration** - Should be <1s
- **Sandbox execution time** - Monitor timeouts

### Health
- **Component uptime** - From health_checks table
- **Healing success rate** - healing_actions results
- **Failed restarts** - Consecutive failures

### Security
- **Hunter alerts/hour** - Monitor spike in threats
- **Governance blocks** - Policy violations
- **Trust score distribution** - Track source quality
- **Verification failures** - Hash chain breaks

### Business
- **Active users** - Daily/weekly
- **Messages per user** - Engagement
- **Knowledge artifacts** - Growth rate
- **Auto-tasks created** - Autonomous activity

## 🚨 Alert Thresholds

### Critical (Immediate Action)
- System mode ≠ "normal"
- Component down >2 minutes
- Verification chain broken
- Critical Hunter alert
- Database connection lost

### Warning (Review Within 1 Hour)
- Reflection loop stale >5 minutes
- Healing action failed
- High Hunter alert
- Pending approvals >10

### Info (Daily Review)
- New knowledge ingested
- Meta-loop recommendations
- Trust score changes
- Model retrained

## 📊 Dashboard Queries

### Daily Health Report
```sql
SELECT component, COUNT(*) as checks, 
       SUM(CASE WHEN status='ok' THEN 1 ELSE 0 END) as ok_count
FROM health_checks 
WHERE created_at > datetime('now', '-24 hours')
GROUP BY component;
```

### Security Summary
```sql
SELECT severity, COUNT(*) as count, status
FROM security_events
WHERE created_at > datetime('now', '-7 days')
GROUP BY severity, status;
```

### Knowledge Growth
```sql
SELECT domain, COUNT(*) as artifacts,
       AVG(size_bytes) as avg_size
FROM knowledge_artifacts
GROUP BY domain;
```

## 🔍 Troubleshooting Queries

### Find Slow Operations
```sql
SELECT action, resource, AVG(duration_ms) as avg_duration
FROM sandbox_runs
GROUP BY action, resource
HAVING avg_duration > 5000
ORDER BY avg_duration DESC;
```

### Audit Trail for User
```sql
SELECT timestamp, actor, action, resource, result
FROM immutable_log
WHERE actor = 'username'
ORDER BY sequence DESC
LIMIT 50;
```

### Failed Healing Actions
```sql
SELECT component, action, result, detail
FROM healing_actions
WHERE result = 'failed'
ORDER BY created_at DESC;
```

## 🎯 Monitoring Checklist

**Daily:**
- [ ] Check health status endpoint
- [ ] Review Hunter alerts
- [ ] Check governance approvals
- [ ] Verify system mode is normal
- [ ] Review healing actions

**Weekly:**
- [ ] Verify log chain integrity
- [ ] Review meta-loop recommendations
- [ ] Check knowledge growth rate
- [ ] Analyze user patterns
- [ ] Review trust scores

**Monthly:**
- [ ] Performance benchmarks
- [ ] Security audit
- [ ] Backup verification
- [ ] Capacity planning
- [ ] Documentation updates

Grace provides complete observability out of the box! 📊✅
