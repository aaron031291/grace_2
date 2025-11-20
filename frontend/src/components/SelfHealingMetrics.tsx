/**
 * Self-Healing Metrics Component
 * 
 * Displays self-healing stats, incidents, playbooks, and actions
 */

import React, { useState, useEffect } from 'react';
import { 
  getSelfHealingStats, 
  getSelfHealingIncidents, 
  getSelfHealingPlaybooks,
  getRecentHealingActions,
  type SelfHealingStats,
  type Incident,
  type Playbook,
  type HealingAction
} from '../api/comprehensive';
import './SelfHealingMetrics.css';

export const SelfHealingMetrics: React.FC = () => {
  const [stats, setStats] = useState<SelfHealingStats | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [actions, setActions] = useState<HealingAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'incidents' | 'playbooks' | 'actions'>('incidents');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, incidentsData, playbooksData, actionsData] = await Promise.all([
        getSelfHealingStats(),
        getSelfHealingIncidents(20),
        getSelfHealingPlaybooks(),
        getRecentHealingActions(15)
      ]);

      setStats(statsData);
      setIncidents(incidentsData.incidents || []);
      setPlaybooks(playbooksData.playbooks || []);
      setActions(actionsData.actions || []);
    } catch (err: any) {
      console.error('Failed to fetch self-healing data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return <div className="sh-metrics-loading">Loading self-healing metrics...</div>;
  }

  if (error) {
    return <div className="sh-metrics-error">⚠️ {error}</div>;
  }

  return (
    <div className="self-healing-metrics">
      <div className="sh-header">
        <h2>🔧 Self-Healing Metrics</h2>
        <button className="refresh-btn" onClick={fetchData}>🔄 Refresh</button>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="sh-stats-grid">
          <div className="sh-stat-card">
            <div className="sh-stat-label">Total Incidents</div>
            <div className="sh-stat-value">{stats.total_incidents}</div>
          </div>
          <div className="sh-stat-card active">
            <div className="sh-stat-label">Active Now</div>
            <div className="sh-stat-value">{stats.active_incidents}</div>
          </div>
          <div className="sh-stat-card resolved">
            <div className="sh-stat-label">Resolved Today</div>
            <div className="sh-stat-value">{stats.resolved_today}</div>
          </div>
          <div className="sh-stat-card">
            <div className="sh-stat-label">Avg Resolution Time</div>
            <div className="sh-stat-value">{stats.average_resolution_time.toFixed(1)}s</div>
          </div>
          <div className="sh-stat-card success">
            <div className="sh-stat-label">Success Rate</div>
            <div className="sh-stat-value">{(stats.success_rate * 100).toFixed(0)}%</div>
            <div className="sh-stat-bar">
              <div 
                className="sh-stat-bar-fill"
                style={{ width: `${stats.success_rate * 100}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="sh-tabs">
        <button 
          className={`sh-tab ${activeTab === 'incidents' ? 'active' : ''}`}
          onClick={() => setActiveTab('incidents')}
        >
          🚨 Incidents ({incidents.length})
        </button>
        <button 
          className={`sh-tab ${activeTab === 'playbooks' ? 'active' : ''}`}
          onClick={() => setActiveTab('playbooks')}
        >
          📖 Playbooks ({playbooks.length})
        </button>
        <button 
          className={`sh-tab ${activeTab === 'actions' ? 'active' : ''}`}
          onClick={() => setActiveTab('actions')}
        >
          ⚡ Recent Actions ({actions.length})
        </button>
      </div>

      {/* Tab Content */}
      <div className="sh-tab-content">
        {activeTab === 'incidents' && (
          <div className="incidents-table">
            <table className="sh-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Component</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Detected At</th>
                  <th>Playbook</th>
                </tr>
              </thead>
              <tbody>
                {incidents.map((incident) => (
                  <tr key={incident.id} className={`incident-row severity-${incident.severity}`}>
                    <td className="incident-type">{incident.type}</td>
                    <td className="incident-component">{incident.component}</td>
                    <td>
                      <span className={`severity-badge severity-${incident.severity}`}>
                        {incident.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge status-${incident.status}`}>
                        {incident.status}
                      </span>
                    </td>
                    <td className="time-cell">
                      {new Date(incident.detected_at).toLocaleString()}
                    </td>
                    <td className="playbook-cell">{incident.playbook_applied || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'playbooks' && (
          <div className="playbooks-grid">
            {playbooks.map((playbook) => (
              <div key={playbook.id} className="playbook-card">
                <div className="playbook-header">
                  <h4>{playbook.name}</h4>
                  <span className="playbook-actions-count">{playbook.actions} actions</span>
                </div>
                <div className="playbook-description">{playbook.description}</div>
                <div className="playbook-stats">
                  <div className="playbook-stat">
                    <span className="label">Success Rate:</span>
                    <span className="value">{(playbook.success_rate * 100).toFixed(0)}%</span>
                  </div>
                  <div className="playbook-stat">
                    <span className="label">Avg Time:</span>
                    <span className="value">{playbook.avg_execution_time.toFixed(1)}s</span>
                  </div>
                </div>
                <div className="playbook-triggers">
                  <strong>Triggers:</strong>
                  {playbook.trigger_conditions.map((trigger, idx) => (
                    <span key={idx} className="trigger-tag">{trigger}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="actions-timeline">
            {actions.map((action, idx) => (
              <div key={idx} className={`action-event status-${action.status}`}>
                <div className="action-timestamp">
                  {new Date(action.timestamp).toLocaleString()}
                </div>
                <div className="action-incident">Incident: {action.incident_id}</div>
                <div className="action-description">{action.action}</div>
                <div className={`action-status status-${action.status}`}>
                  {action.status === 'running' && '⚙️ Running'}
                  {action.status === 'completed' && '✅ Completed'}
                  {action.status === 'failed' && '❌ Failed'}
                </div>
                {action.result && (
                  <div className="action-result">{action.result}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
