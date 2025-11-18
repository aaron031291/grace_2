/**
 * Intelligence Kernel API Client
 */

import axios from 'axios';
import { API_BASE_URL } from '../config';

export interface IntelligenceStatus {
  status: string;
  kernel_type: string;
  is_stub: boolean;
}

export async function getIntelligenceStatus(): Promise<IntelligenceStatus> {
  const response = await axios.get(`${API_BASE_URL}/intelligence/status`);
  return response.data;
}
