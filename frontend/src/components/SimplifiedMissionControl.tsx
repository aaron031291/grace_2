import React, { useState } from 'react';
import './SimplifiedMissionControl.css';

type Tab = 'overview' | 'tasks' | 'playbooks' | 'learning' | 'evidence';

interface SimplifiedMissionControlProps {
  onClose?: () => void;
}

export const SimplifiedMissionControl: React.FC<SimplifiedMissionControlProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [showAlert, setShowAlert] = useState(true);

  // Mock data - replace with actual API calls
  const metrics = {
    health: 98,
    trust: 95,
    pendingApprovals: 3,
    activeTasks: 12,
    completedToday: 47,
  };

  const renderOverview = () => (
    <div className="mc-overview">
      <div className="mc-metrics-grid">
        <div className="mc-metric-card">
          <div className="mc-metric-icon">🛡️</div>
          <div className="mc-metric-content">
            <div className="mc-metric-value">{metrics.health}%</div>
            <div className="mc-metric-label">System Health</div>
          </div>
        </div>

        <div className="mc-metric-card">
          <div className="mc-metric-icon">⚖️</div>
          <div className="mc-metric-content">
            <div className="mc-metric-value">{metrics.trust}%</div>
            <div className="mc-metric-label">Trust Score</div>
          </div>
        </div>

        <div className="mc-metric-card clickable">
          <div className="mc-metric-icon">⏳</div>
          <div className="mc-metric-content">
            <div className="mc-metric-value">{metrics.pendingApprovals}</div>
            <div className="mc-metric-label">Pending Approvals</div>
          </div>
        </div>

        <div className="mc-metric-card">
          <div className="mc-metric-icon">⚙️</div>
          <div className="mc-metric-content">
            <div className="mc-metric-value">{metrics.activeTasks}</div>
            <div className="mc-metric-label">Active Tasks</div>
          </div>
        </div>

        <div className="mc-metric-card">
          <div className="mc-metric-icon">✅</div>
          <div className="mc-metric-content">
            <div className="mc-metric-value">{metrics.completedToday}</div>
            <div className="mc-metric-label">Completed Today</div>
          </div>
        </div>
      </div>

      <div className="mc-quick-actions">
        <h3 className="mc-section-title">Quick Actions</h3>
        <div className="mc-action-buttons">
          <button className="mc-action-btn primary">
            <span className="mc-btn-icon">🔧</span>
            Self-Heal
          </button>
          <button className="mc-action-btn">
            <span className="mc-btn-icon">📊</span>
            View Metrics
          </button>
          <button className="mc-action-btn">
            <span className="mc-btn-icon">🧠</span>
            Learning Status
          </button>
        </div>
      </div>
    </div>
  );

  const renderTasks = () => (
    <div className="mc-tasks">
      <div className="mc-task-list">
        <div className="mc-task-item">
          <div className="mc-task-status running"></div>
          <div className="mc-task-info">
            <div className="mc-task-name">Network Health Scan</div>
            <div className="mc-task-meta">Started 2m ago • Guardian</div>
          </div>
        </div>
        <div className="mc-task-item">
          <div className="mc-task-status completed"></div>
          <div className="mc-task-info">
            <div className="mc-task-name">Code Review - PR #42</div>
            <div className="mc-task-meta">Completed 5m ago • Coding Agent</div>
          </div>
        </div>
        <div className="mc-task-item">
          <div className="mc-task-status pending"></div>
          <div className="mc-task-info">
            <div className="mc-task-name">Memory Consolidation</div>
            <div className="mc-task-meta">Queued • Learning Agent</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPlaybooks = () => (
    <div className="mc-playbooks">
      <div className="mc-playbook-grid">
        <button className="mc-playbook-card">
          <div className="mc-playbook-icon">🔍</div>
          <div className="mc-playbook-name">System Diagnostic</div>
        </button>
        <button className="mc-playbook-card">
          <div className="mc-playbook-icon">🔧</div>
          <div className="mc-playbook-name">Auto-Repair</div>
        </button>
        <button className="mc-playbook-card">
          <div className="mc-playbook-icon">🧹</div>
          <div className="mc-playbook-name">Cleanup</div>
        </button>
        <button className="mc-playbook-card">
          <div className="mc-playbook-icon">📸</div>
          <div className="mc-playbook-name">Snapshot</div>
        </button>
      </div>
    </div>
  );

  const renderLearning = () => (
    <div className="mc-learning">
      <div className="mc-stat-row">
        <span className="mc-stat-label">Total Documents</span>
        <span className="mc-stat-value">1,247</span>
      </div>
      <div className="mc-stat-row">
        <span className="mc-stat-label">Embeddings Generated</span>
        <span className="mc-stat-value">89,432</span>
      </div>
      <div className="mc-stat-row">
        <span className="mc-stat-label">Last Update</span>
        <span className="mc-stat-value">2 hours ago</span>
      </div>
      <button className="mc-action-btn primary" style={{ marginTop: '1rem' }}>
        <span className="mc-btn-icon">⬇️</span>
        Download Learning Data
      </button>
    </div>
  );

  const renderEvidence = () => (
    <div className="mc-evidence">
      <div className="mc-evidence-item">
        <div className="mc-evidence-icon">📄</div>
        <div className="mc-evidence-info">
          <div className="mc-evidence-name">System Health Report</div>
          <div className="mc-evidence-date">Generated today at 09:30</div>
        </div>
      </div>
      <div className="mc-evidence-item">
        <div className="mc-evidence-icon">📊</div>
        <div className="mc-evidence-info">
          <div className="mc-evidence-name">Performance Analytics</div>
          <div className="mc-evidence-date">Generated yesterday</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="simplified-mission-control">
      {showAlert && (
        <div className="mc-alert">
          <span className="mc-alert-icon">ℹ️</span>
          <span className="mc-alert-text">Mission Control is running in demo mode</span>
          <button className="mc-alert-close" onClick={() => setShowAlert(false)}>✕</button>
        </div>
      )}

      <div className="mc-header">
        <div className="mc-header-content">
          <div>
            <h1 className="mc-title">Mission Control</h1>
            <p className="mc-subtitle">System overview and management</p>
          </div>
          {onClose && (
            <button className="mc-close-btn" onClick={onClose} title="Close Mission Control">
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="mc-tabs">
        <button
          className={`mc-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`mc-tab ${activeTab === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveTab('tasks')}
        >
          Tasks
        </button>
        <button
          className={`mc-tab ${activeTab === 'playbooks' ? 'active' : ''}`}
          onClick={() => setActiveTab('playbooks')}
        >
          Playbooks
        </button>
        <button
          className={`mc-tab ${activeTab === 'learning' ? 'active' : ''}`}
          onClick={() => setActiveTab('learning')}
        >
          Learning
        </button>
        <button
          className={`mc-tab ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          Evidence
        </button>
      </div>

      <div className="mc-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'tasks' && renderTasks()}
        {activeTab === 'playbooks' && renderPlaybooks()}
        {activeTab === 'learning' && renderLearning()}
        {activeTab === 'evidence' && renderEvidence()}
      </div>
    </div>
  );
};
