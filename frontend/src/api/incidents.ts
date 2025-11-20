/**
 * Incidents API - Self-Healing System
 * 
 * Provides access to self-healing incidents, stats, and playbooks
 */

import { API_BASE_URL } from '../config';

export interface Incident {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'healing' | 'resolved' | 'failed';
  component: string;
  detected_at: string;
  resolved_at?: string;
  playbook_applied?: string;
  resolution_time?: number;
  error_message?: string;
}

export interface SelfHealingStats {
  total_incidents: number;
  active_incidents: number;
  resolved_today: number;
  average_resolution_time: number;
  success_rate: number;
  mttr?: number;
  mttr_target?: number;
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

export interface IncidentsResponse {
  incidents: Incident[];
  count: number;
  total: number;
}

export interface PlaybooksResponse {
  playbooks: Playbook[];
  count: number;
}

export const IncidentsAPI = {
  /**
   * Get self-healing system statistics
   */
  async getStats(): Promise<SelfHealingStats> {
    const response = await fetch(`${API_BASE_URL}/self-healing/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch self-healing stats: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get self-healing incidents
   */
  async getIncidents(limit: number = 20): Promise<IncidentsResponse> {
    const response = await fetch(`${API_BASE_URL}/self-healing/incidents?limit=${limit}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch incidents: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get available self-healing playbooks
   */
  async getPlaybooks(): Promise<PlaybooksResponse> {
    const response = await fetch(`${API_BASE_URL}/self-healing/playbooks`);
    if (!response.ok) {
      throw new Error(`Failed to fetch playbooks: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get active (pending/healing) incidents
   */
  async getActiveIncidents(): Promise<Incident[]> {
    const data = await this.getIncidents(100);
    return data.incidents.filter(
      (inc) => inc.status === 'pending' || inc.status === 'healing'
    );
  },

  /**
   * Get resolved incidents
   */
  async getResolvedIncidents(limit: number = 20): Promise<Incident[]> {
    const data = await this.getIncidents(limit);
    return data.incidents.filter((inc) => inc.status === 'resolved');
  },

  /**
   * Calculate MTTR (Mean Time To Recovery) from incidents
   */
  calculateMTTR(incidents: Incident[]): number {
    const resolved = incidents.filter(
      (inc) => inc.status === 'resolved' && inc.detected_at && inc.resolved_at
    );
    
    if (resolved.length === 0) return 0;

    const totalTime = resolved.reduce((sum, inc) => {
      const detected = new Date(inc.detected_at).getTime();
      const resolved = new Date(inc.resolved_at!).getTime();
      return sum + (resolved - detected) / 1000; // in seconds
    }, 0);

    return totalTime / resolved.length;
  }
};
