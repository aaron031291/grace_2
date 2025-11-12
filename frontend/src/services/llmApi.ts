import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export interface LLMStatus {
  status: string;
  model: string;
  provider: string;
  total_calls: number;
  total_tokens: number;
  avg_response_time: number;
}

export interface LLMCall {
  id: string;
  timestamp: string;
  prompt: string;
  response: string;
  tokens_used: number;
  response_time_ms: number;
  model: string;
  reasoning_chain?: string[];
}

export interface TokenUsage {
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: number;
  daily_usage: Array<{ date: string; tokens: number }>;
}

export const llmApi = {
  async getStatus(): Promise<LLMStatus> {
    const { data } = await axios.get(`${API_BASE}/api/llm/status`);
    return data;
  },

  async getRecentCalls(limit: number = 20): Promise<LLMCall[]> {
    const { data } = await axios.get(`${API_BASE}/api/llm/calls`, { params: { limit } });
    return data.calls || [];
  },

  async getTokenUsage(): Promise<TokenUsage> {
    const { data } = await axios.get(`${API_BASE}/api/llm/token-usage`);
    return data;
  },

  async testLLM(prompt: string): Promise<{ response: string; reasoning: string[] }> {
    const { data } = await axios.post(`${API_BASE}/api/llm/test`, { prompt });
    return data;
  }
};
