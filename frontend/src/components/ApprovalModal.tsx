import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ApprovalModal.css';

interface Approval {
  id: string;
  action: string;
  description: string;
  tier: string;
  impact: string;
  requested_at: string;
  context: any;
}

interface ApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  token: string;
}

export function ApprovalModal({ isOpen, onClose, token }: ApprovalModalProps) {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [selectedApproval, setSelectedApproval] = useState<Approval | null>(null);
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchApprovals();
      const interval = setInterval(fetchApprovals, 5000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const fetchApprovals = async () => {
    try {
      const res = await fetch(apiUrl('/api/autonomy/approvals', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setApprovals(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch approvals:', err);
    }
  };

  const handleDecision = async (approvalId: string, approved: boolean) => {
    setLoading(true);
    try {
      const res = await fetch(apiUrl('/api/autonomy/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          approval_id: approvalId,
          approved,
          reason: reason || (approved ? 'Approved by user' : 'Rejected by user')
        })
      });

      if (res.ok) {
        await fetchApprovals();
        setSelectedApproval(null);
        setReason('');
      }
    } catch (err) {
      console.error('Approval decision failed:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="approval-modal-overlay" onClick={onClose}>
      <div className="approval-modal-content" onClick={e => e.stopPropagation()}>
        <div className="approval-modal-header">
          <h2>Pending Approvals</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        {approvals.length === 0 ? (
          <div className="approval-empty">
            <p>No pending approvals</p>
            <span className="empty-icon">✓</span>
          </div>
        ) : (
          <div className="approval-list">
            {approvals.map(approval => (
              <div key={approval.id} className="approval-card">
                <div className="approval-header">
                  <div className="approval-title">
                    <span className={`tier-badge ${approval.tier.toLowerCase()}`}>
                      {approval.tier}
                    </span>
                    <h3>{approval.action.replace(/_/g, ' ').toUpperCase()}</h3>
                  </div>
                  <span className={`impact-badge ${approval.impact}`}>
                    {approval.impact} impact
                  </span>
                </div>

                <p className="approval-description">{approval.description}</p>

                <div className="approval-details">
                  <div className="detail-row">
                    <span className="detail-label">Requested:</span>
                    <span className="detail-value">
                      {new Date(approval.requested_at).toLocaleString()}
                    </span>
                  </div>
                  {approval.context && (
                    <div className="detail-row">
                      <span className="detail-label">Context:</span>
                      <pre className="context-preview">
                        {JSON.stringify(approval.context, null, 2).slice(0, 200)}...
                      </pre>
                    </div>
                  )}
                </div>

                {selectedApproval?.id === approval.id ? (
                  <div className="approval-decision">
                    <textarea
                      placeholder="Optional reason for decision..."
                      value={reason}
                      onChange={e => setReason(e.target.value)}
                      className="reason-input"
                      rows={2}
                    />
                    <div className="decision-buttons">
                      <button
                        className="btn-approve"
                        onClick={() => handleDecision(approval.id, true)}
                        disabled={loading}
                      >
                        {loading ? 'Processing...' : 'Approve'}
                      </button>
                      <button
                        className="btn-reject"
                        onClick={() => handleDecision(approval.id, false)}
                        disabled={loading}
                      >
                        Reject
                      </button>
                      <button
                        className="btn-cancel"
                        onClick={() => setSelectedApproval(null)}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    className="btn-review"
                    onClick={() => setSelectedApproval(approval)}
                  >
                    Review & Decide
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
