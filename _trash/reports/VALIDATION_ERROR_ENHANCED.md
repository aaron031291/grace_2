# Validation Error Response Enhanced

**Date:** 2025-11-08  
**Status:** ✅ ENHANCED

## Problem

Validation errors (422) returned basic structure without pipeline traceability:

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

❌ No execution trace  
❌ No data provenance  
❌ No helpful suggestions  
❌ No documentation links

## Solution

Updated validation error handler to return **ErrorResponse** format with full traceability.

### Before:
```python
return JSONResponse(
    status_code=422,
    content={
        "error": "validation_error",
        "message": "Request validation failed",
        "details": exc.errors(),
        "request_id": request_id
    }
)
```

### After:
```python
return JSONResponse(
    status_code=422,
    content={
        "error": "validation_error",
        "message": f"Request validation failed: {error_msg}",
        "details": {"validation_errors": errors, "field": field},
        "request_id": request_id,
        "suggestions": [
            "Provide the required field: email",
            "See API documentation for correct format"
        ],
        "documentation_url": "http://localhost:8000/docs",
        "timestamp": "2025-11-08T12:00:00Z",
        "execution_trace": {
            "request_id": "req_xyz",
            "steps": [{
                "component": "fastapi_validator",
                "action": "validate_request_schema",
                "data_source": "request_body",
                "error": "Validation failed at field 'email': field required"
            }],
            "data_sources_used": ["request_body", "openapi_schema"]
        },
        "data_provenance": [{
            "source_type": "request",
            "source_id": "request_body",
            "confidence": 0.0,
            "verified": false
        }]
    }
)
```

## Example: Missing Required Field

**Request:**
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John"}'
# Missing required field: email
```

**Response (422):**
```json
{
  "error": "validation_error",
  "message": "Request validation failed: field required",
  "details": {
    "validation_errors": [
      {
        "loc": ["body", "email"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ],
    "field": "body -> email"
  },
  "request_id": "req_abc123",
  "suggestions": [
    "Provide the required field: body -> email",
    "See API documentation for correct format"
  ],
  "documentation_url": "http://localhost:8000/docs",
  "timestamp": "2025-11-08T12:00:00Z",
  "execution_trace": {
    "request_id": "req_abc123",
    "total_duration_ms": 0,
    "steps": [
      {
        "step_number": 1,
        "component": "fastapi_validator",
        "action": "validate_request_schema",
        "duration_ms": 0,
        "data_source": "request_body",
        "error": "Validation failed at field 'body -> email': field required"
      }
    ],
    "data_sources_used": ["request_body", "openapi_schema"],
    "agents_involved": [],
    "database_queries": 0
  },
  "data_provenance": [
    {
      "source_type": "request",
      "source_id": "request_body",
      "timestamp": "2025-11-08T12:00:00Z",
      "confidence": 0.0,
      "verified": false
    }
  ]
}
```

## Example: Wrong Type

**Request:**
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": 123, "name": "John"}'
# Email should be string, not number
```

**Response (422):**
```json
{
  "error": "validation_error",
  "message": "Request validation failed: str type expected",
  "details": {
    "validation_errors": [
      {
        "loc": ["body", "email"],
        "msg": "str type expected",
        "type": "type_error.str"
      }
    ],
    "field": "body -> email"
  },
  "request_id": "req_xyz789",
  "suggestions": [
    "Check the data type for field: body -> email",
    "See API documentation for correct format"
  ],
  "documentation_url": "http://localhost:8000/docs",
  "execution_trace": {
    "steps": [{
      "component": "fastapi_validator",
      "error": "Validation failed at field 'body -> email': str type expected"
    }]
  },
  "data_provenance": [{
    "source_type": "request",
    "confidence": 0.0,
    "verified": false
  }]
}
```

## Benefits

### 1. **Better Developer Experience**
- Clear error messages with field names
- Helpful suggestions to fix the issue
- Direct link to API documentation
- Shows exactly where validation failed

### 2. **Pipeline Visibility**
- `execution_trace` shows validation happened before processing
- Reveals which component caught the error (fastapi_validator)
- Shows request body was the data source
- Confirms no database queries were made (failed early)

### 3. **Data Provenance**
- Marks request data as `verified: false`
- Shows `confidence: 0.0` for invalid data
- Tracks that source was `request_body`
- Helps identify malformed client requests

### 4. **Consistent Error Format**
All errors now follow the same pattern:
- ✅ Validation errors (422)
- ✅ Application errors (ErrorResponse)
- ✅ Internal errors (500)

### 5. **Automatic Suggestions**
Smart suggestions based on error type:
- Missing field → "Provide the required field: X"
- Wrong type → "Check the data type for field: X"
- Generic → "Check your request body matches the API schema"

## Impact

**Every validation error across all endpoints** now includes:
- ✅ Execution trace showing validation pipeline
- ✅ Data provenance marking data as unverified
- ✅ Helpful suggestions to fix the error
- ✅ Documentation link
- ✅ Request ID for debugging
- ✅ Timestamp

## Files Modified

1. ✅ [backend/main.py](file:///c:/Users/aaron/grace_2/backend/main.py) - Enhanced validation_exception_handler

## Testing

```python
# Test missing field
curl -X POST http://localhost:8000/api/test \
  -H "Content-Type: application/json" \
  -d '{}'
# ✅ Returns helpful error with suggestions

# Test wrong type
curl -X POST http://localhost:8000/api/test \
  -H "Content-Type: application/json" \
  -d '{"field": 123}' 
# ✅ Returns type error with field name and suggestions
```

## What This Means

Now **every validation error** in Grace's API provides:
1. **What went wrong** - Clear error message
2. **Where it failed** - Exact field path
3. **How to fix it** - Actionable suggestions
4. **Where to look** - Documentation link
5. **Pipeline trace** - Shows request → validation → error
6. **Data status** - Marks data as unverified

**Complete observability even for invalid requests!** 🎯
