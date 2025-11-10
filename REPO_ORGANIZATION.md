# Repository Organization - Clean Structure

**All unified logic documentation now organized in `/docs`**

---

## Documentation Structure

### `/docs/unified_logic/` - Unified Logic Hub System
```
README.md                          - Index and quick start
UNIFIED_LOGIC_HUB_COMPLETE.md     - Complete overview
UNIFIED_LOGIC_HUB_ARCHITECTURE.md - Detailed architecture
INTEGRATION_COMPLETE.md            - Integration guide
GATED_MEMORY_FETCH.md             - Memory fusion details
ML_AND_HANDSHAKE_COMPLETE.md      - ML & handshake protocol
UPDATE_MISSION_TRACKING.md         - Mission tracking
BOOT_UNIFIED_LOGIC.md             - Boot integration
AGENT_FETCH_ETIQUETTE.md          - Agent training guide
```

### `/docs/compliance/` - Compliance & Security
```
COMPLIANCE_FRAMEWORK.md           - Multi-standard mapping (ISO 9001/27001, SOC 2, etc.)
MAX_GRADE_HARDENING.md            - Production security guide
```

### `/docs/operations/` - Operational Procedures
```
OPERATIONAL_RUNBOOK.md            - Complete ops guide
```

### `/docs/status_archive/` - Historical Status
```
APPLICATION_COMPLETE.md           - Application status
COMPLETE_BUILD_AND_APPLY.md       - Build & apply status
SYSTEM_STATUS.md                  - System verification
```

---

## Code Structure

### `/backend/` - Core Implementation

#### Unified Logic System
```
unified_logic_hub.py              - Central orchestrator (600 lines)
memory_fusion_service.py          - Gated memory access (650 lines)
logic_update_awareness.py         - Observation windows (500 lines)
ml_update_integration.py          - ML learning integration (500 lines)
component_handshake.py            - Onboarding protocol (600 lines)
capa_system.py                    - Quality management (450 lines)
handshake_subscribers.py          - Auto-ack handlers (180 lines)
watchdog_integration.py           - Anomaly handling (150 lines)
```

#### API Routes
```
routes/unified_logic_hub_api.py   - Logic hub endpoints (300 lines)
routes/memory_fusion_api.py       - Memory fusion endpoints (300 lines)
routes/capa_api.py                - CAPA endpoints (180 lines)
```

#### Database Models
```
base_models.py                    - LogicUpdateRecord, CAPARecord, ComponentRegistration
```

### `/alembic/versions/` - Database Migrations
```
20251109_120000_add_logic_update_record.py    - Logic updates table
20251109_130000_add_capa_and_components.py    - CAPA & registry tables
```

### `/config/` - Configuration
```
metrics_catalog.yaml              - Metrics with playbook_id, risk_level, etc.
```

### `/backend/playbooks/` - Operational Playbooks
```
logic_update_rollback.yaml        - Automatic rollback playbook
```

---

## Root Directory (Clean)

### Essential Files
```
GRACE.ps1                         - Main boot script
README.md                         - Project readme
QUICK_START.md                    - Quick start guide
.env.example                      - Environment template
alembic.ini                       - Migration config
docker-compose.yml                - Container orchestration
```

### Boot Scripts
```
GRACE.ps1                         - Main boot (includes unified logic init)
GRACE_SAFE.ps1                    - Safe mode boot
GRACE_backup.ps1                  - Backup script
BOOT_GRACE_REAL.ps1              - Alternative boot
```

### Documentation Index
```
START_HERE.md                     - Where to begin
REPO_STRUCTURE.md                 - Repository layout
QUICK_START.md                    - Getting started
```

---

## Folder Structure

```
grace_2/
├── backend/                      # Core implementation
│   ├── routes/                   # API endpoints
│   │   ├── unified_logic_hub_api.py
│   │   ├── memory_fusion_api.py
│   │   └── capa_api.py
│   ├── playbooks/                # YAML playbooks
│   │   └── logic_update_rollback.yaml
│   ├── unified_logic_hub.py      # Unified logic core
│   ├── memory_fusion_service.py  # Memory fusion
│   ├── capa_system.py            # CAPA system
│   ├── component_handshake.py    # Handshake protocol
│   ├── ml_update_integration.py  # ML integration
│   └── watchdog_integration.py   # Watchdog hooks
│
├── docs/                         # Documentation
│   ├── unified_logic/            # Unified logic docs
│   │   ├── README.md
│   │   ├── UNIFIED_LOGIC_HUB_COMPLETE.md
│   │   ├── INTEGRATION_COMPLETE.md
│   │   ├── GATED_MEMORY_FETCH.md
│   │   ├── ML_AND_HANDSHAKE_COMPLETE.md
│   │   └── AGENT_FETCH_ETIQUETTE.md
│   ├── compliance/               # Compliance docs
│   │   ├── COMPLIANCE_FRAMEWORK.md
│   │   └── MAX_GRADE_HARDENING.md
│   ├── operations/               # Ops guides
│   │   └── OPERATIONAL_RUNBOOK.md
│   └── status_archive/           # Historical status
│       ├── APPLICATION_COMPLETE.md
│       └── COMPLETE_BUILD_AND_APPLY.md
│
├── alembic/                      # Database migrations
│   └── versions/
│       ├── 20251109_120000_add_logic_update_record.py
│       └── 20251109_130000_add_capa_and_components.py
│
├── config/                       # Configuration
│   └── metrics_catalog.yaml
│
├── databases/                    # SQLite databases
│   └── grace.db
│
└── GRACE.ps1                     # Main boot script
```

---

## Navigation Guide

### I Want To...

**Understand the unified logic system**
→ Read `/docs/unified_logic/README.md`

**Start Grace with unified logic**
→ Run `.\GRACE.ps1`

**Check compliance status**
→ Read `/docs/compliance/COMPLIANCE_FRAMEWORK.md`

**Operate Grace in production**
→ Read `/docs/operations/OPERATIONAL_RUNBOOK.md`

**Train agents on fetch protocol**
→ Read `/docs/unified_logic/AGENT_FETCH_ETIQUETTE.md`

**Implement a new subsystem**
→ Read `/docs/unified_logic/ML_AND_HANDSHAKE_COMPLETE.md` (handshake protocol)

**Troubleshoot issues**
→ Read `/docs/operations/OPERATIONAL_RUNBOOK.md` (troubleshooting section)

---

## File Counts

**Implementation:**
- Backend code: 8 files (~3,500 lines)
- API routes: 3 files (~780 lines)
- Database migrations: 2 files (~200 lines)
- Playbooks: 1 file (~100 lines)

**Documentation:**
- Unified logic docs: 9 files (~15,000 words)
- Compliance docs: 2 files (~8,000 words)
- Operations docs: 1 file (~3,000 words)

**Total:** 26 files, ~4,600 lines of code, ~26,000 words of documentation

---

## Quick Links

| Resource | Path |
|----------|------|
| **Main README** | `/README.md` |
| **Unified Logic Index** | `/docs/unified_logic/README.md` |
| **Boot Script** | `/GRACE.ps1` |
| **Operations Guide** | `/docs/operations/OPERATIONAL_RUNBOOK.md` |
| **Compliance Status** | `/docs/compliance/COMPLIANCE_FRAMEWORK.md` |
| **API Docs** | `http://localhost:8000/docs` (when running) |

---

## Summary

✅ **Documentation organized** into logical folders  
✅ **Code structured** by functionality  
✅ **Migrations tracked** in alembic  
✅ **Config centralized** in /config  
✅ **Clean root directory** with essential files only  

**Result:** Professional repository structure ready for production and compliance audits.
