# Verification & Mission API Documentation

**Base URL**: `http://localhost:8000/api/verification`  
**Authentication**: Bearer token required (except `/health`)  
**Version**: 1.0.0

---

## Overview

The Verification API provides stable contracts for frontend consumption of:
- **Action Contracts** - Expected vs actual verification records
- **Safe-Hold Snapshots** - Rollback capability
- **Mission Timelines** - Multi-action progression tracking
- **System Health** - Smoke checks and statistics

All endpoints include data integrity checks and follow consistent response schemas.

---

## Endpoints

### GET `/stats`

Get overall verification statistics.

**Query Parameters**:
- `days` (optional): Number of days to look back (default: 7, max: 90)

**Response**: `VerificationStats`
```json
{
  "total_contracts": 142,
  "successful_contracts": 135,
  "failed_contracts": 5,
  "rolled_back_contracts": 2,
  "success_rate": 95.07,
  "avg_confidence": 0.847,
  "total_snapshots": 28,
  "golden_snapshots": 3
}
```

**Example**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/verification/stats?days=30"
```

---

### GET `/contracts`

List action contracts with pagination and filtering.

**Query Parameters**:
- `limit` (optional): Max results (default: 50, max: 500)
- `offset` (optional): Pagination offset (default: 0)
- `tier` (optional): Filter by tier (`tier_1`, `tier_2`, `tier_3`)
- `status` (optional): Filter by status (`pending`, `verified`, `failed`, `rolled_back`)

**Response**: `List[ContractSummary]`
```json
[
  {
    "id": "contract-abc123",
    "action_type": "clear_lock_files",
    "tier": "tier_2",
    "status": "verified",
    "confidence_score": 0.95,
    "created_at": "2025-11-07T18:00:00Z",
    "executed_at": "2025-11-07T18:00:02Z",
    "was_rolled_back": false
  }
]
```

**Example**:
```bash
# Get tier 2 contracts only
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/verification/contracts?tier=tier_2&limit=20"
```

---

### GET `/contracts/{contract_id}`

Get full contract details including verification results.

**Path Parameters**:
- `contract_id` (required): Contract identifier

**Response**: `ContractDetail`
```json
{
  "id": "contract-abc123",
  "action_type": "clear_lock_files",
  "playbook_id": "warm_cache",
  "tier": "tier_2",
  "status": "verified",
  "expected_effect": {
    "target_resource": "grace_backend",
    "target_state": {
      "status": "completed",
      "error_resolved": true
    },
    "success_criteria": [...]
  },
  "actual_effect": {
    "status": "completed",
    "error_resolved": true,
    "benchmark_passed": true,
    "error_rate": 0.02
  },
  "verification_result": {
    "confidence": 0.95,
    "success": true,
    "matches": [...]
  },
  "confidence_score": 0.95,
  "created_at": "2025-11-07T18:00:00Z",
  "executed_at": "2025-11-07T18:00:02Z",
  "verified_at": "2025-11-07T18:00:05Z",
  "snapshot_id": "snapshot-20251107-180000",
  "triggered_by": "input_sentinel:error-123"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/verification/contracts/contract-abc123"
```

---

### GET `/snapshots`

List safe-hold snapshots.

**Query Parameters**:
- `limit` (optional): Max results (default: 50, max: 500)
- `offset` (optional): Pagination offset (default: 0)
- `is_golden` (optional): Filter by golden status (boolean)

**Response**: `List[SnapshotSummary]`
```json
[
  {
    "id": "snapshot-20251107-180000",
    "snapshot_type": "pre_action",
    "status": "active",
    "is_golden": true,
    "created_at": "2025-11-07T18:00:00Z",
    "components_count": 3
  }
]
```

**Example**:
```bash
# Get only golden snapshots
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/verification/snapshots?is_golden=true"
```

---

### GET `/missions`

List missions with progression tracking.

**Query Parameters**:
- `limit` (optional): Max results (default: 50, max: 500)
- `offset` (optional): Pagination offset (default: 0)
- `status` (optional): Filter by status (`in_progress`, `completed`, `failed`)

**Response**: `List[MissionSummary]`
```json
[
  {
    "mission_id": "mission-recovery-123",
    "mission_name": "Database Recovery",
    "status": "completed",
    "progress_ratio": 1.0,
    "confidence_score": 0.92,
    "completed_actions": 5,
    "total_planned_actions": 5,
    "started_at": "2025-11-07T17:00:00Z",
    "completed_at": "2025-11-07T17:05:00Z"
  }
]
```

---

### GET `/missions/{mission_id}`

Get detailed mission status with all associated contracts.

**Path Parameters**:
- `mission_id` (required): Mission identifier

**Response**:
```json
{
  "mission_id": "mission-recovery-123",
  "mission_name": "Database Recovery",
  "mission_goal": "Resolve database lock and restore service",
  "status": "completed",
  "progress_ratio": 1.0,
  "confidence_score": 0.92,
  "completed_actions": 5,
  "total_planned_actions": 5,
  "started_at": "2025-11-07T17:00:00Z",
  "completed_at": "2025-11-07T17:05:00Z",
  "contracts": [
    {
      "id": "contract-abc123",
      "action_type": "clear_lock_files",
      "status": "verified",
      "confidence_score": 0.95,
      "created_at": "2025-11-07T17:00:01Z"
    }
  ]
}
```

---

### POST `/smoke-check`

Run comprehensive smoke checks on verification system.

**Response**:
```json
{
  "passed": true,
  "checks": {
    "tables_exist": true,
    "contracts_valid": true,
    "snapshots_valid": true,
    "missions_valid": true,
    "no_orphans": true
  },
  "errors": [],
  "timestamp": "2025-11-07T18:30:00.000Z",
  "message": "All checks passed"
}
```

**Checks Performed**:
1. All required tables exist
2. Contract table accessible
3. Snapshot table accessible
4. Mission table accessible
5. No orphaned foreign key references

---

### GET `/health`

Quick health check (no authentication required for monitoring).

**Response**:
```json
{
  "status": "healthy",
  "contracts_count": 142,
  "snapshots_count": 28,
  "missions_count": 15,
  "timestamp": "2025-11-07T18:30:00.000Z"
}
```

---

## Frontend Integration Guide

### React Hook Example

```typescript
// hooks/useVerificationStats.ts

import { useState, useEffect } from 'react';

interface VerificationStats {
  total_contracts: number;
  successful_contracts: number;
  success_rate: number;
  avg_confidence: number;
}

export function useVerificationStats(days: number = 7) {
  const [stats, setStats] = useState<VerificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('grace_token');
        const response = await fetch(
          `http://localhost:8000/api/verification/stats?days=${days}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        if (!response.ok) throw new Error('Failed to fetch stats');
        
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [days]);

  return { stats, loading, error };
}
```

### Component Example

```tsx
// components/VerificationDashboard.tsx

import { useVerificationStats } from '../hooks/useVerificationStats';

export function VerificationDashboard() {
  const { stats, loading, error } = useVerificationStats(7);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="verification-dashboard">
      <h2>Verification Statistics (Last 7 Days)</h2>
      
      <div className="stats-grid">
        <StatCard 
          label="Total Contracts" 
          value={stats.total_contracts} 
        />
        <StatCard 
          label="Success Rate" 
          value={`${stats.success_rate}%`}
          color={stats.success_rate > 90 ? 'green' : 'orange'}
        />
        <StatCard 
          label="Avg Confidence" 
          value={`${(stats.avg_confidence * 100).toFixed(1)}%`}
        />
      </div>
    </div>
  );
}
```

---

## Smoke Check Integration

### CI Pipeline

```bash
# In your CI script:

# 1. Start backend
python -m backend.main &
BACKEND_PID=$!

# 2. Wait for startup
sleep 5

# 3. Run smoke check
response=$(curl -s http://localhost:8000/api/verification/smoke-check \
  -H "Authorization: Bearer $TOKEN")

# 4. Check if passed
passed=$(echo $response | jq -r '.passed')
if [ "$passed" != "true" ]; then
  echo "Smoke check failed:"
  echo $response | jq '.errors'
  kill $BACKEND_PID
  exit 1
fi

echo "Smoke check passed!"

# 5. Cleanup
kill $BACKEND_PID
```

---

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "error": "validation_error",
  "message": "Request validation failed",
  "details": [...],
  "request_id": "req-abc123"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (missing/invalid token)
- `404` - Resource not found
- `422` - Validation error
- `500` - Internal server error (degraded response)

---

## Rate Limits

- **Default**: 100 requests/minute per user
- **Smoke check**: 10 requests/minute (monitoring)
- **Health check**: No limit (public endpoint)

---

## Versioning

API follows semantic versioning. Breaking changes will be announced with:
- New major version endpoint (e.g., `/api/v2/verification`)
- Deprecation notice (90 days minimum)
- Migration guide

**Current Version**: 1.0.0  
**Stability**: Production-ready

---

## Support

For issues or questions:
- Check [VERIFICATION_SYSTEM_LIVE.md](../VERIFICATION_SYSTEM_LIVE.md)
- Review [DATA_CUBE_WALKTHROUGH.md](DATA_CUBE_WALKTHROUGH.md)
- File issue in GitHub repository
