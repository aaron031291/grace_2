/**
 * Schema Approval Panel
 * View and approve/reject schema proposals from auto-ingestion
 */

import { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Table,
  AlertCircle,
  TrendingUp,
  Eye
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
  action?: 'row_insertion' | 'table_creation' | 'schema_modification';
}

export function SchemaApprovalPanel() {
  const [proposals, setProposals] = useState<SchemaProposal[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<SchemaProposal | null>(null);
  const [filter, setFilter] = useState<'all' | 'high_confidence' | 'low_confidence'>('all');

  useEffect(() => {
    loadProposals();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(loadProposals, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadProposals() {
    try {
      const response = await fetch('http://localhost:8000/api/memory/tables/proposals/pending');
      const data = await response.json();
      setProposals(data.proposals || []);
    } catch (err) {
      console.error('Failed to load proposals:', err);
    }
  }

  async function approveProposal(proposalId: string) {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/memory/tables/proposals/${proposalId}/approve`,
        { method: 'POST' }
      );
      const result = await response.json();
      
      if (result.success) {
        await loadProposals();
        setSelectedProposal(null);
      } else {
        alert(`Failed to approve: ${result.error}`);
      }
    } catch (err) {
      console.error('Approval failed:', err);
      alert('Approval failed');
    } finally {
      setLoading(false);
    }
  }

  async function rejectProposal(proposalId: string, reason: string) {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/memory/tables/proposals/${proposalId}/reject`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reason })
        }
      );
      const result = await response.json();
      
      if (result.success) {
        await loadProposals();
        setSelectedProposal(null);
      }
    } catch (err) {
      console.error('Rejection failed:', err);
    } finally {
      setLoading(false);
    }
  }

  const filteredProposals = proposals.filter(p => {
    if (filter === 'high_confidence') return p.confidence >= 0.8;
    if (filter === 'low_confidence') return p.confidence < 0.8;
    return true;
  });

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Table className="w-5 h-5" />
          Schema Proposals
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Review and approve auto-detected schema proposals
        </p>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-700 flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1 rounded text-sm ${
            filter === 'all' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          All ({proposals.length})
        </button>
        <button
          onClick={() => setFilter('high_confidence')}
          className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
            filter === 'high_confidence' ? 'bg-green-600' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          <TrendingUp className="w-3 h-3" />
          High Confidence
        </button>
        <button
          onClick={() => setFilter('low_confidence')}
          className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
            filter === 'low_confidence' ? 'bg-yellow-600' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          <AlertCircle className="w-3 h-3" />
          Needs Review
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Proposal List */}
        <div className="w-1/2 border-r border-gray-700 overflow-y-auto">
          {filteredProposals.length === 0 ? (
            <div className="p-8 text-center text-gray-400">
              <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No pending proposals</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-700">
              {filteredProposals.map(proposal => (
                <div
                  key={proposal.proposal_id}
                  onClick={() => setSelectedProposal(proposal)}
                  className={`p-4 cursor-pointer hover:bg-gray-800 transition ${
                    selectedProposal?.proposal_id === proposal.proposal_id ? 'bg-gray-800' : ''
                  }`}
                >
                  {/* Proposal Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-blue-400" />
                      <span className="font-medium text-sm">
                        {proposal.file_path.split('/').pop()}
                      </span>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        proposal.confidence >= 0.8
                          ? 'bg-green-900 text-green-300'
                          : proposal.confidence >= 0.6
                          ? 'bg-yellow-900 text-yellow-300'
                          : 'bg-red-900 text-red-300'
                      }`}
                    >
                      {Math.round(proposal.confidence * 100)}% confident
                    </span>
                  </div>

                  {/* Target Table */}
                  <div className="flex items-center gap-2 mb-2">
                    <Table className="w-3 h-3 text-gray-400" />
                    <span className="text-sm text-gray-300">
                      {proposal.recommended_table}
                    </span>
                    {!proposal.table_exists && (
                      <span className="px-1.5 py-0.5 bg-purple-900 text-purple-300 text-xs rounded">
                        New Table
                      </span>
                    )}
                  </div>

                  {/* Reasoning Preview */}
                  <p className="text-xs text-gray-400 line-clamp-2">
                    {proposal.reasoning}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Proposal Detail */}
        <div className="flex-1 overflow-y-auto">
          {selectedProposal ? (
            <div className="p-6">
              {/* Header */}
              <div className="mb-6">
                <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Proposal Details
                </h3>
                <p className="text-sm text-gray-400">
                  {selectedProposal.file_path}
                </p>
              </div>

              {/* Metadata */}
              <div className="mb-6 grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-gray-400 mb-1">Target Table</div>
                  <div className="font-medium">{selectedProposal.recommended_table}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Confidence</div>
                  <div className="font-medium">
                    {Math.round(selectedProposal.confidence * 100)}%
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Action</div>
                  <div className="font-medium capitalize">
                    {selectedProposal.table_exists ? 'Row Insertion' : 'Table Creation'}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Timestamp</div>
                  <div className="font-medium text-sm">
                    {new Date(selectedProposal.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>

              {/* Reasoning */}
              <div className="mb-6">
                <div className="text-xs text-gray-400 mb-2">AI Reasoning</div>
                <div className="bg-gray-800 p-3 rounded text-sm">
                  {selectedProposal.reasoning}
                </div>
              </div>

              {/* Extracted Fields */}
              <div className="mb-6">
                <div className="text-xs text-gray-400 mb-2">Extracted Fields</div>
                <div className="bg-gray-800 rounded overflow-hidden">
                  {Object.entries(selectedProposal.extracted_fields).map(([key, value]) => (
                    <div key={key} className="border-b border-gray-700 last:border-0">
                      <div className="p-3 flex justify-between items-start">
                        <span className="font-mono text-sm text-blue-400">{key}</span>
                        <span className="text-sm text-gray-300 max-w-md text-right break-words">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => approveProposal(selectedProposal.proposal_id)}
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:text-gray-500 py-2 rounded font-medium flex items-center justify-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Approve & Insert
                </button>
                <button
                  onClick={() => {
                    const reason = prompt('Reason for rejection (optional):');
                    if (reason !== null) {
                      rejectProposal(selectedProposal.proposal_id, reason);
                    }
                  }}
                  disabled={loading}
                  className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:text-gray-500 py-2 rounded font-medium flex items-center justify-center gap-2"
                >
                  <XCircle className="w-4 h-4" />
                  Reject
                </button>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <Table className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p>Select a proposal to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
