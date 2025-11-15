# Grace - Quick Start

## Start Grace (2 Terminals)

### Terminal 1: Start Backend
```bash
python serve.py
```

Or use:
```bash
RUN_GRACE.cmd
```

### Terminal 2: Start Learning
```bash
python start_grace_now.py
```

This will:
1. ✅ Get curriculum overview (11 domains, 25+ projects)
2. ✅ Start first project (CRM System or E-commerce Analytics)
3. ✅ Grace works autonomously for 1 hour
4. ✅ Shows progress and learnings

---

## What You'll See

```
======================================================================
GRACE - AUTONOMOUS AI LEARNING SYSTEM
======================================================================

STEP 1: Get Curriculum Overview
----------------------------------------------------------------------
📚 Total Knowledge Domains: 11
🎓 Domains Mastered: 0
✅ Projects Completed: 0

🎯 Priority Projects (Business Value):
   1. proj_crm_system - Full CRM System (business need)
   2. proj_ecommerce_tracking - E-commerce Analytics SaaS
   3. proj_cloud_infra_scratch - Cloud Infrastructure from Scratch

STEP 2: Check Current Status
----------------------------------------------------------------------
🤖 System: autonomous_learning
📝 Mode: project_based
🧠 LLM: local_open_source
🧪 Sandbox: Enabled
💤 No active project - Ready to start learning!

STEP 3: Start First Project
----------------------------------------------------------------------
🚀 Starting next learning project...
✅ Project Started!
   ID: proj_crm_system
   Name: Full CRM System
   Domain: business_apps
   
📋 Project Plan:
   Total Phases: 5
   Estimated Hours: 90
   
   Phases:
      1. Research & Design
      2. Core Implementation
      3. Advanced Features
      4. Testing & Edge Cases
      5. Documentation & KPIs

STEP 4: Grace Works on Project
----------------------------------------------------------------------
🔨 Grace is working autonomously...
✅ Work Session Complete!
   Progress: 2.5%
   Iterations: 4
   Edge Cases Discovered: 1
   Solutions Tested: 1
   Learnings Recorded: 4

✅ GRACE IS NOW LEARNING!
```

---

## Continue Learning

**Let Grace work more:**
```bash
curl -X POST http://localhost:8000/api/learning/project/work \
  -H "Content-Type: application/json" \
  -d '{"hours": 2.0}'
```

**Check progress:**
```bash
curl http://localhost:8000/api/learning/progress
```

**Complete project (when ~100%):**
```bash
curl -X POST http://localhost:8000/api/learning/project/complete
```

---

## API Endpoints

All learning APIs available at: http://localhost:8000/docs

Key endpoints:
- `GET /api/learning/curriculum/overview` - See all domains
- `GET /api/learning/progress` - Current progress
- `POST /api/learning/project/start` - Start next project
- `POST /api/learning/project/work` - Work session
- `POST /api/learning/project/complete` - Finish project

---

## What Grace Is Doing

When you run `start_grace_now.py`, Grace:

1. **Picks Priority Project** (CRM, E-commerce, or Cloud)
2. **Creates Project Plan** (Research → Implementation → Testing → Docs)
3. **Works Autonomously**:
   - Implements features
   - Discovers edge cases in sandbox
   - Tests multiple solutions
   - Optimizes performance
   - Documents everything
4. **Tracks KPIs**:
   - Code quality
   - Test coverage
   - Performance benchmarks
   - Documentation
5. **Calculates Trust Score** (must be ≥70%)
6. **Records Learnings** to memory

---

## Remote Access (Bonus)

While Grace is learning, you can also use remote access:

**Terminal 3:**
```bash
python remote_access_client.py setup
python remote_access_client.py shell
```

---

## Files & Directories

**Grace's Work:**
- `sandbox/learning_projects/proj_*/` - Built projects
- `databases/learning_curriculum/` - Progress tracking
- `logs/remote_sessions/` - Remote access recordings

**Documentation:**
- `AUTONOMOUS_LEARNING_SYSTEM.md` - Complete learning docs
- `REMOTE_ACCESS_LIVE.md` - Remote access guide
- `GRACE_LEARNING_COMPLETE.md` - System overview

---

## That's It!

**Start Grace:**
```bash
# Terminal 1
python serve.py

# Terminal 2
python start_grace_now.py
```

**Grace is now learning by building real systems!** 🚀
