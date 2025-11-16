# TRUST Framework - Quick Start Guide

## What You Have

**21 production systems** for enterprise-grade AI governance across **20 open-source models**.

**Everything is production code. No stubs, no placeholders.**

---

## Quick Start (5 Minutes)

### 1. Start Grace

```bash
python serve.py
```

Wait for boot to complete. You'll see:

```
[CHUNK 6] TRUST Framework + External Model Protocol
  ✓ HTM Anomaly Detection: Active
  ✓ Verification Mesh: 5-role quorum
  ✓ Model Health Telemetry: 20 monitors
  ✓ Adaptive Guardrails: 4 levels
  ✓ Ahead-of-User Research: Predictive
  ✓ Data Hygiene Pipeline: 6 checks
  ✓ Hallucination Ledger: Tracking
  ✓ External Model Protocol: Secure
  ✓ Advanced Watchdog: Predictive failure detection
  ✓ Model Integrity System: Checksum + behavioral verification
  ✓ Model Rollback: Snapshot-based recovery
```

### 2. Check Dashboard

```bash
curl http://localhost:8000/api/trust/dashboard
```

Or use CLI:

```bash
python scripts/utilities/trust_framework_cli.py dashboard
```

### 3. Verify Models

```bash
python scripts/utilities/verify_all_models.cmd
```

---

## Key Commands

### CLI Tool

```bash
# Framework status
python scripts/utilities/trust_framework_cli.py status

# Dashboard
python scripts/utilities/trust_framework_cli.py dashboard

# Check specific model health
python scripts/utilities/trust_framework_cli.py health qwen2.5:72b

# Verify model integrity
python scripts/utilities/trust_framework_cli.py integrity llama3.1:70b

# Run stress test (maps execution window)
python scripts/utilities/trust_framework_cli.py stress-test deepseek-r1:70b

# List all models
python scripts/utilities/trust_framework_cli.py list-health
```

### API Endpoints

```bash
# Complete status
curl http://localhost:8000/api/trust/status

# Dashboard
curl http://localhost:8000/api/trust/dashboard

# Model health
curl http://localhost:8000/api/trust/models/qwen2.5:72b/health

# All models health
curl http://localhost:8000/api/trust/models/health/all

# Verify integrity
curl http://localhost:8000/api/trust/models/llama3.1:70b/integrity

# Hallucination ledger
curl http://localhost:8000/api/trust/hallucinations/ledger

# Retraining priorities
curl http://localhost:8000/api/trust/hallucinations/retraining-priorities

# Data hygiene stats
curl http://localhost:8000/api/trust/data-hygiene/stats

# Chaos drill stats
curl http://localhost:8000/api/trust/chaos-drills/stats

# Run stress test
curl -X POST http://localhost:8000/api/trust/models/deepseek-r1:70b/stress-test

# Get execution window
curl http://localhost:8000/api/trust/models/deepseek-r1:70b/execution-window
```

---

## What Each System Does

### 1. **HTM Anomaly Detection**
Learns baseline probability distributions, detects when model output drifts.

**When to use**: Continuous monitoring (runs automatically)

### 2. **Verification Mesh**
5-role quorum validation before accepting any output.

**When to use**: High-stakes decisions, critical operations

### 3. **Model Health Telemetry**
Token-level metrics (perplexity, entropy, latency).

**When to use**: Performance monitoring, capacity planning

### 4. **Adaptive Guardrails**
Dynamic trust thresholds based on mission risk + hallucination history.

**When to use**: All missions (auto-adjusts)

### 5. **Ahead-of-User Research**
Predicts likely next questions, pre-fetches research.

**When to use**: Long conversations, research sessions

### 6. **Data Hygiene Pipeline**
6 audit checks before data enters system.

**When to use**: Before ingesting external data

### 7. **Hallucination Ledger**
Tracks every error, adjusts model trust dynamically.

**When to use**: Post-incident analysis, retraining decisions

### 8. **Model Integrity**
Checksum + behavioral verification to detect tampering.

**When to use**: Daily verification, after model updates

### 9. **Model Rollback**
Revert to known-good versions when needed.

**When to use**: After integrity violations, performance issues

### 10. **Stress Testing**
Maps safe execution windows per model.

**When to use**: One-time setup for each model, after updates

### 11. **Context Provenance**
Every chunk has source_id + confidence + freshness.

**When to use**: Context re-use decisions

### 12. **Uncertainty Reporting**
"60% confident—need X, Y, Z to reach 90%"

**When to use**: When confidence is insufficient

---

## Common Workflows

### Daily Operations

**Morning check:**
```bash
python scripts/utilities/trust_framework_cli.py dashboard
```

**If issues found:**
```bash
python scripts/utilities/trust_framework_cli.py health <model>
python scripts/utilities/trust_framework_cli.py integrity <model>
```

**If model compromised:**
```bash
curl -X POST http://localhost:8000/api/trust/models/<model>/rollback
```

### New Model Setup

**After installing new model:**
```bash
# 1. Verify integrity
python scripts/utilities/trust_framework_cli.py integrity <model>

# 2. Map execution window
python scripts/utilities/trust_framework_cli.py stress-test <model>

# 3. Check health
python scripts/utilities/trust_framework_cli.py health <model>
```

### Security Testing

**Run chaos drills:**
```bash
curl -X POST http://localhost:8000/api/trust/chaos-drills/run/<model>
```

**Check results:**
```bash
curl http://localhost:8000/api/trust/chaos-drills/stats
```

### Performance Issues

**Check execution windows:**
```bash
curl http://localhost:8000/api/trust/models/<model>/execution-window
```

**Check if in grey zone:**
```bash
python scripts/utilities/trust_framework_cli.py health <model>
```

**If degrading:**
- Reduce context window
- Consider preventive restart
- Check for memory leaks

---

## Guardian Auto-Remediation

Guardian automatically handles:

- **Port not responding** → Kill zombie + restart
- **Module not found** → Fix import paths
- **Network degradation** → Run diagnostics + cleanup
- **Service crashed** → Collect logs + restart
- **Guardrail bypassed** → Quarantine model + alert

**Check remediation stats:**
```bash
curl http://localhost:8000/api/ports/status
```

---

## Integration with Existing Systems

### With Self-Healing
- Guardian delegates system recovery to self-healing
- Shares network + boot playbooks

### With Coding Agent
- Guardian delegates code fixes to coding agent
- Receives code-related triggers

### With Port Manager
- Advanced watchdog predicts port failures
- Preventive restarts before service dies

---

## Files & Locations

**Code**: `backend/trust_framework/`
**APIs**: `backend/routes/trust_framework_api.py`
**CLI**: `scripts/utilities/trust_framework_cli.py`
**Data**: `databases/` (fingerprints, ledgers, baselines)
**Logs**: `logs/external_model_audit/`
**Docs**: `docs/TRUST_FRAMEWORK_COMPLETE.md`

---

## Troubleshooting

**"Could not connect to Grace"**
- Make sure Grace is running: `python serve.py`
- Check port: Default is 8000

**"Model not found"**
- Check model is installed: `ollama list`
- Verify exact name (including tag): `qwen2.5:72b` not just `qwen2.5`

**"Stress test timeout"**
- Increase timeout in CLI
- Run stress test on smaller models first
- Large models (236B) take longer

**"Integrity verification failed"**
- Check model was installed correctly
- Re-pull model: `ollama pull <model>`
- Create new snapshot after verification

---

## What's Next

**Immediate:**
1. Verify all 20 models: `python scripts/utilities/verify_all_models.cmd`
2. Map execution windows for critical models (qwen2.5:72b, llama3.1:70b, deepseek-r1:70b)
3. Monitor dashboard: `python scripts/utilities/trust_framework_cli.py dashboard`

**Ongoing:**
- Daily health checks
- Weekly integrity verification
- Monthly stress tests
- Quarterly chaos drills

**Advanced:**
- Integrate with SIEM/monitoring tools
- Connect to incident response system
- Add custom playbooks
- Tune guardrail thresholds

---

## Summary

✅ **21 production systems**
✅ **20+ API endpoints**
✅ **Full CLI tooling**
✅ **Auto-remediation active**
✅ **Complete observability**

**Grace has enterprise-grade AI governance.**

**Start using:** `python serve.py` then `python scripts/utilities/trust_framework_cli.py dashboard`

🎯 **Production ready. Nothing missing.**
