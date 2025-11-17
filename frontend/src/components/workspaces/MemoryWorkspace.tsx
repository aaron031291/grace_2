import { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface MemoryWorkspaceProps {
  workspace: Workspace;
}

export function MemoryWorkspace({ workspace }: MemoryWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">💾</span>
          <h1>Memory</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">Upload Files</button>
          <button className="workspace-action-btn">New Folder</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="memory-dual-pane">
          {/* File Tree */}
          <div className="memory-tree-pane">
            <div className="memory-tree-header">
              <h3>File Explorer</h3>
              <input 
                type="text" 
                placeholder="Search files..." 
                className="memory-search-input"
              />
            </div>
            <div className="memory-tree">
              <div className="tree-item tree-folder tree-expanded">
                <span className="tree-icon">📁</span>
                <span className="tree-label">Documents</span>
              </div>
              <div className="tree-item tree-file tree-indent-1">
                <span className="tree-icon">📄</span>
                <span className="tree-label">project-plan.md</span>
              </div>
              <div className="tree-item tree-file tree-indent-1">
                <span className="tree-icon">📄</span>
                <span className="tree-label">requirements.txt</span>
              </div>
              <div className="tree-item tree-folder tree-indent-1">
                <span className="tree-icon">📁</span>
                <span className="tree-label">specs</span>
              </div>
              <div className="tree-item tree-folder tree-expanded">
                <span className="tree-icon">📁</span>
                <span className="tree-label">Code</span>
              </div>
              <div className="tree-item tree-file tree-indent-1">
                <span className="tree-icon">🐍</span>
                <span className="tree-label">main.py</span>
              </div>
              <div className="tree-item tree-file tree-indent-1">
                <span className="tree-icon">⚛️</span>
                <span className="tree-label">App.tsx</span>
              </div>
            </div>
          </div>

          {/* File Preview */}
          <div className="memory-preview-pane">
            <div className="memory-preview-header">
              <div className="preview-file-info">
                <span className="preview-file-icon">📄</span>
                <span className="preview-file-name">project-plan.md</span>
              </div>
              <div className="preview-actions">
                <button className="preview-action-btn">📋 Copy</button>
                <button className="preview-action-btn">💾 Save to World Model</button>
                <button className="preview-action-btn">📤 Share</button>
              </div>
            </div>
            <div className="memory-preview-content">
              <div className="preview-markdown">
                <h1>Project Plan</h1>
                <p>This is a sample markdown file showing the preview functionality.</p>
                <h2>Features</h2>
                <ul>
                  <li>Dual-pane file manager</li>
                  <li>File preview with syntax highlighting</li>
                  <li>Version history</li>
                  <li>Quick actions</li>
                </ul>
              </div>
            </div>
            <div className="memory-preview-footer">
              <div className="file-metadata">
                <span>Size: 2.4 KB</span>
                <span>Modified: 2 hours ago</span>
                <span>Type: Markdown</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
