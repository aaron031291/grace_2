# Coding Agent Integration - Layer 3

**Making the Agentic Coding Agent a first-class citizen in the dashboard**

---

## Overview

The Coding Agent is Grace's capability to **build software autonomously**: features, tests, infrastructure, research projects, blockchain applications, and more. It's surfaced in **Layer 3 (Agentic Brain)** and orchestrates work through Layers 2 and 4.

**Flow**:
```
Layer 3: Define coding task → Create intent
   ↓
Layer 2: HTM orchestrates execution → Spawn coding agent
   ↓
Coding Agent: Plans → Codes → Tests → Documents
   ↓
Layer 3: Monitor progress → Review artifacts
   ↓
Layer 4: Deploy → Provision → Update secrets
   ↓
Layer 3: Complete intent → Learning retrospective
```

---

## Layer 3 UI: Agentic Builder Section

### Placement

**Location**: Layer 3 Dashboard, below Intent Table, above Retrospectives

```
Layer 3: Intent & Learning
├── Active Intents Table
├── 🤖 Agentic Builder ← NEW SECTION
│   ├── Coding Task Form
│   ├── Active Builds (table)
│   └── Completed Projects (collapsible)
├── Retrospectives List
└── Agentic Brain Kernels
```

---

## Agentic Builder Form

### UI Design

```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 Agentic Builder - Autonomous Code Generation             │
├─────────────────────────────────────────────────────────────┤
│ What would you like Grace to build?                         │
│                                                             │
│ Project Type:                                               │
│ ● Feature  ○ Test Suite  ○ Infrastructure  ○ Research      │
│ ○ Website  ○ Blockchain  ○ API Integration  ○ Custom       │
│                                                             │
│ Description:                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Build a real-time chat feature with WebSocket support, │ │
│ │ user authentication, and message persistence to         │ │
│ │ PostgreSQL database. Include React frontend and         │ │
│ │ FastAPI backend with comprehensive tests.               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Target Domain:                                              │
│ [Dropdown: Full-Stack Web Application ▼]                   │
│ Options: Web App, Infrastructure, Research, Blockchain,     │
│          API, CLI Tool, Library, Documentation              │
│                                                             │
│ Constraints:                                                │
│ Deadline:     [2025-11-20] [No deadline ☐]                 │
│ Environment:  ☑ Development  ☑ Staging  ☐ Production       │
│ Compliance:   ☐ HIPAA  ☐ SOC2  ☑ None                      │
│ Stack:        [React + FastAPI ▼]                           │
│                                                             │
│ Artifacts (Optional):                                       │
│ Repository: [https://github.com/user/project     ]         │
│ Datasets:   [+ Add dataset URL or upload]                  │
│ Docs:       [+ Add reference documentation]                │
│                                                             │
│ Advanced Options:                                           │
│ ☑ Generate tests (unit + integration)                      │
│ ☑ Generate documentation                                   │
│ ☑ Include deployment config                                │
│ ☐ Request human review before deployment                   │
│                                                             │
│ [Preview Plan] [Start Build] [Save as Template]            │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### 1. Create Coding Intent

**Endpoint**: `POST /api/coding_agent/create`

**Request Body**:
```json
{
  "project_type": "feature",
  "description": "Build a real-time chat feature with WebSocket support...",
  "target_domain": "full_stack_web",
  "constraints": {
    "deadline": "2025-11-20",
    "environments": ["development", "staging"],
    "compliance": [],
    "stack": "react_fastapi"
  },
  "artifacts": {
    "repository": "https://github.com/user/project",
    "datasets": [],
    "docs": []
  },
  "options": {
    "generate_tests": true,
    "generate_docs": true,
    "include_deployment": true,
    "require_review": false
  }
}
```

**Response**:
```json
{
  "intent_id": "int-code-001",
  "agent_type": "coding_agent",
  "status": "planning",
  "estimated_tasks": 25,
  "estimated_duration_hours": 8,
  "plan_preview": {
    "phases": [
      "Planning & Design (1h)",
      "Backend API Development (2h)",
      "Frontend Development (2h)",
      "Testing (1.5h)",
      "Documentation (1h)",
      "Deployment Setup (0.5h)"
    ],
    "deliverables": [
      "WebSocket chat backend (FastAPI)",
      "React chat UI components",
      "PostgreSQL schema & migrations",
      "Unit tests (80%+ coverage)",
      "Integration tests",
      "API documentation",
      "Deployment configs (Docker, K8s)"
    ]
  },
  "next_step": "Review plan and confirm to start execution"
}
```

---

### 2. Get Coding Agent Status

**Endpoint**: `GET /api/coding_agent/status/{intent_id}`

**Response**:
```json
{
  "intent_id": "int-code-001",
  "status": "executing",
  "current_phase": "Backend API Development",
  "progress_percent": 35,
  "elapsed_time_minutes": 45,
  "estimated_remaining_minutes": 75,
  "artifacts_generated": [
    {
      "type": "code",
      "path": "backend/routes/chat_api.py",
      "lines": 234,
      "status": "completed"
    },
    {
      "type": "code",
      "path": "frontend/src/components/ChatWidget.tsx",
      "lines": 156,
      "status": "in_progress"
    },
    {
      "type": "test",
      "path": "tests/test_chat_api.py",
      "lines": 89,
      "status": "pending"
    }
  ],
  "logs": [
    "10:30:15 INFO  Generated chat API endpoints",
    "10:30:20 INFO  Created WebSocket handler",
    "10:30:25 INFO  Building React chat component..."
  ],
  "blockers": [],
  "approval_needed": null
}
```

---

### 3. Review & Approve Plan

**Endpoint**: `POST /api/coding_agent/{intent_id}/approve`

**Request Body**:
```json
{
  "approved": true,
  "modifications": [
    "Add Redis caching layer",
    "Use TypeScript instead of JavaScript"
  ],
  "priority": "high"
}
```

**Response**:
```json
{
  "intent_id": "int-code-001",
  "status": "executing",
  "plan_updated": true,
  "message": "Plan approved with modifications. Execution started."
}
```

---

### 4. Request Human Review

**Endpoint**: `POST /api/coding_agent/{intent_id}/request_review`

**Triggered when**: Coding agent encounters decision point or needs approval

**Request Body**:
```json
{
  "review_type": "code_review",
  "context": "Generated authentication middleware",
  "artifacts": ["backend/middleware/auth.py"],
  "question": "Should I use JWT or session-based auth?",
  "options": ["JWT", "Session", "Both"]
}
```

**Response**: Pushes notification to Co-Pilot pane

---

### 5. Deploy to Layer 4

**Endpoint**: `POST /api/coding_agent/{intent_id}/deploy`

**Request Body**:
```json
{
  "target_environment": "staging",
  "deployment_config": {
    "docker_build": true,
    "run_tests": true,
    "auto_rollback": true
  }
}
```

**Response**:
```json
{
  "deployment_id": "deploy-abc-123",
  "status": "initiated",
  "layer4_task_id": "task-deploy-001",
  "message": "Deployment handed off to Layer 4 Deployment Service"
}
```

---

## Layer 3 UI: Active Builds Table

### Display

```
┌─────────────────────────────────────────────────────────────┐
│ Active Coding Projects (2)                                  │
├─────────────────────────────────────────────────────────────┤
│ Intent ID │ Project       │ Phase      │ Progress│ Actions  │
├───────────┼───────────────┼────────────┼─────────┼──────────┤
│ int-c-001 │ Chat Feature  │ Executing  │ ████ 35%│[View][⏸]│
│           │               │ Backend API│         │[Stop][📋]│
├───────────┼───────────────┼────────────┼─────────┼──────────┤
│ int-c-002 │ Test Suite    │ Planning   │ █░░░ 10%│[Approve] │
│           │ Expansion     │ Review Plan│         │[Modify]  │
└─────────────────────────────────────────────────────────────┘
```

**Click [View]** → Opens detailed progress modal

**Click [📋]** → Expands inline to show logs:
```
┌─ Coding Agent Logs (int-c-001) ────────────────┐
│ [Live ON] [Filter: All ▼]                     │
│ 10:30:15 INFO  Generated chat API endpoints   │
│ 10:30:20 INFO  Created WebSocket handler      │
│ 10:30:25 INFO  Building React component...    │
│ 10:30:30 WARN  Missing dependency: socket.io  │
│ 10:30:31 INFO  Added socket.io to package.json│
│ [Export] [Stop Build] [Request Help]          │
└────────────────────────────────────────────────┘
```

---

## Progress Detail Modal

**Triggered by**: Clicking [View] on active build

```
┌─────────────────────────────────────────────────────────────┐
│ Coding Project: Chat Feature (int-c-001)               [×]  │
├─────────────────────────────────────────────────────────────┤
│ Status: Executing  │  Progress: 35%  │  Elapsed: 45 min    │
│                                                             │
│ Current Phase: Backend API Development                      │
│ ████████████████████████████████░░░░░░░░░░░░░░░░░░░░ 65%   │
│                                                             │
│ Phases:                                                     │
│ ✓ Planning & Design (1h) - Completed                       │
│ ⏳ Backend API Development (2h) - 65% complete              │
│ ○ Frontend Development (2h) - Pending                       │
│ ○ Testing (1.5h) - Pending                                  │
│ ○ Documentation (1h) - Pending                              │
│ ○ Deployment Setup (0.5h) - Pending                         │
│                                                             │
│ Artifacts Generated (5):                                    │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ ✓ backend/routes/chat_api.py (234 lines)             │   │
│ │ ✓ backend/models/chat_message.py (67 lines)          │   │
│ │ ✓ backend/websocket/chat_handler.py (156 lines)      │   │
│ │ ⏳ frontend/src/components/ChatWidget.tsx (in progress)│   │
│ │ ○ tests/test_chat_api.py (pending)                   │   │
│ │ [View Code] [Download All]                            │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                             │
│ Blockers: None                                              │
│                                                             │
│ Next Steps:                                                 │
│ • Complete React chat component (30 min remaining)          │
│ • Generate unit tests                                       │
│ • Run test suite                                            │
│                                                             │
│ Actions:                                                    │
│ [⏸ Pause] [■ Stop] [💬 Chat with Agent] [🚀 Deploy Now]   │
└─────────────────────────────────────────────────────────────┘
```

---

## Co-Pilot Integration

### Grace Proactive Messages (Coding Agent)

**1. Plan Ready for Review**:
```
Grace (10:30a): 🤖 Coding plan ready for review

Project: Chat Feature
Estimated time: 8 hours
Phases: 6 (design, backend, frontend, tests, docs, deploy)

The plan includes:
• WebSocket chat backend (FastAPI)
• React chat UI
• PostgreSQL message storage
• 80%+ test coverage
• Docker deployment config

[✓ Approve & Start] [📝 Modify Plan] [❌ Cancel]
```

**2. Approval Needed**:
```
Grace (11:15a): ❓ Coding agent needs your input

Building authentication for chat feature.
Which approach should I use?

Options:
• JWT tokens (stateless, scalable)
• Session cookies (simpler, server-side)
• OAuth 2.0 (enterprise-ready)

[JWT] [Sessions] [OAuth] [Let Grace Decide]
```

**3. Build Complete**:
```
Grace (14:30a): ✅ Chat feature build complete!

Generated artifacts:
• 12 code files (1,234 lines)
• 8 test files (567 lines)
• API documentation
• Deployment configs

All tests passing (94% coverage)

Ready to deploy?
[🚀 Deploy to Staging] [👁 Review Code] [📊 View Report]
```

**4. Deployment Handoff**:
```
Grace (14:35a): 🚀 Deploying to staging...

Handed off to Layer 4 Deployment Service:
• Building Docker image
• Running tests
• Deploying to staging cluster

Track progress in Layer 4 or wait here.
[Go to Layer 4] [Monitor Here] [Cancel Deploy]
```

**5. Learning Feedback**:
```
Grace (15:00a): 🎓 Build completed successfully!

Retrospective:
• Time: 4.5h (planned: 8h) - 44% faster! ⭐
• Tests: 94% coverage (target: 80%)
• Code quality: A+ (zero linting errors)

Lessons learned:
• WebSocket pattern reusable for future features
• React hooks reduced component complexity
• PostgreSQL schema optimization improved performance

[View Full Retro] [Apply Learnings] [Start New Build]
```

---

## Execution Monitoring

### Status Flow

```
Planning (10-20%)
   ↓
Designing (20-30%)
   ↓
Coding (30-70%)
   ↓
Testing (70-85%)
   ↓
Documenting (85-95%)
   ↓
Deploying (95-100%)
   ↓
Completed (100%)
```

### Real-Time Updates

**In Layer 3 Active Builds Table**:
```
int-c-001 | Chat Feature | Executing: Coding | ████████░░░░ 45%
          Live log: "Generated ChatWidget.tsx (156 lines)"
```

**Updates every**:
- Status changes: Immediate (WebSocket push)
- Progress: Every 30 seconds
- Logs: Real-time stream
- Artifacts: As generated

---

## Layer 4 Handoff

### Deploy Button Flow

**When user clicks [🚀 Deploy Now]**:

```
Step 1: Layer 3 creates deployment request
  POST /api/coding_agent/{intent_id}/deploy
  {
    "target_environment": "staging",
    "deployment_config": {...}
  }

Step 2: Backend creates Layer 4 task
  - Type: "deployment"
  - Source: "coding_agent"
  - Artifacts: Code files from intent
  - Config: Deployment settings

Step 3: Layer 4 Deployment Service picks up task
  - Builds Docker image
  - Runs tests in container
  - Deploys to staging cluster
  - Updates deployment status

Step 4: Layer 3 monitors deployment
  - Shows "Deploying..." status
  - Polls Layer 4 deployment status
  - Updates progress in UI

Step 5: Deployment completes
  - Layer 4 returns success/failure
  - Layer 3 updates intent status to "deployed"
  - Co-pilot notifies user
  - Learning loop captures metrics
```

### Layer 4 Integration Points

**Secrets Management**:
- If build needs API keys → Layer 4 Secrets Vault
- Agent requests secrets via Layer 3 approval
- User approves → Secrets passed to build securely

**Infrastructure Provisioning**:
- If build needs cloud resources → Layer 4 provisioning
- Agent generates Terraform/CloudFormation
- Layer 4 executes provisioning
- Reports back to Layer 3

**Documentation Updates**:
- Generated docs → Layer 4 documentation service
- Auto-commit to repo
- Update internal knowledge base

---

## Learning Loop Integration

### Retrospective Capture

**When coding intent completes**:

```
POST /api/learning/retrospective

Body: {
  "cycle_name": "Coding Build: Chat Feature",
  "insights": [
    "WebSocket pattern reusable for real-time features",
    "React hooks reduced code complexity by 30%",
    "PostgreSQL JSONB improved query performance"
  ],
  "improvements": [
    "Added WebSocket utility library",
    "Created React hooks template",
    "Optimized DB schema patterns"
  ],
  "metrics": {
    "planned_hours": 8,
    "actual_hours": 4.5,
    "efficiency_gain": 0.44,
    "test_coverage": 0.94,
    "code_quality_score": "A+"
  },
  "reusable_artifacts": [
    "WebSocket handler template",
    "React chat component library",
    "PostgreSQL chat schema"
  ]
}
```

**Displayed in Layer 3 Retrospectives List**:
```
┌────────────────────────────────────────────────────────┐
│ Coding Build: Chat Feature - Nov 14, 2:00 PM           │
│ Duration: 4.5h (planned: 8h) - 44% faster! ⭐          │
│                                                        │
│ 💡 Insights:                                           │
│ • WebSocket pattern reusable                           │
│ • React hooks reduced complexity 30%                   │
│ • PostgreSQL JSONB improved queries                    │
│                                                        │
│ ⬆️ Improvements Applied:                               │
│ • Added WebSocket utility library                      │
│ • Created React hooks template                         │
│ • Optimized DB schema patterns                         │
│                                                        │
│ Artifacts: [View Code] [Reuse Template]               │
└────────────────────────────────────────────────────────┘
```

---

## Enhanced Layer 3 Dashboard Layout

```
┌──────────────────────────────────────────┬─────────────────┐
│ 🧠 Layer 3: Intent & Learning             │ Grace Co-Pilot │
│                                          │ [🤖 Building...]│
├──────────────────────────────────────────┼─────────────────┤
│ Active Intents (General)                 │ Notifications   │
│ ┌──────────────────────────────────────┐ │ ┌─────────────┐ │
│ │ int-001 | Analyze Q4 data | 65%      │ │ │🤖 Plan ready│ │
│ └──────────────────────────────────────┘ │ │  Chat build │ │
│                                          │ │  [Approve]  │ │
│ 🤖 Agentic Builder ← NEW SECTION         │ └─────────────┘ │
│ ┌──────────────────────────────────────┐ ├─────────────────┤
│ │ [Coding Task Form - See above]       │ │ Chat            │
│ └──────────────────────────────────────┘ │ ┌─────────────┐ │
│                                          │ │You: Build    │ │
│ Active Coding Projects (2)               │ │chat feature  │ │
│ ┌──────────────────────────────────────┐ │ │             │ │
│ │ int-c-001 | Chat | Coding | 35% [▼] │ │ │Grace: I'll   │ │
│ │ │ ┌─ Progress Detail ──────────────┐ │ │ │create a plan│ │
│ │ │ │ Phase: Backend API (65%)      │ │ │ │First, let me│ │
│ │ │ │ Artifacts: 3 completed        │ │ │ │understand... │ │
│ │ │ │ [View Code] [Chat] [Pause]    │ │ │ │             │ │
│ │ │ └───────────────────────────────┘ │ │ │[WebSocket]  │ │
│ │ int-c-002 | Tests | Planning | 10% │ │ │[REST API]   │ │
│ └──────────────────────────────────────┘ │ │[GraphQL]    │ │
│                                          │ └─────────────┘ │
│ Completed Projects (5) [Show ▼]          ├─────────────────┤
│                                          │ Quick Actions   │
│ Learning Retrospectives                  │ [🤖 New Build]  │
│ ┌──────────────────────────────────────┐ │ [📋 View Plans] │
│ │ Coding Build: Chat Feature (above)   │ │ [🚀 Deploy All] │
│ └──────────────────────────────────────┘ │ [🎓 Review]     │
│                                          │                 │
│ Agentic Brain Kernels                    │                 │
│ [Learning Loop] [Intent Engine]          │                 │
│ [Policy AI] [Enrichment] [Trust]         │                 │
│ [Playbook] [Coding Agent ← NEW]          │                 │
└──────────────────────────────────────────┴─────────────────┘
```

---

## Coding Agent Kernel Terminal

**Added to Layer 3 Agentic Brain Kernels**:

```
[Kernel: Coding Agent] ──────────────── [●] Active  [▼]
│ Active Builds: 2 | Completed Today: 1
│ Success Rate: 94% | Avg Duration: 6.2h
│ [▶ Start] [■ Stop] [🤖 New Build] [📋 Logs]

{If expanded:}
│ ┌─ Coding Agent Console ──────────────────────────────┐
│ │ [Live ON] [Filter: Current Build ▼]                 │
│ │ 10:30:15 INFO  [int-c-001] Generated API endpoints  │
│ │ 10:30:20 INFO  [int-c-001] Created WebSocket handler│
│ │ 10:30:25 INFO  [int-c-001] Building React component │
│ │ 10:30:30 WARN  [int-c-001] Missing dependency       │
│ │ 10:30:31 INFO  [int-c-001] Added socket.io          │
│ │ [Export] [Stop Build] [View Artifacts]              │
│ └─────────────────────────────────────────────────────┘
│
│ ┌─ Quick Actions ──────────────────────────────────────┐
│ │ [New Build] [View Active] [Deploy All] [Review Code]│
│ └─────────────────────────────────────────────────────┘
```

---

## Example User Flows

### Flow 1: Build New Feature

```
User: Navigate to Layer 3
User: Fill out Agentic Builder form
  - Type: Feature
  - Description: "Real-time chat with WebSocket"
  - Domain: Full-Stack Web
  - Generate tests: ✓
User: Click [Preview Plan]
  → Grace shows estimated plan (6 phases, 8 hours)
User: Click [Start Build]
  → Intent created, appears in Active Coding Projects
  → Coding Agent Kernel starts working
  → Progress updates in real-time
  → Logs stream in console
Grace: (30 min later) "Need input: JWT or Sessions?"
User: Clicks [JWT] button in co-pilot notification
  → Build continues
Grace: (4 hours later) "Build complete! All tests passing."
User: Clicks [Deploy to Staging]
  → Handoff to Layer 4
  → Deployment proceeds
Grace: (10 min later) "Deployed to staging! URL: https://staging..."
User: Tests feature, provides feedback
Grace: Creates retrospective with learnings
```

---

### Flow 2: Build Infrastructure

```
User: Layer 3 → Agentic Builder
User: Fill form
  - Type: Infrastructure
  - Description: "Kubernetes cluster with monitoring"
  - Domain: Infrastructure
  - Artifacts: AWS account, region preferences
User: Click [Start Build]
Grace: "Planning infrastructure setup..."
Grace: "Generated Terraform configs for:
       • EKS cluster (3 nodes)
       • Prometheus monitoring
       • Grafana dashboards
       • Auto-scaling groups"
Grace: "Approve plan?"
User: [Approve & Start]
Grace: "Building..."
  → Coding agent generates all configs
  → Creates deployment pipeline
Grace: "Ready to provision. This will create AWS resources."
User: Clicks [Deploy Now]
  → Layer 4 executes Terraform
  → Provisions cluster
  → Installs monitoring
Grace: "Cluster provisioned! Endpoint: https://cluster..."
Grace: "Storing cluster credentials in Layer 4 Secrets Vault"
  → Auto-saves kubeconfig
User: Done! Infrastructure ready to use
```

---

### Flow 3: Build Blockchain Application

```
User: Layer 3 → Agentic Builder
User: Fill form
  - Type: Blockchain
  - Description: "NFT marketplace with wallet integration"
  - Domain: Blockchain
  - Stack: Solidity + Ethers.js + React
User: [Start Build]
Grace: "Planning NFT marketplace..."
Grace: Shows plan:
  • Smart contracts (Solidity)
  • Frontend (React + Ethers.js)
  • IPFS integration
  • Wallet connectors (MetaMask, WalletConnect)
  • Tests (Hardhat)
User: [Approve]
Grace: Builds everything over 12 hours
Grace: "Smart contracts ready. Deploy to testnet?"
User: [Deploy to Testnet]
  → Layer 4 deploys contracts
  → Verifies on Etherscan
Grace: "Deployed! Contract: 0x123abc..."
Grace: "Frontend deploying to Vercel..."
Grace: "Complete! App: https://nft-marketplace..."
User: Tests, provides feedback
Grace: Learning loop captures blockchain patterns
```

---

## Backend Implementation

### Coding Agent Service

**File**: `backend/services/coding_agent_service.py`

```python
class CodingAgentService:
    """
    Orchestrates autonomous code generation
    Integrates with HTM for task management
    """
    
    async def create_coding_intent(
        self,
        project_type: str,
        description: str,
        target_domain: str,
        constraints: dict,
        artifacts: dict,
        options: dict
    ) -> dict:
        """
        Create coding intent and generate plan
        """
        # Generate plan using AI
        plan = await self.generate_plan(description, target_domain)
        
        # Create intent in database
        intent = await self.create_intent_record(
            agent_type="coding_agent",
            goal=description,
            plan=plan,
            constraints=constraints
        )
        
        # Return intent with plan preview
        return {
            "intent_id": intent.id,
            "status": "planning",
            "plan_preview": plan
        }
    
    async def execute_coding_intent(self, intent_id: str):
        """
        Execute the coding plan
        Spawns HTM tasks for each phase
        """
        intent = await self.get_intent(intent_id)
        
        for phase in intent.plan.phases:
            # Create HTM task for this phase
            htm_task = await self.create_htm_task(
                intent_id=intent_id,
                phase=phase.name,
                estimated_duration=phase.duration
            )
            
            # Execute phase
            artifacts = await self.execute_phase(phase, htm_task)
            
            # Store artifacts
            await self.store_artifacts(intent_id, artifacts)
            
            # Update progress
            await self.update_progress(intent_id, phase.progress)
        
        # Mark complete
        await self.complete_intent(intent_id)
    
    async def deploy_artifacts(
        self,
        intent_id: str,
        target_environment: str
    ):
        """
        Hand off to Layer 4 for deployment
        """
        # Get generated artifacts
        artifacts = await self.get_artifacts(intent_id)
        
        # Create Layer 4 deployment task
        deployment_task = await self.create_layer4_task(
            type="deployment",
            artifacts=artifacts,
            environment=target_environment
        )
        
        return {
            "deployment_id": deployment_task.id,
            "layer4_task_id": deployment_task.id,
            "status": "initiated"
        }
```

---

## Frontend Components

### Agentic Builder Form

**File**: `frontend/src/components/AgenticBuilderForm.tsx`

```typescript
export const AgenticBuilderForm: React.FC = ({ onCreate }) => {
  const [formData, setFormData] = useState({
    project_type: 'feature',
    description: '',
    target_domain: 'full_stack_web',
    constraints: {
      deadline: null,
      environments: ['development'],
      compliance: [],
      stack: 'react_fastapi'
    },
    artifacts: {
      repository: '',
      datasets: [],
      docs: []
    },
    options: {
      generate_tests: true,
      generate_docs: true,
      include_deployment: true,
      require_review: false
    }
  });

  const handleSubmit = async () => {
    const response = await axios.post(
      'http://localhost:8000/api/coding_agent/create',
      formData
    );
    
    onCreate(response.data);
  };

  return (
    <div className="agentic-builder-form">
      {/* Form fields as shown in wireframe above */}
      <button onClick={handleSubmit}>Start Build</button>
    </div>
  );
};
```

---

### Active Builds Table

**File**: `frontend/src/components/ActiveBuildsTable.tsx`

```typescript
export const ActiveBuildsTable: React.FC = () => {
  const [builds, setBuilds] = useState([]);

  useEffect(() => {
    fetchBuilds();
    const interval = setInterval(fetchBuilds, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchBuilds = async () => {
    const response = await axios.get(
      'http://localhost:8000/api/coding_agent/active'
    );
    setBuilds(response.data.builds);
  };

  return (
    <table className="builds-table">
      {builds.map(build => (
        <BuildRow key={build.intent_id} build={build} />
      ))}
    </table>
  );
};
```

---

## Integration Checklist

### Backend
- [ ] Create `coding_agent_service.py`
- [ ] Add `POST /api/coding_agent/create`
- [ ] Add `GET /api/coding_agent/status/{id}`
- [ ] Add `POST /api/coding_agent/{id}/approve`
- [ ] Add `POST /api/coding_agent/{id}/deploy`
- [ ] Add `POST /api/coding_agent/{id}/request_review`
- [ ] Integrate with HTM for task spawning
- [ ] Integrate with Layer 4 for deployment
- [ ] Add learning loop feedback

### Frontend
- [ ] Create `AgenticBuilderForm.tsx`
- [ ] Create `ActiveBuildsTable.tsx`
- [ ] Create `BuildProgressModal.tsx`
- [ ] Add to Layer 3 dashboard
- [ ] Add Coding Agent kernel terminal
- [ ] Update co-pilot notifications
- [ ] Add deploy buttons
- [ ] Test end-to-end flow

---

## Success Criteria

**MVP with Coding Agent**:
- [ ] User can submit coding task via form
- [ ] Grace generates and shows plan
- [ ] User can approve plan
- [ ] Coding agent executes (generates code)
- [ ] Progress visible in Layer 3
- [ ] Logs stream in console
- [ ] User can deploy via Layer 4
- [ ] Retrospective captured
- [ ] Co-pilot shows relevant notifications

**Future Enhancements**:
- Real-time collaboration (watch agent code live)
- Code review UI (inline comments)
- Artifact preview (syntax highlighting)
- Multi-agent builds (parallel work)
- Version control integration (auto-commit)

---

**Coding Agent is now a first-class citizen in Layer 3!** 🤖✨

Users can describe high-level goals, Grace plans and executes, Layer 2 orchestrates, Layer 4 deploys, and everything is visible and controllable from the unified dashboard.
