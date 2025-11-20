/**
 * Mission List Component
 * 
 * Displays active and resolved missions with detailed plan views
 */

import React, { useState, useEffect } from 'react';
import { MissionControlAPI, type Mission, type MissionDetail } from '../api/missions';
import './MissionList.css';

interface MissionListProps {
  filter?: 'all' | 'active' | 'resolved';
  limit?: number;
}

export const MissionList: React.FC<MissionListProps> = ({ filter = 'all', limit = 50 }) => {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selectedMission, setSelectedMission] = useState<MissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const fetchMissions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let data;
      if (filter === 'active') {
        data = { missions: await MissionControlAPI.getActiveMissions(limit) };
      } else if (filter === 'resolved') {
        data = { missions: await MissionControlAPI.getResolvedMissions(limit) };
      } else {
        data = await MissionControlAPI.listMissions({ limit });
      }
      
      setMissions(data.missions || []);
    } catch (err: any) {
      console.error('Failed to fetch missions:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMissionClick = async (missionId: string) => {
    try {
      setDetailsLoading(true);
      const details = await MissionControlAPI.getMission(missionId);
      setSelectedMission(details);
    } catch (err: any) {
      console.error('Failed to fetch mission details:', err);
      alert(`Failed to load mission details: ${err.message}`);
    } finally {
      setDetailsLoading(false);
    }
  };

  const executeMission = async (missionId: string, type: 'coding' | 'healing') => {
    try {
      await MissionControlAPI.executeMission(missionId, type);
      alert(`Mission execution started: ${type}`);
      await fetchMissions();
    } catch (err: any) {
      alert(`Failed to execute mission: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchMissions();
    const interval = setInterval(fetchMissions, 30000);
    return () => clearInterval(interval);
  }, [filter, limit]);

  if (loading && missions.length === 0) {
    return <div className="mission-list-loading">Loading missions...</div>;
  }

  return (
    <div className="mission-list">
      <div className="mission-list-header">
        <h2>📋 Mission List</h2>
        <div className="mission-stats">
          <span className="stat-badge">
            Total: <strong>{missions.length}</strong>
          </span>
          <span className="stat-badge active">
            Active: <strong>{missions.filter(m => m.status === 'open' || m.status === 'in_progress').length}</strong>
          </span>
          <span className="stat-badge resolved">
            Resolved: <strong>{missions.filter(m => m.status === 'resolved').length}</strong>
          </span>
        </div>
        <button className="refresh-btn" onClick={fetchMissions}>🔄 Refresh</button>
      </div>

      {error && <div className="mission-list-error">⚠️ {error}</div>}

      <div className="mission-list-content">
        <div className="missions-table-container">
          <table className="missions-table-full">
            <thead>
              <tr>
                <th>ID</th>
                <th>Subsystem</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Assigned To</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Symptoms</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {missions.map((mission) => (
                <tr 
                  key={mission.mission_id}
                  className={`mission-row-full severity-${mission.severity} status-${mission.status}`}
                  onClick={() => handleMissionClick(mission.mission_id)}
                >
                  <td className="mission-id-full" title={mission.mission_id}>
                    {mission.mission_id.substring(0, 20)}...
                  </td>
                  <td>
                    <span className="subsystem-tag">{mission.subsystem_id}</span>
                  </td>
                  <td>
                    <span className={`severity-tag severity-${mission.severity}`}>
                      {mission.severity}
                    </span>
                  </td>
                  <td>
                    <span className={`status-tag status-${mission.status}`}>
                      {mission.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="assigned-to">{mission.assigned_to}</td>
                  <td className="time-cell-full">
                    {new Date(mission.created_at).toLocaleString()}
                  </td>
                  <td className="time-cell-full">
                    {new Date(mission.updated_at).toLocaleString()}
                  </td>
                  <td className="count-cell">{mission.symptoms_count}</td>
                  <td className="actions-cell">
                    <button 
                      className="action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMissionClick(mission.mission_id);
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mission Details Panel */}
        {selectedMission && (
          <div className="mission-details-overlay" onClick={() => setSelectedMission(null)}>
            <div className="mission-details-panel" onClick={(e) => e.stopPropagation()}>
              <div className="details-header">
                <h3>Mission Details</h3>
                <button className="close-details-btn" onClick={() => setSelectedMission(null)}>×</button>
              </div>

              {detailsLoading ? (
                <div className="details-loading">Loading details...</div>
              ) : (
                <div className="details-content">
                  <div className="details-section">
                    <h4>📋 Overview</h4>
                    <div className="details-grid">
                      <div className="detail-item">
                        <span className="detail-label">Mission ID:</span>
                        <span className="detail-value">{selectedMission.mission_id}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Subsystem:</span>
                        <span className="detail-value">{selectedMission.subsystem_id}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Severity:</span>
                        <span className={`severity-tag severity-${selectedMission.severity}`}>
                          {selectedMission.severity}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Status:</span>
                        <span className={`status-tag status-${selectedMission.status}`}>
                          {selectedMission.status.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Assigned To:</span>
                        <span className="detail-value">{selectedMission.assigned_to}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Detected By:</span>
                        <span className="detail-value">{selectedMission.detected_by}</span>
                      </div>
                    </div>
                  </div>

                  {/* Symptoms */}
                  {selectedMission.symptoms && selectedMission.symptoms.length > 0 && (
                    <div className="details-section">
                      <h4>🔍 Symptoms ({selectedMission.symptoms.length})</h4>
                      <div className="symptoms-list">
                        {selectedMission.symptoms.map((symptom, idx) => (
                          <div key={idx} className="symptom-card">
                            <div className="symptom-description">{symptom.description}</div>
                            {symptom.observed_value !== undefined && (
                              <div className="symptom-metric">
                                Observed: {symptom.observed_value} {symptom.threshold !== undefined && `(Threshold: ${symptom.threshold})`}
                              </div>
                            )}
                            {symptom.log_snippet && (
                              <div className="symptom-log">{symptom.log_snippet}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Remediation History */}
                  {selectedMission.remediation_history && selectedMission.remediation_history.length > 0 && (
                    <div className="details-section">
                      <h4>🔧 Remediation History ({selectedMission.remediation_history.length})</h4>
                      <div className="remediation-timeline">
                        {selectedMission.remediation_history.map((event, idx) => (
                          <div key={idx} className="remediation-event">
                            <div className="event-time">
                              {new Date(event.timestamp).toLocaleString()}
                            </div>
                            <div className="event-actor">By: {event.actor}</div>
                            <div className="event-action">{event.action}</div>
                            {event.result && (
                              <div className="event-result">Result: {event.result}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Context & Workspace */}
                  {selectedMission.context && (
                    <div className="details-section">
                      <h4>⚙️ Context</h4>
                      <div className="context-grid">
                        <div className="context-item">
                          <span className="context-label">Git SHA:</span>
                          <span className="context-value">{selectedMission.context.git_sha?.substring(0, 12)}</span>
                        </div>
                        <div className="context-item">
                          <span className="context-label">Branch:</span>
                          <span className="context-value">{selectedMission.context.branch || 'N/A'}</span>
                        </div>
                        <div className="context-item">
                          <span className="context-label">Environment:</span>
                          <span className="context-value">{selectedMission.context.env}</span>
                        </div>
                        <div className="context-item">
                          <span className="context-label">Version:</span>
                          <span className="context-value">{selectedMission.context.version || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Execution Actions */}
                  <div className="details-actions">
                    {(selectedMission.status === 'open' || selectedMission.status === 'in_progress') && (
                      <>
                        <button 
                          className="execute-btn coding"
                          onClick={() => executeMission(selectedMission.mission_id, 'coding')}
                        >
                          💻 Execute Coding Mission
                        </button>
                        <button 
                          className="execute-btn healing"
                          onClick={() => executeMission(selectedMission.mission_id, 'healing')}
                        >
                          🔧 Execute Healing Mission
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
