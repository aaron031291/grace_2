/**
 * Chaos Engineering API Client
 * 
 * Provides access to chaos testing campaigns with governance controls
 */

import { API_BASE_URL } from '../config';

export interface ChaosCampaign {
  campaign_id: string;
  name: string;
  environment: 'staging' | 'production' | 'dev';
  status: 'pending_approval' | 'approved' | 'running' | 'halted' | 'completed' | 'rejected';
  created_by: string;
  approved_by?: string;
  started_at?: string;
  completed_at?: string;
  halted_at?: string;
  halt_reason?: string;
  targets: string[];
  failure_types: string[];
  duration_minutes: number;
  governance_required: boolean;
  trust_score_before?: number;
  trust_score_after?: number;
  kpis: {
    mttr_seconds?: number;
    recovery_success_rate?: number;
    incidents_triggered?: number;
    auto_recoveries?: number;
  };
}

export interface ChaosConfig {
  chaos_enabled: boolean;
  allowed_environments: string[];
  governance_required: boolean;
  guardian_halt_enabled: boolean;
  min_trust_score: number;
  max_blast_radius: number;
}

export interface ChaosStatus {
  active_campaigns: number;
  total_campaigns: number;
  governance_pending: number;
  config: ChaosConfig;
  last_run?: string;
  guardian_override_active: boolean;
}

export const ChaosAPI = {
  /**
   * Get chaos engineering status
   */
  async getStatus(): Promise<ChaosStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/chaos/status`);
      if (!response.ok) {
        // Return default status if endpoint doesn't exist
        return {
          active_campaigns: 0,
          total_campaigns: 0,
          governance_pending: 0,
          config: {
            chaos_enabled: false,
            allowed_environments: ['staging'],
            governance_required: true,
            guardian_halt_enabled: true,
            min_trust_score: 0.8,
            max_blast_radius: 20
          },
          guardian_override_active: false
        };
      }
      return response.json();
    } catch (error) {
      console.error('Failed to fetch chaos status:', error);
      throw error;
    }
  },

  /**
   * Get active chaos campaigns
   */
  async getCampaigns(): Promise<ChaosCampaign[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/chaos/campaigns`);
      if (!response.ok) {
        return [];
      }
      const data = await response.json();
      return data.campaigns || [];
    } catch (error) {
      console.error('Failed to fetch chaos campaigns:', error);
      return [];
    }
  },

  /**
   * Toggle chaos testing
   */
  async toggleChaos(enabled: boolean): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chaos/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to toggle chaos: ${response.statusText}`);
    }
  },

  /**
   * Create chaos campaign (requires governance approval)
   */
  async createCampaign(campaign: {
    name: string;
    environment: string;
    targets: string[];
    failure_types: string[];
    duration_minutes: number;
  }): Promise<ChaosCampaign> {
    const response = await fetch(`${API_BASE_URL}/chaos/campaigns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(campaign)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create chaos campaign: ${response.statusText}`);
    }
    
    return response.json();
  },

  /**
   * Approve chaos campaign (governance)
   */
  async approveCampaign(campaignId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chaos/campaigns/${campaignId}/approve`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to approve campaign: ${response.statusText}`);
    }
  },

  /**
   * Halt chaos campaign (Guardian override)
   */
  async haltCampaign(campaignId: string, reason?: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chaos/campaigns/${campaignId}/halt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason: reason || 'Guardian halt' })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to halt campaign: ${response.statusText}`);
    }
  },

  /**
   * Run without governance (Guardian override)
   */
  async runWithoutGovernance(campaignId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chaos/campaigns/${campaignId}/override-start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        guardian_override: true,
        track_kpis: true 
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to override start campaign: ${response.statusText}`);
    }
  },

  /**
   * Update chaos configuration
   */
  async updateConfig(config: Partial<ChaosConfig>): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chaos/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update chaos config: ${response.statusText}`);
    }
  }
};
