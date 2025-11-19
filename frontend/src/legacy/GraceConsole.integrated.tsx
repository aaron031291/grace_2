import { useState } from 'react';
import { useWorkspaces, useWorkspaceActions } from './hooks/useWorkspaces';
import type { Citation } from './services/chatApi';

import LogsPane from './panels/LogsPane';
import TaskManager from './panels/TaskManager';
import ChatPane from './panels/ChatPane';
import MemoryExplorer from './panels/MemoryExplorer';
import WorkspaceManager from './panels/WorkspaceManager.enhanced';

import './GraceConsole.css';

type PanelType = 'logs' | 'tasks' | 'chat' | 'memory' | 'workspace';

interface LayoutConfig {
  main: PanelType;
  sidebar?: PanelType;
  bottom?: PanelType;
}

export default function GraceConsole() {
  const [layout, setLayout] = useState<LayoutConfig>({
    main: 'workspace',
    sidebar: 'tasks',
    bottom: 'logs'
  });
  
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [bottomCollapsed, setBottomCollapsed] = useState(false);

  // Workspace management
  const {
    workspaces,
    activeWorkspace,
    openWorkspace,
    closeWorkspace,
    setActiveWorkspace,
  } = useWorkspaces();

  // Workspace action helpers
  const workspaceActions = useWorkspaceActions(openWorkspace);

  // Handle citation clicks from chat
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
        if (citation.id) {
          workspaceActions.openArtifactViewer(citation.id, citation.title);
          setLayout(prev => ({ ...prev, main: 'workspace' }));
        }
        break;
      
      default:
        console.log('Citation clicked:', citation);
    }
  };

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

  const swapPanel = (position: keyof LayoutConfig, newType: PanelType) => {
    setLayout(prev => ({ ...prev, [position]: newType }));
  };

  return (
    <div className="grace-console">
      <div className="console-header">
        <div className="console-logo">
          <span className="logo-icon">🧠</span>
          <span className="logo-text">GRACE Console</span>
        </div>
        
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

        <div className="console-actions">
          {workspaces.length > 0 && (
            <div className="workspace-indicator" title={`${workspaces.length} workspace(s) open`}>
              <span className="workspace-count">{workspaces.length}</span>
              <span className="workspace-label">workspaces</span>
            </div>
          )}
          <button className="action-btn" title="Settings">⚙️</button>
          <button className="action-btn" title="Help">❓</button>
          <button className="status-btn">
            <span className="status-dot"></span>
            Ready
          </button>
        </div>
      </div>

      <div className="console-body">
        <div className="console-main-area">
          <div className="main-panel">
            {renderPanel(layout.main)}
          </div>

          {!bottomCollapsed && layout.bottom && (
            <div className="bottom-panel">
              <div className="panel-header">
                <span className="panel-title">{getPanelTitle(layout.bottom)}</span>
                <div className="panel-controls">
                  <button onClick={() => setBottomCollapsed(true)} title="Collapse">
                    ▼
                  </button>
                </div>
              </div>
              <div className="panel-content">
                {renderPanel(layout.bottom)}
              </div>
            </div>
          )}
        </div>

        {!sidebarCollapsed && layout.sidebar && (
          <div className="console-sidebar">
            <div className="panel-header">
              <span className="panel-title">{getPanelTitle(layout.sidebar)}</span>
              <div className="panel-controls">
                <button onClick={() => setSidebarCollapsed(true)} title="Collapse">
                  ▶
                </button>
              </div>
            </div>
            <div className="panel-content">
              {renderPanel(layout.sidebar)}
            </div>
          </div>
        )}
      </div>

      {(sidebarCollapsed || bottomCollapsed) && (
        <div className="collapsed-controls">
          {sidebarCollapsed && (
            <button 
              className="expand-btn sidebar-expand"
              onClick={() => setSidebarCollapsed(false)}
              title="Expand sidebar"
            >
              ◀ {getPanelTitle(layout.sidebar!)}
            </button>
          )}
          {bottomCollapsed && (
            <button 
              className="expand-btn bottom-expand"
              onClick={() => setBottomCollapsed(false)}
              title="Expand bottom panel"
            >
              ▲ {getPanelTitle(layout.bottom!)}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function getPanelTitle(type: PanelType): string {
  const titles: Record<PanelType, string> = {
    logs: 'System Logs',
    tasks: 'Mission Control',
    chat: 'Grace Chat',
    memory: 'Memory Explorer',
    workspace: 'Workspace'
  };
  return titles[type] || type;
}
