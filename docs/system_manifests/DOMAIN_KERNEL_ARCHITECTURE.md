# Grace Domain Kernel Architecture
## From 270 APIs to 8 Intelligent Domain Kernels

## Current Problem
❌ 270 individual API endpoints  
❌ Frontend calls specific routes  
❌ No intelligence at API layer  
❌ Manual orchestration required  

## New Architecture
✅ 8 Domain Kernels (AI Agents)  
✅ Frontend calls domain, not specific APIs  
✅ Kernel decides what to fetch  
✅ Automatic orchestration  

---

## 🎯 The 8 Domain Kernels

### 1. Core Kernel (`core-kernel`)
**Purpose:** System fundamentals & user interaction  
**Intelligence:** Understands basic user needs, routes complex requests to other kernels

**Manages 35 endpoints:**
- `/api/chat` - Main conversation
- `/api/auth/*` - Authentication (2)
- `/api/tasks/*` - Task management (3)
- `/api/health` - System health
- `/api/metrics/*` - System metrics (3)
- `/api/history/*` - History tracking (2)
- `/api/reflections/*` - Reflection system (2)
- `/api/summaries/*` - Summaries (2)
- `/api/plugins/*` - Plugin management (3)
- `/api/issues/*` - Issue tracking (3)
- `/api/speech/*` - Speech/TTS (8)
- `/api/evaluation/*` - Evaluation (2)

**Kernel API:**
```typescript
POST /kernel/core
{
  "intent": "I need task status and health",
  "context": {}
}

// Kernel decides to call:
// - /api/tasks internally
// - /api/health internally
// Returns aggregated intelligent response
```

---

### 2. Memory Kernel (`memory-kernel`)
**Purpose:** All knowledge storage & retrieval  
**Intelligence:** Semantic understanding, context assembly, relevance ranking

**Manages 25 endpoints:**
- `/api/memory/*` - Memory tree, items, domains (6)
- `/api/knowledge/*` - Knowledge query, trust scoring (8)
- `/api/ingest/*` - Text, URL, file ingestion (4)
- `/api/trust/*` - Trust sources, scoring (5)
- `/api/immutable/*` - Immutable log (2)

**Kernel API:**
```typescript
POST /kernel/memory
{
  "intent": "Find everything about sales pipelines",
  "context": { "user_id": "123" }
}

// Kernel intelligently:
// - Searches memory tree
// - Queries knowledge base
// - Checks trust scores
// - Ranks by relevance
// - Returns unified context
```

---

### 3. Code Kernel (`code-kernel`)
**Purpose:** All code generation, execution, understanding  
**Intelligence:** Writes code, validates, executes safely, learns patterns

**Manages 30 endpoints:**
- `/api/coding/*` - Code generation, parsing, context (16)
- `/api/sandbox/*` - Sandbox execution (5)
- `/api/execution/*` - Code execution (4)
- `/api/commit/*` - Commit workflows (2)
- `/api/grace-architect/*` - Self-extension (7)

**Kernel API:**
```typescript
POST /kernel/code
{
  "intent": "Build a sales pipeline with validation",
  "requirements": {
    "language": "python",
    "features": ["API integration", "error handling"]
  }
}

// Kernel orchestrates:
// - Parses requirements
// - Generates code
// - Validates in sandbox
// - Runs tests
// - Returns working code + execution results
```

---

### 4. Governance Kernel (`governance-kernel`)
**Purpose:** Safety, policy, approvals, constitutional checks  
**Intelligence:** Interprets policies, makes approval decisions, learns from precedents

**Manages 50 endpoints:**
- `/api/governance/*` - Policies, checks, approvals (9)
- `/api/constitutional/*` - Constitutional principles (12)
- `/api/hunter/*` - Threat detection (4)
- `/api/autonomy/*` - Autonomy tiers, checks (8)
- `/api/parliament/*` - Parliamentary governance (13)
- `/api/verification/*` - Verification audit (4)

**Kernel API:**
```typescript
POST /kernel/governance
{
  "intent": "Check if I can deploy this code to production",
  "action": { "type": "deploy", "target": "production", "code": "..." }
}

// Kernel decides:
// - Run Layer-1 constitutional check
// - Run Layer-2 policy check
// - Check deployment policies
// - Assess risk level
// - Decide: approve/block/require-approval
```

---

### 5. Verification Kernel (`verification-kernel`)
**Purpose:** Action contracts, snapshots, benchmarks, mission tracking  
**Intelligence:** Creates contracts, verifies outcomes, detects drift

**Manages 25 endpoints:**
- `/api/verification/*` - Contracts, snapshots, benchmarks (21)
- `/api/autonomous/improver/*` - Autonomous fixing (4)

**Kernel API:**
```typescript
POST /kernel/verification
{
  "intent": "Verify the last deployment worked correctly",
  "mission_id": "mission_123"
}

// Kernel orchestrates:
// - Gets mission contracts
// - Compares expected vs actual
// - Runs benchmarks
// - Checks for drift
// - Returns verification report
```

---

### 6. Intelligence Kernel (`intelligence-kernel`)
**Purpose:** ML, predictions, temporal reasoning, causal analysis  
**Intelligence:** Trains models, makes predictions, finds patterns

**Manages 45 endpoints:**
- `/api/ml/*` - Model training, deployment (3)
- `/api/temporal/*` - Predictions, simulations, patterns (11)
- `/api/causal/*` - Causal graphs, analysis (11)
- `/api/learning/*` - Learning aggregates, outcomes (2)
- `/api/meta/*` - Meta-loop, analyses, recommendations (8)
- `/api/cognition/*` - Intent parsing, execution (10)

**Kernel API:**
```typescript
POST /kernel/intelligence
{
  "intent": "Predict sales for next quarter and explain what drives it",
  "data_context": { "historical_data": "..." }
}

// Kernel orchestrates:
// - Trains/loads prediction model
// - Runs temporal simulation
// - Builds causal graph
// - Generates explanation
// - Returns prediction + reasoning
```

---

### 7. Infrastructure Kernel (`infra-kernel`)
**Purpose:** System operations, monitoring, scheduling, observability  
**Intelligence:** Monitors health, schedules tasks, coordinates workers

**Manages 30 endpoints:**
- `/api/scheduler/*` - Scheduler observability (2)
- `/api/subagents/*` - Subagent management (2)
- `/api/concurrent/*` - Concurrent execution (7)
- `/api/goals/*` - Goal management (7)
- `/api/playbooks/*` - Playbook execution (2)
- `/api/incidents/*` - Incident management (3)
- `/api/agentic-insights/*` - Agent insights (5)
- `/api/health/*` - Health monitoring (2)

**Kernel API:**
```typescript
POST /kernel/infrastructure
{
  "intent": "Scale up workers and monitor performance",
  "target_load": "high"
}

// Kernel orchestrates:
// - Checks current load
// - Spawns additional workers
// - Monitors performance
// - Adjusts resource allocation
// - Returns scaling report
```

---

### 8. Federation Kernel (`federation-kernel`)
**Purpose:** External integrations (GitHub, Slack, AWS, APIs)  
**Intelligence:** Manages external connections, handles auth, aggregates data

**Manages 30 endpoints:**
- `/api/external/github/*` - GitHub operations (6)
- `/api/external/slack/*` - Slack operations (6)
- `/api/external/aws/*` - AWS operations (8)
- `/api/external/secrets/*` - Secrets management (4)
- Webhook handlers (6)

**Kernel API:**
```typescript
POST /kernel/federation
{
  "intent": "Create GitHub issue and notify team on Slack",
  "issue": { "title": "Bug in prod", "repo": "grace" },
  "slack_channel": "#engineering"
}

// Kernel orchestrates:
// - Authenticates to GitHub
// - Creates issue
// - Formats notification
// - Posts to Slack
// - Returns confirmation with links
```

---

## Kernel Intelligence Pattern

Each kernel is an AI agent that:

### 1. Receives Intent
```python
@router.post("/kernel/{domain}")
async def domain_kernel(request: KernelRequest):
    # request.intent = "user's natural language request"
    # request.context = additional context
```

### 2. Parses & Plans
```python
# Kernel uses LLM to understand
plan = await kernel.parse_intent(request.intent)
# Returns: {
#   "actions": ["fetch_tasks", "check_health"],
#   "sequence": "parallel",
#   "data_needed": ["task_list", "health_status"]
# }
```

### 3. Executes Intelligently
```python
# Calls underlying APIs based on plan
results = await kernel.execute_plan(plan)
# Handles errors, retries, fallbacks automatically
```

### 4. Aggregates & Responds
```python
# Intelligent aggregation
response = await kernel.aggregate_results(results, request.intent)
return KernelResponse(
    answer=response.text,
    data=response.structured_data,
    execution_trace=trace,
    kernels_consulted=[...],
    confidence=0.95
)
```

---

## New Kernel Response Schema

```typescript
interface KernelResponse {
  // Intelligent answer
  answer: string;
  
  // Structured data (if any)
  data?: any;
  
  // Which APIs the kernel called
  apis_called: string[];
  
  // Other kernels consulted
  kernels_consulted: string[];
  
  // Execution trace (kernel-level)
  execution_trace: {
    kernel_name: string;
    intent_understood: string;
    plan_created: Action[];
    apis_executed: string[];
    aggregation_method: string;
    total_duration_ms: number;
  };
  
  // Data provenance
  data_provenance: DataProvenance[];
  
  // Trust & governance
  trust_score: number;
  governance_checks: GovernanceCheck[];
  
  // Suggested panels (for Orb UI)
  suggested_panels?: Panel[];
}
```

---

## Benefits

### Instead of:
```typescript
// Old way - manual orchestration
const tasks = await http.get('/api/tasks');
const health = await http.get('/api/health');
const metrics = await http.get('/api/metrics/summary');
// Manually combine results
```

### Now:
```typescript
// New way - intelligent kernel
const response = await http.post('/kernel/core', {
  intent: "Show me system status and my tasks"
});
// Kernel handles everything intelligently
```

---

## Migration Path

### Phase 1: Build Kernels (keep old APIs)
- Create 8 kernel agents
- Wire to existing 270 APIs
- Both work in parallel

### Phase 2: Frontend switches to kernels
- Update GraceOrb to call kernels
- Keep compatibility layer

### Phase 3: Deprecate direct API calls
- Mark old endpoints as deprecated
- All traffic through kernels

---

## Implementation

Each kernel needs:
1. Intent parser (LLM-based)
2. Action planner
3. API orchestrator
4. Result aggregator
5. Governance integration

---

## Domain Breakdown

| Kernel | Endpoints | % of Total |
|--------|-----------|------------|
| Core | 35 | 13% |
| Memory | 25 | 9% |
| Code | 30 | 11% |
| Governance | 50 | 19% |
| Verification | 25 | 9% |
| Intelligence | 45 | 17% |
| Infrastructure | 30 | 11% |
| Federation | 30 | 11% |
| **Total** | **270** | **100%** |

---

## Next Steps

Want me to build the domain kernel system? Each kernel would be an intelligent agent that:
- Understands natural language intent
- Plans optimal API calls
- Aggregates results intelligently
- Returns cohesive responses

**This turns 270 dumb endpoints into 8 intelligent agents!** 🎯
