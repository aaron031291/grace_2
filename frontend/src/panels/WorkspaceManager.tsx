import { useWorkspaces, type Workspace, type WorkspaceType } from '../hooks/useWorkspaces';
import MissionDetailWorkspace from '../components/workspaces/MissionDetailWorkspace';
import DashboardWorkspace from '../components/workspaces/DashboardWorkspace';
import ArtifactViewerWorkspace from '../components/workspaces/ArtifactViewerWorkspace';
import './WorkspaceManager.enhanced.css';

interface WorkspaceManagerProps {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  onClose: (id: string) => void;
  onSwitch: (id: string) => void;
}

export default function WorkspaceManager({
  workspaces,
  activeWorkspace,
  onClose,
  onSwitch,
}: WorkspaceManagerProps) {
  
  const renderWorkspace = (workspace: Workspace) => {
    switch (workspace.type) {
      case 'mission-detail':
        return <MissionDetailWorkspace payload={workspace.payload} />;
      
      case 'kpi-dashboard':
      case 'crm-dashboard':
      case 'sales-dashboard':
        return <DashboardWorkspace type={workspace.type} payload={workspace.payload} />;
      
      case 'artifact-viewer':
        return <ArtifactViewerWorkspace payload={workspace.payload} />;
      
      case 'code-diff':
        return <CodeDiffPlaceholder payload={workspace.payload} />;
      
      case 'log-viewer':
        return <LogViewerPlaceholder payload={workspace.payload} />;
      
      case 'memory-preview':
        return <MemoryPreviewPlaceholder payload={workspace.payload} />;
      
      case 'custom':
        return workspace.payload.component || <CustomPlaceholder />;
      
      default:
        return <DefaultPlaceholder type={workspace.type} />;
    }
  };

  if (workspaces.length === 0) {
    return (
      <div className="workspace-manager-enhanced">
        <div className="no-workspaces">
          <div className="no-workspaces-icon">📋</div>
          <h3>No Active Workspaces</h3>
          <p>Open a workspace from logs, tasks, or chat to get started</p>
          <div className="suggested-actions">
            <p className="suggestion-label">Try:</p>
            <ul>
              <li>Click a mission in Task Manager</li>
              <li>Click a citation in Chat</li>
              <li>View logs for a specific service</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="workspace-manager-enhanced">
      <div className="workspace-tabs">
        {workspaces.map((workspace) => (
          <div
            key={workspace.id}
            className={`workspace-tab ${activeWorkspace?.id === workspace.id ? 'active' : ''}`}
            onClick={() => onSwitch(workspace.id)}
          >
            <span className="tab-icon">{getWorkspaceIcon(workspace.type)}</span>
            <span className="tab-title" title={workspace.title}>
              {workspace.title}
            </span>
            <button
              className="tab-close"
              onClick={(e) => {
                e.stopPropagation();
                onClose(workspace.id);
              }}
              title="Close"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="workspace-content-area">
        {activeWorkspace ? (
          renderWorkspace(activeWorkspace)
        ) : (
          <div className="no-active-workspace">
            <p>Select a workspace from the tabs above</p>
          </div>
        )}
      </div>
    </div>
  );
}

function getWorkspaceIcon(type: WorkspaceType): string {
  const icons: Record<WorkspaceType, string> = {
    'mission-detail': '🎯',
    'kpi-dashboard': '📈',
    'crm-dashboard': '👥',
    'sales-dashboard': '💰',
    'artifact-viewer': '📄',
    'code-diff': '💻',
    'log-viewer': '📋',
    'memory-preview': '🧠',
    'custom': '⚙️',
  };
  return icons[type] || '📌';
}

// Placeholder components
function CodeDiffPlaceholder({ payload }: any) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <h2>💻 Code Diff</h2>
      </div>
      <div className="workspace-content">
        <div className="placeholder">
          <h3>Code Diff Viewer</h3>
          <p>File: <code>{payload.filePath}</code></p>
          <p>Commit: <code>{payload.commitSha || 'working copy'}</code></p>
          <p>Wire this to a diff viewer component (e.g., react-diff-viewer)</p>
        </div>
      </div>
    </div>
  );
}

function LogViewerPlaceholder({ payload }: any) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <h2>📋 Log Viewer</h2>
      </div>
      <div className="workspace-content">
        <div className="placeholder">
          <h3>Log Viewer</h3>
          <p>Source: <code>{payload.logSource}</code></p>
          {payload.logLevel && <p>Level: <code>{payload.logLevel}</code></p>}
          <p>Wire this to a log viewer component with filtering and search</p>
        </div>
      </div>
    </div>
  );
}

function MemoryPreviewPlaceholder({ payload }: any) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <h2>🧠 Memory Preview</h2>
      </div>
      <div className="workspace-content">
        <div className="placeholder">
          <h3>Memory Preview</h3>
          {payload.data && (
            <pre className="memory-data">
              {JSON.stringify(payload.data, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

function CustomPlaceholder() {
  return (
    <div className="workspace-container">
      <div className="workspace-content">
        <div className="placeholder">
          <h3>Custom Workspace</h3>
          <p>Pass a custom component in the payload</p>
        </div>
      </div>
    </div>
  );
}

function DefaultPlaceholder({ type }: { type: string }) {
  return (
    <div className="workspace-container">
      <div className="workspace-content">
        <div className="placeholder">
          <h3>Unknown Workspace Type</h3>
          <p>Type: <code>{type}</code></p>
        </div>
      </div>
    </div>
  );
}
