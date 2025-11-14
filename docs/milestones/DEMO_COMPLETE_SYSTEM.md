# Complete System Demo Guide

**The Ultimate Grace Showcase**: Ingestion → Self-Healing → Model Registry → Memory Studio

This demo showcases Grace's **full autonomous AI operating system** with all kernels working together.

---

## 🎯 Demo Flow Overview

```
1. Book Ingestion (with rate limit hit)
   ↓
2. Self-Healing Auto-Recovery
   ↓
3. Librarian Knowledge Capture
   ↓
4. Model Registry Monitoring
   ↓
5. Memory Studio Visualization
   ↓
6. Co-pilot Natural Language Control
```

---

## 📚 Part 1: Book Ingestion with Self-Healing

### Step 1: Prepare a Real Book

Download a public domain book from Project Gutenberg:

```bash
# Download a real book
curl https://www.gutenberg.org/cache/epub/1342/pg1342.txt -o "pride_and_prejudice.txt"

# Or use this smaller one for faster demo
curl https://www.gutenberg.org/cache/epub/84/pg84.txt -o "frankenstein.txt"
```

Or create a sample book:

```bash
# Create sample book in txt/
mkdir -p txt
cat > txt/grace_ai_principles.txt << 'EOF'
# Grace AI Principles
By Grace Team

## Chapter 1: Autonomous Intelligence

Grace is an AI operating system that manages itself...

## Chapter 2: Self-Healing Architecture

When things go wrong, Grace heals itself automatically...

## Chapter 3: Memory & Knowledge

Everything Grace learns is stored in a unified memory system...

[Continue with 5000+ words for realistic chunking...]
EOF
```

### Step 2: Start the System

```bash
# Terminal 1: Start backend
python serve.py

# Terminal 2: Start frontend (if needed)
cd frontend
npm run dev
```

### Step 3: Upload the Book

**Option A: Via UI** (http://localhost:3000)
1. Navigate to Book Ingestion panel
2. Click "Upload Book"
3. Select `txt/grace_ai_principles.txt`
4. Watch the real-time progress

**Option B: Via API**

```bash
# Upload book
curl -X POST http://localhost:8000/api/books/upload \
  -F "file=@txt/grace_ai_principles.txt" \
  -F "title=Grace AI Principles" \
  -F "author=Grace Team"

# Check ingestion status
curl http://localhost:8000/api/books/status/{book_id}
```

### Step 4: Watch Self-Healing in Action

The ingestion will hit rate limits. Watch the logs:

```bash
tail -f logs/backend.log
```

You'll see:
1. ⚠️ Rate limit detected (429 error)
2. 🔧 Self-healing triggered
3. ⏸️ Exponential backoff started
4. 📝 Incident created
5. ✅ Retry successful
6. 📊 Trust metrics updated

### Step 5: Monitor via APIs

```bash
# Check self-healing stats
curl http://localhost:8000/api/self-healing/stats

# Check incidents
curl http://localhost:8000/api/incidents?status=open

# Check librarian flashcards
curl http://localhost:8000/api/librarian/flashcards
```

**Expected Output:**
```json
{
  "total_incidents": 2,
  "auto_resolved": 1,
  "manual_intervention": 0,
  "playbooks_executed": ["api_backoff", "retry_with_backoff"],
  "mean_resolution_time_seconds": 8.5
}
```

---

## 🤖 Part 2: Model Registry Population & Rollback

### Step 1: Register Active Models

Create a script to populate with realistic models:

```bash
python scripts/populate_model_registry.py
```

**Script contents** (`scripts/populate_model_registry.py`):

```python
import requests
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

models = [
    {
        "model_id": "fraud_detector_v1",
        "name": "Fraud Detection Model",
        "version": "1.2.3",
        "framework": "sklearn",
        "model_type": "classification",
        "owner": "data_science",
        "team": "ml_platform",
        "training_data_hash": "abc123def456",
        "training_dataset_size": 500000,
        "evaluation_metrics": {
            "accuracy": 0.94,
            "precision": 0.92,
            "recall": 0.91,
            "f1_score": 0.915,
            "auc_roc": 0.96
        },
        "description": "Production fraud detection model using ensemble methods",
        "tags": ["fraud", "production", "ensemble"]
    },
    {
        "model_id": "sentiment_analyzer_v2",
        "name": "Sentiment Analysis",
        "version": "2.0.1",
        "framework": "pytorch",
        "model_type": "classification",
        "owner": "nlp_team",
        "team": "ai_research",
        "training_data_hash": "xyz789abc012",
        "training_dataset_size": 1000000,
        "evaluation_metrics": {
            "accuracy": 0.89,
            "precision": 0.87,
            "recall": 0.88,
            "f1_score": 0.875
        },
        "description": "BERT-based sentiment classifier for customer reviews",
        "tags": ["nlp", "sentiment", "bert", "production"]
    },
    {
        "model_id": "churn_predictor_v3",
        "name": "Customer Churn Prediction",
        "version": "3.1.0",
        "framework": "sklearn",
        "model_type": "classification",
        "owner": "analytics",
        "team": "data_science",
        "training_data_hash": "churn456xyz",
        "training_dataset_size": 250000,
        "evaluation_metrics": {
            "accuracy": 0.86,
            "precision": 0.84,
            "recall": 0.85,
            "f1_score": 0.845
        },
        "description": "Random forest model for customer churn prediction",
        "tags": ["churn", "customer", "production"]
    }
]

# Register models
for model in models:
    response = requests.post(f"{BASE_URL}/api/model-registry/models", json=model)
    print(f"✅ Registered: {model['name']} - {response.json()}")

# Promote to production
for model in models:
    requests.patch(
        f"{BASE_URL}/api/model-registry/models/{model['model_id']}/deployment",
        json={"status": "production", "canary_percentage": 0.0}
    )
    print(f"🚀 Promoted to production: {model['model_id']}")

print("\n✅ Model registry populated!")
```

### Step 2: Simulate Model Performance

Record healthy performance:

```bash
curl -X POST http://localhost:8000/api/model-registry/models/fraud_detector_v1/performance \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "fraud_detector_v1",
    "version": "1.2.3",
    "latency_p50_ms": 42.5,
    "latency_p95_ms": 85.3,
    "latency_p99_ms": 120.7,
    "requests_per_second": 250.0,
    "error_rate": 0.002,
    "ood_rate": 0.04,
    "input_drift_score": 0.08,
    "accuracy": 0.94
  }'
```

### Step 3: Simulate Degradation & Watch Rollback

Inject degraded performance:

```bash
# Record 5 bad snapshots to trigger rollback
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/model-registry/models/fraud_detector_v1/performance \
    -H "Content-Type: application/json" \
    -d '{
      "model_id": "fraud_detector_v1",
      "version": "1.2.3",
      "latency_p50_ms": 55.0,
      "latency_p95_ms": 150.0,
      "latency_p99_ms": 280.0,
      "requests_per_second": 120.0,
      "error_rate": 0.09,
      "ood_rate": 0.25,
      "input_drift_score": 0.38,
      "accuracy": 0.82
    }'
  sleep 1
done
```

### Step 4: Check Rollback Triggers

```bash
# Check if rollback needed
curl "http://localhost:8000/api/model-registry/models/fraud_detector_v1/rollback-check?auto_remediate=true"
```

**Expected Response:**
```json
{
  "model_id": "fraud_detector_v1",
  "should_rollback": true,
  "reasons": [
    "High error rate: 9.00%",
    "High OOD rate: 25.00%",
    "Input distribution drift: 0.380"
  ],
  "auto_remediate": true
}
```

### Step 5: Monitor Production Fleet

```bash
curl http://localhost:8000/api/model-registry/monitor/production
```

**Expected Response:**
```json
{
  "total_models": 3,
  "healthy": 2,
  "degraded": 0,
  "failing": 1,
  "issues": [
    {
      "model_id": "fraud_detector_v1",
      "version": "1.2.3",
      "reasons": [
        "High error rate: 9.00%",
        "High OOD rate: 25.00%"
      ]
    }
  ]
}
```

---

## 🧠 Part 3: Memory Studio & Librarian Verification

### Step 1: Check Librarian Flashcards

```bash
curl http://localhost:8000/api/librarian/flashcards | jq
```

**Expected Output:**
```json
{
  "flashcards": [
    {
      "id": "fc_001",
      "front": "What happened during book ingestion at 2025-11-13 14:30?",
      "back": "Hit rate limit (429), self-healing triggered api_backoff playbook, recovered in 8s",
      "category": "operational_knowledge",
      "created_at": "2025-11-13T14:30:15Z"
    },
    {
      "id": "fc_002",
      "front": "Which model triggered rollback on 2025-11-13?",
      "back": "fraud_detector_v1 - High error rate (9%), OOD rate (25%), drift (0.38)",
      "category": "ml_ops",
      "created_at": "2025-11-13T15:15:22Z"
    }
  ]
}
```

### Step 2: Query Memory Workspace

```bash
# Search memories
curl -X POST http://localhost:8000/api/librarian/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did we learn about rate limits?",
    "top_k": 5
  }'
```

### Step 3: Check Trust Metrics

```bash
curl http://localhost:8000/api/librarian/trust-metrics
```

**Expected Output:**
```json
{
  "api_connectors": {
    "openai": {
      "trust_score": 0.92,
      "success_rate": 0.94,
      "avg_latency_ms": 850,
      "last_failure": "2025-11-13T14:30:05Z - Rate limit"
    }
  },
  "self_healing_playbooks": {
    "api_backoff": {
      "trust_score": 0.95,
      "success_rate": 1.0,
      "executions": 12
    }
  }
}
```

---

## 🎨 Part 4: UI Demo Flow

### Launch the UI

```bash
# Open browser to http://localhost:3000
```

### Demo Sequence (show these panels):

**1. Operations Dashboard** (Main view)
- ✅ System health: All green
- 📊 Active incidents: 1 (model rollback)
- 📈 Ingestion progress: 87% complete
- 🤖 Models: 2 healthy, 1 degraded

**2. Book Ingestion Panel**
- Upload interface
- Real-time progress with chunks
- Rate limit recovery visualization
- Trust score updates

**3. Incident Timeline**
- Filter: Show "Resolved < 1h"
- View incident detail:
  - Plain-English summary
  - What was done (playbook executed)
  - Who approved (auto-approved)
  - Resolution time

**4. Memory Studio**
- Flashcard view (knowledge retention)
- Memory graph (connections)
- Search interface
- Trust metrics dashboard

**5. Model Registry Dashboard**
- Table of models with health badges
- Click on `fraud_detector_v1`:
  - Health: Critical (red)
  - Error rate chart
  - OOD detection chart
  - Rollback button

**6. Co-pilot Chat**

Demo conversation:
```
User: "Grace, show me open incidents"
Grace: "You have 1 open incident: fraud_detector_v1 triggered rollback 
        due to high error rate (9%) and drift. I've already marked it 
        for rollback. Should I execute?"

User: "Approve rollback"
Grace: "✅ Rollback executed. Model status changed to ROLLBACK. 
        Previous stable version deployed. Monitoring for improvement."

User: "Explain what happened with the book upload"
Grace: "Today at 14:30, while ingesting 'Grace AI Principles', I hit 
        OpenAI's rate limit. I automatically triggered the api_backoff 
        playbook, waited 8 seconds, and successfully resumed. The book 
        is now 87% ingested with 450 chunks processed."

User: "What's the trust score for OpenAI?"
Grace: "OpenAI API trust score: 92% (excellent). Success rate: 94%, 
        Average latency: 850ms. Last failure was the rate limit at 14:30, 
        which I handled automatically."
```

---

## 🔄 Part 5: Complete Integration Flow

### Watch the Full Loop

1. **Upload book** → Triggers ingestion
2. **Rate limit hit** → Self-healing activates
3. **Playbook executes** → Incident created
4. **Librarian captures** → Flashcard generated
5. **Trust updated** → Memory graph updated
6. **Co-pilot narrates** → Plain-English summary

### Verify Every Integration Point

```bash
# Run verification script
python scripts/verify_full_integration.py
```

**Script checks:**
- ✅ Backend health
- ✅ Event bus working
- ✅ Self-healing responding
- ✅ Incident registry active
- ✅ Model registry integrated
- ✅ Librarian capturing events
- ✅ Memory Studio accessible
- ✅ Co-pilot API responding

---

## 📊 Demo Metrics to Showcase

**Autonomy Metrics:**
- 🤖 **Auto-remediation rate**: 95%
- ⚡ **Mean time to recovery**: 8.5 seconds
- 🎯 **Success rate**: 94%
- 📈 **Knowledge retention**: 450 flashcards
- 🔄 **Trust scores**: 0.92 average

**Scale Metrics:**
- 📚 **Books ingested**: 12
- 📄 **Chunks processed**: 5,420
- 🧠 **Embeddings created**: 5,420
- 🤖 **Models monitored**: 3
- 📊 **Performance snapshots**: 127

**Governance Metrics:**
- 📝 **Incidents logged**: 28
- ✅ **Auto-resolved**: 26
- ⚠️ **Requires review**: 2
- 🔒 **Compliance checks**: 100%

---

## 🎬 Demo Script (5-Minute Pitch)

### Minute 1: The Problem
"AI systems break. Rate limits, API failures, model drift. Traditionally, someone gets paged at 3 AM. Not with Grace."

### Minute 2: Book Ingestion + Self-Healing
"Watch: I upload a book. OpenAI rate limit hits. Grace detects it, triggers a playbook, backs off, retries. **No human involved.** The incident is logged, knowledge is captured."

### Minute 3: Model Operations
"Grace monitors production models. Error rate spikes to 9%. Grace detects it, creates an incident, triggers rollback. **Automatically.** Previous stable version deployed."

### Minute 4: Knowledge & Learning
"Grace remembers everything. Every failure, every recovery. Flashcards for quick recall. Trust scores for each component. It's learning from every incident."

### Minute 5: The Multiplier
"This isn't just automation. Grace is an **autonomous AI operating system**. Self-healing, self-monitoring, self-documenting. Your team multiplies their impact."

---

## 🚀 Advanced Demo Features

### 1. Chaos Testing

Inject failures manually:

```bash
# Kill the embedding service
pkill -f embedding_service

# Watch Grace detect and handle it
tail -f logs/self_healing.log
```

### 2. Multi-Book Ingestion

Upload 5 books simultaneously:

```bash
for book in txt/*.txt; do
  curl -X POST http://localhost:8000/api/books/upload \
    -F "file=@$book" &
done
```

Watch Grace manage concurrent operations with self-healing.

### 3. Model A/B Testing

Deploy canary:

```bash
curl -X PATCH http://localhost:8000/api/model-registry/models/fraud_detector_v2/deployment \
  -H "Content-Type: application/json" \
  -d '{
    "status": "canary",
    "canary_percentage": 10.0
  }'
```

Watch Grace route 10% of traffic to the canary and monitor both versions.

---

## 📋 Pre-Demo Checklist

### System Setup
- [ ] Backend running (`python serve.py`)
- [ ] Frontend running (`npm run dev`)
- [ ] Database initialized
- [ ] Sample books in `txt/` folder
- [ ] Model registry populated

### Verification
- [ ] Health endpoint returns 200
- [ ] Self-healing stats accessible
- [ ] Incident registry working
- [ ] Model registry APIs responding
- [ ] Librarian flashcards visible
- [ ] Co-pilot responding

### Demo Data
- [ ] At least 1 book ingested
- [ ] At least 1 resolved incident
- [ ] 3+ models in registry
- [ ] Performance snapshots recorded
- [ ] Flashcards generated
- [ ] Trust metrics populated

### UI Polish
- [ ] Health badges colored correctly
- [ ] Real-time updates working
- [ ] Charts rendering
- [ ] Co-pilot chat smooth
- [ ] Memory Studio navigable

---

## 🎯 Success Criteria

After the demo, the audience should understand:

1. **Grace is autonomous** - Self-healing without human intervention
2. **Grace learns** - Every incident becomes knowledge
3. **Grace is integrated** - All systems work together seamlessly
4. **Grace is production-ready** - Real ML ops with governance
5. **Grace multiplies teams** - Developers, ML engineers, ops all benefit

---

## 📞 Troubleshooting

### Backend not starting
```bash
# Check logs
cat logs/backend.log

# Verify port
lsof -i :8000

# Restart
pkill -f serve.py && python serve.py
```

### Frontend issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database issues
```bash
# Reset databases
rm -f databases/*.db
python -c "from backend.database import init_db; init_db()"
```

### Self-healing not triggering
```bash
# Check event bus
curl http://localhost:8000/api/events/health

# Check self-healing config
cat backend/self_healing/playbooks/*.yaml
```

---

**Ready to impress!** 🚀
