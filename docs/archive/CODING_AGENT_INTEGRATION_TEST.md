# Coding Agent Integration - Test Plan

**End-to-end testing for autonomous code generation in Layer 3**

---

## Prerequisites

- [ ] Backend has `coding_agent_api.py` registered
- [ ] Frontend has `AgenticBuilderForm` component
- [ ] Layer 3 dashboard updated with coding builds section
- [ ] Co-pilot quick actions include "New Coding Build"

---

## Test 1: Create Coding Build

### Steps
1. Navigate to Layer 3
2. Verify "Agentic Builder" form is visible
3. Fill out form:
   - **Project Type**: Select "Feature"
   - **Description**: "Build a real-time notification system with WebSocket support and browser push notifications"
   - **Target Domain**: "Full-Stack Web Application"
   - **Stack**: "React + FastAPI"
   - **Generate tests**: ✓
   - **Generate docs**: ✓
   - **Include deployment**: ✓
4. Click [Preview Plan]

### Expected Results
- [ ] Loading state shows "Generating Plan..."
- [ ] Modal opens with plan preview
- [ ] See estimated duration (e.g., "8 hours")
- [ ] See phases listed (6-8 phases)
- [ ] See tasks per phase
- [ ] See deliverables list
- [ ] [Approve & Start Build] button enabled

### API Calls
- [ ] `POST /api/coding_agent/create` returns 200
- [ ] Response includes `intent_id`, `plan_preview`, `estimated_duration_hours`

---

## Test 2: Approve and Start Build

### Steps
1. In plan preview modal, click [Approve & Start Build]
2. Wait for response
3. Check Active Coding Projects table

### Expected Results
- [ ] Alert: "Build started! Track progress in Active Coding Projects table."
- [ ] Modal closes
- [ ] Form clears
- [ ] New row appears in "Active Coding Projects" table:
  - Intent ID: `int-code-001`
  - Project: Description (truncated)
  - Phase: "Planning & Design"
  - Progress: "5%" (or similar)
  - Artifacts: "0 files"
  - Actions: [View] button

### API Calls
- [ ] `POST /api/coding_agent/{id}/approve` returns 200
- [ ] `GET /api/coding_agent/active` returns updated list

---

## Test 3: Monitor Build Progress

### Steps
1. Wait 10-15 seconds (auto-refresh cycle)
2. Observe Active Coding Projects table
3. Refresh manually if needed

### Expected Results
- [ ] Progress percent increases (5% → 10% → 15%...)
- [ ] Current phase updates ("Planning" → "Coding" → "Testing")
- [ ] Artifacts count increases as files are generated
- [ ] Status updates automatically every 5-10 seconds

### API Calls
- [ ] `GET /api/coding_agent/active` polls every 5-10s
- [ ] Response shows updated `progress_percent`, `current_phase`, `artifacts_generated`

---

## Test 4: View Build Details

### Steps
1. In Active Coding Projects table
2. Find a build with progress > 30%
3. Click [👁 View] button

### Expected Results
- [ ] Modal/detail view opens
- [ ] Shows current phase with progress bar
- [ ] Lists all phases (completed ✓, active ⏳, pending ○)
- [ ] Shows artifacts generated:
  - File paths
  - Line counts
  - Status (completed, in-progress, pending)
- [ ] Shows logs from coding agent
- [ ] Actions available: [Pause], [Stop], [Deploy Now]

### API Calls
- [ ] `GET /api/coding_agent/status/{intent_id}` returns detailed status

---

## Test 5: Deploy Build

### Steps
1. Wait for build to reach 95%+ progress
2. Verify [🚀 Deploy] button appears in Actions column
3. Click [🚀 Deploy]
4. Confirm deployment to staging

### Expected Results
- [ ] Confirmation dialog: "Deploy this build to staging?"
- [ ] Click OK
- [ ] Alert: "Deployment initiated! Check Layer 4 for progress."
- [ ] Build status may update to "deploying"
- [ ] Layer 4 receives deployment task

### API Calls
- [ ] `POST /api/coding_agent/{id}/deploy` returns 200
- [ ] Response includes `deployment_id`, `layer4_task_id`
- [ ] Layer 4 deployment service picks up task

---

## Test 6: Co-Pilot Interactions

### Test 6.1: Plan Review Notification

**Trigger**: Coding agent generates plan

**Expected in Co-Pilot**:
```
Grace: 🤖 Coding plan ready for review

Project: Notification System
Estimated: 8 hours, 6 phases

[✓ Approve & Start] [📝 Modify] [❌ Cancel]
```

**Actions**:
- [ ] Click [Approve & Start] → Starts build
- [ ] Notification dismissed
- [ ] Build appears in table

---

### Test 6.2: Review Request Notification

**Trigger**: Coding agent needs decision (simulated)

**Expected in Co-Pilot**:
```
Grace: ❓ Coding agent needs input

Should I use JWT or session-based authentication?

[JWT] [Sessions] [Let Grace Decide]
```

**Actions**:
- [ ] Click [JWT] → Build resumes with JWT
- [ ] Build status updates
- [ ] Notification dismissed

---

### Test 6.3: Build Complete Notification

**Trigger**: Build reaches 100%

**Expected in Co-Pilot**:
```
Grace: ✅ Build complete!

Generated:
• 12 code files
• 8 test files
• Documentation

All tests passing (94% coverage)

[🚀 Deploy to Staging] [👁 Review Code] [📊 Report]
```

**Actions**:
- [ ] Click [Deploy to Staging] → Starts deployment
- [ ] Click [Review Code] → Opens artifact viewer
- [ ] Click [Report] → Opens retrospective

---

## Test 7: Learning Loop Integration

### Steps
1. Complete a coding build (or simulate completion)
2. Check retrospectives list
3. Verify learning captured

### Expected Results
- [ ] New retrospective appears in list:
  - Title: "Coding Build: [description]"
  - Insights include efficiency metrics
  - Improvements list patterns learned
  - Metrics show actual vs planned time
- [ ] Learning stats update:
  - Total builds increments
  - Success rate calculated
  - Efficiency gains tracked
  - Domain patterns captured

### API Calls
- [ ] `POST /api/coding_agent/{id}/complete` creates retrospective
- [ ] `GET /api/telemetry/learning/retrospectives` includes coding builds
- [ ] `GET /api/coding_agent/learning_stats` returns updated stats

---

## Test 8: Layer 4 Handoff

### Steps
1. Complete a build (95%+)
2. Click [Deploy] button
3. Navigate to Layer 4 (when built)
4. Verify deployment task appears

### Expected Results
- [ ] Layer 3: Deployment initiated message
- [ ] Layer 4: New deployment task appears
- [ ] Task shows:
  - Source: "coding_agent"
  - Artifacts: Files from build
  - Status: "initiated" → "building" → "deploying"
- [ ] Deployment proceeds automatically
- [ ] Layer 3 receives completion notification

### Data Flow
```
Layer 3: User clicks [Deploy]
   ↓
POST /api/coding_agent/{id}/deploy
   ↓
Backend: Creates Layer 4 deployment task
   ↓
Layer 4: Deployment Service picks up task
   ↓
Layer 4: Builds Docker, runs tests, deploys
   ↓
Layer 4: Updates task status
   ↓
Layer 3: Polls deployment status
   ↓
Co-Pilot: Notifies user of completion
   ↓
Learning Loop: Captures deployment metrics
```

---

## Test 9: Error Handling

### Test 9.1: Build Failure
**Simulate**: Coding agent encounters error

**Expected**:
- [ ] Build status changes to "failed"
- [ ] Error message displayed
- [ ] Co-pilot notifies: "Build failed: [reason]"
- [ ] User can retry or cancel
- [ ] Learning loop captures failure for improvement

---

### Test 9.2: Deployment Failure
**Simulate**: Layer 4 deployment fails

**Expected**:
- [ ] Deployment status: "failed"
- [ ] Co-pilot notifies: "Deployment failed: [reason]"
- [ ] User can retry or rollback
- [ ] Build artifacts preserved
- [ ] Can re-deploy after fixes

---

### Test 9.3: Network Errors
**Simulate**: Backend offline during build monitoring

**Expected**:
- [ ] Graceful error handling
- [ ] Retry logic kicks in
- [ ] User notified if persistent failure
- [ ] Build state preserved
- [ ] Can resume monitoring when backend returns

---

## Test 10: Reusability & Learning

### Steps
1. Complete 3 builds of similar type (e.g., 3 web features)
2. Check learning stats
3. Create 4th build of same type

### Expected Results
- [ ] Learning stats show:
  - 3 completed builds
  - Average efficiency calculated
  - Domain patterns identified
  - Reusable components counted
- [ ] 4th build should:
  - Have better time estimate
  - Reuse components from previous builds
  - Complete faster (showing learning)
  - Reference similar builds in plan

### API Calls
- [ ] `GET /api/coding_agent/learning_stats`
- [ ] Response shows improvements over time

---

## Integration Checklist

### Backend
- [ ] `coding_agent_api.py` registered in main app
- [ ] All 7 coding agent endpoints functional
- [ ] Integrates with intent API
- [ ] Creates HTM tasks for orchestration
- [ ] Hands off to Layer 4 deployment
- [ ] Creates learning retrospectives

### Frontend
- [ ] `AgenticBuilderForm` component renders
- [ ] Form validation works
- [ ] Plan preview modal displays
- [ ] Active builds table shows coding intents
- [ ] Deploy button appears when ready
- [ ] Co-pilot shows coding agent notifications
- [ ] Quick action "New Coding Build" works

### Layer Integration
- [ ] Layer 3 shows coding intents separately from general intents
- [ ] Layer 2 HTM orchestrates coding tasks
- [ ] Layer 4 receives deployment handoff
- [ ] Learning loop captures all coding builds
- [ ] Co-pilot provides continuous updates

---

## User Scenarios

### Scenario 1: Build New Feature
```
User: "I need a user authentication system"
Action: Fill Agentic Builder form
  - Type: Feature
  - Description: "User authentication with JWT, email/password, OAuth (Google), password reset, 2FA"
  - Stack: React + FastAPI
Result: Grace generates plan → User approves → Build executes
Time: 6-8 hours (autonomous)
Output: Complete auth system with tests + docs
Deploy: One-click to staging
Learn: Auth patterns captured for future builds
```

---

### Scenario 2: Build Infrastructure
```
User: "Set up Kubernetes monitoring stack"
Action: Fill Agentic Builder form
  - Type: Infrastructure
  - Description: "K8s cluster with Prometheus, Grafana, AlertManager, and custom dashboards"
  - Stack: Terraform + AWS
Result: Grace generates IaC plan → User approves → Provisions infrastructure
Time: 4-6 hours
Output: Complete monitoring stack + runbooks
Deploy: Terraform apply via Layer 4
Learn: Infrastructure patterns for future DevOps tasks
```

---

### Scenario 3: Build Tests
```
User: "Need comprehensive test coverage"
Action: Fill Agentic Builder form
  - Type: Test Suite
  - Description: "Unit + integration + E2E tests for chat feature"
  - Existing repo: https://github.com/user/chat-app
Result: Grace analyzes codebase → Generates test plan → Writes tests
Time: 3-4 hours
Output: Test suite with 85%+ coverage
Deploy: Auto-commits to repo
Learn: Testing patterns for similar features
```

---

## Success Criteria

**MVP Coding Agent**:
- [ ] User can submit coding task via form
- [ ] Grace generates realistic plan
- [ ] Build executes (simulated progress for MVP)
- [ ] Progress visible in table
- [ ] Deploy button appears when ready
- [ ] Deployment hands off to Layer 4
- [ ] Retrospective created after completion
- [ ] Learning stats accumulate

**Full Coding Agent** (Post-MVP):
- [ ] Actually generates working code (LLM integration)
- [ ] Runs tests automatically
- [ ] Validates code quality
- [ ] Auto-commits to git
- [ ] Real-time progress updates
- [ ] Interactive code review
- [ ] Multi-agent collaboration

---

## Known Limitations (MVP)

1. **Simulated Execution**: Build progress is simulated, not real code generation (post-MVP: integrate actual code gen LLM)
2. **Mock Artifacts**: File lists are mocked (post-MVP: real files with code viewer)
3. **Basic Plan Generation**: Template-based plans (post-MVP: AI-generated custom plans)
4. **Layer 4 Stub**: Deployment hands off but Layer 4 not fully built yet

**These are acceptable for validating the UX and workflow**

---

## Next Steps After Testing

### If Tests Pass ✅
1. Collect user feedback on coding agent UX
2. Decide: Integrate real code gen LLM or build Layer 4 first?
3. Plan production rollout timeline

### If Tests Fail ❌
1. Debug and fix issues
2. Re-test
3. Adjust UX based on findings

---

**Ready to test the Coding Agent integration!** 🤖✨
