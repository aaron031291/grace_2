# Data Hooks & Services Architecture

Complete implementation of a clean data layer for Mission Control with React hooks, proper state management, and comprehensive error handling.

## Architecture Overview

```
┌─────────────────┐
│  Component      │  TaskManager.tsx
│  (UI Logic)     │  - Renders UI
└────────┬────────┘  - Handles user interactions
         │
         ▼
┌─────────────────┐
│  Custom Hook    │  useMissions.ts
│  (State Mgmt)   │  - Manages state
└────────┬────────┘  - Auto-refresh logic
         │            - Optimistic updates
         ▼
┌─────────────────┐
│  API Service    │  missionApi.ts
│  (HTTP Layer)   │  - API calls
└─────────────────┘  - Error handling
         │            - Type safety
         ▼
    Backend API
```

## 1. API Service Layer

**File:** `frontend/src/services/missionApi.ts`

### Features
- ✅ Centralized API endpoint definitions
- ✅ Type-safe request/response interfaces
- ✅ Custom error handling with `MissionApiError`
- ✅ Authentication header management
- ✅ Query parameter building

### API Functions

```typescript
// Fetch missions with filters
fetchMissions(filters?: MissionFilters): Promise<MissionsResponse>

// Get single mission details
fetchMissionDetails(missionId: string): Promise<MissionDetail>

// Execute a mission
executeMission(missionId: string, missionType?: 'coding' | 'healing'): Promise<any>

// Acknowledge mission
acknowledgeMission(missionId: string): Promise<any>

// Get system status
fetchMissionControlStatus(): Promise<any>

// Get subsystem health
fetchSubsystemHealth(): Promise<any>

// Create mission
createMission(missionData: any): Promise<any>

// Preventive missions
createPreventiveMission(relatedMissionId: string): Promise<any>
```

### Type Definitions

```typescript
interface Mission {
  mission_id: string;
  subsystem_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'awaiting_validation' | 'observing' | 'resolved' | 'escalated' | 'failed';
  detected_by: string;
  assigned_to: string;
  created_at: string;
  updated_at: string;
  symptoms_count?: number;
  remediation_events_count?: number;
}

interface MissionDetail extends Mission {
  context?: { /* ... */ };
  symptoms?: Array<{ /* ... */ }>;
  workspace?: { /* ... */ };
  acceptance_criteria?: { /* ... */ };
  remediation_history?: Array<{ /* ... */ }>;
  kpi_deltas?: Record<string, number>;
}

interface MissionFilters {
  status?: string;
  subsystem_id?: string;
  severity?: string;
  limit?: number;
}
```

### Error Handling

```typescript
class MissionApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'MissionApiError';
  }
}

// Usage
try {
  await fetchMissions();
} catch (error) {
  if (error instanceof MissionApiError) {
    console.error(`API error ${error.status}:`, error.message);
  }
}
```

### Configuration

Set API base URL via environment variable:
```bash
VITE_API_BASE=http://localhost:8017
```

Or it defaults to `http://localhost:8017`

## 2. React Hooks

**File:** `frontend/src/hooks/useMissions.ts`

### `useMissions` Hook

The main hook for fetching and managing missions.

#### Features
- ✅ Auto-refresh with configurable interval (default 30s)
- ✅ Loading, error, and empty states
- ✅ Optimistic UI updates
- ✅ Filter management
- ✅ Action handlers (execute, acknowledge)
- ✅ Silent background refreshes

#### Usage

```typescript
import { useMissions } from '../hooks/useMissions';

function MyComponent() {
  const {
    // Data
    missions,
    total,
    
    // State
    loading,
    error,
    isEmpty,
    
    // Actions
    refresh,
    executeMission,
    acknowledgeMission,
    getMissionDetails,
    
    // Config
    setFilters,
    setAutoRefresh,
  } = useMissions({
    filters: {
      severity: 'critical',
      subsystem_id: 'crm',
      limit: 50
    },
    autoRefresh: true,
    refreshInterval: 30000, // 30 seconds
    onError: (error) => {
      console.error('Mission error:', error);
      // Show toast notification, etc.
    }
  });

  return (
    <div>
      {loading && <Spinner />}
      {error && <ErrorMessage error={error} />}
      {isEmpty && <EmptyState />}
      {missions.map(m => <MissionCard key={m.mission_id} mission={m} />)}
    </div>
  );
}
```

#### Options

```typescript
interface UseMissionsOptions {
  filters?: MissionFilters;          // Initial filters
  autoRefresh?: boolean;             // Enable auto-refresh (default: true)
  refreshInterval?: number;          // Refresh interval in ms (default: 30000)
  onError?: (error: Error) => void;  // Error callback
}
```

#### Return Value

```typescript
interface UseMissionsResult {
  // Data
  missions: Mission[];        // Array of missions
  total: number;             // Total count
  
  // State
  loading: boolean;          // Loading state
  error: Error | null;       // Error if any
  isEmpty: boolean;          // True if no missions and not loading
  
  // Actions
  refresh: () => Promise<void>;                                    // Manual refresh
  executeMission: (id: string, type?: 'coding' | 'healing') => Promise<void>;  // Execute mission
  acknowledgeMission: (id: string) => Promise<void>;               // Acknowledge mission
  getMissionDetails: (id: string) => Promise<MissionDetail | null>; // Get details
  
  // Config
  setFilters: (filters: MissionFilters) => void;  // Update filters
  setAutoRefresh: (enabled: boolean) => void;     // Toggle auto-refresh
}
```

### `useMissionDetails` Hook

For fetching a single mission's details.

```typescript
import { useMissionDetails } from '../hooks/useMissions';

function MissionDetailPanel({ missionId }: { missionId: string | null }) {
  const { mission, loading, error, refresh } = useMissionDetails(missionId);

  if (loading) return <Spinner />;
  if (error) return <Error error={error} />;
  if (!mission) return null;

  return <div>{/* Render mission details */}</div>;
}
```

### `useMissionStats` Hook

Compute statistics from missions array.

```typescript
import { useMissionStats } from '../hooks/useMissions';

function MissionStats({ missions }: { missions: Mission[] }) {
  const stats = useMissionStats(missions);

  return (
    <div>
      <div>Total: {stats.total}</div>
      <div>Open: {stats.byStatus.open || 0}</div>
      <div>In Progress: {stats.byStatus.in_progress || 0}</div>
      <div>Critical: {stats.bySeverity.critical || 0}</div>
    </div>
  );
}
```

Returns:
```typescript
{
  total: number;
  byStatus: Record<string, number>;
  bySeverity: Record<string, number>;
  bySubsystem: Record<string, number>;
}
```

## 3. Component Integration

The refactored `TaskManager` demonstrates all these features:

### Loading State
```typescript
if (loading && missions.length === 0) {
  return (
    <div className="loading-state">
      <div className="loading-spinner"></div>
      <p>Loading missions...</p>
    </div>
  );
}
```

### Error State
```typescript
if (error && missions.length === 0) {
  return (
    <div className="error-state">
      <div className="error-icon">⚠️</div>
      <h3>Failed to load missions</h3>
      <p className="error-message">{error.message}</p>
      <button onClick={() => refresh()} className="retry-btn">
        Retry
      </button>
    </div>
  );
}
```

### Empty State
```typescript
if (isEmpty) {
  return (
    <div className="empty-state">
      <div className="empty-icon">🎯</div>
      <h3>No missions found</h3>
      <p>
        {filterSeverity || filterSubsystem 
          ? 'Try adjusting your filters'
          : 'All systems running smoothly'}
      </p>
    </div>
  );
}
```

### Error Banner (Partial Errors)
Shows errors without blocking the UI when there are existing missions:

```typescript
{error && (
  <div className="error-banner">
    <span className="error-icon">⚠️</span>
    <span>{error.message}</span>
    <button onClick={() => refresh()} className="dismiss-btn">Retry</button>
  </div>
)}
```

### Optimistic Updates

The hook automatically handles optimistic updates:

```typescript
// When you call executeMission:
await executeMission(missionId);

// Internally:
// 1. Optimistically update UI (status → 'in_progress')
// 2. Call API
// 3. Refresh to get server state
// 4. On error: revert optimistic update
```

No manual state manipulation needed!

## 4. State Management Flow

### Initial Load
```
1. Component mounts
2. useMissions hook initializes
3. Calls fetchMissions()
4. Sets loading = true
5. Fetches data from API
6. Updates missions state
7. Sets loading = false
```

### Auto-Refresh
```
1. Timer triggers (every 30s)
2. Calls refresh(false)  // false = silent (no loading spinner)
3. Fetches latest data
4. Updates missions state
5. UI re-renders with new data
```

### User Action (Execute Mission)
```
1. User clicks "Execute"
2. Component calls executeMission(id)
3. Hook optimistically updates mission status
4. UI immediately reflects change
5. API call is made
6. On success: refresh to get server state
7. On error: revert optimistic update & show error
```

### Filter Change
```
1. User changes filter
2. Component calls setFilters({ severity: 'critical' })
3. Hook triggers refresh with new filters
4. Fetches filtered data
5. Updates missions state
```

## 5. Benefits

### Code Reusability
Use the same hook across multiple components:
```typescript
// In TaskManager
const { missions } = useMissions({ filters: { status: 'open' } });

// In Dashboard
const { missions: critical } = useMissions({ filters: { severity: 'critical' } });

// In Sidebar
const { total } = useMissions({ autoRefresh: true });
```

### Separation of Concerns
- **Components:** Pure UI rendering
- **Hooks:** State management & business logic
- **Services:** HTTP requests & data transformation

### Type Safety
Full TypeScript support throughout the stack:
```typescript
const mission: Mission = missions[0];
const status: Mission['status'] = mission.status;  // Type-safe!
```

### Error Handling
Centralized error handling with custom error types:
```typescript
try {
  await executeMission(id);
} catch (error) {
  if (error instanceof MissionApiError) {
    // Handle API errors
  } else {
    // Handle other errors
  }
}
```

### Testing
Easy to test each layer independently:

```typescript
// Test service
import { fetchMissions } from './services/missionApi';
test('fetchMissions returns missions', async () => {
  const data = await fetchMissions();
  expect(data.missions).toBeArray();
});

// Test hook
import { renderHook } from '@testing-library/react-hooks';
import { useMissions } from './hooks/useMissions';
test('useMissions loads data', async () => {
  const { result, waitForNextUpdate } = renderHook(() => useMissions());
  await waitForNextUpdate();
  expect(result.current.loading).toBe(false);
});
```

## 6. Best Practices

### 1. Always handle loading states
```typescript
if (loading) return <Spinner />;
```

### 2. Always handle errors
```typescript
if (error) return <ErrorMessage error={error} />;
```

### 3. Always handle empty states
```typescript
if (isEmpty) return <EmptyState />;
```

### 4. Use silent refreshes for background updates
```typescript
refresh(false);  // No loading spinner
```

### 5. Provide error callbacks for user feedback
```typescript
useMissions({
  onError: (error) => {
    toast.error(error.message);
  }
});
```

### 6. Clean up on unmount
The hook automatically cleans up timers and subscriptions.

## 7. Future Enhancements

### WebSocket Support
Replace polling with WebSocket for real-time updates:

```typescript
// In useMissions hook
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8017/mission-control/stream');
  ws.onmessage = (event) => {
    const mission = JSON.parse(event.data);
    setMissions(prev => [...prev, mission]);
  };
  return () => ws.close();
}, []);
```

### Caching with React Query
For advanced caching and deduplication:

```typescript
import { useQuery } from '@tanstack/react-query';

function useMissions(filters) {
  return useQuery({
    queryKey: ['missions', filters],
    queryFn: () => fetchMissions(filters),
    refetchInterval: 30000,
  });
}
```

### Infinite Scroll
Load more missions as user scrolls:

```typescript
function useMissionsPaginated(pageSize = 50) {
  const [page, setPage] = useState(0);
  const { missions } = useMissions({
    filters: { limit: pageSize, offset: page * pageSize }
  });
  
  const loadMore = () => setPage(p => p + 1);
  return { missions, loadMore };
}
```

## 8. Migration Guide

### Before (Direct API calls in component)
```typescript
function TaskManager() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    setLoading(true);
    fetch('/api/missions')
      .then(r => r.json())
      .then(setMissions)
      .finally(() => setLoading(false));
  }, []);
  
  return /* JSX */;
}
```

### After (Using hook)
```typescript
function TaskManager() {
  const { missions, loading, error, isEmpty } = useMissions();
  
  if (loading) return <Spinner />;
  if (error) return <Error error={error} />;
  if (isEmpty) return <Empty />;
  
  return /* JSX */;
}
```

Much cleaner, more maintainable, and feature-rich!

## Summary

✅ **Service Layer** - Clean API abstraction with type safety  
✅ **Custom Hooks** - Reusable state management logic  
✅ **Loading States** - Spinner during initial load  
✅ **Error States** - Retry button and error messages  
✅ **Empty States** - Helpful messaging when no data  
✅ **Auto-refresh** - Configurable background polling  
✅ **Optimistic Updates** - Instant UI feedback  
✅ **Filter Management** - Dynamic query parameter handling  
✅ **Type Safety** - Full TypeScript support  
✅ **Error Handling** - Centralized with custom error types  

The Task Manager now has production-quality data fetching with all the features you'd expect from a modern React application!
