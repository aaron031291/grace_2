import { useState, useEffect, useCallback } from 'react';
import './TaskManager.enhanced.css';

interface Mission {
  mission_id: string;
  subsystem_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'awaiting_validation' | 'observing' | 'resolved' | 'escalated' | 'failed';
  detected_by: string;
  assigned_to: string;
  created_at: string;
  updated_at: string;
  symptoms_count?: number;
  remediation_events_count?: number;
}

interface MissionDetail extends Mission {
  context?: {
    git_sha: string;
    config_hash: string;
    env: string;
    branch?: string;
    version?: string;
  };
  symptoms?: Array<{
    description: string;
    metric_id?: string;
    observed_value?: number;
    threshold?: number;
  }>;
  workspace?: {
    repo_path: string;
    working_branch: string;
  };
}

const API_BASE = 'http://localhost:8017';
const REFRESH_INTERVAL = 5000;

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
  const [missions, setMissions] = useState<Mission[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<string>('');
  const [filterSubsystem, setFilterSubsystem] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [selectedMission, setSelectedMission] = useState<MissionDetail | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
    'Content-Type': 'application/json'
  });

  const fetchMissions = useCallback(async (showLoading = true) => {
    if (showLoading) setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterSeverity) params.append('severity', filterSeverity);
      if (filterSubsystem) params.append('subsystem_id', filterSubsystem);
      params.append('limit', '100');

      const response = await fetch(`${API_BASE}/mission-control/missions?${params}`, {
        headers: getAuthHeaders()
      });
      
      if (!response.ok) throw new Error('Failed to fetch missions');
      
      const data = await response.json();
      setMissions(data.missions || []);
    } catch (error) {
      console.error('Failed to fetch missions:', error);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, [filterSeverity, filterSubsystem]);

  const fetchMissionDetails = async (missionId: string) => {
    try {
      const response = await fetch(`${API_BASE}/mission-control/missions/${missionId}`, {
        headers: getAuthHeaders()
      });
      
      if (!response.ok) throw new Error('Failed to fetch mission details');
      
      const data = await response.json();
      setSelectedMission(data);
    } catch (error) {
      console.error('Failed to fetch mission details:', error);
    }
  };

  const executeMission = async (missionId: string, missionType: 'coding' | 'healing' = 'coding') => {
    try {
      setMissions(prev => prev.map(m => 
        m.mission_id === missionId 
          ? { ...m, status: 'in_progress' } 
          : m
      ));

      const response = await fetch(`${API_BASE}/mission-control/missions/${missionId}/execute`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ mission_type: missionType })
      });

      if (!response.ok) {
        throw new Error('Failed to execute mission');
      }

      await fetchMissions(false);
      
      if (selectedMission?.mission_id === missionId) {
        await fetchMissionDetails(missionId);
      }
    } catch (error) {
      console.error('Failed to execute mission:', error);
      fetchMissions(false);
    }
  };

  const requestMissionDetails = (mission: Mission) => {
    fetchMissionDetails(mission.mission_id);
  };

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => fetchMissions(false), REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchMissions]);

  const missionsByStatus = missions.reduce((acc, mission) => {
    if (!acc[mission.status]) acc[mission.status] = [];
    acc[mission.status].push(mission);
    return acc;
  }, {} as Record<string, Mission[]>);

  const getSeverityClass = (severity: string) => `severity-${severity}`;
  const getStatusClass = (status: string) => `status-${status.replace('_', '-')}`;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const MissionCard = ({ mission }: { mission: Mission }) => (
    <div className="mission-card" onClick={() => requestMissionDetails(mission)}>
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
              executeMission(mission.mission_id);
            }}
            className="action-btn execute-btn"
          >
            Execute
          </button>
        )}
        <button 
          onClick={(e) => {
            e.stopPropagation();
            requestMissionDetails(mission);
          }}
          className="action-btn details-btn"
        >
          Details
        </button>
      </div>
    </div>
  );

  return (
    <div className="task-manager-enhanced">
      <div className="task-header">
        <h2>Mission Control</h2>
        <div className="task-stats">
          <span className="stat">
            <strong>{missions.length}</strong> total
          </span>
          <span className="stat open">
            <strong>{missionsByStatus.open?.length || 0}</strong> open
          </span>
          <span className="stat in-progress">
            <strong>{missionsByStatus.in_progress?.length || 0}</strong> in progress
          </span>
        </div>
        <div className="task-controls">
          <select 
            value={filterSeverity} 
            onChange={(e) => setFilterSeverity(e.target.value)}
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
            onChange={(e) => setFilterSubsystem(e.target.value)}
            className="task-search"
          />

          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>

          <button onClick={() => fetchMissions()} className="refresh-btn" disabled={loading}>
            {loading ? '⟳' : '↻'} Refresh
          </button>
        </div>
      </div>

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
              <button onClick={() => setSelectedMission(null)} className="close-btn">
                ×
              </button>
            </div>

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
                  <div className="detail-row">
                    <span className="detail-label">Version:</span>
                    <span className="detail-value">{selectedMission.context.version || 'N/A'}</span>
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

              {selectedMission.workspace && (
                <div className="detail-section">
                  <h4>Workspace</h4>
                  <div className="detail-row">
                    <span className="detail-label">Repository:</span>
                    <span className="detail-value mono">{selectedMission.workspace.repo_path}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Branch:</span>
                    <span className="detail-value mono">{selectedMission.workspace.working_branch}</span>
                  </div>
                </div>
              )}

              <div className="detail-actions">
                {selectedMission.status === 'open' && (
                  <button 
                    onClick={() => executeMission(selectedMission.mission_id)}
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
          </div>
        )}
      </div>

      {missions.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🎯</div>
          <h3>No missions found</h3>
          <p>Adjust filters or wait for new missions to be created</p>
        </div>
      )}
    </div>
  );
}
