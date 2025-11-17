import { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface LearningWorkspaceProps {
  workspace: Workspace;
}

export function LearningWorkspace({ workspace }: LearningWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">🧠</span>
          <h1>Learning Engine</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">New Learning Job</button>
          <button className="workspace-action-btn">View Domains</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="workspace-grid">
          {/* Active Learning Jobs */}
          <div className="workspace-card workspace-card-wide">
            <div className="card-header">
              <h3>Active Learning Jobs</h3>
            </div>
            <div className="card-content">
              <div className="learning-job-list">
                <div className="learning-job-item">
                  <div className="job-icon">📚</div>
                  <div className="job-details">
                    <div className="job-title">Python Best Practices</div>
                    <div className="job-progress-bar">
                      <div className="job-progress-fill" style={{ width: '75%' }}></div>
                    </div>
                    <div className="job-meta">
                      <span>75% complete</span>
                      <span>~5 min remaining</span>
                    </div>
                  </div>
                  <button className="job-action-btn">View</button>
                </div>
                <div className="learning-job-item">
                  <div className="job-icon">🌐</div>
                  <div className="job-details">
                    <div className="job-title">Web Security Fundamentals</div>
                    <div className="job-progress-bar">
                      <div className="job-progress-fill" style={{ width: '40%' }}></div>
                    </div>
                    <div className="job-meta">
                      <span>40% complete</span>
                      <span>~12 min remaining</span>
                    </div>
                  </div>
                  <button className="job-action-btn">View</button>
                </div>
              </div>
            </div>
          </div>

          {/* Domain Knowledge */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Domain Knowledge</h3>
            </div>
            <div className="card-content">
              <div className="domain-list">
                <div className="domain-item">
                  <div className="domain-name">Python Development</div>
                  <div className="domain-confidence">
                    <div className="confidence-bar">
                      <div className="confidence-fill" style={{ width: '92%', background: 'var(--color-success)' }}></div>
                    </div>
                    <span className="confidence-value">92%</span>
                  </div>
                </div>
                <div className="domain-item">
                  <div className="domain-name">DevOps</div>
                  <div className="domain-confidence">
                    <div className="confidence-bar">
                      <div className="confidence-fill" style={{ width: '85%', background: 'var(--color-success)' }}></div>
                    </div>
                    <span className="confidence-value">85%</span>
                  </div>
                </div>
                <div className="domain-item">
                  <div className="domain-name">Web Security</div>
                  <div className="domain-confidence">
                    <div className="confidence-bar">
                      <div className="confidence-fill" style={{ width: '67%', background: 'var(--color-warning)' }}></div>
                    </div>
                    <span className="confidence-value">67%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Learning Stats */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Learning Statistics</h3>
            </div>
            <div className="card-content">
              <div className="learning-stats">
                <div className="stat-item">
                  <div className="stat-label">Jobs Completed</div>
                  <div className="stat-value">1,247</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Knowledge Entries</div>
                  <div className="stat-value">8,432</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Success Rate</div>
                  <div className="stat-value">94.2%</div>
                </div>
                <div className="stat-item">
                  <div className="stat-label">Avg Job Time</div>
                  <div className="stat-value">8.5 min</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
