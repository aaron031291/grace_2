import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export interface LearningStatus {
  loop_active: boolean;
  total_entries: number;
  patterns_detected: number;
  learning_rate: number;
  last_update: string;
}

export interface LearningEntry {
  id: string;
  timestamp: string;
  event_type: string;
  context: string;
  outcome: string;
  confidence: number;
  applied: boolean;
}

export interface Pattern {
  id: string;
  pattern_type: string;
  description: string;
  frequency: number;
  confidence: number;
  first_seen: string;
  last_seen: string;
  examples: string[];
}

export interface LearningStats {
  total_patterns: number;
  active_patterns: number;
  avg_confidence: number;
  learning_velocity: number;
  entries_per_day: number;
}

export const learningApi = {
  async getStatus(): Promise<LearningStatus> {
    const { data } = await axios.get(`${API_BASE}/api/learning/status`);
    return data;
  },

  async getEntries(limit: number = 20): Promise<LearningEntry[]> {
    const { data } = await axios.get(`${API_BASE}/api/learning/entries`, { params: { limit } });
    return data.entries || [];
  },

  async getPatterns(): Promise<Pattern[]> {
    const { data } = await axios.get(`${API_BASE}/api/learning/patterns`);
    return data.patterns || [];
  },

  async getStats(): Promise<LearningStats> {
    const { data } = await axios.get(`${API_BASE}/api/learning/stats`);
    return data;
  },

  async toggleLoop(active: boolean): Promise<void> {
    await axios.post(`${API_BASE}/api/learning/toggle`, { active });
  }
};
