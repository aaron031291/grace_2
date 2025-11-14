# GRACE Dashboard System - Complete Specification

## 📋 Executive Summary

The GRACE Dashboard System is a comprehensive multi-layer observability and control platform that provides real-time telemetry, interactive controls, and AI-driven insights across all system components.

**Status**: ✅ Fully Specified - Ready for Implementation

---

## 🎯 System Overview

### Four Dashboard Layers

1. **Layer 1: Operations Console** 🎛️
   - Real-time kernel monitoring and control
   - Cryptographic health tracking
   - Ingestion throughput metrics
   - Live log viewing

2. **Layer 2: HTM Console** 📊
   - Task queue management with filters
   - Timing and size analytics
   - Workload perception and SLA tracking
   - Priority override controls

3. **Layer 3: Intent & Learning** 🧠
   - Active intent tracking with progress
   - Learning retrospectives and insights
   - Playbook success analytics
   - AI policy suggestions with approval workflow

4. **Layer 4: Dev/OS View** ⚙️
   - Secrets vault with consent workflow
   - Recording ingestion management
   - Remote access session logs
   - Deployment status and stress testing

---

## 📂 Complete File Manifest

### Backend Implementation

```
backend/routes/
├── telemetry_api.py          # REST API endpoints for all layers
│   ├── Layer 1: /api/telemetry/kernels/*
│   ├── Layer 1: /api/telemetry/crypto/*
│   ├── Layer 1: /api/telemetry/ingestion/*
│   ├── Layer 2: /api/telemetry/htm/*
│   ├── Layer 3: /api/telemetry/intent/*
│   ├── Layer 3: /api/telemetry/learning/*
│   ├── Layer 4: /api/telemetry/secrets/*
│   ├── Layer 4: /api/telemetry/recordings/*
│   ├── Layer 4: /api/telemetry/remote_access/*
│   └── Layer 4: /api/telemetry/deployment/*
│
└── telemetry_ws.py            # WebSocket streaming (real-time updates)
    ├── /ws/telemetry endpoint
    ├── 2-second broadcast interval
    └── Heartbeat ping/pong support
```

### Frontend Implementation

```
frontend/src/pages/
├── Layer1OpsConsole.tsx       # Ops Console component
├── Layer1OpsConsole.css       # Ops Console styles
├── Layer2HTMConsole.tsx       # HTM Console component
├── Layer2HTMConsole.css       # HTM Console styles
├── Layer3IntentLearning.tsx   # Learning Console component
├── Layer3IntentLearning.css   # Learning Console styles
├── Layer4DevOSView.tsx        # Dev/OS View component
├── Layer4DevOSView.css        # Dev/OS View styles
├── UnifiedDashboard.tsx       # Main dashboard router
└── UnifiedDashboard.css       # Navigation styles
```

### Documentation

```
docs/
├── TELEMETRY_DASHBOARD_GUIDE.md    # Comprehensive technical guide
│   ├── Architecture overview
│   ├── API endpoint documentation
│   ├── Installation & setup
│   ├── Usage guide
│   ├── Troubleshooting
│   └── Production considerations
│
├── DASHBOARD_INTEGRATION.md        # Quick start integration
│   ├── Backend route registration
│   ├── Model requirements
│   ├── Frontend integration
│   ├── Testing procedures
│   └── Troubleshooting
│
├── DASHBOARD_API_CONTRACT.md       # Complete API specification
│   ├── All endpoint payloads (request/response)
│   ├── Field definitions and types
│   ├── User interaction flows
│   ├── Backend processing logic
│   └── Error response formats
│
├── DASHBOARD_DATA_FLOWS.md         # Visual flows & state machines
│   ├── Data flow diagrams (ASCII art)
│   ├── Interaction state machines
│   ├── Error handling map
│   └── Component relationships
│
└── DASHBOARD_COMPLETE_SPEC.md      # This document (summary)
```

---

## 🔌 API Endpoint Summary

### Layer 1: Operations (9 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/telemetry/kernels/status` | Kernel metrics |
| GET | `/api/telemetry/crypto/health` | Crypto health |
| GET | `/api/telemetry/ingestion/throughput` | Ingestion stats |
| POST | `/api/telemetry/kernels/{id}/control` | Control kernel |
| GET | `/api/telemetry/kernels/{id}/logs` | View logs |

### Layer 2: HTM Console (3 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/telemetry/htm/queue` | Queue metrics |
| GET | `/api/telemetry/htm/tasks` | Task list (filterable) |
| GET | `/api/telemetry/htm/workload` | Workload stats |
| POST | `/api/telemetry/htm/tasks/{id}/priority` | Override priority |

### Layer 3: Learning (5 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/telemetry/intent/active` | Active intents |
| GET | `/api/telemetry/intent/{id}/details` | Intent details |
| GET | `/api/telemetry/learning/retrospectives` | Learning cycles |
| GET | `/api/telemetry/learning/playbooks` | Playbook success |
| GET | `/api/telemetry/learning/policy_suggestions` | Policy AI |
| POST | `/api/telemetry/learning/policy_suggestions/{id}/respond` | Accept/reject policy |

### Layer 4: Dev/OS (8 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/telemetry/secrets/status` | Vault health |
| POST | `/api/secrets/store` | Store secret |
| GET | `/api/telemetry/recordings/pending` | Pending recordings |
| POST | `/api/recording/ingest/{id}` | Start ingestion |
| GET | `/api/recording/ingest/{job_id}/status` | Poll ingestion |
| GET | `/api/telemetry/remote_access/sessions` | Session logs |
| GET | `/api/telemetry/deployment/status` | Deployment info |
| POST | `/api/stress/run` | Run stress test |
| GET | `/api/stress/{id}/status` | Poll stress test |

### WebSocket (1 endpoint)

| Protocol | Endpoint | Purpose |
|----------|----------|---------|
| WS | `/ws/telemetry` | Real-time updates (2s interval) |

**Total: 26 API endpoints + 1 WebSocket**

---

## 🎨 User Interaction Flows

### 1. Control Kernel (Layer 1)
```
User clicks "Restart" → Confirmation (optional) → API call → Success toast → Status update
```

### 2. Store Secret (Layer 4)
```
Click "+ Add Secret" → Fill form → Click "Save" → Consent modal → 
Confirm consent → API call → Success toast → Vault refresh
```

### 3. Ingest Recording (Layer 4)
```
Click "Ingest" → Confirm → API call → Show "Processing" badge → 
Poll status every 5s → Update progress → Complete toast
```

### 4. Respond to Policy (Layer 3)
```
Click [Accept/Review/Reject] → Confirmation modal → Enter notes → 
Submit → API call → Remove card → Show next steps
```

### 5. Run Stress Test (Layer 4)
```
Click "Run Stress Test" → Config modal → Select params → Start → 
Progress modal → Poll metrics → Show results → Close
```

### 6. Override Task Priority (Layer 2)
```
Right-click task → "Change Priority" → Modal → Select priority → 
Enter reason → Submit → Update row → Queue re-sort
```

---

## 📊 Data Refresh Strategy

### Polling Intervals

| Component | Method | Interval | Rationale |
|-----------|--------|----------|-----------|
| Layer 1 & 2 | HTTP Poll | 5s | Frequent kernel/queue changes |
| Layer 3 & 4 | HTTP Poll | 10s | Slower-changing data |
| All Layers | WebSocket | 2s | Critical real-time metrics |
| Kernel Logs | HTTP Poll | 3s | Live log streaming |
| Job Status | HTTP Poll | 5s | Progress tracking |

### Auto-Refresh Controls

- Each dashboard has toggle: "Auto-refresh"
- When disabled: Manual refresh button only
- When enabled: Automatic polling at specified intervals
- WebSocket connection persists regardless (for live alerts)

---

## 🧩 Component Architecture

### Frontend Component Tree

```
<UnifiedDashboard>
  ├── <Navigation>
  │   ├── [Layer 1 Button]
  │   ├── [Layer 2 Button]
  │   ├── [Layer 3 Button]
  │   └── [Layer 4 Button]
  │
  └── <DashboardContent>
      ├── {activeLayer === 'layer1' && <Layer1OpsConsole />}
      ├── {activeLayer === 'layer2' && <Layer2HTMConsole />}
      ├── {activeLayer === 'layer3' && <Layer3IntentLearning />}
      └── {activeLayer === 'layer4' && <Layer4DevOSView />}

<Layer1OpsConsole>
  ├── <KernelMetricsGrid />
  ├── <KernelTable>
  │   └── <KernelRow> (actions: start/stop/restart/stress/logs)
  ├── <CryptoHealthGrid />
  ├── <IngestionThroughputGrid />
  └── {selectedKernel && <LogsModal />}

<Layer2HTMConsole>
  ├── <QueueMetricsGrid />
  ├── <WorkloadPerceptionGrid />
  ├── <OriginStatsGrid />
  ├── <SizeDistributionChart />
  ├── <TaskFilters>
  │   ├── <OriginSelect />
  │   └── <StatusSelect />
  └── <TaskTable>
      └── <TaskRow> (action: change priority)

<Layer3IntentLearning>
  ├── <ActiveIntentsGrid>
  │   └── <IntentCard> (click → details modal)
  ├── <PlaybookSuccessTable />
  ├── <RetrospectivesList>
  │   └── <RetrospectiveCard>
  └── <PolicySuggestionsList>
      └── <PolicyCard> (actions: accept/review/reject)

<Layer4DevOSView>
  ├── <SecretsVaultGrid /> (button: + Add Secret)
  ├── <DeploymentStatusGrid /> (button: Run Stress Test)
  ├── <RecordingsTable> (action: Ingest)
  ├── <RemoteSessionsTable />
  ├── {showSecretModal && <AddSecretModal />}
  ├── {showConsentModal && <ConsentModal />}
  └── {showStressModal && <StressTestModal />}
```

### Backend Service Dependencies

```
telemetry_api.py
├── depends on: KernelRegistry
├── depends on: HTMQueue
├── depends on: CryptoHealthMonitor
├── depends on: LearningLoop
├── depends on: Database models (Intent, PlaybookExecution, etc.)
└── depends on: get_session (SQLAlchemy)

telemetry_ws.py
├── depends on: KernelRegistry
├── depends on: HTMQueue
├── depends on: CryptoHealthMonitor
└── broadcasts to: All WebSocket clients
```

---

## 🔒 Security Considerations

### Secrets Management
- **Encryption**: AES-256 for all stored secrets
- **Consent**: Explicit user consent required before storage
- **Audit**: All secret operations logged (user, timestamp, action)
- **Access**: Never expose secret values in API responses
- **Display**: Show masked values only (e.g., `sk-***...***abc`)

### User Actions
- **Authentication**: Add auth middleware to all telemetry endpoints (production)
- **Authorization**: Role-based access for destructive actions (kernel control, priority override)
- **Audit Trail**: Log all user interactions (who, what, when)
- **Rate Limiting**: Prevent abuse of control endpoints

### API Security
- **CORS**: Configure allowed origins for production
- **Input Validation**: Validate all request parameters
- **SQL Injection**: Use parameterized queries (SQLAlchemy)
- **XSS Protection**: Sanitize user input in notes/reason fields

---

## 📈 Performance Optimization

### Backend
- **Caching**: Cache kernel/HTM metrics for 2-5s (Redis)
- **Database Indexes**: Index frequently queried fields (status, created_at, origin)
- **Connection Pooling**: Use SQLAlchemy pool for DB connections
- **Async Processing**: Use async/await for all I/O operations

### Frontend
- **Lazy Loading**: Load charts/tables only when visible
- **Virtualization**: Use virtual scrolling for large task tables
- **Memoization**: Memoize expensive calculations (React.useMemo)
- **Debouncing**: Debounce filter changes (300ms)

### WebSocket
- **Broadcast Optimization**: Only send changed data (delta updates)
- **Compression**: Enable WebSocket compression for large payloads
- **Reconnection**: Auto-reconnect with exponential backoff
- **Heartbeat**: Keep connection alive with ping/pong

---

## 🧪 Testing Strategy

### Backend Testing

```python
# Unit Tests
- test_kernel_status_endpoint()
- test_crypto_health_endpoint()
- test_htm_queue_endpoint()
- test_store_secret_with_consent()
- test_store_secret_without_consent()
- test_recording_ingestion_flow()
- test_stress_test_validation()

# Integration Tests
- test_kernel_control_flow()
- test_priority_override_flow()
- test_policy_response_flow()
- test_websocket_broadcast()

# Load Tests
- test_concurrent_api_requests()
- test_websocket_broadcast_to_many_clients()
```

### Frontend Testing

```typescript
// Component Tests
- render Layer1OpsConsole with mock data
- test kernel control button clicks
- test auto-refresh toggle
- test filter interactions (Layer 2)
- test secret form validation
- test modal open/close flows

// Integration Tests
- test dashboard layer switching
- test API call error handling
- test WebSocket reconnection
- test polling on component mount

// E2E Tests
- test full kernel control flow
- test full secret storage flow
- test full recording ingestion flow
- test full stress test execution
```

### Stress Testing with Dashboard

1. Run stress test from Layer 4
2. Monitor Layer 1 for kernel stress scores
3. Monitor Layer 2 for HTM queue depth increase
4. Verify Layer 3 shows new intents/retrospectives
5. Check WebSocket broadcasts update all layers

---

## 📦 Deployment Checklist

### Pre-Deployment

- [ ] All backend routes registered in FastAPI app
- [ ] WebSocket broadcaster starts on app startup
- [ ] Database models created/migrated
- [ ] Environment variables configured (API_BASE, DB_URL)
- [ ] CORS settings configured for production domain
- [ ] Authentication middleware added to endpoints
- [ ] Rate limiting configured
- [ ] Logging and error tracking configured

### Frontend Build

- [ ] Update API_BASE to production URL
- [ ] Build frontend: `npm run build`
- [ ] Test production build locally
- [ ] Configure SSL/TLS for WebSocket (wss://)
- [ ] Set up CDN for static assets
- [ ] Enable gzip compression

### Post-Deployment

- [ ] Verify all 26 API endpoints respond
- [ ] Test WebSocket connection
- [ ] Run smoke tests for each layer
- [ ] Monitor error rates and performance
- [ ] Set up dashboard analytics
- [ ] Configure alerts for critical metrics

---

## 🎯 Success Metrics

### Technical Metrics
- **API Response Time**: < 200ms (p95)
- **WebSocket Latency**: < 100ms
- **Frontend Load Time**: < 2s
- **Error Rate**: < 0.1%
- **Uptime**: > 99.9%

### User Metrics
- **Dashboard Load Time**: < 3s
- **Interaction Response**: < 500ms
- **Auto-Refresh Reliability**: > 99%
- **User Actions Success Rate**: > 98%

### Business Metrics
- **System Visibility**: All kernels/tasks/intents monitored
- **Mean Time to Detection (MTTD)**: < 30s
- **Mean Time to Resolution (MTTR)**: < 5min
- **Operator Efficiency**: 50% reduction in manual checks

---

## 🚀 Next Steps

### For Design Team
1. Review [DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md) for exact data structures
2. Review [DASHBOARD_DATA_FLOWS.md](./DASHBOARD_DATA_FLOWS.md) for interaction flows
3. Create wireframes based on component specifications
4. Design UI states: idle, loading, success, error
5. Create style guide (colors, typography, spacing)

### For Frontend Team
1. Review [DASHBOARD_INTEGRATION.md](./DASHBOARD_INTEGRATION.md) for setup
2. Implement UnifiedDashboard router
3. Build Layer 1-4 components using provided templates
4. Integrate API calls with error handling
5. Add WebSocket connection for live updates
6. Write component tests

### For Backend Team
1. Review [TELEMETRY_DASHBOARD_GUIDE.md](./TELEMETRY_DASHBOARD_GUIDE.md) for architecture
2. Register telemetry routes in FastAPI app
3. Implement or stub required services (KernelRegistry, HTMQueue, etc.)
4. Create database models if missing
5. Set up WebSocket broadcaster
6. Write API tests

### For QA Team
1. Set up test environment
2. Create test data (kernels, tasks, intents, recordings)
3. Test all 26 API endpoints
4. Test WebSocket connection and broadcasts
5. Test all user interaction flows
6. Run stress test and verify dashboard updates

---

## 📚 Related Documentation

- [TELEMETRY_DASHBOARD_GUIDE.md](./TELEMETRY_DASHBOARD_GUIDE.md) - Comprehensive technical guide
- [DASHBOARD_INTEGRATION.md](./DASHBOARD_INTEGRATION.md) - Quick start integration
- [DASHBOARD_API_CONTRACT.md](./DASHBOARD_API_CONTRACT.md) - Complete API specification
- [DASHBOARD_DATA_FLOWS.md](./DASHBOARD_DATA_FLOWS.md) - Visual flows & state machines

---

## ✅ Specification Status

| Component | Status | Files | Documentation |
|-----------|--------|-------|---------------|
| Backend API | ✅ Complete | `telemetry_api.py` | API contract defined |
| WebSocket | ✅ Complete | `telemetry_ws.py` | Broadcast logic defined |
| Layer 1 Frontend | ✅ Complete | `Layer1OpsConsole.tsx/.css` | Component ready |
| Layer 2 Frontend | ✅ Complete | `Layer2HTMConsole.tsx/.css` | Component ready |
| Layer 3 Frontend | ✅ Complete | `Layer3IntentLearning.tsx/.css` | Component ready |
| Layer 4 Frontend | ✅ Complete | `Layer4DevOSView.tsx/.css` | Component ready |
| Unified Router | ✅ Complete | `UnifiedDashboard.tsx/.css` | Navigation ready |
| Documentation | ✅ Complete | 4 MD files | Fully documented |

---

**The GRACE Dashboard System is fully specified and ready for implementation.**

All data feeds are clearly defined, user interactions are mapped, backend flows are documented, and frontend components are templated. Designers have exact payload structures, developers have clear specifications, and QA has testable flows.

**You are now ready to move into wireframing, prototyping, and UI layout.**
