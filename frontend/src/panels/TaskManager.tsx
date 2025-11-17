import { useState, useMemo } from 'react';
import { useMissions, useMissionDetails, useMissionStats } from '../hooks/useMissions';
import type { Mission, MissionDetail } from '../services/missionApi';
import './TaskManager.css';

const StatusCategories = {
  open: { label: 'Open', color: '#ffaa00' },
  in_progress: { label: 'In Progress', color: '#00ccff' },
  awaiting_validation: { label: 'Awaiting Validation', color: '#aa88ff' },
  observing: { label: 'Observing', color: '#00ff88' },
  resolved: { label: 'Resolved', color: '#00aa44' },
  escalated: { label: 'Escalated', color: '#ff4444' },
  failed: { label: 'Failed', color: '#ff0000' }
};

export default function TaskManager() {
  const [filterSeverity, setFilterSeverity] = useState<string>('');
  const [filterSubsystem, setFilterSubsystem] = useState<string>('');
  const [selectedMissionId, setSelectedMissionId] = useState<string | null>(null);

  // Use missions hook with filters
  const {
    missions,
    total,
    loading,
    error,
    isEmpty,
    refresh,
    executeMission: executeAction,
    acknowledgeMission,
    setAutoRefresh,
    setFilters,
  } = useMissions({
    filters: {
      severity: filterSeverity || undefined,
      subsystem_id: filterSubsystem || undefined,
      limit: 100,
    },
    autoRefresh: true,
    refreshInterval: 30000, // 30 seconds
    onError: (err) => {
      console.error('Mission error:', err);
    },
  });

  // Use mission details hook
  const {
    mission: selectedMission,
    loading: detailsLoading,
    error: detailsError,
  } = useMissionDetails(selectedMissionId);

  // Get mission statistics
  const stats = useMissionStats(missions);

  // Group missions by status
  const missionsByStatus = useMemo(() => {
    return missions.reduce((acc, mission) => {
      if (!acc[mission.status]) acc[mission.status] = [];
      acc[mission.status].push(mission);
      return acc;
    }, {} as Record<string, Mission[]>);
  }, [missions]);

  // Update filters when filter inputs change
  const handleSeverityChange = (severity: string) => {
    setFilterSeverity(severity);
    setFilters({
      severity: severity || undefined,
      subsystem_id: filterSubsystem || undefined,
      limit: 100,
    });
  };

  const handleSubsystemChange = (subsystem: string) => {
    setFilterSubsystem(subsystem);
    setFilters({
      severity: filterSeverity || undefined,
      subsystem_id: subsystem || undefined,
      limit: 100,
    });
  };

  const handleExecuteMission = async (missionId: string) => {
    try {
      await executeAction(missionId);
    } catch (err) {
      // Error already handled by hook's onError callback
    }
  };

  const handleAcknowledgeMission = async (missionId: string) => {
    try {
      await acknowledgeMission(missionId);
    } catch (err) {
      // Error already handled
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getSeverityClass = (severity: string) => `severity-${severity}`;
  const getStatusClass = (status: string) => `status-${status.replace('_', '-')}`;

  // Loading State
  if (loading && missions.length === 0) {
    return (
      <div className="task-manager-enhanced">
        <div className="task-header">
          <h2>Mission Control</h2>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading missions...</p>
        </div>
      </div>
    );
  }

  // Error State
  if (error && missions.length === 0) {
    return (
      <div className="task-manager-enhanced">
        <div className="task-header">
          <h2>Mission Control</h2>
        </div>
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Failed to load missions</h3>
          <p className="error-message">{error.message}</p>
          <button onClick={() => refresh()} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Empty State
  if (isEmpty) {
    return (
      <div className="task-manager-enhanced">
        <div className="task-header">
          <h2>Mission Control</h2>
          <div className="task-controls">
            <select 
              value={filterSeverity} 
              onChange={(e) => handleSeverityChange(e.target.value)}
              className="task-filter"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            <input
              type="text"
              placeholder="Filter by subsystem..."
              value={filterSubsystem}
              onChange={(e) => handleSubsystemChange(e.target.value)}
              className="task-search"
            />

            <button onClick={() => refresh()} className="refresh-btn">
              ↻ Refresh
            </button>
          </div>
        </div>
        <div className="empty-state">
          <div className="empty-icon">🎯</div>
          <h3>No missions found</h3>
          <p>
            {filterSeverity || filterSubsystem 
              ? 'Try adjusting your filters or create a new mission'
              : 'All systems are running smoothly. No active missions.'}
          </p>
          {(filterSeverity || filterSubsystem) && (
            <button 
              onClick={() => {
                setFilterSeverity('');
                setFilterSubsystem('');
                setFilters({ limit: 100 });
              }}
              className="clear-filters-btn"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>
    );
  }

  // Mission Card Component
  const MissionCard = ({ mission }: { mission: Mission }) => (
    <div className="mission-card" onClick={() => setSelectedMissionId(mission.mission_id)}>
      <div className="mission-card-header">
        <span className={`severity-badge ${getSeverityClass(mission.severity)}`}>
          {mission.severity.toUpperCase()}
        </span>
        <span className="mission-time">{formatDate(mission.created_at)}</span>
      </div>

      <div className="mission-card-body">
        <div className="mission-id">{mission.mission_id}</div>
        <div className="mission-subsystem">
          <span className="label">Subsystem:</span> {mission.subsystem_id}
        </div>
        <div className="mission-assigned">
          <span className="label">Assigned to:</span> {mission.assigned_to}
        </div>
        {mission.symptoms_count !== undefined && mission.symptoms_count > 0 && (
          <div className="mission-symptoms">
            {mission.symptoms_count} symptom{mission.symptoms_count !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      <div className="mission-card-actions">
        {mission.status === 'open' && (
          <button 
            onClick={(e) => {
              e.stopPropagation();
              handleExecuteMission(mission.mission_id);
            }}
            className="action-btn execute-btn"
          >
            Execute
          </button>
        )}
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setSelectedMissionId(mission.mission_id);
          }}
          className="action-btn details-btn"
        >
          Details
        </button>
      </div>
    </div>
  );

  // Main Render
  return (
    <div className="task-manager-enhanced">
      <div className="task-header">
        <h2>Mission Control</h2>
        <div className="task-stats">
          <span className="stat">
            <strong>{total}</strong> total
          </span>
          <span className="stat open">
            <strong>{stats.byStatus.open || 0}</strong> open
          </span>
          <span className="stat in-progress">
            <strong>{stats.byStatus.in_progress || 0}</strong> in progress
          </span>
        </div>
        <div className="task-controls">
          <select 
            value={filterSeverity} 
            onChange={(e) => handleSeverityChange(e.target.value)}
            className="task-filter"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <input
            type="text"
            placeholder="Filter by subsystem..."
            value={filterSubsystem}
            onChange={(e) => handleSubsystemChange(e.target.value)}
            className="task-search"
          />

          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              defaultChecked
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (30s)
          </label>

          <button onClick={() => refresh()} className="refresh-btn" disabled={loading}>
            {loading ? '⟳' : '↻'} Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error.message}</span>
          <button onClick={() => refresh()} className="dismiss-btn">Retry</button>
        </div>
      )}

      <div className="tasks-content">
        <div className="tasks-columns">
          {Object.entries(StatusCategories).map(([status, config]) => {
            const statusMissions = missionsByStatus[status] || [];
            if (statusMissions.length === 0) return null;

            return (
              <div key={status} className="status-column">
                <div className="column-header" style={{ borderTopColor: config.color }}>
                  <h3>{config.label}</h3>
                  <span className="mission-count">{statusMissions.length}</span>
                </div>
                <div className="column-missions">
                  {statusMissions.map(mission => (
                    <MissionCard key={mission.mission_id} mission={mission} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {selectedMission && (
          <div className="mission-detail-panel">
            <div className="detail-header">
              <h3>Mission Details</h3>
              <button onClick={() => setSelectedMissionId(null)} className="close-btn">
                ×
              </button>
            </div>

            {detailsLoading ? (
              <div className="detail-loading">
                <div className="loading-spinner"></div>
                <p>Loading details...</p>
              </div>
            ) : detailsError ? (
              <div className="detail-error">
                <p>Failed to load mission details</p>
                <button onClick={() => setSelectedMissionId(selectedMission.mission_id)}>
                  Retry
                </button>
              </div>
            ) : (
              <div className="detail-body">
                <div className="detail-section">
                  <div className="detail-row">
                    <span className="detail-label">Mission ID:</span>
                    <span className="detail-value mono">{selectedMission.mission_id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Status:</span>
                    <span className={`status-badge ${getStatusClass(selectedMission.status)}`}>
                      {StatusCategories[selectedMission.status]?.label || selectedMission.status}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Severity:</span>
                    <span className={`severity-badge ${getSeverityClass(selectedMission.severity)}`}>
                      {selectedMission.severity.toUpperCase()}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Subsystem:</span>
                    <span className="detail-value">{selectedMission.subsystem_id}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Detected by:</span>
                    <span className="detail-value">{selectedMission.detected_by}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Assigned to:</span>
                    <span className="detail-value">{selectedMission.assigned_to}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Created:</span>
                    <span className="detail-value">{new Date(selectedMission.created_at).toLocaleString()}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Updated:</span>
                    <span className="detail-value">{new Date(selectedMission.updated_at).toLocaleString()}</span>
                  </div>
                </div>

                {selectedMission.context && (
                  <div className="detail-section">
                    <h4>Context</h4>
                    <div className="detail-row">
                      <span className="detail-label">Environment:</span>
                      <span className="detail-value">{selectedMission.context.env}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Branch:</span>
                      <span className="detail-value mono">{selectedMission.context.branch || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Git SHA:</span>
                      <span className="detail-value mono">{selectedMission.context.git_sha.substring(0, 8)}</span>
                    </div>
                  </div>
                )}

                {selectedMission.symptoms && selectedMission.symptoms.length > 0 && (
                  <div className="detail-section">
                    <h4>Symptoms ({selectedMission.symptoms.length})</h4>
                    {selectedMission.symptoms.map((symptom, idx) => (
                      <div key={idx} className="symptom-card">
                        <div className="symptom-description">{symptom.description}</div>
                        {symptom.metric_id && (
                          <div className="symptom-metric">
                            Metric: <code>{symptom.metric_id}</code>
                            {symptom.observed_value !== undefined && (
                              <> = {symptom.observed_value} {symptom.threshold !== undefined && `(threshold: ${symptom.threshold})`}</>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {selectedMission.kpi_deltas && Object.keys(selectedMission.kpi_deltas).length > 0 && (
                  <div className="detail-section">
                    <h4>KPI Impact</h4>
                    {Object.entries(selectedMission.kpi_deltas).map(([key, value]) => (
                      <div key={key} className="kpi-delta-row">
                        <span className="kpi-name">{key}:</span>
                        <span className={value > 0 ? 'delta-positive' : 'delta-negative'}>
                          {value > 0 ? '+' : ''}{value}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="detail-actions">
                  {selectedMission.status === 'open' && (
                    <button 
                      onClick={() => handleExecuteMission(selectedMission.mission_id)}
                      className="action-btn execute-btn-large"
                    >
                      Execute Mission
                    </button>
                  )}
                  <button className="action-btn secondary-btn">
                    View Logs
                  </button>
                  <button className="action-btn secondary-btn">
                    Open Workspace
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
