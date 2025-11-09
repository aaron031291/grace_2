# GRACE Metrics & Telemetry Catalog

This catalog defines the first production-ready metric set for Grace’s autonomous
systems, along with the schemas used to publish, persist, and act on telemetry.
It is intentionally opinionated so collectors, proactive intelligence, and playbook
executors all speak the same language.

---

## 1. Metric Categories & Signals

Each metric entry defines:

| Field | Meaning |
| ----- | ------- |
| `metric_id` | Globally unique identifier (`category.metric`) |
| `source` | System producing the data (Prometheus, CloudWatch, internal service) |
| `resource_scope` | Logical entity being measured (service, queue, shard, subsystem) |
| `interval` | Recommended scrape/publish cadence |
| `unit` | Canonical unit for values |
| `aggregation` | How values are summarised over time (avg, p95, max, sum) |
| `thresholds` | [good, warning, critical] boundaries; used by planner & dashboards |
| `playbooks` | Actions or alerts tied to threshold breaches |

### 1.1 API & Gateway Health

| metric_id | Description | source | resource_scope | interval | unit | aggregation | thresholds (good / warn / critical) | playbooks |
| --------- | ----------- | ------ | --------------- | -------- | ---- | ----------- | ----------------------------------- | --------- |
| `api.latency_p95` | 95th percentile response latency for the public FastAPI gateway | Prometheus `histogram_quantile` | `service` (e.g. `grace-api`) | 60s | milliseconds | p95 per scrape | `<350 / 350–500 / >500` | Warn: scale app shard; Critical: failover plan |
| `api.error_rate` | 5xx responses ÷ total requests | Prometheus `rate` | `service` | 60s | ratio (0–1) | avg | `<0.01 / 0.01–0.03 / >0.03` | Warn: restart workers; Critical: engage remediation |
| `api.request_rate` | Requests per second | Prometheus `rate` | `service` | 60s | req/s | avg | `<200 / 200–400 / >400` (per shard) | Warn: pre-scale; Critical: activate autoscaling playbook |
| `api.saturation` | Gunicorn/Uvicorn worker saturation | Prometheus | `service` | 60s | percent | max | `<70 / 70–85 / >85` | Warn: spawn extra workers; Critical: shed load |

### 1.2 Background Execution & Queues

| metric_id | Description | source | resource_scope | interval | unit | aggregation | thresholds | playbooks |
| --------- | ----------- | ------ | --------------- | -------- | ---- | ----------- | ---------- | --------- |
| `executor.queue_depth` | Pending tasks in `execution_tasks` | Internal SQL collector | `queue` | 30s | count | max | `<25 / 25–75 / >75` | Warn: scale workers; Critical: spawn emergency shard |
| `executor.task_latency` | Age of oldest queued task | Internal SQL | `queue` | 30s | seconds | max | `<60 / 60–180 / >180` | Warn: increase workers; Critical: escalate to human |
| `executor.worker_utilization` | Active workers ÷ total workers | Internal telemetry | `worker_pool` | 30s | percent | avg | `<70 / 70–90 / >90` | Warn: spawn additional worker; Critical: block new submissions |

### 1.3 Learning & Ingestion Pipeline

| metric_id | Description | source | resource_scope | interval | unit | aggregation | thresholds | playbooks |
| --------- | ----------- | ------ | --------------- | -------- | ---- | ----------- | ---------- | --------- |
| `learning.sessions_started` | Learning sessions kicked off | Web Learning Orchestrator | `subsystem` (`web_learning`) | 5m | count | sum | `<3 / 3–6 / >6` per 5m | Warn: throttle if high; Critical: review governance load |
| `learning.sources_verified` | Percentage of learned sources passing governance/constitutional checks | Provenance tracker | `subsystem` | 5m | percent | avg | `>85 / 70–85 / <70` | Warn: run trust analysis; Critical: stop ingestion cycle |
| `learning.sandbox_pass_rate` | Sandbox applications that pass tests | Knowledge sandbox | `subsystem` | 5m | percent | avg | `>80 / 60–80 / <60` | Warn: re-run with stricter policies; Critical: disable auto-application |
| `learning.governance_blocks` | Count of ingestion attempts blocked by governance | Governance framework | `subsystem` | 5m | count | sum | `<2 / 2–5 / >5` | Warn: audit rules; Critical: require human review |

### 1.4 Autonomy & Decision Quality

| metric_id | Description | source | resource_scope | interval | unit | aggregation | thresholds | playbooks |
| --------- | ----------- | ------ | --------------- | -------- | ---- | ----------- | ---------- | --------- |
| `autonomy.plan_success_rate` | Percentage of recovery plans completing without rollback | Agentic spine | `subsystem` (`agentic_spine`) | 5m | percent | avg | `>90 / 75–90 / <75` | Warn: tighten guardrails; Critical: downgrade autonomy tier |
| `autonomy.approvals_pending` | High-risk actions awaiting approval | Governance engine | `subsystem` | 1m | count | max | `<3 / 3–7 / >7` | Warn: notify reviewers; Critical: pause new high-risk plans |
| `autonomy.autonomy_ratio` | Actions executed autonomously ÷ total actions | Agentic spine | `subsystem` | 10m | percent | avg | Target 70–85; `<60` triggers capability review, `>90` triggers trust check | Review thresholds |
| `autonomy.rollback_rate` | Plans rolled back after execution | Agentic spine | `subsystem` | 5m | percent | avg | `<5 / 5–10 / >10` | Warn: run post-mortem; Critical: lock planner to supervised mode |

### 1.5 Infrastructure & Host Health

| metric_id | Description | source | resource_scope | interval | unit | aggregation | thresholds | playbooks |
| --------- | ----------- | ------ | --------------- | -------- | ---- | ----------- | ---------- | --------- |
| `infra.cpu_utilization` | CPU usage per host/shard | Prometheus / Cloud provider | `host` | 30s | percent | avg | `<70 / 70–85 / >85` | Warn: shift load; Critical: scale nodes |
| `infra.memory_utilization` | Memory usage per host/shard | Prometheus | `host` | 30s | percent | avg | `<75 / 75–90 / >90` | Warn: restart non-critical services; Critical: migrate workloads |
| `infra.disk_usage` | Disk utilisation for critical volumes | Prometheus | `volume` | 5m | percent | max | `<70 / 70–85 / >85` | Warn: cleanup tasks; Critical: trigger disk expansion |
| `infra.pod_ready_ratio` | Ready pods ÷ desired pods (k8s) | Kubernetes API | `service` | 30s | percent | avg | `>95 / 90–95 / <90` | Warn: reschedule pods; Critical: escalate to infra team |

---

## 2. Event & Persistence Schemas

### 2.1 `MetricEvent`

Used by collectors when publishing into the trigger mesh.

```jsonc
{
  "event_type": "metrics.api.latency_p95",      // event type MUST be `metrics.{metric_id}`
  "source": "prometheus",                       // collector identifier
  "actor": "metrics_collector",                 // service account
  "resource": {
    "scope": "service",
    "id": "grace-api"
  },
  "payload": {
    "metric_id": "api.latency_p95",
    "value": 412.5,
    "unit": "ms",
    "aggregation": "p95",
    "interval_seconds": 60,
    "observed_at": "2025-11-09T14:03:00Z",
    "thresholds": {
      "good": "<350",
      "warning": "350-500",
      "critical": ">500"
    },
    "computed_band": "warning",
    "trend": "increasing",                      // optional: increasing|decreasing|steady
    "annotations": {
      "prometheus_query": "histogram_quantile(0.95, ...)"
    }
  },
  "timestamp": "2025-11-09T14:03:02Z"
}
```

Validation rules:

| Field | Type | Notes |
| ----- | ---- | ----- |
| `payload.metric_id` | string | Must match catalog entry |
| `payload.value` | number | Raw numeric value |
| `payload.unit` | enum | `ms`, `percent`, `ratio`, `count`, `req_per_sec`, `seconds` |
| `payload.computed_band` | enum | `good`, `warning`, `critical` |
| `payload.trend` | enum | optional, default `steady` |

### 2.2 `MetricsSnapshot`

Periodic aggregation stored for dashboards or anomaly detection.

```jsonc
{
  "snapshot_id": "grace-api:2025-11-09T14:05:00Z:api.latency_p95",
  "metric_id": "api.latency_p95",
  "resource_scope": "service",
  "resource_id": "grace-api",
  "window_start": "2025-11-09T14:00:00Z",
  "window_end": "2025-11-09T14:05:00Z",
  "stats": {
    "min": 280.5,
    "max": 612.0,
    "avg": 410.2,
    "p95": 498.3,
    "sample_count": 5
  },
  "bands": {
    "good_samples": 3,
    "warning_samples": 1,
    "critical_samples": 1
  },
  "latest_band": "critical",
  "derived_actions": [
    {
      "action_type": "playbook_recommendation",
      "playbook_id": "scale-api-shard",
      "confidence": 0.8
    }
  ],
  "created_at": "2025-11-09T14:05:02Z"
}
```

Recommended persistence table (`metrics_snapshots`):

| Column | Type | Notes |
| ------ | ---- | ----- |
| `snapshot_id` | TEXT PK | deterministic ID as above |
| `metric_id` | TEXT | FK to catalog |
| `resource_scope` | TEXT | `service`, `queue`, `host`, etc. |
| `resource_id` | TEXT | identifier of measured entity |
| `window_start`, `window_end` | TIMESTAMP | aggregation window |
| `stats` | JSON | aggregate statistics |
| `bands` | JSON | counts per band |
| `latest_band` | TEXT | `good|warning|critical` |
| `derived_actions` | JSON | optional recommended actions |
| `created_at` | TIMESTAMP | insertion time |

### 2.3 Catalog Reference Schema (YAML / JSON)

The catalog can be stored in a YAML file (`config/metrics_catalog.yaml`) mirroring the tables above:

```yaml
metrics:
  - metric_id: api.latency_p95
    category: api
    description: "95th percentile FastAPI latency"
    unit: ms
    aggregation: p95
    thresholds:
      good: { upper: 350 }
      warning: { lower: 350, upper: 500 }
      critical: { lower: 500 }
    playbooks:
      - scale-api-shard
      - failover-gateway
    recommended_interval_seconds: 60
    source: prometheus
    resource_scope: service
    tags: [production, customer-facing]
```

Collectors should fetch this catalog at startup to ensure metric IDs, units, and thresholds remain in sync with the central definition.

---

## 3. Implementation Guidance

1. **Catalog First** – record agreed metrics in `config/metrics_catalog.yaml` using the schema above. Update the proactive intelligence thresholds in `config/agentic_config.yaml` to match these values.
2. **Collector Development** – implement collectors (Prometheus, CloudWatch, custom SQL) that emit `MetricEvent` objects. Each collector should:
   - Load metric definitions (queries, thresholds) from the catalog.
   - Normalise values to canonical units.
   - Compute the band (`good|warning|critical`) before publishing to the trigger mesh.
3. **Proactive Intelligence** – update the proactive intelligence service to subscribe to `metrics.*` events, maintain rolling windows, emit `MetricsSnapshot` records, and hand off to the planner when thresholds are breached.
4. **Playbook Binding** – ensure playbooks referenced in the catalog exist (e.g. `scale-api-shard`, `spawn-executor-worker`) and include risk levels consistent with the thresholds.
5. **Dashboards and Alerts** – surface the snapshot data in the frontend dashboards and configure alerting (Slack/email) for critical bands.

With this catalog and schema in place, Grace can reason over live metrics, predict incidents, and execute governed responses using consistent data throughout the stack.

