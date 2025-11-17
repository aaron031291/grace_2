/**
 * Secrets Vault API Service
 * Secure credential storage and retrieval
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export interface Secret {
  id: string;
  name: string;
  type: 'api_key' | 'token' | 'password' | 'certificate';
  tags?: string[];
  domain?: string;
  created_at: string;
  last_used?: string;
  use_count?: number;
  approved_by?: string;
  expires_at?: string;
  metadata?: Record<string, any>;
}

export interface CreateSecretRequest {
  name: string;
  value: string;
  type: 'api_key' | 'token' | 'password' | 'certificate';
  tags?: string[];
  domain?: string;
  expires_at?: string;
  metadata?: Record<string, any>;
}

export interface SecretValue {
  name: string;
  value: string;
  retrieved_at: string;
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token') || 'dev-token';
  const userId = localStorage.getItem('user_id') || 'aaron';
  
  return {
    'Authorization': `Bearer ${token}`,
    'X-User-ID': userId,
    'X-Client': 'grace-console',
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Vault API error');
  }
  return response.json();
}

/**
 * List all secrets (metadata only, no values)
 */
export async function listSecrets(filters?: {
  domain?: string;
  type?: string;
  tags?: string[];
}): Promise<Secret[]> {
  const params = new URLSearchParams();
  if (filters?.domain) params.append('service', filters.domain); // Backend uses 'service' param
  if (filters?.type) params.append('type', filters.type);
  if (filters?.tags) filters.tags.forEach(tag => params.append('tags', tag));

  const response = await fetch(`${API_BASE}/api/vault/secrets?${params}`, {
    headers: getAuthHeaders(),
  }).catch(() => {
    // Gracefully handle 404 or network errors
    console.warn('[Vault API] listSecrets endpoint not available');
    return new Response(JSON.stringify({ secrets: [], count: 0 }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  });

  const data = await handleResponse<{ secrets: Secret[]; count?: number }>(response);
  return data.secrets || [];
}

/**
 * Get secret metadata (no value)
 */
export async function getSecretMetadata(name: string): Promise<Secret> {
  const response = await fetch(`${API_BASE}/api/vault/secrets/${name}/metadata`, {
    headers: getAuthHeaders(),
  });

  return handleResponse<Secret>(response);
}

/**
 * Get secret value (decrypted)
 * This operation is logged for audit
 */
export async function getSecretValue(name: string): Promise<SecretValue> {
  const response = await fetch(`${API_BASE}/api/vault/secrets/${name}`, {
    headers: getAuthHeaders(),
  });

  return handleResponse<SecretValue>(response);
}

/**
 * Create/store a new secret
 */
export async function createSecret(request: CreateSecretRequest): Promise<{
  id: string;
  name: string;
  status: string;
}> {
  const response = await fetch(`${API_BASE}/api/vault/secrets`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  return handleResponse(response);
}

/**
 * Update secret metadata (not value)
 */
export async function updateSecretMetadata(
  name: string,
  updates: {
    tags?: string[];
    domain?: string;
    expires_at?: string;
    metadata?: Record<string, any>;
  }
): Promise<Secret> {
  const response = await fetch(`${API_BASE}/api/vault/secrets/${name}/metadata`, {
    method: 'PATCH',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });

  return handleResponse(response);
}

/**
 * Rotate/update secret value
 */
export async function rotateSecret(
  name: string,
  newValue: string,
  reason?: string
): Promise<{ status: string; rotated_at: string }> {
  const response = await fetch(`${API_BASE}/api/vault/secrets/${name}/rotate`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: newValue, reason }),
  });

  return handleResponse(response);
}

/**
 * Delete secret
 */
export async function deleteSecret(
  name: string,
  reason: string
): Promise<{ status: string; audit_log_id: string }> {
  if (!reason.trim()) {
    throw new Error('Deletion reason is required for audit');
  }

  const response = await fetch(`${API_BASE}/api/vault/secrets/${name}`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reason }),
  });

  return handleResponse(response);
}

/**
 * Get secret access audit log
 */
export async function getSecretAuditLog(
  name: string
): Promise<Array<{
  timestamp: string;
  actor: string;
  action: 'created' | 'accessed' | 'rotated' | 'deleted';
  result: string;
}>> {
  const response = await fetch(`${API_BASE}/api/vault/secrets/${name}/audit`, {
    headers: getAuthHeaders(),
  });

  const data = await handleResponse<{ logs: any[] }>(response);
  return data.logs || [];
}

/**
 * Copy secret to clipboard (with audit logging)
 */
export async function copySecretToClipboard(name: string): Promise<void> {
  const secretData = await getSecretValue(name);
  
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(secretData.value);
  } else {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = secretData.value;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }
}

/**
 * Test secret (verify it works)
 */
export async function testSecret(
  name: string,
  testEndpoint?: string
): Promise<{ valid: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/api/vault/secrets/${name}/test`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ test_endpoint: testEndpoint }),
  });

  return handleResponse(response);
}

/**
 * Get vault statistics
 */
export async function getVaultStats(): Promise<{
  total_secrets: number;
  by_type: Record<string, number>;
  by_domain: Record<string, number>;
  expires_soon: number;
}> {
  const response = await fetch(`${API_BASE}/api/vault/stats`, {
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}
