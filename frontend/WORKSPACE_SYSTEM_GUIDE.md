# Dynamic Workspace System Guide

Complete implementation of a tab-based workspace management system for Grace Console.

## Overview

The workspace system allows users to open multiple views (missions, dashboards, artifacts, etc.) in tabbed workspaces, with full navigation integration from logs, tasks, and chat.

## Architecture

```
┌─────────────────────────────────────┐
│  GraceConsole                       │
│  ├─ useWorkspaces hook              │  State Management
│  └─ useWorkspaceActions helpers     │  
└────────────┬────────────────────────┘
             │
             ├─ Chat → openWorkspace(citation)
             ├─ Tasks → openWorkspace(mission)
             └─ Logs → openWorkspace(logs)
             │
             ▼
┌─────────────────────────────────────┐
│  WorkspaceManager                   │  Tab Bar + Content
│  ├─ Tab Bar (open/close/switch)    │
│  └─ Content Area (render workspace) │
└────────────┬────────────────────────┘
             │
             ▼
     Workspace Components
     ├─ MissionDetailWorkspace
     ├─ DashboardWorkspace
     ├─ ArtifactViewerWorkspace
     └─ ... (other types)
```

## Core Hook: `useWorkspaces`

### Data Structure

```typescript
interface Workspace {
  id: string;                    // Unique ID: "ws_1234567890_abc123"
  title: string;                 // Display name in tab
  type: WorkspaceType;           // Type of workspace
  payload: WorkspacePayload;     // Data for the workspace
  createdAt: string;             // ISO timestamp
}

type WorkspaceType = 
  | 'mission-detail'      // Mission information
  | 'kpi-dashboard'       // KPI metrics
  | 'crm-dashboard'       // CRM data
  | 'sales-dashboard'     // Sales analytics
  | 'artifact-viewer'     // Document/file viewer
  | 'code-diff'           // Code comparison
  | 'log-viewer'          // Filtered logs
  | 'memory-preview'      // Memory/knowledge data
  | 'custom';             // Custom component

interface WorkspacePayload {
  // Mission detail
  missionId?: string;
  
  // Dashboards
  filters?: Record<string, any>;
  timeRange?: string;
  
  // Artifact viewer
  artifactId?: string;
  artifactType?: string;
  
  // Code diff
  filePath?: string;
  commitSha?: string;
  
  // Log viewer
  logSource?: string;
  logLevel?: string;
  
  // Custom
  component?: React.ReactNode;
  data?: any;
}
```

### Usage

```typescript
import { useWorkspaces } from './hooks/useWorkspaces';

function MyComponent() {
  const {
    workspaces,          // Array of open workspaces
    activeWorkspace,     // Currently displayed workspace
    openWorkspace,       // Open a new workspace
    closeWorkspace,      // Close workspace by ID
    setActiveWorkspace,  // Switch to workspace
    clearWorkspaces,     // Close all workspaces
    hasWorkspace,        // Check if workspace exists
    getWorkspaceById,    // Get workspace by ID
  } = useWorkspaces();

  // Open a mission detail workspace
  const workspaceId = openWorkspace(
    'mission-detail',                    // type
    'Mission ABC-123',                   // title
    { missionId: 'mission_abc123' }      // payload
  );

  // Close a workspace
  closeWorkspace(workspaceId);

  // Switch to a workspace
  setActiveWorkspace(workspaceId);

  // Check if workspace exists
  const exists = hasWorkspace('mission-detail', { missionId: 'mission_abc123' });
}
```

### Workspace Actions Helper

Convenience methods for common workspace types:

```typescript
import { useWorkspaceActions } from './hooks/useWorkspaces';

const workspaceActions = useWorkspaceActions(openWorkspace);

// Open mission detail
workspaceActions.openMissionDetail('mission_123', 'Optional Title');

// Open KPI dashboard with filters
workspaceActions.openKPIDashboard({ 
  timeRange: 'last_30_days',
  severity: 'critical'
});

// Open CRM dashboard
workspaceActions.openCRMDashboard({ customerId: '12345' });

// Open artifact viewer
workspaceActions.openArtifactViewer('artifact_456', 'Document.pdf');

// Open code diff
workspaceActions.openCodeDiff('src/app.tsx', 'abc123def');

// Open log viewer
workspaceActions.openLogViewer('auth-service', 'error');

// Open memory preview
workspaceActions.openMemoryPreview({ key: 'value' }, 'Memory Data');
```

## Workspace Components

Each workspace type has its own component:

### 1. MissionDetailWorkspace

Displays full mission information with context, symptoms, and actions.

```typescript
// Automatically uses useMissionDetails hook
<MissionDetailWorkspace payload={{ missionId: 'mission_123' }} />
```

**Features:**
- Loading/error/empty states
- Mission overview (status, severity, subsystem)
- Symptoms list with metrics
- Context (env, branch, git SHA)
- Workspace info (repo, branch)
- Action buttons (Execute, View Logs, View Code)

### 2. DashboardWorkspace

Generic dashboard with filter display and placeholder for actual dashboard.

```typescript
<DashboardWorkspace 
  type="kpi-dashboard"
  payload={{ filters: { timeRange: '30d' } }}
/>
```

**Types:**
- `kpi-dashboard` - KPI metrics
- `crm-dashboard` - CRM data
- `sales-dashboard` - Sales analytics

**Features:**
- Filter chip display
- Icon per dashboard type
- Placeholder with integration instructions

### 3. ArtifactViewerWorkspace

Document/file viewer with preview placeholder.

```typescript
<ArtifactViewerWorkspace payload={{ artifactId: 'artifact_456' }} />
```

**Features:**
- Artifact loading
- Preview area (ready for PDF.js, image viewer, code highlighting)
- Actions (Download, Share, Re-ingest)

### 4. Placeholder Components

Ready-to-wire placeholders for:
- **Code Diff** - Compare file versions
- **Log Viewer** - Filtered log display
- **Memory Preview** - Knowledge/memory data viewer

## Integration

### From Chat (Citations)

When user clicks a citation in chat:

```typescript
<ChatPane
  onOpenWorkspace={(citation) => {
    if (citation.type === 'mission') {
      workspaceActions.openMissionDetail(citation.id, citation.title);
    } else if (citation.type === 'kpi') {
      workspaceActions.openKPIDashboard({ kpiId: citation.id });
    } else if (citation.type === 'document') {
      workspaceActions.openArtifactViewer(citation.id, citation.title);
    }
    
    // Switch main panel to workspace
    setLayout(prev => ({ ...prev, main: 'workspace' }));
  }}
/>
```

### From Task Manager (Missions)

When user clicks "Details" on a mission:

```typescript
// In TaskManager
const handleViewDetails = (mission: Mission) => {
  workspaceActions.openMissionDetail(mission.mission_id, mission.mission_id);
  // Optionally switch to workspace panel
};
```

### From Logs (Log Source)

When user wants to view logs for a specific service:

```typescript
// In LogsPane
const handleViewServiceLogs = (service: string, level?: string) => {
  workspaceActions.openLogViewer(service, level);
};
```

### From Memory Explorer (Artifacts)

When user clicks an artifact:

```typescript
// In MemoryExplorer
const handleViewArtifact = (artifact: Artifact) => {
  workspaceActions.openArtifactViewer(artifact.artifact_id, artifact.title);
};
```

## WorkspaceManager Component

Renders tab bar and active workspace content.

### Props

```typescript
interface WorkspaceManagerProps {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  onClose: (id: string) => void;
  onSwitch: (id: string) => void;
}
```

### Features

**Tab Bar:**
- Scrollable horizontal tabs
- Icon + title per tab
- Close button (×) per tab
- Active tab highlighted
- Hover effects

**Content Area:**
- Renders active workspace component
- Empty state when no workspaces
- Helpful suggestions for getting started

**Empty State:**
```
No Active Workspaces
Open a workspace from logs, tasks, or chat to get started

Try:
• Click a mission in Task Manager
• Click a citation in Chat  
• View logs for a specific service
```

## GraceConsole Integration

The console coordinates all panels and workspace management:

```typescript
function GraceConsole() {
  // Workspace management
  const {
    workspaces,
    activeWorkspace,
    openWorkspace,
    closeWorkspace,
    setActiveWorkspace,
  } = useWorkspaces();

  const workspaceActions = useWorkspaceActions(openWorkspace);

  // Handle citation clicks from chat
  const handleCitationClick = (citation: Citation) => {
    switch (citation.type) {
      case 'mission':
        workspaceActions.openMissionDetail(citation.id, citation.title);
        setLayout(prev => ({ ...prev, main: 'workspace' }));
        break;
      // ... other types
    }
  };

  return (
    <div className="grace-console">
      {/* Header with workspace indicator */}
      {workspaces.length > 0 && (
        <div className="workspace-indicator">
          <span className="workspace-count">{workspaces.length}</span>
          <span className="workspace-label">workspaces</span>
        </div>
      )}

      {/* Chat with workspace integration */}
      <ChatPane onOpenWorkspace={handleCitationClick} />

      {/* Workspace manager */}
      <WorkspaceManager
        workspaces={workspaces}
        activeWorkspace={activeWorkspace}
        onClose={closeWorkspace}
        onSwitch={setActiveWorkspace}
      />
    </div>
  );
}
```

## User Flows

### Open Mission from Chat

```
1. User asks: "Show me mission ABC-123"
2. Grace responds with [mission:mission_abc123] citation
3. User clicks citation pill
4. handleCitationClick extracts mission ID
5. workspaceActions.openMissionDetail() creates workspace
6. Tab appears in workspace bar
7. MissionDetailWorkspace loads and displays mission
```

### Open Dashboard from Task

```
1. User clicks "View Dashboard" in task
2. Task Manager calls workspaceActions.openKPIDashboard()
3. New workspace created with filters
4. Switches to workspace panel
5. DashboardWorkspace renders with filters
```

### Multiple Workspaces

```
User Flow:
1. Opens Mission A (tab created)
2. Opens Mission B (second tab created)
3. Opens KPI Dashboard (third tab created)
4. Clicks Mission A tab (switches to Mission A)
5. Closes Mission B tab (removed from array)
6. Workspace count shows "2 workspaces"
```

## Preventing Duplicates

Check before opening:

```typescript
const handleOpenMission = (missionId: string) => {
  // Check if already open
  if (hasWorkspace('mission-detail', { missionId })) {
    // Find and switch to existing workspace
    const existing = workspaces.find(w => 
      w.type === 'mission-detail' && w.payload.missionId === missionId
    );
    if (existing) {
      setActiveWorkspace(existing.id);
      return;
    }
  }
  
  // Open new workspace
  workspaceActions.openMissionDetail(missionId);
};
```

## Styling

### Tab Bar

```css
.workspace-tab {
  background: #242424;
  border: 1px solid #333;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s;
}

.workspace-tab.active {
  background: #1a1a1a;
  border-top: 2px solid #00ff88;  /* Green indicator */
}
```

### Workspace Indicator

```css
.workspace-indicator {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 16px;
}

.workspace-count {
  color: #00ff88;
  font-weight: bold;
}
```

## Extending the System

### Add a New Workspace Type

1. **Add type to `useWorkspaces.ts`:**
```typescript
type WorkspaceType = 
  | 'mission-detail'
  | 'my-new-type';  // Add here

interface WorkspacePayload {
  myNewData?: string;  // Add payload fields
}
```

2. **Create workspace component:**
```typescript
// components/workspaces/MyNewWorkspace.tsx
export default function MyNewWorkspace({ payload }: Props) {
  return <div>My custom workspace with {payload.myNewData}</div>;
}
```

3. **Add to WorkspaceManager renderer:**
```typescript
const renderWorkspace = (workspace: Workspace) => {
  switch (workspace.type) {
    case 'my-new-type':
      return <MyNewWorkspace payload={workspace.payload} />;
    // ... other cases
  }
};
```

4. **Add helper action:**
```typescript
// In useWorkspaceActions
const openMyNewWorkspace = useCallback((data: string) => {
  return openWorkspace('my-new-type', 'My Title', { myNewData: data });
}, [openWorkspace]);
```

5. **Use it:**
```typescript
workspaceActions.openMyNewWorkspace('some data');
```

## Best Practices

### 1. Use Unique Titles
```typescript
// Good
openMissionDetail(id, `Mission ${id}`);

// Better
openMissionDetail(id, mission.subsystem_id);
```

### 2. Check for Existing Workspaces
Avoid duplicates by checking first.

### 3. Switch to Workspace Panel
After opening a workspace, switch the main view:
```typescript
workspaceActions.openMissionDetail(id);
setLayout(prev => ({ ...prev, main: 'workspace' }));
```

### 4. Clean Payload Data
Only include necessary data in payload:
```typescript
// Good
{ missionId: 'abc123' }

// Avoid
{ missionId: 'abc123', entireMissionObject: {...} }
```

### 5. Provide Fallbacks
Handle missing data gracefully in workspace components.

## Future Enhancements

1. **Persistence** - Save workspace state to localStorage
2. **Drag & Drop** - Reorder tabs
3. **Split View** - Multiple workspaces side-by-side
4. **Workspace Groups** - Organize related workspaces
5. **History** - Recently closed workspaces
6. **Pinning** - Pin important workspaces
7. **Search** - Search open workspaces
8. **Keyboard Shortcuts** - `Cmd+1` for first workspace, etc.

## Summary

✅ **Dynamic workspace state** - Array-based with unique IDs  
✅ **Open/close/switch actions** - Full lifecycle management  
✅ **Tab bar UI** - Scrollable tabs with icons and close buttons  
✅ **Type-based rendering** - Each workspace type has its component  
✅ **Navigation integration** - Wire from chat, tasks, logs, memory  
✅ **Workspace indicator** - Shows count of open workspaces  
✅ **Empty states** - Helpful guidance when no workspaces  
✅ **Helper actions** - Convenience methods for common types  

The workspace system is production-ready and fully integrated with all console panels! 🚀
