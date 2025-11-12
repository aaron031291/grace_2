/**
 * Intelligence Kernel API Client
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface IntelligenceStatus {
  status: string;
  kernel_type: string;
  is_stub: boolean;
}

export async function getIntelligenceStatus(): Promise<IntelligenceStatus> {
  const response = await axios.get(`${API_BASE}/api/intelligence/status`);
  return response.data;
}
