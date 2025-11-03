# Codebase Consolidation Plan

**Goal:** Make `grace_rebuild/` the single source of truth, eliminate duplication

---

## Current Structure Analysis

### Root Directory (OLD - Contains duplicates)
```
grace_2/
├── scripts/          ← 13 old files (auth.py, database.py, etc.)
├── docs/             ← 34 old .md files
├── batch_scripts/    ← 3 old .bat files
├── txt/              ← 1 old requirements.txt
├── databases/        ← Empty or old data
├── grace-frontend/   ← KEEP (only copy)
├── grace_rebuild/    ← NEW (source of truth)
└── sandbox/          ← ?
```

### grace_rebuild/ (NEW - Source of truth)
```
grace_rebuild/
├── backend/          ← All production code (100+ files)
├── scripts/          ← 38 scripts including new tests
├── docs/             ← 100+ docs including new ones
├── batch_scripts/    ← 16 scripts including new ones
├── txt/              ← 5 .txt files
├── databases/        ← metrics.db
├── grace-frontend/   ← Duplicate of root
├── cli/              ← CLI code
├── tests/            ← Test infrastructure
└── minimal_backend.py ← New working backend
```

---

## Consolidation Strategy

### Phase 1: Identify What to Keep

**From root (to review):**
- `scripts/` - Check if anything unique
- `grace-frontend/` - Keep this one or rebuild's?
- `sandbox/` - Check if contains anything
- `ml_artifacts/` - Check if contains data

**From grace_rebuild:**
- Keep everything - this is the active codebase

---

### Phase 2: Move grace_rebuild Up

**Actions:**
1. Copy `grace_rebuild/` contents to root
2. Merge any unique files from old root
3. Delete old duplicates
4. Remove now-empty `grace_rebuild/` folder

---

### Phase 3: Clean Directory Structure

**Final structure:**
```
grace_2/
├── backend/          ← Production code
├── frontend/         ← Renamed from grace-frontend
├── cli/              ← CLI tools
├── scripts/          ← All scripts (consolidated)
├── docs/             ← All documentation
├── batch_scripts/    ← Startup scripts
├── tests/            ← Test infrastructure
├── config/           ← Configuration
├── databases/        ← Database files
├── txt/              ← Text files
├── ml_artifacts/     ← ML models/data
├── reports/          ← Generated reports
├── minimal_backend.py ← Quick start backend
└── README.md         ← Main readme
```

---

## Execution Plan

### Step 1: Backup Current State
```bash
git add -A
git commit -m "Backup before consolidation"
git branch backup-pre-consolidation
```

### Step 2: Check for Unique Files in Root

Compare:
- Root scripts vs grace_rebuild scripts
- Root docs vs grace_rebuild docs
- Root frontend vs grace_rebuild frontend

### Step 3: Consolidate

```bash
# Move unique files from root to grace_rebuild
# (if any found)

# Move grace_rebuild contents up
xcopy /E /Y grace_rebuild\backend backend\
xcopy /E /Y grace_rebuild\cli cli\
xcopy /E /Y grace_rebuild\tests tests\
# ... etc for each directory

# Copy key files
copy grace_rebuild\minimal_backend.py .
copy grace_rebuild\*.bat .
```

### Step 4: Clean Up

```bash
# Remove old root files
rmdir /S /Q grace_2\scripts
rmdir /S /Q grace_2\docs
rmdir /S /Q grace_2\batch_scripts

# Remove grace_rebuild after migration
rmdir /S /Q grace_rebuild
```

### Step 5: Verify

```bash
# Test backend still works
py minimal_backend.py

# Test frontend still works
cd frontend
npm run dev

# Run tests
py scripts\test_grace_simple.py
```

---

## Risk Assessment

**Low Risk:**
- grace_rebuild has all the active code
- Root files appear to be old/duplicates
- Git backup created before changes

**Mitigation:**
- Create git branch first
- Keep backup for 1 week
- Test after each major move

---

## Which grace-frontend to Keep?

**Root grace-frontend:**
- Check if has unique components
- Check if more developed

**grace_rebuild/grace-frontend:**
- Check if same or different

**Decision:** Compare and keep the more complete one

---

## Next Steps

1. Review this plan
2. Create backup branch
3. Execute consolidation
4. Test everything works
5. Commit consolidated structure

---

**Ready to execute when you confirm.**
