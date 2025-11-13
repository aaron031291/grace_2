/**
 * Factory Pattern API Client
 * Clean, type-safe API helpers for the new modular backend
 * No circular imports - each domain is independent
 */

const API_BASE = 'http://localhost:8000';

// ===== Helper Function =====

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// ===== SYSTEM API =====

export const system = {
  async getHealth() {
    return fetchJSON('/system/health');
  },
  
  async getMetrics() {
    return fetchJSON('/system/metrics');
  },
};

// ===== SELF-HEALING API =====

export const selfHealing = {
  async getStats() {
    return fetchJSON('/self-healing/stats');
  },
  
  async getIncidents(limit = 20) {
    return fetchJSON(`/self-healing/incidents?limit=${limit}`);
  },
  
  async getPlaybooks() {
    return fetchJSON('/self-healing/playbooks');
  },
  
  async getRecentActions(limit = 15) {
    return fetchJSON(`/self-healing/actions/recent?limit=${limit}`);
  },
  
  async enable() {
    return fetchJSON('/self-healing/enable', { method: 'POST' });
  },
  
  async disable() {
    return fetchJSON('/self-healing/disable', { method: 'POST' });
  },
  
  async triggerPlaybook(playbookId: string) {
    return fetchJSON(`/self-healing/playbooks/${playbookId}/trigger`, { method: 'POST' });
  },
};

// ===== LIBRARIAN API =====

export const librarian = {
  async getStatus() {
    return fetchJSON('/librarian/status');
  },
  
  async getSchemaProposals() {
    return fetchJSON('/librarian/schema-proposals');
  },
  
  async approveSchema(proposalId: number) {
    return fetchJSON(`/librarian/schema-proposals/${proposalId}/approve`, { method: 'POST' });
  },
  
  async rejectSchema(proposalId: number) {
    return fetchJSON(`/librarian/schema-proposals/${proposalId}/reject`, { method: 'POST' });
  },
  
  async getFileOperations(limit = 20) {
    return fetchJSON(`/librarian/file-operations?limit=${limit}`);
  },
  
  async getOrganizationSuggestions() {
    return fetchJSON('/librarian/organization-suggestions');
  },
  
  async getActiveAgents() {
    return fetchJSON('/librarian/agents');
  },
  
  async getImmutableLogs(limit = 100) {
    return fetchJSON(`/librarian/logs/immutable?limit=${limit}`);
  },
  
  async getLogTail(lines = 50) {
    return fetchJSON(`/librarian/logs/tail?lines=${lines}`);
  },
};

// ===== MEMORY API =====

export const memory = {
  async getStats() {
    return fetchJSON('/memory/stats');
  },
  
  async listDomains() {
    return fetchJSON('/memory/domains');
  },
  
  async getRecentActivity(limit = 20) {
    return fetchJSON(`/memory/recent-activity?limit=${limit}`);
  },
  
  async search(query: string, domain?: string, limit = 10) {
    const params = new URLSearchParams({ query, limit: limit.toString() });
    if (domain) params.append('domain', domain);
    return fetchJSON(`/memory/search?${params}`);
  },
  
  async getArtifact(artifactId: number) {
    return fetchJSON(`/memory/artifacts/${artifactId}`);
  },
  
  async createArtifact(artifact: any) {
    return fetchJSON('/memory/artifacts', {
      method: 'POST',
      body: JSON.stringify(artifact),
    });
  },
  
  async deleteArtifact(artifactId: number) {
    return fetchJSON(`/memory/artifacts/${artifactId}`, { method: 'DELETE' });
  },
};

// ===== INGESTION API =====

export const ingestion = {
  async getStatus() {
    return fetchJSON('/ingestion/status');
  },
  
  async listJobs(status?: string, limit = 20) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (status) params.append('status', status);
    return fetchJSON(`/ingestion/jobs?${params}`);
  },
  
  async getJob(jobId: number) {
    return fetchJSON(`/ingestion/jobs/${jobId}`);
  },
  
  async createJob(request: any) {
    return fetchJSON('/ingestion/jobs', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },
  
  async cancelJob(jobId: number) {
    return fetchJSON(`/ingestion/jobs/${jobId}/cancel`, { method: 'POST' });
  },
  
  async retryJob(jobId: number) {
    return fetchJSON(`/ingestion/jobs/${jobId}/retry`, { method: 'POST' });
  },
  
  async getMetrics() {
    return fetchJSON('/ingestion/metrics');
  },
};

// ===== TRUSTED SOURCES API =====

export const trustedSources = {
  async list() {
    return fetchJSON('/trusted-sources/');
  },
  
  async get(sourceId: number) {
    return fetchJSON(`/trusted-sources/${sourceId}`);
  },
  
  async create(source: any) {
    return fetchJSON('/trusted-sources/', {
      method: 'POST',
      body: JSON.stringify(source),
    });
  },
  
  async update(sourceId: number, source: any) {
    return fetchJSON(`/trusted-sources/${sourceId}`, {
      method: 'PUT',
      body: JSON.stringify(source),
    });
  },
  
  async delete(sourceId: number) {
    return fetchJSON(`/trusted-sources/${sourceId}`, { method: 'DELETE' });
  },
};

// ===== Unified API Object =====

export const api = {
  system,
  selfHealing,
  librarian,
  memory,
  ingestion,
  trustedSources,
};

export default api;
