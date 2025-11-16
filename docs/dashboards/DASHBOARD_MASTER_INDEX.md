# GRACE Dashboard System - Master Index 📚

**Complete documentation suite for the GRACE multi-layer dashboard system**

---

## 🎯 Start Here

### For Designers/Wireframers
👉 **[WIREFRAMING_BRIEF.md](./WIREFRAMING_BRIEF.md)** - Your main reference  
   - Exact data contracts for each layer
   - User interaction flows with sequences
   - UI element specifications
   - Design tokens and style guide

📋 **[WIREFRAME_QUICK_REFERENCE.md](./WIREFRAME_QUICK_REFERENCE.md)** - Print this!  
   - One-page cheat sheet
   - Color codes, fonts, spacing
   - Component specs
   - State indicators

### For Frontend Developers
👉 **[DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md)** - Complete API spec  
   - All 26 endpoints with exact payloads
   - Request/response examples
   - Field definitions and types
   - Error responses

🔧 **[DASHBOARD_INTEGRATION.md](./DASHBOARD_INTEGRATION.md)** - Setup guide  
   - Backend route registration
   - Frontend component integration
   - Testing procedures
   - Troubleshooting

### For Backend Developers
✅ **[BACKEND_ENDPOINTS_CONFIRMED.md](./BACKEND_ENDPOINTS_CONFIRMED.md)** - Endpoint inventory  
   - 26 REST + 1 WebSocket confirmed ready
   - Service dependencies mapped
   - Database models required
   - Integration checklist

🗺️ **[DASHBOARD_DATA_FLOWS.md](./DASHBOARD_DATA_FLOWS.md)** - Visual flows  
   - ASCII data flow diagrams
   - State machine diagrams
   - Component relationships
   - Error handling patterns

### For Everyone
📖 **[TELEMETRY_DASHBOARD_GUIDE.md](./TELEMETRY_DASHBOARD_GUIDE.md)** - Technical guide  
   - System architecture
   - Installation & deployment
   - Usage instructions
   - Production considerations

📄 **[DASHBOARD_COMPLETE_SPEC.md](./DASHBOARD_COMPLETE_SPEC.md)** - Unified spec  
   - Component architecture
   - File manifest
   - Success metrics
   - Testing strategy

🎉 **[DASHBOARD_DELIVERY_SUMMARY.md](../DASHBOARD_DELIVERY_SUMMARY.md)** - Executive summary  
   - What was delivered
   - Project metrics
   - Next steps for each role

---

## 📂 Documentation Map

```
docs/
├── DASHBOARD_MASTER_INDEX.md           ← You are here
│
├── For Designers:
│   ├── WIREFRAMING_BRIEF.md            ⭐ Main reference
│   └── WIREFRAME_QUICK_REFERENCE.md    📋 Cheat sheet
│
├── For Frontend Developers:
│   ├── DASHBOARD_API_CONTRACT.md       ⭐ API spec
│   └── DASHBOARD_INTEGRATION.md        🔧 Setup guide
│
├── For Backend Developers:
│   ├── BACKEND_ENDPOINTS_CONFIRMED.md  ✅ Endpoint list
│   └── DASHBOARD_DATA_FLOWS.md         🗺️ Flow diagrams
│
└── For Everyone:
    ├── TELEMETRY_DASHBOARD_GUIDE.md    📖 Technical guide
    ├── DASHBOARD_COMPLETE_SPEC.md      📄 Unified spec
    └── DASHBOARD_DELIVERY_SUMMARY.md   🎉 Summary
```

---

## 🎛️ Layer 1: Operations Console

**What it does**: Real-time kernel monitoring, crypto health, ingestion metrics

**UI Components**:
- Kernel metrics grid (5 cards)
- Kernel status table (8 columns)
- Crypto health grid (5-6 cards)
- Ingestion throughput grid (4-5 cards)
- Kernel log viewer (modal)

**Data Sources** (5 endpoints):
- `GET /api/telemetry/kernels/status`
- `GET /api/telemetry/crypto/health`
- `GET /api/telemetry/ingestion/throughput`
- `POST /api/telemetry/kernels/{id}/control`
- `GET /api/telemetry/kernels/{id}/logs`

**Key Interactions**:
- Control kernel (start/stop/restart/stress)
- View kernel logs (real-time streaming)

**Wireframe Reference**: [WIREFRAMING_BRIEF.md - Layer 1](./WIREFRAMING_BRIEF.md#layer-1-operations-console-)

---

## 📊 Layer 2: HTM Console

**What it does**: Task queue management with timing/size analytics, SLA tracking

**UI Components**:
- Queue metrics grid (9 cards)
- Workload perception grid (4 cards)
- Origin performance cards (3 cards)
- Size distribution chart
- Task table with filters (8 columns)
- Priority override modal

**Data Sources** (4 endpoints):
- `GET /api/telemetry/htm/queue`
- `GET /api/telemetry/htm/tasks` (with filters)
- `GET /api/telemetry/htm/workload`
- `POST /api/telemetry/htm/tasks/{id}/priority`

**Key Interactions**:
- Filter tasks by origin/status
- Override task priority (context menu)

**Wireframe Reference**: [WIREFRAMING_BRIEF.md - Layer 2](./WIREFRAMING_BRIEF.md#layer-2-htm-console-)

---

## 🧠 Layer 3: Intent & Learning

**What it does**: Agentic goals, learning retrospectives, AI policy suggestions

**UI Components**:
- Active intent cards (with progress bars)
- Intent detail modal (linked HTM tasks)
- Playbook success table (3 columns)
- Retrospectives list (insights + improvements)
- Policy suggestion cards (with evidence)
- Policy response modal (accept/review/reject)

**Data Sources** (6 endpoints):
- `GET /api/telemetry/intent/active`
- `GET /api/telemetry/intent/{id}/details`
- `GET /api/telemetry/learning/retrospectives`
- `GET /api/telemetry/learning/playbooks`
- `GET /api/telemetry/learning/policy_suggestions`
- `POST /api/telemetry/learning/policy_suggestions/{id}/respond`

**Key Interactions**:
- View intent details (modal with HTM tasks)
- Respond to policy suggestion (accept/review/reject)

**Wireframe Reference**: [WIREFRAMING_BRIEF.md - Layer 3](./WIREFRAMING_BRIEF.md#layer-3-intent--learning-)

---

## ⚙️ Layer 4: Dev/OS View

**What it does**: Secrets vault, recording ingestion, deployment status

**UI Components**:
- Secrets vault grid (3 cards)
- Add secret form (modal)
- Consent modal (overlay)
- Deployment status grid (5 cards)
- Recordings table (5 columns)
- Remote access sessions table (6 columns)
- Stress test config modal
- Stress test progress modal

**Data Sources** (9 endpoints):
- `GET /api/telemetry/secrets/status`
- `POST /api/secrets/store`
- `GET /api/telemetry/recordings/pending`
- `POST /api/recording/ingest/{id}`
- `GET /api/recording/ingest/{job_id}/status`
- `GET /api/telemetry/remote_access/sessions`
- `GET /api/telemetry/deployment/status`
- `POST /api/stress/run`
- `GET /api/stress/{id}/status`

**Key Interactions**:
- Save secret (form → consent → encrypted storage)
- Ingest recording (async job with polling)
- Run stress test (config → progress → results)

**Wireframe Reference**: [WIREFRAMING_BRIEF.md - Layer 4](./WIREFRAMING_BRIEF.md#layer-4-devos-view-)

---

## 🌐 Real-Time Updates

**WebSocket**: `ws://localhost:8000/ws/telemetry`

**Broadcast Interval**: 2 seconds

**What updates**:
- Kernel metrics (total, active, idle, errors)
- HTM queue metrics (depth, pending, active)
- Crypto status (health, signatures, failures)

**UI Integration**:
- Live indicator (pulsing green dot)
- Auto-update metrics without full refresh
- Reconnect on disconnect

**Reference**: [DASHBOARD_API_CONTRACT.md - WebSocket](./DASHBOARD_API_CONTRACT.md#websocket-real-time-updates)

---

## 🎨 Design System

### Colors
| Use | Hex | Name |
|-----|-----|------|
| Success | `#00ff88` | Green |
| Warning | `#ffaa00` | Yellow |
| Error | `#ff4444` | Red |
| Info | `#00aaff` | Blue |
| Background | `#0a0a0a` | Near Black |
| Surface | `#1a1a1a` | Dark Gray |

### Typography
- **Font**: Segoe UI, Tahoma, sans-serif
- **Mono**: Courier New
- **Sizes**: 28px (H1), 20px (H2), 14px (body), 12px (labels)

### Components
- **Badges**: 4-12px padding, 12px radius, uppercase
- **Cards**: 20px padding, 8-10px radius
- **Progress Bars**: 8-12px height, gradient fill
- **Tables**: 12px cell padding, striped rows

**Full Reference**: [WIREFRAME_QUICK_REFERENCE.md - Design Tokens](./WIREFRAME_QUICK_REFERENCE.md#color-palette)

---

## 🔄 Key User Flows

### 1. Control Kernel
```
Click button → Spinner → API call → Success toast → Status update
```
**Time**: 1-3 seconds  
**States**: Idle → Loading → Success/Error

### 2. Save Secret
```
[+Add] → Form → [Save] → Consent modal → [Yes] → Encrypt → Toast
```
**Time**: 5-10 seconds  
**States**: Idle → Form → Consent → Submitting → Success/Error  
**Security**: AES-256 encryption, audit logging

### 3. Ingest Recording
```
[Ingest] → Start job → Poll status (5s) → Progress updates → Complete toast
```
**Time**: 5-20 minutes (async)  
**States**: Pending → Starting → Processing → Completed/Failed  
**Polling**: Every 5 seconds until done

### 4. Respond to Policy
```
[Accept] → Confirmation → Notes → Submit → Create task → Remove card
```
**Time**: 2-5 seconds  
**States**: Idle → Modal → Submitting → Success/Error  
**Actions**: Accept (create task), Review (schedule), Reject (close)

**All Flows**: [WIREFRAMING_BRIEF.md - Interaction Flows](./WIREFRAMING_BRIEF.md#interaction-flow-control-kernel)

---

## 📊 Data Summary

### Total Data Points

| Layer | Endpoints | UI Components | User Flows |
|-------|-----------|---------------|------------|
| Layer 1 | 5 | 10+ | 2 |
| Layer 2 | 4 | 12+ | 2 |
| Layer 3 | 6 | 10+ | 2 |
| Layer 4 | 9 | 15+ | 4 |
| **Total** | **26** | **47+** | **10** |

### Field Counts

| Data Type | Fields |
|-----------|--------|
| Kernel metrics | 10 per kernel |
| HTM task data | 8 per task |
| Intent data | 7 per intent |
| Secret data | 6 per secret |
| Recording data | 5 per recording |

**All Fields**: [DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md)

---

## ✅ Implementation Checklist

### Backend
- [ ] Register telemetry routes in FastAPI
- [ ] Start WebSocket broadcaster on startup
- [ ] Implement/stub service classes
- [ ] Create database models
- [ ] Add authentication middleware
- [ ] Configure CORS
- [ ] Set up logging

### Frontend
- [ ] Create UnifiedDashboard router
- [ ] Implement Layer 1-4 components
- [ ] Add API client wrapper
- [ ] Connect WebSocket
- [ ] Add polling for async jobs
- [ ] Implement toast notifications
- [ ] Add loading/error states

### Testing
- [ ] Unit tests for endpoints
- [ ] Integration tests for flows
- [ ] WebSocket tests
- [ ] Polling behavior tests
- [ ] Error scenario tests
- [ ] Load tests

**Full Checklist**: [BACKEND_ENDPOINTS_CONFIRMED.md - Integration](./BACKEND_ENDPOINTS_CONFIRMED.md#integration-checklist)

---

## 🚀 Getting Started

### 1. Designers/Wireframers
1. Read [WIREFRAMING_BRIEF.md](./WIREFRAMING_BRIEF.md)
2. Print [WIREFRAME_QUICK_REFERENCE.md](./WIREFRAME_QUICK_REFERENCE.md)
3. Start wireframing Layer 1 (simplest)
4. Move to Layers 2-4
5. Create responsive layouts

### 2. Frontend Developers
1. Read [DASHBOARD_INTEGRATION.md](./DASHBOARD_INTEGRATION.md)
2. Reference [DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md)
3. Set up API client
4. Implement components layer by layer
5. Test with mock data

### 3. Backend Developers
1. Read [BACKEND_ENDPOINTS_CONFIRMED.md](./BACKEND_ENDPOINTS_CONFIRMED.md)
2. Review [DASHBOARD_DATA_FLOWS.md](./DASHBOARD_DATA_FLOWS.md)
3. Register routes
4. Implement services
5. Write tests

### 4. QA Engineers
1. Read [TELEMETRY_DASHBOARD_GUIDE.md](./TELEMETRY_DASHBOARD_GUIDE.md)
2. Review user flows in [WIREFRAMING_BRIEF.md](./WIREFRAMING_BRIEF.md)
3. Create test data
4. Write test plans
5. Execute tests

---

## 📞 Quick Links

| Need | Document |
|------|----------|
| **Wireframe data contracts** | [WIREFRAMING_BRIEF.md](./WIREFRAMING_BRIEF.md) |
| **Exact API payloads** | [DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md) |
| **Setup instructions** | [DASHBOARD_INTEGRATION.md](./DASHBOARD_INTEGRATION.md) |
| **Endpoint list** | [BACKEND_ENDPOINTS_CONFIRMED.md](./BACKEND_ENDPOINTS_CONFIRMED.md) |
| **Visual flows** | [DASHBOARD_DATA_FLOWS.md](./DASHBOARD_DATA_FLOWS.md) |
| **Technical guide** | [TELEMETRY_DASHBOARD_GUIDE.md](./TELEMETRY_DASHBOARD_GUIDE.md) |
| **Unified spec** | [DASHBOARD_COMPLETE_SPEC.md](./DASHBOARD_COMPLETE_SPEC.md) |
| **Quick reference** | [WIREFRAME_QUICK_REFERENCE.md](./WIREFRAME_QUICK_REFERENCE.md) |

---

## 📈 Project Status

| Component | Status |
|-----------|--------|
| **Backend API** | ✅ Fully specified |
| **WebSocket** | ✅ Fully specified |
| **Frontend Components** | ✅ Templates ready |
| **Data Contracts** | ✅ Complete |
| **User Flows** | ✅ All documented |
| **Documentation** | ✅ Comprehensive |
| **Wireframing** | 🎨 Ready to start |
| **Implementation** | ⏳ Pending wireframes |

---

## 🎯 Success Criteria

- [x] All endpoints specified (26 REST + 1 WS)
- [x] All data contracts defined
- [x] All user flows documented
- [x] All UI states specified
- [x] Complete documentation suite
- [ ] Wireframes created
- [ ] Components implemented
- [ ] Tests written
- [ ] Deployed to production

---

**📚 GRACE Dashboard System - Complete Documentation Suite**

**You are ready to wireframe, design, and implement!** 🚀
