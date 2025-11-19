/**
 * Logs API Service
 * Handles fetching and streaming logs from backend
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export interface LogEntry {
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  domain: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface LogsResponse {
  logs: LogEntry[];
  total: number;
  limit: number;
}

export interface LogFilters {
  limit?: number;
  level?: string;
  domain?: string;
  search?: string;
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token') || 'dev-token';
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

/**
 * Fetch recent logs with optional filtering
 */
export async function fetchRecentLogs(filters: LogFilters = {}): Promise<LogsResponse> {
  try {
    const params = new URLSearchParams();
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.level) params.append('level', filters.level);
    if (filters.domain) params.append('domain', filters.domain);
    if (filters.search) params.append('search', filters.search);

    const response = await fetch(`${API_BASE}/api/logs/recent?${params}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      // Gracefully handle endpoint not found
      if (response.status === 404) {
        console.warn('[Logs API] /api/logs/recent endpoint not available (404)');
        return { logs: [], total: 0, limit: filters.limit || 100 };
      }
      throw new Error(`Logs API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('[Logs API] Error fetching recent logs:', error);
    return { logs: [], total: 0, limit: filters.limit || 100 };
  }
}

/**
 * Fetch governance-specific logs
 */
export async function fetchGovernanceLogs(filters: LogFilters = {}): Promise<LogsResponse> {
  try {
    const params = new URLSearchParams();
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.level) params.append('level', filters.level);
    if (filters.search) params.append('search', filters.search);

    const response = await fetch(`${API_BASE}/api/logs/governance?${params}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      // Gracefully handle endpoint not found
      if (response.status === 404) {
        console.warn('[Logs API] /api/logs/governance endpoint not available (404)');
        return { logs: [], total: 0, limit: filters.limit || 100 };
      }
      throw new Error(`Logs API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('[Logs API] Error fetching governance logs:', error);
    return { logs: [], total: 0, limit: filters.limit || 100 };
  }
}

/**
 * Get available log domains
 */
export async function fetchLogDomains(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE}/api/logs/domains`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    return data.domains || [];
  } catch (error) {
    console.error('[Logs API] Error fetching log domains:', error);
    return [];
  }
}

/**
 * Get available log levels
 */
export async function fetchLogLevels(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE}/api/logs/levels`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      return ['info', 'success', 'warning', 'error'];
    }

    const data = await response.json();
    return data.levels || ['info', 'success', 'warning', 'error'];
  } catch (error) {
    console.error('[Logs API] Error fetching log levels:', error);
    return ['info', 'success', 'warning', 'error'];
  }
}

/**
 * Connect to logs WebSocket stream
 */
export function connectLogsWebSocket(
  onMessage: (log: LogEntry) => void,
  onError?: (error: Event) => void
): WebSocket | null {
  try {
    const wsUrl = API_BASE.replace('http', 'ws');
    const ws = new WebSocket(`${wsUrl}/api/logs/stream`);

    ws.onmessage = (event) => {
      try {
        const log = JSON.parse(event.data);
        onMessage(log);
      } catch (error) {
        console.error('[Logs WebSocket] Error parsing message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[Logs WebSocket] Connection error:', error);
      if (onError) onError(error);
    };

    ws.onclose = () => {
      console.log('[Logs WebSocket] Connection closed');
    };

    return ws;
  } catch (error) {
    console.error('[Logs WebSocket] Failed to connect:', error);
    return null;
  }
}
