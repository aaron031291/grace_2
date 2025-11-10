# Grace Self-Healing System

## 🏥 Overview

Grace monitors her own health, detects failures, and automatically repairs herself while maintaining full audit trails and governance compliance.

## 🔍 Health Monitoring

### Components Monitored (Every 30s)
1. **Reflection Service** - Checks if running + last reflection age
2. **Database** - Ping latency, connection status
3. **Task Executor** - Worker count, queue status
4. **Trigger Mesh** - Event routing operational

### Health Status Levels
- **ok** - Operating normally
- **warn** - Degraded performance
- **critical** - Component failure

## ⚕️ Automatic Remediation

### Healing Rules

**Reflection Service Failure**
```
If: Not running OR last reflection > 2 minutes old
Then: Stop → Restart reflection service
Log: healing_actions table
Result: success/failed
```

**Task Executor Failure**
```
If: Worker count = 0
Then: Stop workers → Restart with 3 workers
Log: healing_actions table
```

**Database Connection Issues**
```
If: Latency > 1000ms OR connection failed
Then: Switch to read_only mode
Notify: via Trigger Mesh
Prevent: Write operations until recovered
```

**Trigger Mesh Failure**
```
If: Not running
Then: Restart + resubscribe all handlers
Log: healing_actions table
```

### Consecutive Failure Handling
- Track failures per component
- After 2 consecutive failures → Attempt healing
- After healing → Reset counter on success
- If healing fails → Enter safe mode

## 🛡️ Fallback Modes

### System Modes
1. **normal** - Full operation
2. **read_only** - No writes (DB issues)
3. **observation_only** - Monitor but don't act
4. **emergency** - Critical failure, minimal operation

### Mode Transitions
```
Normal → Read-Only (DB issues)
Normal → Observation-Only (Repeated healing failures)
Any → Emergency (Critical security event)
```

### Mode Enforcement
- Checked before write operations
- API endpoints respect current mode
- Mode changes logged immutably
- Governance required for mode changes

## 📊 API Endpoints

### Status & Monitoring
```bash
GET /api/health/status
# Returns: system_mode, health_checks[], healing_actions[]
```

### Manual Control
```bash
POST /api/health/restart
Body: {"component": "reflection_service"}
# Requires: Governance approval
# Returns: success/failed + details
```

### Mode Management
```bash
GET /api/health/mode
# Returns: current mode, reason, changed_at

POST /api/health/mode
Body: {"mode": "read_only", "reason": "maintenance"}
# Requires: Governance approval
```

## 🔄 Integration with Other Systems

### Trigger Mesh
```
Health check fails
  → Event: "health.component_failed"
  → Subscribers: Governance, Hunter, Meta-loop
  → Healing attempted
  → Event: "health.healing_attempted"
  → Result logged
```

### Governance
```
Healing action proposed
  → Policy check: "manual_restart"
  → If critical component → Requires approval
  → Audit logged
  → Action executed
```

### Hunter Protocol
```
Repeated failures detected
  → Hunter checks: Is this an attack?
  → Security event logged
  → If suspicious → Block + alert
```

### Meta-Loop
```
Healing success rate tracked
  → Meta-analysis: "Healing effectiveness"
  → If rate < 50% → Recommendation
  → Meta-meta: Measures improvement
```

## 📈 Metrics Tracked

- Component uptime %
- Healing success rate
- Time to recovery (MTTR)
- Consecutive failure count
- Mode transition frequency

## 🧪 Testing

### Simulate Failures
```python
# Test reflection service failure
reflection_service._running = False
await health_monitor.check_all_components()
# Expect: Healing action logged, service restarted
```

### Test Mode Transitions
```python
system_state.mode = "read_only"
# Try write operation
# Expect: Blocked or queued
```

## 🎯 Example Scenarios

### Scenario 1: Reflection Service Hangs
```
Time: 12:00 - Reflection loop hangs
12:00:30 - Health check: critical (stale reflection)
12:01:00 - Health check: critical (2nd failure)
12:01:00 - Healing: Restart reflection service
12:01:05 - Health check: ok (service recovered)
12:01:05 - Counter reset
Result: Self-healed in 65 seconds
```

### Scenario 2: Database Connection Lost
```
Time: 14:00 - DB connection fails
14:00:30 - Health check: critical
14:01:00 - Health check: critical (2nd failure)
14:01:00 - Healing: Enter read_only mode
14:01:00 - Trigger Mesh: "health.mode_changed"
14:05:00 - DB recovers
14:05:30 - Health check: ok
14:05:30 - Mode: Back to normal
Result: Graceful degradation, no data loss
```

### Scenario 3: Suspicious Repeated Failures
```
Time: 16:00 - Task executor fails
16:00:30 - Healing: Restart workers (success)
16:05:00 - Task executor fails again
16:05:30 - Healing: Restart workers (success)
16:10:00 - Task executor fails again (3rd time)
16:10:01 - Hunter: Suspicious pattern detected
16:10:01 - Security event logged
16:10:01 - Governance: Block further restarts
16:10:01 - Mode: Observation-only
16:10:01 - Task created: "Investigate task executor issues"
Result: Prevented potential attack, human review required
```

## ✅ Current Status

✅ Health monitoring every 30 seconds
✅ Automatic component restart
✅ Fallback mode system
✅ Governed manual control
✅ Complete audit trail
✅ Integration with all subsystems

Grace now maintains herself autonomously while staying secure and auditable! ⚕️🔒
