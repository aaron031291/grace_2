import type { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface TerminalWorkspaceProps {
  workspace: Workspace;
}

export function TerminalWorkspace({ workspace }: TerminalWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">⚡</span>
          <h1>Terminal</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">New Session</button>
          <button className="workspace-action-btn">Clear History</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="terminal-container">
          <div className="terminal-output">
            <div className="terminal-line">
              <span className="terminal-prompt">grace@system:~$</span>
              <span className="terminal-command">status</span>
            </div>
            <div className="terminal-line terminal-output-text">
              System Status: Operational
            </div>
            <div className="terminal-line terminal-output-text">
              Health: 79% | Trust: 75% | Confidence: 73%
            </div>
            <div className="terminal-line terminal-output-text">
              Active Kernels: 20/20
            </div>
            <div className="terminal-line">
              <span className="terminal-prompt">grace@system:~$</span>
              <span className="terminal-command">list-missions</span>
            </div>
            <div className="terminal-line terminal-output-text">
              Active Missions:
            </div>
            <div className="terminal-line terminal-output-text">
              1. Deploy E-commerce Platform (60% complete)
            </div>
            <div className="terminal-line terminal-output-text">
              2. Database Migration (waiting for approval)
            </div>
            <div className="terminal-line">
              <span className="terminal-prompt">grace@system:~$</span>
              <span className="terminal-cursor">_</span>
            </div>
          </div>
          <div className="terminal-input-area">
            <span className="terminal-prompt">grace@system:~$</span>
            <input 
              type="text" 
              className="terminal-input" 
              placeholder="Type a command..."
              autoFocus
            />
          </div>
        </div>
      </div>
    </div>
  );
}
