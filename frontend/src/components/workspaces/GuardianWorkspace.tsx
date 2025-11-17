import type { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface GuardianWorkspaceProps {
  workspace: Workspace;
}

export function GuardianWorkspace({ workspace }: GuardianWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">🛡️</span>
          <h1>Guardian</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">Run Network Scan</button>
          <button className="workspace-action-btn">View Playbooks</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="workspace-grid">
          {/* KPI Dashboard */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>System Health</h3>
            </div>
            <div className="card-content">
              <div className="kpi-grid">
                <div className="kpi-item">
                  <div className="kpi-label">Active Threats</div>
                  <div className="kpi-value kpi-error">3</div>
                </div>
                <div className="kpi-item">
                  <div className="kpi-label">Playbooks Run</div>
                  <div className="kpi-value">127</div>
                </div>
                <div className="kpi-item">
                  <div className="kpi-label">Success Rate</div>
                  <div className="kpi-value kpi-success">94%</div>
                </div>
                <div className="kpi-item">
                  <div className="kpi-label">Avg Response Time</div>
                  <div className="kpi-value">2.3s</div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Recent Alerts</h3>
              <button className="card-action-btn">View All</button>
            </div>
            <div className="card-content">
              <div className="alert-list">
                <div className="alert-item alert-critical">
                  <div className="alert-icon">🔴</div>
                  <div className="alert-details">
                    <div className="alert-title">Port scan detected</div>
                    <div className="alert-time">2 minutes ago</div>
                  </div>
                  <button className="alert-action-btn">Investigate</button>
                </div>
                <div className="alert-item alert-warning">
                  <div className="alert-icon">🟡</div>
                  <div className="alert-details">
                    <div className="alert-title">Unusual traffic pattern</div>
                    <div className="alert-time">15 minutes ago</div>
                  </div>
                  <button className="alert-action-btn">Investigate</button>
                </div>
                <div className="alert-item alert-info">
                  <div className="alert-icon">🔵</div>
                  <div className="alert-details">
                    <div className="alert-title">System update available</div>
                    <div className="alert-time">1 hour ago</div>
                  </div>
                  <button className="alert-action-btn">Review</button>
                </div>
              </div>
            </div>
          </div>

          {/* Active Playbooks */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Active Playbooks</h3>
            </div>
            <div className="card-content">
              <div className="playbook-list">
                <div className="playbook-item">
                  <div className="playbook-name">Network Monitoring</div>
                  <div className="playbook-status playbook-running">Running</div>
                </div>
                <div className="playbook-item">
                  <div className="playbook-name">Threat Detection</div>
                  <div className="playbook-status playbook-running">Running</div>
                </div>
                <div className="playbook-item">
                  <div className="playbook-name">Auto-Remediation</div>
                  <div className="playbook-status playbook-paused">Paused</div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Quick Actions</h3>
            </div>
            <div className="card-content">
              <div className="quick-actions-grid">
                <button className="quick-action-btn">
                  <span className="quick-action-icon">🔍</span>
                  <span className="quick-action-label">Scan Network</span>
                </button>
                <button className="quick-action-btn">
                  <span className="quick-action-icon">🛡️</span>
                  <span className="quick-action-label">Run Playbook</span>
                </button>
                <button className="quick-action-btn">
                  <span className="quick-action-icon">📊</span>
                  <span className="quick-action-label">View Logs</span>
                </button>
                <button className="quick-action-btn">
                  <span className="quick-action-icon">⚙️</span>
                  <span className="quick-action-label">Configure</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
