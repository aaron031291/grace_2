import React, { useEffect, useMemo, useState } from 'react';
import { OverviewAPI } from '../api/overview';
import type {
  MetricsSummaryResponse,
  SelfHealingStatus,
  LearningStatus,
  MissionSummary,
  SnapshotSummary,
  RemoteStatus,
} from '../api/overview';
import './SystemOverviewPanel.css';

interface SystemOverviewPanelProps {
  remoteActive?: boolean;
  onToggleRemote?: () => void;
  onOpenTasks?: () => void;
  onOpenFileExplorer?: () => void;
}

const REFRESH_INTERVAL_MS = 8000;

const formatPercent = (value?: number) => `${Math.round((value ?? 0) * 100)}%`;

const formatTimestamp = (iso?: string) => {
  if (!iso) return '—';
  const date = new Date(iso);
  return isNaN(date.getTime()) ? '—' : date.toLocaleTimeString();
};

const formatDuration = (seconds?: number) => {
  if (!seconds && seconds !== 0) return '—';
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
};

export const SystemOverviewPanel: React.FC<SystemOverviewPanelProps> = ({
  remoteActive,
  onToggleRemote,
  onOpenTasks,
  onOpenFileExplorer,
}) => {
  const [metrics, setMetrics] = useState<MetricsSummaryResponse | null>(null);
  const [selfHealing, setSelfHealing] = useState<SelfHealingStatus | null>(null);
  const [learning, setLearning] = useState<LearningStatus | null>(null);
  const [missions, setMissions] = useState<MissionSummary[]>([]);
  const [snapshots, setSnapshots] = useState<SnapshotSummary[]>([]);
  const [remote, setRemote] = useState<RemoteStatus | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    const errors: string[] = [];
    try {
      const results = await Promise.allSettled([
        OverviewAPI.getMetricsSummary(),
        OverviewAPI.getSelfHealingStatus(),
        OverviewAPI.getLearningStatus(),
        OverviewAPI.getMissions(),
        OverviewAPI.getRecentSnapshots(4),
        OverviewAPI.getRemoteStatus(),
      ]);

      const [
        metricsResult,
        selfHealingResult,
        learningResult,
        missionsResult,
        snapshotsResult,
        remoteResult,
      ] = results;

      if (metricsResult.status === 'fulfilled') {
        setMetrics(metricsResult.value);
      } else {
        errors.push('metrics');
      }

      if (selfHealingResult.status === 'fulfilled') {
        setSelfHealing(selfHealingResult.value);
      } else {
        errors.push('self-healing');
      }

      if (learningResult.status === 'fulfilled') {
        setLearning(learningResult.value);
      } else {
        errors.push('learning');
      }

      if (missionsResult.status === 'fulfilled') {
        setMissions(missionsResult.value.missions || []);
      } else {
        errors.push('missions');
      }

      if (snapshotsResult.status === 'fulfilled') {
        setSnapshots(snapshotsResult.value.snapshots || []);
      } else {
        errors.push('snapshots');
      }

      if (remoteResult.status === 'fulfilled') {
        setRemote(remoteResult.value);
      } else {
        errors.push('remote');
      }

      setLastUpdated(new Date().toISOString());
      setError(errors.length ? `Partial data (missing: ${errors.join(', ')})` : null);
    } catch (err) {
      console.error('SystemOverviewPanel: loadData failed', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  const trustScore = useMemo(() => {
    if (!metrics) return 0;
    const { data } = metrics;
    return data?.trust ?? data?.trust_score ?? metrics.trust_score ?? 0;
  }, [metrics]);

  const confidenceScore = useMemo(() => {
    if (!metrics) return 0;
    const { data } = metrics;
    return data?.confidence ?? metrics.confidence ?? 0;
  }, [metrics]);

  const pendingApprovals = metrics?.data?.pending_approvals ?? metrics?.pending_approvals ?? 0;
  const activeTasks = metrics?.data?.active_tasks ?? metrics?.active_tasks ?? 0;
  const systemHealth = metrics?.data?.health ?? metrics?.data?.system_status ?? metrics?.health ?? metrics?.system_status ?? 'unknown';

  return (
    <section className="system-overview-panel">
      <div className="system-overview-header">
        <div>
          <h2>System Overview</h2>
          <p className="system-overview-subtitle">
            Unified health, healing, learning, and mission snapshot
          </p>
        </div>
        <div className="system-overview-actions">
          {lastUpdated && !loading && (
            <span className="last-updated">
              Updated {new Date(lastUpdated).toLocaleTimeString()}
            </span>
          )}
          <button className="ghost-button" onClick={loadData}>
            ⟳ Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="system-overview-error">
          ⚠️ {error}
        </div>
      )}

      <div className="system-overview-grid">
        <article className="overview-card overview-card--wide">
          <div className="overview-card-header">
            <h3>🏥 System Health</h3>
            <span className={`status-chip status-${systemHealth}`}>
              {systemHealth}
            </span>
          </div>
          <div className="metrics-row">
            <div className="metric-block">
              <div className="metric-label">Trust</div>
              <div className="metric-value">{formatPercent(trustScore)}</div>
              <div className="metric-bar">
                <div className="metric-fill" style={{ width: formatPercent(trustScore) }} />
              </div>
            </div>
            <div className="metric-block">
              <div className="metric-label">Confidence</div>
              <div className="metric-value">{formatPercent(confidenceScore)}</div>
              <div className="metric-bar">
                <div className="metric-fill" style={{ width: formatPercent(confidenceScore) }} />
              </div>
            </div>
            <div className="metric-block compact">
              <div className="metric-label">Approvals</div>
              <div className="metric-value small">{pendingApprovals}</div>
              <div className="metric-subtext">Pending</div>
            </div>
            <div className="metric-block compact">
              <div className="metric-label">Tasks</div>
              <div className="metric-value small">{activeTasks}</div>
              <div className="metric-subtext">Active</div>
            </div>
          </div>
        </article>

        <article className="overview-card">
          <div className="overview-card-header">
            <h3>🛠️ Self-Healing</h3>
            <span className={`status-chip status-${selfHealing?.status || 'unknown'}`}>
              {selfHealing?.status || 'unknown'}
            </span>
          </div>
          <ul className="overview-list">
            <li>
              <span>Active Playbooks</span>
              <strong>{selfHealing?.active_playbooks ?? '—'}</strong>
            </li>
            <li>
              <span>Incidents</span>
              <strong>{selfHealing?.incidents ?? '—'}</strong>
            </li>
            <li>
              <span>Last Run</span>
              <strong>{formatTimestamp(selfHealing?.last_run)}</strong>
            </li>
          </ul>
          <button className="outline-button" onClick={() => onOpenTasks?.()}>
            View Healing Queue
          </button>
        </article>

        <article className="overview-card">
          <div className="overview-card-header">
            <h3>🧠 Learning Loop</h3>
            <span className={`status-chip status-${learning?.status || 'unknown'}`}>
              {learning?.status || 'unknown'}
            </span>
          </div>
          <div className="learning-content">
            <p>
              Component: <strong>{learning?.component ?? '—'}</strong>
            </p>
            {learning?.error && (
              <p className="error-text">
                {learning.error}
              </p>
            )}
            <button className="outline-button" onClick={() => onOpenFileExplorer?.()}>
              Open Learning Memory
            </button>
          </div>
        </article>

        <article className="overview-card overview-card--missions">
          <div className="overview-card-header">
            <h3>🎯 Missions</h3>
            <span className="status-chip">
              {missions.length} active
            </span>
          </div>
          {missions.length === 0 ? (
            <p className="placeholder-text">No active missions</p>
          ) : (
            <ul className="mission-list">
              {missions.slice(0, 3).map((mission) => (
                <li key={mission.mission_id || mission.id}>
                  <div className="mission-title">
                    {mission.title || mission.name || mission.mission_id || 'Mission'}
                  </div>
                  <div className="mission-meta">
                    <span className={`badge badge-${(mission.status || 'unknown').toLowerCase()}`}>
                      {mission.status || 'unknown'}
                    </span>
                    {mission.progress !== undefined && (
                      <span className="mission-progress">
                        {Math.round(mission.progress)}%
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <button className="outline-button" onClick={() => onOpenTasks?.()}>
            View Missions
          </button>
        </article>

        <article className="overview-card">
          <div className="overview-card-header">
            <h3>📸 Snapshots</h3>
            <span className="status-chip">
              {snapshots.length} recent
            </span>
          </div>
          {snapshots.length === 0 ? (
            <p className="placeholder-text">No safe-hold snapshots found</p>
          ) : (
            <ul className="overview-list">
              {snapshots.slice(0, 3).map((snapshot) => (
                <li key={snapshot.id}>
                  <div>
                    <strong>{snapshot.snapshot_type}</strong>
                    <div className="snapshot-meta">
                      {snapshot.is_golden ? '⭐ Golden' : snapshot.status}
                      {snapshot.created_at && (
                        <span> · {new Date(snapshot.created_at).toLocaleTimeString()}</span>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="overview-card">
          <div className="overview-card-header">
            <h3>🛰️ Remote Access</h3>
            <span className={`status-chip status-${remote?.health || 'unknown'}`}>
              {remote?.health || 'unknown'}
            </span>
          </div>
          <ul className="overview-list">
            <li>
              <span>Uptime</span>
              <strong>{formatDuration(remote?.uptime_seconds)}</strong>
            </li>
            <li>
              <span>Memory</span>
              <strong>{remote ? `${remote.memory_usage_mb.toFixed(1)} MB` : '—'}</strong>
            </li>
            <li>
              <span>Learning Jobs</span>
              <strong>{remote?.learning_jobs ?? '—'}</strong>
            </li>
          </ul>
          <button
            className={`outline-button ${remoteActive ? 'outline-button--active' : ''}`}
            onClick={() => onToggleRemote?.()}
          >
            {remoteActive ? 'Disconnect Remote' : 'Start Remote'}
          </button>
        </article>
      </div>

      {loading && (
        <div className="system-overview-loading">
          <span>Loading overview…</span>
        </div>
      )}
    </section>
  );
};
