/**
 * Background Tasks API Client
 * 
 * Manages background tasks and job queue
 */

import { API_BASE_URL } from '../config';

export interface BackgroundTask {
  task_id: string;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress?: number;
  result?: any;
  error?: string;
}

export class TasksAPI {
  private static baseUrl = API_BASE_URL || '';

  static async getTasks(): Promise<BackgroundTask[]> {
    const response = await fetch(`${this.baseUrl}/api/control/tasks`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to fetch tasks');
    }

    const data = await response.json();
    return data.pending_tasks || [];
  }

  static async getTaskStatus(taskId: string): Promise<BackgroundTask> {
    const response = await fetch(`${this.baseUrl}/api/world-model/background-tasks/${taskId}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to fetch task status');
    }

    return response.json();
  }

  static async cancelTask(taskId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/control/tasks/${taskId}/cancel`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to cancel task');
    }

    return response.json();
  }
}
