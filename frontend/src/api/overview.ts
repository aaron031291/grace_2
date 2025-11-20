import { API_BASE_URL } from '../config';

export interface MetricsSummaryResponse {
  success?: boolean;
  data?: {
    trust?: number;
    trust_score?: number;
    confidence?: number;
    pending_approvals?: number;
    active_tasks?: number;
    health?: 'healthy' | 'degraded' | 'offline';
    system_status?: 'healthy' | 'degraded' | 'offline';
  };
  trust_score?: number;
  confidence?: number;
  pending_approvals?: number;
  active_tasks?: number;
  health?: 'healthy' | 'degraded' | 'offline';
  system_status?: 'healthy' | 'degraded' | 'offline';
}

export interface SelfHealingStatus {
  status: string;
  health?: string;
  message?: string;
  active_playbooks?: number;
  incidents?: number;
  last_run?: string;
  capabilities?: string[];
  [key: string]: any;
}

export interface LearningStatus {
  status: string;
  component?: string;
  error?: string;
}

export interface MissionSummary {
  mission_id?: string;
  id?: string;
  title?: string;
  name?: string;
  description?: string;
  status?: string;
  progress?: number;
  priority?: string;
  updated_at?: string;
}

export interface SnapshotSummary {
  id: string;
  snapshot_type: string;
  status: string;
  is_golden: boolean;
  is_validated?: boolean;
  system_health_score?: number;
  created_at?: string;
  triggered_by?: string;
}

export interface RemoteStatus {
  timestamp: string;
  health: string;
  trust_score: number;
  confidence: number;
  active_tasks: number;
  active_missions: number;
  pending_approvals: number;
  learning_jobs: number;
  incidents: number;
  memory_usage_mb: number;
  uptime_seconds: number;
}

type JsonResponse<T> = Promise<T>;

async function fetchJson<T>(url: string): JsonResponse<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const OverviewAPI = {
  getMetricsSummary: () =>
    fetchJson<MetricsSummaryResponse>(`${API_BASE_URL}/metrics/summary`),

  getSelfHealingStatus: () =>
    fetchJson<SelfHealingStatus>(`${API_BASE_URL}/self-healing/status`),

  getLearningStatus: () =>
    fetchJson<LearningStatus>(`${API_BASE_URL}/learning/status`),

  getMissions: () =>
    fetchJson<{ missions?: MissionSummary[] }>(
      `${API_BASE_URL}/world-model/missions`
    ),

  getRecentSnapshots: (limit = 5) =>
    fetchJson<{ snapshots: SnapshotSummary[] }>(
      `${API_BASE_URL}/verification/snapshots?limit=${limit}`
    ),

  getRemoteStatus: () =>
    fetchJson<RemoteStatus>(`${API_BASE_URL}/remote/status`),
};

export type OverviewDataBundle = {
  metrics?: MetricsSummaryResponse;
  selfHealing?: SelfHealingStatus;
  learning?: LearningStatus;
  missions?: MissionSummary[];
  snapshots?: SnapshotSummary[];
  remote?: RemoteStatus;
};
