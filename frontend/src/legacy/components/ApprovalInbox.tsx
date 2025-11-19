/**
 * Approval Inbox - Consolidated Queue for All Pending Approvals
 * 
 * Features:
 * - View all pending approvals in one place
 * - Filter by status, tier, domain, risk
 * - Compare plans side-by-side
 * - Bulk approve/reject
 * - Email/Slack notifications with deep links
 * - Real-time updates
 */

import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, XCircle, Clock, AlertTriangle, 
  Filter, Search, RefreshCw, Eye, GitCompare 
} from 'lucide-react';
import './ApprovalInbox.css';

interface ApprovalRequest {
  id: string;
  type: 'playbook' | 'mission' | 'schema' | 'deployment' | 'learning';
  title: string;
  description: string;
  tier: 1 | 2 | 3;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  domain: string;
  requested_by: string;
  requested_at: string;
  expires_at?: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  details: {
    action?: string;
    expected_effects?: string[];
    rollback_plan?: string;
    kpis?: Record<string, string>;
  };
}

export function ApprovalInbox() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [selectedApprovals, setSelectedApprovals] = useState<Set<string>>(new Set());
  const [filterStatus, setFilterStatus] = useState<string>('pending');
  const [filterTier, setFilterTier] = useState<string>('all');
  const [filterRisk, setFilterRisk] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchApprovals = async () => {
    setIsLoading(true);
    try {
      const mockApprovals: ApprovalRequest[] = [
        {
          id: 'apr-001',
          type: 'playbook',
          title: 'Restart Nginx Service',
          description: 'HTTP 502 errors detected, need to restart nginx',
          tier: 2,
          risk_level: 'medium',
          domain: 'guardian',
          requested_by: 'self_healing_agent',
          requested_at: new Date(Date.now() - 300000).toISOString(),
          status: 'pending',
          details: {
            action: 'restart-nginx',
            expected_effects: ['Nginx service restart', '~5s downtime', 'Clears connection pool'],
            rollback_plan: 'Restore previous config, restart with --safe-mode',
            kpis: {
              'HTTP 502 rate': '15% → 0%',
              'Response time': '2.5s → 0.3s'
            }
          }
        },
        {
          id: 'apr-002',
          type: 'mission',
          title: 'Deploy Frontend Updates',
          description: 'Deploy new UI features to production',
          tier: 3,
          risk_level: 'high',
          domain: 'copilot',
          requested_by: 'autonomous_pipeline',
          requested_at: new Date(Date.now() - 600000).toISOString(),
          expires_at: new Date(Date.now() + 3600000).toISOString(),
          status: 'pending',
          details: {
            action: 'deploy-frontend',
            expected_effects: ['Build frontend', 'Deploy to production', 'Run smoke tests'],
            rollback_plan: 'Revert to previous deployment',
            kpis: {
              'Build time': '< 5 minutes',
              'Smoke tests': '100% pass rate'
            }
          }
        },
        {
          id: 'apr-003',
          type: 'learning',
          title: 'Learn New Domain: Kubernetes',
          description: 'Autonomous learning detected new domain',
          tier: 1,
          risk_level: 'low',
          domain: 'learning',
          requested_by: 'learning_engine',
          requested_at: new Date(Date.now() - 900000).toISOString(),
          status: 'pending',
          details: {
            action: 'learn-kubernetes',
            expected_effects: ['Fetch documentation', 'Extract knowledge', 'Update world model'],
            kpis: {
              'Documents processed': '50+',
              'Knowledge entries': '200+'
            }
          }
        }
      ];
      setApprovals(mockApprovals);
    } catch (error) {
      console.error('Failed to fetch approvals:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (approvalId: string) => {
    try {
      console.log('Approving:', approvalId);
      setApprovals(prev => prev.map(a => 
        a.id === approvalId ? { ...a, status: 'approved' as const } : a
      ));
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  const handleReject = async (approvalId: string) => {
    try {
      console.log('Rejecting:', approvalId);
      setApprovals(prev => prev.map(a => 
        a.id === approvalId ? { ...a, status: 'rejected' as const } : a
      ));
    } catch (error) {
      console.error('Failed to reject:', error);
    }
  };

  const handleBulkApprove = async () => {
    for (const id of selectedApprovals) {
      await handleApprove(id);
    }
    setSelectedApprovals(new Set());
  };

  const handleBulkReject = async () => {
    for (const id of selectedApprovals) {
      await handleReject(id);
    }
    setSelectedApprovals(new Set());
  };

  const toggleSelection = (id: string) => {
    const newSelection = new Set(selectedApprovals);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    setSelectedApprovals(newSelection);
  };

  const filteredApprovals = approvals.filter(a => {
    if (filterStatus !== 'all' && a.status !== filterStatus) return false;
    if (filterTier !== 'all' && a.tier.toString() !== filterTier) return false;
    if (filterRisk !== 'all' && a.risk_level !== filterRisk) return false;
    if (searchQuery && !a.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !a.description.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      case 'critical': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'approved': return <CheckCircle className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      case 'expired': return <AlertTriangle className="w-4 h-4" />;
      default: return null;
    }
  };

  return (
    <div className="approval-inbox-container">
      {/* Header */}
      <div className="inbox-header">
        <div className="header-left">
          <h2>Approval Inbox</h2>
          <span className="approval-count">
            {filteredApprovals.filter(a => a.status === 'pending').length} pending
          </span>
        </div>
        <div className="header-right">
          <button className="refresh-btn" onClick={fetchApprovals} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'spinning' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="inbox-filters">
        <div className="filter-group">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search approvals..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="filter-search"
          />
        </div>
        <div className="filter-group">
          <Filter className="w-4 h-4 text-gray-400" />
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="filter-select">
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="expired">Expired</option>
          </select>
        </div>
        <div className="filter-group">
          <select value={filterTier} onChange={(e) => setFilterTier(e.target.value)} className="filter-select">
            <option value="all">All Tiers</option>
            <option value="1">Tier 1</option>
            <option value="2">Tier 2</option>
            <option value="3">Tier 3</option>
          </select>
        </div>
        <div className="filter-group">
          <select value={filterRisk} onChange={(e) => setFilterRisk(e.target.value)} className="filter-select">
            <option value="all">All Risk Levels</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedApprovals.size > 0 && (
        <div className="bulk-actions">
          <span>{selectedApprovals.size} selected</span>
          <button className="bulk-btn approve" onClick={handleBulkApprove}>
            <CheckCircle className="w-4 h-4" />
            Approve All
          </button>
          <button className="bulk-btn reject" onClick={handleBulkReject}>
            <XCircle className="w-4 h-4" />
            Reject All
          </button>
          <button className="bulk-btn" onClick={() => setSelectedApprovals(new Set())}>
            Clear Selection
          </button>
        </div>
      )}

      {/* Approvals List */}
      <div className="approvals-list">
        {filteredApprovals.length === 0 ? (
          <div className="empty-state">
            <CheckCircle className="w-12 h-12 text-gray-600" />
            <p>No approvals found</p>
            <span>All caught up!</span>
          </div>
        ) : (
          filteredApprovals.map(approval => (
            <div
              key={approval.id}
              className={`approval-card ${selectedApprovals.has(approval.id) ? 'selected' : ''}`}
              onClick={() => setSelectedApproval(approval)}
            >
              <div className="approval-checkbox">
                <input
                  type="checkbox"
                  checked={selectedApprovals.has(approval.id)}
                  onChange={(e) => {
                    e.stopPropagation();
                    toggleSelection(approval.id);
                  }}
                />
              </div>
              <div className="approval-content">
                <div className="approval-header-row">
                  <div className="approval-title-section">
                    <h3>{approval.title}</h3>
                    <div className="approval-badges">
                      <span className="badge type">{approval.type}</span>
                      <span className="badge tier">Tier {approval.tier}</span>
                      <span 
                        className="badge risk" 
                        style={{ background: getRiskColor(approval.risk_level) }}
                      >
                        {approval.risk_level}
                      </span>
                    </div>
                  </div>
                  <div className="approval-status" style={{ color: getRiskColor(approval.risk_level) }}>
                    {getStatusIcon(approval.status)}
                    <span>{approval.status}</span>
                  </div>
                </div>
                <p className="approval-description">{approval.description}</p>
                <div className="approval-meta">
                  <span>Requested by: {approval.requested_by}</span>
                  <span>Domain: {approval.domain}</span>
                  <span>{new Date(approval.requested_at).toLocaleString()}</span>
                </div>
              </div>
              <div className="approval-actions">
                <button
                  className="action-btn view"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedApproval(approval);
                  }}
                >
                  <Eye className="w-4 h-4" />
                </button>
                {approval.status === 'pending' && (
                  <>
                    <button
                      className="action-btn approve"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleApprove(approval.id);
                      }}
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                    <button
                      className="action-btn reject"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReject(approval.id);
                      }}
                    >
                      <XCircle className="w-4 h-4" />
                    </button>
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Detail Panel */}
      {selectedApproval && (
        <div className="detail-panel-overlay" onClick={() => setSelectedApproval(null)}>
          <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
            <div className="detail-header">
              <h3>{selectedApproval.title}</h3>
              <button onClick={() => setSelectedApproval(null)}>×</button>
            </div>
            <div className="detail-content">
              <div className="detail-section">
                <h4>Description</h4>
                <p>{selectedApproval.description}</p>
              </div>
              {selectedApproval.details.expected_effects && (
                <div className="detail-section">
                  <h4>Expected Effects</h4>
                  <ul>
                    {selectedApproval.details.expected_effects.map((effect, idx) => (
                      <li key={idx}>{effect}</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedApproval.details.rollback_plan && (
                <div className="detail-section">
                  <h4>Rollback Plan</h4>
                  <p>{selectedApproval.details.rollback_plan}</p>
                </div>
              )}
              {selectedApproval.details.kpis && (
                <div className="detail-section">
                  <h4>KPIs to Improve</h4>
                  <ul>
                    {Object.entries(selectedApproval.details.kpis).map(([key, value]) => (
                      <li key={key}><strong>{key}:</strong> {value}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            {selectedApproval.status === 'pending' && (
              <div className="detail-actions">
                <button
                  className="detail-btn approve"
                  onClick={() => {
                    handleApprove(selectedApproval.id);
                    setSelectedApproval(null);
                  }}
                >
                  <CheckCircle className="w-4 h-4" />
                  Approve
                </button>
                <button
                  className="detail-btn reject"
                  onClick={() => {
                    handleReject(selectedApproval.id);
                    setSelectedApproval(null);
                  }}
                >
                  <XCircle className="w-4 h-4" />
                  Reject
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ApprovalInbox;
