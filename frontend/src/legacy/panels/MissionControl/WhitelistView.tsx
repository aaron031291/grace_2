/**
 * Whitelist View
 * Manage approved sources for autonomous learning
 */

import { useState, useEffect } from 'react';
import './WhitelistView.css';

interface WhitelistEntry {
  id: string;
  domain: string;
  source_type: 'url' | 'domain' | 'api' | 'repository';
  approved_by: string;
  approved_at: string;
  reason?: string;
  trust_score?: number;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export default function WhitelistView() {
  const [entries, setEntries] = useState<WhitelistEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEntry, setNewEntry] = useState({
    domain: '',
    source_type: 'url' as const,
    reason: '',
  });

  const loadWhitelist = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/learning/whitelist`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          console.warn('[Whitelist] Endpoint not available');
          setEntries([]);
          return;
        }
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setEntries(data.entries || []);
    } catch (error) {
      console.error('Failed to load whitelist:', error);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWhitelist();
  }, []);

  const handleAdd = async () => {
    if (!newEntry.domain.trim()) return;

    try {
      const response = await fetch(`${API_BASE}/api/learning/whitelist`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newEntry,
          approved_by: 'aaron',
        }),
      });

      if (response.ok) {
        setNewEntry({ domain: '', source_type: 'url', reason: '' });
        setShowAddForm(false);
        loadWhitelist();
      }
    } catch (error) {
      console.error('Failed to add entry:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Remove this entry from whitelist?')) return;

    try {
      await fetch(`${API_BASE}/api/learning/whitelist/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
        },
      });

      loadWhitelist();
    } catch (error) {
      console.error('Failed to delete entry:', error);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'url': return '🔗';
      case 'domain': return '🌐';
      case 'api': return '🔌';
      case 'repository': return '📦';
      default: return '📄';
    }
  };

  if (loading) {
    return (
      <div className="whitelist-view">
        <div className="loading">Loading whitelist...</div>
      </div>
    );
  }

  return (
    <div className="whitelist-view">
      <div className="whitelist-header">
        <div className="whitelist-info">
          <p>
            Approved sources for autonomous learning and data ingestion.
            Only whitelisted sources can be accessed without manual approval.
          </p>
          <div className="stats">
            <strong>{entries.length}</strong> approved sources
          </div>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="add-btn"
        >
          {showAddForm ? '✕ Cancel' : '+ Add Source'}
        </button>
      </div>

      {showAddForm && (
        <div className="add-form">
          <h3>Add Approved Source</h3>
          
          <div className="form-group">
            <label>Domain/URL</label>
            <input
              type="text"
              value={newEntry.domain}
              onChange={(e) => setNewEntry({ ...newEntry, domain: e.target.value })}
              placeholder="example.com or https://example.com/api"
            />
          </div>

          <div className="form-group">
            <label>Type</label>
            <select
              value={newEntry.source_type}
              onChange={(e) => setNewEntry({ ...newEntry, source_type: e.target.value as any })}
            >
              <option value="url">URL</option>
              <option value="domain">Domain</option>
              <option value="api">API</option>
              <option value="repository">Repository</option>
            </select>
          </div>

          <div className="form-group">
            <label>Reason (optional)</label>
            <textarea
              value={newEntry.reason}
              onChange={(e) => setNewEntry({ ...newEntry, reason: e.target.value })}
              placeholder="Why is this source approved?"
              rows={3}
            />
          </div>

          <button onClick={handleAdd} className="submit-btn">
            Approve Source
          </button>
        </div>
      )}

      <div className="whitelist-entries">
        {entries.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <div className="empty-message">No approved sources yet</div>
            <div className="empty-hint">
              Add sources to allow Grace to learn autonomously
            </div>
          </div>
        ) : (
          entries.map(entry => (
            <div key={entry.id} className="whitelist-entry">
              <div className="entry-header">
                <div className="entry-type">
                  {getTypeIcon(entry.source_type)} {entry.source_type}
                </div>
                {entry.trust_score !== undefined && (
                  <div className="trust-score">
                    Trust: {entry.trust_score}%
                  </div>
                )}
              </div>

              <div className="entry-domain">{entry.domain}</div>

              {entry.reason && (
                <div className="entry-reason">{entry.reason}</div>
              )}

              <div className="entry-meta">
                <span>Approved by {entry.approved_by}</span>
                <span>•</span>
                <span>{new Date(entry.approved_at).toLocaleDateString()}</span>
              </div>

              <button
                onClick={() => handleDelete(entry.id)}
                className="delete-btn"
              >
                Remove
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
