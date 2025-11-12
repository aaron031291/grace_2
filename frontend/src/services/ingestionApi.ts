import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export interface IngestionTask {
  id: string;
  source: string;
  type: 'file' | 'directory' | 'url' | 'database';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  total_items: number;
  processed_items: number;
  started_at: string;
  completed_at?: string;
  error?: string;
}

export interface IngestionStats {
  total_ingested: number;
  active_tasks: number;
  failed_tasks: number;
  total_size_mb: number;
  avg_speed_items_per_sec: number;
}

export interface IngestionHistory {
  id: string;
  source: string;
  type: string;
  items_processed: number;
  duration_seconds: number;
  completed_at: string;
  success: boolean;
}

export const ingestionApi = {
  async getActiveTasks(): Promise<IngestionTask[]> {
    const { data } = await axios.get(`${API_BASE}/api/ingestion/tasks`);
    return data.tasks || [];
  },

  async getStats(): Promise<IngestionStats> {
    const { data } = await axios.get(`${API_BASE}/api/ingestion/stats`);
    return data;
  },

  async getHistory(limit: number = 20): Promise<IngestionHistory[]> {
    const { data } = await axios.get(`${API_BASE}/api/ingestion/history`, { params: { limit } });
    return data.history || [];
  },

  async startIngestion(source: string, type: string): Promise<{ task_id: string }> {
    const { data } = await axios.post(`${API_BASE}/api/ingestion/start`, { source, type });
    return data;
  },

  async stopIngestion(taskId: string): Promise<void> {
    await axios.post(`${API_BASE}/api/ingestion/stop/${taskId}`);
  },

  async retryFailed(taskId: string): Promise<void> {
    await axios.post(`${API_BASE}/api/ingestion/retry/${taskId}`);
  }
};
