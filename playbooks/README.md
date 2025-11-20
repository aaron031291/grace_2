# Grace Autonomous Recovery Playbooks

This directory contains YAML playbooks that define Grace's autonomous remediation strategies. Each playbook is triggered automatically by specific error conditions and executes a series of steps to recover gracefully.

## Available Playbooks

### 1. Missing Module Recovery
**File:** `missing_module_recovery.yaml`  
**Trigger:** `ModuleNotFoundError`, `ImportError`, boot failures  
**Actions:**
- Detects missing Python modules
- Creates stub modules for optional dependencies
- Wraps imports in try/except for graceful degradation
- Opens coding-agent work orders for required packages
- Alerts Guardian with context

**Auto-Execute:** ✅ Yes (for optional modules)

---

### 2. Port Inventory Cleanup
**File:** `port_inventory_cleanup.yaml`  
**Trigger:** Dead ports detected, snapshot failures, hourly schedule  
**Actions:**
- Scans active ports in range 8000-8010
- Identifies stale port allocations
- Prunes dead allocations from registry
- Syncs watchdog monitor list to active ports
- Restarts port watchdog if needed

**Auto-Execute:** ✅ Yes  
**Schedule:** Hourly + on snapshot failure

---

### 3. GitHub Token Missing
**File:** `github_token_missing.yaml`  
**Trigger:** GitHub API rate limit warnings, missing token logs  
**Actions:**
- Checks secrets vault for stored token
- Falls back to .env file
- Prompts operator if not found (interactive mode)
- Writes token to .env securely
- Restarts GitHub miner
- Verifies 5000/hr rate limit activated

**Auto-Execute:** ✅ Yes (if token in vault)  
**Manual Prompt:** If vault empty

---

### 4. FAISS Lock Recovery
**File:** `faiss_lock_recovery.yaml`  
**Trigger:** "database is locked" errors, vector store API failures  
**Actions:**
- Identifies processes holding FAISS locks
- Attempts graceful unlock
- Restarts embedding service
- Force-unlocks if graceful fails
- Rebuilds index if corrupted
- Rechecks `/api/vectors/health`
- Escalates if lock persists after 3 attempts

**Auto-Execute:** ✅ Yes  
**Max Retries:** 3  
**Escalation:** After retry limit

---

### 5. Google Search Quota Exhaustion
**File:** `google_search_quota.yaml`  
**Trigger:** 429/403 errors, 95% quota threshold, manual command  
**Actions:**
- Pauses active remote-learning missions
- Switches search provider to fallback (Bing → DuckDuckGo → Mock)
- Preserves mission state for resume
- Notifies Guardian with quota status
- Resumes missions on fallback provider
- Schedules automatic restore when quota resets

**Auto-Execute:** ✅ Yes  
**Fallback Chain:** Google → Bing → DuckDuckGo → Mock

---

## Playbook Structure

Each playbook follows this YAML structure:

```yaml
name: playbook_name
version: 1.0.0
priority: high|medium|low

metadata:
  description: What this playbook does
  owner: guardian
  auto_trigger: true|false
  requires_approval: true|false

triggers:
  - type: exception|log_message|api_error|scheduled|manual
    pattern: error pattern
    severity: error|warning|info

conditions:
  - check: condition_expression
    reason: why this check is needed

steps:
  - name: step_name
    action: action_to_perform
    condition: when to run (optional)
    inputs:
      - input_vars
    operations:
      - operation_1
      - operation_2
    outputs:
      - output_vars

recovery:
  on_failure:
    - fallback actions
  on_success:
    - cleanup actions

metrics:
  track:
    - metric_names
  alert_thresholds:
    - condition: action
```

## How Playbooks Are Executed

1. **Trigger Detection**
   - Guardian monitors logs, exceptions, API responses
   - Playbook triggered when pattern matches

2. **Condition Checks**
   - All conditions must pass before execution
   - Prevents infinite loops and unsafe operations

3. **Step Execution**
   - Steps run sequentially
   - Each step can have conditional logic
   - Outputs from one step become inputs to next

4. **Recovery Handling**
   - On failure: rollback, restore backups, escalate
   - On success: cleanup, metrics update, continue

5. **Guardian Notification**
   - All playbook executions logged to immutable log
   - Guardian receives notifications with severity
   - Escalations create tickets for human operators

## Testing Playbooks

### Manual Trigger
```bash
# Trigger a specific playbook manually
python -m backend.playbook_engine execute missing_module_recovery

# Test with dry-run (no actual changes)
python -m backend.playbook_engine test missing_module_recovery --dry-run
```

### Monitor Execution
```bash
# Watch playbook execution logs
tail -f logs/playbooks/*.log

# Check immutable log for playbook events
grep "playbook" logs/immutable_audit.jsonl
```

### Metrics
```bash
# View playbook success rates
curl http://localhost:8000/api/playbooks/metrics

# Get specific playbook stats
curl http://localhost:8000/api/playbooks/missing_module_recovery/stats
```

## Creating New Playbooks

1. **Copy template** from existing playbook
2. **Define triggers** - when should it run?
3. **Set conditions** - safety checks before execution
4. **Write steps** - what actions to take
5. **Add recovery** - what to do on failure/success
6. **Test thoroughly** - dry-run mode first
7. **Document** - add to this README

## Best Practices

✅ **DO:**
- Make playbooks idempotent (safe to run multiple times)
- Include rollback steps in recovery section
- Log all actions to immutable log
- Test with dry-run before enabling auto-trigger
- Set appropriate retry limits
- Add clear escalation paths

❌ **DON'T:**
- Execute destructive actions without backups
- Auto-trigger during critical operations (boot, shutdown)
- Create infinite retry loops
- Skip condition checks
- Ignore escalation thresholds

## Integration with Guardian

All playbooks are orchestrated by Guardian:

```python
from backend.core.guardian import guardian
from backend.playbook_engine import playbook_registry

# Guardian automatically registers playbooks on boot
guardian.register_playbooks(playbook_registry.get_all())

# Playbooks trigger automatically based on system events
# Guardian monitors execution and handles escalations
```

## Monitoring Dashboard

View playbook activity:
- **Web UI:** http://localhost:8000/playbooks
- **API:** http://localhost:8000/api/playbooks/status
- **Logs:** `logs/playbooks/`

## Support

For issues or questions about playbooks:
1. Check logs in `logs/playbooks/`
2. Review immutable audit log
3. Contact Guardian via `/api/guardian/ask`
4. See full docs in `docs/playbooks/`
