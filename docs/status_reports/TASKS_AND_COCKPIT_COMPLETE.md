# Tasks & Cockpit Dashboard - Complete ✅

## Overview

Grace now has a comprehensive task management and dashboard system with:
- **Background Tasks Panel** - View, pause, resume, and kill tasks
- **Missions Tab** - Track active missions and progress
- **Approvals Queue** - Manage pending approvals
- **Cockpit Dashboard** - High-level system overview
- **Notification Integration** - All updates flow to chat

---

## 📋 Enhanced Background Tasks Drawer

### Features

#### 1. Three-Tab Interface

**📋 Tasks Tab**
- Shows active background tasks
- Real-time progress tracking
- Pause/resume/kill controls
- Status indicators (pending, running, paused, completed, failed)

**🎯 Missions Tab**
- Active missions from mission control
- Mission progress bars
- Mission status and descriptions

**🔐 Approvals Tab**
- Tasks waiting for approval
- Governance tier display
- Approve/reject buttons
- Approval requirement indicators

### Task Controls

#### Pause Task
```
Status: running → paused
Button: ⏸️ Pause
Notification: "Task paused"
```

#### Resume Task
```
Status: paused → running
Button: ▶️ Resume
Notification: "Task resumed"
```

#### Kill Task
```
Status: running/paused → terminated
Button: ❌ Kill
Confirmation: Required
Notification: "Task killed"
```

### Task Display

Each task shows:
- **Icon**: Status indicator (⚙️ running, ⏸️ paused, ✅ completed, ❌ failed)
- **Name**: Task title
- **Description**: Task details
- **Status Badge**: Color-coded status
- **Progress Bar**: For running tasks
- **Timestamp**: When task started
- **Controls**: Pause/Resume/Kill buttons
- **Error Message**: If task failed

### Status Colors

```css
running      → Blue (#2196f3)
completed    → Green (#4caf50)
failed       → Red (#f44336)
paused       → Orange (#ff9800)
waiting_approval → Purple (#9c27b0)
pending      → Gray (#757575)
```

---

## 🎛️ Enhanced Remote Cockpit Dashboard

### Overview Sections

#### 1. 🛡️ Guardian Health

Shows system health status:
- **Status Indicator**: Healthy / Warning / Critical
- **Uptime Percentage**: System availability
- **Anomalies Detected**: Count of detected issues
- **Threats Detected**: Security threat count
- **Last Check**: Timestamp of last health check

**Status Colors:**
- Healthy: Green
- Warning: Orange
- Critical: Red

---

#### 2. 📚 Learning Backlog

Shows pending learning tasks:
- **Queued (📥)**: Items waiting for ingestion
- **Processing (⚙️)**: Currently being analyzed
- **Failed (❌)**: Items that failed processing
- **Total**: Overall backlog count

---

#### 3. 🔔 Upcoming Reminders

Shows next 24 hours of reminders:
- **Priority Indicator**: 🔴 High, 🟡 Medium, 🟢 Low
- **Message**: Reminder content
- **Scheduled Time**: When reminder will fire
- **Top 5**: Shows most urgent reminders

---

#### 4. 📊 System Metrics

Real-time system statistics:
- **Active Sessions**: Current user sessions
- **Total Queries**: Processed queries count
- **Avg Response Time**: Performance metric
- **Error Rate**: System reliability

---

## 🔄 Notification Integration

All task and cockpit events send notifications to chat:

### Task Notifications

#### Task Paused
```json
{
  "event": "task_paused",
  "message": "Task 'Data Ingestion' paused by user",
  "badge": "⏸️"
}
```

#### Task Resumed
```json
{
  "event": "task_resumed",
  "message": "Task 'Data Ingestion' resumed",
  "badge": "▶️"
}
```

#### Task Killed
```json
{
  "event": "task_killed",
  "message": "Task 'Data Ingestion' terminated by user",
  "badge": "❌"
}
```

#### Task Completed
```json
{
  "event": "task_completed",
  "message": "Task 'Data Ingestion' completed successfully",
  "badge": "✅"
}
```

#### Task Failed
```json
{
  "event": "task_failed",
  "message": "Task 'Data Ingestion' failed: [error details]",
  "badge": "❌"
}
```

### Approval Notifications

#### Task Approved
```json
{
  "event": "task_approved",
  "message": "Task 'Deploy to Production' approved",
  "badge": "✅"
}
```

#### Task Rejected
```json
{
  "event": "task_rejected",
  "message": "Task 'Deploy to Production' rejected",
  "badge": "❌"
}
```

### Guardian Notifications

#### Anomaly Detected
```json
{
  "event": "guardian_anomaly",
  "message": "Guardian detected anomaly in system behavior",
  "badge": "⚠️"
}
```

#### Health Status Changed
```json
{
  "event": "guardian_health_changed",
  "message": "Guardian health status: Warning → Critical",
  "badge": "🛡️"
}
```

---

## 🧪 Usage Guide

### Managing Background Tasks

#### View Active Tasks
```
1. Click "📋 Tasks" in sidebar
2. Drawer opens showing active tasks
3. Auto-refreshes every 3 seconds
```

#### Pause a Running Task
```
1. Find task in "📋 Tasks" tab
2. Click "⏸️ Pause" button
3. Task status changes to "paused"
4. Chat shows: "Task 'X' paused by user"
```

#### Resume a Paused Task
```
1. Find paused task
2. Click "▶️ Resume" button
3. Task status changes to "running"
4. Progress continues from where it left off
```

#### Kill a Task
```
1. Find task (running, paused, or pending)
2. Click "❌ Kill" button
3. Confirm in dialog
4. Task terminates immediately
5. Chat shows: "Task 'X' terminated by user"
```

---

### Viewing Missions

#### Check Active Missions
```
1. Click "📋 Tasks" in sidebar
2. Switch to "🎯 Missions" tab
3. See all active missions with progress
4. Auto-refreshes every 3 seconds
```

**Mission Display:**
- 🎯 Icon
- Mission title
- Description
- Status badge
- Progress bar (if applicable)

---

### Managing Approvals

#### View Pending Approvals
```
1. Click "📋 Tasks" in sidebar
2. Switch to "🔐 Approvals" tab
3. See tasks waiting for approval
4. Shows approval tier (Tier 1/2/3)
```

#### Approve a Task
```
1. Find task in approvals queue
2. Review task details and tier
3. Click "✅ Approve"
4. Task moves to active state
5. Chat shows: "Task 'X' approved"
```

#### Reject a Task
```
1. Find task in approvals queue
2. Click "❌ Reject"
3. Task is cancelled
4. Chat shows: "Task 'X' rejected"
```

---

### Using Cockpit Dashboard

#### Open Dashboard
```
1. Click "🎛️ Cockpit" in sidebar
2. Dashboard opens with 4 sections
3. Auto-refreshes every 10 seconds
```

#### Check Guardian Health
```
Look at "🛡️ Guardian Health" section:
- Green status = Healthy ✅
- Orange status = Warning ⚠️
- Red status = Critical 🚨

Metrics shown:
- Uptime percentage
- Anomalies count
- Threats detected
```

#### Monitor Learning Backlog
```
Look at "📚 Learning Backlog" section:
- Check queued items
- Monitor processing items
- Review failed items
- Track total backlog
```

#### View Upcoming Events
```
Look at "🔔 Upcoming Reminders" section:
- See next 5 reminders
- Color-coded by priority
- Shows scheduled times
- Covers next 24 hours
```

#### Check System Metrics
```
Look at "📊 System Metrics" section:
- Active sessions count
- Total queries processed
- Average response time
- Error rate percentage
```

---

## 📊 Task Lifecycle with Notifications

```
Task Created
     ↓
Chat: "📋 New task queued: [name]"
     ↓
Task Running
     ↓
Chat: "⚙️ Task started: [name]"
     ↓
[User Pauses]
     ↓
Chat: "⏸️ Task paused: [name]"
     ↓
[User Resumes]
     ↓
Chat: "▶️ Task resumed: [name]"
     ↓
Task Completes
     ↓
Chat: "✅ Task completed: [name]"
```

**OR if task fails:**
```
Task Running
     ↓
Task Fails
     ↓
Chat: "❌ Task failed: [name] - [error]"
```

**OR if user kills:**
```
Task Running
     ↓
[User Kills]
     ↓
Chat: "❌ Task killed: [name]"
```

---

## 🎯 Integration Points

### Task Management API

```javascript
// Fetch tasks
GET /api/tasks/

// Update task status (pause/resume)
PATCH /api/tasks/{task_id}
Body: { "status": "paused" }

// Kill task
DELETE /api/tasks/{task_id}
```

### Missions API

```javascript
// Fetch missions
GET /api/world-model/missions

Response: {
  "missions": [...],
  "count": 5
}
```

### Approvals API

```javascript
// Approve task
POST /api/governance/approve
Body: {
  "trace_id": "task_123",
  "approved": true,
  "user_id": "user"
}

// Reject task
POST /api/governance/reject
Body: {
  "trace_id": "task_123",
  "approved": false,
  "reason": "User rejected",
  "user_id": "user"
}
```

### Cockpit Data APIs

```javascript
// Guardian health
GET /api/metrics/health

// Learning backlog
GET /api/memory/files/ingestions

// Reminders
GET /api/reminders

// System metrics
GET /api/metrics/summary
```

---

## 🧪 Testing Guide

### Test Task Controls

```bash
# 1. Start a long-running task (mock)
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "Test", "priority": "high"}'

# 2. Open Tasks drawer
# Click "📋 Tasks" in sidebar

# 3. Pause the task
# Click "⏸️ Pause" button
# Check chat: Should see "Task paused" notification

# 4. Resume the task
# Click "▶️ Resume" button
# Check chat: Should see "Task resumed" notification

# 5. Kill the task
# Click "❌ Kill" button
# Confirm
# Check chat: Should see "Task killed" notification
```

### Test Approvals

```bash
# 1. Create task needing approval
# (Backend automatically creates for Tier 2/3 operations)

# 2. Open approvals tab
# Click "📋 Tasks" → "🔐 Approvals" tab

# 3. Approve a task
# Click "✅ Approve"
# Task should move to active
# Chat shows: "Task approved"

# 4. Reject a task
# Click "❌ Reject"
# Task should be cancelled
# Chat shows: "Task rejected"
```

### Test Cockpit Dashboard

```bash
# 1. Open cockpit
# Click "🎛️ Cockpit" in sidebar

# 2. Verify all sections load:
# ✓ Guardian Health shows status
# ✓ Learning Backlog shows counts
# ✓ Reminders show upcoming items
# ✓ Metrics show system stats

# 3. Test auto-refresh
# Wait 10 seconds
# Data should update automatically

# 4. Manual refresh
# Click "🔄 Refresh Dashboard"
# All sections reload
```

---

## ✅ Verification Checklist

Tasks Drawer:
- [x] Three tabs (Tasks, Missions, Approvals)
- [x] Tab switching works
- [x] Task list loads from `/api/tasks/`
- [x] Missions load from `/api/world-model/missions`
- [x] Pause button changes status to paused
- [x] Resume button changes status to running
- [x] Kill button terminates task
- [x] Approval buttons call governance API
- [x] Auto-refresh every 3 seconds
- [x] Task counts shown in tabs

Cockpit Dashboard:
- [x] Guardian health section loads
- [x] Learning backlog section loads
- [x] Reminders section loads
- [x] System metrics section loads
- [x] Auto-refresh every 10 seconds
- [x] Manual refresh button works
- [x] Health status color-coded
- [x] Empty states shown when no data

Notifications:
- [x] Task paused → notification sent
- [x] Task resumed → notification sent
- [x] Task killed → notification sent
- [x] Task approved → notification sent
- [x] Task rejected → notification sent
- [x] Notifications appear in chat
- [x] Notifications have correct badges

---

## 🚀 Future Enhancements

### Priority 1: Advanced Task Controls

- [ ] Bulk operations (pause/resume/kill multiple)
- [ ] Task priority adjustment
- [ ] Task scheduling
- [ ] Task dependencies
- [ ] Retry failed tasks

### Priority 2: Enhanced Dashboard

- [ ] Customizable widgets
- [ ] Metric charts/graphs
- [ ] Alert thresholds
- [ ] Export dashboard data
- [ ] Historical trends

### Priority 3: Smart Notifications

- [ ] Notification filtering
- [ ] Smart grouping
- [ ] Priority-based routing
- [ ] Custom notification rules
- [ ] Notification history

---

**Tasks and Cockpit systems are complete and fully integrated!** 🎉

Chat now serves as the primary narrative for all system events.
