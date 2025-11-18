import { apiUrl, WS_BASE_URL } from './config';
/**
 * Comprehensive API Client
 * Type-safe API helpers for all panels
 */

// DEPRECATED: Use api/factory.ts instead for the new clean architecture
// This file maintained for backwards compatibility
const API_BASE = apiUrl('/api';

// ===== TYPES =====

export interface SelfHealingStats {
  total_incidents: number;
  active_incidents: number;
  resolved_today: number;
  average_resolution_time: number;
  success_rate: number;
}

export interface Incident {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'detected' | 'analyzing' | 'healing' | 'resolved' | 'failed';
  component: string;
  detected_at: string;
  resolved_at?: string;
  playbook_applied?: string;
}

export interface Playbook {
  id: string;
  name: string;
  description: string;
  trigger_conditions: string[];
  actions: number;
  success_rate: number;
  avg_execution_time: number;
}

export interface HealingAction {
  timestamp: string;
  incident_id: string;
  action: string;
  status: 'running' | 'completed' | 'failed';
  result?: string;
}

export interface ImmutableLog {
  seq: number;
  timestamp: string;
  action_type: string;
  target_path: string;
  actor: string;
  details: any;
  hash: string;
}

export interface LogTailEntry {
  timestamp: string;
  action_type: string;
  target_path: string;
  message: string;
}

export interface MemoryStats {
  total_artifacts: number;
  total_domains: number;
  total_size_bytes: number;
  recent_updates: number;
  active_queries: number;
  cache_hit_rate: number;
}

export interface MemoryActivity {
  id: number;
  timestamp: string;
  type: 'store' | 'retrieve' | 'update' | 'query';
  domain: string;
  artifact_path: string;
  status: string;
  duration_ms: number;
}

export interface TrustOverview {
  total_sources: number;
  trusted_sources: number;
  untrusted_sources: number;
  pending_review: number;
  average_trust_score: number;
  verification_rate: number;
  last_updated: string;
}

export interface TrustSource {
  id: string;
  name: string;
  url: string;
  trust_score: number;
  status: 'trusted' | 'untrusted' | 'pending';
  last_verified: string;
  verification_count: number;
}

export interface Alert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  source: string;
  acknowledged: boolean;
}

export interface KnowledgeStats {
  total_documents: number;
  total_chunks: number;
  total_embeddings: number;
  books_ingested: number;
  queries_today: number;
  avg_retrieval_time_ms: number;
  storage_size_mb: number;
}

export interface KnowledgeQuery {
  id: number;
  query: string;
  timestamp: string;
  results_count: number;
  retrieval_time_ms: number;
  relevance_score: number;
}

export interface SystemHealth {
  status: string;
  uptime_seconds: number;
  components: Record<string, any>;
  metrics: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
    network_requests_per_sec: number;
  };
}

export interface ComprehensiveMetrics {
  self_healing: {
    total_runs: number;
    average_success_rate: number;
    mttr_minutes: number;
    average_execution_time_ms: number;
  };
  ingestion: {
    total_ingested: number;
    chunks_processed: number;
    average_chunk_time_ms: number;
    success_rate: number;
  };
  verification: {
    total_verifications: number;
    passed: number;
    failed: number;
    pass_rate: number;
  };
  trust_levels: {
    high_trust: number;
    medium_trust: number;
    low_trust: number;
    average_score: number;
  };
  timestamp: string;
}

// ===== HELPER FUNCTION =====

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  const contentType = response.headers.get('content-type');
  if (!contentType?.includes('application/json')) {
    throw new Error('Response is not JSON');
  }

  return response.json();
}

// ===== SELF-HEALING API =====

export async function getSelfHealingStats(): Promise<SelfHealingStats> {
  return fetchJSON<SelfHealingStats>('/self-healing/stats');
}

export async function getSelfHealingIncidents(limit = 20): Promise<{ incidents: Incident[]; count: number; total: number }> {
  return fetchJSON(`/self-healing/incidents?limit=${limit}`);
}

export async function getSelfHealingPlaybooks(): Promise<{ playbooks: Playbook[]; count: number }> {
  return fetchJSON('/self-healing/playbooks');
}

export async function getRecentHealingActions(limit = 15): Promise<{ actions: HealingAction[]; count: number }> {
  return fetchJSON(`/self-healing/actions/recent?limit=${limit}`);
}

export async function enableSelfHealing(): Promise<{ status: string; message: string }> {
  return fetchJSON('/self-healing/enable', { method: 'POST' });
}

export async function disableSelfHealing(): Promise<{ status: string; message: string }> {
  return fetchJSON('/self-healing/disable', { method: 'POST' });
}

export async function triggerPlaybook(playbookId: string): Promise<{ status: string; playbook_id: string; execution_id: string; message: string }> {
  return fetchJSON(`/self-healing/playbooks/${playbookId}/trigger`, { method: 'POST' });
}

// ===== LIBRARIAN LOG API =====

export async function getImmutableLogs(limit = 100): Promise<{ logs: ImmutableLog[]; count: number; integrity_verified: boolean }> {
  return fetchJSON(`/librarian/logs/immutable?limit=${limit}`);
}

export async function getLogTail(lines = 50): Promise<{ logs: LogTailEntry[]; count: number }> {
  return fetchJSON(`/librarian/logs/tail?lines=${lines}`);
}

// ===== MEMORY API =====

export async function getMemoryStats(): Promise<MemoryStats> {
  return fetchJSON('/memory/stats');
}

export async function getMemoryRecentActivity(limit = 20): Promise<{ activities: MemoryActivity[]; count: number }> {
  return fetchJSON(`/memory/recent-activity?limit=${limit}`);
}

// ===== TRUST API =====

export async function getTrustOverview(): Promise<TrustOverview> {
  return fetchJSON('/trust/overview');
}

export async function getTrustSources(): Promise<{ sources: TrustSource[]; count: number }> {
  return fetchJSON('/trust/sources');
}

// ===== ALERTS API =====

export async function getActiveAlerts(): Promise<{ alerts: Alert[]; count: number; unacknowledged: number }> {
  return fetchJSON('/alerts/active');
}

// ===== KNOWLEDGE API =====

export async function getKnowledgeStats(): Promise<KnowledgeStats> {
  return fetchJSON('/knowledge/stats');
}

export async function getRecentQueries(limit = 10): Promise<{ queries: KnowledgeQuery[]; count: number }> {
  return fetchJSON(`/knowledge/recent-queries?limit=${limit}`);
}

// ===== SYSTEM API =====

export async function getSystemHealth(): Promise<SystemHealth> {
  return fetchJSON('/system/health');
}

export async function getComprehensiveMetrics(): Promise<ComprehensiveMetrics> {
  return fetchJSON('/metrics/comprehensive');
}

// Export all as a single API object
export const api = {
  selfHealing: {
    getStats: getSelfHealingStats,
    getIncidents: getSelfHealingIncidents,
    getPlaybooks: getSelfHealingPlaybooks,
    getRecentActions: getRecentHealingActions,
    enable: enableSelfHealing,
    disable: disableSelfHealing,
    triggerPlaybook,
  },
  logs: {
    getImmutable: getImmutableLogs,
    getTail: getLogTail,
  },
  memory: {
    getStats: getMemoryStats,
    getRecentActivity: getMemoryRecentActivity,
  },
  trust: {
    getOverview: getTrustOverview,
    getSources: getTrustSources,
  },
  alerts: {
    getActive: getActiveAlerts,
  },
  knowledge: {
    getStats: getKnowledgeStats,
    getRecentQueries,
  },
  system: {
    getHealth: getSystemHealth,
    getMetrics: getComprehensiveMetrics,
  },
};

export default api;
