/**
 * Grace API Client with Full Traceability Support
 * Automatically includes execution_trace and data_provenance
 */

import { http } from './client';
import type { 
  HealthResponse, 
  ExecutionTrace, 
  DataProvenance,
  VerificationAuditResponse
} from './types';

// ============ Health API ============

export async function getHealth(): Promise<HealthResponse> {
  return await http.get<HealthResponse>('/health');
}

// ============ Verification API ============

export async function getVerificationAudit(params: {
  limit?: number;
  actor?: string;
  action_type?: string;
  hours_back?: number;
}): Promise<VerificationAuditResponse> {
  return await http.get<VerificationAuditResponse>('/api/verification/audit', {
    query: params
  });
}

export async function getVerificationStats(hours_back: number = 24) {
  return await http.get('/api/verification/stats', {
    query: { hours_back }
  });
}

export async function getMissionDetail(mission_id: string) {
  return await http.get(`/api/verification/missions/${mission_id}`);
}

// ============ Memory API ============

export async function getMemoryDomains() {
  return await http.get('/api/memory/domains');
}

export async function getMemoryTree(domain?: string, category?: string) {
  return await http.get('/api/memory/tree', {
    query: { domain, category }
  });
}

export async function createMemoryArtifact(data: {
  path: string;
  content: string;
  domain?: string;
  category?: string;
  metadata?: Record<string, any>;
  reason?: string;
}) {
  return await http.post('/api/memory/items', data);
}

// ============ Tasks API ============

export async function getTasks() {
  return await http.get('/api/tasks');
}

export async function createTask(data: {
  title: string;
  description?: string;
  priority?: string;
}) {
  return await http.post('/api/tasks', data);
}

export async function updateTask(task_id: number, data: {
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
}) {
  return await http.patch(`/api/tasks/${task_id}`, data);
}

// ============ Chat API ============

export async function sendChatMessage(message: string, domain?: string) {
  return await http.post('/api/chat', {
    message,
    domain
  });
}

// ============ Knowledge API ============

export async function queryKnowledge(query: string, limit: number = 10, domain?: string) {
  return await http.post('/api/knowledge/query', {
    query,
    limit,
    domain
  });
}

// ============ Plugins API ============

export async function getPlugins() {
  return await http.get('/api/plugins');
}

export async function enablePlugin(plugin_name: string) {
  return await http.post(`/api/plugins/${plugin_name}/enable`);
}

export async function disablePlugin(plugin_name: string) {
  return await http.post(`/api/plugins/${plugin_name}/disable`);
}

// ============ Metrics API ============

export async function getMetricsSummary() {
  return await http.get('/api/metrics/summary');
}

export async function getUserMetrics(username: string) {
  return await http.get(`/api/metrics/user/${username}`);
}

// ============ Governance API ============

export async function getGovernancePolicies() {
  return await http.get('/api/governance/policies');
}

export async function getAuditLogs(limit: number = 100) {
  return await http.get('/api/governance/audit', {
    query: { limit }
  });
}

export async function getPendingApprovals() {
  return await http.get('/api/governance/approvals/pending');
}

// ============ Helper: Extract Execution Info ============

export function extractExecutionInfo(response: any): {
  duration: number;
  components: string[];
  dataSources: string[];
  databaseQueries: number;
  verified: boolean;
} {
  const trace = response.execution_trace as ExecutionTrace | undefined;
  const provenance = response.data_provenance as DataProvenance[] | undefined;
  
  return {
    duration: trace?.total_duration_ms ?? 0,
    components: trace?.steps.map(s => s.component) ?? [],
    dataSources: trace?.data_sources_used ?? [],
    databaseQueries: trace?.database_queries ?? 0,
    verified: provenance?.every(p => p.verified) ?? false
  };
}

// ============ Helper: Check Data Trust ============

export function getDataTrustScore(response: any): number {
  const provenance = response.data_provenance as DataProvenance[] | undefined;
  if (!provenance || provenance.length === 0) return 0;
  
  // Average confidence score
  const avgConfidence = provenance.reduce((sum, p) => sum + p.confidence, 0) / provenance.length;
  
  // Reduce score if any unverified
  const allVerified = provenance.every(p => p.verified);
  
  return allVerified ? avgConfidence : avgConfidence * 0.7;
}
