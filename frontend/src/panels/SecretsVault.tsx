/**
 * Secrets Vault Panel
 * Secure credential management with governance
 */

import { useState, useEffect, useCallback } from 'react';
import {
  listSecrets,
  getSecretMetadata,
  getSecretValue,
  createSecret,
  rotateSecret,
  deleteSecret,
  getSecretAuditLog,
  copySecretToClipboard,
  testSecret,
  getVaultStats,
  type Secret,
  type CreateSecretRequest,
} from '../services/vaultApi';
import './SecretsVault.css';

const SECRET_TYPES = [
  { value: 'api_key', label: 'API Key', icon: '🔑' },
  { value: 'token', label: 'Access Token', icon: '🎫' },
  { value: 'password', label: 'Password', icon: '🔒' },
  { value: 'certificate', label: 'Certificate', icon: '📜' },
];

const COMMON_SECRETS = [
  { name: 'OPENAI_API_KEY', type: 'api_key', domain: 'ai' },
  { name: 'GITHUB_TOKEN', type: 'token', domain: 'code' },
  { name: 'GOOGLE_SEARCH_KEY', type: 'api_key', domain: 'search' },
  { name: 'DUCKDUCKGO_APP_KEY', type: 'api_key', domain: 'search' },
  { name: 'SLACK_TOKEN', type: 'token', domain: 'notifications' },
  { name: 'SALESFORCE_API_KEY', type: 'api_key', domain: 'crm' },
];

export default function SecretsVault() {
  const [secrets, setSecrets] = useState<Secret[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [selectedSecret, setSelectedSecret] = useState<Secret | null>(null);
  const [auditLog, setAuditLog] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // UI state
  const [showAddForm, setShowAddForm] = useState(false);
  const [showValue, setShowValue] = useState(false);
  const [secretValue, setSecretValue] = useState<string>('');
  const [copySuccess, setCopySuccess] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState<CreateSecretRequest>({
    name: '',
    value: '',
    type: 'api_key',
    tags: [],
    domain: '',
  });

  const fetchSecrets = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [secretsList, statsData] = await Promise.all([
        listSecrets(),
        getVaultStats().catch(() => null),
      ]);

      setSecrets(secretsList);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load secrets'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSecrets();
  }, [fetchSecrets]);

  const handleSelectSecret = async (secret: Secret) => {
    setSelectedSecret(secret);
    setShowValue(false);
    setSecretValue('');
    
    try {
      const logs = await getSecretAuditLog(secret.name);
      setAuditLog(logs);
    } catch (err) {
      console.error('Failed to load audit log:', err);
      setAuditLog([]);
    }
  };

  const handleRevealValue = async () => {
    if (!selectedSecret) return;

    try {
      const data = await getSecretValue(selectedSecret.name);
      setSecretValue(data.value);
      setShowValue(true);
    } catch (err) {
      alert('Failed to retrieve secret: ' + (err as Error).message);
    }
  };

  const handleCopyToClipboard = async () => {
    if (!selectedSecret) return;

    try {
      await copySecretToClipboard(selectedSecret.name);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      alert('Failed to copy secret: ' + (err as Error).message);
    }
  };

  const handleCreateSecret = async () => {
    if (!formData.name.trim() || !formData.value.trim()) {
      alert('Name and value are required');
      return;
    }

    try {
      await createSecret(formData);
      setShowAddForm(false);
      setFormData({
        name: '',
        value: '',
        type: 'api_key',
        tags: [],
        domain: '',
      });
      await fetchSecrets();
      alert('Secret stored successfully');
    } catch (err) {
      alert('Failed to store secret: ' + (err as Error).message);
    }
  };

  const handleRotateSecret = async () => {
    if (!selectedSecret) return;

    const newValue = prompt('Enter new secret value:');
    if (!newValue) return;

    const reason = prompt('Reason for rotation (for audit log):');
    if (!reason) return;

    try {
      await rotateSecret(selectedSecret.name, newValue, reason);
      await fetchSecrets();
      setShowValue(false);
      alert('Secret rotated successfully');
    } catch (err) {
      alert('Failed to rotate secret: ' + (err as Error).message);
    }
  };

  const handleDeleteSecret = async () => {
    if (!selectedSecret) return;

    const reason = prompt('Reason for deletion (required for audit):');
    if (!reason?.trim()) {
      alert('Deletion reason is required');
      return;
    }

    if (!confirm(`Delete secret "${selectedSecret.name}"? This action is logged.`)) {
      return;
    }

    try {
      await deleteSecret(selectedSecret.name, reason);
      setSelectedSecret(null);
      await fetchSecrets();
      alert('Secret deleted');
    } catch (err) {
      alert('Failed to delete secret: ' + (err as Error).message);
    }
  };

  const handleQuickAdd = (template: typeof COMMON_SECRETS[0]) => {
    setFormData({
      name: template.name,
      value: '',
      type: template.type as any,
      domain: template.domain,
      tags: [template.domain],
    });
    setShowAddForm(true);
  };

  return (
    <div className="secrets-vault">
      {/* Header */}
      <div className="vault-header">
        <h2>🔐 Secrets Vault</h2>
        {stats && (
          <div className="vault-stats">
            <span className="stat">
              <strong>{stats.total_secrets || secrets.length}</strong> secrets
            </span>
            {stats.expires_soon > 0 && (
              <span className="stat warning">
                <strong>{stats.expires_soon}</strong> expiring soon
              </span>
            )}
          </div>
        )}
        <button
          className="add-secret-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕ Cancel' : '+ Add Secret'}
        </button>
      </div>

      {/* Add Secret Form */}
      {showAddForm && (
        <div className="add-secret-form">
          <h3>Add New Secret</h3>
          
          <div className="quick-add-templates">
            <p className="template-label">Common secrets:</p>
            <div className="template-buttons">
              {COMMON_SECRETS.map(template => (
                <button
                  key={template.name}
                  onClick={() => handleQuickAdd(template)}
                  className="template-btn"
                >
                  {template.name}
                </button>
              ))}
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>Secret Name *</label>
              <input
                type="text"
                placeholder="OPENAI_API_KEY"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="form-field">
              <label>Type *</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
              >
                {SECRET_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field full-width">
              <label>Secret Value *</label>
              <textarea
                placeholder="Paste your API key or token here..."
                value={formData.value}
                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                rows={3}
                className="secret-input"
              />
            </div>

            <div className="form-field">
              <label>Domain (Optional)</label>
              <input
                type="text"
                placeholder="ai, crm, search, etc."
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              />
            </div>

            <div className="form-field">
              <label>Tags (Optional)</label>
              <input
                type="text"
                placeholder="learning, rag, production"
                onChange={(e) => setFormData({ 
                  ...formData, 
                  tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                })}
              />
            </div>
          </div>

          <div className="form-actions">
            <button onClick={handleCreateSecret} className="submit-btn">
              🔒 Store Secret Securely
            </button>
          </div>

          <div className="security-notice">
            <span className="notice-icon">🛡️</span>
            <span>
              Secrets are encrypted at rest and access is logged to audit trail.
              Requires approval for sensitive operations.
            </span>
          </div>
        </div>
      )}

      {/* Secrets List */}
      <div className="vault-content">
        <div className="secrets-list">
          {loading && secrets.length === 0 ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading vault...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h3>Failed to load vault</h3>
              <p>{error.message}</p>
              <button onClick={fetchSecrets} className="retry-btn">Retry</button>
            </div>
          ) : secrets.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔐</div>
              <h3>No Secrets Stored</h3>
              <p>Add your first API key or token to get started</p>
              <button onClick={() => setShowAddForm(true)} className="add-first-btn">
                + Add Your First Secret
              </button>
            </div>
          ) : (
            secrets.map(secret => (
              <SecretCard
                key={secret.id}
                secret={secret}
                isSelected={selectedSecret?.id === secret.id}
                onClick={() => handleSelectSecret(secret)}
              />
            ))
          )}
        </div>

        {/* Detail Panel */}
        {selectedSecret && (
          <div className="secret-detail-panel">
            <div className="detail-header">
              <h3>🔐 {selectedSecret.name}</h3>
              <button className="close-btn" onClick={() => setSelectedSecret(null)}>
                ×
              </button>
            </div>

            <div className="detail-body">
              <div className="detail-section">
                <h4>Information</h4>
                <InfoRow label="Type" value={selectedSecret.type} />
                <InfoRow label="Domain" value={selectedSecret.domain || 'N/A'} />
                <InfoRow label="Created" value={new Date(selectedSecret.created_at).toLocaleString()} />
                {selectedSecret.last_used && (
                  <InfoRow label="Last Used" value={new Date(selectedSecret.last_used).toLocaleString()} />
                )}
                <InfoRow label="Use Count" value={selectedSecret.use_count?.toString() || '0'} />
              </div>

              {selectedSecret.tags && selectedSecret.tags.length > 0 && (
                <div className="detail-section">
                  <h4>Tags</h4>
                  <div className="tag-pills">
                    {selectedSecret.tags.map(tag => (
                      <span key={tag} className="tag-pill">#{tag}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="detail-section">
                <h4>Secret Value</h4>
                {showValue ? (
                  <div className="secret-value-display">
                    <code>{secretValue}</code>
                    <button onClick={() => setShowValue(false)} className="hide-btn">
                      👁️ Hide
                    </button>
                  </div>
                ) : (
                  <div className="secret-hidden">
                    <span>••••••••••••••••</span>
                    <button onClick={handleRevealValue} className="reveal-btn">
                      👁️ Reveal (Logged)
                    </button>
                  </div>
                )}
              </div>

              {auditLog.length > 0 && (
                <div className="detail-section">
                  <h4>Access History ({auditLog.length})</h4>
                  <div className="audit-entries">
                    {auditLog.slice(0, 5).map((log, idx) => (
                      <div key={idx} className="audit-entry">
                        <span className="audit-time">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                        <span className="audit-action">{log.action}</span>
                        <span className="audit-actor">{log.actor}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="detail-actions">
              <button
                className="action-btn primary"
                onClick={handleCopyToClipboard}
              >
                {copySuccess ? '✅ Copied!' : '📋 Copy to Clipboard'}
              </button>
              <button className="action-btn" onClick={handleRotateSecret}>
                🔄 Rotate Secret
              </button>
              <button className="action-btn danger" onClick={handleDeleteSecret}>
                🗑️ Delete
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SecretCard({ secret, isSelected, onClick }: any) {
  const getTypeIcon = (type: string) => {
    return SECRET_TYPES.find(t => t.value === type)?.icon || '🔑';
  };

  const isExpiringSoon = () => {
    if (!secret.expires_at) return false;
    const expiryDate = new Date(secret.expires_at);
    const now = new Date();
    const daysUntilExpiry = (expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
    return daysUntilExpiry < 30 && daysUntilExpiry > 0;
  };

  return (
    <div
      className={`secret-card ${isSelected ? 'selected' : ''} ${isExpiringSoon() ? 'expiring' : ''}`}
      onClick={onClick}
    >
      <div className="card-header">
        <span className="secret-icon">{getTypeIcon(secret.type)}</span>
        {isExpiringSoon() && <span className="expiry-badge">⚠️ Expiring</span>}
      </div>

      <div className="card-body">
        <div className="secret-name">{secret.name}</div>
        <div className="secret-meta">
          <span className="meta-type">{secret.type}</span>
          {secret.domain && <span className="meta-domain">{secret.domain}</span>}
        </div>
        {secret.tags && secret.tags.length > 0 && (
          <div className="secret-tags">
            {secret.tags.slice(0, 2).map(tag => (
              <span key={tag} className="mini-tag">#{tag}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="info-row">
      <span className="info-label">{label}:</span>
      <span className="info-value">{value}</span>
    </div>
  );
}
