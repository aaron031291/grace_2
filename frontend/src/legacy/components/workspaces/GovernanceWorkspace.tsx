import type { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface GovernanceWorkspaceProps {
  workspace: Workspace;
}

export function GovernanceWorkspace({ workspace }: GovernanceWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">⚖️</span>
          <h1>Governance</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">View Policies</button>
          <button className="workspace-action-btn">Audit Log</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="workspace-grid">
          {/* Pending Approvals */}
          <div className="workspace-card workspace-card-wide">
            <div className="card-header">
              <h3>Pending Approvals</h3>
              <span className="approval-count">5 pending</span>
            </div>
            <div className="card-content">
              <div className="approval-list">
                <div className="approval-item">
                  <div className="approval-icon tier-3">T3</div>
                  <div className="approval-details">
                    <div className="approval-title">Deploy to Production</div>
                    <div className="approval-meta">
                      <span className="approval-requester">Copilot</span>
                      <span className="approval-time">10 minutes ago</span>
                    </div>
                  </div>
                  <div className="approval-actions">
                    <button className="approval-btn approval-approve">Approve</button>
                    <button className="approval-btn approval-reject">Reject</button>
                    <button className="approval-btn approval-simulate">Simulate</button>
                  </div>
                </div>
                <div className="approval-item">
                  <div className="approval-icon tier-2">T2</div>
                  <div className="approval-details">
                    <div className="approval-title">Modify Database Schema</div>
                    <div className="approval-meta">
                      <span className="approval-requester">Learning Engine</span>
                      <span className="approval-time">1 hour ago</span>
                    </div>
                  </div>
                  <div className="approval-actions">
                    <button className="approval-btn approval-approve">Approve</button>
                    <button className="approval-btn approval-reject">Reject</button>
                    <button className="approval-btn approval-simulate">Simulate</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Policy Compliance */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Policy Compliance</h3>
            </div>
            <div className="card-content">
              <div className="compliance-stats">
                <div className="compliance-item">
                  <div className="compliance-label">Active Policies</div>
                  <div className="compliance-value">24</div>
                </div>
                <div className="compliance-item">
                  <div className="compliance-label">Violations (24h)</div>
                  <div className="compliance-value compliance-error">0</div>
                </div>
                <div className="compliance-item">
                  <div className="compliance-label">Compliance Rate</div>
                  <div className="compliance-value compliance-success">100%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Decisions */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Recent Decisions</h3>
            </div>
            <div className="card-content">
              <div className="decision-list">
                <div className="decision-item decision-approved">
                  <div className="decision-icon">✅</div>
                  <div className="decision-details">
                    <div className="decision-title">API Key Rotation</div>
                    <div className="decision-time">Approved 30m ago</div>
                  </div>
                </div>
                <div className="decision-item decision-rejected">
                  <div className="decision-icon">❌</div>
                  <div className="decision-details">
                    <div className="decision-title">Delete Production Data</div>
                    <div className="decision-time">Rejected 1h ago</div>
                  </div>
                </div>
                <div className="decision-item decision-approved">
                  <div className="decision-icon">✅</div>
                  <div className="decision-details">
                    <div className="decision-title">Update Dependencies</div>
                    <div className="decision-time">Approved 2h ago</div>
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
