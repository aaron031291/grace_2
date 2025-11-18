/**
 * Learning System API Client
 */

import axios from 'axios';
import { apiUrl, WS_BASE_URL } from '../config';

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

export interface LearningStatus {
  status: string;
  component: string;
  error?: string;
}

export async function getLearningStatus(): Promise<LearningStatus> {
  const response = await axios.get(`${API_BASE}/api/learning/status`);
  return response.data;
}
