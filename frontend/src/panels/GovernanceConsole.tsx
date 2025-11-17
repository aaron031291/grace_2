/**
 * Governance Console
 * Manage approval requests and view audit logs
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getPendingApprovals,
  getApprovals,
  getApprovalDetails,
  approveRequest,
  rejectRequest,
  getApprovalStats,
  getAuditLogs,
  askGraceAboutApproval,
  type ApprovalRequest,
  type AuditLog,
} from '../services/governanceApi';
import './GovernanceConsole.css';

export default function GovernanceConsole() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [activeTab, setActiveTab] = useState<'pending' | 'history' | 'audit'>('pending');
  const [graceContext, setGraceContext] = useState<string>('');
  const [askingGrace, setAskingGrace] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [pending, statsData, logs] = await Promise.all([
        getPendingApprovals(),
        getApprovalStats(),
        getAuditLogs({ limit: 50 }),
      ]);

      setApprovals(pending);
      setStats(statsData);
      setAuditLogs(logs);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load governance data'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleApprove = async (requestId: number) => {
    const reason = prompt('Reason for approval (for audit log):');
    if (reason === null) return;

    try {
      await approveRequest(requestId, reason || 'Approved via governance console');
      await fetchData();
      setSelectedApproval(null);
      alert('Request approved');
    } catch (err) {
      alert('Approval failed: ' + (err as Error).message);
    }
  };

  const handleReject = async (requestId: number) => {
    const reason = prompt('Reason for rejection (required):');
    if (!reason?.trim()) {
      alert('Rejection reason is required');
      return;
    }

    try {
      await rejectRequest(requestId, reason);
      await fetchData();
      setSelectedApproval(null);
      alert('Request rejected');
    } catch (err) {
      alert('Rejection failed: ' + (err as Error).message);
    }
  };

  const handleAskGrace = async (requestId: number) => {
    setAskingGrace(true);
    try {
      const result = await askGraceAboutApproval(requestId);
      setGraceContext(result.response);
    } catch (err) {
      alert('Failed to ask Grace: ' + (err as Error).message);
    } finally {
      setAskingGrace(false);
    }
  };

  const handleSelectApproval = async (approval: ApprovalRequest) => {
    setSelectedApproval(approval);
    setGraceContext('');
    
    if (approval.id) {
      try {
        const details = await getApprovalDetails(approval.id);
        setSelectedApproval(details);
      } catch (err) {
        console.error('Failed to load approval details:', err);
      }
    }
  };

  return (
    <div className="governance-console">
      {/* Header */}
      <div className="governance-header">
        <h2>Governance Console</h2>
        {stats && (
          <div className="governance-stats">
            <span className="stat pending">
              <strong>{stats.pending || 0}</strong> pending
            </span>
            <span className="stat approved">
              <strong>{stats.approved || 0}</strong> approved
            </span>
            <span className="stat rejected">
              <strong>{stats.rejected || 0}</strong> rejected
            </span>
          </div>
        )}
        <button onClick={fetchData} className="refresh-btn" disabled={loading}>
          {loading ? '⟳' : '↻'} Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="governance-tabs">
        <button
          className={activeTab === 'pending' ? 'active' : ''}
          onClick={() => setActiveTab('pending')}
        >
          ⏳ Pending ({stats?.pending || 0})
        </button>
        <button
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          📜 History
        </button>
        <button
          className={activeTab === 'audit' ? 'active' : ''}
          onClick={() => setActiveTab('audit')}
        >
          📋 Audit Log
        </button>
      </div>

      {/* Content */}
      <div className="governance-content">
        <div className="governance-main">
          {loading && approvals.length === 0 ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading governance data...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h3>Failed to load</h3>
              <p>{error.message}</p>
              <button onClick={fetchData} className="retry-btn">Retry</button>
            </div>
          ) : activeTab === 'pending' ? (
            <PendingApprovals
              approvals={approvals}
              onSelect={handleSelectApproval}
              selectedId={selectedApproval?.id}
            />
          ) : activeTab === 'history' ? (
            <ApprovalHistory
              onSelect={handleSelectApproval}
            />
          ) : (
            <AuditLogView logs={auditLogs} />
          )}
        </div>

        {/* Detail Panel */}
        {selectedApproval && activeTab !== 'audit' && (
          <div className="approval-detail-panel">
            <div className="detail-header">
              <h3>Approval Request #{selectedApproval.id}</h3>
              <button className="close-btn" onClick={() => setSelectedApproval(null)}>
                ×
              </button>
            </div>

            <div className="detail-body">
              <div className="detail-section">
                <h4>Request Information</h4>
                <div className="info-grid">
                  <InfoRow label="Status" value={selectedApproval.status} badge />
                  <InfoRow label="Requested by" value={selectedApproval.requested_by} />
                  <InfoRow label="Action" value={selectedApproval.action || 'N/A'} />
                  <InfoRow label="Resource" value={selectedApproval.resource_type || 'N/A'} />
                  <InfoRow label="Resource ID" value={selectedApproval.resource_id || 'N/A'} mono />
                  <InfoRow label="Risk Level" value={selectedApproval.risk_level || 'N/A'} badge />
                  <InfoRow label="Created" value={new Date(selectedApproval.created_at).toLocaleString()} />
                </div>
              </div>

              {selectedApproval.reason && (
                <div className="detail-section">
                  <h4>Reason</h4>
                  <div className="reason-box">{selectedApproval.reason}</div>
                </div>
              )}

              {selectedApproval.context && (
                <div className="detail-section">
                  <h4>Context</h4>
                  <pre className="context-box">
                    {JSON.stringify(selectedApproval.context, null, 2)}
                  </pre>
                </div>
              )}

              {graceContext && (
                <div className="detail-section grace-context">
                  <h4>Grace's Analysis</h4>
                  <div className="grace-response">{graceContext}</div>
                </div>
              )}

              {selectedApproval.status === 'approved' && selectedApproval.decision_by && (
                <div className="detail-section decision-made">
                  <h4>Decision</h4>
                  <div className="info-grid">
                    <InfoRow label="Decided by" value={selectedApproval.decision_by} />
                    <InfoRow label="Decided at" value={new Date(selectedApproval.decided_at!).toLocaleString()} />
                    <InfoRow label="Reason" value={selectedApproval.decision_reason || 'N/A'} />
                  </div>
                </div>
              )}
            </div>

            {selectedApproval.status === 'pending' && (
              <div className="detail-actions">
                <button
                  className="action-btn ask-grace"
                  onClick={() => handleAskGrace(selectedApproval.id)}
                  disabled={askingGrace}
                >
                  {askingGrace ? '⏳ Asking...' : '🤔 Discuss with Grace'}
                </button>
                <button
                  className="action-btn approve"
                  onClick={() => handleApprove(selectedApproval.id)}
                >
                  ✅ Approve
                </button>
                <button
                  className="action-btn reject"
                  onClick={() => handleReject(selectedApproval.id)}
                >
                  ❌ Reject
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function PendingApprovals({ approvals, onSelect, selectedId }: any) {
  if (approvals.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">✅</div>
        <h3>No Pending Approvals</h3>
        <p>All requests have been processed</p>
      </div>
    );
  }

  return (
    <div className="approvals-list">
      {approvals.map((approval: ApprovalRequest) => (
        <ApprovalCard
          key={approval.id}
          approval={approval}
          isSelected={selectedId === approval.id}
          onClick={() => onSelect(approval)}
        />
      ))}
    </div>
  );
}

function ApprovalCard({ approval, isSelected, onClick }: any) {
  const getRiskColor = (risk?: string) => {
    const colors: Record<string, string> = {
      critical: '#ff0000',
      high: '#ff4444',
      medium: '#ffaa00',
      low: '#00ccff',
    };
    return colors[risk || 'low'] || '#888';
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      className={`approval-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="card-header">
        <span
          className="risk-indicator"
          style={{ background: getRiskColor(approval.risk_level) }}
          title={approval.risk_level || 'low'}
        ></span>
        <span className="approval-time">{formatTime(approval.created_at)}</span>
      </div>

      <div className="card-body">
        <div className="approval-action">
          {approval.action || 'Action'} on {approval.resource_type || 'resource'}
        </div>
        <div className="approval-requester">
          Requested by: <strong>{approval.requested_by}</strong>
        </div>
        {approval.reason && (
          <div className="approval-reason">{approval.reason}</div>
        )}
      </div>
    </div>
  );
}

function ApprovalHistory({ onSelect }: any) {
  const [history, setHistory] = useState<ApprovalRequest[]>([]);
  const [filter, setFilter] = useState<'all' | 'approved' | 'rejected'>('all');

  useEffect(() => {
    const fetchHistory = async () => {
      const data = await getApprovals({ 
        status: filter === 'all' ? undefined : filter,
        limit: 100 
      });
      setHistory(data);
    };
    fetchHistory();
  }, [filter]);

  return (
    <div className="approval-history">
      <div className="history-filters">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button
          className={filter === 'approved' ? 'active' : ''}
          onClick={() => setFilter('approved')}
        >
          Approved
        </button>
        <button
          className={filter === 'rejected' ? 'active' : ''}
          onClick={() => setFilter('rejected')}
        >
          Rejected
        </button>
      </div>

      <div className="history-list">
        {history.map(approval => (
          <ApprovalCard
            key={approval.id}
            approval={approval}
            onClick={() => onSelect(approval)}
          />
        ))}
      </div>
    </div>
  );
}

function AuditLogView({ logs }: { logs: AuditLog[] }) {
  return (
    <div className="audit-log-view">
      {logs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No Audit Logs</h3>
          <p>System activity will appear here</p>
        </div>
      ) : (
        <div className="audit-log-list">
          {logs.map((log, idx) => (
            <div key={idx} className="audit-log-entry">
              <div className="log-timestamp">
                {new Date(log.timestamp).toLocaleString()}
              </div>
              <div className="log-actor">{log.actor}</div>
              <div className="log-action">{log.action}</div>
              <div className="log-resource">{log.resource}</div>
              <div className={`log-result result-${log.result}`}>
                {log.result}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value, badge, mono }: any) {
  return (
    <div className="info-row">
      <span className="info-label">{label}:</span>
      <span className={`info-value ${badge ? 'badge' : ''} ${mono ? 'mono' : ''}`}>
        {value}
      </span>
    </div>
  );
}
