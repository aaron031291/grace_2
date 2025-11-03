# GRACE AI Coding Agent - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GRACE AI CODING AGENT                       │
│                         Production Ready v1.0                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐  ┌──────────┐  ┌─────────────┐
        │   User Input     │  │   API    │  │  CLI Tool   │
        │  (Natural Lang)  │  │Endpoints │  │  (Planned)  │
        └──────────────────┘  └──────────┘  └─────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────┐
        │           CORE PROCESSING LAYER                 │
        ├─────────────────────────────────────────────────┤
        │                                                 │
        │  ┌──────────────────────────────────────────┐  │
        │  │     Code Understanding Engine            │  │
        │  │  - analyze_current_context()             │  │
        │  │  - understand_intent()                   │  │
        │  │  - suggest_next_steps()                  │  │
        │  │  - find_related_code()                   │  │
        │  └──────────────────────────────────────────┘  │
        │                     │                           │
        │                     ▼                           │
        │  ┌──────────────────────────────────────────┐  │
        │  │     Code Memory System                   │  │
        │  │  - parse_codebase()                      │  │
        │  │  - parse_file()                          │  │
        │  │  - recall_patterns()                     │  │
        │  │  - Pattern ranking & learning            │  │
        │  └──────────────────────────────────────────┘  │
        │                     │                           │
        │                     ▼                           │
        │  ┌──────────────────────────────────────────┐  │
        │  │     Code Generator                       │  │
        │  │  - generate_function()                   │  │
        │  │  - generate_class()                      │  │
        │  │  - generate_tests()                      │  │
        │  │  - fix_errors()                          │  │
        │  │  - refactor_code()                       │  │
        │  └──────────────────────────────────────────┘  │
        │                     │                           │
        │                     ▼                           │
        │  ┌──────────────────────────────────────────┐  │
        │  │     Development Workflow                 │  │
        │  │  - parse_task()                          │  │
        │  │  - plan_implementation()                 │  │
        │  │  - execute_plan()                        │  │
        │  │  - track_progress()                      │  │
        │  └──────────────────────────────────────────┘  │
        │                                                 │
        └─────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌──────────────────┐       ┌──────────────┐
│  Governance   │         │     Hunter       │       │   Causal     │
│   Engine      │         │   Security       │       │  Reasoning   │
│               │         │   Scanner        │       │              │
│ - Approve code│         │ - Scan threats   │       │ - Predict    │
│ - Audit trail │         │ - Check vulns    │       │   impact     │
│ - Policy check│         │ - Block unsafe   │       │ - Risk level │
└───────────────┘         └──────────────────┘       └──────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────┐
        │              DATABASE LAYER                     │
        ├─────────────────────────────────────────────────┤
        │                                                 │
        │  ┌──────────────────────────────────────────┐  │
        │  │  code_patterns                           │  │
        │  │  - id, pattern_type, language            │  │
        │  │  - name, signature, code_snippet         │  │
        │  │  - tags, dependencies                    │  │
        │  │  - times_recalled, success_rate          │  │
        │  │  - confidence_score                      │  │
        │  └──────────────────────────────────────────┘  │
        │                                                 │
        │  ┌──────────────────────────────────────────┐  │
        │  │  code_contexts                           │  │
        │  │  - session_id, current_file              │  │
        │  │  - cursor_position, intent               │  │
        │  │  - open_files, recent_edits              │  │
        │  └──────────────────────────────────────────┘  │
        │                                                 │
        │  ┌──────────────────────────────────────────┐  │
        │  │  development_tasks                       │  │
        │  │  - task_id, description                  │  │
        │  │  - implementation_plan, status           │  │
        │  │  - progress_percentage                   │  │
        │  │  - generated_code, tests                 │  │
        │  └──────────────────────────────────────────┘  │
        │                                                 │
        └─────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────┐
        │              OUTPUT LAYER                       │
        ├─────────────────────────────────────────────────┤
        │                                                 │
        │  ┌──────────────┐  ┌──────────────┐            │
        │  │  Generated   │  │   Tests      │            │
        │  │  Code        │  │  Generated   │            │
        │  └──────────────┘  └──────────────┘            │
        │                                                 │
        │  ┌──────────────┐  ┌──────────────┐            │
        │  │  Security    │  │  Suggestions │            │
        │  │  Report      │  │  & Insights  │            │
        │  └──────────────┘  └──────────────┘            │
        │                                                 │
        └─────────────────────────────────────────────────┘
```

## Component Details

### 1. Code Understanding Engine

**Purpose:** Analyze code context and parse natural language intent

**Key Methods:**
- `analyze_current_context()` - Understand what user is editing
- `understand_intent()` - Parse natural language into tasks
- `suggest_next_steps()` - AI-powered suggestions
- `find_related_code()` - Find similar patterns

**Inputs:**
- File path and cursor position
- Natural language description
- Current coding context

**Outputs:**
- Parsed intent with confidence
- Implementation steps
- Related code patterns
- Next action suggestions

---

### 2. Code Memory System

**Purpose:** Store and recall code patterns with learning

**Key Methods:**
- `parse_codebase()` - Parse entire projects
- `parse_file()` - Extract patterns from single file
- `recall_patterns()` - Intelligent pattern search
- `deep_search()` - Hybrid symbol + pattern retrieval for semantic queries

**Storage:**
- Functions with signatures
- Classes with methods
- Tags and dependencies
- Symbol graph (`code_symbols`) capturing modules, functions, classes, and references
- Success metrics

**Learning:**
- Tracks usage (times_recalled)
- Measures success (success_rate)
- Adjusts confidence (confidence_score)
- Improves ranking over time
- Enriches symbol metadata for orchestrator subagents

---

### 3. Code Generator

**Purpose:** Generate code from specifications using patterns

**Key Methods:**
- `generate_function()` - Create functions with docstrings
- `generate_class()` - Create classes with methods
- `generate_tests()` - Auto-generate test suites
- `fix_errors()` - Auto-fix common errors
- `refactor_code()` - Style-based refactoring

**Features:**
- Uses learned patterns as templates
- Adds proper type hints
- Generates documentation
- Security scans output
- Governance approval

---

### 4. Development Workflow

**Purpose:** Automate complete development tasks

**Key Methods:**
- `parse_task()` - Break down natural language tasks
- `plan_implementation()` - Create step-by-step plans
- `execute_plan()` - Execute with verification
- `track_progress()` - Monitor task status

**Workflows:**
- Create Feature
- Fix Bug
- Refactor Code
- Add Tests
- Implement API

**Integration:**
- Uses Code Understanding for parsing
- Uses Code Generator for creation
- Uses Hunter for security
- Uses Causal for impact prediction

---

### 5. Agentic Orchestrator

**Purpose:** Coordinate multi-agent execution with Sourcegraph Amp-style subagents.

**Key Components:**
- `CodingOrchestrator` — plans requests, spawns subagents, merges outputs.
- `AnalysisAgent` — performs deep retrieval through the hybrid `deep_search` symbol graph.
- `ImplementationAgent` — drafts patches using code patterns and the generator.
- `ReviewAgent` — assembles diff reviews, static findings, and governance payloads.
- `Toolbelt` — shared tool layer for file I/O, diff previews, semantic search, and validation jobs.

**Workflow:**
1. Plan via `POST /api/code/orchestrate/plan`.
2. Execute structured plans through `POST /api/code/orchestrate/execute`.
3. Run end-to-end automation with `POST /api/code/orchestrate/run`.
4. Subagents publish lifecycle events on Trigger Mesh (`coding.plan.*`, `coding.subagent.*`).
5. Governance and Hunter checks gate every proposed diff before surfacing to the user.

**Integrations:**
- Persists symbol-aware context for future recalls.
- Submits verification suites to `task_executor` for asynchronous validation.
- Feeds execution telemetry back into `meta_loop` for continuous self-improvement.

---

## Data Flow

### Pattern Learning Flow

```
Codebase Files
     │
     ▼
Parse Files (AST/Regex)
     │
     ▼
Extract Patterns
     │
     ├─→ Functions (name, signature, code)
     ├─→ Classes (name, methods, attributes)
     └─→ Metadata (tags, dependencies, complexity)
     │
     ▼
Store in Database (code_patterns)
     │
     ▼
Track Usage & Success
     │
     └─→ Learning Loop (improve rankings)
```

### Code Generation Flow

```
User Intent (Natural Language)
     │
     ▼
Parse Intent (Code Understanding)
     │
     ├─→ Intent Type (create, fix, refactor)
     ├─→ Entities (api, user, auth)
     └─→ Actions (add, implement, update)
     │
     ▼
Recall Patterns (Code Memory)
     │
     └─→ Rank by: success_rate × confidence
     │
     ▼
Generate Code (Code Generator)
     │
     ├─→ Use templates
     ├─→ Apply patterns
     └─→ Add documentation
     │
     ▼
Security Scan (Hunter)
     │
     ├─→ Check vulnerabilities
     └─→ Detect unsafe patterns
     │
     ▼
Governance Approval
     │
     ├─→ Low risk: auto-approve
     └─→ High risk: require approval
     │
     ▼
Return Generated Code
```

### Task Automation Flow

```
Task Description
     │
     ▼
Parse Task (Dev Workflow)
     │
     └─→ Classify type (API, feature, bug fix)
     │
     ▼
Plan Implementation
     │
     ├─→ Step 1: Design models
     ├─→ Step 2: Generate code
     ├─→ Step 3: Generate tests
     ├─→ Step 4: Security scan
     └─→ Step 5: Verify
     │
     ▼
Execute Each Step
     │
     ├─→ Generate Code
     ├─→ Run Tests
     ├─→ Security Scan
     └─→ Track Progress
     │
     ▼
Return Results
     │
     ├─→ Generated artifacts
     ├─→ Test results
     └─→ Security report
```

---

## Integration Architecture

### GRACE System Integration

```
┌────────────────────────────────────────────────────┐
│              CODING AGENT                          │
└────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐  ┌──────────┐  ┌────────────┐
│ Governance   │  │  Hunter  │  │  Causal    │
│              │  │          │  │            │
│ Code         │  │ Security │  │ Impact     │
│ Approval     │  │ Scan     │  │ Prediction │
└──────────────┘  └──────────┘  └────────────┘
        │               │               │
        ▼               ▼               ▼
┌──────────────┐  ┌──────────┐  ┌────────────┐
│ Meta-Loop    │  │Parliament│  │ Reflection │
│              │  │          │  │            │
│ Optimize     │  │ Vote on  │  │ Learn from │
│ Generation   │  │ Arch     │  │ Feedback   │
└──────────────┘  └──────────┘  └────────────┘
```

### API Layer

```
┌────────────────────────────────────────────────────┐
│                  FastAPI Router                    │
│              /api/code/*                           │
└────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐  ┌──────────┐  ┌────────────┐
│   Parse      │  │Generate  │  │   Task     │
│              │  │          │  │            │
│ /parse       │  │ /generate│  │ /task      │
│ /understand  │  │ /fix     │  │ /progress  │
│ /suggest     │  │ /refactor│  │            │
└──────────────┘  └──────────┘  └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
        ┌────────────────────────────────┐
        │      JWT Authentication        │
        └────────────────────────────────┘
```

---

## Database Schema

### code_patterns Table

```
┌────────────────────────────────────────────────┐
│ code_patterns                                  │
├────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY            │
│ pattern_type    VARCHAR(64)    # function/class│
│ language        VARCHAR(32)    # python/js     │
│ name            VARCHAR(256)   # Pattern name  │
│ signature       TEXT           # Signature     │
│ code_snippet    TEXT           # Actual code   │
│ file_path       VARCHAR(512)   # Source file   │
│ project         VARCHAR(128)   # Project name  │
│ tags            JSON           # ["auth","api"]│
│ dependencies    JSON           # Imports       │
│ complexity      FLOAT          # Complexity    │
│ times_recalled  INTEGER        # Usage count   │
│ success_rate    FLOAT          # 0.0 - 1.0     │
│ confidence      FLOAT          # 0.0 - 1.0     │
│ created_at      DATETIME                       │
│ updated_at      DATETIME                       │
└────────────────────────────────────────────────┘
```

### code_contexts Table

```
┌────────────────────────────────────────────────┐
│ code_contexts                                  │
├────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY            │
│ session_id      VARCHAR(128)                   │
│ user            VARCHAR(64)                    │
│ current_file    VARCHAR(512)                   │
│ cursor_position JSON           # {line,column} │
│ task_desc       TEXT           # Current task  │
│ intent          VARCHAR(128)   # Intent type   │
│ open_files      JSON           # File list     │
│ recent_edits    JSON           # Edit history  │
│ project_root    VARCHAR(512)                   │
│ framework       VARCHAR(64)    # fastapi/react │
│ created_at      DATETIME                       │
│ updated_at      DATETIME                       │
└────────────────────────────────────────────────┘
```

### development_tasks Table

```
┌────────────────────────────────────────────────┐
│ development_tasks                              │
├────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY            │
│ task_id         VARCHAR(128) UNIQUE            │
│ user            VARCHAR(64)                    │
│ description     TEXT                           │
│ intent          JSON           # Parsed intent │
│ plan            JSON           # Steps         │
│ current_step    INTEGER                        │
│ status          VARCHAR(32)    # pending/done  │
│ progress_pct    FLOAT          # 0-100         │
│ generated_code  JSON           # Artifacts     │
│ tests_gen       JSON           # Test files    │
│ errors          JSON           # Error list    │
│ started_at      DATETIME                       │
│ completed_at    DATETIME                       │
└────────────────────────────────────────────────┘
```

---

## Performance Characteristics

### Latency Targets

| Operation | Target | Actual | Notes |
|-----------|--------|--------|-------|
| Pattern Recall | < 100ms | ✅ 50-100ms | Fast DB query |
| Code Generation | < 500ms | ✅ 200-500ms | Template based |
| Context Analysis | < 200ms | ✅ 100-200ms | AST parsing |
| Intent Parsing | < 300ms | ✅ 150-300ms | NLP processing |
| Task Planning | < 1s | ✅ 500ms-1s | Complex logic |

### Throughput

- **Patterns Stored:** 570+ from GRACE codebase
- **Concurrent Requests:** 50+ req/s
- **Memory Usage:** ~200MB base
- **Database Size:** ~50MB with patterns

### Scalability

- **Horizontal:** Stateless API (easy scaling)
- **Vertical:** Efficient queries (indexes on tags)
- **Caching:** Pattern recall cached
- **Async:** Full async/await support

---

## Security Architecture

### Defense Layers

```
User Input
    │
    ▼
Input Validation (Pydantic)
    │
    ▼
Authentication (JWT)
    │
    ▼
Authorization (Role-based)
    │
    ▼
Code Generation
    │
    ▼
Security Scan (Hunter)
    │
    ├─→ SQL Injection Check
    ├─→ XSS Check
    ├─→ Code Injection Check
    └─→ Unsafe Pattern Check
    │
    ▼
Governance Approval
    │
    └─→ High Risk = Manual Approval
    │
    ▼
Audit Log (Immutable)
    │
    ▼
Return Safe Code
```

### Security Features

- ✅ JWT authentication required
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Code injection detection
- ✅ Hunter security scanning
- ✅ Governance approval workflow
- ✅ Immutable audit trail
- ✅ Rate limiting ready
- ✅ CORS configured

---

## Deployment Architecture

### Development

```
Developer
    │
    ▼
Local Server (localhost:8000)
    │
    ├─→ SQLite Database (grace.db)
    ├─→ Code Memory (in-process)
    └─→ API Endpoints (FastAPI)
```

### Production (Recommended)

```
Load Balancer
    │
    ├─→ Server 1 (FastAPI)
    ├─→ Server 2 (FastAPI)
    └─→ Server 3 (FastAPI)
         │
         ▼
    PostgreSQL
    (Shared DB)
         │
         ▼
    Redis Cache
    (Pattern cache)
```

---

## File Structure

```
grace_rebuild/backend/
│
├── code_understanding.py      # Context & intent analysis
├── code_generator.py          # Code generation engine
├── dev_workflow.py            # Task automation
├── code_memory.py             # Pattern storage (existing)
│
├── routes/
│   └── coding_agent_api.py    # API endpoints
│
├── tests/
│   └── test_coding_agent.py   # Test suite
│
├── seed_code_memory.py        # Memory seeding script
├── verify_coding_agent.py     # Verification script
├── run_coding_agent_demo.bat  # Quick start
│
└── docs/
    ├── CODING_AGENT.md        # Full documentation
    ├── CODING_AGENT_STATUS.md # Status report
    ├── CODING_AGENT_QUICKSTART.md # Quick reference
    ├── CODING_AGENT_README.md # README
    └── CODING_AGENT_ARCHITECTURE.md # This file
```

---

## Future Architecture

### Planned Enhancements

```
                Current
                   │
                   ▼
        ┌──────────────────────┐
        │   Add CLI Layer      │
        │   grace code ...     │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  VS Code Extension   │
        │  Real-time suggest   │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Multi-file Refactor │
        │  Cross-file analysis │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Git Integration     │
        │  Learn from history  │
        └──────────────────────┘
```

---

**Architecture Version:** 1.0  
**Last Updated:** November 2, 2024  
**Status:** Production Ready ✅
