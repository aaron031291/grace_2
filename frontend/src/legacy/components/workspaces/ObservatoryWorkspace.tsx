import type { Workspace } from '../../GraceEnterpriseUI';
import './WorkspaceCommon.css';

interface ObservatoryWorkspaceProps {
  workspace: Workspace;
}

export function ObservatoryWorkspace({ workspace }: ObservatoryWorkspaceProps) {
  return (
    <div className="workspace-container">
      <div className="workspace-header">
        <div className="workspace-title">
          <span className="workspace-icon">👁️</span>
          <h1>Observatory</h1>
        </div>
        <div className="workspace-actions">
          <button className="workspace-action-btn">Export Report</button>
          <button className="workspace-action-btn">Configure Alerts</button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="workspace-grid">
          {/* System Health Overview */}
          <div className="workspace-card workspace-card-wide">
            <div className="card-header">
              <h3>System Health Overview</h3>
            </div>
            <div className="card-content">
              <div className="health-overview-grid">
                <div className="health-metric-card">
                  <div className="health-metric-icon">💚</div>
                  <div className="health-metric-details">
                    <div className="health-metric-label">Health</div>
                    <div className="health-metric-value">79%</div>
                    <div className="health-metric-trend health-trend-up">↑ 5%</div>
                  </div>
                </div>
                <div className="health-metric-card">
                  <div className="health-metric-icon">🤝</div>
                  <div className="health-metric-details">
                    <div className="health-metric-label">Trust</div>
                    <div className="health-metric-value">75%</div>
                    <div className="health-metric-trend health-trend-down">↓ 2%</div>
                  </div>
                </div>
                <div className="health-metric-card">
                  <div className="health-metric-icon">💪</div>
                  <div className="health-metric-details">
                    <div className="health-metric-label">Confidence</div>
                    <div className="health-metric-value">73%</div>
                    <div className="health-metric-trend health-trend-up">↑ 3%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Components */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>System Components</h3>
            </div>
            <div className="card-content">
              <div className="component-list">
                <div className="component-item component-healthy">
                  <div className="component-status">🟢</div>
                  <div className="component-name">Guardian</div>
                  <div className="component-uptime">99.9%</div>
                </div>
                <div className="component-item component-healthy">
                  <div className="component-status">🟢</div>
                  <div className="component-name">Learning Engine</div>
                  <div className="component-uptime">99.7%</div>
                </div>
                <div className="component-item component-warning">
                  <div className="component-status">🟡</div>
                  <div className="component-name">Self-Healing</div>
                  <div className="component-uptime">95.2%</div>
                </div>
                <div className="component-item component-healthy">
                  <div className="component-status">🟢</div>
                  <div className="component-name">Copilot</div>
                  <div className="component-uptime">99.5%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Performance Metrics</h3>
            </div>
            <div className="card-content">
              <div className="performance-metrics">
                <div className="perf-metric-item">
                  <div className="perf-metric-label">API Latency (p95)</div>
                  <div className="perf-metric-value">142ms</div>
                </div>
                <div className="perf-metric-item">
                  <div className="perf-metric-label">Requests/sec</div>
                  <div className="perf-metric-value">1,247</div>
                </div>
                <div className="perf-metric-item">
                  <div className="perf-metric-label">Error Rate</div>
                  <div className="perf-metric-value">0.02%</div>
                </div>
                <div className="perf-metric-item">
                  <div className="perf-metric-label">CPU Usage</div>
                  <div className="perf-metric-value">42%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Events */}
          <div className="workspace-card">
            <div className="card-header">
              <h3>Recent Events</h3>
            </div>
            <div className="card-content">
              <div className="event-list">
                <div className="event-item event-info">
                  <div className="event-icon">ℹ️</div>
                  <div className="event-details">
                    <div className="event-title">System health improved</div>
                    <div className="event-time">5 minutes ago</div>
                  </div>
                </div>
                <div className="event-item event-warning">
                  <div className="event-icon">⚠️</div>
                  <div className="event-details">
                    <div className="event-title">High memory usage detected</div>
                    <div className="event-time">15 minutes ago</div>
                  </div>
                </div>
                <div className="event-item event-success">
                  <div className="event-icon">✅</div>
                  <div className="event-details">
                    <div className="event-title">Auto-healing completed</div>
                    <div className="event-time">1 hour ago</div>
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
