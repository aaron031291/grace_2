import React, { useState, useEffect } from 'react';
import './GovernancePanel.css';
import LibrarianGovernance from '../Knowledge/LibrarianGovernance';

interface ApprovalRequest {
  id: string;
  trace_id: string;
  agent: string;
  action_type: string;
  reason: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  details?: any;
}

export const GovernancePanel: React.FC = () => {
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalRequest[]>([]);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'approvals' | 'librarian'>('approvals');

  useEffect(() => {
    fetchPendingApprovals();
  }, []);

  const fetchPendingApprovals = async () => {
    try {
      const response = await fetch('/api/governance/pending');
      if (response.ok) {
        const data = await response.json();
        setPendingApprovals(data.approvals || []);
      }
    } catch (error) {
      console.error('Failed to fetch approvals:', error);
    }
  };

  const handleApprove = async (traceId: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/governance/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trace_id: traceId, reason: 'Approved by user' }),
      });

      if (response.ok) {
        await fetchPendingApprovals();
        setSelectedApproval(null);
      }
    } catch (error) {
      console.error('Failed to approve:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (traceId: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/governance/reject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trace_id: traceId, reason: 'Rejected by user' }),
      });

      if (response.ok) {
        await fetchPendingApprovals();
        setSelectedApproval(null);
      }
    } catch (error) {
      console.error('Failed to reject:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#888';
    }
  };

  return (
    <div className="governance-panel">
      <div className="governance-tabs">
        <button
          className={`governance-tab ${activeTab === 'approvals' ? 'active' : ''}`}
          onClick={() => setActiveTab('approvals')}
        >
          Pending Approvals
        </button>
        <button
          className={`governance-tab ${activeTab === 'librarian' ? 'active' : ''}`}
          onClick={() => setActiveTab('librarian')}
        >
          Librarian Governance
        </button>
      </div>

      {activeTab === 'approvals' ? (
        <>
          <div className="governance-header">
            <h3 className="governance-title">Pending Approvals</h3>
            <button className="refresh-btn-gov" onClick={fetchPendingApprovals}>🔄</button>
          </div>

          {pendingApprovals.length === 0 ? (
            <div className="empty-approvals">
              <div className="empty-icon-gov">✅</div>
              <div className="empty-text">No pending approvals</div>
            </div>
          ) : (
            <div className="approvals-list">
              {pendingApprovals.map((approval) => (
                <div
                  key={approval.id}
                  className={`approval-item ${selectedApproval?.id === approval.id ? 'selected' : ''}`}
                  onClick={() => setSelectedApproval(approval)}
                >
                  <div className="approval-header-row">
                    <span className="approval-agent">{approval.agent}</span>
                    <span
                      className="approval-risk"
                      style={{ color: getRiskColor(approval.risk_level) }}
                    >
                      {approval.risk_level}
                    </span>
                  </div>

                  <div className="approval-action">{approval.action_type}</div>
                  <div className="approval-reason">{approval.reason}</div>
                  <div className="approval-meta">{approval.timestamp}</div>

                  <div className="approval-actions">
                    <button
                      className="approve-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleApprove(approval.trace_id);
                      }}
                      disabled={loading}
                    >
                      ✓ Approve
                    </button>
                    <button
                      className="reject-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReject(approval.trace_id);
                      }}
                      disabled={loading}
                    >
                      ✕ Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="governance-stats">
            <div className="stat-item">
              <span className="stat-label">Secret Rotation</span>
              <span className="stat-value compliant">Compliant</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Approval Coverage</span>
              <span className="stat-value">100%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Audit Logging</span>
              <span className="stat-value enabled">Enabled</span>
            </div>
          </div>

          <div className="governance-actions-bottom">
            <button className="gov-action-btn">Request Approval</button>
            <button className="gov-action-btn">Revoke Token</button>
            <button className="gov-action-btn">View Audit Trail</button>
          </div>
        </>
      ) : (
        <LibrarianGovernance />
      )}
    </div>
  );
};
