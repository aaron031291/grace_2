/**
 * Models API Service
 * Get model metadata, performance, and availability
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export interface ModelInfo {
  name: string;
  size: string;
  type: 'coding' | 'reasoning' | 'long-context' | 'vision' | 'general';
  available: boolean;
  loaded: boolean;
  capabilities: string[];
  performance?: {
    speed: number;
    quality: number;
    success_rate: number;
  };
  status?: 'active' | 'loading' | 'not_loaded' | 'error';
}

export interface ModelPerformance {
  model_name: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_response_time_ms: number;
  success_rate: number;
  quality_score: number;
  last_used: string;
}

function getAuthHeaders(): Record<string, string> {
  return {
    'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
  };
}

/**
 * Get all available models
 */
export async function getAvailableModels(): Promise<ModelInfo[]> {
  const response = await fetch(`${API_BASE}/api/models/available`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    console.warn('Failed to get models');
    return [];
  }

  const data = await response.json();
  return data.models || [];
}

/**
 * Get model performance metrics
 */
export async function getModelPerformance(modelName?: string): Promise<ModelPerformance[]> {
  const url = modelName
    ? `${API_BASE}/api/models/performance/${modelName}`
    : `${API_BASE}/api/models/performance`;

  const response = await fetch(url, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    console.warn('Failed to get model performance');
    return [];
  }

  const data = await response.json();
  return Array.isArray(data) ? data : [data];
}

/**
 * Approve model output (feedback)
 */
export async function approveModelOutput(
  modelName: string,
  messageId: string,
  approved: boolean,
  feedback?: string
): Promise<void> {
  await fetch(`${API_BASE}/api/models/approve`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model_name: modelName,
      message_id: messageId,
      approved,
      feedback,
    }),
  });
}

/**
 * Get recommended model for task type
 */
export async function getRecommendedModel(taskType: string): Promise<string> {
  const response = await fetch(`${API_BASE}/api/models/recommend?task_type=${taskType}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    return 'auto'; // Fallback to auto-selection
  }

  const data = await response.json();
  return data.recommended_model || 'auto';
}
