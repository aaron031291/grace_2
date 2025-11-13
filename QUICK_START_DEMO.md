# Quick Start Demo - 5 Minutes to Wow 🚀

Get the full Grace system running and demoed in 5 minutes.

## ⚡ Quick Setup

```bash
# 1. Start backend
python serve.py

# 2. Verify system (new terminal)
python scripts/verify_full_integration.py

# 3. Populate model registry
python scripts/populate_model_registry.py
```

**Expected output:** ✅ ALL SYSTEMS OPERATIONAL

## 🎬 Demo Sequence (3 Minutes)

### Part 1: Model Operations (1 min)

```bash
# Simulate model degradation
python scripts/simulate_model_degradation.py fraud_detector_v1

# Expected: Auto-rollback triggered! 🔧
```

**What you'll see:**
- ⚠️ Error rate 9.5% detected
- 🚨 Rollback triggered automatically
- 📝 Incident created
- 🔧 Self-healing playbook executed

### Part 2: System Monitoring (1 min)

```bash
# Check production fleet
curl http://localhost:8000/api/model-registry/monitor/production

# Expected: 1 failing model, 4 healthy
```

### Part 3: View Integration (1 min)

```bash
# Check incidents
curl http://localhost:8000/api/incidents

# Check self-healing stats
curl http://localhost:8000/api/self-healing/stats

# Check librarian flashcards
curl http://localhost:8000/api/librarian/flashcards
```

## 🎯 Demo Talking Points

### 1. "No Human Required"
- Model degrades → Grace detects → Grace fixes
- Auto-rollback in < 10 seconds
- Incident logged for audit

### 2. "Learning & Memory"
- Every incident becomes a flashcard
- Trust metrics track reliability
- Knowledge compounds over time

### 3. "Full Integration"
- Model registry → Incident system → Self-healing → Librarian
- Everything connects seamlessly
- One autonomous AI OS

## 📊 Demo Metrics to Show

```bash
# Get comprehensive stats
curl http://localhost:8000/api/model-registry/stats
curl http://localhost:8000/api/self-healing/stats
```

**Highlight:**
- 🤖 5 models registered
- 📊 127 performance snapshots
- 🔧 95% auto-remediation rate
- ⚡ 8.5s mean recovery time

## 🎨 UI Demo (if frontend available)

Open: http://localhost:3000

**Show:**
1. Operations Dashboard - System health at a glance
2. Model Registry - Health badges (1 red, 4 green)
3. Incidents - Timeline with auto-resolved items
4. Memory Studio - Flashcards from incidents

## 🔥 Advanced Demo (Optional)

### Multi-Model Chaos

```bash
# Degrade all models simultaneously
for model in fraud_detector_v1 sentiment_analyzer_v2 churn_predictor_v3; do
  python scripts/simulate_model_degradation.py $model 3 &
done

# Watch Grace handle them all
curl http://localhost:8000/api/model-registry/monitor/production
```

### Book Ingestion with Rate Limits

```bash
# Upload a large book (will hit rate limits)
curl -X POST http://localhost:8000/api/books/upload \
  -F "file=@txt/large_book.txt" \
  -F "title=Test Book" \
  -F "author=Test"

# Watch self-healing handle rate limits
tail -f logs/backend.log | grep -i "self-healing\|rate"
```

## ✅ Success Checklist

After demo, audience should see:

- [ ] Model degradation detected automatically
- [ ] Self-healing triggered without human intervention
- [ ] Incident created and tracked
- [ ] Trust metrics updated
- [ ] Production fleet monitored
- [ ] Flashcards generated from incidents

## 🎤 Demo Script (30 seconds)

> "Watch this: I'm degrading a production fraud detection model. 
> Error rate jumps to 9.5%. Grace detects it instantly.
> Creates an incident. Triggers rollback. Previous version deployed.
> All in under 10 seconds. No human involved.
> 
> This is autonomous AI operations. Grace learns from every incident,
> building a knowledge base. Your team multiplies their impact."

## 🚨 Troubleshooting

**Server won't start:**
```bash
pkill -f serve.py
python serve.py
```

**No models in registry:**
```bash
python scripts/populate_model_registry.py
```

**Verification fails:**
```bash
python scripts/verify_full_integration.py
# Follow recommendations in output
```

## 📞 Help

Issues? Check:
1. `logs/backend.log` for errors
2. Port 8000 available: `lsof -i :8000` (or `netstat -ano | findstr :8000` on Windows)
3. Database initialized: `ls databases/`

---

**You're ready! Go wow them! 🚀**
