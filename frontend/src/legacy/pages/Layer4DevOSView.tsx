/**
 * Layer 4 Dev/OS View
 * Secrets & recording workflows, remote-access sessions, code/deployment status
 * Modals for storing API keys (with consent prompts), listing recordings awaiting ingestion,
 * and launching automated tests/stress runs
 */
import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import axios from 'axios';
import './Layer4DevOSView.css';

interface SecretsStatus {
  total_secrets: number;
  encrypted: number;
  vault_health: string;
}

interface Recording {
  recording_id: string;
  type: string;
  filename: string;
  size_mb: number;
  created_at: string;
}

interface RemoteSession {
  session_id: string;
  user: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number;
}

interface DeploymentStatus {
  last_deployment: string;
  environment: string;
  version: string;
  health_check: string;
  pending_tests: number;
}

const API_BASE = apiUrl('';

export const Layer4DevOSView: React.FC = () => {
  const [secretsStatus, setSecretsStatus] = useState<SecretsStatus | null>(null);
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [remoteSessions, setRemoteSessions] = useState<RemoteSession[]>([]);
  const [deploymentStatus, setDeploymentStatus] = useState<DeploymentStatus | null>(null);
  const [showSecretModal, setShowSecretModal] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [secretFormData, setSecretFormData] = useState({ key_name: '', key_value: '', category: 'api_key' });
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchSecretsStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/secrets/status`);
      setSecretsStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch secrets status:', error);
    }
  };

  const fetchRecordings = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/recordings/pending`);
      setRecordings(response.data.recordings || []);
    } catch (error) {
      console.error('Failed to fetch recordings:', error);
    }
  };

  const fetchRemoteSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/remote_access/sessions?active_only=false`);
      setRemoteSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch remote sessions:', error);
    }
  };

  const fetchDeploymentStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/deployment/status`);
      setDeploymentStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch deployment status:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchSecretsStatus(),
        fetchRecordings(),
        fetchRemoteSessions(),
        fetchDeploymentStatus()
      ]);
      setLoading(false);
    };

    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, 10000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const handleSaveSecret = async () => {
    setShowSecretModal(false);
    setShowConsentModal(true);
  };

  const handleConsentConfirm = async () => {
    try {
      await axios.post(`${API_BASE}/api/secrets/store`, {
        name: secretFormData.key_name,
        value: secretFormData.key_value,
        category: secretFormData.category,
        consent_given: true
      });
      setShowConsentModal(false);
      setSecretFormData({ key_name: '', key_value: '', category: 'api_key' });
      await fetchSecretsStatus();
      alert('Secret stored successfully!');
    } catch (error) {
      console.error('Failed to store secret:', error);
      alert('Failed to store secret');
    }
  };

  const triggerRecordingIngestion = async (recordingId: string) => {
    try {
      await axios.post(`${API_BASE}/api/recording/ingest/${recordingId}`);
      await fetchRecordings();
      alert('Recording ingestion started!');
    } catch (error) {
      console.error('Failed to trigger ingestion:', error);
      alert('Failed to trigger ingestion');
    }
  };

  const runStressTest = async () => {
    try {
      await axios.post(`${API_BASE}/api/stress/run`);
      alert('Stress test initiated!');
    } catch (error) {
      console.error('Failed to run stress test:', error);
      alert('Failed to run stress test');
    }
  };

  const getHealthColor = (health: string) => {
    switch (health.toLowerCase()) {
      case 'healthy':
      case 'passing':
        return '#00ff88';
      case 'degraded':
        return '#ffaa00';
      case 'unhealthy':
      case 'failing':
        return '#ff4444';
      default:
        return '#888';
    }
  };

  if (loading) {
    return <div className="dev-console-loading">Loading Dev/OS View...</div>;
  }

  return (
    <div className="layer4-dev-os-view">
      <div className="console-header">
        <h1>⚙️ Layer 4: Dev/OS View</h1>
        <div className="header-controls">
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (10s)
          </label>
          <button onClick={() => window.location.reload()}>Refresh All</button>
        </div>
      </div>

      {/* Secrets Vault Status */}
      <section className="secrets-section">
        <div className="section-header">
          <h2>🔐 Secrets Vault</h2>
          <button className="btn-primary" onClick={() => setShowSecretModal(true)}>
            + Add Secret
          </button>
        </div>
        <div className="secrets-grid">
          <div className="secrets-card">
            <div className="card-label">Total Secrets</div>
            <div className="card-value">{secretsStatus?.total_secrets || 0}</div>
          </div>
          <div className="secrets-card">
            <div className="card-label">Encrypted</div>
            <div className="card-value">{secretsStatus?.encrypted || 0}</div>
          </div>
          <div className="secrets-card">
            <div className="card-label">Vault Health</div>
            <div
              className="card-value"
              style={{ color: getHealthColor(secretsStatus?.vault_health || 'unknown') }}
            >
              {secretsStatus?.vault_health || 'unknown'}
            </div>
          </div>
        </div>
      </section>

      {/* Deployment Status */}
      <section className="deployment-section">
        <h2>🚀 Deployment Status</h2>
        <div className="deployment-grid">
          <div className="deployment-card">
            <div className="card-label">Environment</div>
            <div className="card-value">{deploymentStatus?.environment || 'N/A'}</div>
          </div>
          <div className="deployment-card">
            <div className="card-label">Version</div>
            <div className="card-value">{deploymentStatus?.version || 'N/A'}</div>
          </div>
          <div className="deployment-card">
            <div className="card-label">Health Check</div>
            <div
              className="card-value"
              style={{ color: getHealthColor(deploymentStatus?.health_check || 'unknown') }}
            >
              {deploymentStatus?.health_check || 'unknown'}
            </div>
          </div>
          <div className="deployment-card">
            <div className="card-label">Last Deployment</div>
            <div className="card-value">
              {deploymentStatus?.last_deployment
                ? new Date(deploymentStatus.last_deployment).toLocaleString()
                : 'N/A'}
            </div>
          </div>
        </div>
        <div className="deployment-actions">
          <button className="btn-secondary" onClick={runStressTest}>
            ⚡ Run Stress Test
          </button>
          <button className="btn-secondary">🧪 Run Unit Tests</button>
          <button className="btn-secondary">📊 View Logs</button>
        </div>
      </section>

      {/* Pending Recordings */}
      <section className="recordings-section">
        <h2>🎙️ Recordings Awaiting Ingestion</h2>
        {recordings.length > 0 ? (
          <table className="recordings-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Filename</th>
                <th>Size</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {recordings.map((recording) => (
                <tr key={recording.recording_id}>
                  <td className="recording-id">{recording.recording_id.substring(0, 8)}</td>
                  <td>{recording.type}</td>
                  <td className="filename">{recording.filename}</td>
                  <td>{recording.size_mb.toFixed(2)} MB</td>
                  <td>{new Date(recording.created_at).toLocaleString()}</td>
                  <td>
                    <button
                      className="btn-small btn-primary"
                      onClick={() => triggerRecordingIngestion(recording.recording_id)}
                    >
                      Ingest
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">No recordings awaiting ingestion</div>
        )}
      </section>

      {/* Remote Access Sessions */}
      <section className="remote-sessions-section">
        <h2>🌐 Remote Access Sessions</h2>
        {remoteSessions.length > 0 ? (
          <table className="sessions-table">
            <thead>
              <tr>
                <th>Session ID</th>
                <th>User</th>
                <th>Status</th>
                <th>Started</th>
                <th>Ended</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {remoteSessions.map((session) => (
                <tr key={session.session_id}>
                  <td className="session-id">{session.session_id.substring(0, 8)}</td>
                  <td>{session.user}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{
                        backgroundColor: session.status === 'active' ? '#00ff88' : '#888'
                      }}
                    >
                      {session.status}
                    </span>
                  </td>
                  <td>{new Date(session.started_at).toLocaleString()}</td>
                  <td>{session.ended_at ? new Date(session.ended_at).toLocaleString() : '-'}</td>
                  <td>{session.duration_minutes} min</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">No remote access sessions</div>
        )}
      </section>

      {/* Add Secret Modal */}
      {showSecretModal && (
        <div className="modal-overlay" onClick={() => setShowSecretModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Secret</h3>
              <button className="close-btn" onClick={() => setShowSecretModal(false)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Secret Name</label>
                <input
                  type="text"
                  value={secretFormData.key_name}
                  onChange={(e) =>
                    setSecretFormData({ ...secretFormData, key_name: e.target.value })
                  }
                  placeholder="e.g., OPENAI_API_KEY"
                />
              </div>
              <div className="form-group">
                <label>Secret Value</label>
                <input
                  type="password"
                  value={secretFormData.key_value}
                  onChange={(e) =>
                    setSecretFormData({ ...secretFormData, key_value: e.target.value })
                  }
                  placeholder="Enter secret value"
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select
                  value={secretFormData.category}
                  onChange={(e) =>
                    setSecretFormData({ ...secretFormData, category: e.target.value })
                  }
                >
                  <option value="api_key">API Key</option>
                  <option value="password">Password</option>
                  <option value="token">Token</option>
                  <option value="certificate">Certificate</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowSecretModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleSaveSecret}>
                Save Secret
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Consent Modal */}
      {showConsentModal && (
        <div className="modal-overlay">
          <div className="modal-content consent-modal">
            <div className="modal-header">
              <h3>🔒 Consent Required</h3>
            </div>
            <div className="modal-body">
              <p>You are about to store a secret in the encrypted vault.</p>
              <div className="consent-details">
                <p><strong>Secret Name:</strong> {secretFormData.key_name}</p>
                <p><strong>Category:</strong> {secretFormData.category}</p>
              </div>
              <div className="consent-info">
                <p>This secret will be:</p>
                <ul>
                  <li>✓ Encrypted using AES-256 encryption</li>
                  <li>✓ Stored securely in the GRACE vault</li>
                  <li>✓ Accessible only to authorized agents</li>
                  <li>✓ Audited and logged</li>
                </ul>
              </div>
              <p className="consent-question">Do you consent to storing this secret?</p>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowConsentModal(false)}>
                ✕ No, Cancel
              </button>
              <button className="btn-primary" onClick={handleConsentConfirm}>
                ✓ Yes, I Consent
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
