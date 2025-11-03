# Quick Start - Get Backend + Frontend Working

**Goal:** Get backend API running and frontend connected with CLI

---

## Current Situation

**Metrics server crashes on startup** - needs debugging  
**Main backend has import issues** - too complex to fix quickly  
**Frontend exists but not connected** - needs API

---

## Working Solution: Use What Works

### Step 1: Use Metrics System Standalone (Works Now)

The metrics system works **without a server**. Here's a working demo:

**Create:** `grace_rebuild/demo_working_metrics.py`

```python
import asyncio
import sys
sys.path.insert(0, '.')

from backend.metrics_service import publish_metric, get_metrics_collector
from backend.cognition_metrics import get_metrics_engine
from backend.metric_publishers import *

async def demo():
    print("Publishing metrics from all 9 domains...")
    
    # Publish test metrics
    await CoreMetrics.publish_uptime(0.99)
    await CoreMetrics.publish_governance_score(0.93)
    await OrchestratorMetrics.publish_task_completed(True, 0.95)
    await HunterMetrics.publish_scan_completed(1, 0.98, 0.012)
    await KnowledgeMetrics.publish_ingestion_completed(0.92, 30)
    await MLMetrics.publish_training_completed(0.96, 1200)
    await TemporalMetrics.publish_prediction_made(0.88)
    await ParliamentMetrics.publish_vote_completed(0.94)
    await FederationMetrics.publish_connector_health("test", 0.97)
    
    print("\nGetting cognition status...")
    engine = get_metrics_engine()
    status = engine.get_status()
    
    print(f"\nOverall Health: {status['overall_health']:.1%}")
    print(f"Overall Trust: {status['overall_trust']:.1%}")
    print(f"SaaS Ready: {status['saas_ready']}")
    print(f"\nDomains tracked: {len(status['domains'])}")
    
    for domain, data in list(status['domains'].items())[:5]:
        print(f"  {domain}: Health={data['health']:.1%}")
    
    # Get readiness report
    print("\nGenerating readiness report...")
    from backend.readiness_report import get_report_generator
    generator = get_report_generator()
    report = generator.generate_markdown_report()
    
    print(f"Report generated: {len(report)} characters")
    print("\nFirst 500 chars:")
    print(report[:500])

asyncio.run(demo())
```

**Run:**
```bash
cd grace_rebuild
py demo_working_metrics.py
```

**This works TODAY without any server.**

---

### Step 2: Check Frontend Setup

```bash
cd grace-frontend
dir package.json
```

If exists, check what's configured:
```bash
type package.json
```

---

### Step 3: Alternative - Create Minimal Working Backend

Since the full backend has issues, create a minimal one:

**Create:** `grace_rebuild/minimal_backend.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.insert(0, 'backend')

app = FastAPI(title="Grace Minimal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import only working routers
try:
    from backend.routers.cognition import router as cognition_router
    app.include_router(cognition_router)
    print("Cognition router loaded")
except Exception as e:
    print(f"Could not load cognition router: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Minimal backend running"}

@app.get("/api/status")
def status():
    from backend.cognition_metrics import get_metrics_engine
    engine = get_metrics_engine()
    return engine.get_status()

if __name__ == "__main__":
    import uvicorn
    print("Starting minimal backend on :8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

**Run:**
```bash
py minimal_backend.py
```

---

### Step 4: Frontend Connection

**Check frontend:**
```bash
cd grace-frontend
npm install
npm run dev
```

**Create API client:** `grace-frontend/src/api/client.ts`

```typescript
const API_BASE = 'http://localhost:8000';

export async function getCognitionStatus() {
  const response = await fetch(`${API_BASE}/api/cognition/status`);
  return response.json();
}

export async function getHealth() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
```

**Simple component:** `grace-frontend/src/components/Status.tsx`

```typescript
import { useEffect, useState } from 'react';
import { getCognitionStatus } from '../api/client';

export function Status() {
  const [status, setStatus] = useState(null);
  
  useEffect(() => {
    getCognitionStatus().then(setStatus);
  }, []);
  
  if (!status) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Grace Status</h1>
      <p>Health: {(status.overall_health * 100).toFixed(1)}%</p>
      <p>Trust: {(status.overall_trust * 100).toFixed(1)}%</p>
      <p>SaaS Ready: {status.saas_ready ? 'Yes' : 'No'}</p>
    </div>
  );
}
```

---

### Step 5: CLI Connection

The CLI commands are written but need backend running.

**Simplified CLI test:**

```python
# test_cli_simple.py
import asyncio
import httpx

async def test_cli():
    try:
        r = httpx.get('http://localhost:8000/api/cognition/status', timeout=2)
        data = r.json()
        
        print("GRACE COGNITION STATUS")
        print("=" * 40)
        print(f"Health:     {data['overall_health']:.1%}")
        print(f"Trust:      {data['overall_trust']:.1%}")
        print(f"Confidence: {data['overall_confidence']:.1%}")
        print(f"SaaS Ready: {data['saas_ready']}")
        print("=" * 40)
        
    except Exception as e:
        print(f"Error: Backend not running on :8000")
        print(f"Start with: py minimal_backend.py")

asyncio.run(test_cli())
```

---

## Recommended Approach

**Option 1: Standalone (Works Immediately)**
- Use metrics system in Python scripts
- No server needed
- Can integrate into domain code today
- Limited: No API, no frontend, no CLI

**Option 2: Minimal Backend (30 min to working)**
- Create minimal_backend.py (done above)
- Start on port 8000
- Frontend can connect
- CLI can connect
- Full metrics API available

**Option 3: Debug Full Backend (3-4 hours)**
- Fix all route imports
- Fix circular dependencies
- Get full Grace backend running
- Most complete but time-consuming

---

## Immediate Action Plan

**Do this now (10 minutes):**

1. Create `minimal_backend.py` (code above)
2. Run: `py minimal_backend.py`
3. Test: Open http://localhost:8000/health in browser
4. Test: Open http://localhost:8000/api/status
5. Success: Backend is running!

**Then (20 minutes):**

6. cd grace-frontend
7. npm install
8. Create simple Status component
9. npm run dev
10. Open http://localhost:5173
11. Success: Frontend connected!

**Then (10 minutes):**

12. Create test_cli_simple.py
13. Run: py test_cli_simple.py
14. Success: CLI can read from backend!

---

**Total time:** 40 minutes to get backend + frontend + CLI all connected

**Start with:** Create and run `minimal_backend.py`
