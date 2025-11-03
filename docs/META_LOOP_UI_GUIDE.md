# Meta-Loop Approval UI - Complete Guide

## 🎯 Overview

The Meta-Loop Approval UI provides a comprehensive dashboard for managing Grace's self-optimization recommendations. It allows operators to review, approve, reject, and monitor the effectiveness of meta-level changes.

## 📁 Component Structure

### Frontend Components

1. **`MetaLoopDashboard.tsx`** - Main dashboard with 3 tabs
   - Location: `grace-frontend/src/components/MetaLoopDashboard.tsx`
   - Features:
     - Tab-based navigation (Pending/Applied/Performance)
     - Real-time updates via WebSocket
     - Auto-refresh every 10 seconds
     - Full approval workflow integration

2. **`RecommendationCard.tsx`** - Individual recommendation display
   - Location: `grace-frontend/src/components/RecommendationCard.tsx`
   - Features:
     - Visual diff (current → proposed value)
     - Risk level badge (low/medium/high)
     - Predicted impact bar
     - Reasoning display
     - Approve/Reject buttons

### Backend API Endpoints

**Base URL:** `http://localhost:8000/api/meta/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/recommendations/pending` | GET | Get all pending recommendations |
| `/recommendations/applied` | GET | Get history of applied changes |
| `/recommendations/{id}/approve` | POST | Approve and apply a recommendation |
| `/recommendations/{id}/reject` | POST | Reject a recommendation |
| `/changes/{id}/rollback` | POST | Rollback an applied change |
| `/performance` | GET | Get performance analytics |
| `/test/create-samples` | POST | Create sample data for testing |

### WebSocket

**Endpoint:** `ws://localhost:8000/ws/meta-updates?token={jwt_token}`

**Event Types:**
- `new_recommendation` - New recommendation submitted
- `recommendation_applied` - Recommendation approved and applied

## 🚀 Quick Start

### 1. Start the Backend

```bash
cd grace_rebuild/backend
uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend

```bash
cd grace_rebuild/grace-frontend
npm run dev
```

### 3. Access the UI

1. Open browser to `http://localhost:5173`
2. Login with credentials: `admin` / `admin123`
3. Click "🧠 Meta-Loop" button in navigation

### 4. Create Test Data

**Option A - Via API:**
```bash
curl -X POST http://localhost:8000/api/meta/test/create-samples
```

**Option B - Via Batch Script:**
```bash
cd grace_rebuild
create_test_recs.bat
```

## 📊 UI Features

### Pending Recommendations Tab

**What You'll See:**
- List of all pending recommendations awaiting approval
- Each card shows:
  - Component name (e.g., "Reflection Loop")
  - Recommendation type (e.g., "interval_adjustment")
  - Current value → Proposed value with % change
  - Risk level badge (color-coded)
  - Predicted impact (+XX% improvement)
  - Reasoning/justification
  - Approve & Reject buttons

**Risk Level Colors:**
- 🟢 **Low Risk** - Green badge, safe to approve
- 🟡 **Medium Risk** - Yellow badge, requires review
- 🔴 **High Risk** - Red badge, careful consideration needed

**User Actions:**
1. Click **"✅ Approve & Apply"** to:
   - Mark recommendation as approved
   - Apply the change immediately
   - Record the approval in audit log
   - Move to Applied Changes tab

2. Click **"❌ Reject"** to:
   - Mark recommendation as rejected
   - Remove from pending queue
   - Record rejection reason

### Applied Changes Tab

**What You'll See:**
- History of all applied recommendations
- Each entry shows:
  - Component and change type
  - Timestamp and approver
  - Before/After values
  - Performance metrics (response time, success rate)
  - Improvement percentage (green if positive, red if negative)
  - Rollback button (for negative improvements)

**Metrics Display:**
- **Before Metrics vs After Metrics**
  - Response Time: XXms → YYms
  - Success Rate: XX% → YY%
  
- **Improvement %**
  - Green ↑ XX% - Performance improved
  - Red ↓ XX% - Performance degraded

**Rollback Feature:**
- Appears when improvement_pct < 0 (performance degraded)
- Click **"⚠️ Rollback"** to revert change
- Restores previous configuration
- Records rollback in audit log

### Performance Tab

**Analytics Displayed:**

1. **Summary Metrics (3 cards)**
   - Acceptance Rate: % of recommendations approved
   - Avg Improvement: Average effectiveness score
   - Total Optimizations: Count of applied changes

2. **Effectiveness Over Time**
   - Bar chart showing meta-loop performance
   - Each bar represents one optimization
   - Hover to see timestamp and score
   - Empty state: "Not enough data yet"

3. **Component Performance Trends**
   - Mini charts for each component
   - Shows value changes over time
   - Identifies which components benefit most
   - Helps prioritize future optimizations

## 🔄 Complete Workflow Example

### Scenario: Reflection Loop Interval Optimization

1. **Meta-Loop Detects Issue**
   - Current reflection interval: 300 seconds
   - Analysis shows this is too slow
   - Creates recommendation to reduce to 120 seconds

2. **Operator Reviews Recommendation**
   - Opens Meta-Loop dashboard
   - Sees "Reflection Loop" recommendation
   - Risk Level: LOW
   - Predicted Impact: +35.5% improvement
   - Reasoning: "Current 5-minute interval causes delayed insights..."

3. **Operator Approves**
   - Clicks "Approve & Apply"
   - Backend immediately applies change
   - Reflection interval now 120 seconds

4. **System Measures Effectiveness**
   - Collects metrics for 24-48 hours
   - Compares before/after performance
   - Calculates improvement percentage

5. **Results Displayed**
   - Applied Changes tab shows:
     - Old value: 300 → New value: 120
     - Response time improved
     - Success rate increased
     - Improvement: +38.2% (green indicator)

6. **If Performance Degraded**
   - Improvement shows: -15.3% (red)
   - Rollback button appears
   - Operator can revert change
   - System learns from failure

## 🎨 UI Design Details

### Color Scheme
- Background: `#0f0f1e` (dark blue)
- Cards: `#1a1a2e` (lighter blue)
- Primary Accent: `#7b2cbf` (purple)
- Secondary Accent: `#00d4ff` (cyan)
- Success: `#00ff88` (green)
- Warning: `#ffcc00` (yellow)
- Error: `#ff4444` (red)

### Typography
- Headers: Bold, cyan color
- Body: Regular, white
- Metadata: Small, gray (#888)

### Interactive Elements
- Buttons have hover states
- Cards have subtle borders
- Progress bars animate on load
- Charts are interactive (hover for details)

## 🧪 Testing Checklist

### Manual Testing Steps

1. **Pending Recommendations**
   - [ ] View list of pending recommendations
   - [ ] Risk levels display correctly
   - [ ] Current → Proposed values shown
   - [ ] Predicted impact displays
   - [ ] Reasoning text readable
   - [ ] Approve button works
   - [ ] Reject button works
   - [ ] Recommendation disappears after approval
   - [ ] Counter updates in tab label

2. **Applied Changes**
   - [ ] Applied changes appear after approval
   - [ ] Before/After metrics display
   - [ ] Improvement % calculated correctly
   - [ ] Green for positive, red for negative
   - [ ] Rollback button appears for negatives
   - [ ] Timestamp and approver shown
   - [ ] Rollback functionality works

3. **Performance Tab**
   - [ ] Acceptance rate calculates
   - [ ] Average improvement shows
   - [ ] Total optimizations count correct
   - [ ] Effectiveness chart renders
   - [ ] Component trends display
   - [ ] Empty states show when no data
   - [ ] Hover tooltips work on charts

4. **Real-time Updates**
   - [ ] WebSocket connects
   - [ ] New recommendations appear automatically
   - [ ] Applied changes update in real-time
   - [ ] Polling works if WebSocket fails

5. **Error Handling**
   - [ ] API errors handled gracefully
   - [ ] Loading states display
   - [ ] Network errors don't crash UI
   - [ ] Invalid data handled

## 🔧 Integration Points

### Backend Dependencies

- `meta_loop_approval.py` - Approval queue management
- `meta_loop_engine.py` - Recommendation application
- `meta_api.py` - REST API endpoints
- `websocket_routes.py` - WebSocket handler
- `governance.py` - Policy enforcement
- `verification.py` - Audit trail

### Data Flow

```
Meta-Loop Analysis
    ↓
Recommendation Queue
    ↓
Pending Recommendations API
    ↓
Frontend Display
    ↓
User Approval
    ↓
Governance Check
    ↓
Apply Change
    ↓
Measure Effectiveness
    ↓
Applied Changes History
```

## 📈 Metrics Tracked

### Recommendation Metrics
- Submission time
- Confidence score (0.0-1.0)
- Risk level (low/medium/high)
- Predicted impact (%)

### Application Metrics
- Applied timestamp
- Approver username
- Before/after response time
- Before/after success rate
- Effectiveness score
- Rollback status

### Performance Metrics
- Acceptance rate
- Average improvement
- Component-specific trends
- Time-series effectiveness

## 🛡️ Security Features

1. **Authentication Required**
   - JWT token validation
   - User must be logged in

2. **Governance Integration**
   - Policy checks before applying
   - Audit trail for all actions
   - Cryptographic verification

3. **Rollback Protection**
   - Can revert failed changes
   - Preserves system stability
   - Records rollback reasons

## 🐛 Troubleshooting

### Common Issues

**Problem:** No recommendations showing
- **Solution:** Run `/api/meta/test/create-samples` to generate test data

**Problem:** WebSocket not connecting
- **Solution:** UI falls back to polling, check browser console for errors

**Problem:** Approve button doesn't work
- **Solution:** Check browser console, verify backend is running, check auth token

**Problem:** Performance charts empty
- **Solution:** Need at least one applied recommendation with measured effectiveness

**Problem:** 404 on API calls
- **Solution:** Verify backend server running on port 8000

## 📝 Future Enhancements

- [ ] Batch approval/rejection
- [ ] Filtering and search
- [ ] Export to CSV
- [ ] Recommendation comments
- [ ] A/B testing support
- [ ] Schedule delayed application
- [ ] Automatic rollback thresholds
- [ ] Slack/email notifications
- [ ] Mobile-responsive design
- [ ] Dark/light theme toggle

## 🎓 Training Material

### For Operators

1. **Daily Routine**
   - Check Pending Recommendations tab
   - Review risk levels
   - Approve low-risk items
   - Schedule review for high-risk items
   - Monitor Performance tab weekly

2. **Best Practices**
   - Always read reasoning before approving
   - Be cautious with HIGH risk items
   - Monitor Applied Changes for regressions
   - Use rollback if metrics degrade
   - Document approval decisions

3. **When to Rollback**
   - Improvement % is negative
   - Error rates increased
   - Response time degraded
   - User complaints spike
   - System instability observed

---

**Built with:** React + TypeScript + Vite + FastAPI + WebSocket + PostgreSQL
**Version:** 1.0.0
**Last Updated:** 2025-11-02
