# Unified Console - Implementation Roadmap

**Goal**: Build Grace's unified console in 4 weeks with incremental delivery

---

## 🎯 Phase 1: Three-Pane Layout (Week 1)

### Objective
Set up the core layout with logs, chat, and task manager using placeholder data

### Tasks

#### 1.1 Project Setup
- [ ] Create React/Svelte project in `frontend/console/`
```bash
cd frontend
npx create-react-app console --template typescript
cd console
npm install tailwindcss @tailwindcss/typography
npm install react-split-pane socket.io-client
npm install @tanstack/react-query zustand
```

- [ ] Configure Tailwind CSS
- [ ] Set up project structure
```
frontend/console/src/
├── components/
│   ├── Console/
│   │   ├── ConsoleLayout.tsx
│   │   ├── LogsPane.tsx
│   │   ├── ChatPane.tsx
│   │   └── TaskManagerPane.tsx
│   └── Shared/
│       ├── Button.tsx
│       ├── Card.tsx
│       └── Badge.tsx
├── hooks/
├── api/
├── types/
└── App.tsx
```

---

#### 1.2 Build ConsoleLayout Component
- [ ] Create three-pane split layout
- [ ] Use `react-split-pane` for resizable panels
- [ ] Ensure each pane scrolls independently
- [ ] Make responsive (adapts to screen sizes)
  - [ ] Desktop: 3 columns (30% | 40% | 30%)
  - [ ] Tablet: 2 columns + collapsible sidebar
  - [ ] Mobile: Tabs between panes

**Implementation**:
```typescript
// ConsoleLayout.tsx
import SplitPane from 'react-split-pane';

export const ConsoleLayout = () => {
  return (
    <div className="console-layout h-screen">
      <SplitPane
        split="vertical"
        defaultSize="30%"
        minSize={200}
        maxSize={-200}
      >
        {/* Logs Pane */}
        <LogsPane />
        
        <SplitPane
          split="vertical"
          defaultSize="60%"
          minSize={300}
        >
          {/* Chat Pane */}
          <ChatPane />
          
          {/* Task Manager Pane */}
          <TaskManagerPane />
        </SplitPane>
      </SplitPane>
    </div>
  );
};
```

---

#### 1.3 Build LogsPane with Placeholder Data
- [ ] Create scrollable log container
- [ ] Add color-coding for log levels
  - [ ] 🟢 Green: Success/OK
  - [ ] 🟡 Yellow: Warning
  - [ ] 🔴 Red: Error
  - [ ] 🔵 Blue: Info
- [ ] Add filter controls
  - [ ] Filter by level
  - [ ] Filter by domain
  - [ ] Search/grep
- [ ] Add auto-scroll toggle
- [ ] Use placeholder log data

**Placeholder Data**:
```typescript
const PLACEHOLDER_LOGS = [
  { level: 'success', message: '[OK] Mission #123 completed', timestamp: '10:30:15', domain: 'memory' },
  { level: 'warning', message: '[WARN] High latency detected (120ms)', timestamp: '10:30:18', domain: 'ai' },
  { level: 'error', message: '[ERROR] Connection timeout', timestamp: '10:30:20', domain: 'integration' },
  { level: 'info', message: '[INFO] Processing request...', timestamp: '10:30:22', domain: 'core' },
];
```

---

#### 1.4 Build ChatPane with Placeholder
- [ ] Create message list (scrollable)
- [ ] Create input area
  - [ ] Text input field
  - [ ] Send button
  - [ ] Attach button (placeholder)
  - [ ] Voice button (placeholder)
- [ ] Add message bubbles
  - [ ] User messages (right-aligned)
  - [ ] Grace messages (left-aligned)
  - [ ] Markdown rendering
  - [ ] Code syntax highlighting
- [ ] Handle Enter key to send
- [ ] Use placeholder conversation

**Placeholder Data**:
```typescript
const PLACEHOLDER_CHAT = [
  { from: 'user', text: 'How is the memory domain doing?', timestamp: '10:25' },
  { from: 'grace', text: 'Memory domain is healthy. Latency is 45ms (↓20% from 1h ago).', timestamp: '10:25' },
  { from: 'user', text: 'Show me the dashboard', timestamp: '10:26' },
  { from: 'grace', text: 'Opening Memory Domain dashboard...', timestamp: '10:26' },
];
```

---

#### 1.5 Build TaskManagerPane with Placeholder
- [ ] Create mission cards
  - [ ] Mission ID
  - [ ] Status badge (Active, Completed, Failed)
  - [ ] Subsystem
  - [ ] KPI delta
  - [ ] Timestamp
  - [ ] Click handler (placeholder)
- [ ] Add tabs for mission types
  - [ ] Active
  - [ ] Proactive
  - [ ] Follow-ups
- [ ] Use placeholder mission data

**Placeholder Data**:
```typescript
const PLACEHOLDER_MISSIONS = [
  {
    id: 'mission_123',
    type: 'active',
    status: 'completed',
    subsystem: 'memory_domain',
    title: 'Fix memory leak',
    kpi_delta: -45,
    kpi_unit: '%',
    started: '10:15',
    completed: '10:30'
  },
  {
    id: 'mission_124',
    type: 'proactive',
    status: 'in_progress',
    subsystem: 'ai_domain',
    title: 'Optimize latency',
    kpi_delta: null,
    started: '10:28'
  },
];
```

---

#### 1.6 Responsive Design
- [ ] Desktop layout (3 columns)
- [ ] Tablet layout (2 columns + drawer)
- [ ] Mobile layout (tabs)
- [ ] Test on different screen sizes
- [ ] Ensure smooth transitions

---

### Phase 1 Deliverable
✅ **Working three-pane layout with placeholder data**
- Logs pane shows mock logs with color-coding
- Chat pane accepts input and shows mock conversation
- Task Manager shows mock missions
- All panes scroll independently
- Responsive on desktop/tablet/mobile

**Demo-able**: Yes (with static data)

---

## 🪟 Phase 2: Dynamic Workspaces (Week 2)

### Objective
Add tab strip and workspace spawning flow

### Tasks

#### 2.1 Build Workspace Infrastructure
- [ ] Create `WorkspaceManager` state management
```typescript
// stores/workspaceStore.ts
import create from 'zustand';

interface WorkspaceState {
  workspaces: Workspace[];
  activeId: string | null;
  spawn: (config: WorkspaceConfig) => void;
  close: (id: string) => void;
  setActive: (id: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  workspaces: [],
  activeId: null,
  
  spawn: (config) => set((state) => {
    const workspace = createWorkspace(config);
    return {
      workspaces: [...state.workspaces, workspace],
      activeId: workspace.id
    };
  }),
  
  close: (id) => set((state) => ({
    workspaces: state.workspaces.filter(w => w.id !== id),
    activeId: state.activeId === id ? state.workspaces[0]?.id : state.activeId
  })),
  
  setActive: (id) => set({ activeId: id })
}));
```

---

#### 2.2 Build Tab Strip
- [ ] Create `TabBar` component
  - [ ] Tab for each workspace
  - [ ] Active tab highlighted
  - [ ] Close button (×) per tab
  - [ ] "+" button to spawn new
  - [ ] Drag to reorder
- [ ] Add tab icons based on workspace type
- [ ] Implement tab switching
- [ ] Add middle-click to close

**Implementation**:
```typescript
// TabBar.tsx
export const TabBar = () => {
  const { workspaces, activeId, setActive, close } = useWorkspaceStore();
  
  return (
    <div className="tab-bar">
      {workspaces.map(workspace => (
        <div
          key={workspace.id}
          className={`tab ${activeId === workspace.id ? 'active' : ''}`}
          onClick={() => setActive(workspace.id)}
        >
          <span className="tab-icon">{workspace.icon}</span>
          <span className="tab-title">{workspace.title}</span>
          <button 
            className="tab-close"
            onClick={(e) => {
              e.stopPropagation();
              close(workspace.id);
            }}
          >
            ×
          </button>
        </div>
      ))}
      
      <button className="tab-new" onClick={openSpawnDialog}>
        +
      </button>
    </div>
  );
};
```

---

#### 2.3 Build WorkspaceContainer
- [ ] Create `WorkspaceContainer` component
- [ ] Render active workspace
- [ ] Handle workspace switching
- [ ] Show loading states
- [ ] Handle errors

**Implementation**:
```typescript
// WorkspaceContainer.tsx
export const WorkspaceContainer = () => {
  const { workspaces, activeId } = useWorkspaceStore();
  
  const activeWorkspace = workspaces.find(w => w.id === activeId);
  
  if (!activeWorkspace) {
    return <EmptyState />;
  }
  
  return (
    <div className="workspace-container">
      <WorkspaceRenderer workspace={activeWorkspace} />
    </div>
  );
};

const WorkspaceRenderer = ({ workspace }) => {
  const Component = WORKSPACE_COMPONENTS[workspace.type];
  return <Component config={workspace.config} />;
};
```

---

#### 2.4 Wire "Open CRM Dashboard" Button
- [ ] Add test button in chat pane: "Open CRM Dashboard"
- [ ] Click spawns workspace with mock CRM data
- [ ] Verify tab appears
- [ ] Verify tab switching works
- [ ] Verify close works
- [ ] Prove the flow end-to-end

**Implementation**:
```typescript
// In ChatPane.tsx
const handleOpenDashboard = () => {
  spawn({
    type: 'domain_dashboard',
    title: 'CRM Dashboard',
    config: {
      domain: 'core',
      port: 8200,
      mockData: MOCK_CRM_DASHBOARD_DATA
    }
  });
};

// Add button
<button onClick={handleOpenDashboard}>
  📊 Open CRM Dashboard (Test)
</button>
```

---

#### 2.5 Build Mock Dashboard Workspace
- [ ] Create `DomainDashboard` component (placeholder)
- [ ] Show mock metrics
  - [ ] Health indicator
  - [ ] Latency
  - [ ] Requests/sec
  - [ ] Error count
- [ ] Add mock chart
- [ ] Add "Close" button

**Mock Data**:
```typescript
const MOCK_CRM_DASHBOARD_DATA = {
  health: 'healthy',
  latency_ms: 45,
  requests_per_sec: 120,
  error_count: 0,
  last_24h: [
    { time: '00:00', latency: 50 },
    { time: '06:00', latency: 48 },
    { time: '12:00', latency: 45 },
    { time: '18:00', latency: 43 },
  ]
};
```

---

### Phase 2 Deliverable
✅ **Dynamic workspaces working with mock data**
- Tab bar shows/switches workspaces
- "Open CRM Dashboard" button spawns workspace
- Workspace displays mock metrics
- Close tab works correctly
- Flow proven end-to-end

**Demo-able**: Yes (workspace spawning proven)

---

## 🔌 Phase 3: Data Wiring (Week 2-3)

### Objective
Replace placeholder data with live feeds from backend

### Tasks

#### 3.1 Wire Logs to Real Data
- [ ] Create `/api/logs/recent` endpoint (backend)
```python
# backend/routes/logs_api.py

@router.get("/api/logs/recent")
async def get_recent_logs(limit: int = 100, level: str = None, domain: str = None):
    """Get recent log entries"""
    # Pull from trigger mesh or log aggregator
    return {"logs": [...]}
```

- [ ] Create WebSocket endpoint for live logs (backend)
```python
@app.websocket("/ws/logs")
async def logs_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe to domain event bus
    async for event in domain_event_bus.subscribe('*'):
        await websocket.send_json({
            'level': event.severity,
            'message': event.message,
            'timestamp': event.timestamp,
            'domain': event.source_domain
        })
```

- [ ] Create `useLogsWebSocket` hook (frontend)
```typescript
// hooks/useLogsWebSocket.ts
export const useLogsWebSocket = () => {
  const [logs, setLogs] = useState<Log[]>([]);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8017/ws/logs');
    
    ws.onmessage = (event) => {
      const log = JSON.parse(event.data);
      setLogs(prev => [log, ...prev].slice(0, 1000));  // Keep last 1000
    };
    
    return () => ws.close();
  }, []);
  
  return logs;
};
```

- [ ] Replace placeholder logs with live data
- [ ] Test real-time log streaming
- [ ] Verify filters work with live data

---

#### 3.2 Wire Tasks to Mission Control API
- [ ] Ensure `/api/missions/active` endpoint exists (backend)
- [ ] Ensure `/api/missions/followups` endpoint exists (backend)
- [ ] Create WebSocket for mission updates (backend)
```python
@app.websocket("/ws/missions")
async def missions_websocket(websocket: WebSocket):
    await websocket.accept()
    
    async for event in domain_event_bus.subscribe('mission.*'):
        await websocket.send_json({
            'mission_id': event.data.get('mission_id'),
            'status': event.data.get('status'),
            'type': event.event_type
        })
```

- [ ] Create `useMissions` hook (frontend)
```typescript
// hooks/useMissions.ts
export const useMissions = () => {
  return useQuery({
    queryKey: ['missions', 'active'],
    queryFn: async () => {
      const response = await fetch('/api/missions/active');
      return response.json();
    },
    refetchInterval: 5000
  });
};
```

- [ ] Replace placeholder missions with live data
- [ ] Add WebSocket for real-time updates
- [ ] Test mission status changes in real-time

---

#### 3.3 Wire Chat to AI Domain
- [ ] Create `/api/chat/send` endpoint (backend)
```python
@router.post("/api/chat/send")
async def send_chat_message(message: str, user_id: str):
    """Send message to Grace and get response"""
    # Route to AI Domain (8202)
    response = await ai_domain.chat(message, user_id)
    return {"response": response}
```

- [ ] Create `useChatSend` hook (frontend)
```typescript
export const useChatSend = () => {
  return useMutation({
    mutationFn: async (message: string) => {
      const response = await fetch('/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, user_id: 'admin' })
      });
      return response.json();
    }
  });
};
```

- [ ] Replace placeholder chat with live AI responses
- [ ] Add streaming support for LLM responses
- [ ] Show "Grace is typing..." indicator

---

### Phase 3 Deliverable
✅ **Live data flowing through all panes**
- Logs stream in real-time from backend
- Tasks pull from Mission Control API
- Chat sends to AI domain and gets real responses
- No more placeholder data

**Demo-able**: Yes (fully functional with real Grace)

---

## 📂 Phase 4: Memory Explorer (Week 3)

### Objective
Build knowledge artifact explorer integrated with dynamic workspaces

### Tasks (Organized by Component)

#### 4.1 Build Explorer Shell
- [ ] Create `FileExplorer` component
- [ ] Build sidebar with category tree
  - [ ] Fetch from `/api/knowledge/categories`
  - [ ] Show file counts per category
  - [ ] Expand/collapse nested categories
- [ ] Build artifact list
  - [ ] Fetch from `/api/knowledge/list`
  - [ ] Display metadata cards
  - [ ] Sort controls
  - [ ] Pagination
- [ ] Build preview panel
  - [ ] Shows on artifact selection
  - [ ] Renders content by type
  - [ ] Action buttons

**Backend API** (create first):
```python
# backend/routes/knowledge_explorer_api.py

@router.get("/api/knowledge/categories")
async def get_categories():
    """Get knowledge categories with counts"""
    return scan_grace_training_directory()

@router.get("/api/knowledge/list")
async def list_artifacts(category: str = None, tags: str = None):
    """List knowledge artifacts with metadata"""
    return query_knowledge_database(category, tags)
```

---

#### 4.2 Connect List/Search to Knowledge APIs
- [ ] Wire artifact list to `/api/knowledge/list`
- [ ] Implement search bar
  - [ ] Debounce input (500ms)
  - [ ] Call `/api/knowledge/search` (RAG)
  - [ ] Show results with relevance scores
- [ ] Add filter controls
  - [ ] Category filter
  - [ ] Date range filter
  - [ ] Tag filter
  - [ ] File type filter
- [ ] Implement sorting
  - [ ] By name
  - [ ] By date
  - [ ] By size
  - [ ] By relevance (in search mode)

**Implementation**:
```typescript
// ArtifactList.tsx
export const ArtifactList = ({ filters }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['knowledge', 'list', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const response = await fetch(`/api/knowledge/list?${params}`);
      return response.json();
    }
  });
  
  if (isLoading) return <LoadingSpinner />;
  
  return (
    <div className="artifact-list">
      {data.artifacts.map(artifact => (
        <ArtifactCard 
          key={artifact.id} 
          artifact={artifact}
          onSelect={handleSelect}
        />
      ))}
    </div>
  );
};
```

---

#### 4.3 Hook Upload/Re-ingest Controls
- [ ] Create upload button handler
- [ ] Implement drag & drop zone
  - [ ] Visual feedback on drag-over
  - [ ] Handle file drop
  - [ ] Support multiple files
- [ ] Wire to ingestion endpoints
  - [ ] `/api/knowledge/upload` for single files
  - [ ] `/api/knowledge/bulk-upload` for multiple
  - [ ] `/api/remote-access/rag/ingest-text` for text paste
  - [ ] `/api/speech/upload-voice-note` for audio
- [ ] Add upload progress indicators
- [ ] Show success/error notifications
- [ ] Refresh list after upload

**Implementation**:
```typescript
// DropZone.tsx
const handleDrop = async (files: FileList) => {
  const fileArray = Array.from(files);
  
  for (const file of fileArray) {
    // Check duplicate
    const isDuplicate = await checkDuplicate(file.name);
    if (isDuplicate) {
      const proceed = confirm(`${file.name} exists. Upload anyway?`);
      if (!proceed) continue;
    }
    
    // Upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', selectedCategory);
    formData.append('auto_ingest', 'true');
    
    const response = await fetch('/api/knowledge/upload', {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      showNotification(`✅ ${file.name} uploaded and ingested`);
    }
  }
  
  refreshList();
};
```

- [ ] Implement re-ingest button
  - [ ] Shows on artifact card
  - [ ] Calls `/api/knowledge/{id}/re-ingest`
  - [ ] Shows progress
  - [ ] Updates artifact metadata

---

#### 4.4 Tie Selection into Dynamic Workspaces
- [ ] Add "Open in Workspace" button to artifacts
- [ ] Determine workspace type from file extension
  - [ ] .pdf → `DocumentViewerWorkspace`
  - [ ] .md, .py, .js → `CodeEditorWorkspace`
  - [ ] .mp3, .wav → `AudioPlayerWorkspace`
  - [ ] .png, .jpg → `ImageViewerWorkspace`
- [ ] Spawn workspace on click
- [ ] Pass artifact ID to workspace
- [ ] Workspace fetches full content

**Implementation**:
```typescript
// ArtifactCard.tsx
const handleOpenInWorkspace = (artifact: Artifact) => {
  const workspaceType = determineWorkspaceType(artifact.file_extension);
  
  spawn({
    type: workspaceType,
    title: artifact.filename,
    config: {
      artifactId: artifact.id,
      filePath: artifact.source_path
    }
  });
};
```

---

#### 4.5 Build Workspace Types for Files
- [ ] Create `DocumentViewerWorkspace`
  - [ ] PDF.js integration
  - [ ] Page navigation
  - [ ] Zoom controls
  - [ ] Download button
- [ ] Create `CodeEditorWorkspace`
  - [ ] Monaco Editor integration
  - [ ] Syntax highlighting
  - [ ] Read-only mode
  - [ ] Line numbers
- [ ] Create `AudioPlayerWorkspace`
  - [ ] HTML5 audio player
  - [ ] Show transcript
  - [ ] Timestamp navigation
- [ ] Create `ImageViewerWorkspace`
  - [ ] Image display with zoom
  - [ ] Show OCR results
  - [ ] Download button

---

### Phase 4 Deliverable
✅ **Memory Explorer fully functional**
- Browse knowledge artifacts by category
- Search with RAG-powered semantic search
- Upload files via drag & drop
- Re-ingest existing artifacts
- Open files in appropriate workspace type
- Dynamic workspaces for deeper file views

**Demo-able**: Yes (full knowledge management)

---

## 🎨 Phase 5: Optional Widgets (Week 4)

### Objective
Add daily brief and approvals shortcut

### Tasks

#### 5.1 Daily Brief Widget
- [ ] Create `DailyBrief` component
- [ ] Fetch from `/api/reports/daily-brief`
- [ ] Display summary:
  - [ ] Missions completed today
  - [ ] Issues prevented
  - [ ] Patterns learned
  - [ ] Tomorrow's watchlist
- [ ] Add expand/collapse
- [ ] Position near chat pane (top-right corner)

**Implementation**:
```typescript
// DailyBrief.tsx
export const DailyBrief = () => {
  const { data } = useQuery({
    queryKey: ['daily-brief'],
    queryFn: () => fetch('/api/reports/daily-brief').then(r => r.json()),
    refetchInterval: 3600000  // Refresh every hour
  });
  
  return (
    <div className="daily-brief">
      <h3>📊 Daily Brief</h3>
      <p>{data?.summary}</p>
      
      <div className="metrics">
        <Metric label="Missions" value={data?.missions_today} />
        <Metric label="Prevented" value={data?.issues_prevented} />
        <Metric label="Learned" value={data?.patterns_learned} />
      </div>
      
      <button onClick={() => spawnDailyBriefWorkspace()}>
        View Full Report
      </button>
    </div>
  );
};
```

---

#### 5.2 Approvals Shortcut
- [ ] Create `ApprovalsWidget` component
- [ ] Show pending approval count
- [ ] "Approve All" button
- [ ] Calls `/api/approvals/grant-all`
- [ ] Updates on approval granted
- [ ] Position near command palette or top bar

**Implementation**:
```typescript
// ApprovalsWidget.tsx
export const ApprovalsWidget = () => {
  const { data: pending } = useQuery({
    queryKey: ['approvals', 'pending'],
    queryFn: () => 
      fetch('/api/secrets/consent/pending?user_id=admin').then(r => r.json())
  });
  
  const { mutate: approveAll } = useMutation({
    mutationFn: () => 
      fetch('/api/approvals/grant-all', { method: 'POST' }),
    onSuccess: () => {
      showNotification('✅ All operations authorized');
      queryClient.invalidateQueries(['approvals']);
    }
  });
  
  if (pending?.total === 0) return null;
  
  return (
    <div className="approvals-widget">
      <Badge count={pending?.total} />
      <button onClick={() => approveAll()}>
        ✅ Approve All ({pending?.total})
      </button>
    </div>
  );
};
```

---

### Phase 5 Deliverable
✅ **Polish and optional features added**
- Daily brief shows today's summary
- Approvals shortcut for one-click authorization
- Professional, polished UI
- All features integrated

**Demo-able**: Yes (production-ready)

---

## 📊 Overall Timeline

### Week 1: Foundation
- ✅ Three-pane layout with placeholder data
- ✅ Responsive design
- ✅ Independent scrolling
- **Deliverable**: Static console shell

### Week 2: Interactivity
- ✅ Dynamic workspaces infrastructure
- ✅ Tab spawning/switching/closing
- ✅ Wire to real backend APIs
- **Deliverable**: Live data flowing

### Week 3: Memory Explorer
- ✅ File explorer shell
- ✅ Upload/re-ingest controls
- ✅ RAG search integration
- ✅ Workspace integration
- **Deliverable**: Full knowledge management

### Week 4: Polish
- ✅ Daily brief widget
- ✅ Approvals shortcut
- ✅ Performance optimization
- ✅ Final testing
- **Deliverable**: Production-ready console

---

## 🎯 Milestone Checklist

### Milestone 1: Shell (End of Week 1)
- [ ] Three panes visible with mock data
- [ ] Each pane scrolls independently
- [ ] Responsive on desktop/tablet/mobile
- [ ] Can be demo'd to stakeholders

### Milestone 2: Live (End of Week 2)
- [ ] Logs stream from backend
- [ ] Chat sends to Grace and gets responses
- [ ] Tasks show real missions
- [ ] Dynamic workspaces spawn correctly
- [ ] Can be used for real debugging

### Milestone 3: Explorer (End of Week 3)
- [ ] Can browse all knowledge artifacts
- [ ] Can upload files via drag & drop
- [ ] Can search with RAG
- [ ] Can open files in workspaces
- [ ] Knowledge base fully manageable

### Milestone 4: Production (End of Week 4)
- [ ] All features complete
- [ ] Performance optimized
- [ ] Security reviewed
- [ ] Documentation complete
- [ ] Ready for deployment

---

## 🚀 Quick Start for Development

### Backend First (Day 1)
```bash
# Create log API
touch backend/routes/logs_api.py
# Implement /api/logs/recent and /ws/logs

# Add to main.py
from backend.routes.logs_api import router as logs_router
app.include_router(logs_router)

# Test
curl http://localhost:8017/api/logs/recent
```

### Frontend Shell (Day 2-3)
```bash
# Create React app
cd frontend
npx create-react-app console --template typescript
cd console

# Install dependencies
npm install tailwindcss react-split-pane socket.io-client @tanstack/react-query

# Build layout
# Implement ConsoleLayout, LogsPane, ChatPane, TaskManagerPane

# Run
npm start
```

### Wire Together (Day 4-5)
```bash
# Connect frontend to backend APIs
# Replace placeholder data with API calls
# Test WebSocket connections
# Verify data flows correctly
```

---

## 📋 Task Dependencies

```
Phase 1 (Layout)
  ↓
Phase 2 (Workspaces) ← depends on Phase 1
  ↓
Phase 3 (Data Wiring) ← depends on Phase 1 & 2
  ↓
Phase 4 (Explorer) ← depends on Phase 1, 2, 3
  ↓
Phase 5 (Widgets) ← depends on all previous
```

**Can parallelize**:
- Backend API development (Phase 3 tasks)
- Frontend component development (Phase 1-2 tasks)

**Must be sequential**:
- Layout → Workspaces → Data Wiring → Explorer

---

## ✅ Definition of Done (per Phase)

### Phase 1 Done When:
- [ ] Can view three panes on screen
- [ ] Panes resize correctly
- [ ] Works on desktop/tablet/mobile
- [ ] Placeholder data displays properly
- [ ] Code reviewed and merged

### Phase 2 Done When:
- [ ] Can spawn workspace from button
- [ ] Tab bar shows/switches tabs
- [ ] Can close tabs
- [ ] Mock workspace displays correctly
- [ ] Flow proven end-to-end

### Phase 3 Done When:
- [ ] Logs stream from backend in real-time
- [ ] Chat sends to AI and gets responses
- [ ] Tasks show actual missions
- [ ] All APIs integrated
- [ ] No more placeholder data

### Phase 4 Done When:
- [ ] Can browse all knowledge artifacts
- [ ] Can upload files and see them indexed
- [ ] Can search with RAG
- [ ] Can open files in workspaces
- [ ] All file types supported

### Phase 5 Done When:
- [ ] Daily brief widget works
- [ ] Approvals shortcut works
- [ ] UI polished and professional
- [ ] Performance acceptable
- [ ] Ready for production

---

**Next Step**: Start with Phase 1 - build the three-pane layout shell! 🚀
