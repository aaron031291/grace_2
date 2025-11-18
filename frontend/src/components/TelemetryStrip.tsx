/**
 * Telemetry Strip
 * 
 * Compact status bar showing system health, learning jobs, missions, and remote heartbeat
 */

import React, { useState, useEffect } from 'react';
import { useNotifications } from '../hooks/useNotifications';
import { API_BASE_URL } from '../config';
import './TelemetryStrip.css';

interface MetricsSummary {
  health: string;
  trust_score: number;
  confidence: number;
  pending_approvals: number;
  active_tasks: number;
  system_status: string;
}

export const TelemetryStrip: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [learningJobs, setLearningJobs] = useState(0);
  const [activeMissions, setActiveMissions] = useState(0);
  const [remoteHeartbeat, setRemoteHeartbeat] = useState<string>('offline');
  const { notifications, connected } = useNotifications('user');

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Count learning-related notifications
    const learningCount = notifications.filter(n => 
      n.message.toLowerCase().includes('learn') || 
      n.message.toLowerCase().includes('training')
    ).length;
    setLearningJobs(learningCount);

    // Count mission notifications
    const missionCount = notifications.filter(n => 
      n.message.toLowerCase().includes('mission') || 
      n.message.toLowerCase().includes('task')
    ).length;
    setActiveMissions(missionCount);

    // Check remote heartbeat from notifications
    const remoteNotif = notifications.find(n => n.message.toLowerCase().includes('remote'));
    if (remoteNotif) {
      setRemoteHeartbeat('active');
    }
  }, [notifications]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/metrics/summary`);
      const data = await response.json();
      if (data.success && data.data) {
        setMetrics(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#4caf50';
      case 'degraded': return '#ff9800';
      case 'offline': return '#f44336';
      default: return '#888';
    }
  };

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✅';
      case 'degraded': return '⚠️';
      case 'offline': return '❌';
      default: return '⏸️';
    }
  };

  if (!metrics) {
    return (
      <div className="telemetry-strip loading">
        <span>Loading metrics...</span>
      </div>
    );
  }

  return (
    <div className="telemetry-strip">
      <div className="telemetry-item" title="System Health">
        <span className="telemetry-icon">{getHealthIcon(metrics.system_status)}</span>
        <span className="telemetry-label">Guardian</span>
        <span 
          className="telemetry-value"
          style={{ color: getHealthColor(metrics.system_status) }}
        >
          {metrics.system_status}
        </span>
      </div>

      <div className="telemetry-divider" />

      <div className="telemetry-item" title="Trust Score">
        <span className="telemetry-icon">🛡️</span>
        <span className="telemetry-label">Trust</span>
        <span className="telemetry-value">
          {(metrics.trust_score * 100).toFixed(0)}%
        </span>
      </div>

      <div className="telemetry-divider" />

      <div className="telemetry-item" title="Learning Jobs">
        <span className="telemetry-icon">📚</span>
        <span className="telemetry-label">Learning</span>
        <span className="telemetry-value">{learningJobs} jobs</span>
      </div>

      <div className="telemetry-divider" />

      <div className="telemetry-item" title="Active Missions">
        <span className="telemetry-icon">🎯</span>
        <span className="telemetry-label">Missions</span>
        <span className="telemetry-value">{activeMissions} active</span>
      </div>

      <div className="telemetry-divider" />

      <div className="telemetry-item" title="Remote Connection">
        <span className="telemetry-icon">🌐</span>
        <span className="telemetry-label">Remote</span>
        <span 
          className="telemetry-value"
          style={{ color: remoteHeartbeat === 'active' ? '#4caf50' : '#888' }}
        >
          {remoteHeartbeat}
        </span>
      </div>

      <div className="telemetry-divider" />

      <div className="telemetry-item" title="Pending Approvals">
        <span className="telemetry-icon">⚠️</span>
        <span className="telemetry-label">Pending</span>
        <span 
          className="telemetry-value"
          style={{ color: metrics.pending_approvals > 0 ? '#ff9800' : '#4caf50' }}
        >
          {metrics.pending_approvals}
        </span>
      </div>

      <div className="telemetry-divider" />

      <div className="telemetry-item" title="WebSocket Connection">
        <span className="telemetry-icon">{connected ? '🟢' : '🔴'}</span>
        <span className="telemetry-label">WS</span>
        <span className="telemetry-value">{connected ? 'live' : 'offline'}</span>
      </div>
    </div>
  );
};
