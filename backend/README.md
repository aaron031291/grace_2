# Backend Directory Structure

## Organized Subdirectories

### Core Systems
- **`core/`** - Layer 1 kernels, message bus, orchestration
- **`kernels/`** - Domain-specific kernels
- **`middleware/`** - Request/response middleware

### Models & Data
- **`models/`** - Data models, schemas (21 files)
- **`database_files/`** - SQLite databases (5 files)
- **`memory_services/`** - Memory management (11 files)
- **`memory_tables/`** - Memory table definitions

### Agents & Intelligence
- **`agents/`** - Agent implementations
- **`agents_core/`** - Core agent systems (9 files)
- **`grace_components/`** - Grace-specific components (9 files)
- **`agentic/`** - Agentic architecture

### Execution & Workflows
- **`workflow_engines/`** - Workflow execution engines (13 files)
- **`execution/`** - Task execution (5 files)
- **`orchestrators/`** - System orchestrators (6 files)

### Intelligence & Learning
- **`ml_training/`** - ML model training (11 files)
- **`learning_systems/`** - Learning loops (6 files)
- **`cognition/`** - Cognitive systems
- **`temporal/`** - Temporal reasoning (7 files)

### Governance & Security
- **`governance/`** - Governance framework
- **`governance_system/`** - Governance engines (3 files)
- **`parliament_system/`** - Parliamentary governance
- **`security/`** - Security systems (6 files)
- **`hunter.py`** - Threat detection

### Services
- **`routes/`** - API routes
- **`api/`** - API definitions
- **`services/`** - Business services
- **`ingestion_services/`** - Ingestion pipeline (3 files)

### Monitoring & Observability
- **`monitoring/`** - Metrics and monitoring (10 files)
- **`health/`** - Health checks
- **`logging/`** - Logging systems (7 files)

### Integration & Communication
- **`integration_layer/`** - System integrations (4 files)
- **`communication/`** - WebSockets, notifications (6 files)
- **`integrations/`** - External integrations

### Automation & Optimization
- **`automation/`** - Automation systems
- **`autonomy/`** - Autonomous agents (12 files)
- **`optimization/`** - Performance optimization
- **`self_heal/`** - Self-healing systems

### Supporting Systems
- **`boot/`** - Boot and startup (10 files)
- **`config/`** - Configuration (4 files)
- **`utilities/`** - Helper utilities (3 files)
- **`capabilities/`** - Capability management (4 files)
- **`meta_systems/`** - Meta-level systems (2 files)

### Testing & Validation
- **`test_files/`** - Backend tests (14 files)
- **`tests/`** - Test suites
- **`verification_system/`** - Verification tools (5 files)
- **`verification/`** - Verification framework

### Specialized
- **`knowledge/`** - Knowledge management (10 files)
- **`analysis_tools/`** - Analysis utilities (2 files)
- **`data_services/`** - Data handling (3 files)
- **`speech_tts/`** - Speech and TTS (1 file)
- **`crypto/`** - Cryptography (2 files)
- **`plugins/`** - Plugin system (1 file)
- **`reporting/`** - Reporting tools (4 files)

### Other
- **`processors/`** - Data processors
- **`collectors/`** - Data collectors
- **`databases/`** - Database management
- **`domains/`** - Domain logic
- **`executors/`** - Execution engines
- **`external_apis/`** - External API clients
- **`playbooks/`** - Playbook definitions
- **`remote_access/`** - Remote access
- **`routers/`** - Routing
- **`subsystems/`** - Subsystems
- **`transcendence/`** - Transcendence layer
- **`clarity/`** - Clarity framework
- **`cli/`** - CLI tools
- **`collaboration/`** - Collaboration tools
- **`data_cube/`** - Data cube
- **`mission_control/`** - Mission control

### Miscellaneous
- **`misc/`** - Miscellaneous files (60 files)
- **`batch_scripts/`** - Batch scripts (2 files)
- **`documentation/`** - Backend docs (15 files)
- **`seed_data/`** - Seed data scripts (8 files)

### Core Files (Root)
- `requirements.txt` - Python dependencies
- `__init__.py` - Package initialization

---

**Total:** 180+ files organized into 50+ logical subdirectories
**Root files:** Reduced from 180+ to 2 essential files
