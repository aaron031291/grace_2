/**
 * Learning System API Client
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LearningStatus {
  status: string;
  component: string;
  error?: string;
}

export async function getLearningStatus(): Promise<LearningStatus> {
  const response = await axios.get(`${API_BASE}/api/learning/status`);
  return response.data;
}
