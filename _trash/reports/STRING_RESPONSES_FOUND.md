# API Endpoints Returning Raw Strings/Dicts

**Date:** 2025-11-08  
**Status:** ⚠️ FOUND 48 ENDPOINTS RETURNING RAW DATA

## Summary

Found **48 endpoints** returning raw dicts/lists instead of proper Pydantic schemas. These show as **"string"** in API documentation.

### Breakdown:
- **RAW_DICT:** 44 endpoints - Return plain dictionaries
- **RAW_LIST:** 4 endpoints - Return plain lists
- **Total Files Affected:** 19 files

## Priority Files to Fix

| File | Endpoints | Priority |
|------|-----------|----------|
| agentic_insights.py | 4 | HIGH |
| goals.py | 4 | HIGH |
| ingest.py | 4 | HIGH |
| execution.py | 3 | MEDIUM |
| health_unified.py | 3 | MEDIUM |
| incidents.py | 3 | MEDIUM |
| issues.py | 3 | MEDIUM |
| metrics.py | 3 | MEDIUM |
| ml_api.py | 3 | MEDIUM |
| plugin_routes.py | 3 | MEDIUM |
| commit_routes.py | 2 | LOW |
| learning_routes.py | 2 | LOW |
| reflections.py | 2 | LOW |
| scheduler_observability.py | 2 | LOW |
| subagent_bridge.py | 2 | LOW |
| summaries.py | 2 | LOW |
| evaluation.py | 1 | LOW |
| meta_focus.py | 1 | LOW |
| playbooks.py | 1 | LOW |

## Detailed List

### agentic_insights.py (4 endpoints)
```python
# Line 92
GET /status
return {...  # ❌ Raw dict

# Line 179
POST /verbosity
return {"verbosity": level, "message": f"Verbosity set to {level}"}  # ❌ Raw dict

# Line 204
GET /search
return {...  # ❌ Raw dict

# Line 227
GET /health
return {...  # ❌ Raw dict
```

### goals.py (4 endpoints)
```python
# Line 137
POST /{goal_id}/criteria
return {"ok": True}  # ❌ Raw dict

# Line 154
POST /{goal_id}/dependencies
return {"ok": True, "dependency_id": dep.id}  # ❌ Raw dict

# Line 175
GET /{goal_id}/graph
return {"nodes": nodes, "edges": edges}  # ❌ Raw dict

# Line 197
POST /{goal_id}/evaluate
return {"goal_id": goal.id, "status": status...}  # ❌ Raw dict
```

### ingest.py (4 endpoints)
```python
# Line 27
POST /text
return {"status": "ingested", "artifact_id": artifact_id}  # ❌ Raw dict

# Line 50
POST /url
return {...  # ❌ Raw dict

# Line 109
POST /file
return {...  # ❌ Raw dict

# Line 137
GET /artifacts
return [...]  # ❌ Raw list
```

### execution.py (3 endpoints)
```python
# Line 69
GET /languages
return {"languages": languages, "count": len(languages)}  # ❌ Raw dict

# Line 89
GET /presets
return {"presets": presets, "count": len(presets)}  # ❌ Raw dict

# Line 109
POST /validate
return {...  # ❌ Raw dict
```

### health_unified.py (3 endpoints)
```python
# Line 38
POST /health/ingest_signal
return {"ok": True, "service_id": svc.id, "signal_id": sig.id}  # ❌ Raw dict

# Line 58
GET /health/state
return {...  # ❌ Raw dict

# Line 99
POST /triage/diagnose
return {"service": svc.name, "diagnoses": findings}  # ❌ Raw dict
```

### incidents.py (3 endpoints)
```python
# Line 30
POST /notify
return {"ok": True, "incident_id": inc.id}  # ❌ Raw dict

# Line 65
POST /ack
return {"ok": True, "incident_id": inc.id, "status": inc.status}  # ❌ Raw dict

# Line 94
GET /{incident_id}
return {...  # ❌ Raw dict
```

### issues.py (3 endpoints)
```python
# Line 12
GET /
return [...]  # ❌ Raw list

# Line 41
GET /{issue_id}
return {...  # ❌ Raw dict

# Line 66
POST /{issue_id}/resolve
return result  # ❌ Raw dict
```

### metrics.py (3 endpoints)
```python
# Line 10
GET /summary
return {...  # ❌ Raw dict

# Line 26
GET /user/{username}
return {...  # ❌ Raw dict

# Line 46
GET /history
return {"domain": domain, "kpi": kpi, "count": len(events), "events": events}  # ❌ Raw dict
```

### ml_api.py (3 endpoints)
```python
# Line 11
POST /train
return {"status": "trained", "model_id": model_id}  # ❌ Raw dict

# Line 32
POST /deploy/{model_id}
return {"status": "deployed" if success else "blocked"}  # ❌ Raw dict

# Line 42
GET /models
return [...]  # ❌ Raw list
```

### plugin_routes.py (3 endpoints)
```python
# Line 7
GET /
return {"plugins": plugin_manager.list_plugins()}  # ❌ Raw dict

# Line 12
POST /{plugin_name}/enable
return {"status": "enabled", "plugin": plugin_name}  # ❌ Raw dict

# Line 21
POST /{plugin_name}/disable
return {"status": "disabled", "plugin": plugin_name}  # ❌ Raw dict
```

## Why This Is a Problem

### 1. **API Documentation Shows "string"**
```yaml
responses:
  200:
    description: Successful Response
    content:
      application/json:
        schema:
          type: string  # ❌ Not helpful!
```

### 2. **No Type Safety**
- Frontend can't auto-generate types
- No IDE autocomplete
- No validation at runtime

### 3. **No Execution Traceability**
- Can't include execution_trace
- Can't include data_provenance
- No pipeline visibility

### 4. **Inconsistent API**
- Some endpoints have schemas
- Some return raw dicts
- Confusing for developers

## Solution Needed

Each endpoint needs:

1. **Pydantic Response Schema**
```python
class EndpointResponse(BaseModel):
    # ... response fields ...
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)
```

2. **response_model Declaration**
```python
@router.get("/endpoint", response_model=EndpointResponse)
async def endpoint():
    return EndpointResponse(...)
```

3. **Proper Response Construction**
```python
# Before
return {"status": "ok", "data": data}

# After
return EndpointResponse(
    status="ok",
    data=data,
    execution_trace=...,
    data_provenance=...
)
```

## Next Steps

1. Create missing schemas in schemas_extended.py
2. Update each endpoint to use response_model
3. Modify return statements to use schema classes
4. Add execution_trace and data_provenance
5. Test API documentation

Full audit saved to: [string_responses_audit.txt](file:///c:/Users/aaron/grace_2/reports/string_responses_audit.txt)

**48 endpoints need fixing to complete API traceability!**
