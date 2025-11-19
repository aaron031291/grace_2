/**
 * Schema Review Modal
 * Review and approve/reject schema proposals
 */

import { useState } from 'react';
import {
  CheckCircle,
  XCircle,
  FileText,
  Table,
  AlertCircle,
  TrendingUp,
  X
} from 'lucide-react';

interface SchemaProposal {
  proposal_id: string;
  file_path: string;
  recommended_table: string;
  confidence: number;
  table_exists: boolean;
  extracted_fields: Record<string, any>;
  reasoning: string;
  timestamp: string;
}

interface SchemaReviewModalProps {
  proposals: SchemaProposal[];
  onApprove: (proposalId: string) => Promise<void>;
  onReject: (proposalId: string, reason: string) => Promise<void>;
  onClose?: () => void;
}

export function SchemaReviewModal({ 
  proposals, 
  onApprove, 
  onReject,
  onClose 
}: SchemaReviewModalProps) {
  const [selectedProposal, setSelectedProposal] = useState<SchemaProposal | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [loading, setLoading] = useState(false);

  if (proposals.length === 0) {
    return null;
  }

  const handleApprove = async (proposalId: string) => {
    setLoading(true);
    try {
      await onApprove(proposalId);
      setSelectedProposal(null);
    } catch (err) {
      console.error('Approval failed:', err);
      alert('Failed to approve proposal');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (proposalId: string) => {
    setLoading(true);
    try {
      await onReject(proposalId, rejectReason);
      setSelectedProposal(null);
      setRejectReason('');
    } catch (err) {
      console.error('Rejection failed:', err);
      alert('Failed to reject proposal');
    } finally {
      setLoading(false);
    }
  };

  const currentProposal = selectedProposal || proposals[0];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Table className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-bold text-white">
              Schema Proposals ({proposals.length} pending)
            </h2>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-700 rounded"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          )}
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* Proposal List */}
          <div className="w-64 border-r border-gray-700 overflow-y-auto">
            {proposals.map(proposal => (
              <div
                key={proposal.proposal_id}
                onClick={() => setSelectedProposal(proposal)}
                className={`
                  p-3 cursor-pointer hover:bg-gray-700 border-b border-gray-700
                  ${currentProposal.proposal_id === proposal.proposal_id ? 'bg-gray-700' : ''}
                `}
              >
                <div className="flex items-center gap-2 mb-1">
                  <FileText className="w-3 h-3 text-blue-400" />
                  <span className="text-sm font-medium text-white truncate">
                    {proposal.file_path.split('/').pop()}
                  </span>
                </div>
                
                <div className="text-xs text-gray-400 mb-1">
                  → {proposal.recommended_table.replace('memory_', '')}
                </div>
                
                <div
                  className={`
                    text-xs px-1.5 py-0.5 rounded inline-block
                    ${proposal.confidence >= 0.8
                      ? 'bg-green-900 text-green-300'
                      : proposal.confidence >= 0.6
                      ? 'bg-yellow-900 text-yellow-300'
                      : 'bg-red-900 text-red-300'
                    }
                  `}
                >
                  {Math.round(proposal.confidence * 100)}% confident
                </div>
              </div>
            ))}
          </div>

          {/* Proposal Detail */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-3xl">
              {/* File Info */}
              <div className="mb-6">
                <div className="text-sm text-gray-400 mb-1">File Path</div>
                <div className="font-mono text-sm text-white bg-gray-900 px-3 py-2 rounded">
                  {currentProposal.file_path}
                </div>
              </div>

              {/* Target Table */}
              <div className="mb-6">
                <div className="text-sm text-gray-400 mb-1">Target Table</div>
                <div className="flex items-center gap-2">
                  <Table className="w-4 h-4 text-blue-400" />
                  <span className="text-lg font-medium text-white">
                    {currentProposal.recommended_table}
                  </span>
                  {!currentProposal.table_exists && (
                    <span className="px-2 py-1 bg-purple-900 text-purple-300 text-xs rounded">
                      New Table
                    </span>
                  )}
                </div>
              </div>

              {/* Confidence */}
              <div className="mb-6">
                <div className="text-sm text-gray-400 mb-2">Confidence Score</div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-700 rounded-full h-3 overflow-hidden">
                    <div
                      className={`
                        h-full transition-all
                        ${currentProposal.confidence >= 0.8
                          ? 'bg-green-500'
                          : currentProposal.confidence >= 0.6
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                        }
                      `}
                      style={{ width: `${currentProposal.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-white font-bold">
                    {Math.round(currentProposal.confidence * 100)}%
                  </span>
                </div>
              </div>

              {/* AI Reasoning */}
              <div className="mb-6">
                <div className="text-sm text-gray-400 mb-2">AI Reasoning</div>
                <div className="bg-gray-900 p-4 rounded text-sm text-gray-300 leading-relaxed">
                  {currentProposal.reasoning}
                </div>
              </div>

              {/* Extracted Fields */}
              <div className="mb-6">
                <div className="text-sm text-gray-400 mb-2">
                  Extracted Fields ({Object.keys(currentProposal.extracted_fields).length})
                </div>
                <div className="bg-gray-900 rounded overflow-hidden">
                  {Object.entries(currentProposal.extracted_fields).map(([key, value]) => (
                    <div
                      key={key}
                      className="border-b border-gray-800 last:border-0 px-4 py-3 flex justify-between items-start"
                    >
                      <span className="font-mono text-sm text-blue-400">{key}</span>
                      <span className="text-sm text-gray-300 max-w-md text-right break-words">
                        {typeof value === 'object'
                          ? JSON.stringify(value, null, 2)
                          : String(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Reject Reason (if rejecting) */}
              <div className="mb-6">
                <div className="text-sm text-gray-400 mb-2">Rejection Reason (Optional)</div>
                <textarea
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Explain why this proposal should be rejected..."
                  className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm text-white resize-none"
                  rows={3}
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => handleApprove(currentProposal.proposal_id)}
                  disabled={loading}
                  className="
                    flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 
                    disabled:text-gray-500 py-3 rounded font-medium 
                    flex items-center justify-center gap-2 text-white
                  "
                >
                  <CheckCircle className="w-5 h-5" />
                  Approve & Insert
                </button>
                
                <button
                  onClick={() => handleReject(currentProposal.proposal_id)}
                  disabled={loading}
                  className="
                    flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 
                    disabled:text-gray-500 py-3 rounded font-medium 
                    flex items-center justify-center gap-2 text-white
                  "
                >
                  <XCircle className="w-5 h-5" />
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
