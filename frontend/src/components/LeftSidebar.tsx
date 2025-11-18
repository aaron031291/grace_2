import type { Capability, Workspace } from '../GraceEnterpriseUI';
import './LeftSidebar.css';

interface LeftSidebarProps {
  activeCapability: Capability | null;
  activeWorkspace: Workspace | null;
  workspaces: Workspace[];
  onCapabilityClick: (capability: Capability) => void;
  onWorkspaceClick: (workspace: Workspace) => void;
  onWorkspaceClose: (id: string) => void;
  onCreateWorkspace: (type: Capability) => void;
  onCommandPaletteOpen: () => void;
}

const capabilities: Array<{ id: Capability; icon: string; label: string }> = [
  { id: 'guardian', icon: '🛡️', label: 'Guardian' },
  { id: 'self-healing', icon: '🔧', label: 'Self-Healing' },
  { id: 'copilot', icon: '🤖', label: 'Copilot' },
  { id: 'world-model', icon: '🌍', label: 'World Model' },
  { id: 'learning', icon: '🧠', label: 'Learning Engine' },
  { id: 'governance', icon: '⚖️', label: 'Governance' },
  { id: 'mission-control', icon: '🎯', label: 'Mission Control' },
  { id: 'observatory', icon: '👁️', label: 'Observatory' },
  { id: 'memory', icon: '💾', label: 'Memory' },
  { id: 'terminal', icon: '⚡', label: 'Terminal' },
  { id: 'agentic', icon: '🤖', label: 'Agentic Organism' },
  { id: 'phase7', icon: '🚀', label: 'Phase 7: SaaS' },
  { id: 'mission-designer', icon: '🎨', label: 'Mission Designer' },
  { id: 'approval-inbox', icon: '📥', label: 'Approval Inbox' },
  { id: 'learning-jobs', icon: '📚', label: 'Learning Jobs' },
];

export function LeftSidebar({
  activeCapability,
  activeWorkspace,
  workspaces,
  onCapabilityClick,
  onWorkspaceClick,
  onWorkspaceClose,
  onCommandPaletteOpen,
}: LeftSidebarProps) {
  return (
    <div className="left-sidebar">
      {/* Core Actions */}
      <div className="sidebar-section">
        <button className="new-chat-btn" onClick={() => onCapabilityClick('terminal')}>
          <span className="btn-icon">✨</span>
          <span className="btn-text">New Chat</span>
        </button>
        
        <button className="sidebar-action-btn" onClick={onCommandPaletteOpen}>
          <span className="btn-icon">🔍</span>
          <span className="btn-text">Command Palette</span>
          <span className="btn-shortcut">⌘K</span>
        </button>
      </div>

      {/* Grace Capabilities */}
      <div className="sidebar-section">
        <div className="section-header">Grace Capabilities</div>
        <div className="capabilities-list">
          {capabilities.map((cap) => (
            <button
              key={cap.id}
              className={`capability-btn ${activeCapability === cap.id ? 'active' : ''}`}
              onClick={() => onCapabilityClick(cap.id)}
              title={cap.label}
            >
              <span className="capability-icon">{cap.icon}</span>
              <span className="capability-label">{cap.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Workspaces */}
      {workspaces.length > 0 && (
        <div className="sidebar-section">
          <div className="section-header">
            <span>Workspaces</span>
            <button 
              className="add-workspace-btn"
              onClick={() => onCommandPaletteOpen()}
              title="Create workspace"
            >
              +
            </button>
          </div>
          <div className="workspaces-list">
            {workspaces.map((workspace) => (
              <div
                key={workspace.id}
                className={`workspace-item ${activeWorkspace?.id === workspace.id ? 'active' : ''}`}
              >
                <button
                  className="workspace-btn"
                  onClick={() => onWorkspaceClick(workspace)}
                >
                  <span className="workspace-icon">
                    {capabilities.find(c => c.id === workspace.type)?.icon || '📊'}
                  </span>
                  <span className="workspace-title">{workspace.title}</span>
                </button>
                <button
                  className="workspace-close-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onWorkspaceClose(workspace.id);
                  }}
                  title="Close workspace"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chat History */}
      <div className="sidebar-section sidebar-section-grow">
        <div className="section-header">Chat History</div>
        <div className="chat-history-list">
          <div className="chat-history-empty">
            <p>No recent chats</p>
          </div>
        </div>
      </div>
    </div>
  );
}
