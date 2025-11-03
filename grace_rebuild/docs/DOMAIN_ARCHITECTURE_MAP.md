# Grace 10-Domain Architecture Map

Complete mapping of backend components to domains with API endpoints, CLI commands, and metric publishers.

---

## 1. CORE – Platform Operations & Governance 💓

### Backend Components
```
├── governance.py                    # Policy engine, rule evaluation
├── governance_models.py             # Policy DB schemas
├── seed_governance_policies.py      # Default policies
├── self_healing.py                  # Health monitor, auto-recovery
├── self_healing_cli.py              # CLI for healing triggers
├── verification.py                  # Cryptographic verification
├── verification_middleware.py       # Request verification layer
├── verification_integration.py      # Cross-system verification
├── immutable_log.py                 # Audit trail for all actions
├── trigger_mesh.py                  # Event bus connecting domains
├── tests/routes/health_routes.py    # Health check endpoints
├── issue_models.py                  # Incident tracking models
```

### API Endpoints
```python
GET  /health                         # Quick health check
GET  /api/health/status              # Detailed health with subsystems
GET  /api/verification/audit         # Verification audit log
GET  /api/verification/stats         # Verification statistics
GET  /api/verification/failed        # Failed verifications
POST /api/governance/evaluate        # Evaluate policy compliance
GET  /api/governance/policies        # List active policies
POST /api/self-healing/trigger       # Manual healing trigger
GET  /api/issues                     # List incidents
```

### CLI Commands
```bash
grace core heartbeat                 # Platform heartbeat check
grace core governance                # Governance status
grace core self-heal                 # Trigger self-healing
grace core policies                  # List governance policies
grace core verify                    # Run verification audit
```

### Metrics Published
- `uptime` - System uptime percentage
- `governance_score` - Policy compliance score
- `healing_actions` - Auto-healing actions taken
- `verification_failures` - Failed verification count
- `event_bus_latency` - Trigger mesh latency

### Dependencies
- Used by: ALL domains (shared infrastructure)
- Calls: None (foundation layer)

---

## 2. TRANSCENDENCE – Agentic Development Partner 🧠

### Backend Components
```
├── agentic/
│   ├── orchestrator.py              # Multi-agent task orchestration
│   ├── subagents.py                 # Specialized sub-agents
│   └── tools.py                     # Agent tooling
├── code_generator.py                # Code generation engine
├── code_understanding.py            # AST analysis, intent extraction
├── dev_workflow.py                  # Automated development workflow
├── grace_architect_agent.py         # Architecture design agent
├── code_memory.py                   # Pattern recognition & storage
├── memory_service.py                # Memory search & retrieval
├── memory_models.py                 # Memory DB schemas
├── seed_code_memory.py              # Pattern seeding
├── transcendence/
│   ├── api.py                       # Transcendence API router
│   ├── cognitive_observatory.py     # Cognition monitoring
│   ├── integration_hub.py           # Cross-domain integration
│   ├── ml_integration.py            # ML-powered features
│   ├── multi_modal_memory.py        # Multi-modal memory system
│   ├── self_awareness.py            # Self-reflection capabilities
│   ├── unified_intelligence.py      # Intelligence aggregation
│   └── voice_integration.py         # Voice interface
├── ide_websocket_handler.py         # IDE real-time comms
├── grace_ide/                       # IDE implementation
├── tests/routes/coding_agent_api.py # Coding agent endpoints
├── routes/grace_architect_api.py    # Architect agent endpoints
├── tests/routes/memory_api.py       # Memory API endpoints
```

### API Endpoints
```python
POST /api/transcendence/plan         # Create task plan
POST /api/transcendence/generate     # Generate code
POST /api/transcendence/understand   # Analyze code intent
GET  /api/transcendence/memory/search # Search code patterns
POST /api/transcendence/memory/seed  # Seed new patterns
GET  /api/coding-agent/status        # Agent status
POST /api/coding-agent/execute       # Execute coding task
GET  /api/architect/design           # Architecture recommendations
POST /api/architect/review           # Review architecture
GET  /api/memory/patterns            # Retrieve patterns
POST /api/memory/learn               # Learn from code
```

### CLI Commands
```bash
grace transcendence plan "build auth system"    # Plan task
grace transcendence generate spec.md            # Generate code
grace transcendence memory "jwt patterns"       # Search memory
grace transcendence architect review ./src      # Architecture review
grace transcendence ide connect                 # Connect IDE
```

### Metrics Published
- `task_success` - Task completion rate
- `code_quality` - Generated code quality score
- `memory_recall` - Pattern recall accuracy
- `planning_accuracy` - Plan vs. execution alignment
- `architecture_score` - Architecture quality metric

### Dependencies
- Uses: Core (governance, verification), Knowledge (patterns), Security (Hunter scans)
- Calls: ML (quality prediction), Temporal (impact analysis), Parliament (approvals)

---

## 3. KNOWLEDGE – Ingestion & Business Intelligence 📚

### Backend Components
```
├── ingestion_service.py             # Knowledge ingestion pipeline
├── knowledge.py                     # Knowledge management
├── knowledge_models.py              # Knowledge DB schemas
├── trusted_sources.py               # Source trust scoring
├── memory.py                        # General memory system
├── summaries.py                     # Knowledge summarization
├── evaluation.py                    # Knowledge evaluation
├── tests/routes/trust_api.py        # Trust scoring API
├── clarifier.py                     # Knowledge clarification
```

### API Endpoints
```python
POST /api/knowledge/ingest           # Ingest new knowledge
GET  /api/knowledge/search           # Search knowledge base
GET  /api/knowledge/sources          # List trusted sources
GET  /api/trust/score/{source_id}    # Get trust score
POST /api/trust/evaluate             # Evaluate source trust
GET  /api/knowledge/summaries        # Retrieve summaries
POST /api/knowledge/clarify          # Clarify ambiguous knowledge
GET  /api/evaluation/metrics         # Knowledge quality metrics
```

### CLI Commands
```bash
grace knowledge ingest source.pdf              # Ingest knowledge
grace knowledge search "authentication best"   # Search knowledge
grace knowledge trust                          # View trust scores
grace knowledge sources                        # List trusted sources
grace knowledge evaluate                       # Evaluate quality
```

### Metrics Published
- `trust_score` - Overall trust score
- `ingestion_rate` - Documents ingested/hour
- `recall_accuracy` - Search recall accuracy
- `source_diversity` - Source variety metric
- `knowledge_freshness` - Average age of knowledge

### Dependencies
- Uses: Core (verification), ML (trust classifiers)
- Calls: Transcendence (pattern extraction), Temporal (trend analysis)

---

## 4. SECURITY – Hunter Threat Detection 🛡️

### Backend Components
```
├── hunter.py                        # Threat detection engine
├── hunter_integration.py            # Hunter integrations
├── seed_hunter_rules.py             # Default security rules
├── auto_quarantine.py               # Automatic quarantine
├── auto_fix.py                      # Automatic remediation
├── ide_security.py                  # IDE sandbox security
├── constitutional_engine.py         # Constitutional AI safety
├── constitutional_models.py         # Constitution DB schemas
├── constitutional_verifier.py       # Constitutional verification
├── seed_constitution.py             # AI constitution seeding
├── tests/routes/constitutional_api.py # Constitution API
```

### API Endpoints
```python
POST /api/hunter/scan                # Run security scan
GET  /api/hunter/rules               # List security rules
GET  /api/hunter/alerts              # Active alerts
POST /api/hunter/quarantine          # Quarantine threat
GET  /api/hunter/quarantined         # View quarantined items
POST /api/hunter/auto-fix            # Trigger auto-fix
GET  /api/constitutional/status      # Constitutional compliance
POST /api/constitutional/verify      # Verify against constitution
GET  /api/constitutional/rules       # List constitutional rules
```

### CLI Commands
```bash
grace security scan ./code                 # Scan for threats
grace security rules                       # View security rules
grace security alerts                      # View active alerts
grace security quarantine                  # List quarantined items
grace security constitutional              # Constitutional status
```

### Metrics Published
- `threats_detected` - Threats found
- `scan_coverage` - Code coverage percentage
- `response_time` - Threat response time (seconds)
- `false_positive_rate` - False positive rate
- `auto_fix_success` - Auto-fix success rate

### Dependencies
- Uses: Core (governance, verification), Transcendence (code analysis)
- Calls: ML (threat classification), Parliament (rule approval)

---

## 5. ML – Machine Learning Platform 🤖

### Backend Components
```
├── training_pipeline.py             # Training orchestration
├── train_trust_model.py             # Trust score model training
├── train_alert_model.py             # Alert classification training
├── ml_runtime.py                    # Inference runtime
├── model_deployment.py              # Model deployment engine
├── ml_classifiers.py                # ML classifiers
├── ml_models_table.py               # Model registry DB
├── auto_retrain.py                  # Auto-retraining engine
├── validate_ml_system.py            # ML system validation
├── mldl.py                          # ML/DL utilities
├── learning.py                      # Learning algorithms
├── tests/routes/ml_api.py           # ML API endpoints
├── transcendence/ml_integration.py  # ML-Transcendence bridge
```

### API Endpoints
```python
POST /api/ml/train                   # Start training run
POST /api/ml/deploy                  # Deploy model
GET  /api/ml/models                  # List models
GET  /api/ml/model/{id}              # Get model details
POST /api/ml/inference               # Run inference
GET  /api/ml/evaluate/{id}           # Evaluate model
POST /api/ml/retrain/{id}            # Trigger retrain
GET  /api/ml/metrics                 # Training metrics
```

### CLI Commands
```bash
grace ml train trust_model              # Train model
grace ml deploy model_123 --show-conf   # Deploy with confidence
grace ml list                           # List models
grace ml evaluate model_123             # Evaluate model
grace ml retrain model_123              # Retrain model
```

### Metrics Published
- `model_accuracy` - Model accuracy score
- `deployment_success` - Deployment success rate
- `inference_latency` - Inference latency (ms)
- `training_efficiency` - Training time/epoch
- `auto_retrain_triggers` - Auto-retrain trigger count

### Dependencies
- Uses: Core (verification), Knowledge (training data)
- Calls: Temporal (trend prediction), Parliament (model approval)

---

## 6. TEMPORAL – Causal Reasoning & Forecasting ⏰

### Backend Components
```
├── causal.py                        # Causal event logging
├── causal_graph.py                  # Causal graph construction
├── causal_analyzer.py               # Impact analysis
├── temporal_reasoning.py            # Temporal prediction engine
├── temporal_models.py               # Temporal DB schemas
├── simulation_engine.py             # What-if simulations
├── tests/routes/causal_graph_api.py # Causal graph API
├── tests/routes/temporal_api.py     # Temporal API
```

### API Endpoints
```python
GET  /api/causal/graph               # View causal graph
POST /api/causal/event               # Log causal event
GET  /api/causal/impact/{change_id}  # Analyze impact
POST /api/temporal/forecast          # Generate forecast
POST /api/temporal/simulate          # Run simulation
GET  /api/temporal/trends            # View temporal trends
GET  /api/temporal/predictions       # Active predictions
```

### CLI Commands
```bash
grace temporal graph                    # View causal graph
grace temporal simulate "remove auth"   # Run simulation
grace temporal forecast deployments     # Forecast metric
grace temporal trends                   # View trends
```

### Metrics Published
- `prediction_accuracy` - Forecast accuracy
- `graph_completeness` - Causal graph coverage
- `sim_quality` - Simulation quality score
- `event_latency` - Event processing latency
- `impact_precision` - Impact prediction precision

### Dependencies
- Uses: Core (event bus), Knowledge (historical data)
- Calls: ML (prediction models), Parliament (decision impact)

---

## 7. PARLIAMENT – Governance & Meta-Loop 🏛️

### Backend Components
```
├── parliament_engine.py             # Voting & consensus engine
├── parliament_models.py             # Parliament DB schemas
├── seed_parliament.py               # Parliament initialization
├── meta_loop.py                     # Meta-loop core
├── meta_loop_engine.py              # Meta-loop orchestration
├── meta_loop_approval.py            # Approval workflows
├── seed_meta_governance.py          # Meta-governance seeding
├── grace_parliament_agent.py        # Parliament agent
├── reflection.py                    # System reflection
├── tests/routes/parliament_api.py   # Parliament API
├── tests/routes/meta_api.py         # Meta-loop API
```

### API Endpoints
```python
GET  /api/parliament/votes           # Active votes
POST /api/parliament/vote            # Cast vote
GET  /api/parliament/results/{id}    # Vote results
GET  /api/meta/recommendations       # Meta-loop recommendations
POST /api/meta/approve               # Approve recommendation
GET  /api/meta/metrics               # Meta-loop metrics
GET  /api/parliament/compliance      # Compliance dashboard
POST /api/reflection/trigger         # Trigger reflection
```

### CLI Commands
```bash
grace parliament vote                   # View active votes
grace parliament recommendations        # Meta-loop recommendations
grace parliament compliance             # Compliance dashboard
grace parliament history                # Vote history
```

### Metrics Published
- `vote_participation` - Vote participation rate
- `recommendation_adoption` - Recommendation adoption rate
- `compliance_score` - Compliance score
- `reflection_quality` - Reflection quality metric
- `meta_convergence` - Meta-loop convergence rate

### Dependencies
- Uses: Core (governance), ALL domains (analyzes cross-domain performance)
- Calls: Temporal (impact forecasting), ML (optimization suggestions)

---

## 8. FEDERATION – External Integration & Collaboration 🌐

### Backend Components
```
├── external_apis/
│   ├── github_connector.py          # GitHub integration
│   ├── slack_connector.py           # Slack integration
│   └── aws_connector.py             # AWS integration
├── secrets_vault.py                 # Secrets management
├── grace_external_agent.py          # External agent coordinator
├── plugin_system.py                 # Plugin framework
├── execution_engine.py              # Execution isolation
├── sandbox_manager.py               # Sandbox management
├── sandbox_models.py                # Sandbox DB schemas
├── tests/routes/external_api_routes.py # External API routes
├── tests/routes/plugin_routes.py    # Plugin routes
├── tests/routes/websocket_routes.py # WebSocket routes
├── websocket_manager.py             # WebSocket manager
```

### API Endpoints
```python
GET  /api/federation/connectors      # List connectors
POST /api/federation/github/sync     # Sync with GitHub
POST /api/federation/slack/notify    # Send Slack notification
GET  /api/secrets/list               # List secrets (metadata)
POST /api/secrets/store              # Store secret
POST /api/plugins/install            # Install plugin
GET  /api/plugins/list               # List plugins
POST /api/sandbox/create             # Create sandbox
POST /api/sandbox/execute            # Execute in sandbox
WS   /ws/external                    # External WebSocket
```

### CLI Commands
```bash
grace federation connectors             # List connectors
grace federation secrets                # Manage secrets
grace federation github sync            # Sync with GitHub
grace federation slack send "message"   # Send Slack message
grace federation plugins                # List plugins
```

### Metrics Published
- `connector_health` - Connector health score
- `api_success` - API call success rate
- `secret_rotation` - Secret rotation compliance
- `plugin_uptime` - Plugin uptime
- `sandbox_isolation` - Sandbox isolation score

### Dependencies
- Uses: Core (verification), Security (secret scanning)
- Calls: Knowledge (external data ingestion), Temporal (API trend analysis)

---

## 9. COGNITION – Real-time Intelligence Dashboard 🧠📊

### Backend Components
```
├── cognition/
│   └── example_usage.py             # Cognition examples
├── cognition_metrics.py             # Metrics aggregation engine
├── routers/cognition.py             # Cognition API router
├── transcendence/cognitive_observatory.py # Observatory
├── transcendence/unified_intelligence.py  # Intelligence hub
├── grace_complete_self_awareness.py # Self-awareness
```

### API Endpoints
```python
GET  /api/cognition/status           # Real-time cognition status
GET  /api/cognition/readiness        # SaaS readiness report
POST /api/cognition/domain/{id}/update # Update domain KPIs
GET  /api/cognition/benchmark/{metric} # Benchmark details
GET  /api/cognition/observatory      # Cognitive observatory
GET  /api/cognition/intelligence     # Unified intelligence view
```

### CLI Commands
```bash
grace cognition                      # Live cognition dashboard
grace readiness                      # SaaS readiness report
grace cognition domain core          # Domain-specific status
grace cognition benchmarks           # Benchmark status
```

### Metrics Published
- `overall_health` - Aggregate health across domains
- `overall_trust` - Aggregate trust score
- `overall_confidence` - Aggregate confidence
- `benchmark_progress` - Progress toward 90% goal
- `saas_readiness` - Boolean SaaS ready flag

### Dependencies
- Uses: ALL domains (aggregates metrics from everywhere)
- Calls: Parliament (meta-loop for optimization)

---

## 10. SPEECH – Voice Interface & Multi-Modal 🎤

### Backend Components
```
├── speech_service.py                # Speech recognition service
├── speech_models.py                 # Speech DB schemas
├── tts_service.py                   # Text-to-speech
├── tests/routes/speech_api.py       # Speech API
├── transcendence/voice_integration.py # Voice integration
```

### API Endpoints
```python
POST /api/speech/recognize           # Speech to text
POST /api/speech/synthesize          # Text to speech
GET  /api/speech/models              # Available models
POST /api/speech/command             # Voice command
GET  /api/speech/status              # Speech service status
```

### CLI Commands
```bash
grace speech listen                  # Start voice listening
grace speech say "hello"             # Text to speech
grace speech models                  # List speech models
```

### Metrics Published
- `recognition_accuracy` - Speech recognition accuracy
- `synthesis_quality` - TTS quality score
- `command_success` - Voice command success rate
- `latency` - End-to-end voice latency
- `multi_modal_integration` - Integration quality

### Dependencies
- Uses: Transcendence (command understanding), Core (verification)
- Calls: Knowledge (voice data indexing)

---

## Shared Infrastructure (Used by All Domains)

### Backend Components
```
├── database.py                      # Database connection
├── models.py                        # Core DB models
├── auth.py                          # Authentication
├── task_executor.py                 # Async task execution
├── trigger_mesh.py                  # Event bus
├── immutable_log.py                 # Audit log
├── verification.py                  # Cryptographic verification
```

### Metrics Service (NEW - To Be Created)
```
├── metrics_service.py               # Central metrics collector
├── metrics_models.py                # Metrics DB schemas
├── metrics_aggregator.py            # Rolling window aggregator
```

---

## Cross-Domain Integration Points

### Event Flow
```
1. User action → Core (verification)
2. Core → Trigger Mesh (event published)
3. Trigger Mesh → Subscribed domains
4. Domain → Metrics Service (KPI update)
5. Metrics Service → Cognition (aggregation)
6. Cognition → Parliament (if threshold breach)
7. Parliament → Meta-Loop (optimization)
```

### Metric Publishing Pattern
```python
# Each domain publishes metrics after operations
from backend.metrics_service import publish_metric

async def execute_task():
    # Do work
    result = await do_work()
    
    # Publish metrics
    await publish_metric(
        domain="transcendence",
        kpi="task_success",
        value=1.0 if result.success else 0.0,
        metadata={"task_id": result.id}
    )
```

---

## Next Implementation Steps

1. **Create metrics_service.py** - Central collector
2. **Add metric publishers** to each domain
3. **Wire CLI commands** to domain APIs
4. **Test end-to-end** metric flow
5. **Validate 90% trigger** fires correctly
