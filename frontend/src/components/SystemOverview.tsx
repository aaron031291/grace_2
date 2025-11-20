/**
 * System Overview Panel - Tile Grid with Detail Drawers
 * 
 * Surfaces:
 * - Health & Trust tile
 * - Learning Status tile
 * - Mission Registry tile
 * - Self-Healing Timeline tile
 * - Snapshot Management tile
 * - Remote Access Controls tile
 * 
 * Quick Controls:
 * - Pause/Resume Learning (Google/Bing collectors)
 * - Remote Shell toggle
 */

import React, { useState, useEffect } from 'react';
import { RemoteAPI } from '../api/remote';
import { MissionControlAPI, type Mission } from '../api/missions';
import { SnapshotAPI, type Snapshot } from '../api/snapshots';
import { IncidentsAPI, type SelfHealingStats, type Incident } from '../api/incidents';
import { IngestionAPI, type IngestionStats, type IngestedFile } from '../api/ingestion';
import { API_BASE_URL } from '../config';
import './SystemOverview.css';

interface HealthMetrics {
  trust_score: number;
  guardian_score: number;
  health_score: number;
  uptime_percent: number;
}

interface LearningStatus {
  status: 'active' | 'paused' | 'disabled';
  google_enabled: boolean;
  bing_enabled: boolean;
  total_artifacts: number;
  pending_ingestion: number;
  last_updated: string;
}

interface RemoteAccessStatus {
  active: boolean;
  session_id?: string;
  firefox_agent_running: boolean;
  active_sessions: number;
  last_heartbeat?: string;
}

type DetailDrawer = 'health' | 'learning' | 'missions' | 'healing' | 'snapshots' | 'remote' | 'ingestion' | null;

export const SystemOverview: React.FC = () => {
  // State for tiles
  const [health, setHealth] = useState<HealthMetrics | null>(null);
  const [learning, setLearning] = useState<LearningStatus | null>(null);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [healingStats, setHealingStats] = useState<SelfHealingStats | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [remoteStatus, setRemoteStatus] = useState<RemoteAccessStatus | null>(null);
  const [ingestionStats, setIngestionStats] = useState<IngestionStats | null>(null);
  const [recentFiles, setRecentFiles] = useState<IngestedFile[]>([]);

  // State for drawers
  const [activeDrawer, setActiveDrawer] = useState<DetailDrawer>(null);
  
  // State for controls
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAllData();
    const interval = setInterval(loadAllData, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, []);

  const loadAllData = async () => {
    try {
      await Promise.all([
        loadHealth(),
        loadLearningStatus(),
        loadMissions(),
        loadIncidents(),
        loadSnapshots(),
        loadRemoteStatus(),
        loadIngestionStats()
      ]);
    } catch (err) {
      console.error('Failed to load overview data:', err);
    }
  };

  const loadHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/metrics/summary`);
      if (response.ok) {
        const data = await response.json();
        setHealth({
          trust_score: data.data?.trust_score || data.data?.trust || 0,
          guardian_score: data.data?.guardian_score || 0,
          health_score: data.data?.health || data.data?.health_score || 0,
          uptime_percent: data.data?.uptime_percent || 99.0
        });
      }
    } catch (err) {
      console.warn('Failed to load health metrics:', err);
    }
  };

  const loadLearningStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning/status`);
      if (response.ok) {
        const data = await response.json();
        setLearning({
          status: data.status || 'active',
          google_enabled: data.google_enabled ?? true,
          bing_enabled: data.bing_enabled ?? true,
          total_artifacts: data.total_artifacts || 0,
          pending_ingestion: data.pending_ingestion || 0,
          last_updated: data.last_updated || new Date().toISOString()
        });
      }
    } catch (err) {
      console.warn('Failed to load learning status:', err);
      // Set default state if endpoint doesn't exist
      setLearning({
        status: 'active',
        google_enabled: true,
        bing_enabled: true,
        total_artifacts: 0,
        pending_ingestion: 0,
        last_updated: new Date().toISOString()
      });
    }
  };

  const loadMissions = async () => {
    try {
      const data = await MissionControlAPI.listMissions();
      setMissions(data.missions || []);
    } catch (err) {
      console.warn('Failed to load missions:', err);
    }
  };

  const loadIncidents = async () => {
    try {
      const data = await IncidentsAPI.getIncidents(20);
      setIncidents(data.incidents || []);
      
      // Load stats separately
      const stats = await IncidentsAPI.getStats();
      setHealingStats(stats);
    } catch (err) {
      console.warn('Failed to load incidents:', err);
    }
  };

  const loadSnapshots = async () => {
    try {
      const data = await SnapshotAPI.listSnapshots();
      setSnapshots(data.snapshots || []);
    } catch (err) {
      console.warn('Failed to load snapshots:', err);
    }
  };

  const loadRemoteStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/remote/status`);
      if (response.ok) {
        const data = await response.json();
        setRemoteStatus({
          active: data.active || false,
          session_id: data.session_id,
          firefox_agent_running: data.firefox_agent_running || false,
          active_sessions: data.active_sessions || 0,
          last_heartbeat: data.last_heartbeat
        });
      }
    } catch (err) {
      console.warn('Failed to load remote status:', err);
      setRemoteStatus({
        active: false,
        firefox_agent_running: false,
        active_sessions: 0
      });
    }
  };

  const loadIngestionStats = async () => {
    try {
      const stats = await IngestionAPI.getStats();
      setIngestionStats(stats);
      
      // Load recent files for drawer
      const files = await IngestionAPI.getRecentFiles(10);
      setRecentFiles(files);
    } catch (err) {
      console.warn('Failed to load ingestion stats:', err);
    }
  };

  // Quick Controls
  const handleLearningToggle = async (collector: 'google' | 'bing' | 'all') => {
    setLoading(true);
    setError(null);

    try {
      const endpoint = collector === 'all' 
        ? `${API_BASE_URL}/api/learning/${learning?.status === 'active' ? 'pause' : 'resume'}`
        : `${API_BASE_URL}/api/learning/toggle/${collector}`;

      const response = await fetch(endpoint, { method: 'POST' });
      
      if (response.ok) {
        await loadLearningStatus();
      } else {
        throw new Error('Failed to toggle learning');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Learning toggle failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoteToggle = async () => {
    setLoading(true);
    setError(null);

    try {
      if (remoteStatus?.active && remoteStatus.session_id) {
        // Stop remote access
        await RemoteAPI.stopRemoteAccess(remoteStatus.session_id);
      } else {
        // Start remote access
        await RemoteAPI.startRemoteAccess('user');
      }
      
      await loadRemoteStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Remote toggle failed');
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 0.8) return '#27ae60';
    if (score >= 0.6) return '#f39c12';
    return '#e74c3c';
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      active: '#27ae60',
      paused: '#f39c12',
      disabled: '#95a5a6',
      pending: '#3498db',
      completed: '#27ae60',
      failed: '#e74c3c'
    };
    return colors[status] || '#95a5a6';
  };

  return (
    <div className="system-overview">
      <div className="overview-header">
        <h1>🎯 System Overview</h1>
        <div className="overview-controls">
          <button
            className={`quick-control ${learning?.status === 'active' ? 'active' : 'paused'}`}
            onClick={() => handleLearningToggle('all')}
            disabled={loading}
            title={learning?.status === 'active' ? 'Pause Learning' : 'Resume Learning'}
          >
            {learning?.status === 'active' ? '⏸️ Pause Learning' : '▶️ Resume Learning'}
          </button>
          <button
            className={`quick-control ${remoteStatus?.active ? 'active' : ''}`}
            onClick={handleRemoteToggle}
            disabled={loading}
            title={remoteStatus?.active ? 'Stop Remote Access' : 'Start Remote Access'}
          >
            {remoteStatus?.active ? '🔓 Remote Active' : '🔒 Remote Off'}
          </button>
        </div>
      </div>

      {error && (
        <div className="overview-error">
          ⚠️ {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Tile Grid */}
      <div className="overview-grid">
        {/* Health & Trust Tile */}
        <div className="overview-tile" onClick={() => setActiveDrawer('health')}>
          <div className="tile-icon">🏥</div>
          <div className="tile-content">
            <h3>Health & Trust</h3>
            <div className="tile-metrics">
              <div className="metric">
                <span className="metric-label">Trust</span>
                <span className="metric-value" style={{ color: getHealthColor(health?.trust_score || 0) }}>
                  {((health?.trust_score || 0) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Health</span>
                <span className="metric-value" style={{ color: getHealthColor(health?.health_score || 0) }}>
                  {((health?.health_score || 0) * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
          <div className="tile-expand">→</div>
        </div>

        {/* Learning Status Tile */}
        <div className="overview-tile" onClick={() => setActiveDrawer('learning')}>
          <div className="tile-icon">🧠</div>
          <div className="tile-content">
            <h3>Learning Status</h3>
            <div className="tile-status">
              <span 
                className="status-badge" 
                style={{ background: getStatusBadge(learning?.status || 'disabled') }}
              >
                {learning?.status || 'Unknown'}
              </span>
              <div className="tile-stats">
                <span>{learning?.total_artifacts || 0} artifacts</span>
                {learning && learning.pending_ingestion > 0 && (
                  <span className="pending">{learning.pending_ingestion} pending</span>
                )}
              </div>
            </div>
          </div>
          <div className="tile-expand">→</div>
        </div>

        {/* Mission Registry Tile */}
        <div className="overview-tile" onClick={() => setActiveDrawer('missions')}>
          <div className="tile-icon">🎯</div>
          <div className="tile-content">
            <h3>Mission Registry</h3>
            <div className="tile-stats">
              <span>{missions.length} total missions</span>
              <span>{missions.filter(m => m.status === 'in_progress').length} in progress</span>
              <span>{missions.filter(m => m.status === 'resolved').length} resolved</span>
            </div>
          </div>
          <div className="tile-expand">→</div>
        </div>

        {/* Self-Healing Timeline Tile */}
        <div className="overview-tile" onClick={() => setActiveDrawer('healing')}>
          <div className="tile-icon">🔧</div>
          <div className="tile-content">
            <h3>Self-Healing</h3>
            <div className="tile-stats">
              <span>{healingStats?.total_incidents || 0} total incidents</span>
              {healingStats && (
                <>
                  <span>{healingStats.resolved_today || 0} resolved today</span>
                  <span className="success-rate">
                    {(healingStats.success_rate * 100).toFixed(0)}% success
                  </span>
                </>
              )}
            </div>
          </div>
          <div className="tile-expand">→</div>
        </div>

        {/* Snapshot Management Tile */}
        <div className="overview-tile" onClick={() => setActiveDrawer('snapshots')}>
          <div className="tile-icon">📸</div>
          <div className="tile-content">
            <h3>Snapshots</h3>
            <div className="tile-stats">
              <span>{snapshots.length} available</span>
              {snapshots.length > 0 && (
                <span className="latest">
                  Latest: {new Date(snapshots[0]?.timestamp || '').toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
          <div className="tile-expand">→</div>
        </div>

        {/* Remote Access Controls Tile */}
        <div className="overview-tile" onClick={() => setActiveDrawer('remote')}>
          <div className="tile-icon">{remoteStatus?.active ? '🔓' : '🔒'}</div>
          <div className="tile-content">
            <h3>Remote Access</h3>
            <div className="tile-status">
              <span 
                className="status-badge" 
                style={{ background: remoteStatus?.active ? '#27ae60' : '#95a5a6' }}
              >
                {remoteStatus?.active ? 'Active' : 'Inactive'}
              </span>
              <div className="tile-stats">
                <span>{remoteStatus?.active_sessions || 0} sessions</span>
                {remoteStatus?.firefox_agent_running && <span>🦊 Firefox Agent</span>}
              </div>
            </div>
          </div>
          <div className="tile-expand">→</div>
        </div>

        {/* File Ingestion Tile */}
        <div className="overview-tile" onClick={() => setActiveDrawer('ingestion')}>
          <div className="tile-icon">📥</div>
          <div className="tile-content">
            <h3>File Ingestion</h3>
            <div className="tile-stats">
              <span>{ingestionStats?.total_files || 0} total files</span>
              <span>{ingestionStats?.recent_ingestions_7d || 0} this week</span>
              {ingestionStats && Object.keys(ingestionStats.by_modality).length > 0 && (
                <span className="modality-count">
                  {Object.keys(ingestionStats.by_modality).length} modalities
                </span>
              )}
            </div>
          </div>
          <div className="tile-expand">→</div>
        </div>
      </div>

      {/* Detail Drawers */}
      {activeDrawer && (
        <div className="detail-drawer-overlay" onClick={() => setActiveDrawer(null)}>
          <div className="detail-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <h2>
                {activeDrawer === 'health' && '🏥 Health & Trust Details'}
                {activeDrawer === 'learning' && '🧠 Learning Status Details'}
                {activeDrawer === 'missions' && '🎯 Mission Registry'}
                {activeDrawer === 'healing' && '🔧 Self-Healing Timeline'}
                {activeDrawer === 'snapshots' && '📸 Snapshot Management'}
                {activeDrawer === 'remote' && '🔒 Remote Access Controls'}
                {activeDrawer === 'ingestion' && '📥 File Ingestion'}
              </h2>
              <button className="drawer-close" onClick={() => setActiveDrawer(null)}>✕</button>
            </div>
            
            <div className="drawer-content">
              {activeDrawer === 'health' && <HealthDetails health={health} />}
              {activeDrawer === 'learning' && (
                <LearningDetails 
                  learning={learning} 
                  onToggle={handleLearningToggle}
                  loading={loading}
                />
              )}
              {activeDrawer === 'missions' && <MissionsDetails missions={missions} />}
              {activeDrawer === 'healing' && (
                <HealingDetails incidents={incidents} stats={healingStats} />
              )}
              {activeDrawer === 'snapshots' && <SnapshotsDetails snapshots={snapshots} />}
              {activeDrawer === 'remote' && (
                <RemoteDetails 
                  status={remoteStatus} 
                  onToggle={handleRemoteToggle}
                  loading={loading}
                />
              )}
              {activeDrawer === 'ingestion' && (
                <IngestionDetails stats={ingestionStats} files={recentFiles} />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Detail Components
const HealthDetails: React.FC<{ health: HealthMetrics | null }> = ({ health }) => (
  <div className="health-details">
    <div className="detail-metric">
      <span className="detail-label">Trust Score</span>
      <div className="detail-bar">
        <div 
          className="detail-bar-fill" 
          style={{ 
            width: `${(health?.trust_score || 0) * 100}%`,
            background: '#3498db'
          }}
        />
      </div>
      <span className="detail-value">{((health?.trust_score || 0) * 100).toFixed(1)}%</span>
    </div>
    
    <div className="detail-metric">
      <span className="detail-label">Guardian Score</span>
      <div className="detail-bar">
        <div 
          className="detail-bar-fill" 
          style={{ 
            width: `${(health?.guardian_score || 0) * 100}%`,
            background: '#27ae60'
          }}
        />
      </div>
      <span className="detail-value">{((health?.guardian_score || 0) * 100).toFixed(1)}%</span>
    </div>
    
    <div className="detail-metric">
      <span className="detail-label">System Health</span>
      <div className="detail-bar">
        <div 
          className="detail-bar-fill" 
          style={{ 
            width: `${(health?.health_score || 0) * 100}%`,
            background: '#f39c12'
          }}
        />
      </div>
      <span className="detail-value">{((health?.health_score || 0) * 100).toFixed(1)}%</span>
    </div>
    
    <div className="detail-metric">
      <span className="detail-label">Uptime</span>
      <span className="detail-value">{(health?.uptime_percent || 0).toFixed(2)}%</span>
    </div>
  </div>
);

const LearningDetails: React.FC<{
  learning: LearningStatus | null;
  onToggle: (collector: 'google' | 'bing' | 'all') => void;
  loading: boolean;
}> = ({ learning, onToggle, loading }) => (
  <div className="learning-details">
    <div className="detail-section">
      <h3>Collector Status</h3>
      <div className="collector-controls">
        <div className="collector-row">
          <span>Google Collector</span>
          <button
            className={`toggle-btn ${learning?.google_enabled ? 'active' : ''}`}
            onClick={() => onToggle('google')}
            disabled={loading}
          >
            {learning?.google_enabled ? '✓ Enabled' : '✕ Disabled'}
          </button>
        </div>
        <div className="collector-row">
          <span>Bing Collector</span>
          <button
            className={`toggle-btn ${learning?.bing_enabled ? 'active' : ''}`}
            onClick={() => onToggle('bing')}
            disabled={loading}
          >
            {learning?.bing_enabled ? '✓ Enabled' : '✕ Disabled'}
          </button>
        </div>
      </div>
    </div>
    
    <div className="detail-section">
      <h3>Statistics</h3>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-label">Total Artifacts</span>
          <span className="stat-value">{learning?.total_artifacts || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Pending Ingestion</span>
          <span className="stat-value">{learning?.pending_ingestion || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Last Updated</span>
          <span className="stat-value">
            {learning?.last_updated 
              ? new Date(learning.last_updated).toLocaleString() 
              : 'N/A'}
          </span>
        </div>
      </div>
    </div>
  </div>
);

const MissionsDetails: React.FC<{ missions: Mission[] }> = ({ missions }) => (
  <div className="missions-details">
    {missions.length === 0 ? (
      <p className="empty-state">No missions found</p>
    ) : (
      <div className="missions-list">
        {missions.slice(0, 10).map((mission) => (
          <div key={mission.mission_id} className="mission-item">
            <div className="mission-header">
              <span className="mission-name">{mission.subsystem_id}</span>
              <span className={`mission-status status-${mission.status}`}>
                {mission.status}
              </span>
            </div>
            <div className="mission-meta">
              <span>Created: {new Date(mission.created_at).toLocaleDateString()}</span>
              {mission.resolved_at && (
                <span>Resolved: {new Date(mission.resolved_at).toLocaleDateString()}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

const HealingDetails: React.FC<{
  incidents: Incident[];
  stats: SelfHealingStats | null;
}> = ({ incidents, stats }) => (
  <div className="healing-details">
    <div className="healing-stats">
      <div className="stat-card">
        <span className="stat-label">Total Incidents</span>
        <span className="stat-value">{stats?.total_incidents || 0}</span>
      </div>
      <div className="stat-card">
        <span className="stat-label">Active</span>
        <span className="stat-value">{stats?.active_incidents || 0}</span>
      </div>
      <div className="stat-card">
        <span className="stat-label">Resolved Today</span>
        <span className="stat-value success">{stats?.resolved_today || 0}</span>
      </div>
      <div className="stat-card">
        <span className="stat-label">Success Rate</span>
        <span className="stat-value">
          {((stats?.success_rate || 0) * 100).toFixed(0)}%
        </span>
      </div>
    </div>
    
    <div className="incidents-timeline">
      <h3>Recent Incidents</h3>
      {incidents.slice(0, 5).map((incident) => (
        <div key={incident.id} className="incident-item">
          <div className="incident-header">
            <span className="incident-type">{incident.type}</span>
            <span className="incident-time">
              {new Date(incident.detected_at).toLocaleString()}
            </span>
          </div>
          <div className="incident-message">{incident.error_message || 'No details'}</div>
          {incident.status === 'resolved' && (
            <div className="incident-badge success">✓ Resolved</div>
          )}
        </div>
      ))}
    </div>
  </div>
);

const SnapshotsDetails: React.FC<{ snapshots: Snapshot[] }> = ({ snapshots }) => (
  <div className="snapshots-details">
    {snapshots.length === 0 ? (
      <p className="empty-state">No snapshots available</p>
    ) : (
      <div className="snapshots-list">
        {snapshots.map((snapshot) => (
          <div key={snapshot.snapshot_id} className="snapshot-item">
            <div className="snapshot-header">
              <span className="snapshot-label">{snapshot.label || 'Unlabeled'}</span>
              <span className="snapshot-date">
                {new Date(snapshot.timestamp).toLocaleString()}
              </span>
            </div>
            {snapshot.description && (
              <div className="snapshot-description">{snapshot.description}</div>
            )}
            <div className="snapshot-meta">
              <span>Size: {snapshot.size_mb ? snapshot.size_mb.toFixed(2) : '0.00'} MB</span>
              <span className={`badge ${snapshot.verified_ok ? 'success' : 'warning'}`}>
                {snapshot.verified_ok ? '✓ Verified' : '⚠ Unverified'}
              </span>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

const RemoteDetails: React.FC<{
  status: RemoteAccessStatus | null;
  onToggle: () => void;
  loading: boolean;
}> = ({ status, onToggle, loading }) => (
  <div className="remote-details">
    <div className="remote-status-card">
      <h3>Connection Status</h3>
      <div className="status-indicator">
        <span className={`status-dot ${status?.active ? 'active' : 'inactive'}`} />
        <span className="status-text">
          {status?.active ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      <button
        className={`remote-toggle-btn ${status?.active ? 'disconnect' : 'connect'}`}
        onClick={onToggle}
        disabled={loading}
      >
        {loading ? '⏳ Processing...' : status?.active ? '🔒 Disconnect' : '🔓 Connect'}
      </button>
    </div>
    
    <div className="remote-info">
      {status?.session_id && (
        <div className="info-row">
          <span className="info-label">Session ID</span>
          <span className="info-value">{status.session_id.slice(0, 16)}...</span>
        </div>
      )}
      <div className="info-row">
        <span className="info-label">Active Sessions</span>
        <span className="info-value">{status?.active_sessions || 0}</span>
      </div>
      <div className="info-row">
        <span className="info-label">Firefox Agent</span>
        <span className="info-value">
          {status?.firefox_agent_running ? '✓ Running' : '✕ Stopped'}
        </span>
      </div>
      {status?.last_heartbeat && (
        <div className="info-row">
          <span className="info-label">Last Heartbeat</span>
          <span className="info-value">
            {new Date(status.last_heartbeat).toLocaleString()}
          </span>
        </div>
      )}
    </div>
  </div>
);

const IngestionDetails: React.FC<{
  stats: IngestionStats | null;
  files: IngestedFile[];
}> = ({ stats, files }) => (
  <div className="ingestion-details">
    <div className="ingestion-stats">
      <div className="stat-card">
        <span className="stat-label">Total Files</span>
        <span className="stat-value">{stats?.total_files || 0}</span>
      </div>
      <div className="stat-card">
        <span className="stat-label">This Week</span>
        <span className="stat-value success">{stats?.recent_ingestions_7d || 0}</span>
      </div>
      <div className="stat-card">
        <span className="stat-label">Avg Trust Score</span>
        <span className="stat-value">
          {((stats?.average_trust_score || 0) * 100).toFixed(0)}%
        </span>
      </div>
      <div className="stat-card">
        <span className="stat-label">Total Chunks</span>
        <span className="stat-value">{stats?.total_chunks || 0}</span>
      </div>
    </div>
    
    {stats && Object.keys(stats.by_modality).length > 0 && (
      <div className="detail-section">
        <h3>By Modality</h3>
        <div className="modality-breakdown">
          {Object.entries(stats.by_modality).map(([modality, count]) => (
            <div key={modality} className="modality-item">
              <span className="modality-name">{modality}</span>
              <span className="modality-count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    )}
    
    <div className="detail-section">
      <h3>Recent Files</h3>
      {files.length === 0 ? (
        <p className="empty-state">No files ingested yet</p>
      ) : (
        <div className="files-list">
          {files.map((file) => (
            <div key={file.document_id} className="file-item">
              <div className="file-header">
                <span className="file-title">{file.title}</span>
                <span className={`file-modality modality-${file.modality}`}>
                  {file.modality}
                </span>
              </div>
              <div className="file-meta">
                <span>Trust: {(file.trust_score * 100).toFixed(0)}%</span>
                <span>{new Date(file.ingested_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
);
