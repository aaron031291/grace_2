import React, { useState, useEffect } from 'react';
import './BuildProgressCard.css';

interface BuildProgressCardProps {
  jobId: string;
  spec: string;
  status: string;
  trustScore?: number;
  approvals?: {
    governance: { status: string; approved_at?: string };
    scan: { status: string; passed: boolean; results?: any };
    user: { status: string; approved_at?: string };
  };
  onApprove?: (jobId: string) => void;
  onReject?: (jobId: string, reason: string) => void;
}

const BuildProgressCard: React.FC<BuildProgressCardProps> = ({
  jobId,
  spec,
  status,
  trustScore = 0,
  approvals,
  onApprove,
  onReject,
}) => {
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectInput, setShowRejectInput] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'failed':
      case 'rejected':
        return '#ef4444';
      case 'waiting_for_governance':
      case 'waiting_for_user_approval':
        return '#f59e0b';
      default:
        return '#3b82f6';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'failed':
      case 'rejected':
        return '✗';
      case 'waiting_for_governance':
      case 'waiting_for_user_approval':
        return '⏸';
      default:
        return '⟳';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      created: 'Created',
      planning: 'Planning',
      implementing: 'Implementing',
      waiting_for_governance: 'Waiting for Governance Approval',
      scanning: 'Running Quality Scans',
      waiting_for_user_approval: 'Waiting for Your Approval',
      applying: 'Applying Changes',
      completed: 'Completed',
      failed: 'Failed',
      rejected: 'Rejected',
    };
    return labels[status] || status;
  };

  const handleApprove = () => {
    if (onApprove) {
      onApprove(jobId);
    }
  };

  const handleReject = () => {
    if (onReject) {
      onReject(jobId, rejectReason || 'User rejected');
      setShowRejectInput(false);
      setRejectReason('');
    }
  };

  const showApprovalButtons =
    status === 'waiting_for_governance' || status === 'waiting_for_user_approval';

  return (
    <div className="build-progress-card">
      <div className="build-progress-header">
        <div
          className="build-progress-status-icon"
          style={{ backgroundColor: getStatusColor(status) }}
        >
          {getStatusIcon(status)}
        </div>
        <div className="build-progress-info">
          <div className="build-progress-title">Build: {spec}</div>
          <div className="build-progress-job-id">Job ID: {jobId}</div>
        </div>
      </div>

      <div className="build-progress-status">
        <div className="build-progress-status-label">{getStatusLabel(status)}</div>
        {trustScore > 0 && (
          <div className="build-progress-trust-score">
            Trust Score: {trustScore.toFixed(1)}/100
          </div>
        )}
      </div>

      {approvals && (
        <div className="build-progress-approvals">
          <div className="build-progress-approval-item">
            <span className="build-progress-approval-label">Governance:</span>
            <span
              className={`build-progress-approval-status ${approvals.governance.status}`}
            >
              {approvals.governance.status}
            </span>
          </div>
          <div className="build-progress-approval-item">
            <span className="build-progress-approval-label">Quality Scan:</span>
            <span
              className={`build-progress-approval-status ${approvals.scan.status}`}
            >
              {approvals.scan.status}
              {approvals.scan.passed !== undefined &&
                ` (${approvals.scan.passed ? 'Passed' : 'Failed'})`}
            </span>
          </div>
          <div className="build-progress-approval-item">
            <span className="build-progress-approval-label">User Approval:</span>
            <span className={`build-progress-approval-status ${approvals.user.status}`}>
              {approvals.user.status}
            </span>
          </div>
        </div>
      )}

      {showApprovalButtons && (
        <div className="build-progress-actions">
          {!showRejectInput ? (
            <>
              <button
                className="build-progress-button build-progress-button-approve"
                onClick={handleApprove}
              >
                ✓ Approve
              </button>
              <button
                className="build-progress-button build-progress-button-reject"
                onClick={() => setShowRejectInput(true)}
              >
                ✗ Reject
              </button>
            </>
          ) : (
            <div className="build-progress-reject-input">
              <input
                type="text"
                placeholder="Reason for rejection (optional)"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                className="build-progress-input"
              />
              <button
                className="build-progress-button build-progress-button-reject"
                onClick={handleReject}
              >
                Confirm Reject
              </button>
              <button
                className="build-progress-button build-progress-button-cancel"
                onClick={() => {
                  setShowRejectInput(false);
                  setRejectReason('');
                }}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      )}

      {status === 'completed' && (
        <div className="build-progress-completed">
          ✓ Build completed successfully! Check the PR for details.
        </div>
      )}

      {(status === 'failed' || status === 'rejected') && (
        <div className="build-progress-error">
          Build {status}. Check the logs for details.
        </div>
      )}
    </div>
  );
};

export default BuildProgressCard;
