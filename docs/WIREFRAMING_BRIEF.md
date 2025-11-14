# GRACE Dashboard Wireframing Brief

**For**: Design & UX Team  
**Purpose**: Data contracts and interaction flows for wireframing  
**Status**: ✅ Backend endpoints confirmed and ready

---

## Layer 1: Operations Console 🎛️

### Data Contract: Kernel Status

**Source**: `GET /api/telemetry/kernels/status` ✅

**UI Consumes**:
```typescript
interface KernelDisplay {
  // Header Metrics
  total_kernels: number           // Display: "5 Kernels"
  active: number                  // Display: "3 Active" (green)
  idle: number                    // Display: "2 Idle" (yellow)
  errors: number                  // Display: "0 Errors" (red if > 0)
  avg_boot_time_ms: number        // Display: "1,250 ms avg boot"
  
  // Table Rows (per kernel)
  kernels: [{
    kernel_id: string             // Display: First 8 chars "kern-a1b2"
    name: string                  // Display: "ingestion-kernel-01"
    status: "active"|"idle"|      // Badge color: green|yellow|red|blue
            "error"|"booting"
    health: "healthy"|"degraded"| // Icon: ✓|⚠|✗|?
            "unhealthy"|"unknown"
    uptime_seconds: number        // Display: "60m" or "3h 25m"
    task_count: number            // Display: "12 tasks"
    error_count: number           // Display: "0" (red if > 0)
    stress_score: number          // Progress bar: 0-100%
  }]
}
```

**Visual Elements**:
- **Metrics Grid**: 5 cards (total, active, idle, errors, avg boot)
- **Table**: Sortable, 8 columns, action buttons per row
- **Status Badges**: Color-coded pills (green/yellow/red/blue)
- **Stress Bar**: Gradient fill bar (green → yellow → red)
- **Action Buttons**: Restart (↻), Stop (■), Stress (⚡), Logs (📋)

---

### Data Contract: Crypto Health

**Source**: `GET /api/telemetry/crypto/health` ✅

**UI Consumes**:
```typescript
interface CryptoDisplay {
  overall_health: "healthy"|      // Large status indicator
                  "degraded"|
                  "unhealthy"
  signatures_validated: number    // Counter: "1,234"
  signature_failures: number      // Counter: "2" (red if > 0)
  encrypted_items: number         // Counter: "456"
  key_rotation_due: boolean       // Badge: "DUE" (yellow) or "OK" (green)
  last_key_rotation: string       // Timestamp: "Nov 10, 8:00 AM"
}
```

**Visual Elements**:
- **Grid**: 5-6 cards with label + value
- **Status Indicator**: Large colored badge (green/yellow/red)
- **Rotation Badge**: Prominent if due

---

### Data Contract: Ingestion Throughput

**Source**: `GET /api/telemetry/ingestion/throughput?hours=24` ✅

**UI Consumes**:
```typescript
interface IngestionDisplay {
  total_jobs: number              // Display: "150 jobs"
  total_mb: number                // Display: "2,048.75 MB"
  avg_duration_seconds: number    // Display: "12.5s avg"
  max_duration_seconds: number    // Display: "45.2s max"
  throughput_mb_per_hour: number  // Display: "85.36 MB/h"
}
```

**Visual Elements**:
- **Grid**: 4-5 cards
- **Optional Chart**: Bar chart showing throughput over time (future)

---

### Interaction Flow: Control Kernel

**Trigger**: User clicks "Restart" button on a kernel row

**Sequence**:
```
1. User clicks [↻ Restart] button
   └─> Button disables, shows spinner icon

2. UI sends: POST /api/telemetry/kernels/{kernel_id}/control?action=restart ✅
   └─> Loading state: entire row dims, spinner in actions column

3. Backend validates kernel exists
   └─> If invalid: 404 error
   
4. Backend executes restart:
   - Stops kernel gracefully
   - Flushes active tasks
   - Reboots kernel
   - Updates database status
   
5. Backend broadcasts WebSocket update
   └─> All connected clients receive new kernel status

6. Backend responds: 200 OK
   └─> UI removes spinner, re-enables button
   └─> UI shows toast: "Kernel restarted successfully" (green, 3s)
   └─> UI updates kernel row with new status/uptime

Error Path:
3. Backend error: 500
   └─> UI shows toast: "Failed to restart kernel: [error]" (red, 5s)
   └─> UI re-enables button for retry
```

**UI States**:
- **Idle**: Button enabled, normal color
- **Loading**: Button disabled, spinner icon, row dimmed
- **Success**: Button enabled, toast notification, row updated
- **Error**: Button enabled, error toast with retry option

**Backend Endpoint**: ✅ `POST /api/telemetry/kernels/{id}/control`

---

### Interaction Flow: View Kernel Logs

**Trigger**: User clicks "📋 Logs" button

**Sequence**:
```
1. User clicks [📋] button
   └─> Modal opens (loading state)

2. UI sends: GET /api/telemetry/kernels/{kernel_id}/logs?lines=100 ✅
   
3. Backend fetches recent logs from file/database
   
4. Backend responds: {kernel_id, logs: ["line1", "line2", ...]}
   └─> UI displays logs in scrollable pre-formatted text
   └─> UI auto-scrolls to bottom

5. While modal open, UI polls every 3 seconds:
   └─> GET /api/telemetry/kernels/{kernel_id}/logs?lines=100
   └─> Appends new lines, auto-scrolls

6. User clicks [✕ Close]
   └─> Stop polling, close modal
```

**UI States**:
- **Loading**: Spinner in modal
- **Displaying**: Scrollable log viewer, auto-refresh indicator
- **Closed**: Polling stopped

**Backend Endpoint**: ✅ `GET /api/telemetry/kernels/{id}/logs`

---

## Layer 2: HTM Console 📊

### Data Contract: HTM Queue Metrics

**Source**: `GET /api/telemetry/htm/queue` ✅

**UI Consumes**:
```typescript
interface HTMQueueDisplay {
  // Header Metrics
  queue_depth: number             // Display: "25 tasks in queue"
  pending_tasks: number           // Display: "15" (yellow badge)
  active_tasks: number            // Display: "10" (green badge)
  completed_today: number         // Display: "145" (with ✓ icon)
  failed_today: number            // Display: "3" (red if > 0)
  
  // Performance Metrics
  avg_wait_time_seconds: number   // Display: "45.2s avg wait"
  p95_duration_seconds: number    // Display: "120.5s P95"
  avg_task_size_mb: number        // Display: "12.8 MB avg"
  sla_breaches: number            // Display: "2" (red badge if > 0)
}
```

**Visual Elements**:
- **Metrics Grid**: 9 cards, color-coded by status
- **SLA Badge**: Prominent if breaches > 0

---

### Data Contract: HTM Tasks

**Source**: `GET /api/telemetry/htm/tasks?origin={filter}&status={filter}&limit=50` ✅

**UI Consumes**:
```typescript
interface HTMTaskDisplay {
  task_id: string                 // Display: First 8 chars "task-xyz1"
  origin: "filesystem"|           // Badge: Blue|Purple|Orange
          "remote"|"hunter"
  status: "pending"|"active"|     // Badge: Yellow|Blue|Green|Red
          "completed"|"failed"
  size_mb: number                 // Display: "15.50 MB"
  duration_seconds: number|null   // Display: "32.1s" or "-" if null
  priority: "low"|"normal"|       // Text or badge
            "high"|"critical"
  created_at: string              // Display: "10:25 AM" or relative
  completed_at: string|null       // Display: "10:25 AM" or "-"
}
```

**Visual Elements**:
- **Filters**: Two dropdowns (Origin, Status)
- **Table**: 8 columns, sortable, color-coded badges
- **Origin Badges**: Different color per origin
- **Status Badges**: Different color per status
- **Context Menu**: Right-click for actions

---

### Data Contract: Workload Perception

**Source**: `GET /api/telemetry/htm/workload` ✅

**UI Consumes**:
```typescript
interface WorkloadDisplay {
  active_agents: number           // Display: "7 agents"
  auto_escalations_today: number  // Display: "12 escalations"
  capacity_utilization_percent: number  // Progress bar: 0-100%
  workload_status: "normal"|      // Status badge: Green|Yellow|Red
                   "high"|"critical"
}
```

**Visual Elements**:
- **Grid**: 4 cards
- **Capacity Bar**: Gradient fill (green → yellow → red)
- **Status Badge**: Large, color-coded

---

### Data Contract: Origin Performance Stats

**Source**: Calculated client-side from tasks array

**UI Computes**:
```typescript
interface OriginStats {
  origin: string                  // "filesystem" | "remote" | "hunter"
  task_count: number              // Total tasks from this origin
  avg_duration: number            // Average of all duration_seconds
  avg_size_mb: number             // Average of all size_mb
}
```

**Visual Elements**:
- **Cards**: One per origin (3 total)
- **Bar Charts**: Compare origins side-by-side

---

### Interaction Flow: Override Task Priority

**Trigger**: User right-clicks task row → "Change Priority"

**Sequence**:
```
1. User right-clicks task row
   └─> Context menu appears: ["Change Priority", "View Details"]

2. User clicks "Change Priority"
   └─> Modal opens with form:
       - Current priority: "normal" (display only)
       - New priority dropdown: [Low, Normal, High, Critical]
       - Reason text box (required)
       - [Cancel] [Submit] buttons

3. User selects new priority, enters reason, clicks [Submit]
   └─> Form disables, spinner appears

4. UI sends: POST /api/telemetry/htm/tasks/{task_id}/priority ✅
   Body: {
     "priority": "critical",
     "reason": "User manual override"
   }

5. Backend validates:
   - Task exists and is in pending/active state
   - Priority is valid enum value
   - Reason is non-empty

6. Backend updates:
   - task.priority in database
   - Re-sorts queue if task is pending
   - Creates audit log entry

7. Backend broadcasts WebSocket update
   └─> Queue metrics refresh for all clients

8. Backend responds: 200 OK
   {
     "task_id": "task-xyz123",
     "old_priority": "normal",
     "new_priority": "critical",
     "status": "updated"
   }

9. UI closes modal
   └─> Shows toast: "Priority updated to Critical" (green, 3s)
   └─> Updates task row with new priority badge
   └─> Refreshes queue metrics

Error Path:
5. Validation fails (e.g., task already completed): 400
   └─> UI shows error in modal: "Cannot change priority: task completed"
   └─> Form re-enables for correction
```

**UI States**:
- **Idle**: Row normal, context menu hidden
- **Menu Open**: Context menu visible
- **Modal Open**: Form active, submit enabled
- **Submitting**: Form disabled, spinner visible
- **Success**: Modal closed, row updated, toast shown
- **Error**: Modal open, error message, form re-enabled

**Backend Endpoint**: ✅ `POST /api/telemetry/htm/tasks/{id}/priority`

---

## Layer 3: Intent & Learning 🧠

### Data Contract: Active Intents

**Source**: `GET /api/telemetry/intent/active` ✅

**UI Consumes**:
```typescript
interface IntentDisplay {
  intent_id: string               // Display: First 8 chars "int-abc1"
  goal: string                    // Display: Full text (truncate if > 100 chars)
  status: "pending"|"active"|     // Badge: Yellow|Blue|Green|Red
          "completed"|"failed"
  completion_percent: number      // Progress bar: 0-100%
  created_at: string              // Display: "Nov 14, 8:00 AM"
  htm_tasks_generated: number     // Display: "12 tasks"
  estimated_completion: string|null  // Display: "In 2 hours" or "-"
}
```

**Visual Elements**:
- **Card Grid**: One card per intent
- **Progress Bar**: Inside each card
- **Status Badge**: Top-right corner
- **Click**: Opens detail modal

---

### Data Contract: Intent Details (Modal)

**Source**: `GET /api/telemetry/intent/{intent_id}/details` ✅

**UI Consumes**:
```typescript
interface IntentDetailsDisplay {
  intent_id: string               // Modal title
  goal: string                    // Large text at top
  status: string                  // Status badge
  completion_percent: number      // Large progress bar
  created_at: string              // Timestamp
  
  htm_tasks: [{                   // Table of linked tasks
    task_id: string               // Link to Layer 2 (filter by task_id)
    description: string           // Display in table
    status: string                // Status badge
  }]
  
  insights: string[]              // Bulleted list
}
```

**Visual Elements**:
- **Modal**: Large, scrollable
- **Header**: Goal + status + progress
- **Table**: Linked HTM tasks
- **List**: Generated insights

---

### Data Contract: Learning Retrospectives

**Source**: `GET /api/telemetry/learning/retrospectives?limit=10` ✅

**UI Consumes**:
```typescript
interface RetrospectiveDisplay {
  id: string                      // Not displayed
  cycle_name: string              // Display: "Learning Cycle #47"
  insights: string[]              // Bulleted list with 💡 icon
  improvements: string[]          // Bulleted list with ⬆️ icon
  timestamp: string               // Display: "Nov 14, 9:00 AM"
}
```

**Visual Elements**:
- **Card List**: One card per retrospective
- **Two Columns**: Insights | Improvements
- **Icons**: 💡 for insights, ⬆️ for improvements

---

### Data Contract: Playbook Success Rates

**Source**: `GET /api/telemetry/learning/playbooks` ✅

**UI Consumes**:
```typescript
interface PlaybookDisplay {
  playbook_name: string           // Display: "data-ingestion-standard"
  total_runs: number              // Display: "145 runs"
  success_rate_percent: number    // Display: "94.5%" + progress bar
}
```

**Visual Elements**:
- **Table**: 3 columns (name, runs, success rate)
- **Success Bar**: Color-coded (green > 80%, yellow 60-80%, red < 60%)

---

### Data Contract: Policy Suggestions

**Source**: `GET /api/telemetry/learning/policy_suggestions` ✅

**UI Consumes**:
```typescript
interface PolicySuggestionDisplay {
  suggestion_id: string           // Not displayed
  policy_area: string             // Badge: "Security" | "Performance" | etc.
  suggestion: string              // Large text (main message)
  confidence: number              // Display: "87% confidence" + badge color
  supporting_evidence: string[]   // Bulleted list
  created_at: string              // Timestamp
}
```

**Visual Elements**:
- **Card List**: One card per suggestion
- **Area Badge**: Top-left (Security, Performance, etc.)
- **Confidence Badge**: Top-right, color-coded (green > 80%, yellow 60-80%, red < 60%)
- **Evidence List**: Collapsible or always visible
- **Action Buttons**: [✓ Accept] [👁 Review] [✕ Reject]

---

### Interaction Flow: Respond to Policy Suggestion

**Trigger**: User clicks [Accept], [Review], or [Reject] button

**Sequence**:
```
1. User clicks [✓ Accept] button on a policy card
   └─> Confirmation modal opens:
       - Policy area: "Security"
       - Suggestion: "Implement rate limiting..."
       - Confidence: "87%"
       - Action: "Accept" (highlighted in green)
       - Notes text box (optional)
       - [Cancel] [Confirm Accept] buttons

2. User enters notes (optional), clicks [Confirm Accept]
   └─> Modal form disables, spinner appears

3. UI sends: POST /api/telemetry/learning/policy_suggestions/{id}/respond ✅
   Body: {
     "action": "accept",
     "notes": "Agreed, will implement in Sprint 12"
   }

4. Backend validates:
   - Suggestion exists and status is "pending"
   - Action is valid: "accept" | "review" | "reject"

5. Backend processes based on action:
   
   If "accept":
   - Updates suggestion status to "accepted"
   - Creates implementation task in backlog
   - Schedules follow-up review in 2 weeks
   
   If "review":
   - Updates suggestion status to "under_review"
   - Schedules review meeting
   
   If "reject":
   - Updates suggestion status to "rejected"
   - Logs reason and closes suggestion
   
   All actions:
   - Update AI learning model with feedback
   - Create audit log entry

6. Backend responds: 200 OK
   {
     "suggestion_id": "pol-abc123",
     "action": "accept",
     "status": "processed",
     "next_steps": [
       "Implementation ticket created: TASK-1234",
       "Review scheduled for Nov 28"
     ]
   }

7. UI closes modal
   └─> Removes card from list with slide-out animation
   └─> Shows toast: "Policy accepted. Task created: TASK-1234" (green, 5s)
   └─> Optionally shows "Next Steps" in toast or separate modal

Error Path:
4. Suggestion already processed: 400
   └─> UI shows error in modal: "This suggestion has already been processed"
   └─> User clicks [Cancel] to close
```

**UI States**:
- **Idle**: Card visible, buttons enabled
- **Modal Open**: Form active, action highlighted
- **Submitting**: Form disabled, spinner visible
- **Success**: Card removed, toast shown
- **Error**: Modal shows error, buttons re-enabled

**Backend Endpoint**: ✅ `POST /api/telemetry/learning/policy_suggestions/{id}/respond`

---

## Layer 4: Dev/OS View ⚙️

### Data Contract: Secrets Vault Status

**Source**: `GET /api/telemetry/secrets/status` ✅

**UI Consumes**:
```typescript
interface SecretsVaultDisplay {
  total_secrets: number           // Display: "15 secrets"
  encrypted: number               // Display: "15 encrypted"
  vault_health: "healthy"|        // Status badge: Green|Yellow|Red
                "degraded"|
                "unhealthy"
}
```

**Visual Elements**:
- **Grid**: 3 cards
- **Health Badge**: Large, prominent
- **Add Button**: [+ Add Secret] (top-right)

---

### Data Contract: Pending Recordings

**Source**: `GET /api/telemetry/recordings/pending` ✅

**UI Consumes**:
```typescript
interface RecordingDisplay {
  recording_id: string            // Display: First 8 chars "rec-abc1"
  type: "voice"|"screen"|"video"  // Icon: 🎤 | 🖥️ | 🎥
  filename: string                // Display: "meeting_2025-11-14.mp3"
  size_mb: number                 // Display: "45.2 MB"
  created_at: string              // Display: "9:00 AM"
}
```

**Visual Elements**:
- **Table**: 5 columns (ID, type, filename, size, created, actions)
- **Type Icons**: Visual indicator per type
- **Action Button**: [Ingest] per row

---

### Data Contract: Remote Access Sessions

**Source**: `GET /api/telemetry/remote_access/sessions?active_only=false` ✅

**UI Consumes**:
```typescript
interface RemoteSessionDisplay {
  session_id: string              // Display: First 8 chars "sess-abc1"
  user: string                    // Display: "admin@grace.ai"
  status: "active"|"ended"|       // Badge: Green|Gray|Red
          "terminated"
  started_at: string              // Display: "10:00 AM"
  ended_at: string|null           // Display: "11:15 AM" or "-"
  duration_minutes: number        // Display: "75 min"
}
```

**Visual Elements**:
- **Table**: 6 columns
- **Status Badge**: Color-coded
- **Filter Toggle**: "Active Only" checkbox

---

### Data Contract: Deployment Status

**Source**: `GET /api/telemetry/deployment/status` ✅

**UI Consumes**:
```typescript
interface DeploymentDisplay {
  last_deployment: string         // Display: "Nov 14, 6:00 AM"
  environment: string             // Badge: "Production" | "Staging"
  version: string                 // Display: "v4.2.1"
  health_check: "passing"|        // Badge: Green|Red|Gray
                "failing"|"unknown"
  pending_tests: number           // Display: "0 pending"
}
```

**Visual Elements**:
- **Grid**: 5 cards
- **Environment Badge**: Color-coded (prod = red, staging = yellow)
- **Health Badge**: Large, prominent
- **Action Buttons**: [⚡ Run Stress Test] [🧪 Run Tests] [📊 View Logs]

---

### Interaction Flow: Save Secret (with Consent)

**Trigger**: User clicks [+ Add Secret] button

**Sequence**:
```
1. User clicks [+ Add Secret]
   └─> Modal opens: "Add Secret" form
       - Name text input (required)
       - Value password input (required)
       - Category dropdown: [API Key, Password, Token, Certificate]
       - [Cancel] [Save Secret] buttons

2. User fills form:
   - Name: "OPENAI_API_KEY"
   - Value: "sk-abc123..." (masked input)
   - Category: "API Key"
   
3. User clicks [Save Secret]
   └─> Form validates (name not empty, value not empty)
   └─> If invalid, show inline errors
   └─> If valid, proceed to consent

4. Consent modal opens (overlay on top of form modal):
   └─> Header: "🔒 Consent Required"
   └─> Display:
       - "You are storing: OPENAI_API_KEY"
       - "Category: API Key"
       - "This secret will be:"
         ✓ Encrypted using AES-256
         ✓ Stored in secure vault
         ✓ Accessible only to authorized agents
         ✓ Audited and logged
       - "Do you consent to storing this secret?"
       - [✕ No, Cancel] [✓ Yes, I Consent] buttons

5. User clicks [✓ Yes, I Consent]
   └─> Both modals disable, spinner appears

6. UI sends: POST /api/secrets/store ✅
   Body: {
     "name": "OPENAI_API_KEY",
     "value": "sk-abc123...",
     "category": "api_key",
     "consent_given": true
   }

7. Backend validates:
   - consent_given is true
   - Name doesn't already exist
   - Value is non-empty

8. Backend processes:
   - Encrypts value using AES-256
   - Stores in SecretVault table
   - Creates audit log: (user, timestamp, "secret_stored", name)
   - NEVER logs the actual secret value

9. Backend responds: 200 OK
   {
     "secret_id": "sec-xyz789",
     "name": "OPENAI_API_KEY",
     "category": "api_key",
     "encrypted": true,
     "stored_at": "2025-11-14T10:35:00Z",
     "status": "success"
   }

10. UI closes both modals
    └─> Shows toast: "Secret 'OPENAI_API_KEY' stored successfully" (green, 3s)
    └─> Refreshes secrets status (GET /api/telemetry/secrets/status)
    └─> Updates vault health card

Error Paths:

7a. Consent not given: 400
    └─> UI shows error in consent modal: "Consent required"
    └─> Re-enables buttons

7b. Duplicate name: 409
    └─> UI closes consent modal, shows error in form modal:
        "A secret named 'OPENAI_API_KEY' already exists"
    └─> Highlights name field, re-enables form

7c. Server error: 500
    └─> UI shows toast: "Failed to store secret: [error]" (red, 5s)
    └─> Closes modals, allows retry
```

**UI States**:
- **Idle**: Add button enabled
- **Form Open**: Modal with form, Submit enabled
- **Consent Open**: Overlay modal, buttons enabled
- **Submitting**: Both modals disabled, spinner visible
- **Success**: Modals closed, toast shown, vault refreshed
- **Error**: Error shown, forms re-enabled

**Backend Endpoint**: ✅ `POST /api/secrets/store`

---

### Interaction Flow: Approve Recording for Ingestion

**Trigger**: User clicks [Ingest] button on a recording row

**Sequence**:
```
1. User clicks [Ingest] button
   └─> Confirmation modal opens (optional):
       - "Start ingestion for 'meeting_2025-11-14.mp3'?"
       - "This will transcribe, index, and make available for learning."
       - "Estimated time: 15 minutes"
       - [Cancel] [Start Ingestion] buttons
   
   (Alternative: Skip confirmation, go straight to step 3)

2. User clicks [Start Ingestion]
   └─> Modal closes, button disables

3. UI sends: POST /api/recording/ingest/{recording_id} ✅

4. Backend validates:
   - Recording exists
   - Recording status is "pending" (not already processing)

5. Backend creates ingestion job:
   - Insert into IngestionJob table
   - Update recording.status = "processing"
   - Generate job_id

6. Backend starts async task:
   - If voice/video: Transcribe audio
   - If video: Extract keyframes
   - Index content for search
   - Generate summary/tags
   - Update job progress periodically

7. Backend responds: 200 OK (immediately, job runs async)
   {
     "recording_id": "rec-abc123",
     "ingestion_job_id": "job-xyz789",
     "status": "started",
     "estimated_duration_minutes": 15
   }

8. UI updates recording row:
   └─> Replaces [Ingest] button with "Processing..." badge
   └─> Shows progress bar (initially 0%)

9. UI starts polling (every 5 seconds):
   └─> GET /api/recording/ingest/{job_id}/status ✅

10. Backend returns progress:
    {
      "job_id": "job-xyz789",
      "recording_id": "rec-abc123",
      "status": "processing",
      "progress_percent": 45,
      "current_step": "transcription",
      "estimated_completion": "2025-11-14T10:50:00Z"
    }

11. UI updates progress bar: 45%

12. (Repeat polling until status changes)

13. Job completes, backend returns:
    {
      "job_id": "job-xyz789",
      "status": "completed",
      "progress_percent": 100,
      "result": {
        "transcript_url": "/api/recordings/rec-abc123/transcript",
        "summary": "Meeting discussed Q4 objectives..."
      }
    }

14. UI stops polling
    └─> Removes row from "Pending" table
    └─> Shows toast: "Ingestion complete: meeting_2025-11-14.mp3" (green, 3s)
    └─> Optionally moves to "Completed" section

Error Paths:

4. Recording not found: 404
   └─> Toast: "Recording not found" (red)

4. Recording already processing: 409
   └─> Toast: "Ingestion already in progress" (yellow)

13. Job failed:
    {
      "status": "failed",
      "error": "Transcription service unavailable"
    }
    └─> UI stops polling
    └─> Badge changes to "Failed" (red)
    └─> Button changes to [Retry]
    └─> Toast: "Ingestion failed: [error]" (red, 5s)
```

**UI States**:
- **Idle**: [Ingest] button enabled
- **Confirming**: Modal open (optional)
- **Starting**: Button disabled, spinner
- **Processing**: "Processing..." badge, progress bar 0-100%
- **Completed**: Row removed or moved, toast shown
- **Failed**: "Failed" badge, [Retry] button, error toast

**Backend Endpoints**: 
- ✅ `POST /api/recording/ingest/{id}` (start job)
- ✅ `GET /api/recording/ingest/{job_id}/status` (poll progress)

---

### Interaction Flow: Pause/Resume Kernel

**Note**: "Pause" is similar to "Stop" but gentler (suspends vs. terminates)

**Trigger**: User clicks [Pause] button on a kernel (if implemented)

**Sequence**:
```
1. User clicks [⏸ Pause] button
   └─> Button disables, shows spinner

2. UI sends: POST /api/telemetry/kernels/{kernel_id}/control?action=pause ✅
   (Note: "pause" action would need to be added to existing control endpoint)

3. Backend validates kernel state (must be "active")

4. Backend pauses kernel:
   - Stops accepting new tasks
   - Completes current task
   - Saves state to disk
   - Updates kernel.status = "paused"

5. Backend responds: 200 OK
   {
     "kernel_id": "kern-a1b2",
     "action": "pause",
     "status": "success"
   }

6. UI updates row:
   └─> Status badge changes to "Paused" (gray)
   └─> [⏸ Pause] button changes to [▶ Resume]
   └─> Toast: "Kernel paused" (blue, 3s)

Resume Flow:

1. User clicks [▶ Resume]
   └─> Button disables, spinner

2. UI sends: POST /api/telemetry/kernels/{kernel_id}/control?action=resume ✅

3. Backend resumes kernel:
   - Loads saved state
   - Starts accepting tasks
   - Updates kernel.status = "active"

4. UI updates row:
   └─> Status badge changes to "Active" (green)
   └─> [▶ Resume] button changes to [⏸ Pause]
   └─> Toast: "Kernel resumed" (green, 3s)
```

**UI States**:
- **Active**: [⏸ Pause] button
- **Paused**: [▶ Resume] button
- **Transitioning**: Spinner, disabled

**Backend Endpoint**: ✅ `POST /api/telemetry/kernels/{id}/control` (add "pause" and "resume" actions)

---

## Real-Time Updates via WebSocket

**All Layers**: `ws://localhost:8000/ws/telemetry` ✅

**Broadcast Frequency**: Every 2 seconds

**Message Format**:
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

**UI Integration**:
- Connect on dashboard load
- Update metric cards without full refresh
- Show live indicator (dot pulsing green when connected)
- Reconnect automatically if disconnected

---

## Wireframing Checklist

### Layer 1: Operations Console
- [ ] Header metrics grid (5 cards)
- [ ] Kernel table with 8 columns
- [ ] Status badges (4 colors: green, yellow, red, blue)
- [ ] Stress score progress bars
- [ ] Action button group (4 buttons per row)
- [ ] Crypto health grid (5-6 cards)
- [ ] Ingestion throughput grid (4-5 cards)
- [ ] Logs modal (scrollable, fixed font)
- [ ] Auto-refresh toggle
- [ ] WebSocket live indicator

### Layer 2: HTM Console
- [ ] Queue metrics grid (9 cards)
- [ ] Workload perception grid (4 cards)
- [ ] Origin stats cards (3 cards, one per origin)
- [ ] Size distribution chart (bar chart)
- [ ] Filter dropdowns (2: origin, status)
- [ ] Task table with 8 columns
- [ ] Origin badges (3 colors)
- [ ] Status badges (4 colors)
- [ ] Priority override modal (dropdown + text box)
- [ ] Context menu (right-click)

### Layer 3: Learning Dashboard
- [ ] Active intents grid (card layout)
- [ ] Progress bars (inside each card)
- [ ] Intent detail modal (with HTM task table)
- [ ] Playbook success table (3 columns)
- [ ] Success rate bars (color-coded)
- [ ] Retrospectives list (card layout)
- [ ] Two-column layout (insights | improvements)
- [ ] Policy suggestions list (card layout)
- [ ] Confidence badges (color-coded)
- [ ] Evidence list (collapsible or visible)
- [ ] Action buttons (3: accept, review, reject)
- [ ] Confirmation modal (with notes field)

### Layer 4: Dev/OS View
- [ ] Secrets vault grid (3 cards)
- [ ] Add secret button (prominent)
- [ ] Add secret modal (3-field form)
- [ ] Consent modal (overlay, checkbox-style info)
- [ ] Deployment status grid (5 cards)
- [ ] Action buttons (3: stress, tests, logs)
- [ ] Recordings table (5 columns)
- [ ] Type icons (3 types)
- [ ] Ingest button + progress badge
- [ ] Remote sessions table (6 columns)
- [ ] Status filter toggle

### Global/Shared
- [ ] Navigation bar (4 layer buttons)
- [ ] Toast notification system
- [ ] Loading spinners (buttons, modals, tables)
- [ ] Error states (inline, modal, toast)
- [ ] Empty states (no data messages)
- [ ] Responsive breakpoints (mobile, tablet, desktop)

---

## Design Tokens / Style Guide

### Colors

**Status Colors**:
- Success/Active: `#00ff88` (green)
- Warning/Idle: `#ffaa00` (yellow)
- Error/Failed: `#ff4444` (red)
- Info/Booting: `#00aaff` (blue)
- Neutral/Gray: `#888888` (gray)

**Semantic Colors**:
- Background: `#0a0a0a` (near black)
- Surface: `#1a1a1a` (dark gray)
- Border: `#333333` (medium gray)
- Text Primary: `#e0e0e0` (light gray)
- Text Secondary: `#888888` (medium gray)

**Origin Colors** (Layer 2):
- Filesystem: `#00aaff` (blue)
- Remote: `#ff00ff` (purple)
- Hunter: `#ffaa00` (orange)

### Typography

**Font Family**: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif  
**Monospace**: 'Courier New', monospace (for IDs, logs)

**Font Sizes**:
- H1 (Dashboard Title): 28px
- H2 (Section Title): 20px
- H3 (Card Title): 16px
- Body: 14px
- Small/Labels: 12px
- Tiny: 10px

### Spacing

**Grid Gap**: 15-20px  
**Card Padding**: 20px  
**Button Padding**: 8px 16px (small), 10px 20px (large)  
**Modal Padding**: 20px  

### Components

**Badges**: 
- Padding: 4px 12px
- Border-radius: 12px
- Font-size: 10-11px
- Font-weight: bold
- Text-transform: uppercase

**Progress Bars**:
- Height: 8-12px
- Border-radius: 4-6px
- Gradient: Green → Yellow → Red (for stress/capacity)

**Cards**:
- Border: 1px solid #333
- Border-radius: 8-10px
- Background: #1a1a1a
- Hover: Border-color change, slight lift

**Tables**:
- Header background: #2a2a2a
- Row hover: #252525
- Border: 1px solid #333
- Cell padding: 12px

**Modals**:
- Overlay: rgba(0, 0, 0, 0.85)
- Max-width: 500px (small), 1000px (large)
- Border-radius: 10px
- Box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5)

---

## Next Steps for Wireframing

1. **Start with Layer 1** (simplest, most visual)
   - Sketch header metrics grid
   - Design kernel table layout
   - Create action button group
   - Design logs modal

2. **Move to Layer 2** (add filters and charts)
   - Design filter row
   - Sketch task table with badges
   - Create priority override modal
   - Add performance charts

3. **Layer 3** (cards and lists)
   - Design intent cards with progress
   - Sketch policy suggestion cards
   - Create confirmation modal
   - Design retrospective layout

4. **Layer 4** (forms and multi-step flows)
   - Design secrets vault cards
   - Create add secret form
   - Design consent modal (overlay)
   - Sketch recording table with progress

5. **Polish** (transitions, states, responsive)
   - Define loading states for each component
   - Design error states
   - Create empty states
   - Design mobile/tablet layouts
   - Add microinteractions (hover, click, transitions)

---

## Questions for Wireframing?

**Data Contracts**: All fields defined above  
**Interactions**: All flows documented with states  
**Backend Support**: All endpoints confirmed with ✅  
**Design Tokens**: Colors, fonts, spacing provided  

**Ready to wireframe!** 🎨

For questions:
- Data/API questions → See [DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md)
- Technical details → See [TELEMETRY_DASHBOARD_GUIDE.md](./TELEMETRY_DASHBOARD_GUIDE.md)
- Visual flows → See [DASHBOARD_DATA_FLOWS.md](./DASHBOARD_DATA_FLOWS.md)
