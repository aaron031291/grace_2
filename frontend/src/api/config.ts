/**
 * Centralized API Configuration
 * 
 * Uses Vite proxy in development, direct URL in production
 */

const isDevelopment = import.meta.env.DEV;

// Base URL without /api prefix for direct backend calls
const BASE_URL = isDevelopment
  ? ''  // Proxied by Vite to backend
  : import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const API_BASE_URL = `${BASE_URL}/api`;

export const API_ENDPOINTS = {
  // Chat API
  chat: `${API_BASE_URL}/chat`,
  chatApprove: `${API_BASE_URL}/chat/approve`,
  chatHistory: (sessionId: string) => `${API_BASE_URL}/chat/history/${sessionId}`,
  chatSessions: `${API_BASE_URL}/chat/sessions`,
  
  // Metrics API
  metricsHealth: `${API_BASE_URL}/metrics/health`,
  metricsSummary: `${API_BASE_URL}/metrics/summary`,
  
  // Governance API
  governancePending: `${API_BASE_URL}/governance/pending`,
  governanceApprove: `${API_BASE_URL}/governance/approve`,
  governanceReject: `${API_BASE_URL}/governance/reject`,
  governanceHistory: `${API_BASE_URL}/governance/history`,
  governanceStats: `${API_BASE_URL}/governance/stats`,
  
  // World Model API
  worldModelQuery: `${API_BASE_URL}/world-model/query`,
  worldModelArtifacts: `${API_BASE_URL}/world-model/artifacts`,
};

export default API_BASE_URL;
