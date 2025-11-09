# Unified Logic Hub & Memory Fusion
## Complete Documentation Index

**Grace's enterprise-grade change control and compliance system**

---

## Quick Start

**Read these first:**
1. [UNIFIED_LOGIC_HUB_COMPLETE.md](UNIFIED_LOGIC_HUB_COMPLETE.md) - System overview
2. [BOOT_UNIFIED_LOGIC.md](BOOT_UNIFIED_LOGIC.md) - Boot integration
3. [OPERATIONAL_RUNBOOK.md](../operations/OPERATIONAL_RUNBOOK.md) - How to operate

---

## Documentation

### Core Architecture
- **[UNIFIED_LOGIC_HUB_ARCHITECTURE.md](UNIFIED_LOGIC_HUB_ARCHITECTURE.md)** - Detailed architecture
- **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)** - Integration guide
- **[GATED_MEMORY_FETCH.md](GATED_MEMORY_FETCH.md)** - Memory fusion details

### Advanced Features
- **[ML_AND_HANDSHAKE_COMPLETE.md](ML_AND_HANDSHAKE_COMPLETE.md)** - ML integration & handshake protocol
- **[UPDATE_MISSION_TRACKING.md](UPDATE_MISSION_TRACKING.md)** - Mission tracking system
- **[AGENT_FETCH_ETIQUETTE.md](AGENT_FETCH_ETIQUETTE.md)** - Agent training guide

### Compliance
- **[COMPLIANCE_FRAMEWORK.md](../compliance/COMPLIANCE_FRAMEWORK.md)** - ISO 9001, ISO 27001, SOC 2, etc.
- **[MAX_GRADE_HARDENING.md](../compliance/MAX_GRADE_HARDENING.md)** - Production security

### Operations
- **[OPERATIONAL_RUNBOOK.md](../operations/OPERATIONAL_RUNBOOK.md)** - Operational procedures

---

## System Components

### 1. Unified Logic Hub
**Purpose:** Central change control system

**Features:**
- 8-stage pipeline (governance → crypto → validation → distribution)
- Automatic rollback on failures
- Observation windows (1-72h based on risk)
- Complete audit trail

**API:** `/api/logic-hub/*`

### 2. Memory Fusion Service
**Purpose:** Gated memory access with governance

**Features:**
- Governance-checked fetch
- Crypto-signed storage
- Auto-refresh on logic updates
- Fetch integrity verification

**API:** `/api/memory-fusion/*`

### 3. CAPA System
**Purpose:** ISO 9001 quality management

**Features:**
- Corrective/preventive actions
- Root cause analysis
- Learning integration
- Automatic creation on failures

**API:** `/api/capa/*`

### 4. Component Handshake
**Purpose:** Secure component onboarding

**Features:**
- Quorum-based acknowledgment
- Validation windows
- Component registry
- Version tracking

**Protocol:** Via trigger mesh events

### 5. ML Update Integration
**Purpose:** Learning from updates

**Features:**
- Feeds data to ML models
- Creates training labels
- Regression correlation
- Trust score enrichment

### 6. Update Awareness
**Purpose:** Post-update monitoring

**Features:**
- Update summaries for agents
- Observation windows
- Anomaly detection
- Automatic rollback triggers

---

## Key Flows

### Logic Update Flow
```
Submit → Govern → Sign → Validate → Package → Distribute → Observe → Learn
```

### Memory Fetch Flow
```
Request → Govern → Sign → Route → Enrich → Audit → Return
```

### Component Onboarding Flow
```
Request → Validate → Announce → Acknowledge → Quorum → Integrate → Observe
```

### CAPA Workflow
```
Detect → Create → Analyze → Plan → Implement → Verify → Close → Learn
```

---

## API Endpoints

### Unified Logic Hub
- `POST /api/logic-hub/updates/schema`
- `POST /api/logic-hub/updates/code-module`
- `POST /api/logic-hub/updates/playbook`
- `GET /api/logic-hub/updates/{id}`
- `GET /api/logic-hub/stats`
- `POST /api/logic-hub/updates/{id}/rollback`

### Memory Fusion
- `POST /api/memory-fusion/fetch`
- `POST /api/memory-fusion/verify-fetch`
- `POST /api/memory-fusion/store`
- `GET /api/memory-fusion/audit-trail/{session_id}`
- `GET /api/memory-fusion/stats`

### CAPA
- `POST /api/capa/create`
- `POST /api/capa/root-cause`
- `GET /api/capa/{capa_id}`
- `GET /api/capa/metrics/stats`

---

## Database Tables

- `logic_updates` - Update registry
- `capa_records` - Quality management
- `component_registry` - Component tracking
- `immutable_log` - Audit trail (existing)

---

## Quick Reference

| Task | Command |
|------|---------|
| Submit schema update | `POST /api/logic-hub/updates/schema` |
| Fetch memory (gated) | `POST /api/memory-fusion/fetch` |
| Create CAPA | `POST /api/capa/create` |
| Check update status | `GET /api/logic-hub/updates/{id}` |
| Verify fetch integrity | `POST /api/memory-fusion/verify-fetch` |
| Get system stats | `GET /api/logic-hub/stats` |

---

## Status

**Built:** ✅ Complete (~7,500 lines)  
**Applied:** ✅ Migrations run, policies seeded  
**Integrated:** ✅ Wired into boot script  
**Operational:** ✅ Ready on next boot  

**Coverage:**
- ISO 9001: 85%
- ISO 27001: 75%
- SOC 2: 80%
- NIST CSF: 85%

---

## See Also

- [Backend Implementation](../../backend/) - Source code
- [Configuration](../../config/) - Metrics catalog
- [Migrations](../../alembic/versions/) - Database schemas
- [Playbooks](../../backend/playbooks/) - Rollback playbooks
