import { apiUrl, WS_BASE_URL } from './config';
/**
 * Phase 8 API Client: End-to-End Testing & Production Readiness
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || apiUrl('';

export interface Phase8Summary {
  phase: string;
  description: string;
  components: string[];
  status: string;
  endpoints: number;
}

export interface ReadinessCheck {
  id: string;
  name: string;
  category: string;
  status: string;
  checks: Array<{
    name: string;
    status: string;
    message: string;
  }>;
}

export interface ReadinessResult {
  timestamp: string;
  overall_status: string;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  readiness_score: number;
  categories: Record<string, {
    total: number;
    passed: number;
    failed: number;
  }>;
  checks: ReadinessCheck[];
}

export interface SystemHealth {
  timestamp: string;
  status: string;
  components: Record<string, {
    status: string;
    message?: string;
    cpu_percent?: number;
    memory_percent?: number;
    disk_percent?: number;
  }>;
  metrics: {
    uptime_seconds: number;
    total_requests: number;
    error_rate: number;
    avg_response_time_ms: number;
  };
  warnings?: string[];
  unhealthy_components?: string[];
}

export interface IntegrationTest {
  id: string;
  name: string;
  description: string;
  phases: string[];
  critical: boolean;
  status?: string;
  message?: string;
  duration_ms?: number;
}

export interface IntegrationResult {
  timestamp: string;
  overall_status: string;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  skipped_tests: number;
  success_rate: number;
  critical_failures: string[];
  tests: IntegrationTest[];
}

export interface Phase8Status {
  phase: string;
  timestamp: string;
  overall_status: string;
  readiness: {
    status: string;
    score: number;
    total_checks: number;
    passed_checks: number;
  };
  health: {
    status: string;
    cpu_percent: number;
    memory_percent: number;
  };
  integrations: {
    status: string;
    success_rate: number;
    total_tests: number;
    passed_tests: number;
  };
  e2e_tests: {
    status: string;
    total_tests: number;
  };
}

export class Phase8ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getSummary(): Promise<Phase8Summary> {
    const response = await fetch(`${this.baseUrl}/api/phase8/summary`);
    if (!response.ok) throw new Error('Failed to fetch Phase 8 summary');
    return response.json();
  }

  async getReadinessChecks(): Promise<ReadinessResult> {
    const response = await fetch(`${this.baseUrl}/api/phase8/readiness/checks`);
    if (!response.ok) throw new Error('Failed to fetch readiness checks');
    return response.json();
  }

  async getReadinessChecklist(): Promise<ReadinessCheck[]> {
    const response = await fetch(`${this.baseUrl}/api/phase8/readiness/checklist`);
    if (!response.ok) throw new Error('Failed to fetch readiness checklist');
    return response.json();
  }

  async getReadinessSummary(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/phase8/readiness/summary`);
    if (!response.ok) throw new Error('Failed to fetch readiness summary');
    return response.json();
  }

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await fetch(`${this.baseUrl}/api/phase8/health/system`);
    if (!response.ok) throw new Error('Failed to fetch system health');
    return response.json();
  }

  async getHealthHistory(limit: number = 10): Promise<SystemHealth[]> {
    const response = await fetch(`${this.baseUrl}/api/phase8/health/history?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch health history');
    return response.json();
  }

  async getComponentHealth(component: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/phase8/health/component/${component}`);
    if (!response.ok) throw new Error('Failed to fetch component health');
    return response.json();
  }

  async getHealthMetrics(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/phase8/health/metrics`);
    if (!response.ok) throw new Error('Failed to fetch health metrics');
    return response.json();
  }

  async validateAllIntegrations(): Promise<IntegrationResult> {
    const response = await fetch(`${this.baseUrl}/api/phase8/integrations/validate`);
    if (!response.ok) throw new Error('Failed to validate integrations');
    return response.json();
  }

  async getIntegrationMap(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/phase8/integrations/map`);
    if (!response.ok) throw new Error('Failed to fetch integration map');
    return response.json();
  }

  async validateIntegration(integrationId: string): Promise<IntegrationTest> {
    const response = await fetch(`${this.baseUrl}/api/phase8/integrations/${integrationId}`);
    if (!response.ok) throw new Error('Failed to validate integration');
    return response.json();
  }

  async getTestStatus(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/phase8/tests/status`);
    if (!response.ok) throw new Error('Failed to fetch test status');
    return response.json();
  }

  async getTestResults(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/phase8/tests/results`);
    if (!response.ok) throw new Error('Failed to fetch test results');
    return response.json();
  }

  async getStatus(): Promise<Phase8Status> {
    const response = await fetch(`${this.baseUrl}/api/phase8/status`);
    if (!response.ok) throw new Error('Failed to fetch Phase 8 status');
    return response.json();
  }
}

export const phase8Api = new Phase8ApiClient();
