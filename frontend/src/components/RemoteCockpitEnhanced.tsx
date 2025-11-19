/**
 * Enhanced Remote Cockpit - High-Level Dashboard
 * 
 * Shows:
 * - Guardian health status
 * - Learning backlog
 * - Upcoming reminders
 * - System metrics
 */

import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import './RemoteCockpit.css';

interface GuardianHealth {
  status: string;
  last_check: string;
  anomalies: number;
  threats_detected: number;
  uptime_percent: number;
}

interface LearningBacklog {
  total_items: number;
  pending_ingestion: number;
  pending_analysis: number;
  failed_items: number;
}

interface Reminder {
  id: string;
  message: string;
  scheduled_time: string;
  priority: string;
}

interface RemoteCockpitProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RemoteCockpit: React.FC<RemoteCockpitProps> = ({ isOpen, onClose }) => {
  const [guardianHealth, setGuardianHealth] = useState<GuardianHealth | null>(null);
  const [learningBacklog, setLearningBacklog] = useState<LearningBacklog | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadDashboard();
      const interval = setInterval(loadDashboard, 10000); // Refresh every 10s
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await Promise.all([
        loadGuardianHealth(),
        loadLearningBacklog(),
        loadReminders(),
        loadSystemMetrics()
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const loadGuardianHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/metrics/health`);
      if (response.ok) {
        const data = await response.json();
        setGuardianHealth({
          status: data.status || 'healthy',
          last_check: data.timestamp || new Date().toISOString(),
          anomalies: data.anomalies_detected || 0,
          threats_detected: data.threats_detected || 0,
          uptime_percent: data.uptime_percent || 99.9
        });
      }
    } catch (err) {
      console.warn('Failed to load guardian health:', err);
    }
  };

  const loadLearningBacklog = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/memory/files/ingestions`);
      if (response.ok) {
        const data = await response.json();
        const pending = data.filter((i: any) => i.status === 'queued' || i.status === 'processing');
        const failed = data.filter((i: any) => i.status === 'failed');
        
        setLearningBacklog({
          total_items: data.length,
          pending_ingestion: pending.filter((i: any) => i.status === 'queued').length,
          pending_analysis: pending.filter((i: any) => i.status === 'processing').length,
          failed_items: failed.length
        });
      }
    } catch (err) {
      console.warn('Failed to load learning backlog:', err);
    }
  };

  const loadReminders = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/reminders`);
      if (response.ok) {
        const data = await response.json();
        // Get upcoming reminders (next 24 hours)
        const upcoming = data.filter((r: any) => {
          const scheduledTime = new Date(r.scheduled_time);
          const now = new Date();
          const hoursDiff = (scheduledTime.getTime() - now.getTime()) / (1000 * 60 * 60);
          return hoursDiff > 0 && hoursDiff < 24;
        });
        setReminders(upcoming.slice(0, 5)); // Top 5 upcoming
      }
    } catch (err) {
      console.warn('Failed to load reminders:', err);
    }
  };

  const loadSystemMetrics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/metrics/summary`);
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data);
      }
    } catch (err) {
      console.warn('Failed to load system metrics:', err);
    }
  };

  const getHealthColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return '#4caf50';
      case 'warning': return '#ff9800';
      case 'critical': return '#f44336';
      default: return '#757575';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="remote-cockpit">
      <div className="cockpit-overlay" onClick={onClose} />
      <div className="cockpit-panel">
        <div className="cockpit-header">
          <h2>🎛️ Grace Cockpit</h2>
          <button className="cockpit-close" onClick={onClose}>×</button>
        </div>

        <div className="cockpit-content">
          {loading && !guardianHealth && (
            <div className="cockpit-loading">Loading dashboard...</div>
          )}

          {error && (
            <div className="cockpit-error">
              ⚠️ {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {/* Guardian Health */}
          <div className="dashboard-section">
            <h3>🛡️ Guardian Health</h3>
            {guardianHealth ? (
              <div className="health-card">
                <div className="health-status" style={{ borderColor: getHealthColor(guardianHealth.status) }}>
                  <div className="health-indicator" style={{ backgroundColor: getHealthColor(guardianHealth.status) }}>
                    {guardianHealth.status.toUpperCase()}
                  </div>
                  <div className="health-metrics">
                    <div className="metric">
                      <span className="metric-label">Uptime</span>
                      <span className="metric-value">{guardianHealth.uptime_percent}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Anomalies</span>
                      <span className="metric-value">{guardianHealth.anomalies}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Threats</span>
                      <span className="metric-value">{guardianHealth.threats_detected}</span>
                    </div>
                  </div>
                </div>
                <div className="health-last-check">
                  Last check: {new Date(guardianHealth.last_check).toLocaleString()}
                </div>
              </div>
            ) : (
              <div className="section-empty">No health data available</div>
            )}
          </div>

          {/* Learning Backlog */}
          <div className="dashboard-section">
            <h3>📚 Learning Backlog</h3>
            {learningBacklog ? (
              <div className="backlog-card">
                <div className="backlog-stats">
                  <div className="stat-item">
                    <span className="stat-icon">📥</span>
                    <div className="stat-info">
                      <div className="stat-value">{learningBacklog.pending_ingestion}</div>
                      <div className="stat-label">Queued</div>
                    </div>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">⚙️</span>
                    <div className="stat-info">
                      <div className="stat-value">{learningBacklog.pending_analysis}</div>
                      <div className="stat-label">Processing</div>
                    </div>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">❌</span>
                    <div className="stat-info">
                      <div className="stat-value">{learningBacklog.failed_items}</div>
                      <div className="stat-label">Failed</div>
                    </div>
                  </div>
                </div>
                <div className="backlog-total">
                  Total: {learningBacklog.total_items} items in backlog
                </div>
              </div>
            ) : (
              <div className="section-empty">No backlog data available</div>
            )}
          </div>

          {/* Upcoming Reminders */}
          <div className="dashboard-section">
            <h3>🔔 Upcoming Reminders</h3>
            {reminders.length > 0 ? (
              <div className="reminders-list">
                {reminders.map((reminder) => (
                  <div key={reminder.id} className="reminder-item">
                    <span className="reminder-priority" data-priority={reminder.priority}>
                      {reminder.priority === 'high' ? '🔴' : reminder.priority === 'medium' ? '🟡' : '🟢'}
                    </span>
                    <div className="reminder-content">
                      <div className="reminder-message">{reminder.message}</div>
                      <div className="reminder-time">
                        {new Date(reminder.scheduled_time).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="section-empty">No upcoming reminders</div>
            )}
          </div>

          {/* System Metrics */}
          {systemMetrics && (
            <div className="dashboard-section">
              <h3>📊 System Metrics</h3>
              <div className="metrics-grid">
                {systemMetrics.active_sessions !== undefined && (
                  <div className="metric-card">
                    <div className="metric-card-value">{systemMetrics.active_sessions}</div>
                    <div className="metric-card-label">Active Sessions</div>
                  </div>
                )}
                {systemMetrics.total_queries !== undefined && (
                  <div className="metric-card">
                    <div className="metric-card-value">{systemMetrics.total_queries}</div>
                    <div className="metric-card-label">Total Queries</div>
                  </div>
                )}
                {systemMetrics.avg_response_time !== undefined && (
                  <div className="metric-card">
                    <div className="metric-card-value">{systemMetrics.avg_response_time}ms</div>
                    <div className="metric-card-label">Avg Response Time</div>
                  </div>
                )}
                {systemMetrics.error_rate !== undefined && (
                  <div className="metric-card">
                    <div className="metric-card-value">{systemMetrics.error_rate}%</div>
                    <div className="metric-card-label">Error Rate</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="cockpit-footer">
          <button className="cockpit-refresh-btn" onClick={loadDashboard}>
            🔄 Refresh Dashboard
          </button>
          <span className="cockpit-last-update">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
};
