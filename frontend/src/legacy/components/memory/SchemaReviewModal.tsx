import React, { useState, useEffect } from 'react';
import { type SchemaProposal, getPendingSchemas, approveSchema, rejectSchema } from '../../api/memory';

interface SchemaReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSchemaApproved?: () => void;
}

export const SchemaReviewModal: React.FC<SchemaReviewModalProps> = ({
  isOpen,
  onClose,
  onSchemaApproved,
}) => {
  const [proposals, setProposals] = useState<SchemaProposal[]>([]);
  const [selectedProposal, setSelectedProposal] = useState<SchemaProposal | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadProposals();
    }
  }, [isOpen]);

  const loadProposals = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPendingSchemas();
      setProposals(data);
      if (data.length > 0 && !selectedProposal) {
        setSelectedProposal(data[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load proposals');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (proposalId: string) => {
    try {
      await approveSchema(proposalId);
      setProposals(proposals.filter(p => p.proposal_id !== proposalId));
      if (selectedProposal?.proposal_id === proposalId) {
        setSelectedProposal(proposals[0] || null);
      }
      onSchemaApproved?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve schema');
    }
  };

  const handleReject = async (proposalId: string) => {
    try {
      await rejectSchema(proposalId, rejectReason);
      setProposals(proposals.filter(p => p.proposal_id !== proposalId));
      if (selectedProposal?.proposal_id === proposalId) {
        setSelectedProposal(proposals[0] || null);
      }
      setRejectReason('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject schema');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content schema-review-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Schema Proposals ({proposals.length} pending)</h2>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Loading proposals...</div>
        ) : proposals.length === 0 ? (
          <div className="no-proposals">No pending schema proposals</div>
        ) : (
          <div className="schema-review-content">
            <div className="proposal-list">
              {proposals.map((proposal) => (
                <div
                  key={proposal.proposal_id}
                  className={`proposal-item ${selectedProposal?.proposal_id === proposal.proposal_id ? 'selected' : ''}`}
                  onClick={() => setSelectedProposal(proposal)}
                >
                  <div className="proposal-title">{proposal.table_name}</div>
                  <div className="proposal-meta">
                    Confidence: {(proposal.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="proposal-date">
                    {new Date(proposal.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>

            {selectedProposal && (
              <div className="proposal-details">
                <h3>{selectedProposal.table_name}</h3>
                <div className="confidence-badge">
                  Confidence: {(selectedProposal.confidence * 100).toFixed(0)}%
                </div>

                <div className="schema-section">
                  <h4>Proposed Schema</h4>
                  <pre className="schema-preview">
                    {JSON.stringify(selectedProposal.proposed_schema, null, 2)}
                  </pre>
                </div>

                <div className="schema-section">
                  <h4>Sample Data ({selectedProposal.sample_rows.length} rows)</h4>
                  <div className="sample-data">
                    <table>
                      <thead>
                        <tr>
                          {selectedProposal.sample_rows[0] &&
                            Object.keys(selectedProposal.sample_rows[0]).map((key) => (
                              <th key={key}>{key}</th>
                            ))}
                        </tr>
                      </thead>
                      <tbody>
                        {selectedProposal.sample_rows.slice(0, 5).map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row).map((val, i) => (
                              <td key={i}>{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="schema-section">
                  <h4>Rejection Reason (optional)</h4>
                  <textarea
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="Enter reason for rejection..."
                    rows={3}
                  />
                </div>

                <div className="proposal-actions">
                  <button
                    onClick={() => handleApprove(selectedProposal.proposal_id)}
                    className="btn-approve"
                  >
                    ✓ Approve Schema
                  </button>
                  <button
                    onClick={() => handleReject(selectedProposal.proposal_id)}
                    className="btn-reject"
                  >
                    ✗ Reject
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
