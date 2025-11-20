/**
 * System Overview API - Comprehensive typed helpers for all dashboard endpoints
 * 
 * Centralizes all API calls used by SystemOverview panel
 */

import { API_BASE_URL } from '../config';

// ==================== Types ====================

export interface HealthSummary {
  status: string;
  trust_score?: number;
  guardian_score?: number;
  health_score?: number;
  uptime_percent?: number;
  data?: {
    trust?: number;
    trust_score?: number;
    guardian_score?: number;
    health?: number;
    health_score?: number;
    uptime_percent?: number;
  };
}

export interface SelfHealStatus {
  status: string;
  total_incidents: number;
  active_incidents: number;
  resolved_today: number;
  success_rate: number;
  average_resolution_time: number;
  mttr?: number;
  mttr_target?: number;
}

export interface LearningStatus {
  status: 'active' | 'paused' | 'disabled';
  google_enabled?: boolean;
  bing_enabled?: boolean;
  total_artifacts: number;
  pending_ingestion?: number;
  knowledge_bases?: number;
  active_sessions?: number;
  last_updated: string;
}

export interface RecentSnapshot {
  snapshot_id: string;
  timestamp: string;
  label: string;
  verified_ok: boolean;
  config_hash?: string;
  git_sha?: string;
  size_mb?: number;
  description?: string;
}

export interface WorldModelMission {
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
}

export interface RemoteHeartbeat {
  active: boolean;
  session_id?: string;
  firefox_agent_running: boolean;
  active_sessions: number;
  last_heartbeat?: string;
  uptime_seconds?: number;
}

// ==================== API Helpers ====================

export const OverviewAPI = {
  /**
   * Get overall system health metrics
   * Used by: Health & Trust tile
   */
  async getHealthSummary(): Promise<HealthSummary> {
    const response = await fetch(`${API_BASE_URL}/api/metrics/summary`);
    if (!response.ok) {
      throw new Error(`Failed to fetch health summary: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get self-healing system status
   * Used by: Self-Healing tile
   */
  async getSelfHealStatus(): Promise<SelfHealStatus> {
    try {
      // Try primary endpoint
      const response = await fetch(`${API_BASE_URL}/api/self-heal/status`);
      if (response.ok) {
        return response.json();
      }
      
      // Fallback to incidents/stats
      const fallbackResponse = await fetch(`${API_BASE_URL}/api/incidents/stats`);
      if (fallbackResponse.ok) {
        const data = await fallbackResponse.json();
        return {
          status: 'active',
          ...data
        };
      }
      
      throw new Error('Self-heal status unavailable');
    } catch (err) {
      // Return default values
      return {
        status: 'unknown',
        total_incidents: 0,
        active_incidents: 0,
        resolved_today: 0,
        success_rate: 0,
        average_resolution_time: 0
      };
    }
  },

  /**
   * Get learning system status
   * Used by: Learning Status tile
   */
  async getLearningStatus(): Promise<LearningStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning/status`);
      if (response.ok) {
        return response.json();
      }
      
      // Return default if endpoint doesn't exist
      return {
        status: 'active',
        total_artifacts: 0,
        last_updated: new Date().toISOString()
      };
    } catch (err) {
      return {
        status: 'disabled',
        total_artifacts: 0,
        last_updated: new Date().toISOString()
      };
    }
  },

  /**
   * Get recent snapshots
   * Used by: Snapshots tile
   */
  async getRecentSnapshots(limit: number = 5): Promise<RecentSnapshot[]> {
    try {
      // Try primary endpoint
      const response = await fetch(`${API_BASE_URL}/api/snapshots/recent?limit=${limit}`);
      if (response.ok) {
        const data = await response.json();
        return data.snapshots || data;
      }
      
      // Fallback to list endpoint
      const fallbackResponse = await fetch(`${API_BASE_URL}/api/snapshots/list`);
      if (fallbackResponse.ok) {
        const data = await fallbackResponse.json();
        return (data.snapshots || []).slice(0, limit);
      }
      
      return [];
    } catch (err) {
      return [];
    }
  },

  /**
   * Get world model missions
   * Used by: Mission Registry tile
   */
  async getWorldModelMissions(limit: number = 20): Promise<WorldModelMission[]> {
    try {
      // Try primary endpoint
      const response = await fetch(`${API_BASE_URL}/api/world-model/missions?limit=${limit}`);
      if (response.ok) {
        const data = await response.json();
        return data.missions || data;
      }
      
      // Fallback to missions/list
      const fallbackResponse = await fetch(`${API_BASE_URL}/api/missions/list?limit=${limit}`);
      if (fallbackResponse.ok) {
        const data = await fallbackResponse.json();
        return data.missions || [];
      }
      
      return [];
    } catch (err) {
      return [];
    }
  },

  /**
   * Get remote access heartbeat
   * Used by: Remote Access tile
   */
  async getRemoteHeartbeat(): Promise<RemoteHeartbeat> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/remote/status`);
      if (response.ok) {
        const data = await response.json();
        return {
          active: data.active || false,
          session_id: data.session_id,
          firefox_agent_running: data.firefox_agent_running || false,
          active_sessions: data.active_sessions || 0,
          last_heartbeat: data.last_heartbeat,
          uptime_seconds: data.uptime_seconds
        };
      }
      
      return {
        active: false,
        firefox_agent_running: false,
        active_sessions: 0
      };
    } catch (err) {
      return {
        active: false,
        firefox_agent_running: false,
        active_sessions: 0
      };
    }
  },

  /**
   * Get complete overview dashboard data (all endpoints in parallel)
   * Used by: SystemOverview component initial load
   */
  async getAllOverviewData(): Promise<{
    health: HealthSummary;
    selfHeal: SelfHealStatus;
    learning: LearningStatus;
    snapshots: RecentSnapshot[];
    missions: WorldModelMission[];
    remote: RemoteHeartbeat;
  }> {
    const [health, selfHeal, learning, snapshots, missions, remote] = await Promise.all([
      this.getHealthSummary(),
      this.getSelfHealStatus(),
      this.getLearningStatus(),
      this.getRecentSnapshots(5),
      this.getWorldModelMissions(20),
      this.getRemoteHeartbeat()
    ]);

    return {
      health,
      selfHeal,
      learning,
      snapshots,
      missions,
      remote
    };
  },

  /**
   * Pause/Resume learning system
   * Used by: Quick controls
   */
  async toggleLearning(action: 'pause' | 'resume'): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/api/learning/${action}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to ${action} learning`);
    }
    
    return response.json();
  },

  /**
   * Toggle specific learning collector
   * Used by: Learning details drawer
   */
  async toggleCollector(collector: 'google' | 'bing'): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/api/learning/toggle/${collector}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to toggle ${collector} collector`);
    }
    
    return response.json();
  }
};
