/**
 * Mission Control API Client
 * 
 * Provides access to mission management and tracking
 */

import { API_BASE_URL } from '../config';

export interface Mission {
  mission_id: string;
  subsystem_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'awaiting_validation' | 'observing' | 'resolved' | 'escalated' | 'failed';
  detected_by: string;
  assigned_to: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  symptoms_count: number;
  remediation_events_count: number;
  description?: string;
  owner?: string;
}

export interface MissionDetail extends Mission {
  symptoms: Array<{
    description: string;
    metric_id?: string;
    observed_value?: number;
    threshold?: number;
    log_snippet?: string;
    detected_at: string;
  }>;
  remediation_history: Array<{
    action: string;
    timestamp: string;
    result: string;
    actor: string;
  }>;
  evidence?: {
    logs: Array<any>;
    test_results: Array<any>;
    metrics_snapshot: Array<any>;
  };
  workspace?: {
    repo_path: string;
    working_branch: string;
  };
  context?: {
    git_sha: string;
    config_hash: string;
    env: string;
    branch?: string;
    version?: string;
  };
}

export interface MissionsResponse {
  total: number;
  missions: Mission[];
}

export interface MissionControlStatus {
  grace_version: string;
  environment: string;
  git_sha: string;
  git_branch: string;
  config_hash: string;
  active_missions: number;
  total_missions: number;
  subsystems: Array<{
    subsystem_id: string;
    status: 'healthy' | 'degraded' | 'critical';
    last_check: string;
  }>;
}

export const MissionControlAPI = {
  /**
   * Get overall mission control status
   */
  async getStatus(): Promise<MissionControlStatus> {
    const response = await fetch(`${API_BASE_URL}/api/mission-control/status`);
    if (!response.ok) {
      throw new Error(`Failed to fetch mission control status: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * List all missions with optional filters
   */
  async listMissions(params?: {
    status?: string;
    subsystem_id?: string;
    severity?: string;
    limit?: number;
  }): Promise<MissionsResponse> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.subsystem_id) queryParams.append('subsystem_id', params.subsystem_id);
    if (params?.severity) queryParams.append('severity', params.severity);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const url = `${API_BASE_URL}/api/mission-control/missions${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch missions: ${response.statusText}`);
    }
    
    return response.json();
  },

  /**
   * Get detailed information about a specific mission
   */
  async getMission(missionId: string): Promise<MissionDetail> {
    const response = await fetch(`${API_BASE_URL}/api/mission-control/missions/${missionId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch mission ${missionId}: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get active missions
   */
  async getActiveMissions(limit: number = 50): Promise<Mission[]> {
    const data = await this.listMissions({ limit });
    return data.missions.filter(
      (m) => m.status === 'open' || m.status === 'in_progress'
    );
  },

  /**
   * Get resolved missions
   */
  async getResolvedMissions(limit: number = 50): Promise<Mission[]> {
    const data = await this.listMissions({ status: 'resolved', limit });
    return data.missions;
  },

  /**
   * Get missions by severity
   */
  async getMissionsBySeverity(severity: 'critical' | 'high' | 'medium' | 'low'): Promise<Mission[]> {
    const data = await this.listMissions({ severity });
    return data.missions;
  },

  /**
   * Get subsystem health
   */
  async getSubsystemHealth(): Promise<{
    subsystems: Array<any>;
    total: number;
    healthy: number;
    degraded: number;
    critical: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/mission-control/subsystems`);
    if (!response.ok) {
      throw new Error(`Failed to fetch subsystem health: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Execute a mission
   */
  async executeMission(missionId: string, missionType: 'coding' | 'healing'): Promise<{
    success: boolean;
    mission_id: string;
    status: string;
    message: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/mission-control/missions/${missionId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mission_type: missionType })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to execute mission: ${response.statusText}`);
    }
    
    return response.json();
  }
};
