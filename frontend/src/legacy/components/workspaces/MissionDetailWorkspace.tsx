import { useEffect } from 'react';
import { useMissionDetails } from '../../hooks/useMissions';
import type { WorkspacePayload } from '../../hooks/useWorkspaces';
import './WorkspaceCommon.css';

interface MissionDetailWorkspaceProps {
  payload: WorkspacePayload;
}

export default function MissionDetailWorkspace({ payload }: MissionDetailWorkspaceProps) {
  const { missionId } = payload;
  const { mission, loading, error, refresh } = useMissionDetails(missionId || null);

  if (loading) {
    return (
      <div className="workspace-container">
        <div className="workspace-loading">
          <div className="loading-spinner"></div>
          <p>Loading mission details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="workspace-container">
        <div className="workspace-error">
          <div className="error-icon">⚠️</div>
          <h3>Failed to load mission</h3>
          <p>{error.message}</p>
          <button onClick={refresh} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  if (!mission) {
    return (
      <div className="workspace-container">
        <div className="workspace-empty">
          <p>Mission not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="workspace-container mission-detail-workspace">
      <div className="workspace-header">
        <h2>{mission.mission_id}</h2>
        <div className="mission-badges">
          <span className={`severity-badge severity-${mission.severity}`}>
            {mission.severity.toUpperCase()}
          </span>
          <span className={`status-badge status-${mission.status}`}>
            {mission.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      <div className="workspace-content">
        <div className="info-section">
          <h3>Overview</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Subsystem:</span>
              <span className="value">{mission.subsystem_id}</span>
            </div>
            <div className="info-item">
              <span className="label">Detected by:</span>
              <span className="value">{mission.detected_by}</span>
            </div>
            <div className="info-item">
              <span className="label">Assigned to:</span>
              <span className="value">{mission.assigned_to}</span>
            </div>
            <div className="info-item">
              <span className="label">Created:</span>
              <span className="value">{new Date(mission.created_at).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {mission.symptoms && mission.symptoms.length > 0 && (
          <div className="info-section">
            <h3>Symptoms ({mission.symptoms.length})</h3>
            <div className="symptoms-list">
              {mission.symptoms.map((symptom, idx) => (
                <div key={idx} className="symptom-card">
                  <p>{symptom.description}</p>
                  {symptom.metric_id && (
                    <div className="symptom-metric">
                      <code>{symptom.metric_id}</code>
                      {symptom.observed_value !== undefined && (
                        <span> = {symptom.observed_value}</span>
                      )}
                      {symptom.threshold !== undefined && (
                        <span className="threshold"> (threshold: {symptom.threshold})</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {mission.context && (
          <div className="info-section">
            <h3>Context</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Environment:</span>
                <span className="value">{mission.context.env}</span>
              </div>
              <div className="info-item">
                <span className="label">Branch:</span>
                <span className="value mono">{mission.context.branch || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="label">Git SHA:</span>
                <span className="value mono">{mission.context.git_sha?.substring(0, 8)}</span>
              </div>
            </div>
          </div>
        )}

        {mission.workspace && (
          <div className="info-section">
            <h3>Workspace</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Repository:</span>
                <span className="value mono">{mission.workspace.repo_path}</span>
              </div>
              <div className="info-item">
                <span className="label">Branch:</span>
                <span className="value mono">{mission.workspace.working_branch}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="workspace-actions">
        {mission.status === 'open' && (
          <button className="action-btn primary">Execute Mission</button>
        )}
        <button className="action-btn">View Logs</button>
        <button className="action-btn">View Code</button>
      </div>
    </div>
  );
}
