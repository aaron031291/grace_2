# Grace Console UI

A comprehensive, production-ready frontend console for Grace that integrates all backend functionality into a unified interface.

## Components Implemented

### 1. **Logs Pane** (`panels/LogsPane.tsx`)
- Real-time log streaming with auto-refresh (3s intervals)
- Filter by level (info, success, warning, error)
- Filter by domain (core, memory, ai, etc.)
- Search logs by message content
- Color-coded log entries for quick scanning
- API: `GET /api/logs/recent`

### 2. **Task Manager** (`panels/TaskManager.tsx`)
- Mission control dashboard
- Lists all missions with status tracking
- Filter by status, severity, subsystem
- Action buttons: Acknowledge, Execute, Details
- KPI delta visualization
- Auto-refresh every 5 seconds
- API: `GET /mission-control/missions`

### 3. **Chat Pane** (`panels/ChatPane.tsx`)
- Conversational interface with Grace
- File attachment support
- Citation/reference display
- Metadata visualization
- Quick action buttons for common queries
- Auto-scrolling message feed
- API: `POST /api/chat`

### 4. **Dynamic Workspaces** (`panels/WorkspaceManager.tsx`)
- Tab-based workspace system
- Support for multiple workspace types:
  - Dashboard workspaces
  - Mission detail viewers
  - Artifact previews
  - Custom workspaces
- Easy to extend with new workspace types
- Tab management (create, close, switch)

### 5. **Memory Explorer** (`panels/MemoryExplorer.tsx`)
- Browse knowledge artifacts
- Category filtering (documents, code, conversations, etc.)
- Search functionality
- File upload/ingest
- Artifact preview with metadata
- Re-ingest capability
- API: `GET /api/ingest/artifacts`

## Console Shell

**Main component:** `GraceConsole.tsx`

Features:
- Flexible 3-panel layout (main + sidebar + bottom)
- Collapsible panels
- Dynamic panel switching
- Responsive design
- Modern dark theme with gradient accents

## Getting Started

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Start Backend
Make sure the Grace backend is running on `http://localhost:8017`

```bash
# In backend directory
python -m uvicorn backend.main:app --reload --port 8017
```

## API Configuration

All components use `http://localhost:8017` as the base URL. To change this, update the `API_BASE` constant in each panel component.

## Features

### Auto-refresh
- **Logs:** Every 3 seconds
- **Tasks:** Every 5 seconds
- Can be toggled in Logs Pane

### Authentication
All API calls include a bearer token:
```typescript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`
}
```

### Responsive Design
- Desktop-first layout
- Collapsible panels for smaller screens
- Mobile-friendly controls

## Architecture

```
GraceConsole (main shell)
├── Console Header (nav + controls)
└── Console Body
    ├── Main Panel (primary view)
    ├── Sidebar Panel (tasks/memory)
    └── Bottom Panel (logs)
```

## Extending

### Adding a New Panel

1. Create component in `frontend/src/panels/YourPanel.tsx`
2. Add corresponding CSS file
3. Register in `GraceConsole.tsx`:
   ```typescript
   type PanelType = 'logs' | 'tasks' | 'chat' | 'memory' | 'workspace' | 'your-panel';
   
   const renderPanel = (type: PanelType) => {
     switch (type) {
       case 'your-panel':
         return <YourPanel />;
       // ... other cases
     }
   }
   ```

### Adding a New Workspace Type

In `WorkspaceManager.tsx`, add to `getWorkspaceComponent`:
```typescript
case 'your-type':
  return <YourWorkspaceComponent metadata={metadata} />;
```

## API Endpoints Used

| Component | Endpoint | Method | Purpose |
|-----------|----------|--------|---------|
| LogsPane | `/api/logs/recent` | GET | Fetch recent logs |
| LogsPane | `/api/logs/domains` | GET | Get log domains |
| TaskManager | `/mission-control/missions` | GET | List missions |
| TaskManager | `/mission-control/missions/{id}/execute` | POST | Execute mission |
| ChatPane | `/api/chat` | POST | Send message |
| MemoryExplorer | `/api/ingest/artifacts` | GET | List artifacts |
| MemoryExplorer | `/api/ingest/upload` | POST | Upload file |

## Styling

All components use a consistent dark theme:
- **Primary:** `#00ff88` (green)
- **Secondary:** `#00ccff` (cyan)
- **Accent:** `#0066cc` (blue)
- **Background:** `#1a1a1a`, `#0d0d0d`
- **Text:** `#e0e0e0`

## Next Steps

Wire the placeholder components:
1. Connect dashboard workspaces to actual dashboard data
2. Implement mission detail viewer
3. Add artifact preview (PDF, images, code)
4. Implement WebSocket for real-time logs (already supported by backend)
5. Add notification system
6. Implement settings panel

## Development

```bash
# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

## Notes

- All components are TypeScript with full type safety
- Uses React hooks (useState, useEffect, useCallback)
- No external UI library dependencies (pure CSS)
- Ready for WebSocket upgrade (logs endpoint supports it)
- Fully responsive and accessible
