import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export interface IntelligenceStatus {
  kernel_active: boolean;
  reasoning_quality: number;
  total_insights: number;
  avg_confidence: number;
  active_analyses: number;
}

export interface Insight {
  id: string;
  timestamp: string;
  category: string;
  content: string;
  confidence: number;
  impact_score: number;
  source: string;
}

export interface ReasoningMetrics {
  avg_depth: number;
  avg_quality: number;
  total_chains: number;
  successful_chains: number;
  avg_confidence: number;
}

export interface Analysis {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  result?: any;
  started_at: string;
  completed_at?: string;
}

export const intelligenceApi = {
  async getStatus(): Promise<IntelligenceStatus> {
    const { data } = await axios.get(`${API_BASE}/api/intelligence/status`);
    return data;
  },

  async getInsights(limit: number = 20): Promise<Insight[]> {
    const { data } = await axios.get(`${API_BASE}/api/intelligence/insights`, { params: { limit } });
    return data.insights || [];
  },

  async getReasoningMetrics(): Promise<ReasoningMetrics> {
    const { data } = await axios.get(`${API_BASE}/api/intelligence/reasoning-metrics`);
    return data;
  },

  async getActiveAnalyses(): Promise<Analysis[]> {
    const { data } = await axios.get(`${API_BASE}/api/intelligence/analyses`);
    return data.analyses || [];
  },

  async triggerAnalysis(type: string): Promise<{ id: string }> {
    const { data } = await axios.post(`${API_BASE}/api/intelligence/analyze`, { type });
    return data;
  }
};
