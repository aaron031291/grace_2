# Grace Coding Standards & Anti-Patterns

**Based on Devin's efficiency analysis and system hardening**

## 🚫 Anti-Patterns to Avoid

### 1. Unbounded Database Queries (HIGH SEVERITY)

❌ **WRONG:**
```python
result = await session.execute(query)
items = result.scalars().all()  # Loads everything into memory
```

✅ **CORRECT:**
```python
result = await session.execute(query.limit(100).offset(0))
items = result.scalars()  # Iterate without .all()
```

**Always:**
- Add `.limit()` to queries
- Implement pagination for list endpoints
- Use database-level filtering, not Python

---

### 2. Sync Operations in Async Context (MEDIUM SEVERITY)

❌ **WRONG:**
```python
async def my_function():
    time.sleep(1)  # Blocks entire event loop
```

✅ **CORRECT:**
```python
async def my_function():
    await asyncio.sleep(1)  # Non-blocking
```

---

### 3. Python-Level Filtering (MEDIUM SEVERITY)

❌ **WRONG:**
```python
sources = self.db.query(Source).all()
for source in sources:
    if source.last_scan and (now - source.last_scan) > timedelta(days=1):
        due_sources.append(source)
```

✅ **CORRECT:**
```python
cutoff = now - timedelta(days=1)
sources = self.db.query(Source).filter(
    Source.last_scan < cutoff
).limit(100).all()
```

**Move filtering to SQL:**
- Date comparisons → `.where()` clauses
- String matching → SQL LIKE/regex
- Aggregations → SQL GROUP BY

---

### 4. Inefficient JSON Parsing (LOW SEVERITY)

❌ **WRONG:**
```python
data = json.loads(response['Payload'].read())  # Reads all into memory first
```

✅ **CORRECT:**
```python
data = json.load(response['Payload'])  # Streaming
```

---

### 5. String Concatenation in Loops (LOW SEVERITY)

❌ **WRONG:**
```python
result = ""
for item in items:
    result += str(item)  # Creates new string each iteration
```

✅ **CORRECT:**
```python
result = "".join(str(item) for item in items)
```

---

## 📦 Import Standards

### Canonical Import Paths

✅ **ALWAYS USE:**
```python
from backend.metrics_service import publish_metric, get_metrics_collector
from backend.cognition_metrics import get_metrics_engine
```

❌ **NEVER USE:**
```python
from backend.monitoring.metrics_service import ...  # OLD PATH
from backend.misc.cognition_metrics import ...      # OLD PATH
```

**Why:** Single source of truth. No subdirectory confusion.

---

## 🔍 Pre-Commit Checks

Run before committing:
```bash
python scripts/detect_anti_patterns.py
```

Install automatic checks:
```bash
pip install pre-commit
pre-commit install
```

---

## 📊 Performance Guidelines

### Database Queries
- **Default limit:** 100 items
- **Max limit:** 1000 items
- Always provide pagination: `limit`, `offset`

### Memory Management
- Stream large files, don't load into memory
- Use generators for large datasets
- Close database sessions promptly

### Async Best Practices
- Never use `time.sleep()` in async code
- Use `asyncio.create_task()` for fire-and-forget
- Handle exceptions in async tasks

---

## 🎯 Code Review Checklist

Before approving PRs, verify:

- [ ] No unbounded `.all()` queries
- [ ] Pagination implemented for list endpoints
- [ ] No `time.sleep()` in async functions
- [ ] Canonical import paths used
- [ ] Database filtering, not Python loops
- [ ] Proper error handling
- [ ] Tests included

---

## 🚀 CI/CD Standards

All PRs must pass:
1. Import validation
2. Anti-pattern detection
3. Lint checks (ruff)
4. Unit tests with coverage

---

## 📚 References

- **Devin's Efficiency Report:** `CODE_EFFICIENCY_REPORT.md`
- **PR #2 Improvements:** `CODE_EFFICIENCY_IMPROVEMENTS_PR2.md`
- **Anti-Pattern Scanner:** `scripts/detect_anti_patterns.py`

---

**Last Updated:** Sovereignty Fix - Nov 2025
**Maintained By:** Grace Core Team
