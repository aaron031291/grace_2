# Tiered Agent Execution System

## Overview

Grace's tiered agent execution system breaks complex tasks into specialized phases (research → design → implement → test → deploy), with Guardian oversight, playbook integration, and continuous learning feedback.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              Tiered Agent Execution Pipeline                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  GUARDIAN OVERSIGHT                                         │ │
│  │  • Pause/Resume pipelines                                  │ │
│  │  • Override decisions                                      │ │
│  │  • Monitor all phases                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  AGENT ORCHESTRATOR                                         │ │
│  │  • Coordinates phase execution                             │ │
│  │  • Max 2 concurrent pipelines                              │ │
│  │  • Auto-recovery on failure                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                │
│         ▼                  ▼                  ▼                 │
│  ┌───────────┐      ┌───────────┐     ┌───────────┐           │
│  │ PHASE 1   │  →   │ PHASE 2   │ →   │ PHASE 3   │ →  ...    │
│  │ RESEARCH  │      │ DESIGN    │     │ IMPLEMENT │           │
│  └───────────┘      └───────────┘     └───────────┘           │
│       │                  │                  │                   │
│       ▼                  ▼                  ▼                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  PLAYBOOKS AS TOOLS                                      │  │
│  │  • research_and_gather                                   │  │
│  │  • create_design_spec                                    │  │
│  │  • implement_code                                        │  │
│  │  • run_tests                                             │  │
│  │  • deploy_to_environment                                 │  │
│  └─────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  ARTIFACTS                                               │  │
│  │  • Research docs                                         │  │
│  │  • Design specs                                          │  │
│  │  • Code files                                            │  │
│  │  • Test results                                          │  │
│  │  • Deployment manifests                                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LEARNING FEEDBACK LOOP                                  │  │
│  │  • Artifacts → Event emitters                            │  │
│  │  • Success/Failure → Triage agent                        │  │
│  │  • Patterns → Learning missions                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Pipeline Phases

### 1. Research Agent
**Purpose**: Gather information and context

**Capabilities**:
- Web research (via Firefox agent)
- GitHub repository analysis
- RAG knowledge retrieval
- Documentation scraping

**Playbooks Used**:
- `research_and_gather`

**Artifacts Produced**:
- `research_doc`: Findings, sources, context

**Example**:
```python
from backend.agents_core.agent_orchestrator import agent_orchestrator

pipeline_id = await agent_orchestrator.execute_pipeline(
    task="Research Kubernetes autoscaling best practices",
    context={"sources": ["web", "github", "rag"]}
)
```

### 2. Design Agent
**Purpose**: Create architecture and specifications

**Capabilities**:
- System design
- API specification
- Database schema design
- Architecture diagrams

**Playbooks Used**:
- `create_design_spec`

**Artifacts Produced**:
- `design_spec`: Architecture, APIs, schemas

**Inputs**: Research artifacts from phase 1

### 3. Implement Agent
**Purpose**: Write code based on design

**Capabilities**:
- Code generation
- File creation
- Dependency management
- Code organization

**Playbooks Used**:
- `implement_code`

**Artifacts Produced**:
- `code`: Generated code, files

**Inputs**: Design artifacts from phase 2

### 4. Test Agent
**Purpose**: Run tests and validation

**Capabilities**:
- Unit testing
- Integration testing
- Type checking
- Linting

**Playbooks Used**:
- `run_tests`

**Artifacts Produced**:
- `test_results`: Pass/fail status, coverage

**Inputs**: Implementation artifacts from phase 3

**Learning Integration**:
- Test failures → Event to learning loop
- Patterns analyzed → Auto-fix suggestions

### 5. Deploy Agent
**Purpose**: Deploy to target environment

**Capabilities**:
- Environment setup
- Deployment execution
- Health checks
- Rollback if needed

**Playbooks Used**:
- `deploy_to_environment`

**Artifacts Produced**:
- `deployment_manifest`: Deployment details, status

**Inputs**: Test artifacts from phase 4 (requires all tests passing)

## Guardian Integration

### Pause Pipeline
Guardian can pause any pipeline at any phase:

```python
from backend.core.message_bus import message_bus

await message_bus.publish('guardian.pause_pipeline', {
    'pipeline_id': 'pipeline_abc123'
})
```

**Effect**:
- Current phase completes
- Pipeline status → `paused`
- Next phase waits for resume
- No resource consumption while paused

### Resume Pipeline
```python
await message_bus.publish('guardian.resume_pipeline', {
    'pipeline_id': 'pipeline_abc123'
})
```

**Effect**:
- Pipeline status → `running`
- Next phase starts immediately

### Override Decision
Guardian can override agent decisions:

```python
await message_bus.publish('guardian.override_pipeline', {
    'pipeline_id': 'pipeline_abc123',
    'override': {
        'skip_tests': False,
        'deployment_environment': 'staging',
        'custom_validation': True
    }
})
```

**Effect**:
- Override data injected into phase context
- Agents respect Guardian directives
- All overrides logged to immutable log

## Playbooks as First-Class Tools

### How Agents Use Playbooks

```python
class ImplementAgent(BaseAgent):
    async def _execute_phase(self, context: Dict[str, Any]):
        # Use playbook as a tool
        result = await self.use_playbook(
            'implement_code',
            {'design': context.get('design_artifacts')}
        )
        
        if result.get('success'):
            # Extract playbook artifacts
            code = result.get('code')
            
            # Create agent artifact
            self.add_artifact(
                artifact_type='code',
                content=code,
                metadata={'playbook': 'implement_code'}
            )
```

### Playbook Results Structure

```python
{
    'success': True,
    'artifacts': [
        {'type': 'file', 'path': 'module.py', 'content': '...'},
        {'type': 'file', 'path': 'tests.py', 'content': '...'}
    ],
    'metadata': {
        'execution_time': 2.5,
        'tools_used': ['code_generator', 'file_writer']
    }
}
```

### Learning Feedback

Every playbook execution emits events:

```python
# Success
await emit_learning_event('playbook.executed', {
    'playbook_id': 'implement_code',
    'agent': 'implement_agent',
    'phase': 'implement',
    'success': True,
    'artifacts': 2
}, severity='low')

# Failure
await emit_learning_event('playbook.failed', {
    'playbook_id': 'run_tests',
    'agent': 'test_agent',
    'phase': 'test',
    'error': 'Type errors in module.py'
}, severity='medium')
```

**Learning Loop Actions**:
1. Triage agent clusters playbook failures
2. High recurrence → Launch learning mission
3. Learn from web/GitHub about resolution
4. Update playbook or create new one
5. Next execution uses improved playbook

## Artifact Collection

### Artifact Structure

```python
@dataclass
class AgentArtifact:
    artifact_id: str
    artifact_type: str  # research_doc, design_spec, code, etc.
    phase: AgentPhase
    content: Any
    metadata: Dict[str, Any]
    created_at: datetime
```

### Artifact Flow

```
Research → design_artifacts
    ↓
Design → implementation_artifacts
    ↓
Implement → test_artifacts
    ↓
Test → deployment_artifacts
    ↓
Deploy → production_artifacts
```

### Artifact Storage

All artifacts:
- ✅ Logged to immutable log
- ✅ Stored with provenance
- ✅ Fed to learning loop
- ✅ Accessible via API

### Learning Integration

```python
async def _feed_artifacts_to_learning_loop(pipeline, result):
    for artifact in result.artifacts:
        await agent_events.emit(
            'agent.artifact.created',
            {
                'pipeline_id': pipeline.pipeline_id,
                'phase': result.phase.value,
                'artifact_type': artifact.artifact_type,
                'playbooks_used': result.playbooks_used
            },
            severity='low'
        )
```

## Auto-Recovery

### Failure Detection

```python
if result.status == AgentStatus.FAILED:
    if self.auto_recover_on_failure:
        recovered = await self._attempt_recovery(
            pipeline,
            phase,
            result
        )
```

### Recovery Playbook

```python
recovery_playbook = guardian_playbook_registry.get_playbook(
    'phase_failure_recovery'
)

recovery_result = await recovery_playbook.execute({
    'pipeline_id': pipeline_id,
    'failed_phase': 'implement',
    'error': 'Syntax errors in generated code'
})
```

**Recovery Actions**:
1. Analyze failure
2. Check if known issue
3. Apply fix playbook
4. Retry phase
5. If still fails → escalate to Guardian

## API Usage

### Execute Pipeline

```bash
POST /api/agent-pipeline/execute

{
  "task": "Build user authentication system",
  "context": {
    "language": "python",
    "framework": "fastapi",
    "database": "postgresql"
  },
  "phases": ["research", "design", "implement", "test"]
}

Response:
{
  "pipeline_id": "pipeline_a3f2",
  "status": "started",
  "task": "Build user authentication system"
}
```

### Monitor Pipeline

```bash
GET /api/agent-pipeline/pipelines/pipeline_a3f2

Response:
{
  "pipeline_id": "pipeline_a3f2",
  "task": "Build user authentication system",
  "status": "running",
  "current_phase": "implement",
  "phase_results": {
    "research": {
      "status": "completed",
      "artifacts": [...]
    },
    "design": {
      "status": "completed",
      "artifacts": [...]
    },
    "implement": {
      "status": "running",
      "artifacts": []
    }
  }
}
```

### Get Artifacts

```bash
GET /api/agent-pipeline/pipelines/pipeline_a3f2/artifacts

Response:
{
  "pipeline_id": "pipeline_a3f2",
  "artifacts": [
    {
      "artifact_id": "research_agent_abc123",
      "artifact_type": "research_doc",
      "phase": "research",
      "content": {...},
      "created_at": "2025-01-20T14:30:00Z"
    },
    {
      "artifact_id": "design_agent_def456",
      "artifact_type": "design_spec",
      "phase": "design",
      "content": {...},
      "created_at": "2025-01-20T14:35:00Z"
    }
  ],
  "total": 2
}
```

### Guardian Control

```bash
POST /api/agent-pipeline/guardian/control

{
  "pipeline_id": "pipeline_a3f2",
  "action": "pause"
}

Response:
{
  "status": "paused",
  "pipeline_id": "pipeline_a3f2"
}
```

## Boot Output

```
[CHUNK 0.75] Tiered Agent Orchestrator...
  [OK] Agent Orchestrator: Online
  [OK] Max concurrent pipelines: 2
  [OK] Pipeline phases: research → design → implement → test → deploy
  [OK] Guardian oversight: Active (pause/resume/override)
  [OK] Playbooks: First-class agent tools
  [OK] Learning loop: Artifact feedback enabled
```

## Event Flow Example

### Scenario: Build Kubernetes Autoscaler

1. **Pipeline Started**:
```
[AGENT-ORCHESTRATOR] Pipeline started: pipeline_k8s
Task: Build Kubernetes autoscaler
Phases: research → design → implement → test → deploy
```

2. **Research Phase**:
```
[RESEARCH] Starting research phase...
[RESEARCH] Using playbook: research_and_gather
  → Web: "kubernetes autoscaling patterns"
  → GitHub: kubernetes/autoscaler repo
  → RAG: "autoscaling best practices"
[RESEARCH] Artifact created: research_doc
[RESEARCH] Research phase completed

Event emitted:
{
  "event_type": "agent.phase.completed",
  "phase": "research",
  "artifacts": 1
}
```

3. **Design Phase**:
```
[DESIGN] Starting design phase...
[DESIGN] Using playbook: create_design_spec
  → Input: research artifacts
  → Output: System architecture
[DESIGN] Artifact created: design_spec
[DESIGN] Design phase completed
```

4. **Implement Phase**:
```
[IMPLEMENT] Starting implementation phase...
[IMPLEMENT] Using playbook: implement_code
  → Language: python
  → Framework: kubernetes-client
[IMPLEMENT] Artifact created: code
[IMPLEMENT] Implementation phase completed
```

5. **Test Phase**:
```
[TEST] Starting test phase...
[TEST] Using playbook: run_tests
  → Unit tests: 25/25 passed
  → Integration tests: 8/10 passed ⚠️

Event emitted to learning loop:
{
  "event_type": "agent.tests.failed",
  "failed_count": 2,
  "total_count": 35
}

Triage agent clusters this event.
If recurrence detected → Launch learning mission.
```

6. **Auto-Recovery** (optional):
```
[AGENT-ORCHESTRATOR] Test phase failed: 2 tests failed
[AGENT-ORCHESTRATOR] Attempting recovery...
[RECOVERY] Using playbook: phase_failure_recovery
  → Analyzing failures
  → Applying fixes
  → Retrying tests
[RECOVERY] Recovery successful
```

7. **Deploy Phase**:
```
[DEPLOY] Starting deploy phase...
[DEPLOY] Checking test results: all passed ✓
[DEPLOY] Using playbook: deploy_to_environment
  → Environment: staging
  → Health check: passed
[DEPLOY] Artifact created: deployment_manifest
[DEPLOY] Deploy phase completed

Pipeline completed successfully!
Total artifacts: 5
Duration: 12.3s
```

## Integration with Senior Developer Agent

The tiered orchestrator works alongside the Senior Developer Agent (Chunk 0.8):

**Senior Developer Agent**:
- High-level planning
- Code review
- Architecture decisions

**Tiered Orchestrator**:
- Executes the plan
- Breaks into phases
- Coordinates specialized agents
- Collects artifacts

**Together**:
```
Senior Dev Agent → Creates plan
     ↓
Tiered Orchestrator → Executes phases
     ↓
Specialized Agents → Do the work
     ↓
Guardian → Oversees & controls
     ↓
Learning Loop → Improves from outcomes
```

## Best Practices

### Pipeline Design
✅ **Do**:
- Use all phases for complex tasks
- Skip phases for simple tasks (e.g., just research + implement)
- Let agents decide playbook usage
- Review artifacts between phases

❌ **Don't**:
- Force deploy without test pass
- Skip research for unknown domains
- Override Guardian without reason

### Guardian Oversight
✅ **Do**:
- Pause for critical errors
- Override for security concerns
- Resume promptly after review

❌ **Don't**:
- Pause indefinitely
- Override without logging reason

### Learning Integration
✅ **Do**:
- Let failures feed learning loop
- Review clustered patterns
- Apply learned fixes
- Update playbooks

❌ **Don't**:
- Ignore repeated failures
- Skip artifact analysis

---

**Status**: ✅ Active  
**Auto-Start**: Yes (Chunk 0.75)  
**Guardian Integration**: Full (pause/resume/override)  
**Learning Integration**: Continuous (artifact feedback)  
**Playbooks**: First-class agent tools
