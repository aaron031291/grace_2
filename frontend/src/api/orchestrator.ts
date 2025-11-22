/**
 * Orchestrator API Client
 *
 * Handles task coordination and multi-agent orchestration
 */

import { API_BASE_URL } from './config';

export interface OrchestratorStatus {
  running: boolean;
  active_agents: number;
  queue_size: number;
  knowledge_gaps: string[];
}

export interface OrchestratorConfig {
  max_agents: number;
}

export class OrchestratorAPI {
  private static baseUrl = `${API_BASE_URL}/orchestrator`;

  static async getStatus(): Promise<OrchestratorStatus> {
    const response = await fetch(`${this.baseUrl}/status`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get orchestrator status');
    }

    return response.json();
  }

  static async getActiveAgents(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/agents`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get active agents');
    }

    return response.json();
  }

  static async getKnowledgeGaps(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/knowledge-gaps`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get knowledge gaps');
    }

    return response.json();
  }

  static async getQueueStatus(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/queue`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get queue status');
    }

    return response.json();
  }

  static async updateConfig(maxAgents: number): Promise<any> {
    const response = await fetch(`${this.baseUrl}/config?max_agents=${maxAgents}`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to update orchestrator config');
    }

    return response.json();
  }

  static async getMetrics(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/metrics`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to get orchestrator metrics');
    }

    return response.json();
  }
}