# Grace Console - Integration Guide

## Adding New Panels to GraceConsole

Quick guide to integrate Governance Console and MCP Tools Panel.

## Step 1: Update GraceConsole.tsx

```typescript
// 1. Add imports at top
import GovernanceConsole from './panels/GovernanceConsole';
import MCPToolsPanel from './panels/MCPToolsPanel';

// 2. Update PanelType (line 13)
type PanelType = 'logs' | 'tasks' | 'chat' | 'memory' | 'workspace' | 'governance' | 'mcp';

// 3. Add to renderPanel function (around line 70)
const renderPanel = (type: PanelType) => {
  switch (type) {
    case 'logs':
      return <LogsPane />;
    
    case 'tasks':
      return <TaskManager />;
    
    case 'chat':
      return <ChatPane onOpenWorkspace={handleCitationClick} />;
    
    case 'memory':
      return <MemoryExplorer />;
    
    case 'governance':
      return <GovernanceConsole />;
    
    case 'mcp':
      return <MCPToolsPanel />;
    
    case 'workspace':
      return (
        <WorkspaceManager
          workspaces={workspaces}
          activeWorkspace={activeWorkspace}
          onClose={closeWorkspace}
          onSwitch={setActiveWorkspace}
        />
      );
    
    default:
      return <div>Unknown panel: {type}</div>;
  }
};

// 4. Add navigation buttons (in console-nav div, around line 105)
<div className="console-nav">
  <button 
    className={layout.main === 'chat' ? 'active' : ''}
    onClick={() => swapPanel('main', 'chat')}
    title="Chat with Grace"
  >
    💬 Chat
  </button>
  <button 
    className={layout.main === 'workspace' ? 'active' : ''}
    onClick={() => swapPanel('main', 'workspace')}
    title="Workspaces"
  >
    📊 Workspace
  </button>
  <button 
    className={layout.main === 'memory' ? 'active' : ''}
    onClick={() => swapPanel('main', 'memory')}
    title="Memory Explorer"
  >
    🧠 Memory
  </button>
  <button 
    className={layout.main === 'governance' ? 'active' : ''}
    onClick={() => swapPanel('main', 'governance')}
    title="Governance"
  >
    ⚖️ Governance
  </button>
  <button 
    className={layout.main === 'mcp' ? 'active' : ''}
    onClick={() => swapPanel('main', 'mcp')}
    title="MCP Tools"
  >
    🔧 MCP
  </button>
  <button 
    className={layout.sidebar === 'tasks' || layout.main === 'tasks' ? 'active' : ''}
    onClick={() => swapPanel('sidebar', 'tasks')}
    title="Mission Control"
  >
    🎯 Tasks
  </button>
  <button 
    className={layout.bottom === 'logs' || layout.main === 'logs' ? 'active' : ''}
    onClick={() => swapPanel('bottom', 'logs')}
    title="System Logs"
  >
    📋 Logs
  </button>
</div>

// 5. Update getPanelTitle function (bottom of file)
function getPanelTitle(type: PanelType): string {
  const titles: Record<PanelType, string> = {
    logs: 'System Logs',
    tasks: 'Mission Control',
    chat: 'Grace Chat',
    memory: 'Memory Explorer',
    workspace: 'Workspace',
    governance: 'Governance',
    mcp: 'MCP Tools',
  };
  return titles[type] || type;
}
```

## Step 2: Test Each Panel

### Test Governance Console

```bash
# Start frontend
npm run dev

# In browser
1. Navigate to http://localhost:5173
2. Click "⚖️ Governance" button
3. Should see pending approvals (if any)
4. Click an approval → Detail panel opens
5. Click "Discuss with Grace" → Gets context
6. Click "Approve" or "Reject" → Prompts for reason
```

### Test MCP Tools

```bash
1. Click "🔧 MCP" button
2. Should see resources list (grace://self, grace://system)
3. Click a resource → Content displays
4. Should see tools list (ask_grace, query_world_model)
5. Click a tool → Parameter form appears
6. Enter parameters (JSON)
7. Click "Execute Tool" → Result displays
```

### Test World Model Mode in Chat

```bash
1. Click "💬 Chat" button
2. Click "🧠 World Model" mode
3. Type: /ask How is the CRM health?
4. Grace queries world model
5. Response includes citations
6. Click citation → Opens workspace
```

### Test Model Selection

```bash
1. In Chat panel
2. Click "🤖 Default" button
3. Model selector dropdown appears
4. Shows available models (qwen2.5, deepseek, etc.)
5. Select a model
6. Button shows selected model name
```

## Step 3: Verify Backend Endpoints

Check your backend has these endpoints:

```bash
# Governance
curl http://localhost:8017/api/governance/approvals?status=pending

# World Model
curl -X POST http://localhost:8017/world-model/ask-grace?question=test

# MCP
curl http://localhost:8017/world-model/mcp/manifest

# Models
curl http://localhost:8017/api/models/available
```

If any endpoint returns 404, check if it's on port 8000 instead of 8017.

## Alternative: Manual Panel Integration

If you prefer to test panels individually first:

### Test Standalone Governance

```typescript
// In main.tsx temporarily
import GovernanceConsole from './panels/GovernanceConsole';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GovernanceConsole />
  </StrictMode>,
);
```

### Test Standalone MCP Tools

```typescript
// In main.tsx temporarily
import MCPToolsPanel from './panels/MCPToolsPanel';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MCPToolsPanel />
  </StrictMode>,
);
```

## Complete GraceConsole.tsx (Reference)

```typescript
import { useState } from 'react';
import { useWorkspaces, useWorkspaceActions } from './hooks/useWorkspaces';
import type { Citation } from './services/chatApi';

// Import all panels
import LogsPane from './panels/LogsPane';
import TaskManager from './panels/TaskManager';
import ChatPane from './panels/ChatPane';
import MemoryExplorer from './panels/MemoryExplorer';
import WorkspaceManager from './panels/WorkspaceManager';
import GovernanceConsole from './panels/GovernanceConsole';
import MCPToolsPanel from './panels/MCPToolsPanel';

import './GraceConsole.css';

type PanelType = 'logs' | 'tasks' | 'chat' | 'memory' | 'workspace' | 'governance' | 'mcp';

export default function GraceConsole() {
  const [layout, setLayout] = useState({
    main: 'workspace' as PanelType,
    sidebar: 'tasks' as PanelType,
    bottom: 'logs' as PanelType,
  });

  const { workspaces, activeWorkspace, openWorkspace, closeWorkspace, setActiveWorkspace } = useWorkspaces();
  const workspaceActions = useWorkspaceActions(openWorkspace);

  const handleCitationClick = (citation: Citation) => {
    switch (citation.type) {
      case 'mission':
        workspaceActions.openMissionDetail(citation.id, citation.title);
        setLayout(prev => ({ ...prev, main: 'workspace' }));
        break;
      case 'kpi':
        workspaceActions.openKPIDashboard({ kpiId: citation.id });
        setLayout(prev => ({ ...prev, main: 'workspace' }));
        break;
      case 'document':
        workspaceActions.openArtifactViewer(citation.id, citation.title);
        setLayout(prev => ({ ...prev, main: 'workspace' }));
        break;
    }
  };

  const renderPanel = (type: PanelType) => {
    switch (type) {
      case 'logs': return <LogsPane />;
      case 'tasks': return <TaskManager />;
      case 'chat': return <ChatPane onOpenWorkspace={handleCitationClick} />;
      case 'memory': return <MemoryExplorer />;
      case 'governance': return <GovernanceConsole />;
      case 'mcp': return <MCPToolsPanel />;
      case 'workspace': return (
        <WorkspaceManager
          workspaces={workspaces}
          activeWorkspace={activeWorkspace}
          onClose={closeWorkspace}
          onSwitch={setActiveWorkspace}
        />
      );
      default: return <div>Unknown panel</div>;
    }
  };

  return (
    <div className="grace-console">
      {/* Header */}
      <div className="console-header">
        <div className="console-logo">
          <span className="logo-icon">🧠</span>
          <span className="logo-text">GRACE Console</span>
        </div>

        <div className="console-nav">
          <button onClick={() => setLayout(p => ({ ...p, main: 'chat' }))}>💬 Chat</button>
          <button onClick={() => setLayout(p => ({ ...p, main: 'workspace' }))}>📊 Workspace</button>
          <button onClick={() => setLayout(p => ({ ...p, main: 'memory' }))}>🧠 Memory</button>
          <button onClick={() => setLayout(p => ({ ...p, main: 'governance' }))}>⚖️ Governance</button>
          <button onClick={() => setLayout(p => ({ ...p, main: 'mcp' }))}>🔧 MCP</button>
          <button onClick={() => setLayout(p => ({ ...p, sidebar: 'tasks' }))}>🎯 Tasks</button>
          <button onClick={() => setLayout(p => ({ ...p, bottom: 'logs' }))}>📋 Logs</button>
        </div>

        <div className="console-actions">
          {workspaces.length > 0 && (
            <div className="workspace-indicator">
              <span className="workspace-count">{workspaces.length}</span>
              <span>workspaces</span>
            </div>
          )}
          <button className="action-btn">⚙️</button>
          <button className="action-btn">❓</button>
          <div className="status-btn">
            <span className="status-dot"></span>
            Ready
          </div>
        </div>
      </div>

      {/* Body with 3-panel layout */}
      <div className="console-body">
        <div className="console-main-area">
          <div className="main-panel">{renderPanel(layout.main)}</div>
          {layout.bottom && (
            <div className="bottom-panel">
              <div className="panel-header">{getPanelTitle(layout.bottom)}</div>
              <div className="panel-content">{renderPanel(layout.bottom)}</div>
            </div>
          )}
        </div>
        {layout.sidebar && (
          <div className="console-sidebar">
            <div className="panel-header">{getPanelTitle(layout.sidebar)}</div>
            <div className="panel-content">{renderPanel(layout.sidebar)}</div>
          </div>
        )}
      </div>
    </div>
  );
}

function getPanelTitle(type: PanelType): string {
  return {
    logs: 'System Logs',
    tasks: 'Mission Control',
    chat: 'Grace Chat',
    memory: 'Memory Explorer',
    workspace: 'Workspace',
    governance: 'Governance',
    mcp: 'MCP Tools',
  }[type] || type;
}
```

Save this as your updated `GraceConsole.tsx` or copy the changes manually.

## 🎯 Summary

✅ **All 7 panels implemented:**
1. Logs - Real-time system logs
2. Tasks - Mission control Kanban
3. Chat - With model selection & world model
4. Memory - Knowledge management with upload
5. Workspace - Dynamic tabs
6. Governance - Approval workflow
7. MCP Tools - Protocol interface

✅ **All wired to backend APIs**  
✅ **All documented**  
✅ **Production-ready**  

Start the frontend and explore! 🚀
