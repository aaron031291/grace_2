import { http } from './client';

// Memory -------------------------------------------------
export interface MemoryDomainSummary {
  count: number;
  categories: string[];
}

export interface MemoryDomainsResponse {
  domains: Record<string, MemoryDomainSummary>;
}

export interface MemoryArtifact {
  id: number;
  path: string;
  domain: string;
  category: string;
  status: string;
  version: number;
  size?: number;
  updated_at?: string;
}

export interface MemoryTreeResponse {
  tree: Record<string, unknown>;
  flat_list: MemoryArtifact[];
}

export async function fetchMemoryDomains(): Promise<MemoryDomainsResponse> {
  return await http.get<MemoryDomainsResponse>('/api/memory/domains');
}

export async function fetchMemoryTree(domain?: string, category?: string): Promise<MemoryTreeResponse> {
  return await http.get<MemoryTreeResponse>('/api/memory/tree', {
    query: {
      domain,
      category,
    },
  });
}

// Tasks -------------------------------------------------
export interface TaskItem {
  id: number;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  auto_generated: boolean;
  created_at: string;
  completed_at?: string | null;
}

export async function fetchTasks(): Promise<TaskItem[]> {
  return await http.get<TaskItem[]>('/api/tasks/');
}

export async function createTask(payload: { title: string; description?: string; priority?: string }): Promise<TaskItem> {
  return await http.post<TaskItem>('/api/tasks/', payload);
}

export async function updateTaskStatus(taskId: number, updates: Partial<Pick<TaskItem, 'status' | 'priority' | 'title' | 'description'>>): Promise<TaskItem> {
  return await http.patch<TaskItem>(`/api/tasks/${taskId}`, updates);
}

// Autonomy -------------------------------------------------
export interface AutonomyStatusResponse {
  tiers: Record<string, number>;
  pending_approvals: number;
  total_policies: number;
}

export interface AutonomyApproval {
  id: string;
  action: string;
  description: string;
  tier: string;
  impact: string;
  requested_at: string;
  context: Record<string, unknown>;
}

export interface AutonomyCheckResponse {
  can_execute: boolean;
  approval_id?: string | null;
  requires_approval?: boolean | null;
  tier?: string | null;
}

export interface AutonomyPolicyEntry {
  name: string;
  description: string;
  approval_required?: boolean;
  auto_approved?: boolean;
  impact: string;
}

export interface AutonomyPoliciesResponse {
  tier_1_operational: AutonomyPolicyEntry[];
  tier_2_code_touching: AutonomyPolicyEntry[];
  tier_3_governance: AutonomyPolicyEntry[];
}

export async function fetchAutonomyStatus(): Promise<AutonomyStatusResponse> {
  return await http.get<AutonomyStatusResponse>('/api/autonomy/status');
}

export async function fetchAutonomyApprovals(): Promise<AutonomyApproval[]> {
  return await http.get<AutonomyApproval[]>('/api/autonomy/approvals');
}

export async function submitAutonomyDecision(approvalId: string, approved: boolean, reason: string): Promise<{ status: string; approval_id: string }> {
  return await http.post<{ status: string; approval_id: string }>('/api/autonomy/approve', {
    approval_id: approvalId,
    approved,
    reason,
  });
}

export async function checkAutonomyAction(action: string, context: Record<string, unknown>): Promise<AutonomyCheckResponse> {
  return await http.post<AutonomyCheckResponse>('/api/autonomy/check', {
    action,
    context,
  });
}

export async function fetchAutonomyPolicies(): Promise<AutonomyPoliciesResponse> {
  return await http.get<AutonomyPoliciesResponse>('/api/autonomy/policies');
}

// Agentic Insights -------------------------------------------------
export interface AgenticStatusResponse {
  status: string;
  active_runs: number;
  pending_approvals: number;
  highest_risk?: Record<string, unknown> | null;
}

export interface AgenticStatisticsResponse {
  total_runs: number;
  successful_runs: number;
  success_rate: number;
  average_risk_score: number;
  autonomous_decisions: number;
  autonomy_rate: number;
  pending_approvals: number;
}

export async function fetchAgenticStatus(): Promise<AgenticStatusResponse> {
  return await http.get<AgenticStatusResponse>('/agent/status');
}

export async function fetchAgenticStatistics(hours = 24): Promise<AgenticStatisticsResponse> {
  return await http.get<AgenticStatisticsResponse>('/agent/statistics', {
    query: { hours },
  });
}

// Subagents -------------------------------------------------
export interface SubagentSpawnResponse {
  success: boolean;
  task_id: string;
  message: string;
}

export async function spawnSubagent(agentType: string, task: string, domain = 'core'): Promise<SubagentSpawnResponse> {
  return await http.post<SubagentSpawnResponse>('/api/subagents/spawn', undefined, {
    query: { agent_type: agentType, task, domain },
  });
}

export interface ActiveSubagentsResponse {
  agents: Record<string, {
    task_id: string;
    agent_type: string;
    task: string;
    domain: string;
    status: string;
    progress: number;
    started_at: string;
    result?: Record<string, unknown> | null;
  }>;
  total: number;
  running: number;
}

export async function fetchActiveSubagents(): Promise<ActiveSubagentsResponse> {
  return await http.get<ActiveSubagentsResponse>('/api/subagents/active');
}

// Chat history -------------------------------------------------
export interface ChatHistoryMessage {
  id: number;
  role: string;
  content: string;
  created_at: string;
}

export async function fetchChatHistory(limit = 20): Promise<ChatHistoryMessage[]> {
  return await http.get<ChatHistoryMessage[]>('/api/memory/history', {
    query: { limit },
  });
}
