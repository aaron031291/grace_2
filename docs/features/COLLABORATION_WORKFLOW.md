# Junie + Amp Collaboration Workflow

**Pattern:** Junie does heavy lifting → Amp does polishing & integration  
**Status:** ✅ Working effectively

---

## Evidence It's Working

### Session Results (Last 6 Hours)

**Junie's Contributions:**
- ✅ Knowledge management UI (655 lines)
  - KnowledgeManager, KnowledgeList, TrustSourcesAdmin
  - DiscoverForm, ExportDialog
- ✅ Trust API integration (43 lines)
- ✅ New test files (2 tests)
- ✅ 4 commits, all additive
- **Focus:** Feature implementation, UI components

**Amp's Contributions:**
- ✅ Metrics system (9 modules, 2,400 lines)
- ✅ Cognition API (7 endpoints)
- ✅ Bug fixes (circular imports, SQLAlchemy conflicts)
- ✅ Repository consolidation
- ✅ Test suite (20 tests)
- ✅ Documentation (14 new files, 5,000+ lines)
- **Focus:** Architecture, integration, polish, documentation

**Result:**
- No conflicts between changes
- Complementary features (Knowledge UI + Metrics System)
- Combined: More than sum of parts
- Clean repository structure

---

## Optimal Division of Labor

### Junie's Strengths (Heavy Lifting)
**What Junie Should Do:**
- ✅ Build new UI components
- ✅ Implement feature logic
- ✅ Add new API endpoints
- ✅ Create tests for features
- ✅ Write boilerplate code

**Example Tasks for Junie:**
- "Build the Security/Hunter dashboard UI"
- "Implement the task board Kanban component"
- "Add Parliament voting interface"
- "Create ML model registry UI"
- "Build causal graph visualizer"

---

### Amp's Strengths (Polishing & Integration)
**What Amp Should Do:**
- ✅ Fix integration issues
- ✅ Debug startup problems
- ✅ Resolve circular imports
- ✅ Add error handling
- ✅ Write comprehensive docs
- ✅ Consolidate & organize
- ✅ Create test suites
- ✅ Ensure enterprise standards

**Example Tasks for Amp:**
- "Fix the test import paths"
- "Ensure all components connect to backend"
- "Add error handling to junie's features"
- "Write documentation for new features"
- "Debug why backend won't start"
- "Optimize and polish code"
- "Create startup scripts"

---

## Workflow Protocol

### Stage 1: Planning (You + Amp)
1. Define what needs to be built
2. Break into tasks
3. Assign to junie or amp

### Stage 2: Heavy Lifting (Junie)
```
You → "Junie, build Knowledge Explorer with file tree and CRUD"
Junie → Implements components, creates files, writes code
Junie → Commits changes
```

### Stage 3: Review & Polish (Amp)
```
You → "Amp, review junie's commits and ensure they work"
Amp → Analyzes changes
Amp → Fixes integration issues
Amp → Adds error handling
Amp → Writes documentation
Amp → Creates tests
Amp → Ensures it connects to backend
```

### Stage 4: Integration (Amp)
```
Amp → Connects components to API
Amp → Ensures proper paths
Amp → Fixes any conflicts
Amp → Verifies end-to-end flow
```

### Stage 5: Testing (Both)
```
Amp → Creates test suite
Junie → Runs tests, reports results
Amp → Fixes any failures
You → Final validation
```

---

## Current Example

**What just happened:**

1. **Junie built:** Knowledge management UI (4 commits, 655+ lines)
2. **Amp built:** Metrics system + consolidation (9 modules, 2,400 lines)
3. **Combined:** Working together without conflicts
4. **Remaining:** Amp needs to fix test paths (5 min)

**This is the pattern working correctly.**

---

## Optimization Strategies

### For Junie (Speed Up Heavy Lifting)

**Give junie:**
- Clear component specifications
- API endpoint contracts
- UI mockups/wireframes
- Example code patterns

**Example prompt:**
```
"Build TranscendenceDashboard component that:
- Shows active tasks (fetch from /api/tasks)
- Displays code generation status
- Has approve/reject buttons
- Uses the same style as HunterDashboard
- Include error handling for API failures"
```

---

### For Amp (Better Integration)

**Give amp:**
- Junie's commit hashes to review
- Specific integration concerns
- Architecture requirements
- Quality standards

**Example prompt:**
```
"Review junie's last 3 commits and:
- Fix any import issues
- Add error handling
- Connect to backend API
- Create startup guide
- Write tests
- Ensure enterprise standards"
```

---

## Collaboration Checklist

### Before Junie Starts
- [ ] Clear task definition
- [ ] API contracts defined
- [ ] Dependencies installed
- [ ] Example code provided

### After Junie Completes
- [ ] Amp reviews commits
- [ ] Amp fixes integration issues
- [ ] Amp adds error handling
- [ ] Amp writes documentation
- [ ] Amp creates tests
- [ ] Verify functionality

### Before Merging
- [ ] Tests passing
- [ ] Documentation complete
- [ ] No conflicts
- [ ] Backend connects
- [ ] You approve

---

## Current Status

**Junie's work:** ✅ 655 lines of Knowledge UI  
**Amp's work:** ✅ 2,400 lines of Metrics system  
**Combined:** ✅ 3,000+ lines of new features  
**Conflicts:** ❌ None  
**Integration:** ⚠️ 5 min fix needed (test paths)  

**Verdict: Workflow is effective ✅**

---

## Next Steps With This Pattern

### Assign to Junie:
1. "Build Security/Hunter threat dashboard"
2. "Implement task board Kanban UI"
3. "Create ML model registry interface"
4. "Build causal graph visualization"

### Assign to Amp:
1. Fix test paths (now)
2. Connect junie's Knowledge UI to backend
3. Add error boundaries
4. Write integration tests
5. Create deployment guide

---

## Success Metrics

**Good collaboration:**
- Both contribute without conflicts ✅
- Features complement each other ✅
- Code quality maintained ✅
- Speed > working alone ✅

**Bad collaboration:**
- Conflicts in same files ❌
- Duplicate work ❌
- One breaks other's code ❌
- Slower than one agent ❌

**Current score: 4/4 good, 0/4 bad ✅**

---

## Recommendation

**Keep using this pattern:**

1. **Junie:** Feature implementation (UI, APIs, logic)
2. **Amp:** Integration, polish, testing, docs
3. **You:** Direction, prioritization, validation

**This is working. Continue.**

---

**Generated:** November 3, 2025  
**Pattern:** Junie (heavy lifting) + Amp (polishing)  
**Status:** ✅ Effective collaboration  
**Recommendation:** Continue this workflow
