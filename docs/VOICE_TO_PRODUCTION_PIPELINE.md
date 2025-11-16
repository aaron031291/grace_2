# Voice to Production Pipeline - Architecture

## Overview

Grace can now build real applications (CRM, websites, blockchains, ecommerce engines) directly from voice/chat discussions using her existing 20+ kernels and RAG memory spine.

```
┌────────────────────────────────────────────────────────────────┐
│            VOICE → SPEC → CODE → DEPLOY → TRACK                │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Voice Chat Discussion                                         │
│         ↓                                                       │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 1. CONVERSATION CAPTURE                          │         │
│  │  - Speech-to-text (Whisper)                      │         │
│  │  - Transcript auto-embedded                       │         │
│  │  - Intent extraction                              │         │
│  └────────────────────┬─────────────────────────────┘         │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 2. BUILD MANIFEST CREATION                       │         │
│  │  - Classifier extracts: build_crm, build_site... │         │
│  │  - Entities: features, tech stack, constraints   │         │
│  │  - Published: build.request.created              │         │
│  └────────────────────┬─────────────────────────────┘         │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 3. SPEC GENERATOR (RAG-Augmented)                │         │
│  │  - Query RAG for past similar builds             │         │
│  │  - Model orchestrator drafts requirements        │         │
│  │  - Data models, APIs, UI flows, integrations     │         │
│  │  - Stored in world model (category='build_spec') │         │
│  └────────────────────┬─────────────────────────────┘         │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 4. TASK DISPATCHER                               │         │
│  │  - Break spec into tasks                         │         │
│  │  - Route to kernels by capability:               │         │
│  │    • coding_kernel → backend/APIs                │         │
│  │    • frontend_kernel → websites/UI               │         │
│  │    • blockchain_kernel → smart contracts         │         │
│  │    • database_kernel → schema/migrations         │         │
│  └────────────────────┬─────────────────────────────┘         │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 5. CODE GENERATION (RAG Context)                 │         │
│  │  - Each kernel uses RAG for patterns             │         │
│  │  - Generates code based on spec + context        │         │
│  │  - Writes to repo/staging branch                 │         │
│  └────────────────────┬─────────────────────────────┘         │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 6. BUILD & DEPLOY                                │         │
│  │  - Run tests (existing CI)                       │         │
│  │  - Build artifacts (Docker, bundles, contracts)  │         │
│  │  - Deploy to environment                          │         │
│  │  - Record in world model (category='deployment') │         │
│  └────────────────────┬─────────────────────────────┘         │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 7. TELEMETRY & TRACKING                          │         │
│  │  - API trackers on new services                  │         │
│  │  - Metrics feed back to RAG                      │         │
│  │  - Grace can report: "CRM has 5 API calls/min"   │         │
│  └────────────────────┬─────────────────────────────┘         │
│                       ↓                                         │
│  ┌──────────────────────────────────────────────────┐         │
│  │ 8. CONVERSATIONAL REPORTING                      │         │
│  │  - Grace uses RAG to recall entire build         │         │
│  │  - Reports: progress, status, metrics            │         │
│  │  - User asks: "How's the CRM?"                   │         │
│  │  - Grace: "Deployed, 5 APIs live, 10 records"    │         │
│  └──────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

---

## Components Required

### 1. Intent Extraction from Voice/Chat

**File**: `backend/conversation/intent_extractor.py`

Classifies conversations as build requests:
- `build_crm` - Customer Relationship Management system
- `build_website` - Static/dynamic website
- `build_blockchain` - Blockchain node/contracts
- `build_ecommerce` - E-commerce engine
- `build_api` - REST API service
- `build_dashboard` - Admin dashboard

Extracts entities:
- Features required
- Tech stack preferences
- Constraints (budget, timeline, scale)
- Integration requirements

### 2. Build Manifest Schema

**File**: `backend/build_system/build_manifest.py`

```python
@dataclass
class BuildManifest:
    manifest_id: str
    build_type: str  # crm, website, blockchain, ecommerce
    title: str
    description: str
    features: List[str]
    tech_stack: Dict[str, str]
    constraints: Dict[str, Any]
    integrations: List[str]
    conversation_id: str
    created_from: str  # voice, chat, api
    confidence: float
    metadata: Dict[str, Any]
```

### 3. Spec Generator (RAG-Augmented)

**File**: `backend/build_system/spec_generator.py`

Uses RAG to:
- Query past similar builds
- Find relevant code patterns
- Locate existing components to reuse

Uses <br>Orchestrator to:
- Draft requirements document
- Design data models
- Plan API endpoints
- Define UI flows

Stores spec in world model for future reference.

### 4. Task Dispatcher

**File**: `backend/build_system/task_dispatcher.py`

Routes tasks to existing kernels based on capabilities:

| Kernel | Capability | Builds |
|--------|-----------|--------|
| `coding_kernel` | Backend code | APIs, services, databases |
| `frontend_kernel` | UI code | Websites, dashboards, admin panels |
| `blockchain_kernel` | Web3 code | Smart contracts, nodes, wallets |
| `database_kernel` | Schema | Migrations, models, indexes |
| `api_kernel` | Integration | API clients, webhooks, trackers |
| `testing_kernel` | QA | Tests, validation, monitoring |

### 5. Code Generator Kernels

Each kernel uses RAG for context:

```python
async def generate_code(task: Task, spec: BuildSpec):
    """Generate code using RAG context"""
    
    # Query RAG for relevant patterns
    context = await rag_service.retrieve_with_citations(
        query=f"{task.type} {task.description}",
        source_types=["code_pattern", "execution_outcome"],
        filters={"tags__contains": [task.type, "successful"]},
        max_tokens=3000
    )
    
    # Use model orchestrator with context
    prompt = RAGPromptTemplate.build_prompt(
        question=f"Generate {task.type} code for: {task.description}",
        context_chunks=context["context"],
        citations=context["citations"],
        mode="technical"
    )
    
    code = await model_orchestrator.generate(
        prompt=prompt,
        domain="coding",
        task_type="code_generation"
    )
    
    return code
```

### 6. Deployment Pipeline

**File**: `backend/build_system/deployment_pipeline.py`

- Builds Docker images
- Deploys to Kubernetes/Docker Compose
- Registers services with service mesh
- Records deployment in world model

### 7. API Tracker

**File**: `backend/build_system/api_tracker.py`

- Instruments new APIs with metrics
- Tracks: requests/min, latency, errors
- Feeds telemetry back to RAG
- Grace can report status conversationally

---

## Implementation Steps

### Phase 1: Voice → Manifest (Week 1)
- [ ] Create intent extractor for build requests
- [ ] Define BuildManifest schema
- [ ] Integrate with recording