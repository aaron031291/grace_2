/**
 * Snapshot Management Component
 * 
 * Displays and manages system snapshots with golden snapshot highlighting
 */

import React, { useState } from 'react';
import { useSnapshots } from '../hooks/useSnapshots';
import { useNotifications } from '../hooks/useNotifications';
import './SnapshotManagement.css';

export const SnapshotManagement: React.FC = () => {
  const { 
    snapshots, 
    goldenSnapshot, 
    stats, 
    events, 
    loading, 
    error, 
    refresh, 
    restoreSnapshot,
    createSnapshot 
  } = useSnapshots();
  
  const { notifications } = useNotifications('user');
  const [restoring, setRestoring] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [newSnapshotLabel, setNewSnapshotLabel] = useState('');

  // Filter snapshot events from notifications
  const snapshotNotifications = notifications.filter(n => 
    n.message.toLowerCase().includes('snapshot') ||
    n.type === 'SNAPSHOT'
  );

  const handleRestore = async (snapshotId: string, snapshotLabel: string) => {
    const confirmed = confirm(
      `⚠️ RESTORE SYSTEM TO SNAPSHOT\n\n` +
      `Snapshot: ${snapshotLabel || snapshotId}\n` +
      `This will overwrite the current state and restart the system.\n\n` +
      `Continue?`
    );
    
    if (!confirmed) return;

    try {
      setRestoring(snapshotId);
      await restoreSnapshot(snapshotId);
      alert('✅ Restore initiated successfully. System will restart.');
    } catch (err: any) {
      alert(`❌ Restore failed: ${err.message}`);
    } finally {
      setRestoring(null);
    }
  };

  const handleCreate = async () => {
    if (!newSnapshotLabel.trim()) {
      alert('Please enter a label for the snapshot');
      return;
    }

    try {
      setCreating(true);
      const snapshotId = await createSnapshot(newSnapshotLabel.trim());
      setNewSnapshotLabel('');
      alert(`✅ Snapshot created: ${snapshotId}`);
    } catch (err: any) {
      alert(`❌ Failed to create snapshot: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  if (loading && snapshots.length === 0) {
    return <div className="snapshot-loading">Loading snapshots...</div>;
  }

  return (
    <div className="snapshot-management">
      <div className="snapshot-header">
        <h2>📸 Snapshot Management</h2>
        <div className="snapshot-actions">
          <button className="refresh-btn" onClick={refresh} disabled={loading}>
            {loading ? '⏳' : '🔄'} Refresh
          </button>
        </div>
      </div>

      {error && <div className="snapshot-error">⚠️ {error}</div>}

      {/* Statistics */}
      {stats && (
        <div className="snapshot-stats-bar">
          <div className="stat-item">
            <span className="stat-label">Total Snapshots:</span>
            <span className="stat-value">{stats.total_snapshots || snapshots.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Golden Snapshots:</span>
            <span className="stat-value golden">{stats.golden_snapshots || snapshots.filter(s => s.is_golden).length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Validated:</span>
            <span className="stat-value validated">{stats.validated_snapshots || snapshots.filter(s => s.is_validated).length}</span>
          </div>
        </div>
      )}

      {/* Create Snapshot Form */}
      <div className="create-snapshot-section">
        <h3>➕ Create New Snapshot</h3>
        <div className="create-snapshot-form">
          <input
            type="text"
            className="snapshot-label-input"
            placeholder="Snapshot label (e.g., before-upgrade)"
            value={newSnapshotLabel}
            onChange={(e) => setNewSnapshotLabel(e.target.value)}
            disabled={creating}
          />
          <button 
            className="create-snapshot-btn"
            onClick={handleCreate}
            disabled={creating || !newSnapshotLabel.trim()}
          >
            {creating ? '⏳ Creating...' : '📸 Create Snapshot'}
          </button>
        </div>
      </div>

      {/* Golden Snapshot Highlight */}
      {goldenSnapshot && (
        <div className="golden-snapshot-section">
          <h3>⭐ Latest Golden Snapshot</h3>
          <div className="golden-snapshot-card">
            <div className="golden-badge">GOLDEN BASELINE</div>
            <div className="snapshot-info-row">
              <span className="info-label">ID:</span>
              <span className="info-value">{goldenSnapshot.id}</span>
            </div>
            {goldenSnapshot.system_health_score !== undefined && (
              <div className="snapshot-info-row">
                <span className="info-label">Health Score:</span>
                <span className="info-value health-score">
                  {(goldenSnapshot.system_health_score * 100).toFixed(0)}%
                </span>
              </div>
            )}
            <div className="snapshot-info-row">
              <span className="info-label">Created:</span>
              <span className="info-value">
                {new Date(goldenSnapshot.created_at).toLocaleString()}
              </span>
            </div>
            {goldenSnapshot.validated_at && (
              <div className="snapshot-info-row">
                <span className="info-label">Validated:</span>
                <span className="info-value">
                  {new Date(goldenSnapshot.validated_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Snapshot List */}
      <div className="snapshot-list-section">
        <h3>📋 All Snapshots ({snapshots.length})</h3>
        <div className="snapshot-list">
          {snapshots.map((snapshot) => {
            const snapshotId = snapshot.id || snapshot.snapshot_id || '';
            const snapshotLabel = snapshot.label || snapshot.notes || snapshot.snapshot_type;
            const isGolden = snapshot.is_golden || false;
            const isValidated = snapshot.is_validated || snapshot.verified_ok || false;
            const createdAt = snapshot.created_at || snapshot.timestamp || '';

            return (
              <div 
                key={snapshotId} 
                className={`snapshot-card ${isGolden ? 'golden' : ''} ${isValidated ? 'validated' : ''}`}
              >
                <div className="snapshot-card-header">
                  <div className="snapshot-id-section">
                    <span className="snapshot-id" title={snapshotId}>
                      {snapshotId.substring(0, 24)}...
                    </span>
                    {isGolden && <span className="golden-badge-small">⭐ Golden</span>}
                    {isValidated && <span className="validated-badge">✓ Validated</span>}
                  </div>
                  <button 
                    className="restore-btn"
                    onClick={() => handleRestore(snapshotId, snapshotLabel)}
                    disabled={restoring === snapshotId}
                  >
                    {restoring === snapshotId ? '⏳ Restoring...' : '↩️ Restore'}
                  </button>
                </div>

                <div className="snapshot-card-body">
                  {snapshotLabel && (
                    <div className="snapshot-label">{snapshotLabel}</div>
                  )}
                  
                  <div className="snapshot-metadata">
                    <div className="metadata-item">
                      <span className="meta-label">Type:</span>
                      <span className="meta-value">{snapshot.snapshot_type || 'boot'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="meta-label">Status:</span>
                      <span className={`meta-value status-${snapshot.status}`}>
                        {snapshot.status || 'available'}
                      </span>
                    </div>
                    {snapshot.system_health_score !== undefined && (
                      <div className="metadata-item">
                        <span className="meta-label">Health:</span>
                        <span className="meta-value health-score">
                          {(snapshot.system_health_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="snapshot-timestamp">
                    Created: {new Date(createdAt).toLocaleString()}
                  </div>

                  {snapshot.triggered_by && (
                    <div className="snapshot-trigger">
                      By: {snapshot.triggered_by}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Snapshot Events */}
      <div className="snapshot-events-section">
        <h3>📡 Snapshot Events</h3>
        
        {/* Combined events from hook and notifications */}
        <div className="events-list">
          {[...events, ...snapshotNotifications.map(n => ({
            event_type: 'SNAPSHOT_CREATED' as const,
            snapshot_id: 'notification',
            timestamp: n.timestamp,
            triggered_by: 'system',
            message: n.message
          }))].slice(0, 10).map((event, idx) => (
            <div key={idx} className={`event-item event-${event.event_type}`}>
              <div className="event-icon">
                {event.event_type === 'SNAPSHOT_CREATED' && '📸'}
                {event.event_type === 'SNAPSHOT_RESTORED' && '↩️'}
                {event.event_type === 'SNAPSHOT_VALIDATED' && '✅'}
              </div>
              <div className="event-content">
                <div className="event-message">{event.message}</div>
                <div className="event-meta">
                  <span className="event-time">
                    {new Date(event.timestamp).toLocaleString()}
                  </span>
                  {event.triggered_by && (
                    <span className="event-trigger">by {event.triggered_by}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {events.length === 0 && snapshotNotifications.length === 0 && (
          <div className="no-events">No recent snapshot events</div>
        )}
      </div>
    </div>
  );
};
