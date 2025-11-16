# Grace Kernel & API Port Architecture

## Overview

Every Grace kernel AND API gets its own dedicated port with full telemetry, metrics, and network healing capabilities. This provides complete isolation, individual monitoring, and Guardian-integrated auto-remediation.

## Port Allocation

### Main API
- **Port 8000** - Main Grace API (aggregate endpoint)

### Kernels (8100-8149)

#### Tier 1: Core Kernels (8100-8109)
- **8100** - Message Bus
- **8101** - Immutable Log

#### Tier 2: Governance Kernels (8110-8119)
- **8110** - Governance
- **8111** - Crypto Kernel
- **8112** - Trust Framework
- **8113** - Policy Engine
- **8114** - Compliance Monitor
- **8115** - Audit Trail

#### Tier 3: Execution Kernels (8120-8129)
- **8120** - Scheduler
- **8121** - Task Executor
- **8122** - Workflow Engine
- **8123** - State Machine

#### Tier 4: Agentic Kernels (8130-8139)
- **8130** - Librarian Kernel
- **8131** - Self Healing Kernel
- **8132** - Coding Agent Kernel
- **8133** - Learning Kernel
- **8134** - Research Kernel

#### Tier 5: Service Kernels (8140-8149)
- **8140** - Telemetry Service
- **8141** - Metrics Aggregator
- **8142** - Alert Service

### API Routes (8200-8299)

#### Core APIs (8200-8209)
- **8200** - Auth API
- **8201** - Health API
- **8202** - Operator Dashboard

#### Memory & Knowledge (8210-8219)
- **8210** - Memory API
- **8211** - Memory Tables API
- **8212** - Memory Workspace API
- **8213** - Knowledge API
- **8214** - Librarian API

#### AI & ML (8220-8229)
- **8220** - Chat API
- **8221** - Autonomous Agent API
- **8222** - ML Dashboard API
- **8223** - Coding Agent API
- **8224** - Agentic API

#### Governance & Security (8230-8239)
- **8230** - Governance API
- **8231** - Trust Framework API
- **8232** - Guardian API
- **8233** - Self Healing API
- **8234** - Immutable API

#### Execution & Control (8240-8249)
- **8240** - Execution API
- **8241** - Mission Control API
- **8242** - Kernels API
- **8243** - Port Manager API

#### Monitoring & Telemetry (8250-8259)
- **8250** - Telemetry API
- **8251** - Metrics API
- **8252** - Observability API
- **8253** - Learning Visibility API
- **8254** - Alerts API

#### Integration & External (8260-8269)
- **8260** - Remote Access API
- **8261** - Integration API
- **8262** - External API
- **8263** - Speech API

#### Specialized Services (8270-8279)
- **8270** - Ingestion API
- **8271** - Vector API
- **8272** - Multimodal API
- **8273** - Temporal API
- **8274** - Causal API

#### Development & Debug (8280-8289)
- **8280** - Sandbox API
- **8281** - Test Endpoint
- **8282** - Meta API

## Benefits

### 1. Complete Isolation
- Each component runs independently
- One crash doesn't affect others
- Clear service boundaries

### 2. Individual Monitoring
- Dedicated health endpoint per component: `http://localhost:{port}/health`
- Dedicated metrics endpoint per component: `http://localhost:{port}/metrics`
- Per-component telemetry and logging

### 3. Network Healing
- Port watchdog monitors all components
- Guardian auto-remediation for failures
- Automatic restart and recovery

### 4. Easier Debugging
- Know exactly which component is failing
- Isolated logs per component
- Clear failure attribution

### 5. Scalability
- Easy to scale individual components
- Load balance specific high-traffic APIs
- Deploy components independently

## API Endpoints

Access the Kernel & API Port Manager at:

### Main Endpoints
- `GET /kernel-ports/assignments` - List all port assignments
- `GET /kernel-ports/port-map` - Get complete port mapping
- `GET /kernel-ports/port/{name}` - Get port for specific component
- `GET /kernel-ports/health-check` - Health check all components
- `GET /kernel-ports/metrics` - Get metrics summary
- `GET /kernel-ports/status` - Overall system status

### Management
- `POST /kernel-ports/reset-failures/{name}` - Reset failure count
- `GET /kernel-ports/by-tier/{tier}` - Get components by tier

### Query Parameters
- `?tier=core|governance|execution|agentic|services|api` - Filter by tier
- `?include_apis=true|false` - Include/exclude API assignments

## Usage Examples

### Get all kernel assignments
```bash
curl http://localhost:8000/kernel-ports/assignments?include_apis=false
```

### Get all API assignments
```bash
curl http://localhost:8000/kernel-ports/by-tier/api
```

### Check health of all components
```bash
curl http://localhost:8000/kernel-ports/health-check
```

### Get port for specific component
```bash
curl http://localhost:8000/kernel-ports/port/librarian_kernel
curl http://localhost:8000/kernel-ports/port/chat_api
```

### Get overall system status
```bash
curl http://localhost:8000/kernel-ports/status
```

## Integration with Guardian

The kernel port manager integrates with Grace's Guardian system:

1. **Port Watchdog** - Monitors all component health endpoints
2. **Auto-Remediation** - Guardian automatically restarts failed components
3. **Failure Tracking** - Records failure counts and patterns
4. **Network Healing** - Full Layer 2-7 network diagnosis and repair

## Integration with Port Manager

The existing port manager now tracks:
- Kernel ports (8100-8149)
- API ports (8200-8299)
- Health status per component
- Failure counts and remediation

## Next Steps

To hardwire kernels and APIs to their dedicated ports:

1. **Modify each kernel** to start on its assigned port
2. **Update API routes** to register on dedicated ports
3. **Configure Guardian** to monitor all ports
4. **Enable auto-restart** for failed components
5. **Set up metrics collection** per port

## Architecture Diagram

```
Main API (8000)
    ├─ Aggregates all APIs
    └─ Routes to dedicated ports

Kernels (8100-8149)
    ├─ Core (8100-8109)
    ├─ Governance (8110-8119)
    ├─ Execution (8120-8129)
    ├─ Agentic (8130-8139)
    └─ Services (8140-8149)

APIs (8200-8299)
    ├─ Core APIs (8200-8209)
    ├─ Memory/Knowledge (8210-8219)
    ├─ AI/ML (8220-8229)
    ├─ Governance/Security (8230-8239)
    ├─ Execution/Control (8240-8249)
    ├─ Monitoring/Telemetry (8250-8259)
    ├─ Integration/External (8260-8269)
    ├─ Specialized Services (8270-8279)
    └─ Development/Debug (8280-8289)

Guardian Watchdog
    └─ Monitors all 8100-8299
```

## Health Check Integration

Each component exposes:
```
http://localhost:{port}/health   → {"status": "ok"}
http://localhost:{port}/metrics  → {detailed metrics}
```

Guardian monitors these endpoints and triggers auto-remediation on failures.
