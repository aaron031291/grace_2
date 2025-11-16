# Dashboard Wireframe Quick Reference Card

**Print this or keep it visible while wireframing** 📌

---

## 🎛️ Layer 1: Operations Console

### Key Screens
1. **Main View**: Metrics grid + kernel table + crypto/ingestion cards
2. **Logs Modal**: Full-screen scrollable log viewer

### Data Sources (5 endpoints)
```
✅ GET /api/telemetry/kernels/status          → Header metrics + table
✅ GET /api/telemetry/crypto/health           → Crypto cards
✅ GET /api/telemetry/ingestion/throughput    → Ingestion cards
✅ POST /kernels/{id}/control?action=restart  → Control kernel
✅ GET /kernels/{id}/logs?lines=100           → View logs
```

### Critical UI Elements
- **5 metric cards**: Total, Active, Idle, Errors, Avg Boot Time
- **Table (8 cols)**: ID, Name, Status, Health, Uptime, Tasks, Errors, Stress, Actions
- **4 action buttons per row**: Restart, Stop, Stress, Logs
- **Status badges**: 4 colors (green=active, yellow=idle, red=error, blue=booting)
- **Stress bars**: 0-100% gradient (green → yellow → red)

### User Flows
1. **Control kernel**: Click button → Spinner → Toast → Row updates
2. **View logs**: Click → Modal opens → Auto-refresh 3s → Close

---

## 📊 Layer 2: HTM Console

### Key Screens
1. **Main View**: Queue metrics + workload + origin stats + task table
2. **Priority Modal**: Change task priority form

### Data Sources (4 endpoints)
```
✅ GET /api/telemetry/htm/queue               → Queue metrics
✅ GET /api/telemetry/htm/tasks?origin=X&status=Y  → Task list
✅ GET /api/telemetry/htm/workload            → Workload cards
✅ POST /htm/tasks/{id}/priority              → Override priority
```

### Critical UI Elements
- **9 queue cards**: Depth, Pending, Active, Completed, Failed, Wait Time, P95, Avg Size, SLA
- **4 workload cards**: Agents, Escalations, Capacity %, Status
- **3 origin cards**: Filesystem, Remote, Hunter (with avg duration/size)
- **Table (8 cols)**: ID, Origin, Status, Priority, Size, Duration, Created, Actions
- **2 filter dropdowns**: Origin, Status
- **Context menu**: Right-click for actions

### User Flows
1. **Filter tasks**: Select dropdown → Table refreshes
2. **Change priority**: Right-click → Modal → Select + Reason → Submit → Row updates

---

## 🧠 Layer 3: Intent & Learning

### Key Screens
1. **Main View**: Intent cards + playbook table + retrospectives + policies
2. **Intent Detail Modal**: Linked HTM tasks + insights
3. **Policy Action Modal**: Confirmation with notes

### Data Sources (6 endpoints)
```
✅ GET /api/telemetry/intent/active           → Intent cards
✅ GET /api/telemetry/intent/{id}/details     → Intent modal
✅ GET /learning/retrospectives               → Retro cards
✅ GET /learning/playbooks                    → Success table
✅ GET /learning/policy_suggestions           → Policy cards
✅ POST /policy_suggestions/{id}/respond      → Accept/review/reject
```

### Critical UI Elements
- **Intent cards**: Goal, Status, Progress bar, HTM count, Created date
- **Playbook table (3 cols)**: Name, Total Runs, Success % (with bar)
- **Retrospective cards**: Cycle name, Insights (💡), Improvements (⬆️)
- **Policy cards**: Area badge, Suggestion, Confidence badge, Evidence, 3 action buttons

### User Flows
1. **View intent details**: Click card → Modal → Show HTM tasks + insights
2. **Respond to policy**: Click [Accept/Review/Reject] → Modal → Notes → Submit → Card removed

---

## ⚙️ Layer 4: Dev/OS View

### Key Screens
1. **Main View**: Secrets cards + deployment cards + recordings table + sessions table
2. **Add Secret Flow**: Form modal → Consent modal (overlay)
3. **Stress Test Modal**: Config form → Progress modal

### Data Sources (9 endpoints)
```
✅ GET /api/telemetry/secrets/status          → Vault cards
✅ POST /api/secrets/store                    → Save secret
✅ GET /recordings/pending                    → Recordings table
✅ POST /recording/ingest/{id}                → Start ingestion
✅ GET /recording/ingest/{job}/status         → Poll progress
✅ GET /remote_access/sessions                → Sessions table
✅ GET /deployment/status                     → Deployment cards
✅ POST /api/stress/run                       → Start stress test
✅ GET /api/stress/{id}/status                → Poll test
```

### Critical UI Elements
- **3 secrets cards**: Total, Encrypted, Health
- **5 deployment cards**: Last Deploy, Environment, Version, Health, Pending Tests
- **Recordings table (5 cols)**: ID, Type (icon), Filename, Size, Created, Actions
- **Sessions table (6 cols)**: ID, User, Status, Started, Ended, Duration
- **Add secret form**: Name, Value (password), Category dropdown
- **Consent modal**: Checklist info, Yes/No buttons

### User Flows
1. **Save secret**: [+Add] → Form → [Save] → Consent → [Yes] → Toast → Vault refreshes
2. **Ingest recording**: [Ingest] → Processing badge → Poll 5s → Complete toast
3. **Run stress test**: [Run] → Config → [Start] → Progress → Results

---

## 🌐 WebSocket (All Layers)

```
✅ ws://localhost:8000/ws/telemetry
```

**Broadcast**: Every 2 seconds  
**Updates**: Kernel metrics, HTM queue, Crypto status  
**UI**: Live indicator (pulsing green dot), auto-refresh metrics

---

## Color Palette

| Use Case | Color | Hex |
|----------|-------|-----|
| **Success/Active** | Green | `#00ff88` |
| **Warning/Idle** | Yellow | `#ffaa00` |
| **Error/Failed** | Red | `#ff4444` |
| **Info/Booting** | Blue | `#00aaff` |
| **Neutral** | Gray | `#888888` |
| **Background** | Near Black | `#0a0a0a` |
| **Surface** | Dark Gray | `#1a1a1a` |
| **Border** | Med Gray | `#333333` |
| **Text Primary** | Light Gray | `#e0e0e0` |
| **Text Secondary** | Med Gray | `#888888` |

---

## Typography

| Element | Size | Weight |
|---------|------|--------|
| Dashboard Title (H1) | 28px | Bold |
| Section Title (H2) | 20px | Bold |
| Card Title (H3) | 16px | Semi-bold |
| Body Text | 14px | Normal |
| Labels | 12px | Normal |
| Badge Text | 10-11px | Bold, Uppercase |

**Font**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif  
**Mono**: Courier New (for IDs, logs)

---

## Component Specs

### Badges
- Padding: `4px 12px`
- Border-radius: `12px`
- Font-size: `10-11px`
- Font-weight: `bold`
- Text-transform: `uppercase`

### Progress Bars
- Height: `8-12px`
- Border-radius: `4-6px`
- Fill: Gradient (green → yellow → red for stress)

### Cards
- Border: `1px solid #333`
- Border-radius: `8-10px`
- Background: `#1a1a1a`
- Padding: `20px`

### Tables
- Header bg: `#2a2a2a`
- Row hover: `#252525`
- Cell padding: `12px`

### Modals
- Overlay: `rgba(0,0,0,0.85)`
- Max-width: `500px` (small), `1000px` (large)
- Border-radius: `10px`

### Buttons
- Small: `6px 12px` padding
- Normal: `8px 16px` padding
- Large: `10px 20px` padding

---

## State Indicators

| State | Visual |
|-------|--------|
| **Loading** | Spinner icon, disabled button, dimmed row |
| **Success** | Green toast (3s), checkmark icon |
| **Error** | Red toast (5s), error icon, retry button |
| **Empty** | Gray placeholder text, icon, call-to-action |
| **Active** | Pulsing green dot (WebSocket) |

---

## Interaction Patterns

### Click Flows
1. **Button → Spinner → Toast → Update**
   - Disable button, show spinner
   - API call
   - Show toast notification
   - Update UI element

2. **Form → Validation → Submit → Feedback**
   - Inline validation on blur
   - Disable form on submit
   - Show spinner
   - Success/error feedback

3. **Modal → Action → Confirmation → Result**
   - Open modal
   - User action (fill form)
   - Optional confirmation step
   - Close modal, show result

### Polling Patterns
- **Job Progress**: Poll every 5s until complete
- **Live Updates**: WebSocket broadcast every 2s
- **Auto-refresh**: Configurable 5-10s intervals

---

## Responsive Breakpoints

| Size | Width | Adjustments |
|------|-------|-------------|
| **Desktop** | > 1200px | Full layout, multi-column grids |
| **Tablet** | 768-1200px | 2-column grids, simplified tables |
| **Mobile** | < 768px | Single column, card-based, bottom sheets |

---

## Priority Checklist

### Must-Have (MVP)
- ✅ All 4 layer views functional
- ✅ Data displays from all endpoints
- ✅ Critical user flows (control, filter, save)
- ✅ Error states
- ✅ Loading states

### Should-Have
- ✅ WebSocket live updates
- ✅ Auto-refresh toggles
- ✅ Modal confirmations
- ✅ Toast notifications
- ✅ Progress indicators for async jobs

### Nice-to-Have
- Charts (bar, line, scatter)
- Advanced filtering
- Bulk actions
- Export data
- Dark/light theme toggle

---

## Testing Scenarios

1. **Layer 1**: Control kernel (restart) → verify status updates
2. **Layer 2**: Filter tasks by origin → verify table updates
3. **Layer 3**: Accept policy → verify card removed
4. **Layer 4**: Save secret → verify consent flow → verify vault updates
5. **All**: Check WebSocket connection → verify live updates

---

## Wireframe Deliverables

For each layer, provide:

1. **Low-fidelity wireframes** (boxes and labels)
2. **High-fidelity mockups** (with real data)
3. **Interaction flows** (annotated sequences)
4. **Responsive layouts** (desktop, tablet, mobile)
5. **Component library** (reusable elements)

---

**Need details?** → See [WIREFRAMING_BRIEF.md](./WIREFRAMING_BRIEF.md)  
**Need APIs?** → See [DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md)  
**Need flows?** → See [DASHBOARD_DATA_FLOWS.md](./DASHBOARD_DATA_FLOWS.md)

**🎨 Ready to wireframe!**
