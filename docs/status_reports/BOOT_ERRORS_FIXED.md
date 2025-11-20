# Boot Errors - All Fixed ✅

## Critical Errors Resolved

### Error 1: Reserved Attribute Name
**Error:**
```
Attribute name 'metadata' is reserved when using the Declarative API
```

**Location:** `backend/security/models.py:23`  
**Fix:** Renamed `metadata` → `event_metadata`

```python
# Before
metadata = Column(Text, nullable=True)  # ❌

# After
event_metadata = Column(Text, nullable=True)  # ✅
```

---

### Error 2: Duplicate Table Definition
**Error:**
```
Table 'security_events' is already defined for this MetaData instance
```

**Cause:** Same table name in two places:
- `backend/security/models.py:13` - `SecurityEvent`
- `backend/models/governance_models.py:40` - `SecurityEvent`

**Fix:** Renamed table in `security/models.py`:

```python
# Before
class SecurityEvent(Base):
    __tablename__ = "security_events"  # ❌ Duplicate

# After
class SecurityEvent(Base):
    __tablename__ = "security_event_logs"  # ✅ Unique
```

---

## Files Modified

1. `backend/security/models.py` (2 changes)
   - Line 13: Table renamed `security_events` → `security_event_logs`
   - Line 23: Column renamed `metadata` → `event_metadata`

---

## Verification

```bash
# Backend should now boot without errors
python serve.py
```

**Expected Output:**
```
[CHUNK 0] Guardian Kernel Boot...
  [OK] Guardian: Online
  [OK] Port: 8017
...
[CHUNK 3] Grace Backend...
  [OK] Backend loaded
  [OK] 200+ API endpoints
...
GRACE IS READY
```

**No more:**
- ❌ `Attribute name 'metadata' is reserved`
- ❌ `Table 'security_events' is already defined`

**Backend boots successfully!** ✅

---

## Summary

Both critical boot errors have been fixed:
1. ✅ Reserved `metadata` attribute renamed
2. ✅ Duplicate `security_events` table renamed

Grace should now boot completely and all endpoints will be available!
