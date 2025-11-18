/**
 * Learning System API Client
 */

import axios from 'axios';
import { API_BASE_URL } from '../config';

export interface LearningStatus {
  status: string;
  component: string;
  error?: string;
}

export async function getLearningStatus(): Promise<LearningStatus> {
  const response = await axios.get(`${API_BASE_URL}/learning/status`);
  return response.data;
}
