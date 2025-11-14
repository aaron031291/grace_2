# GRACE Dashboard MVP - QA & Integration Test Plan

**Comprehensive testing checklist for Layers 1-3**

---

## Test Environment Setup

### Prerequisites
- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:5173`
- [ ] Browser: Chrome/Edge (latest version)
- [ ] Network tab open (DevTools)
- [ ] Console tab open (for errors)

### Verify Backend Health
```bash
# Visit API docs
http://localhost:8000/docs

# Check these endpoints exist:
✓ GET  /api/kernels/layer1/status
✓ GET  /api/kernels/layer2/status
✓ GET  /api/kernels/layer3/status
✓ POST /api/kernels/{id}/action
✓ GET  /api/telemetry/kernels/status
✓ GET  /api/telemetry/htm/queue
✓ POST /api/htm/priorities
✓ POST /api/htm/spawn_agent
✓ GET  /api/telemetry/intent/active
✓ POST /api/intent/create
✓ POST /api/copilot/chat/send
✓ GET  /api/copilot/notifications
```

---

## Layer 1: Operations Console Tests

### Test 1.1: Page Load & Telemetry
**Steps**:
1. Navigate to `http://localhost:5173`
2. Click "Layer 1" navigation button

**Expected**:
- [ ] Page loads in < 3 seconds
- [ ] See "Layer 1: Operations Console" header
- [ ] 5 telemetry cards display with numbers
  - [ ] Total Kernels: 7
  - [ ] Active: 5
  - [ ] Idle: 2
  - [ ] Errors: 0
  - [ ] Avg Boot Time: ~1250ms
- [ ] Cards update every 5 seconds (watch for changes)
- [ ] No JavaScript errors in console

**API Calls** (check Network tab):
- [ ] `GET /api/kernels/layer1/status` - 200 OK
- [ ] `GET /api/telemetry/kernels/status` - 200 OK

---

### Test 1.2: Quick Actions
**Steps**:
1. Click [⚡ Run Boot Stress] button
2. Click [🗑️ Flush Ingestion Queue] button
3. Click [🔐 Check Crypto Status] button

**Expected**:
- [ ] Each button triggers API call
- [ ] Alert/toast appears with result
- [ ] Button disables during action
- [ ] Metrics refresh after action

**API Calls**:
- [ ] `POST /api/telemetry/kernels/{id}/control?action=stress`
- [ ] `POST /api/ingestion/flush` (or similar)

---

### Test 1.3: Kernel Terminals - View
**Steps**:
1. Scroll to "Core Execution Kernels" section
2. Count kernel terminals displayed

**Expected**:
- [ ] See 7 kernel terminals:
  - [ ] Memory Kernel
  - [ ] Librarian Kernel
  - [ ] Governance Kernel
  - [ ] Verification Kernel
  - [ ] Self-Healing Kernel
  - [ ] Ingestion Kernel
  - [ ] Crypto Kernel
- [ ] Each shows: Name, Status, Uptime, Tasks
- [ ] Each has action buttons: [▶][■][↻][⚙][📋]

---

### Test 1.4: Kernel Terminal - Expand/Collapse
**Steps**:
1. Find "Memory Kernel" terminal
2. Click [▼] expand button
3. Wait for console to expand
4. Click [▲] collapse button

**Expected**:
- [ ] Terminal expands smoothly (animation)
- [ ] Console logs section appears
- [ ] Quick actions section appears
- [ ] Logs display (polling starts)
- [ ] Collapse hides sections
- [ ] Polling stops when collapsed

---

### Test 1.5: Kernel Logs
**Steps**:
1. Expand Memory Kernel terminal
2. Observe console logs section
3. Wait 10 seconds
4. Check for log updates

**Expected**:
- [ ] Logs display in console area
- [ ] Logs have timestamps
- [ ] Logs color-coded (ERROR=red, WARN=yellow, INFO=blue)
- [ ] Logs update every 5 seconds (polling)
- [ ] [Refresh] button manually fetches logs
- [ ] [Export] button downloads .txt file
- [ ] [Jump to Error] scrolls to first error

**API Calls**:
- [ ] `GET /api/kernels/memory-kernel-01/logs?lines=50` (every 5s)

---

### Test 1.6: Kernel Actions
**Steps**:
1. Click [↻ Restart] button on any kernel
2. Observe response

**Expected**:
- [ ] Button disables during action
- [ ] Alert/toast shows result
- [ ] Kernel status may update
- [ ] Action completes in < 2 seconds

**API Calls**:
- [ ] `POST /api/kernels/{id}/action` with `{action: "restart"}`

---

### Test 1.7: Co-Pilot Pane - Visibility
**Steps**:
1. Look at right side of screen

**Expected**:
- [ ] Co-pilot pane visible (380px width)
- [ ] Grace avatar displayed
- [ ] Status shows "Ready" (green)
- [ ] Notifications panel visible
- [ ] Chat interface visible
- [ ] Input field visible
- [ ] Quick actions visible (4 buttons for Layer 1)

---

### Test 1.8: Co-Pilot - Notifications
**Steps**:
1. Read notifications in co-pilot pane
2. Click action button in a notification
3. Click [✕] dismiss button

**Expected**:
- [ ] See 3 mock notifications
- [ ] Notifications have icons (🔴🟡🔵)
- [ ] Action buttons work
- [ ] Dismiss removes notification
- [ ] Notification count updates

**API Calls**:
- [ ] `GET /api/copilot/notifications`
- [ ] `POST /api/copilot/notifications/{id}/action`

---

### Test 1.9: Co-Pilot - Chat
**Steps**:
1. Type "help" in chat input
2. Click [Send]
3. Type "show kernel status"
4. Click [Send]

**Expected**:
- [ ] User message appears (right-aligned)
- [ ] Grace responds (left-aligned)
- [ ] Response contains text
- [ ] Response may have action buttons
- [ ] Chat scrolls to bottom
- [ ] Input clears after send

**API Calls**:
- [ ] `POST /api/copilot/chat/send`

---

### Test 1.10: Co-Pilot - Quick Actions
**Steps**:
1. Click each quick action button in co-pilot
   - [↻ Restart All Kernels]
   - [⚡ Run Stress Test]
   - [🔐 Check Crypto]
   - [📋 View System Logs]

**Expected**:
- [ ] Each action triggers
- [ ] Confirmation appears if needed
- [ ] Action executes successfully
- [ ] Dashboard updates accordingly

---

## Layer 2: HTM Console Tests

### Test 2.1: Page Load & Queue Metrics
**Steps**:
1. Click "Layer 2" navigation button

**Expected**:
- [ ] Page loads in < 3 seconds
- [ ] See "Layer 2: HTM Console" header
- [ ] Queue metrics grid displays (7 cards):
  - [ ] Queue Depth
  - [ ] Pending
  - [ ] Active
  - [ ] Completed
  - [ ] SLA Breaches
  - [ ] Avg Wait
  - [ ] P95 Duration
- [ ] Metrics update every 5 seconds

**API Calls**:
- [ ] `GET /api/kernels/layer2/status`
- [ ] `GET /api/telemetry/htm/queue`

---

### Test 2.2: HTM Quick Actions
**Steps**:
1. Click [⏸ Pause Queue]
2. Click [🗑️ Flush Completed]
3. Click [➕ Spawn Agent]

**Expected**:
- [ ] Each button triggers API call
- [ ] Alert shows result
- [ ] Queue metrics refresh
- [ ] Changes reflect in dashboard

**API Calls**:
- [ ] `POST /api/htm/pause`
- [ ] `POST /api/htm/flush`
- [ ] `POST /api/htm/spawn_agent`

---

### Test 2.3: Priority Sliders
**Steps**:
1. Adjust Critical slider to 1.5
2. Adjust High slider to 1.0
3. Click [Apply Priority Changes]

**Expected**:
- [ ] Sliders move smoothly
- [ ] Value displays next to slider
- [ ] Apply button triggers API call
- [ ] Success alert appears
- [ ] Queue metrics refresh

**API Calls**:
- [ ] `POST /api/htm/priorities` with updated weights

---

### Test 2.4: HTM Kernel Terminals
**Steps**:
1. Scroll to "HTM & Scheduler Kernels"
2. Verify kernel terminals displayed

**Expected**:
- [ ] See 5 kernel terminals:
  - [ ] HTM Queue Manager
  - [ ] Trigger Engine
  - [ ] Scheduler Kernel
  - [ ] Agent Pool Manager
  - [ ] Task Router
- [ ] Each shows status, metrics, action buttons
- [ ] Expand/collapse works
- [ ] Logs display when expanded

---

### Test 2.5: Co-Pilot Integration (Layer 2)
**Steps**:
1. Check co-pilot quick actions
2. Verify Layer 2 specific actions

**Expected**:
- [ ] Quick actions changed to Layer 2:
  - [ ] Spawn Extra Agent
  - [ ] Defer Low Priority
  - [ ] Clear Completed
  - [ ] Export Queue Snapshot
- [ ] Actions execute correctly
- [ ] Grace responds to "show queue status"

---

## Layer 3: Learning Console Tests

### Test 3.1: Page Load & Intent List
**Steps**:
1. Click "Layer 3" navigation button

**Expected**:
- [ ] Page loads in < 3 seconds
- [ ] See "Layer 3: Intent & Learning" header
- [ ] Intent table displays
- [ ] See [+ Create Intent] button
- [ ] Table shows columns: ID, Goal, Status, Progress, HTM Tasks, Created

**API Calls**:
- [ ] `GET /api/kernels/layer3/status`
- [ ] `GET /api/telemetry/intent/active`

---

### Test 3.2: Create Intent
**Steps**:
1. Click [+ Create Intent] button
2. Fill form:
   - Goal: "Test intent for QA"
   - Data Source: "Uploaded Files"
   - Priority: "Normal"
3. Click [Create Intent]

**Expected**:
- [ ] Modal opens
- [ ] Form fields editable
- [ ] Submit triggers API call
- [ ] Success alert appears
- [ ] Modal closes
- [ ] New intent appears in table
- [ ] Table refreshes

**API Calls**:
- [ ] `POST /api/intent/create`

---

### Test 3.3: Retrospectives List
**Steps**:
1. Scroll to "Recent Learning Cycles"
2. View retrospectives

**Expected**:
- [ ] Retrospective cards display
- [ ] Each card shows:
  - [ ] Cycle name
  - [ ] Timestamp
  - [ ] Insights list (💡)
  - [ ] Improvements list (⬆️)
- [ ] Cards are readable and well-formatted

**API Calls**:
- [ ] `GET /api/telemetry/learning/retrospectives?limit=5`

---

### Test 3.4: Agentic Brain Kernels
**Steps**:
1. Scroll to "Agentic Brain Kernels"
2. Verify kernel terminals

**Expected**:
- [ ] See 6 kernel terminals:
  - [ ] Learning Loop
  - [ ] Intent Engine
  - [ ] Policy AI
  - [ ] Enrichment Engine
  - [ ] Trust Core
  - [ ] Playbook Runtime
- [ ] Each terminal functional
- [ ] Expand/collapse works
- [ ] Actions executable

---

### Test 3.5: Co-Pilot Integration (Layer 3)
**Steps**:
1. Check co-pilot quick actions

**Expected**:
- [ ] Quick actions changed to Layer 3:
  - [ ] Create New Intent
  - [ ] Review Pending Policies
  - [ ] Generate Retrospective
  - [ ] Export Learning Report
- [ ] [Create New Intent] opens intent form
- [ ] Grace responds to learning queries

---

## Cross-Layer Tests

### Test 4.1: Navigation Between Layers
**Steps**:
1. Start on Layer 1
2. Click "Layer 2" button
3. Click "Layer 3" button
4. Click "Layer 1" button

**Expected**:
- [ ] Layer switches instantly
- [ ] Previous layer unmounts
- [ ] New layer loads and fetches data
- [ ] Co-pilot pane persists (doesn't reload)
- [ ] Co-pilot quick actions update per layer
- [ ] No memory leaks (check DevTools Memory)

---

### Test 4.2: Co-Pilot Persistence
**Steps**:
1. Type message in co-pilot chat on Layer 1
2. Switch to Layer 2
3. Check co-pilot pane

**Expected**:
- [ ] Chat history persists
- [ ] Notifications persist
- [ ] Quick actions update to Layer 2
- [ ] Input field maintains state

---

### Test 4.3: Concurrent Actions
**Steps**:
1. On Layer 1: Click restart on Memory Kernel
2. Immediately switch to Layer 2
3. Check both layers

**Expected**:
- [ ] Layer 1 action completes in background
- [ ] Layer 2 loads correctly
- [ ] No API conflicts
- [ ] Both layers functional

---

### Test 4.4: Auto-Refresh During Inactivity
**Steps**:
1. Load Layer 1
2. Do not interact for 1 minute
3. Observe telemetry cards

**Expected**:
- [ ] Metrics continue updating every 5 seconds
- [ ] No performance degradation
- [ ] Memory usage stable
- [ ] API calls continue

---

## Performance Tests

### Test 5.1: Load Time
**Measure** (DevTools Performance tab):
- [ ] Initial page load: < 3 seconds
- [ ] Layer switch time: < 500ms
- [ ] API response time: < 200ms (average)
- [ ] First Contentful Paint: < 1.5 seconds

---

### Test 5.2: Memory Usage
**Steps**:
1. Open DevTools → Memory tab
2. Take heap snapshot
3. Navigate all layers
4. Return to Layer 1
5. Take another heap snapshot

**Expected**:
- [ ] Memory increase < 20MB
- [ ] No memory leaks detected
- [ ] Heap size stabilizes
- [ ] Garbage collection working

---

### Test 5.3: Network Load
**Steps**:
1. Open DevTools → Network tab
2. Navigate through all layers
3. Wait 1 minute

**Expected**:
- [ ] Polling requests: ~12 per minute per layer
- [ ] Total bandwidth: < 100KB per minute
- [ ] No failed requests (check for 4xx/5xx)
- [ ] Reasonable request size

---

## Functional Integration Tests

### Test 6.1: End-to-End: Restart Kernel
**Steps**:
1. Navigate to Layer 1
2. Expand Memory Kernel
3. Note current uptime
4. Click [↻ Restart]
5. Wait for confirmation
6. Refresh page

**Expected**:
- [ ] Alert: "Action 'restart' executed successfully"
- [ ] Kernel status may briefly show "restarting"
- [ ] Uptime resets to 0m
- [ ] Logs show restart event
- [ ] Co-pilot may show notification

**API Flow**:
```
Frontend: POST /api/kernels/memory-kernel-01/action {action: "restart"}
Backend: Executes restart
Backend: Returns 200 OK
Frontend: Shows alert, refreshes data
```

---

### Test 6.2: End-to-End: Create Intent
**Steps**:
1. Navigate to Layer 3
2. Click [+ Create Intent]
3. Fill form:
   - Goal: "QA Test Intent"
   - Data Source: "Uploaded Files"
   - Priority: "High"
4. Click [Create Intent]
5. Check intent table

**Expected**:
- [ ] Modal opens
- [ ] Form submits successfully
- [ ] Alert: "Intent created successfully"
- [ ] Modal closes
- [ ] New intent appears in table
- [ ] Intent has ID, status "pending", 0% progress

**API Flow**:
```
Frontend: POST /api/intent/create {goal: "QA Test Intent", ...}
Backend: Creates intent, returns intent_id
Frontend: Refreshes intent list
Frontend: GET /api/telemetry/intent/active
Backend: Returns updated list with new intent
```

---

### Test 6.3: End-to-End: Spawn HTM Agent
**Steps**:
1. Navigate to Layer 2
2. Note current active agents (in queue metrics)
3. Click [➕ Spawn Agent] button
4. Wait for confirmation
5. Check queue metrics

**Expected**:
- [ ] Alert: "New agent spawned"
- [ ] Active agents count increases
- [ ] Capacity utilization may change
- [ ] Co-pilot may show notification

**API Flow**:
```
Frontend: POST /api/htm/spawn_agent
Backend: Spawns agent
Backend: Returns agent_id
Frontend: Shows alert
Frontend: Refreshes queue metrics
```

---

### Test 6.4: End-to-End: Co-Pilot Notification Action
**Steps**:
1. Navigate to any layer
2. Find notification in co-pilot pane
3. Click action button (e.g., [Restart])
4. Observe result

**Expected**:
- [ ] Action executes
- [ ] Notification dismissed
- [ ] Dashboard updates
- [ ] Toast/alert confirms

**API Flow**:
```
Frontend: Renders notification from GET /api/copilot/notifications
User: Clicks [Restart] button
Frontend: POST /api/copilot/notifications/{id}/action {action: "restart_kernel"}
Backend: Executes restart
Backend: Returns success
Frontend: Dismisses notification, shows toast
```

---

### Test 6.5: End-to-End: Chat with Grace
**Steps**:
1. Type "help" in co-pilot chat
2. Send message
3. Wait for response
4. Click action button in response (if any)

**Expected**:
- [ ] User message appears immediately
- [ ] Grace status changes to "Thinking..."
- [ ] Grace responds in < 2 seconds
- [ ] Grace message appears
- [ ] Action buttons clickable
- [ ] Actions execute correctly

**API Flow**:
```
Frontend: POST /api/copilot/chat/send {message: "help", context: {...}}
Backend: Processes message
Backend: Returns {text: "I can help...", actions: [...]}
Frontend: Renders Grace message
User: Clicks action button
Frontend: Executes action
```

---

### Test 6.6: End-to-End: Adjust HTM Priorities
**Steps**:
1. Navigate to Layer 2
2. Adjust all 4 priority sliders
3. Note new values
4. Click [Apply Priority Changes]
5. Reload page

**Expected**:
- [ ] Alert: "Priority weights updated"
- [ ] Sliders maintain values
- [ ] Queue metrics may change
- [ ] Settings persist (check with GET /api/htm/priorities)

**API Flow**:
```
Frontend: User adjusts sliders
Frontend: POST /api/htm/priorities {critical_weight: 1.5, ...}
Backend: Saves priorities
Backend: Returns success
Frontend: Shows alert
Frontend: Refreshes queue metrics
```

---

## Error Handling Tests

### Test 7.1: Network Failure
**Steps**:
1. Stop backend server
2. Try to load Layer 1
3. Try to click an action

**Expected**:
- [ ] Error toast/alert appears
- [ ] UI doesn't crash
- [ ] Helpful error message shown
- [ ] Retry option available

---

### Test 7.2: API Error (4xx)
**Steps**:
1. Manually trigger invalid API call (via browser console):
   ```javascript
   axios.post('http://localhost:8000/api/kernels/invalid-id/action', {action: 'restart'})
   ```

**Expected**:
- [ ] Error caught gracefully
- [ ] Error message displayed
- [ ] UI remains functional

---

### Test 7.3: Slow API Response
**Steps**:
1. Simulate slow network (DevTools → Network → Throttling → Slow 3G)
2. Click action button
3. Observe loading state

**Expected**:
- [ ] Button shows loading/spinner
- [ ] Button disabled during request
- [ ] Timeout after 30 seconds
- [ ] Error message if timeout

---

## User Experience Tests

### Test 8.1: Visual Consistency
**Checklist**:
- [ ] All layers use same color scheme
- [ ] Fonts consistent across pages
- [ ] Button styles uniform
- [ ] Card styles uniform
- [ ] Spacing consistent
- [ ] Co-pilot pane looks same on all layers

---

### Test 8.2: Responsiveness
**Steps**:
1. Resize browser window to 1024px width
2. Resize to 1440px width
3. Resize to 1920px width

**Expected** (MVP - Desktop Only):
- [ ] Layout adapts gracefully (no horizontal scroll)
- [ ] Co-pilot pane may overlap at <1600px (acceptable for MVP)
- [ ] All content readable
- [ ] No broken layouts

---

### Test 8.3: Accessibility (Basic)
**Steps**:
1. Navigate using Tab key only
2. Try to reach all interactive elements

**Expected**:
- [ ] Can tab through nav buttons
- [ ] Can tab through action buttons
- [ ] Can tab to kernel expand buttons
- [ ] Can tab to chat input
- [ ] Focus visible (outline/highlight)

---

## Stress Tests

### Test 9.1: Rapid Navigation
**Steps**:
1. Rapidly click between layers (10 times in 10 seconds)

**Expected**:
- [ ] No crashes
- [ ] Layers switch correctly
- [ ] No API call pileup
- [ ] Memory stable
- [ ] No JavaScript errors

---

### Test 9.2: Long-Running Session
**Steps**:
1. Load dashboard
2. Leave running for 10 minutes
3. Interact periodically (every 2 minutes)

**Expected**:
- [ ] No memory leaks
- [ ] Polling continues
- [ ] UI responsive throughout
- [ ] No errors accumulate

---

### Test 9.3: Multiple Concurrent Actions
**Steps**:
1. On Layer 1: Click restart on 3 different kernels rapidly
2. Observe results

**Expected**:
- [ ] All actions execute
- [ ] No race conditions
- [ ] All alerts appear
- [ ] Status updates correctly

---

## Data Accuracy Tests

### Test 10.1: Telemetry Accuracy
**Steps**:
1. Compare dashboard metrics to API responses
2. Use Postman/curl to call `GET /api/telemetry/kernels/status`
3. Verify numbers match UI

**Expected**:
- [ ] Total kernels matches
- [ ] Active count matches
- [ ] All metrics accurate
- [ ] Updates reflect within 5 seconds

---

### Test 10.2: Kernel Status Accuracy
**Steps**:
1. Check kernel status in dashboard
2. Call API directly to verify

**Expected**:
- [ ] Status (active/idle/error) matches
- [ ] Uptime matches
- [ ] Task count matches
- [ ] Metrics match

---

## Known Issues & Workarounds

### Issue 1: WebSocket Not Implemented (MVP)
**Impact**: Logs update every 5 seconds instead of real-time  
**Workaround**: Acceptable for MVP, using HTTP polling  
**Fix**: Post-MVP, implement WebSocket log streaming

### Issue 2: Grace Responses are Basic
**Impact**: Chat uses pattern matching, not true AI  
**Workaround**: Covers common queries ("help", "status", etc.)  
**Fix**: Post-MVP, integrate actual LLM (OpenAI/Anthropic)

### Issue 3: Multi-Modal Input Disabled
**Impact**: No voice/file/screenshot in MVP  
**Workaround**: Text-only chat is functional  
**Fix**: Post-MVP, add voice transcription and file upload

### Issue 4: Layer 4 Not Built
**Impact**: Cannot test secrets/recordings in MVP  
**Workaround**: Focus QA on Layers 1-3  
**Fix**: Build Layer 4 in next iteration

---

## User Feedback Collection

### Feedback Form Template

**After testing, collect feedback**:

```
GRACE Dashboard MVP - User Feedback

Tester Name: _______________
Date: _______________
Layer Tested: ☐ Layer 1  ☐ Layer 2  ☐ Layer 3

1. Overall Experience (1-5): ___

2. What worked well?
   ________________________________________________

3. What was confusing or didn't work?
   ________________________________________________

4. Missing features you need?
   ________________________________________________

5. Co-Pilot (Grace) usefulness (1-5): ___
   Comments:
   ________________________________________________

6. Kernel terminals usability (1-5): ___
   Comments:
   ________________________________________________

7. Performance issues noticed?
   ☐ Slow loading
   ☐ Laggy interactions
   ☐ Memory issues
   ☐ None

8. Suggestions for improvement:
   ________________________________________________
```

---

## Bug Report Template

```
GRACE Dashboard MVP - Bug Report

Bug ID: _______________
Reported By: _______________
Date: _______________

Layer: ☐ Layer 1  ☐ Layer 2  ☐ Layer 3  ☐ Co-Pilot

Severity: ☐ Critical  ☐ High  ☐ Medium  ☐ Low

Description:
________________________________________________

Steps to Reproduce:
1. ________________________________________________
2. ________________________________________________
3. ________________________________________________

Expected Behavior:
________________________________________________

Actual Behavior:
________________________________________________

Screenshots/Logs:
(Attach if available)

Browser Console Errors:
________________________________________________

Network Tab Errors:
________________________________________________
```

---

## QA Sign-Off Checklist

### Layer 1
- [ ] All telemetry cards display correctly
- [ ] Quick actions execute without errors
- [ ] 7 kernel terminals visible and functional
- [ ] Kernel expand/collapse works
- [ ] Logs display and update
- [ ] Kernel actions (restart, stop) work
- [ ] Co-pilot pane visible and functional

### Layer 2
- [ ] Queue metrics display correctly
- [ ] HTM quick actions work
- [ ] Priority sliders functional
- [ ] 5 HTM kernel terminals visible
- [ ] Logs display and update
- [ ] Co-pilot quick actions updated

### Layer 3
- [ ] Intent table displays
- [ ] Intent creation works
- [ ] Retrospectives display
- [ ] 6 agentic kernel terminals visible
- [ ] Co-pilot quick actions updated

### Cross-Layer
- [ ] Navigation works smoothly
- [ ] Co-pilot persists across layers
- [ ] No memory leaks
- [ ] Performance acceptable
- [ ] Error handling works

### Co-Pilot
- [ ] Notifications display
- [ ] Chat interface works
- [ ] Grace responds to queries
- [ ] Action buttons execute
- [ ] Quick actions work

---

## Final QA Approval

**Tested By**: _______________  
**Date**: _______________

**Result**: ☐ Pass  ☐ Fail  ☐ Pass with Issues

**Critical Issues Found**: _______________

**Approved for**: ☐ Internal Demo  ☐ User Testing  ☐ Production

**Notes**:
________________________________________________

---

## Post-QA Action Items

### High Priority Fixes
- [ ] Fix critical bugs
- [ ] Address performance issues
- [ ] Fix broken API calls

### Medium Priority
- [ ] Improve error messages
- [ ] Add missing loading states
- [ ] Polish UX based on feedback

### Low Priority / Post-MVP
- [ ] Add WebSocket streaming
- [ ] Integrate real LLM
- [ ] Build Layer 4
- [ ] Add mobile support
- [ ] Add voice/file input

---

**Ready for QA testing!** Run through this checklist and collect feedback before proceeding to Layer 4. 🧪✅
