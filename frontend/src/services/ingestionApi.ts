/**
 * Ingestion Orchestrator API Client
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface IngestionTask {
  task_id: string;
  task_type: string;
  source: string;
  status: string;
  progress: number;
  started_at?: string;
  completed_at?: string;
  error?: string;
  results: Record<string, any>;
}

export interface IngestionStatus {
  component_id: string;
  component_type: string;
  status: string;
  total_tasks: number;
  active_tasks: number;
  max_concurrent: number;
  modules_loaded: string[];
}

export async function getIngestionStatus(): Promise<IngestionStatus> {
  const response = await axios.get(`${API_BASE}/api/ingestion/status`);
  return response.data;
}

export async function getIngestionTasks(statusFilter?: string): Promise<IngestionTask[]> {
  const response = await axios.get(`${API_BASE}/api/ingestion/tasks`, {
    params: statusFilter ? { status: statusFilter } : {}
  });
  return response.data.tasks;
}

export async function startIngestion(taskType: string, source: string): Promise<{
  success: boolean;
  task: IngestionTask;
}> {
  const response = await axios.post(`${API_BASE}/api/ingestion/start`, null, {
    params: { task_type: taskType, source }
  });
  return response.data;
}

export async function stopIngestion(taskId: string): Promise<{ success: boolean }> {
  const response = await axios.post(`${API_BASE}/api/ingestion/stop/${taskId}`);
  return response.data;
}
