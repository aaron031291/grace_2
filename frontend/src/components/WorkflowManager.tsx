import React, { useState, useEffect } from 'react';

interface Workflow {
  workflow_id: string;
  title: string;
  description: string;
  status: string;
  created_by: string;
  reviewers: string[];
  checklist: Array<{ item: string; completed: boolean }>;
  approval_count: number;
  rejection_count: number;
  checklist_progress: number;
  created_at: string;
}

interface WorkflowManagerProps {
  token: string;
  userId: string;
}

export const WorkflowManager: React.FC<WorkflowManagerProps> = ({ token, userId }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/collaboration/workflows', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setWorkflows(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  };

  const approveWorkflow = async (workflowId: string) => {
    try {
      await fetch(`http://localhost:8000/api/collaboration/workflows/${workflowId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ comments: '' })
      });
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to approve workflow:', error);
    }
  };

  const rejectWorkflow = async (workflowId: string, reason: string) => {
    try {
      await fetch(`http://localhost:8000/api/collaboration/workflows/${workflowId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ reason })
      });
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to reject workflow:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#2ecc71';
      case 'rejected': return '#e74c3c';
      case 'in_review': return '#f39c12';
      case 'pending': return '#95a5a6';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="workflow-manager">
      <div className="workflow-header">
        <h3 className="section-title">Workflows</h3>
        <button className="create-btn" onClick={() => setShowCreateModal(true)}>
          + Create Workflow
        </button>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
        </div>
      ) : workflows.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📋</span>
          <p>No workflows yet</p>
        </div>
      ) : (
        <div className="workflows-grid">
          {workflows.map((workflow) => (
            <div
              key={workflow.workflow_id}
              className="workflow-card"
              onClick={() => setSelectedWorkflow(workflow)}
            >
              <div className="workflow-header-section">
                <div className="workflow-title">{workflow.title}</div>
                <div
                  className="workflow-status"
                  style={{ background: getStatusColor(workflow.status) }}
                >
                  {workflow.status.replace('_', ' ')}
                </div>
              </div>

              <div className="workflow-description">{workflow.description}</div>

              <div className="workflow-meta">
                <div className="meta-item">
                  <span className="meta-icon">👤</span>
                  <span className="meta-text">{workflow.reviewers.length} reviewers</span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon">✓</span>
                  <span className="meta-text">{workflow.approval_count} approvals</span>
                </div>
              </div>

              {workflow.checklist.length > 0 && (
                <div className="workflow-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${workflow.checklist_progress * 100}%` }}
                    />
                  </div>
                  <div className="progress-text">
                    {Math.round(workflow.checklist_progress * 100)}% complete
                  </div>
                </div>
              )}

              <div className="workflow-actions">
                {workflow.status === 'pending' && (
                  <>
                    <button
                      className="workflow-action-btn approve"
                      onClick={(e) => {
                        e.stopPropagation();
                        approveWorkflow(workflow.workflow_id);
                      }}
                    >
                      ✓ Approve
                    </button>
                    <button
                      className="workflow-action-btn reject"
                      onClick={(e) => {
                        e.stopPropagation();
                        const reason = prompt('Rejection reason:');
                        if (reason) rejectWorkflow(workflow.workflow_id, reason);
                      }}
                    >
                      × Reject
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
