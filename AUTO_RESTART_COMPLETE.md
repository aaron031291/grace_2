# Grace Auto-Restart System - COMPLETE ✅

**Date:** November 14, 2025  
**Status:** Production Ready  
**Features:** Self-Restart + External Watchdog + Alert System

---

## 🏗️ Architecture

Grace now has **two-layer resilience**:

### Layer 1: Internal Self-Restart (Control Plane)
**File:** `backend/core/kernel_restart_manager.py`

**How it works:**
- Control Plane monitors kernel heartbeats
- If a kernel misses heartbeat for 60s → auto-restart
- Max 3 restart attempts per kernel
- 30s cooldown between restarts
- Publishes restart events to message bus

**Events Published:**
```
kernel.restart.initiated  - Restart starting
kernel.restart.success    - Restart succeeded
kernel.restart.failed     - Restart failed
kernel.restart.max_attempts - Too many failures
system.critical_kernel_down - Critical kernel dead
```

### Layer 2: External Watchdog (Process Supervisor)
**File:** `grace_watchdog.py`

**How it works:**
- Monitors `python serve.py` process
- Detects crashes vs manual shutdowns
- Auto-restarts on crash
- Respects kill switch (won't restart if manually stopped)
- Logs all events and sends alerts

**State File:** `grace_state.json`
```json
{
  "manual_shutdown": false,  ← Kill switch
  "timestamp": "2025-11-14T...",
  "restart_count": 0
}
```

---

## 🎯 Use Cases

### 1. Grace Crashes
```
1. Process dies unexpectedly
2. Watchdog detects crash
3. Checks grace_state.json → manual_shutdown=false
4. Auto-restarts serve.py
5. Logs event to watchdog.log
6. Creates alert in alerts/ folder
7. Grace boots back up
```

### 2. Kernel Dies
```
1. Kernel stops sending heartbeat
2. Kernel Restart Manager detects timeout (60s)
3. Calls kernel's restart function
4. Publishes kernel.restart.initiated event
5. Kernel restarts
6. Publishes kernel.restart.success
7. Alert system notifies co-pilot
```

### 3. Manual Shutdown (Kill Switch)
```
1. Run: stop_grace.cmd (or grace.cmd stop)
2. Sets manual_shutdown=true in grace_state.json
3. Kills python processes
4. Watchdog sees manual_shutdown=true
5. Watchdog does NOT auto-restart
6. Grace stays stopped until you start her again
```

### 4. System Reboot
```
1. System reboots
2. Watchdog starts on boot (systemd/service)
3. Checks grace_state.json
4. If manual_shutdown=false → auto-start
5. Grace comes back online automatically
```

---

## 🚀 How to Use

### Start Grace with Watchdog (Recommended)
```bash
# Windows
start_grace.cmd

# Or
grace.cmd watch

# PowerShell
.\GRACE.ps1 watch
```

This starts Grace with the watchdog supervisor that will auto-restart on crashes.

### Start Grace Without Watchdog
```bash
# Just the backend
python serve.py

# Or
grace.cmd start
```

### Stop Grace (Kill Switch)
```bash
# Windows
stop_grace.cmd

# Or
grace.cmd stop

# PowerShell
.\GRACE.ps1 stop
```

This sets the `manual_shutdown` flag so watchdog won't restart.

### Check Status
```bash
grace.cmd status

# Or
.\GRACE.ps1 status
```

Shows:
- Manual shutdown flag
- Backend health (port 8000)
- Process info (PID, CPU, memory)

### View Logs
```bash
grace.cmd logs

# Or
type watchdog.log
```

---

## 📊 Production Deployment

### Option 1: PM2 (Node-based supervisor)
```bash
npm install -g pm2

# Start
pm2 start pm2.config.js

# Monitor
pm2 monit

# Logs
pm2 logs grace

# Stop
pm2 stop grace

# Auto-start on boot
pm2 startup
pm2 save
```

**Benefits:**
- Battle-tested process manager
- Built-in monitoring
- Log rotation
- Cluster mode support

### Option 2: Systemd (Linux)
```bash
# Install
sudo cp grace.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable grace
sudo systemctl start grace

# Monitor
sudo systemctl status grace
journalctl -u grace -f

# Stop
sudo systemctl stop grace

# Restart
sudo systemctl restart grace
```

**Benefits:**
- Native Linux integration
- Starts on boot automatically
- Resource limits (CPU, memory)
- Integrated logging

### Option 3: Windows Service
```bash
# Install Python watchdog as Windows service
# (Future enhancement - use nssm or pywin32)

nssm install Grace "C:\Users\aaron\grace_2\.venv\Scripts\python.exe" "grace_watchdog.py"
nssm set Grace AppDirectory "C:\Users\aaron\grace_2"
nssm start Grace
```

---

## 🔔 Alert System

### Alert Files
Located in: `alerts/`

**Files created:**
```
alerts/
├── critical_20251114_120000.json  - Critical failures
├── warning_20251114_120100.json   - Restart warnings
├── info_20251114_120200.json      - Successful restarts
└── latest_notification.json       - Most recent alert
```

### Alert Format
```json
{
  "event_type": "kernel.restart.initiated",
  "timestamp": "2025-11-14T12:00:00",
  "payload": {
    "kernel_name": "memory",
    "reason": "heartbeat_timeout",
    "attempt": 1,
    "critical": false
  }
}
```

### Notification File
```json
{
  "severity": "WARNING",
  "timestamp": "2025-11-14T12:00:00",
  "event": "kernel.restart.initiated",
  "summary": "Kernel 'memory' is being restarted (reason: heartbeat_timeout)",
  "requires_attention": true
}
```

---

## 📈 Monitoring

### Check Restart History
```python
from backend.core.kernel_restart_manager import kernel_restart_manager

status = kernel_restart_manager.get_status()
print(f"Total restarts: {status['total_restarts']}")
print(f"Recent restarts: {status['recent_restarts']}")
```

### View Watchdog Status
```bash
grace.cmd status
```

Output:
```
State File:
  Manual Shutdown: False
  Last Update: 2025-11-14T...

Backend Health:
  ✅ ALIVE on port 8000

Process:
  PID: 12345
  CPU: 1.5s
  Memory: 250 MB
```

---

## 🔧 Configuration

### Kernel Restart Manager
**File:** `backend/core/kernel_restart_manager.py`

```python
# Timeouts
heartbeat_timeout = 60  # seconds
max_restart_attempts = 3
restart_cooldown = 30  # seconds
```

### Watchdog Supervisor
**File:** `grace_watchdog.py`

```python
# Monitoring
check_interval = 5  # seconds
min_uptime_for_success = 30  # seconds
max_consecutive_failures = 5
pause_after_failures = 60  # seconds
```

---

## 🎯 Restart Decision Logic

### Kernel Restart (Internal)
```
if kernel_heartbeat_age > 60s:
    if restart_count < 3:
        if time_since_last_restart > 30s:
            → RESTART KERNEL
        else:
            → WAIT (cooldown)
    else:
        → ALERT CO-PILOT (manual intervention)
```

### Process Restart (External)
```
if serve.py not running:
    if manual_shutdown == true:
        → DO NOT RESTART (kill switch active)
    elif uptime < 30s:
        → RESTART (crash detected)
        → LOG ALERT (boot failure)
    else:
        → RESTART (unexpected exit)
        → LOG ALERT (process died)
```

---

## 📁 Files Created

### Core System
1. `backend/core/kernel_restart_manager.py` - Internal kernel supervision
2. `backend/core/restart_alert_system.py` - Alert monitoring & notification

### Watchdog & Control
3. `grace_watchdog.py` - External process supervisor
4. `grace.cmd` - Windows control script
5. `start_grace.cmd` - Start with watchdog
6. `stop_grace.cmd` - Kill switch
7. `GRACE.ps1` - PowerShell control script

### Production Deployment
8. `pm2.config.js` - PM2 configuration
9. `grace.service` - Systemd service file

### Documentation
10. `AUTO_RESTART_COMPLETE.md` - This file

---

## 🧪 Testing Auto-Restart

### Test 1: Kill a Kernel
```python
# In backend code, simulate kernel death
from backend.core.infrastructure_manager_kernel import infrastructure_manager

# Stop heartbeats (simulates crash)
if infrastructure_manager._heartbeat_task:
    infrastructure_manager._heartbeat_task.cancel()

# Wait 60 seconds, kernel restart manager will auto-restart
```

### Test 2: Kill serve.py Process
```bash
# Find Grace process
tasklist | findstr python

# Kill it
taskkill /F /PID <PID>

# Watchdog will auto-restart in 5 seconds
```

### Test 3: Use Kill Switch
```bash
# Stop manually
stop_grace.cmd

# Check status - should show manual_shutdown=true
grace.cmd status

# Watchdog will NOT restart
```

### Test 4: Restart Manually
```bash
# After kill switch
grace.cmd restart

# Or clear flag and start
echo {"manual_shutdown": false} > grace_state.json
start_grace.cmd
```

---

## 📊 Expected Behavior

### Scenario: Crash During Operation
```
[08:00:00] Grace running normally
[08:15:30] Unexpected crash
[08:15:30] [WATCHDOG] ⚠️ Grace died unexpectedly
[08:15:30] [WATCHDOG] 🔄 Auto-restarting (attempt 1)
[08:15:35] [WATCHDOG] ✅ Grace started (PID: 5678)
[08:15:35] [ALERT-SYS] 📧 Alert sent to co-pilot
[08:16:00] Grace fully operational again
```

**Downtime: ~30 seconds**

### Scenario: Kill Switch Used
```
[08:00:00] Grace running normally
[08:15:00] User runs: stop_grace.cmd
[08:15:00] Manual shutdown flag set
[08:15:01] Grace processes killed
[08:15:05] [WATCHDOG] ℹ️ Grace stopped manually - not restarting
[08:30:00] Grace remains stopped (as intended)
```

**Downtime: Until user restarts**

### Scenario: Kernel Failure
```
[08:00:00] All kernels healthy
[08:15:00] Memory kernel stops responding
[08:16:00] [RESTART-MGR] ⚠️ Kernel memory heartbeat timeout!
[08:16:00] [RESTART-MGR] 🔄 Restarting kernel: memory
[08:16:05] [RESTART-MGR] ✅ Kernel memory restarted
[08:16:05] [ALERT-SYS] 📧 Alert: Memory kernel restarted
[08:16:10] All kernels healthy again
```

**Downtime: ~10 seconds for that kernel**

---

## 🎨 Integration with Layer 1

### Control Plane Integration
```python
from backend.core.kernel_restart_manager import kernel_restart_manager

# During boot, register all kernels
kernel_restart_manager.register_kernel(
    kernel_name="memory",
    restart_function=memory_kernel.initialize,
    critical=True
)

# Start monitoring
await kernel_restart_manager.start()
```

### Alert System Integration
```python
from backend.core.restart_alert_system import restart_alert_system

# Start during boot
await restart_alert_system.start()

# It automatically monitors all restart events
```

---

## 🔐 Safety Features

### 1. Max Restart Attempts
- Prevents infinite restart loops
- After 3 failures → requires manual intervention
- Prevents resource exhaustion

### 2. Restart Cooldown
- 30s minimum between restart attempts
- Gives system time to stabilize
- Prevents rapid restart cycling

### 3. Critical Kernel Alerts
- Marks important kernels as "critical"
- Sends high-priority alerts if critical kernel fails
- Escalates to system-level notification

### 4. Kill Switch Protection
- `manual_shutdown` flag prevents auto-restart
- Clear separation: crash vs manual stop
- Respects user intent

### 5. Alert History
- All restart events saved to files
- Persistent audit trail
- Easy to review what happened

---

## 📞 Commands Reference

### Windows
```bash
# Start with watchdog
start_grace.cmd

# Stop (kill switch)
stop_grace.cmd

# Control commands
grace.cmd start
grace.cmd stop
grace.cmd restart
grace.cmd status
grace.cmd watch
grace.cmd logs
```

### PowerShell
```powershell
# All commands
.\GRACE.ps1 start
.\GRACE.ps1 stop
.\GRACE.ps1 restart
.\GRACE.ps1 status
.\GRACE.ps1 watch
.\GRACE.ps1 logs
```

### Linux (systemd)
```bash
sudo systemctl start grace
sudo systemctl stop grace
sudo systemctl restart grace
sudo systemctl status grace
journalctl -u grace -f
```

### PM2 (All platforms)
```bash
pm2 start pm2.config.js
pm2 stop grace
pm2 restart grace
pm2 logs grace
pm2 monit
```

---

## 🎯 Resilience Strategy

```
┌─────────────────────────────────────────────┐
│         External Watchdog Layer             │
│  (grace_watchdog.py / PM2 / systemd)        │
│                                             │
│  Monitors: serve.py process                 │
│  Restarts: On crash (not manual stop)       │
│  Detects: Crash vs kill switch              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│            Grace Layer 1                    │
│      (Control Plane + Kernels)              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Internal Kernel Supervision            │
│   (kernel_restart_manager.py)               │
│                                             │
│  Monitors: Individual kernel heartbeats     │
│  Restarts: Failed kernels                   │
│  Alerts: Co-pilot on issues                 │
└─────────────────────────────────────────────┘
```

**Result:** Grace survives:
- ✅ Kernel crashes
- ✅ Process crashes
- ✅ System reboots
- ✅ Memory leaks (with max restarts)
- ✅ Network hiccups
- ⚠️ Manual stops (respects kill switch)

---

## 📧 Alert Integrations (Future)

The alert system is ready for:

```python
# Email notifications
async def _notify_copilot(self, alert, severity):
    if severity == "CRITICAL":
        await send_email(
            to="admin@example.com",
            subject=f"Grace Alert: {alert['event_type']}",
            body=alert['summary']
        )
```

```python
# Slack notifications
async def _notify_copilot(self, alert, severity):
    await post_to_slack(
        channel="#grace-alerts",
        message=alert['summary'],
        color="red" if severity == "CRITICAL" else "yellow"
    )
```

```python
# Discord webhook
async def _notify_copilot(self, alert, severity):
    await discord_webhook(
        url=DISCORD_WEBHOOK_URL,
        content=f"**{severity}**: {alert['summary']}"
    )
```

---

## 🎬 Demo

### Start Grace with Full Resilience
```bash
# Terminal 1
cd C:\Users\aaron\grace_2
start_grace.cmd

# Output:
# Starting Grace with Watchdog Supervisor
# ========================================
# 
# The watchdog will:
#   ✅ Keep Grace running
#   ✅ Auto-restart on crashes
#   ✅ Respect kill switch
#   ✅ Log all events
#   ✅ Alert on failures
#
# [WATCHDOG] GRACE WATCHDOG - Process Supervisor Starting
# [WATCHDOG] Starting Grace backend (serve.py)...
# [WATCHDOG] ✅ Grace started (PID: 12345)
#
# [RESTART-MGR] Kernel restart manager started
# [ALERT-SYS] Restart alert system monitoring active
#
# LAYER 1 BOOT COMPLETE - MULTI-OS INFRASTRUCTURE READY
# [INFRA] Infrastructure Manager tracking hosts:
#    [OK] aaron (windows) - healthy
```

### Simulate Crash
```bash
# Terminal 2
taskkill /F /PID 12345

# Terminal 1 shows:
# [WATCHDOG] ⚠️ Grace died unexpectedly after 45s
# [WATCHDOG] 🔄 Auto-restarting Grace (attempt 1)...
# [WATCHDOG] ✅ Grace started (PID: 12346)
# [ALERT-SYS] 📧 Alert sent: grace.restart.success
```

### Use Kill Switch
```bash
# Stop Grace intentionally
stop_grace.cmd

# Output:
# GRACE KILL SWITCH - Manual Stop
# ================================
# Setting manual shutdown flag...
# Stopping Grace process...
# ✅ Grace stopped (manual shutdown)
#    Watchdog will NOT auto-restart

# Watchdog shows:
# [WATCHDOG] ℹ️ Grace stopped manually - not auto-restarting
```

---

## 📊 Metrics

The system tracks:
- Total kernel restarts
- Total process restarts
- Restart reasons (heartbeat, crash, drift)
- Restart success rate
- Mean time between failures (MTBF)
- Mean time to recovery (MTTR)

---

## ✅ Checklist

- [x] Kernel restart manager created
- [x] External watchdog supervisor created
- [x] Alert system implemented
- [x] Kill switch vs crash detection
- [x] Windows control scripts
- [x] PowerShell control script
- [x] PM2 configuration
- [x] Systemd service file
- [x] Alert file system
- [x] Comprehensive documentation

---

## 🚀 Quick Start

**Just run:**
```bash
start_grace.cmd
```

Grace will:
1. Start with watchdog supervision
2. Monitor all kernels for heartbeats
3. Auto-restart failed kernels
4. Auto-restart whole process on crash
5. Respect kill switch for manual stops
6. Alert you on all restart events
7. Keep everything resilient

**Grace is now unbreakable!** 💪

---

*Created: November 14, 2025*  
*Status: Production Ready*  
*Resilience: Multi-Layer ✅*
