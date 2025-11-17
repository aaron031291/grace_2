import { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface MissionWorkspaceProps {
  workspace: Workspace;
}

export function MissionWorkspace({ workspace }: MissionWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">🎯</span>
          <h1>Mission Control</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">New Mission</button>
          <button className="workspace-action-btn">Mission Designer</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="workspace-grid">
          {/* Active Missions */}
          <div className="workspace-card workspace-card-wide">
            <div className="card-header">
              <h3>Active Missions</h3>
            </div>
            <div className="card-content">
              <div className="mission-list">
                <div className="mission-item">
                  <div className="mission-icon mission-running">▶️</div>
                  <div className="mission-details">
                    <div className="mission-title">Deploy E-commerce Platform</div>
                    <div className="mission-progress-bar">
                      <div className="mission-progress-fill" style={{ width: '60%' }}></div>
                    </div>
                    <div className="mission-meta">
                      <span>Step 3 of 5</span>
                      <span>~10 min remaining</span>
                    </div>
                  </div>
                  <button className="mission-action-btn">Monitor</button>
                </div>
                <div className="mission-item">
                  <div className="mission-icon mission-waiting">⏸️</div>
                  <div className="mission-details">
                    <div className="mission-title">Database Migration</div>
                    <div className="mission-meta">
                      <span>Waiting for approval</span>
                    </div>
                  </div>
                  <button className="mission-action-btn">Review</button>
                </div>
              </div>
            </div>
          </div>

          {/* Mission Stats */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Mission Statistics</h3>
            </div>
            <div className="card-content">
              <div className="mission-stats">
                <div className="stat-item">
                  <div className="stat-label">Total Missions</div>
                  <div className="stat-value">342</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Success Rate</div>
                  <div className="stat-value stat-success">96.8%</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Active Now</div>
                  <div className="stat-value">2</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Avg Duration</div>
                  <div className="stat-value">15.2 min</div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Missions */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Recent Missions</h3>
            </div>
            <div className="card-content">
              <div className="recent-mission-list">
                <div className="recent-mission-item mission-success">
                  <div className="recent-mission-icon">✅</div>
                  <div className="recent-mission-details">
                    <div className="recent-mission-title">API Deployment</div>
                    <div className="recent-mission-time">Completed 1h ago</div>
                  </div>
                </div>
                <div className="recent-mission-item mission-success">
                  <div className="recent-mission-icon">✅</div>
                  <div className="recent-mission-details">
                    <div className="recent-mission-title">Security Audit</div>
                    <div className="recent-mission-time">Completed 3h ago</div>
                  </div>
                </div>
                <div className="recent-mission-item mission-failed">
                  <div className="recent-mission-icon">❌</div>
                  <div className="recent-mission-details">
                    <div className="recent-mission-title">Load Test</div>
                    <div className="recent-mission-time">Failed 5h ago</div>
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
