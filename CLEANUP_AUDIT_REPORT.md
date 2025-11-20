# Cleanup Audit Report

## 1. Direct Event Publishing (`.publish()` calls)
**Found: 505+ occurrences**

### High-Priority Files (most calls):
- `backend/routes/chat_api.py` - Multiple publish calls
- `backend/world_model/world_model_service.py` - 10+ calls
- `backend/workflow_engines/commit_workflow.py` - 7 calls
- `backend/watchers/mission_watcher.py` - 5 calls
- `backend/security/input_sentinel.py` - 9 calls
- `backend/security/ethics_sentinel.py` - 4 calls
- `backend/services/` - Multiple files with publish calls
- `backend/self_heal/` - Multiple trigger publish calls

### Recommendation:
Replace direct `.publish()` with centralized event dispatch through unified event bus.

---

## 2. Governance Stub Duplicates
**Found: 2 occurrences**

### Locations:
- `backend/orchestrators/unified_grace_orchestrator.py:125` - `GovernanceKernel = StubComponent`
- `backend/orchestrators/unified_grace_orchestrator.py:140` - Multiple kernel stubs

### Recommendation:
Consolidate stub component definitions into a single location.

---

## 3. Learning Direct Writes
**Found: 0 direct matches**

Pattern searched: `learning.*\.write|direct.*learning.*write`

### Recommendation:
No immediate action needed. May need semantic search if pattern exists differently.

---

## 4. Duplicate Audit/Logging
**Found: 261+ occurrences**

### High-Usage Files:
- `backend/workflow_engines/parliament_engine.py` - Audit logging
- `backend/transcendence/business/` - Multiple files with ImmutableLog
- `backend/speech_tts/` - Audit log integration
- `backend/security/secrets_vault.py` - Extensive audit logging
- `backend/self_heal/runner.py` - Direct AuditLog model usage
- Schema files duplicated: `backend/schemas.py` + `backend/models/schemas.py`

### Recommendation:
Consolidate audit logging through single immutable log service. Remove duplicate schema definitions.

---

## 5. Duplicate Healing Triggers
**Found: 100+ references**

### Key Files with Redundant Trigger Logic:
- `backend/services/log_watcher.py:151` - `trigger_self_healing_on_error()`
- `backend/services/event_bus.py:116` - `trigger_healing_on_failure()`
- `backend/services/model_registry.py` - Multiple trigger methods
- `backend/misc/anomaly_watchdog.py` - Separate healing trigger
- `backend/misc/log_based_healer.py` - Duplicate healing logic
- `backend/core/error_recognition_system.py` - Another trigger path
- `backend/middleware/self_healing_middleware.py` - Yet another trigger

### Recommendation:
Consolidate all healing triggers through `backend/self_heal/intelligent_triggers.py` or unified trigger mesh.

---

## 6. Sandbox/Deployment Helpers
**Found: 446+ references**

### Redundant Sandbox Logic in:
- `backend/unified_logic/unified_logic_hub.py` - Sandbox validation
- `backend/ui_handlers/ide_websocket_handler.py` - Sandbox file operations
- `backend/transcendence/multi_modal_memory.py` - Separate sandbox root
- `backend/tests/routes/sandbox.py` - API endpoints
- `backend/routes/execution.py` - Sandboxed execution
- Multiple references to `sandbox_manager` import

### Recommendation:
Consolidate sandbox operations through single `sandbox_manager` service. Remove duplicate sandbox directories and helpers.

---

## 7. Business Ops Direct API Calls
**Pattern searched: No direct matches**

Would need to search for specific business API patterns (Stripe, payment processors, etc.)

### Recommendation:
Search for specific API client usage patterns in business logic files.

---

## 8. Per-Component Mode Flags
**Found: 947+ mode references** (includes model names, mixed results)

### Legitimate Mode Flags Found:
- `backend/workflow_engines/automation_engine.py:34` - `self.mode = 'manual'`
- `backend/workflow_engines/automation_engine.py:51` - Mode switching logic
- `backend/trust_framework/htm_anomaly_detector.py:119` - `self.learning_mode`
- `backend/routes/elite_systems_api.py:54` - `execution_mode: str = "auto"`

### Recommendation:
Review each component's mode flag and consolidate into unified configuration system.

---

## Summary Statistics

| Category | Count | Priority |
|----------|-------|----------|
| Direct .publish() calls | 505+ | HIGH |
| Governance stubs | 2 | MEDIUM |
| Learning direct writes | 0 | LOW |
| Audit/logging duplicates | 261+ | HIGH |
| Healing trigger duplicates | 100+ | HIGH |
| Sandbox helpers | 446+ | MEDIUM |
| Business API calls | TBD | MEDIUM |
| Mode flags | 5-10 | MEDIUM |

## Next Steps

1. **Immediate**: Consolidate event publishing through unified event bus
2. **High Priority**: Merge duplicate audit logging into single service
3. **High Priority**: Consolidate healing triggers into single trigger mesh
4. **Medium**: Unify sandbox operations through single manager
5. **Medium**: Remove governance stub duplicates
6. **Low**: Search for business API patterns with more specific queries
7. **Low**: Audit mode flags and consolidate into configuration
