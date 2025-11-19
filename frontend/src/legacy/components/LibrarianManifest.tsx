/**
 * Librarian Manifest
 * Shows what Librarian did today and what needs approval
 */

import { useState, useEffect } from 'react';
import {
  Calendar,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  FileText,
  Database,
  Shield
} from 'lucide-react';

interface DailySummary {
  date: string;
  new_files: number;
  tables_updated: number;
  schemas_proposed: number;
  schemas_approved: number;
  ingestion_jobs: number;
  trust_audits: number;
  agents_spawned: number;
  approvals_pending: number;
}

interface PendingApproval {
  id: string;
  type: string;
  title: string;
  description: string;
  confidence: number;
  submitted_at: string;
}

export function LibrarianManifest() {
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>([]);

  useEffect(() => {
    loadData();
    
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    await Promise.all([
      loadDailySummary(),
      loadPendingApprovals()
    ]);
  }

  async function loadDailySummary() {
    try {
      const response = await fetch('/api/librarian/daily-summary');
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  }

  async function loadPendingApprovals() {
    try {
      const response = await fetch('/api/librarian/pending-approvals');
      if (response.ok) {
        const data = await response.json();
        setPendingApprovals(data.approvals || []);
      }
    } catch (err) {
      console.error('Failed to load approvals:', err);
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6 bg-gray-900 text-white">
      {/* What Changed Today */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Calendar className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold">What Changed Today</h2>
        </div>

        {summary ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">New Files</div>
              <div className="text-2xl font-bold text-blue-400">{summary.new_files}</div>
            </div>

            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Tables Updated</div>
              <div className="text-2xl font-bold text-green-400">{summary.tables_updated}</div>
            </div>

            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Schemas Proposed</div>
              <div className="text-2xl font-bold text-purple-400">{summary.schemas_proposed}</div>
              <div className="text-xs text-green-400 mt-1">
                {summary.schemas_approved} approved
              </div>
            </div>

            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Ingestion Jobs</div>
              <div className="text-2xl font-bold text-yellow-400">{summary.ingestion_jobs}</div>
            </div>

            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Trust Audits</div>
              <div className="text-2xl font-bold text-orange-400">{summary.trust_audits}</div>
            </div>

            <div className="p-4 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Agents Spawned</div>
              <div className="text-2xl font-bold text-cyan-400">{summary.agents_spawned}</div>
            </div>

            <div className="p-4 bg-gray-800 rounded-lg border-2 border-orange-500">
              <div className="text-xs text-gray-400 mb-1">Needs Approval</div>
              <div className="text-2xl font-bold text-orange-400">{summary.approvals_pending}</div>
            </div>
          </div>
        ) : (
          <div className="text-gray-500">Loading summary...</div>
        )}
      </div>

      {/* Pending Approvals */}
      {pendingApprovals.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="w-6 h-6 text-orange-400" />
            <h2 className="text-xl font-semibold">Needs Your Approval</h2>
            <span className="px-2 py-1 bg-orange-900 text-orange-300 text-xs rounded">
              {pendingApprovals.length}
            </span>
          </div>

          <div className="space-y-3">
            {pendingApprovals.map(approval => (
              <div
                key={approval.id}
                className="p-4 bg-gray-800 rounded-lg border-l-4 border-orange-500"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold">{approval.title}</h3>
                    <p className="text-sm text-gray-400 mt-1">{approval.description}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded ${
                    approval.confidence >= 0.8
                      ? 'bg-green-900 text-green-300'
                      : 'bg-yellow-900 text-yellow-300'
                  }`}>
                    {(approval.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                  <Clock className="w-3 h-3" />
                  {new Date(approval.submitted_at).toLocaleString()}
                </div>

                <div className="flex gap-2">
                  <button className="px-3 py-1 text-sm bg-green-600 hover:bg-green-500 rounded transition-colors">
                    ✓ Approve
                  </button>
                  <button className="px-3 py-1 text-sm bg-red-600 hover:bg-red-500 rounded transition-colors">
                    ✗ Reject
                  </button>
                  <button className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Kernel & Agent Status */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp className="w-6 h-6 text-green-400" />
          <h2 className="text-xl font-semibold">Active Components</h2>
        </div>

        <div className="bg-gray-800 rounded-lg p-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="font-medium">Librarian Kernel</span>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <span className="text-gray-400">Status: <span className="text-green-400">Running</span></span>
                <span className="text-gray-400">Trust: <span className="text-green-400">100%</span></span>
              </div>
            </div>

            <div className="text-xs text-gray-500 px-3">
              Monitoring 3 directories • Processing 0 files • 0 active agents
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
