import { http } from './client';

export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

export interface ApprovalItem {
  id: number;
  event_id: number;
  status: ApprovalStatus;
  requested_by?: string;
  reason?: string;
  decision_by?: string | null;
  decision_reason?: string | null;
  created_at?: string;
  decided_at?: string | null;
}

export interface ApprovalsListResponse extends Array<ApprovalItem> {}

export async function listApprovals(params?: { status?: ApprovalStatus; requested_by?: string; limit?: number; }): Promise<ApprovalsListResponse> {
  return await http.get<ApprovalsListResponse>('/api/governance/approvals', { query: params });
}

export async function getApproval(id: number): Promise<ApprovalItem> {
  return await http.get<ApprovalItem>(`/api/governance/approvals/${id}`);
}

export async function decideApproval(id: number, decision: 'approve' | 'reject', reason: string = ''): Promise<{ id: number; status: ApprovalStatus; decision_by?: string; decision_reason?: string; decided_at?: string; _verification_id?: string; }> {
  return await http.post(`/api/governance/approvals/${id}/decision`, { decision, reason });
}
