# Session Management System - Complete ✅

## Overview

Grace now has a comprehensive session management system with:
- Remote access sessions with approval workflows
- Screen share sessions with stream URLs
- Real-time status tracking and heartbeat monitoring
- Notification integration for session events
- Connection state UI with "Connecting / Connected / Stopped"
- Session approval notifications

---

## 🔌 Backend API Endpoints

### Remote Access

#### 1. Start Remote Session
```
POST /api/remote/start
```

**Request:**
```json
{
  "user_id": "user",
  "safety_mode": "supervised",  // supervised | autonomous | read_only
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "remote_a1b2c3d4",
  "status": "active",  // or "pending_approval" for autonomous mode
  "requires_approval": false,
  "message": "Session created successfully"
}
```

---

#### 2. Stop Remote Session
```
POST /api/remote/stop/{session_id}
```

**Request:**
```json
{
  "reason": "User requested"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "remote_a1b2c3d4",
  "status": "stopped",
  "commands_executed": 42,
  "duration_seconds": 1234.5
}
```

---

#### 3. Get Remote Session Status
```
GET /api/remote/status/{session_id}
```

**Response (Active):**
```json
{
  "session_id": "remote_a1b2c3d4",
  "status": "active",
  "type": "remote_access",
  "user_id": "user",
  "safety_mode": "supervised",
  "started_at": "2025-11-18T12:00:00",
  "duration_seconds": 345.6,
  "commands_executed": 12,
  "last_activity": "2025-11-18T12:05:45"
}
```

**Response (Stopped):**
```json
{
  "session_id": "remote_a1b2c3d4",
  "status": "stopped",
  "stopped_at": "2025-11-18T12:10:00",
  "stop_reason": "User requested",
  "duration_seconds": 600.0
}
```

---

#### 4. Approve Remote Session
```
POST /api/remote/approve/{session_id}
```

**Response:**
```json
{
  "success": true,
  "session_id": "remote_a1b2c3d4",
  "status": "active"
}
```

---

### Screen Share

#### 5. Start Screen Share
```
POST /api/screen_share/start
```

**Request:**
```json
{
  "user_id": "user",
  "quality": "medium",  // low | medium | high
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "screen_5f6g7h8i",
  "status": "active",
  "stream_url": "/stream/screen_5f6g7h8i",
  "quality": "medium"
}
```

---

#### 6. Stop Screen Share
```
POST /api/screen_share/stop
```

**Request:**
```json
{
  "session_id": "screen_5f6g7h8i"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "screen_5f6g7h8i",
  "status": "stopped",
  "frames_captured": 5432,
  "duration_seconds": 789.1
}
```

---

#### 7. Get Screen Share Status
```
GET /api/screen_share/status/{session_id}
```

**Response:**
```json
{
  "session_id": "screen_5f6g7h8i",
  "status": "active",
  "type": "screen_share",
  "user_id": "user",
  "quality": "medium",
  "stream_url": "/stream/screen_5f6g7h8i",
  "started_at": "2025-11-18T12:15:00",
  "duration_seconds": 234.5,
  "frames_captured": 1234
}
```

---

### Session Management

#### 8. List Active Sessions
```
GET /api/sessions/active
```

**Response:**
```json
{
  "active_sessions": [
    {
      "session_id": "remote_a1b2c3d4",
      "type": "remote_access",
      "status": "active",
      ...
    },
    {
      "session_id": "screen_5f6g7h8i",
      "type": "screen_share",
      "status": "active",
      ...
    }
  ],
  "total": 2
}
```

---

#### 9. Session Heartbeat
```
POST /api/sessions/heartbeat/{session_id}
```

**Response:**
```json
{
  "success": true
}
```

---

#### 10. Check Dropped Sessions
```
POST /api/sessions/check_dropped?timeout_minutes=5
```

**Response:**
```json
{
  "dropped_sessions": ["remote_a1b2c3d4", "screen_5f6g7h8i"],
  "count": 2
}
```

---

## 🔔 Notification Integration

Sessions automatically send notifications for key events:

### Notification Events

#### 1. Remote Session Started
```json
{
  "event": "remote_session_started",
  "data": {
    "session_id": "remote_a1b2c3d4",
    "user_id": "user",
    "message": "Remote access session started (supervised mode)",
    "badge": "🔓",
    "timestamp": "2025-11-18T12:00:00"
  }
}
```

#### 2. Remote Session Needs Approval
```json
{
  "event": "remote_session_approval_needed",
  "data": {
    "session_id": "remote_a1b2c3d4",
    "user_id": "user",
    "safety_mode": "autonomous",
    "message": "Remote access session remote_a1b2c3d4 needs approval (autonomous mode)",
    "badge": "🔐",
    "timestamp": "2025-11-18T12:00:00"
  }
}
```

#### 3. Remote Session Approved
```json
{
  "event": "remote_session_approved",
  "data": {
    "session_id": "remote_a1b2c3d4",
    "user_id": "user",
    "message": "Remote access session approved and activated",
    "badge": "✅",
    "timestamp": "2025-11-18T12:01:00"
  }
}
```

#### 4. Remote Session Stopped
```json
{
  "event": "remote_session_stopped",
  "data": {
    "session_id": "remote_a1b2c3d4",
    "user_id": "user",
    "message": "Remote access session stopped: User requested",
    "badge": "🔒",
    "timestamp": "2025-11-18T12:10:00"
  }
}
```

#### 5. Screen Share Started
```json
{
  "event": "screen_share_started",
  "data": {
    "session_id": "screen_5f6g7h8i",
    "user_id": "user",
    "quality": "medium",
    "message": "Screen share session started (medium quality)",
    "badge": "📺",
    "timestamp": "2025-11-18T12:15:00"
  }
}
```

#### 6. Screen Share Stopped
```json
{
  "event": "screen_share_stopped",
  "data": {
    "session_id": "screen_5f6g7h8i",
    "user_id": "user",
    "message": "Screen share session ended",
    "badge": "📺",
    "timestamp": "2025-11-18T12:25:00"
  }
}
```

#### 7. Session Dropped (Inactive)
```json
{
  "event": "remote_access_dropped",
  "data": {
    "session_id": "remote_a1b2c3d4",
    "user_id": "user",
    "message": "remote_access session dropped (inactive)",
    "badge": "⚠️",
    "timestamp": "2025-11-18T12:30:00"
  }
}
```

---

## 🎨 Frontend UI States

### Connection States

The UI displays clear visual indicators for session states:

#### Remote Access Button States

```
🔒 Remote Access          (Disconnected)
⏳ Loading...             (Connecting/Stopping)
🔐 Pending               (Needs Approval) - orange/pulsing
🔓 Connected             (Active)
Session: remote_a1      (Shows session ID)
Status: Connected       (Shows detailed status)
```

#### Screen Share Button States

```
📺 Screen Share           (Not Sharing)
⏳ Loading...             (Starting/Stopping)
📺 Sharing                (Active)
Session: screen_5f6     (Shows session ID)
Status: Sharing (active) (Shows stream URL)
```

### Visual Indicators

- **Default**: Gray background
- **Active/Connected**: Green background
- **Pending Approval**: Orange background with pulsing animation
- **Failed**: Red error message in sidebar
- **Session ID**: Displayed as truncated monospace text (e.g., `remote_a1`)

---

## 🔄 Session Lifecycle

### Remote Access Flow

```
User Clicks Button
       ↓
POST /api/remote/start
       ↓
┌──────────────────────────┐
│ Check Safety Mode        │
├──────────────────────────┤
│ supervised → Active      │
│ autonomous → Pending     │
└──────────────────────────┘
       ↓
If Pending:
  → Send "approval_needed" notification
  → UI shows "🔐 Pending" (orange/pulsing)
  → Poll status every 2s
  → Admin approves via POST /api/remote/approve/{id}
  → Status changes to "active"
  → UI shows "🔓 Connected" (green)

If Active:
  → Send "session_started" notification
  → UI shows "🔓 Connected" (green)
  → Start heartbeat (every 30s)
       ↓
Session Active
  → Commands execute
  → Heartbeat keeps alive
  → UI shows session ID
       ↓
User Clicks Stop
  → POST /api/remote/stop/{id}
  → Send "session_stopped" notification
  → Clear heartbeat
  → UI returns to "🔒 Remote Access"
```

### Screen Share Flow

```
User Clicks Button
       ↓
POST /api/screen_share/start
       ↓
Create Session
  → Generate session_id
  → Create stream_url
  → Send "screen_share_started" notification
  → UI shows "📺 Sharing" (green)
  → Display stream URL
  → Start heartbeat
       ↓
Capture Frames
  → Increment frames_captured
  → Update last_activity
       ↓
User Clicks Stop
  → POST /api/screen_share/stop
  → Send "screen_share_stopped" notification
  → Clear heartbeat
  → UI returns to "📺 Screen Share"
```

---

## 💓 Heartbeat Monitoring

### Purpose

Heartbeats keep sessions alive and detect dropped connections.

### How It Works

1. **Frontend Sends Heartbeat**
   ```javascript
   setInterval(async () => {
     await RemoteAPI.sessionHeartbeat(sessionId);
   }, 30000); // Every 30 seconds
   ```

2. **Backend Updates Timestamp**
   ```python
   session['last_activity'] = datetime.utcnow().isoformat()
   ```

3. **Detect Dropped Sessions**
   ```python
   # Check for sessions inactive > 5 minutes
   POST /api/sessions/check_dropped?timeout_minutes=5
   
   # Returns:
   {
     "dropped_sessions": ["remote_a1b2c3d4"],
     "count": 1
   }
   ```

4. **Notification Sent**
   ```json
   {
     "event": "remote_access_dropped",
     "message": "Session dropped (inactive)",
     "badge": "⚠️"
   }
   ```

---

## 🧪 Testing Guide

### Test Remote Access

#### Test 1: Start Supervised Session
```bash
# 1. Click "🔒 Remote Access"
# 2. Should show:
#    - "⏳ Loading..." briefly
#    - Then "🔓 Connected" (green)
#    - Session ID displayed
#    - Status: "Connected"

# 3. Check notification
# Should see: "Remote access session started (supervised mode)"
```

#### Test 2: Start Autonomous Session (Needs Approval)
```bash
# 1. Modify code to use 'autonomous' mode
# 2. Click "🔒 Remote Access"
# 3. Should show:
#    - "⏳ Loading..." briefly
#    - Then "🔐 Pending" (orange, pulsing)
#    - Status: "Pending Approval"

# 4. Check notification
# Should see: "Remote access session needs approval"

# 5. Approve via API:
curl -X POST http://localhost:8000/api/remote/approve/remote_a1b2c3d4

# 6. UI should auto-update to:
#    - "🔓 Connected" (green)
#    - Status: "Connected"
```

#### Test 3: Stop Session
```bash
# 1. With active session, click button again
# 2. Should show:
#    - "⏳ Loading..." briefly
#    - Then back to "🔒 Remote Access" (gray)
#    - Session ID cleared
#    - Status: "Stopped"

# 3. Check notification
# Should see: "Remote access session stopped"
```

### Test Screen Share

#### Test 1: Start Screen Share
```bash
# 1. Click "📺 Screen Share"
# 2. Should show:
#    - "⏳ Loading..." briefly
#    - Then "📺 Sharing" (green)
#    - Session ID displayed
#    - Status shows stream URL

# 3. Check notification
# Should see: "Screen share session started (medium quality)"
```

#### Test 2: Stop Screen Share
```bash
# 1. Click button again
# 2. Should show:
#    - "⏳ Loading..." briefly
#    - Back to "📺 Screen Share" (gray)
#    - Session ID cleared

# 3. Check notification
# Should see: "Screen share session ended"
```

### Test Heartbeat & Drop Detection

```bash
# 1. Start a session
# 2. Wait 6 minutes without clicking anything
# 3. Run drop check:
curl -X POST http://localhost:8000/api/sessions/check_dropped?timeout_minutes=5

# 4. Should return dropped session
# 5. Should see notification: "Session dropped (inactive)"
```

---

## 🔧 Configuration

### Safety Modes

```python
# supervised - Requires user approval for each command
# autonomous - Needs initial approval, then runs freely
# read_only - Can only read, no write operations
```

### Screen Share Quality

```python
# low - 640x480, 15fps
# medium - 1280x720, 30fps
# high - 1920x1080, 60fps
```

### Heartbeat Settings

```javascript
// Frontend heartbeat interval
const HEARTBEAT_INTERVAL = 30000; // 30 seconds

// Backend timeout threshold
const TIMEOUT_MINUTES = 5; // 5 minutes
```

---

## 📊 Session History

All stopped sessions are archived in history:

```bash
GET /api/sessions/history?limit=50
```

**Response:**
```json
{
  "history": [
    {
      "session_id": "remote_a1b2c3d4",
      "type": "remote_access",
      "status": "stopped",
      "started_at": "2025-11-18T12:00:00",
      "stopped_at": "2025-11-18T12:10:00",
      "stop_reason": "User requested",
      "duration_seconds": 600.0,
      "commands_executed": 42
    }
  ],
  "total": 127
}
```

---

## ✅ Verification Checklist

Backend:
- [x] Remote access start/stop endpoints
- [x] Screen share start/stop endpoints
- [x] Session status tracking
- [x] Approval workflow for autonomous mode
- [x] Heartbeat monitoring
- [x] Dropped session detection
- [x] Notification integration
- [x] Session history archiving

Frontend:
- [x] Connection state UI (Connecting/Connected/Stopped)
- [x] Session ID display
- [x] Status message display
- [x] Pending approval indicator (pulsing orange)
- [x] Heartbeat sender (every 30s)
- [x] Auto-polling for approval status
- [x] Error handling and display

Integration:
- [x] Notifications sent for all session events
- [x] Approval notifications trigger UI updates
- [x] Dropped session notifications
- [x] Stream URL displayed for screen share

---

**Session management system is complete and fully integrated!** 🎉
