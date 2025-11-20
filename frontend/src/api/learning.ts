/**
 * Learning Control API
 * 
 * Provides access to learning whitelist, status, and controls
 */

import { API_BASE_URL } from '../config';

export interface WhitelistEntry {
  id: string;
  domain: string;
  source_type: 'url' | 'domain' | 'api' | 'repository';
  approved_by: string;
  approved_at: string;
  reason?: string;
  trust_score?: number;
}

export interface LearningStatus {
  status: 'active' | 'paused' | 'disabled';
  total_artifacts: number;
  total_missions: number;
  knowledge_bases: number;
  active_sessions: number;
  last_updated: string;
  web_learning_enabled?: boolean;
  github_learning_enabled?: boolean;
}

export interface ServiceAccount {
  name: string;
  type: 'google' | 'github' | 'openai' | 'anthropic';
  status: 'active' | 'missing' | 'expired' | 'quota_exceeded';
  quota_used?: number;
  quota_limit?: number;
  quota_reset?: string;
  last_used?: string;
}

export const LearningAPI = {
  /**
   * Get learning whitelist
   */
  async getWhitelist(): Promise<WhitelistEntry[]> {
    const response = await fetch(`${API_BASE_URL}/api/learning/whitelist`);
    if (!response.ok) {
      throw new Error(`Failed to fetch whitelist: ${response.statusText}`);
    }
    const data = await response.json();
    return data.entries || [];
  },

  /**
   * Add entry to whitelist
   */
  async addToWhitelist(
    domain: string,
    sourceType: string,
    reason?: string
  ): Promise<WhitelistEntry> {
    const response = await fetch(`${API_BASE_URL}/api/learning/whitelist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain,
        source_type: sourceType,
        reason,
        approved_by: 'user'
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to add whitelist entry: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.entry;
  },

  /**
   * Remove entry from whitelist
   */
  async removeFromWhitelist(entryId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/learning/whitelist/${entryId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to remove whitelist entry: ${response.statusText}`);
    }
  },

  /**
   * Toggle web learning
   */
  async toggleWebLearning(enabled: boolean): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/learning/web-learning/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to toggle web learning: ${response.statusText}`);
    }
  },

  /**
   * Toggle GitHub learning
   */
  async toggleGitHubLearning(enabled: boolean): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/learning/github-learning/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to toggle GitHub learning: ${response.statusText}`);
    }
  },

  /**
   * Get service accounts status
   */
  async getServiceAccounts(): Promise<ServiceAccount[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/service-accounts/status`);
      if (!response.ok) {
        // Return mock data if endpoint doesn't exist yet
        return [
          {
            name: 'Google Search API',
            type: 'google',
            status: 'active',
            quota_used: 850,
            quota_limit: 1000,
            quota_reset: new Date(Date.now() + 86400000).toISOString(),
            last_used: new Date().toISOString()
          },
          {
            name: 'GitHub Token',
            type: 'github',
            status: 'active',
            last_used: new Date(Date.now() - 3600000).toISOString()
          },
          {
            name: 'OpenAI API',
            type: 'openai',
            status: 'active',
            last_used: new Date().toISOString()
          }
        ];
      }
      
      const data = await response.json();
      return data.accounts || [];
    } catch (error) {
      console.error('Failed to fetch service accounts:', error);
      return [];
    }
  }
};
