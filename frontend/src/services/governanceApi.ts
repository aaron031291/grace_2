/**
 * Governance API Service
 * Handles approval requests, decisions, and audit logs
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export interface ApprovalRequest {
  id: number;
  event_id: number;
  status: 'pending' | 'approved' | 'rejected';
  requested_by: string;
  reason: string;
  created_at: string;
  decided_at?: string;
  decision_by?: string;
  decision_reason?: string;
  resource_type?: string;
  resource_id?: string;
  action?: string;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
  context?: Record<string, any>;
}

export interface ApprovalDecision {
  decision: 'approve' | 'reject';
  reason: string;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  actor: string;
  action: string;
  resource: string;
  result: 'success' | 'failure';
  metadata?: Record<string, any>;
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token') || 'dev-token';
  const userId = localStorage.getItem('user_id') || 'aaron';
  
  return {
    'Authorization': `Bearer ${token}`,
    'X-User-ID': userId,
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'API error');
  }
  return response.json();
}

/**
 * Get pending approval requests
 */
export async function getPendingApprovals(): Promise<ApprovalRequest[]> {
  const response = await fetch(`${API_BASE}/api/governance/approvals?status=pending`, {
    headers: getAuthHeaders(),
  });
  
  return handleResponse<ApprovalRequest[]>(response);
}

/**
 * Get all approval requests (with filters)
 */
export async function getApprovals(filters?: {
  status?: string;
  limit?: number;
}): Promise<ApprovalRequest[]> {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.limit) params.append('limit', filters.limit.toString());

  const response = await fetch(`${API_BASE}/api/governance/approvals?${params}`, {
    headers: getAuthHeaders(),
  });
  
  return handleResponse<ApprovalRequest[]>(response);
}

/**
 * Get single approval request
 */
export async function getApprovalDetails(requestId: number): Promise<ApprovalRequest> {
  const response = await fetch(`${API_BASE}/api/governance/approvals/${requestId}`, {
    headers: getAuthHeaders(),
  });
  
  return handleResponse<ApprovalRequest>(response);
}

/**
 * Approve a request
 */
export async function approveRequest(
  requestId: number,
  reason: string = 'Approved via console'
): Promise<any> {
  const response = await fetch(`${API_BASE}/api/governance/approvals/${requestId}/decide`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ decision: 'approve', reason }),
  });
  
  return handleResponse(response);
}

/**
 * Reject a request
 */
export async function rejectRequest(
  requestId: number,
  reason: string
): Promise<any> {
  if (!reason.trim()) {
    throw new Error('Rejection reason is required');
  }

  const response = await fetch(`${API_BASE}/api/governance/approvals/${requestId}/decide`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ decision: 'reject', reason }),
  });
  
  return handleResponse(response);
}

/**
 * Get approval statistics
 */
export async function getApprovalStats(): Promise<{
  pending: number;
  approved: number;
  rejected: number;
  total: number;
}> {
  const response = await fetch(`${API_BASE}/api/governance/approvals/stats`, {
    headers: getAuthHeaders(),
  });
  
  return handleResponse(response);
}

/**
 * Get audit logs
 */
export async function getAuditLogs(filters?: {
  actor?: string;
  action?: string;
  resource?: string;
  limit?: number;
}): Promise<AuditLog[]> {
  const params = new URLSearchParams();
  if (filters?.actor) params.append('actor', filters.actor);
  if (filters?.action) params.append('action', filters.action);
  if (filters?.resource) params.append('resource', filters.resource);
  if (filters?.limit) params.append('limit', filters.limit.toString());

  const response = await fetch(`${API_BASE}/api/governance/audit-log?${params}`, {
    headers: getAuthHeaders(),
  });
  
  return handleResponse<AuditLog[]>(response);
}

/**
 * Ask Grace about an approval (for context)
 */
export async function askGraceAboutApproval(
  requestId: number,
  question?: string
): Promise<{ response: string; context: any }> {
  const approval = await getApprovalDetails(requestId);
  
  const defaultQuestion = `Why was approval request ${requestId} created? ` +
    `It involves ${approval.action} on ${approval.resource_type} ${approval.resource_id}. ` +
    `Should I approve it?`;

  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: question || defaultQuestion,
      context: { approval_request: approval },
    }),
  });
  
  const result = await handleResponse<any>(response);
  
  return {
    response: result.response || result.message,
    context: result.metadata || {},
  };
}
