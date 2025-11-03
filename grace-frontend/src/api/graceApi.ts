/**
 * Grace API Client
 * Connects frontend to Grace backend metrics API
 */

const API_BASE = 'http://localhost:8000';

export interface CognitionStatus {
  timestamp: string;
  overall_health: number;
  overall_trust: number;
  overall_confidence: number;
  saas_ready: boolean;
  domains: Record<string, DomainStatus>;
}

export interface DomainStatus {
  domain_id: string;
  health: number;
  trust: number;
  confidence: number;
  kpis: Record<string, number>;
  last_updated: string;
}

export async function getHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error('Backend not responding');
  return response.json();
}

export async function getCognitionStatus(): Promise<CognitionStatus> {
  const response = await fetch(`${API_BASE}/api/status`);
  if (!response.ok) throw new Error('Failed to fetch cognition status');
  return response.json();
}

export async function getMetrics() {
  const response = await fetch(`${API_BASE}/api/metrics`);
  if (!response.ok) throw new Error('Failed to fetch metrics');
  return response.json();
}
