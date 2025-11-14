# Dashboard API & Interaction Contract

## Overview
This document defines the complete API contract and user interaction flows for all four dashboard layers. Every endpoint includes exact request/response payloads and state flows.

---

## Layer 1: Operations Console

### 1.1 Get Kernel Status
**Endpoint**: `GET /api/telemetry/kernels/status`

**Request**: None (no parameters)

**Response**:
```json
{
  "total_kernels": 5,
  "active": 3,
  "idle": 2,
  "errors": 0,
  "avg_boot_time_ms": 1250.5,
  "kernels": [
    {
      "kernel_id": "kern-a1b2c3d4",
      "name": "ingestion-kernel-01",
      "status": "active",
      "boot_time_ms": 1200,
      "uptime_seconds": 3600,
      "last_heartbeat": "2025-11-14T10:30:15Z",
      "health": "healthy",
      "stress_score": 45,
      "task_count": 12,
      "error_count": 0
    }
  ]
}
```

**Field Definitions**:
- `status`: `"active" | "idle" | "booting" | "error"`
- `health`: `"healthy" | "degraded" | "unhealthy" | "unknown"`
- `stress_score`: 0-100 (percentage)
- `uptime_seconds`: Integer seconds since boot

---

### 1.2 Get Crypto Health
**Endpoint**: `GET /api/telemetry/crypto/health`

**Request**: None

**Response**:
```json
{
  "overall_health": "healthy",
  "signatures_validated": 1234,
  "signature_failures": 2,
  "key_rotation_due": false,
  "last_key_rotation": "2025-11-10T08:00:00Z",
  "encrypted_items": 456,
  "components": {
    "signature_service": "healthy",
    "encryption_vault": "healthy",
    "key_manager": "degraded"
  }
}
```

**Field Definitions**:
- `overall_health`: `"healthy" | "degraded" | "unhealthy" | "unknown"`
- `key_rotation_due`: Boolean indicating if rotation needed
- `components`: Map of component names to health status

---

### 1.3 Get Ingestion Throughput
**Endpoint**: `GET /api/telemetry/ingestion/throughput`

**Query Parameters**:
- `hours` (optional, default: 24): Time window (1-168)

**Example Request**: `GET /api/telemetry/ingestion/throughput?hours=24`

**Response**:
```json
{
  "time_window_hours": 24,
  "total_jobs": 150,
  "total_mb": 2048.75,
  "avg_duration_seconds": 12.5,
  "max_duration_seconds": 45.2,
  "throughput_mb_per_hour": 85.36
}
```

---

### 1.4 Control Kernel (USER INTERACTION)
**Endpoint**: `POST /api/telemetry/kernels/{kernel_id}/control`

**Query Parameters**:
- `action`: `"start" | "stop" | "restart" | "stress"`

**Example Request**: `POST /api/telemetry/kernels/kern-a1b2c3d4/control?action=restart`

**Response**:
```json
{
  "kernel_id": "kern-a1b2c3d4",
  "action": "restart",
  "status": "success"
}
```

**Backend Flow**:
1. Validate kernel_id exists
2. Validate action is allowed for current kernel state
3. Execute action:
   - `start`: Boot kernel, initialize resources, set status to "booting"
   - `stop`: Graceful shutdown, flush tasks, set status to "idle"
   - `restart`: Stop + Start sequence
   - `stress`: Trigger stress test, inject load, monitor metrics
4. Return success/failure
5. Broadcast status update via WebSocket

**Error Response** (400/404/500):
```json
{
  "detail": "Kernel not found",
  "kernel_id": "kern-a1b2c3d4"
}
```

**UI States**:
- Before: Button enabled with action icon
- During: Button disabled, show spinner
- Success: Update kernel status in table, show success toast
- Error: Show error toast, re-enable button

---

### 1.5 Get Kernel Logs
**Endpoint**: `GET /api/telemetry/kernels/{kernel_id}/logs`

**Query Parameters**:
- `lines` (optional, default: 100): Number of recent lines (1-1000)

**Example Request**: `GET /api/telemetry/kernels/kern-a1b2c3d4/logs?lines=50`

**Response**:
```json
{
  "kernel_id": "kern-a1b2c3d4",
  "logs": [
    "2025-11-14 10:30:15 [INFO] Kernel booted successfully",
    "2025-11-14 10:30:16 [INFO] Processing task task-xyz123",
    "2025-11-14 10:30:20 [WARN] High memory usage detected"
  ]
}
```

**UI Display**: Modal with scrollable log viewer, auto-scroll to bottom, refresh every 3s

---

## Layer 2: HTM Console

### 2.1 Get HTM Queue Status
**Endpoint**: `GET /api/telemetry/htm/queue`

**Request**: None

**Response**:
```json
{
  "queue_depth": 25,
  "pending_tasks": 15,
  "active_tasks": 10,
  "completed_today": 145,
  "failed_today": 3,
  "avg_wait_time_seconds": 45.2,
  "p95_duration_seconds": 120.5,
  "avg_task_size_mb": 12.8,
  "sla_breaches": 2,
  "tasks": []
}
```

**Field Definitions**:
- `queue_depth`: Total tasks in queue (pending + active)
- `avg_wait_time_seconds`: Average time from creation to start
- `p95_duration_seconds`: 95th percentile task duration
- `sla_breaches`: Count of tasks exceeding SLA threshold

---

### 2.2 Get HTM Tasks (with filters)
**Endpoint**: `GET /api/telemetry/htm/tasks`

**Query Parameters**:
- `origin` (optional): `"filesystem" | "remote" | "hunter"`
- `status` (optional): `"pending" | "active" | "completed" | "failed"`
- `limit` (optional, default: 50): Max results (1-500)

**Example Request**: `GET /api/telemetry/htm/tasks?origin=filesystem&status=active&limit=20`

**Response**:
```json
{
  "total": 8,
  "tasks": [
    {
      "task_id": "task-xyz123",
      "origin": "filesystem",
      "status": "active",
      "size_mb": 15.5,
      "duration_seconds": 32.1,
      "priority": "high",
      "created_at": "2025-11-14T10:25:00Z",
      "completed_at": null
    },
    {
      "task_id": "task-abc456",
      "origin": "remote",
      "status": "completed",
      "size_mb": 8.2,
      "duration_seconds": 18.5,
      "priority": "normal",
      "created_at": "2025-11-14T10:20:00Z",
      "completed_at": "2025-11-14T10:20:18Z"
    }
  ]
}
```

**Field Definitions**:
- `origin`: Source of task (`filesystem`, `remote`, `hunter`)
- `status`: Current state (`pending`, `active`, `completed`, `failed`)
- `priority`: Task priority (`low`, `normal`, `high`, `critical`)
- `duration_seconds`: Time from start to completion (null if not completed)

---

### 2.3 Get Workload Perception
**Endpoint**: `GET /api/telemetry/htm/workload`

**Request**: None

**Response**:
```json
{
  "active_agents": 7,
  "auto_escalations_today": 12,
  "capacity_utilization_percent": 70,
  "workload_status": "normal"
}
```

**Field Definitions**:
- `workload_status`: `"normal" | "high" | "critical"`
- `capacity_utilization_percent`: 0-100 (based on agent capacity)

---

### 2.4 Override HTM Task Priority (USER INTERACTION)
**Endpoint**: `POST /api/telemetry/htm/tasks/{task_id}/priority`

**Request Body**:
```json
{
  "priority": "critical",
  "reason": "User manual override"
}
```

**Response**:
```json
{
  "task_id": "task-xyz123",
  "old_priority": "normal",
  "new_priority": "critical",
  "status": "updated"
}
```

**Backend Flow**:
1. Validate task exists and is in `pending` or `active` state
2. Update task priority in database
3. Re-sort queue if task is pending
4. Create audit log entry
5. Broadcast queue update via WebSocket

**UI States**:
- Trigger: Right-click task → "Change Priority"
- Modal: Select new priority + reason text box
- Submit: Disable form, show spinner
- Success: Update task row, show toast
- Error: Show error message, re-enable form

---

## Layer 3: Intent & Learning

### 3.1 Get Active Intents
**Endpoint**: `GET /api/telemetry/intent/active`

**Request**: None

**Response**:
```json
{
  "total": 3,
  "intents": [
    {
      "intent_id": "int-abc123",
      "goal": "Analyze Q4 financial data and generate insights",
      "status": "active",
      "completion_percent": 65,
      "created_at": "2025-11-14T08:00:00Z",
      "htm_tasks_generated": 12,
      "estimated_completion": "2025-11-14T12:00:00Z"
    }
  ]
}
```

**Field Definitions**:
- `status`: `"pending" | "active" | "completed" | "failed"`
- `completion_percent`: 0-100 (progress toward goal)
- `htm_tasks_generated`: Count of HTM tasks spawned from this intent

---

### 3.2 Get Intent Details (with linked HTM tasks)
**Endpoint**: `GET /api/telemetry/intent/{intent_id}/details`

**Request**: `GET /api/telemetry/intent/int-abc123/details`

**Response**:
```json
{
  "intent_id": "int-abc123",
  "goal": "Analyze Q4 financial data and generate insights",
  "status": "active",
  "completion_percent": 65,
  "created_at": "2025-11-14T08:00:00Z",
  "htm_tasks": [
    {
      "task_id": "task-xyz123",
      "description": "Ingest financial spreadsheet",
      "status": "completed"
    },
    {
      "task_id": "task-xyz124",
      "description": "Extract data patterns",
      "status": "active"
    }
  ],
  "insights": [
    "Revenue increased 15% quarter-over-quarter",
    "Operating expenses reduced by 8%"
  ]
}
```

**UI Display**: Expandable intent card or detail modal showing linked tasks

---

### 3.3 Get Learning Retrospectives
**Endpoint**: `GET /api/telemetry/learning/retrospectives`

**Query Parameters**:
- `limit` (optional, default: 20): Max results (1-100)

**Response**:
```json
{
  "total": 15,
  "retrospectives": [
    {
      "id": "retro-abc123",
      "cycle_name": "Learning Cycle #47",
      "insights": [
        "Pattern matching improved by 12%",
        "Error rate decreased after validation update"
      ],
      "improvements": [
        "Added input sanitization layer",
        "Optimized query performance"
      ],
      "timestamp": "2025-11-14T09:00:00Z"
    }
  ]
}
```

---

### 3.4 Get Playbook Success Rates
**Endpoint**: `GET /api/telemetry/learning/playbooks`

**Request**: None

**Response**:
```json
{
  "playbooks": [
    {
      "playbook_name": "data-ingestion-standard",
      "total_runs": 145,
      "success_rate_percent": 94.5
    },
    {
      "playbook_name": "error-recovery-auto",
      "total_runs": 67,
      "success_rate_percent": 89.2
    }
  ]
}
```

**Field Definitions**:
- `success_rate_percent`: (successful_runs / total_runs) * 100

---

### 3.5 Get Policy Suggestions
**Endpoint**: `GET /api/telemetry/learning/policy_suggestions`

**Request**: None

**Response**:
```json
{
  "suggestions": [
    {
      "suggestion_id": "pol-abc123",
      "policy_area": "security",
      "suggestion": "Implement rate limiting on API endpoints",
      "confidence": 0.87,
      "supporting_evidence": [
        "Detected 15 potential abuse patterns in last 7 days",
        "Similar systems reduced incidents by 45% with rate limiting"
      ],
      "created_at": "2025-11-14T10:00:00Z"
    }
  ]
}
```

**Field Definitions**:
- `confidence`: 0.0-1.0 (AI confidence score)
- `policy_area`: Category (`"security"`, `"performance"`, `"reliability"`, `"cost"`)

---

### 3.6 Respond to Policy Suggestion (USER INTERACTION)
**Endpoint**: `POST /api/telemetry/learning/policy_suggestions/{suggestion_id}/respond`

**Request Body**:
```json
{
  "action": "accept",
  "notes": "Agreed, will implement in Sprint 12"
}
```

**Actions**: `"accept" | "review" | "reject"`

**Response**:
```json
{
  "suggestion_id": "pol-abc123",
  "action": "accept",
  "status": "processed",
  "next_steps": [
    "Create implementation ticket",
    "Schedule review in 2 weeks"
  ]
}
```

**Backend Flow**:
1. Validate suggestion exists and is `pending`
2. Update suggestion status to action
3. If `accept`: Create implementation task in backlog
4. If `review`: Schedule follow-up review
5. If `reject`: Log reason, close suggestion
6. Update AI learning model with feedback
7. Return next steps

**UI States**:
- Buttons: Accept (green), Review (blue), Reject (red)
- Click: Show confirmation modal with notes field
- Submit: Disable buttons, show spinner
- Success: Remove card from list, show toast
- Error: Show error, re-enable buttons

---

## Layer 4: Dev/OS View

### 4.1 Get Secrets Status
**Endpoint**: `GET /api/telemetry/secrets/status`

**Request**: None

**Response**:
```json
{
  "total_secrets": 15,
  "encrypted": 15,
  "vault_health": "healthy"
}
```

**Field Definitions**:
- `vault_health`: `"healthy" | "degraded" | "unhealthy"`
- All secrets should be encrypted; `encrypted < total_secrets` indicates degraded health

---

### 4.2 Store Secret (USER INTERACTION)
**Endpoint**: `POST /api/secrets/store`

**Request Body**:
```json
{
  "name": "OPENAI_API_KEY",
  "value": "sk-abc123...",
  "category": "api_key",
  "consent_given": true
}
```

**Categories**: `"api_key" | "password" | "token" | "certificate"`

**Response**:
```json
{
  "secret_id": "sec-xyz789",
  "name": "OPENAI_API_KEY",
  "category": "api_key",
  "encrypted": true,
  "stored_at": "2025-11-14T10:35:00Z",
  "status": "success"
}
```

**Backend Flow**:
1. Validate consent_given is `true`
2. Check for duplicate secret name
3. Encrypt value using AES-256
4. Store in SecretVault table
5. Create audit log entry (user, timestamp, action)
6. Return success (never return the actual secret value)

**UI Flow**:
1. User clicks "+ Add Secret"
2. Modal opens with form (name, value, category)
3. User fills form, clicks "Save Secret"
4. Consent modal appears with encryption details
5. User clicks "Yes, I Consent"
6. API call to store secret
7. Success: Close modals, refresh vault status, show toast
8. Error: Show error message, keep modal open

**Error Responses**:
```json
// 400 - Consent not given
{
  "detail": "Consent required to store secret",
  "code": "CONSENT_REQUIRED"
}

// 409 - Duplicate name
{
  "detail": "Secret with this name already exists",
  "code": "DUPLICATE_SECRET"
}
```

---

### 4.3 Get Pending Recordings
**Endpoint**: `GET /api/telemetry/recordings/pending`

**Request**: None

**Response**:
```json
{
  "total": 3,
  "recordings": [
    {
      "recording_id": "rec-abc123",
      "type": "voice",
      "filename": "meeting_2025-11-14.mp3",
      "size_mb": 45.2,
      "created_at": "2025-11-14T09:00:00Z"
    },
    {
      "recording_id": "rec-def456",
      "type": "screen",
      "filename": "demo_capture.mp4",
      "size_mb": 128.5,
      "created_at": "2025-11-14T08:30:00Z"
    }
  ]
}
```

**Field Definitions**:
- `type`: `"voice" | "screen" | "video"`

---

### 4.4 Trigger Recording Ingestion (USER INTERACTION)
**Endpoint**: `POST /api/recording/ingest/{recording_id}`

**Request**: `POST /api/recording/ingest/rec-abc123`

**Response**:
```json
{
  "recording_id": "rec-abc123",
  "ingestion_job_id": "job-xyz789",
  "status": "started",
  "estimated_duration_minutes": 15
}
```

**Backend Flow**:
1. Validate recording exists and status is `pending`
2. Create ingestion job in queue
3. Update recording status to `processing`
4. Start async task:
   - Transcribe audio (if voice/video)
   - Extract frames (if video)
   - Index content for search
   - Generate summary/tags
5. On completion: Update status to `completed`, send notification
6. On error: Update status to `failed`, log error

**UI States**:
- Button: "Ingest" (enabled for pending recordings)
- Click: Confirm modal "Start ingestion for {filename}?"
- Submit: Disable button, show "Processing..." badge
- Success: Update row status, show toast
- Error: Re-enable button, show error toast

**Job Status Endpoint**: `GET /api/recording/ingest/{job_id}/status`

**Response**:
```json
{
  "job_id": "job-xyz789",
  "recording_id": "rec-abc123",
  "status": "processing",
  "progress_percent": 45,
  "current_step": "transcription",
  "estimated_completion": "2025-11-14T10:45:00Z"
}
```

**Poll this endpoint every 5s to update UI progress**

---

### 4.5 Get Remote Access Sessions
**Endpoint**: `GET /api/telemetry/remote_access/sessions`

**Query Parameters**:
- `active_only` (optional, default: true): Show only active sessions

**Response**:
```json
{
  "total": 5,
  "sessions": [
    {
      "session_id": "sess-abc123",
      "user": "admin@grace.ai",
      "status": "active",
      "started_at": "2025-11-14T10:00:00Z",
      "ended_at": null,
      "duration_minutes": 35
    },
    {
      "session_id": "sess-def456",
      "user": "dev@grace.ai",
      "status": "ended",
      "started_at": "2025-11-14T08:00:00Z",
      "ended_at": "2025-11-14T09:15:00Z",
      "duration_minutes": 75
    }
  ]
}
```

**Field Definitions**:
- `status`: `"active" | "ended" | "terminated"`
- `duration_minutes`: Calculated from start/end times

---

### 4.6 Get Deployment Status
**Endpoint**: `GET /api/telemetry/deployment/status`

**Request**: None

**Response**:
```json
{
  "last_deployment": "2025-11-14T06:00:00Z",
  "environment": "production",
  "version": "4.2.1",
  "health_check": "passing",
  "pending_tests": 0,
  "build_info": {
    "commit_sha": "a1b2c3d4",
    "branch": "main",
    "deployed_by": "ci-bot"
  }
}
```

**Field Definitions**:
- `health_check`: `"passing" | "failing" | "unknown"`
- `environment`: `"development" | "staging" | "production"`

---

### 4.7 Run Stress Test (USER INTERACTION)
**Endpoint**: `POST /api/stress/run`

**Request Body**:
```json
{
  "test_type": "full_system",
  "duration_minutes": 10,
  "intensity": "medium"
}
```

**Test Types**: `"kernel_only" | "htm_queue" | "full_system"`
**Intensity**: `"low" | "medium" | "high" | "extreme"`

**Response**:
```json
{
  "stress_test_id": "stress-abc123",
  "status": "running",
  "started_at": "2025-11-14T10:40:00Z",
  "estimated_completion": "2025-11-14T10:50:00Z"
}
```

**Backend Flow**:
1. Validate no other stress test is currently running
2. Create stress test record
3. Start async stress test:
   - Inject synthetic load (tasks, requests, data)
   - Monitor system metrics (CPU, memory, queue depth)
   - Record stress scores and bottlenecks
4. On completion: Generate report, update dashboard metrics
5. Return test ID for polling

**Status Poll**: `GET /api/stress/{stress_test_id}/status`

**Response**:
```json
{
  "stress_test_id": "stress-abc123",
  "status": "completed",
  "duration_minutes": 10,
  "results": {
    "max_queue_depth": 145,
    "avg_response_time_ms": 235,
    "error_rate_percent": 0.5,
    "bottlenecks": ["database_connections", "memory_usage"]
  }
}
```

**UI Flow**:
1. Click "⚡ Run Stress Test"
2. Modal: Select test type, duration, intensity
3. Confirm: "This will simulate load on the system"
4. Start: Show progress modal with live metrics
5. Poll status every 5s, update progress
6. Complete: Show results modal with charts
7. Error: Show error, allow retry

---

## WebSocket Real-Time Updates

### WebSocket Connection
**Endpoint**: `ws://localhost:8000/ws/telemetry`

**Connection Flow**:
1. Client connects to WebSocket
2. Server sends initial state immediately
3. Server broadcasts updates every 2 seconds
4. Client sends "ping" heartbeat every 30s
5. Server responds with `{"type": "pong"}`

**Broadcast Message Format**:
```json
{
  "timestamp": "2025-11-14T10:40:15Z",
  "kernels": {
    "total": 5,
    "active": 3,
    "idle": 2,
    "errors": 0
  },
  "htm": {
    "queue_depth": 25,
    "pending": 15,
    "active": 10
  },
  "crypto": {
    "status": "healthy",
    "signatures_validated": 1234,
    "signature_failures": 2
  }
}
```

**Client Usage**:
```typescript
const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboardMetrics(data);
};

// Heartbeat
setInterval(() => {
  ws.send('ping');
}, 30000);
```

---

## Summary: User Interactions & Backend Flows

| **Action** | **Endpoint** | **Flow** | **UI Feedback** |
|------------|--------------|----------|-----------------|
| Start/Stop Kernel | `POST /api/telemetry/kernels/{id}/control` | Validate → Execute → Broadcast | Button disabled → Toast → Status update |
| View Kernel Logs | `GET /api/telemetry/kernels/{id}/logs` | Fetch logs → Stream in modal | Modal opens → Auto-refresh every 3s |
| Override Task Priority | `POST /api/telemetry/htm/tasks/{id}/priority` | Validate → Update → Re-sort queue | Modal → Spinner → Row update |
| Accept Policy | `POST /api/telemetry/learning/policy_suggestions/{id}/respond` | Update status → Create task → Train AI | Buttons disabled → Card removed |
| Store Secret | `POST /api/secrets/store` | Consent check → Encrypt → Audit | Form → Consent modal → Toast |
| Ingest Recording | `POST /api/recording/ingest/{id}` | Create job → Async process → Notify | Button → Progress badge → Completion toast |
| Run Stress Test | `POST /api/stress/run` | Validate → Inject load → Report | Modal → Progress chart → Results modal |

---

## Next Steps for Designers

With these contracts, you can now:

1. **Design exact UI states** for each interaction (idle, loading, success, error)
2. **Create accurate wireframes** showing real data structures
3. **Plan animations/transitions** for state changes
4. **Design error states** with specific error messages
5. **Build prototypes** using mock data matching these payloads

All endpoints are production-ready and backend flows are documented for implementation.
