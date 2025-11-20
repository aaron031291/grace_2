/**
 * System Overview Dashboard
 * 
 * Consolidated view of all system components:
 * - Health & Trust Metrics
 * - Telemetry Strip
 * - Learning Status
 * - Mission Queue
 * - Snapshots
 * - Self-Healing Status
 * - Chaos Engineering
 * - Remote Access
 */

import React, { useState, useEffect } from 'react';
import { HealthMeter } from './HealthMeter';
import { TelemetryStrip } from './TelemetryStrip';
import { MetricsCharts } from './MetricsCharts';
import { MissionList } from './MissionList';
import { SelfHealingMetrics } from './SelfHealingMetrics';
import { SnapshotManagement } from './SnapshotManagement';
import { MissionControlAPI, type Mission } from '../api/missions';
import { SnapshotAPI, type Snapshot } from '../api/snapshots';
import { IncidentsAPI, type SelfHealingStats } from '../api/incidents';
import { ChaosAPI, type ChaosStatus } from '../api/chaos';
import './SystemDashboard.css';

interface LearningStatus {
  status: 'active' | 'paused' | 'disabled';
  total_artifacts: number;
  total_missions: number;
  knowledge_bases: number;
  active_sessions: number;
  last_updated: string;
}

interface RemoteAccessStatus {
  firefox_agent_running: boolean;
  active_sessions: number;
  last_heartbeat?: string;
}

export const SystemDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'missions' | 'healing' | 'snapshots'>('overview');
  const [learningStatus, setLearningStatus] = useState<LearningStatus | null>(null);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [selfHealingStats, setSelfHealingStats] = useState<SelfHealingStats | null>(null);
  const [chaosStatus, setChaosStatus] = useState<ChaosStatus | null>(null);
  const [remoteStatus, setRemoteStatus] = useState<RemoteAccessStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [
        learningData,
        missionsData,
        snapshotsData,
        healingStats,
        chaos,
        remoteData
      ] = await Promise.allSettled([
        fetch('http://localhost:8017/api/learning/status').then(r => r.ok ? r.json() : null),
        MissionControlAPI.listMissions({ limit: 20 }),
        SnapshotAPI.listSnapshots(),
        IncidentsAPI.getStats(),
        ChaosAPI.getStatus(),
        fetch('http://localhost:8017/api/pc/status').then(r => r.ok ? r.json() : null)
      ]);

      if (learningData.status === 'fulfilled') setLearningStatus(learningData.value);
      if (missionsData.status === 'fulfilled') setMissions(missionsData.value.missions || []);
      if (snapshotsData.status === 'fulfilled') setSnapshots(snapshotsData.value.snapshots || []);
      if (healingStats.status === 'fulfilled') setSelfHealingStats(healingStats.value);
      if (chaos.status === 'fulfilled') setChaosStatus(chaos.value);
      if (remoteData.status === 'fulfilled') {
        const data = remoteData.value;
        setRemoteStatus({
          firefox_agent_running: data?.firefox?.enabled || false,
          active_sessions: data?.active_sessions || 0,
          last_heartbeat: data?.last_heartbeat
        });
      }

      setLoading(false);
    } catch (err: any) {
      console.error('Dashboard fetch error:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Snapshot restore is handled by SnapshotManagement component

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="system-dashboard">
      <div className="dashboard-header">
        <h1>🎯 Grace System Overview</h1>
        <button className="refresh-btn" onClick={fetchDashboardData}>
          🔄 Refresh
        </button>
      </div>

      {/* Telemetry Strip */}
      <div className="dashboard-telemetry">
        <TelemetryStrip />
      </div>

      {/* Navigation Tabs */}
      <div className="dashboard-tabs">
        <button 
          className={`dashboard-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`dashboard-tab ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          📈 Metrics & Charts
        </button>
        <button 
          className={`dashboard-tab ${activeTab === 'missions' ? 'active' : ''}`}
          onClick={() => setActiveTab('missions')}
        >
          🎯 Mission List
        </button>
        <button 
          className={`dashboard-tab ${activeTab === 'healing' ? 'active' : ''}`}
          onClick={() => setActiveTab('healing')}
        >
          🔧 Self-Healing
        </button>
        <button 
          className={`dashboard-tab ${activeTab === 'snapshots' ? 'active' : ''}`}
          onClick={() => setActiveTab('snapshots')}
        >
          📸 Snapshots
        </button>
      </div>

      {error && <div className="dashboard-error">⚠️ {error}</div>}
      {loading && <div className="dashboard-loading">Loading system data...</div>}

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="dashboard-grid">
        {/* Health Meter - Full Width */}
        <div className="dashboard-section health-section">
          <HealthMeter />
        </div>

        {/* Learning Status Card */}
        <div className="dashboard-section learning-status-card">
          <h3>🎓 Learning System</h3>
          {learningStatus ? (
            <div className="learning-stats-grid">
              <div className="stat-box">
                <div className="stat-label">Status</div>
                <div className={`stat-value status-${learningStatus.status}`}>
                  {learningStatus.status === 'active' && '✅ Active'}
                  {learningStatus.status === 'paused' && '⏸️ Paused'}
                  {learningStatus.status === 'disabled' && '❌ Disabled'}
                </div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Artifacts</div>
                <div className="stat-value">{learningStatus.total_artifacts}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Missions</div>
                <div className="stat-value">{learningStatus.total_missions}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Knowledge Bases</div>
                <div className="stat-value">{learningStatus.knowledge_bases}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Active Sessions</div>
                <div className="stat-value">{learningStatus.active_sessions}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Last Updated</div>
                <div className="stat-value small">
                  {new Date(learningStatus.last_updated).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ) : (
            <div className="no-data">Learning data unavailable</div>
          )}
        </div>

        {/* Self-Healing Status Card */}
        <div className="dashboard-section healing-status-card">
          <h3>🔧 Self-Healing</h3>
          {selfHealingStats ? (
            <div className="healing-stats-grid">
              <div className="stat-box">
                <div className="stat-label">Total Incidents</div>
                <div className="stat-value">{selfHealingStats.total_incidents}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Active Now</div>
                <div className="stat-value active">{selfHealingStats.active_incidents}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Resolved Today</div>
                <div className="stat-value resolved">{selfHealingStats.resolved_today}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">MTTR</div>
                <div className="stat-value">{selfHealingStats.average_resolution_time.toFixed(1)}s</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Success Rate</div>
                <div className="stat-value">{(selfHealingStats.success_rate * 100).toFixed(0)}%</div>
              </div>
            </div>
          ) : (
            <div className="no-data">Self-healing data unavailable</div>
          )}
        </div>

        {/* Chaos Engineering Status */}
        <div className="dashboard-section chaos-status-card">
          <h3>🌀 Chaos Engineering</h3>
          {chaosStatus ? (
            <div className="chaos-stats-grid">
              <div className="stat-box">
                <div className="stat-label">Status</div>
                <div className={`stat-value ${chaosStatus.config.chaos_enabled ? 'active' : 'inactive'}`}>
                  {chaosStatus.config.chaos_enabled ? '✅ Running' : '⏸️ Paused'}
                </div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Active Campaigns</div>
                <div className="stat-value">{chaosStatus.active_campaigns}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Governance</div>
                <div className="stat-value">❌ Not Required</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Guardian Halt</div>
                <div className="stat-value">✅ Enabled</div>
              </div>
            </div>
          ) : (
            <div className="no-data">Chaos data unavailable</div>
          )}
        </div>

        {/* Remote Access Status */}
        <div className="dashboard-section remote-status-card">
          <h3>🌐 Remote Access</h3>
          {remoteStatus ? (
            <div className="remote-stats-grid">
              <div className="stat-box">
                <div className="stat-label">Firefox Agent</div>
                <div className={`stat-value ${remoteStatus.firefox_agent_running ? 'active' : 'inactive'}`}>
                  {remoteStatus.firefox_agent_running ? '🟢 Running' : '🔴 Stopped'}
                </div>
              </div>
              <div className="stat-box">
                <div className="stat-label">Active Sessions</div>
                <div className="stat-value">{remoteStatus.active_sessions}</div>
              </div>
              {remoteStatus.last_heartbeat && (
                <div className="stat-box">
                  <div className="stat-label">Last Heartbeat</div>
                  <div className="stat-value small">
                    {new Date(remoteStatus.last_heartbeat).toLocaleTimeString()}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="no-data">Remote access data unavailable</div>
          )}
        </div>

        {/* Mission Queue Table */}
        <div className="dashboard-section mission-queue-section">
          <h3>📋 Mission Queue ({missions.length})</h3>
          {missions.length > 0 ? (
            <div className="mission-queue-table">
              <table className="missions-compact-table">
                <thead>
                  <tr>
                    <th>Mission ID</th>
                    <th>Subsystem</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Started</th>
                  </tr>
                </thead>
                <tbody>
                  {missions.slice(0, 10).map((mission) => (
                    <tr key={mission.mission_id} className={`mission-row-compact severity-${mission.severity}`}>
                      <td className="mission-id-compact" title={mission.mission_id}>
                        {mission.mission_id.substring(0, 16)}...
                      </td>
                      <td>
                        <span className="subsystem-badge-compact">{mission.subsystem_id}</span>
                      </td>
                      <td>
                        <span className={`severity-badge-compact severity-${mission.severity}`}>
                          {mission.severity}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge-compact status-${mission.status}`}>
                          {mission.status}
                        </span>
                      </td>
                      <td className="time-compact">
                        {new Date(mission.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-data">No active missions</div>
          )}
        </div>

        {/* Snapshots Summary - Link to Snapshots Tab */}
        <div className="dashboard-section snapshots-card">
          <h3>📸 System Snapshots ({snapshots.length})</h3>
          <div className="snapshot-summary">
            <div className="summary-stats">
              <div className="summary-stat">
                <span className="summary-label">Total:</span>
                <span className="summary-value">{snapshots.length}</span>
              </div>
              <div className="summary-stat">
                <span className="summary-label">Latest:</span>
                <span className="summary-value">
                  {snapshots[0] ? new Date(snapshots[0].timestamp).toLocaleString() : 'N/A'}
                </span>
              </div>
            </div>
            <button 
              className="view-all-btn"
              onClick={() => setActiveTab('snapshots')}
            >
              📸 View All Snapshots →
            </button>
          </div>
        </div>
      </div>
      )}

      {/* Metrics & Charts Tab */}
      {activeTab === 'metrics' && (
        <div className="dashboard-tab-content">
          <MetricsCharts />
        </div>
      )}

      {/* Mission List Tab */}
      {activeTab === 'missions' && (
        <div className="dashboard-tab-content">
          <MissionList filter="all" limit={50} />
        </div>
      )}

      {/* Self-Healing Tab */}
      {activeTab === 'healing' && (
        <div className="dashboard-tab-content">
          <SelfHealingMetrics />
        </div>
      )}

      {/* Snapshots Tab */}
      {activeTab === 'snapshots' && (
        <div className="dashboard-tab-content">
          <SnapshotManagement />
        </div>
      )}
    </div>
  );
};
