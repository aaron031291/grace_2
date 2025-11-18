/**
 * LLM API Client
 */

import axios from 'axios';
import { API_BASE_URL } from '../config';

export interface LLMStatus {
  status: string;
  model: string;
  is_stub: boolean;
  available: boolean;
}

export async function getLLMStatus(): Promise<LLMStatus> {
  const response = await axios.get(`${API_BASE_URL}/llm/status`);
  return response.data;
}
