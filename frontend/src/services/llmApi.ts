/**
 * LLM API Client
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LLMStatus {
  status: string;
  model: string;
  is_stub: boolean;
  available: boolean;
}

export async function getLLMStatus(): Promise<LLMStatus> {
  const response = await axios.get(`${API_BASE}/api/llm/status`);
  return response.data;
}
