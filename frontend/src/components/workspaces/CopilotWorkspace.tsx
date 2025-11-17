import { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface CopilotWorkspaceProps {
  workspace: Workspace;
}

export function CopilotWorkspace({ workspace }: CopilotWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">🤖</span>
          <h1>Copilot</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">New Project</button>
          <button className="workspace-action-btn">View Templates</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="workspace-grid">
          {/* Active Projects */}
          <div className="workspace-card workspace-card-wide">
            <div className="card-header">
              <h3>Active Projects</h3>
              <button className="card-action-btn">View All</button>
            </div>
            <div className="card-content">
              <div className="project-list">
                <div className="project-item">
                  <div className="project-icon">🌐</div>
                  <div className="project-details">
                    <div className="project-name">E-commerce Platform</div>
                    <div className="project-meta">
                      <span className="project-status project-in-progress">In Progress</span>
                      <span className="project-progress">67% complete</span>
                    </div>
                  </div>
                  <button className="project-action-btn">Continue</button>
                </div>
                <div className="project-item">
                  <div className="project-icon">📊</div>
                  <div className="project-details">
                    <div className="project-name">Analytics Dashboard</div>
                    <div className="project-meta">
                      <span className="project-status project-review">Review</span>
                      <span className="project-progress">95% complete</span>
                    </div>
                  </div>
                  <button className="project-action-btn">Review</button>
                </div>
              </div>
            </div>
          </div>

          {/* Code Generation */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Code Generation</h3>
            </div>
            <div className="card-content">
              <div className="code-gen-stats">
                <div className="stat-item">
                  <div className="stat-label">Files Generated</div>
                  <div className="stat-value">1,247</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Lines of Code</div>
                  <div className="stat-value">45.2K</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Success Rate</div>
                  <div className="stat-value">98.3%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Builds */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Recent Builds</h3>
            </div>
            <div className="card-content">
              <div className="build-list">
                <div className="build-item build-success">
                  <div className="build-icon">✅</div>
                  <div className="build-details">
                    <div className="build-name">E-commerce Platform</div>
                    <div className="build-time">5 minutes ago</div>
                  </div>
                </div>
                <div className="build-item build-success">
                  <div className="build-icon">✅</div>
                  <div className="build-details">
                    <div className="build-name">Analytics Dashboard</div>
                    <div className="build-time">1 hour ago</div>
                  </div>
                </div>
                <div className="build-item build-failed">
                  <div className="build-icon">❌</div>
                  <div className="build-details">
                    <div className="build-name">Payment Service</div>
                    <div className="build-time">2 hours ago</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
