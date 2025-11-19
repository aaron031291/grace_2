/**
 * World Model & RAG API Service
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

function getAuthHeaders(): Record<string, string> {
  return {
    'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
    'X-User-ID': localStorage.getItem('user_id') || 'aaron',
  };
}

/**
 * Query world model
 */
export async function queryWorldModel(question: string): Promise<{
  answer: string;
  context_used: any[];
  citations: any[];
}> {
  const response = await fetch(`${API_BASE}/world-model/query`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) throw new Error('World model query failed');
  return response.json();
}

/**
 * Ask Grace (world model interface)
 */
export async function askGrace(question: string): Promise<{
  response: string;
  citations?: any[];
  context?: any;
}> {
  const response = await fetch(`${API_BASE}/world-model/ask-grace?question=${encodeURIComponent(question)}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error('Ask Grace failed');
  return response.json();
}

/**
 * RAG query
 */
export async function ragQuery(query: string, context?: string): Promise<{
  answer: string;
  sources: any[];
}> {
  const response = await fetch(`${API_BASE}/api/remote-access/rag/query`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, context }),
  });

  if (!response.ok) throw new Error('RAG query failed');
  return response.json();
}

/**
 * Get available models
 */
export async function getAvailableModels(): Promise<{
  models: Array<{
    name: string;
    size: string;
    available: boolean;
    capabilities: string[];
  }>;
}> {
  const response = await fetch(`${API_BASE}/api/models/available`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error('Failed to get models');
  return response.json();
}
