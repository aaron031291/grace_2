/**
 * Missions View
 * Shows current missions from /mission-control/missions
 */

import { useState, useEffect } from 'react';
import { fetchMissions, type Mission } from '../../services/missionApi';
import { getSubsystemTheme } from '../../utils/subsystemColors';
import './MissionsView.css';

export default function MissionsView() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  const loadMissions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchMissions({ limit: 50 });
      setMissions(data.missions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load missions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMissions();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadMissions, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredMissions = missions.filter(mission => {
    if (filter === 'active') {
      return ['open', 'in_progress', 'awaiting_validation'].includes(mission.status);
    }
    if (filter === 'completed') {
      return ['resolved', 'failed'].includes(mission.status);
    }
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return '#ffaa00';
      case 'in_progress': return '#00ccff';
      case 'awaiting_validation': return '#aa88ff';
      case 'resolved': return '#00aa44';
      case 'failed': return '#ff4444';
      default: return '#999';
    }
  };

  if (loading) {
    return (
      <div className="missions-view">
        <div className="loading-state">
          <div className="spinner">🔄</div>
          <div>Loading missions...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="missions-view">
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <div className="error-message">{error}</div>
          <button onClick={loadMissions} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="missions-view">
      <div className="missions-header">
        <div className="missions-stats">
          <div className="stat">
            <strong>{missions.length}</strong> Total
          </div>
          <div className="stat">
            <strong>{missions.filter(m => ['open', 'in_progress'].includes(m.status)).length}</strong> Active
          </div>
          <div className="stat">
            <strong>{missions.filter(m => m.status === 'resolved').length}</strong> Resolved
          </div>
        </div>

        <div className="missions-controls">
          <div className="filter-buttons">
            <button
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button
              className={filter === 'active' ? 'active' : ''}
              onClick={() => setFilter('active')}
            >
              Active
            </button>
            <button
              className={filter === 'completed' ? 'active' : ''}
              onClick={() => setFilter('completed')}
            >
              Completed
            </button>
          </div>

          <button onClick={loadMissions} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="missions-list">
        {filteredMissions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🎯</div>
            <div className="empty-message">No missions found</div>
            <div className="empty-hint">
              Missions will appear here as Grace works
            </div>
          </div>
        ) : (
          filteredMissions.map(mission => {
            const theme = getSubsystemTheme(mission.subsystem_id || 'unknown');

            return (
              <div
                key={mission.mission_id}
                className="mission-card"
                style={{ borderLeftColor: theme.color }}
              >
                <div className="mission-header">
                  <div className="mission-subsystem" style={{ color: theme.color }}>
                    {theme.icon} {mission.subsystem_id}
                  </div>
                  <div
                    className="mission-status"
                    style={{ background: getStatusColor(mission.status) }}
                  >
                    {mission.status.replace('_', ' ')}
                  </div>
                </div>

                <div className="mission-id">{mission.mission_id}</div>

                <div className="mission-meta">
                  <div className="meta-item">
                    <span className="meta-label">Severity:</span>
                    <span
                      className={`severity-badge severity-${mission.severity}`}
                    >
                      {mission.severity}
                    </span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Assigned:</span>
                    <span className="meta-value">{mission.assigned_to}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Created:</span>
                    <span className="meta-value">
                      {new Date(mission.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                {mission.symptoms_count && mission.symptoms_count > 0 && (
                  <div className="mission-symptoms">
                    {mission.symptoms_count} symptom{mission.symptoms_count !== 1 ? 's' : ''} detected
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
