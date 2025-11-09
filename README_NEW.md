# 🤖 Grace AI System

**Intelligent AI system with 9 domain kernels managing 311+ APIs**

---

## ⚡ Quick Start

```powershell
.\RUN_GRACE.ps1
```

See [QUICK_START.md](QUICK_START.md) for details.

---

## 🎯 What is Grace?

Grace is an advanced AI system with:
- **9 Intelligent Domain Kernels** - AI agents that understand intent
- **311+ API Endpoints** - Complete functionality
- **100+ Autonomous Subsystems** - Self-healing, learning, coding
- **Full Transparency** - Execution traces, data provenance
- **Natural Language Interface** - Ask for what you want

### The Revolutionary Architecture

**Before:** 311 individual APIs  
**After:** 9 intelligent AI agents

Each kernel:
- Parses natural language intent
- Orchestrates multiple APIs automatically
- Aggregates results intelligently
- Returns with full transparency

---

## 🧠 The 9 Domain Kernels

| Kernel | Manages | Endpoints | Purpose |
|--------|---------|-----------|---------|
| **Memory** | 25 APIs | `/kernel/memory` | Knowledge & storage |
| **Core** | 47 APIs | `/kernel/core` | System & interaction |
| **Code** | 38 APIs | `/kernel/code` | Code gen & execution |
| **Governance** | 50 APIs | `/kernel/governance` | Policy & safety |
| **Verification** | 35 APIs | `/kernel/verification` | Contracts & benchmarks |
| **Intelligence** | 60 APIs | `/kernel/intelligence` | ML & reasoning |
| **Infrastructure** | 38 APIs | `/kernel/infrastructure` | Monitoring & healing |
| **Federation** | 18 APIs | `/kernel/federation` | External integrations |
| **Base** | Foundation | N/A | Kernel framework |

**Total:** 311 APIs managed by 9 AI agents

See [README_KERNELS.md](README_KERNELS.md) for kernel documentation.

---

## 📦 What's Included

### Core Services
- ✅ FastAPI Backend (http://localhost:8000)
- ✅ Vite Frontend (http://localhost:5173)
- ✅ Interactive API Docs (http://localhost:8000/docs)

### Autonomous Systems
- ✅ Self-Healing (9 subsystems)
- ✅ Coding Agent (6 capabilities)
- ✅ Agentic Layer (orchestration)
- ✅ Web Learning (83+ domains, GitHub, YouTube, Reddit)
- ✅ Constitutional AI & Governance
- ✅ Parliament System (multi-agent)
- ✅ Temporal Reasoning & Causal Graphs
- ✅ ML/DL Learning Systems
- ✅ Complete Monitoring & Logging

---

## 🚀 Usage

### Start Grace
```powershell
.\RUN_GRACE.ps1
```

### Use a Kernel
```bash
curl -X POST http://localhost:8000/kernel/memory \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Find documents about sales pipelines with high trust",
    "context": {"user_id": "123"}
  }'
```

### Check System Health
```bash
curl http://localhost:8000/health
```

### Explore APIs
Open http://localhost:8000/docs

---

## 📖 Documentation

### Getting Started
- [QUICK_START.md](QUICK_START.md) - Get running in 5 minutes
- [BOOT_README.md](BOOT_README.md) - Boot system details

### Architecture
- [README_KERNELS.md](README_KERNELS.md) - Kernel architecture & usage
- [KERNEL_ARCHITECTURE_COMPLETE.md](docs/KERNEL_ARCHITECTURE_COMPLETE.md) - Technical details
- [KERNEL_API_AUDIT_COMPLETE.md](KERNEL_API_AUDIT_COMPLETE.md) - Complete API mapping

### Implementation
- [KERNEL_IMPLEMENTATION_COMPLETE.md](KERNEL_IMPLEMENTATION_COMPLETE.md) - What was built

---

## 🎓 Examples

### Memory Kernel - Knowledge Retrieval
```javascript
POST /kernel/memory
{
  "intent": "Find all sales documents with high trust scores"
}

// Kernel automatically:
// 1. Searches memory tree
// 2. Queries knowledge base  
// 3. Checks trust scores
// 4. Ranks by relevance
// Returns: Unified response with provenance
```

### Code Kernel - Code Generation
```javascript
POST /kernel/code
{
  "intent": "Generate a Python email validator with tests"
}

// Kernel automatically:
// 1. Generates code
// 2. Creates tests
// 3. Runs in sandbox
// 4. Validates
// Returns: Working code + test results
```

### Intelligence Kernel - Predictions
```javascript
POST /kernel/intelligence
{
  "intent": "Predict Q4 sales and explain drivers"
}

// Kernel automatically:
// 1. Loads/trains ML model
// 2. Runs temporal simulation
// 3. Builds causal graph
// 4. Generates explanation
// Returns: Prediction + reasoning
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     GRACE SYSTEM                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐              ┌────────────┐            │
│  │  Frontend   │◄─────────────┤  Backend   │            │
│  │  (Vite UI)  │              │  (FastAPI) │            │
│  └─────────────┘              └──────┬─────┘            │
│                                      │                   │
│                   ┌──────────────────┴────────────┐     │
│                   │                                │     │
│        ┌──────────▼──────────┐      ┌────────────▼───┐ │
│        │  9 Domain Kernels   │      │  Subsystems    │ │
│        │  (311+ APIs)        │      │  (Autonomous)  │ │
│        │                     │      │                │ │
│        │ • Memory (25)       │      │ • Self-Heal    │ │
│        │ • Core (47)         │      │ • Coding Agent │ │
│        │ • Code (38)         │      │ • Web Learning │ │
│        │ • Governance (50)   │      │ • Cognition    │ │
│        │ • Verification (35) │      │ • Parliament   │ │
│        │ • Intelligence (60) │      │ • Temporal     │ │
│        │ • Infrastructure(38)│      │ • Causal       │ │
│        │ • Federation (18)   │      │ • Monitoring   │ │
│        │ • Base (Foundation) │      │ • ...100+ more │ │
│        └─────────────────────┘      └────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 Development

### Run Tests
```powershell
.\TEST_E2E_BOOT.ps1
```

### Boot Options
```powershell
# Backend only
.\RUN_GRACE.ps1 -SkipFrontend

# Quick start (skip installs)
.\RUN_GRACE.ps1 -QuickStart

# Skip tests
.\RUN_GRACE.ps1 -SkipTest
```

### Monitor Logs
```powershell
.\watch_all_logs.ps1
.\watch_healing.ps1
```

---

## 🎯 Key Features

### Intelligence
- ✅ Natural language intent parsing (LLM-powered)
- ✅ Automatic API orchestration
- ✅ Intelligent result aggregation
- ✅ Learning from usage patterns

### Transparency
- ✅ Full execution traces
- ✅ Data provenance tracking
- ✅ Trust scores
- ✅ Confidence levels

### Autonomy
- ✅ Self-healing (detects & fixes issues)
- ✅ Code generation & execution
- ✅ Proactive improvement hunting
- ✅ Performance optimization
- ✅ Goal setting & achievement

### Safety
- ✅ Constitutional AI principles
- ✅ Governance policies
- ✅ Parliamentary oversight
- ✅ Verification contracts
- ✅ Snapshot & rollback

---

## 📊 Stats

- **311+ API Endpoints**
- **9 Domain Kernels**
- **100+ Subsystems**
- **54+ Route Files**
- **9 AI Agents**
- **Full E2E Test Coverage**

---

## 🆘 Support

### Common Issues

**Tests fail?**
```powershell
.\TEST_E2E_BOOT.ps1 -Verbose
```

**Backend won't start?**
```powershell
python test_kernels_quick.py
Get-Content logs\backend.log -Tail 50
```

**Port conflicts?**
```powershell
netstat -ano | findstr :8000
.\BOOT_GRACE_COMPLETE_E2E.ps1 -BackendPort 9000
```

### Documentation
- See [BOOT_README.md](BOOT_README.md) for troubleshooting
- See [QUICK_START.md](QUICK_START.md) for setup help

---

## 📝 License

[Your License Here]

---

## 🎉 Get Started

```powershell
.\RUN_GRACE.ps1
```

**That's all you need!** 🚀
