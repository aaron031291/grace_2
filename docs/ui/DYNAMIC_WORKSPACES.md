# Dynamic Workspaces - Deep Dive

## 🎯 Core Concept

**"When you ask Grace to open something, she spawns a dedicated tab/window. Close it when done - no impact on the main console."**

---

## 💡 Design Philosophy

### Lightweight & Disposable
- **No commitment** - Open a workspace to investigate, close when done
- **No state pollution** - Closing doesn't affect other workspaces or console
- **Fast spawn** - Sub-300ms to open any workspace
- **Minimal overhead** - Each workspace is lightweight, can have 10+ open

### Non-Blocking
- **Independent execution** - Each workspace runs independently
- **Close anytime** - No "save changes?" prompts
- **Background updates** - Workspaces update even when not focused
- **Parallel work** - Open multiple workspaces for different tasks

---

## 🚀 Workspace Spawning

### From Chat
```
User: "open CRM latency dashboard"
Grace: [spawns CRM Dashboard workspace]
      "Opening CRM latency dashboard..."
      
User: "show mission followup_abc123"
Grace: [spawns Mission Detail workspace]
      "Here's the mission detail..."

User: "debug memory leak in domain 8201"
Grace: [spawns Memory Domain Debug workspace]
      "Opening Memory Domain debugger..."
```

### From Task Manager
```
[User clicks mission card in Task Manager]
→ Spawns Mission Detail workspace
→ Shows full mission context
```

### From Command Palette
```
User: Cmd+K → types "dashboard"
→ Shows: "Open Dashboard: Memory, AI, Governance, ..."
→ Selects "Memory"
→ Spawns Memory Domain Dashboard workspace
```

### From Logs Pane
```
User: Clicks domain name in log entry
"[ERROR] Memory Domain: High latency detected"
       ^^^^^^^^^^^^^^
       [click here]
→ Spawns Memory Domain Dashboard workspace
```

---

## 🗂️ Workspace Types

### 1. Domain Dashboard
**Purpose**: Monitor specific domain (8200-8209)

**Spawned by**:
- "open dashboard [domain]"
- Click domain in logs
- Command palette

**Contains**:
- Health status (green/yellow/red)
- Real-time metrics
  - Requests/sec
  - Latency (p50, p95, p99)
  - Error rate
  - Active connections
- Recent activity graph (last hour)
- Recent errors
- Quick actions:
  - Restart domain
  - Trigger healing
  - View detailed logs
  - Open API docs

**API Endpoint**: `GET /api/domains/{id}/dashboard`

---

### 2. Mission Detail
**Purpose**: Deep dive into specific mission

**Spawned by**:
- "show mission [id]"
- Click mission card in Task Manager
- Command palette

**Contains**:
- Mission header
  - ID, Type (Active/Proactive/Follow-up)
  - Subsystem, Priority, Status
- Timeline view
  - When detected
  - When started
  - Actions taken (with timestamps)
  - When completed
- Remediation steps
  - What was broken
  - What Grace did
  - Tests run
  - Validation results
- KPI Comparison
  - Before/After metrics
  - Visual delta (↑↓)
- Related logs (filtered to this mission)
- Outcome summary (Grace's narrative)
- Quick actions:
  - Re-run mission
  - Mark for follow-up
  - Archive
  - Export report

**API Endpoint**: `GET /api/missions/{id}`

---

### 3. Code View
**Purpose**: View/edit code files

**Spawned by**:
- "show file [path]"
- "open code [function]"
- Click file reference in chat/mission

**Contains**:
- Monaco code editor
- Syntax highlighting
- Line numbers
- Go to line/function
- Search/replace
- Read-only or editable (configurable)
- Quick actions:
  - Save file
  - Run file
  - Git blame
  - Open in external editor

**API Endpoint**: `GET /api/files/content?path={path}`

---

### 4. Data Explorer
**Purpose**: Browse database, query results, knowledge base

**Spawned by**:
- "query database [table]"
- "search knowledge [topic]"
- Click data reference in chat

**Contains**:
- Table/tree view of data
- Column sorting
- Filtering
- Search
- Export to CSV/JSON
- Pagination
- Quick actions:
  - Run custom query
  - Refresh data
  - Download results

**API Endpoint**: `GET /api/data/query`

---

### 5. Chart/Metrics View
**Purpose**: Visualize time-series, trends, comparisons

**Spawned by**:
- "show latency trend"
- "compare memory usage"
- Click metric in dashboard

**Contains**:
- Interactive charts (Recharts/Chart.js)
- Time range selector
- Multiple series
- Zoom/pan
- Legend toggle
- Export to PNG/PDF
- Quick actions:
  - Change time range
  - Add/remove series
  - Switch chart type

**API Endpoint**: `GET /api/metrics/timeseries`

---

### 6. Approval Queue
**Purpose**: Review and grant approvals

**Spawned by**:
- "show pending approvals"
- Command palette → "Approvals"
- Notification click

**Contains**:
- List of pending approvals
  - Secret/credential name
  - Requesting service
  - Purpose/reason
  - Risk level
  - Requested time
- Approve/Deny buttons per item
- **"Approve All" button** (single approval)
- Approval history
- Quick actions:
  - Grant all
  - Deny all
  - Review individually

**API Endpoint**: `GET /api/secrets/consent/pending`

---

## 🎨 Workspace UI Design

### Tab Bar
```
┌─────────────────────────────────────────────────────────────┐
│ [Console] [CRM Dashboard] [Mission #123] [Memory Debug] [+] │
│                                                           [×] │
└─────────────────────────────────────────────────────────────┘
```

**Features**:
- Active tab highlighted
- Close button on each tab
- "+" button to spawn new workspace via command
- Drag to reorder
- Middle-click to close
- Favicon/icon per workspace type

### Workspace Content Area
```
┌─────────────────────────────────────────────────────────────┐
│  CRM Dashboard                                          [⚙️] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Health: 🟢 Healthy                                         │
│  Latency: 45ms (↓ 20% from 1h ago)                         │
│                                                              │
│  [Requests/sec chart - last 24h]                            │
│                                                              │
│  Recent Activity:                                            │
│  • 14:30 - POST /api/crm/contacts - 42ms                   │
│  • 14:29 - GET /api/crm/leads - 38ms                       │
│                                                              │
│  Quick Actions:                                              │
│  [Restart] [Heal] [View Logs] [API Docs]                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workspace State Management

### State Isolation
Each workspace maintains its own state:
```typescript
interface WorkspaceState {
  id: string;              // Unique workspace ID
  type: string;            // 'dashboard', 'mission', 'code', etc.
  title: string;           // Tab title
  data: any;               // Workspace-specific data
  lastUpdated: Date;       // Last data refresh
  isPinned: boolean;       // Pin to prevent auto-close
  preferences: any;        // User preferences for this workspace
}
```

### No Cross-Contamination
- Closing Workspace A doesn't affect Workspace B
- Each workspace fetches its own data
- No shared state between workspaces (except global theme/user)

### Optional Persistence
```typescript
// Save open workspaces to localStorage
localStorage.setItem('grace_workspaces', JSON.stringify(openWorkspaces));

// Restore on reload (optional, user can disable)
const savedWorkspaces = JSON.parse(localStorage.getItem('grace_workspaces'));
```

---

## 🎯 Implementation Examples

### Spawn CRM Dashboard
```typescript
// User types: "open CRM latency dashboard"

// Chat handler detects workspace spawn intent
const spawnIntent = parseUserMessage(userMessage);

if (spawnIntent.type === 'spawn_workspace') {
  // Create workspace
  const workspace = {
    id: generateId(),
    type: 'domain_dashboard',
    title: 'CRM Dashboard',
    domain: 'crm',
    port: 8200  // Core Domain
  };
  
  // Add to workspace manager
  workspaceManager.spawn(workspace);
  
  // Fetch data
  const data = await fetch(`/api/domains/crm/dashboard`);
  
  // Render in tab
  renderWorkspace(workspace, data);
}
```

### Spawn Mission Detail
```typescript
// User clicks mission card in Task Manager

const onMissionClick = async (missionId: string) => {
  // Create workspace
  const workspace = {
    id: generateId(),
    type: 'mission_detail',
    title: `Mission ${missionId}`,
    missionId: missionId
  };
  
  // Spawn
  workspaceManager.spawn(workspace);
  
  // Fetch mission data
  const data = await fetch(`/api/missions/${missionId}`);
  
  // Render
  renderMissionDetail(workspace, data);
};
```

### Close Workspace
```typescript
// User clicks [×] on tab

const onWorkspaceClose = (workspaceId: string) => {
  // Simply remove from workspace list
  workspaceManager.close(workspaceId);
  
  // No cleanup needed
  // No confirmation needed
  // Console continues running
  // Other workspaces unaffected
};
```

---

## 🎛️ Workspace Manager

### Core Logic
```typescript
class WorkspaceManager {
  private workspaces: Map<string, Workspace> = new Map();
  private maxWorkspaces = 20;  // Prevent memory issues
  
  spawn(config: WorkspaceConfig): Workspace {
    // Create workspace
    const workspace = new Workspace(config);
    
    // Add to collection
    this.workspaces.set(workspace.id, workspace);
    
    // Enforce limit (close oldest if over limit)
    if (this.workspaces.size > this.maxWorkspaces) {
      const oldest = this.getOldestUnpinned();
      this.close(oldest.id);
    }
    
    return workspace;
  }
  
  close(id: string): void {
    // Remove workspace
    const workspace = this.workspaces.get(id);
    
    if (workspace && !workspace.isPinned) {
      workspace.cleanup();  // Minimal cleanup
      this.workspaces.delete(id);
    }
  }
  
  getActive(): Workspace | null {
    // Return currently focused workspace
    return this.activeWorkspace;
  }
  
  getAll(): Workspace[] {
    return Array.from(this.workspaces.values());
  }
}
```

---

## 🔧 Workspace Features

### Auto-Refresh
```typescript
// Each workspace can auto-refresh its data
class Workspace {
  private refreshInterval?: NodeJS.Timer;
  
  startAutoRefresh(intervalMs: number = 5000) {
    this.refreshInterval = setInterval(() => {
      this.refreshData();
    }, intervalMs);
  }
  
  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
  
  async refreshData() {
    // Fetch latest data from API
    const data = await this.fetchData();
    this.updateUI(data);
  }
}
```

### Linking Between Workspaces
```typescript
// In Mission Detail workspace
<a onClick={() => spawnWorkspace({
  type: 'domain_dashboard',
  domain: mission.subsystem
})}>
  View {mission.subsystem} Dashboard
</a>

// In Domain Dashboard
<a onClick={() => spawnWorkspace({
  type: 'code_view',
  filePath: '/backend/routes/memory_api.py'
})}>
  View memory_api.py
</a>
```

---

## 📊 Example User Workflow

### Scenario: Investigating Memory Issue

**Step 1**: User sees in Logs Pane
```
🔴 [ERROR] Memory Domain: High memory usage detected (87%)
```

**Step 2**: User clicks "Memory Domain"
→ Spawns: **Memory Domain Dashboard** workspace

**Step 3**: Dashboard shows
- Memory usage: 87% (critical)
- Recent spike at 14:25
- Caused by: Large query in memory_api.py

**Step 4**: User clicks "View Code"
→ Spawns: **Code View** workspace (memory_api.py)

**Step 5**: User asks in Chat: "Fix this memory leak"
Grace: "I'll optimize the query. Creating mission..."
→ Task Manager shows: Mission #125 (In Progress)

**Step 6**: User clicks Mission #125
→ Spawns: **Mission Detail** workspace

**Step 7**: Mission completes
- Memory usage: 87% → 42%
- Tests passed: 5/5
- Mission Detail shows full remediation narrative

**Step 8**: User closes all workspaces
→ Main console unaffected
→ Clean workspace
→ Ready for next task

**Total workspaces opened**: 3 (Dashboard, Code, Mission)  
**Impact on console**: None - all lightweight and disposable

---

## 🎨 Visual Mockup

### Workspace in Action
```
┌──────────────────────────────────────────────────────────────┐
│  Grace Console                                               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  [Logs] [Chat] [Tasks]                                       │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  DYNAMIC WORKSPACES                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [Console] [CRM] [Mission #123] [Memory Debug]      [+] │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  CRM Dashboard (Active)                            [×] │ │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │ │
│  │                                                         │ │
│  │  🟢 Healthy | Latency: 45ms | Requests: 120/sec       │ │
│  │                                                         │ │
│  │  [Latency chart - last 24 hours]                       │ │
│  │   60ms ┤         ╭╮                                     │ │
│  │   45ms ┤    ╭────╯╰──╮                                 │ │
│  │   30ms ┤────╯        ╰────                             │ │
│  │        └─────────────────────                          │ │
│  │         12h ago      now                               │ │
│  │                                                         │ │
│  │  Recent Requests:                                       │ │
│  │  • 14:30:45 POST /api/crm/contact - 42ms - 200        │ │
│  │  • 14:30:43 GET /api/crm/leads - 38ms - 200          │ │
│  │                                                         │ │
│  │  [Restart Domain] [Trigger Healing] [View Full Logs]  │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technical Implementation

### Frontend Components
```typescript
// WorkspaceContainer.tsx
export const WorkspaceContainer = () => {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  
  const spawnWorkspace = (config: WorkspaceConfig) => {
    const workspace = createWorkspace(config);
    setWorkspaces([...workspaces, workspace]);
    setActiveId(workspace.id);
  };
  
  const closeWorkspace = (id: string) => {
    setWorkspaces(workspaces.filter(w => w.id !== id));
    if (activeId === id) {
      setActiveId(workspaces[0]?.id || null);
    }
  };
  
  return (
    <div className="workspace-container">
      <TabBar 
        workspaces={workspaces} 
        activeId={activeId}
        onTabClick={setActiveId}
        onTabClose={closeWorkspace}
      />
      
      <WorkspaceContent
        workspace={workspaces.find(w => w.id === activeId)}
      />
    </div>
  );
};
```

### Workspace Data Fetching
```typescript
// useDomainDashboard.ts
export const useDomainDashboard = (domainId: string) => {
  const { data, error, isLoading } = useQuery({
    queryKey: ['domain-dashboard', domainId],
    queryFn: () => fetch(`/api/domains/${domainId}/dashboard`).then(r => r.json()),
    refetchInterval: 5000  // Auto-refresh every 5s
  });
  
  return { dashboard: data, error, isLoading };
};
```

---

## 🎯 Key Benefits

### For Users
✅ **No context switching** - Everything in one window
✅ **Investigate freely** - Open workspaces without commitment
✅ **Clean closure** - Close tabs without side effects
✅ **Parallel investigation** - Multiple workspaces open simultaneously
✅ **Fast access** - Spawn workspace in <300ms

### For Development
✅ **Simple architecture** - Each workspace is independent
✅ **Easy to add** - New workspace type = new component
✅ **Testable** - Each workspace can be tested in isolation
✅ **Maintainable** - No complex state management
✅ **Performant** - Lazy loading, only active workspace renders

---

## 📋 Implementation Checklist

### Backend
- [ ] Create `/api/domains/{id}/dashboard` endpoint
- [ ] Create `/api/missions/{id}` detailed endpoint
- [ ] Create `/api/files/content` file viewer endpoint
- [ ] Create `/api/data/query` data explorer endpoint
- [ ] Create `/api/metrics/timeseries` chart data endpoint
- [ ] Ensure all endpoints return JSON

### Frontend
- [ ] Create `WorkspaceContainer` component
- [ ] Create `TabBar` component
- [ ] Create workspace type components:
  - [ ] `DomainDashboard`
  - [ ] `MissionDetail`
  - [ ] `CodeView`
  - [ ] `DataExplorer`
  - [ ] `ChartView`
  - [ ] `ApprovalQueue`
- [ ] Implement spawning logic
- [ ] Implement closing logic
- [ ] Add auto-refresh
- [ ] Add workspace linking

### Integration
- [ ] Wire chat commands to spawn workspaces
- [ ] Wire task manager clicks to spawn mission details
- [ ] Wire log clicks to spawn domain dashboards
- [ ] Wire command palette to spawn actions

---

**Status**: Dynamic Workspaces fully specified. Ready for implementation! 🚀
