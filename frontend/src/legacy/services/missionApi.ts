/**
 * Mission Control API Service
 * Handles all API calls related to missions, with proper error handling
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export interface MissionFilters {
  status?: string;
  subsystem_id?: string;
  severity?: string;
  limit?: number;
}

export interface Mission {
  mission_id: string;
  subsystem_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'awaiting_validation' | 'observing' | 'resolved' | 'escalated' | 'failed';
  detected_by: string;
  assigned_to: string;
  created_at: string;
  updated_at: string;
  symptoms_count?: number;
  remediation_events_count?: number;
}

export interface MissionDetail extends Mission {
  context?: {
    git_sha: string;
    config_hash: string;
    env: string;
    branch?: string;
    version?: string;
    previous_mission_id?: string;
  };
  symptoms?: Array<{
    description: string;
    metric_id?: string;
    observed_value?: number;
    threshold?: number;
    log_snippet?: string;
    detected_at?: string;
  }>;
  workspace?: {
    repo_path: string;
    working_branch: string;
  };
  acceptance_criteria?: {
    tests_must_pass?: boolean;
    metrics?: Array<{
      metric_id: string;
      comparator: string;
      threshold: number;
    }>;
  };
  remediation_history?: Array<{
    timestamp: string;
    event_type: string;
    description: string;
  }>;
  kpi_deltas?: Record<string, number>;
}

export interface MissionsResponse {
  total: number;
  missions: Mission[];
}

export interface ExecuteMissionRequest {
  mission_type: 'coding' | 'healing';
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

class MissionApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'MissionApiError';
  }
}

/**
 * Get authentication headers
 */
function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token') || 'dev-token';
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

/**
 * Handle API response and errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `API error: ${response.status} ${response.statusText}`;
    let errorDetails;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
      errorDetails = errorData;
    } catch {
      // Response body is not JSON
    }

    throw new MissionApiError(errorMessage, response.status, errorDetails);
  }

  return response.json();
}

/**
 * Build query string from filters
 */
function buildQueryString(filters: MissionFilters): string {
  const params = new URLSearchParams();

  if (filters.status) params.append('status', filters.status);
  if (filters.subsystem_id) params.append('subsystem_id', filters.subsystem_id);
  if (filters.severity) params.append('severity', filters.severity);
  if (filters.limit) params.append('limit', filters.limit.toString());

  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

/**
 * Fetch missions list with optional filtering
 */
export async function fetchMissions(filters: MissionFilters = {}): Promise<MissionsResponse> {
  try {
    const queryString = buildQueryString(filters);
    const response = await fetch(`${API_BASE}/mission-control/missions${queryString}`, {
      headers: getAuthHeaders(),
    });

    return handleResponse<MissionsResponse>(response);
  } catch (error) {
    // Gracefully handle endpoint not found
    if (error instanceof MissionApiError && error.status === 404) {
      console.warn('[Mission API] Missions endpoint not available (404)');
      return { total: 0, missions: [] };
    }
    throw error;
  }
}

/**
 * Fetch single mission details
 */
export async function fetchMissionDetails(missionId: string): Promise<MissionDetail> {
  const response = await fetch(`${API_BASE}/mission-control/missions/${missionId}`, {
    headers: getAuthHeaders(),
  });

  return handleResponse<MissionDetail>(response);
}

/**
 * Execute a mission
 */
export async function executeMission(
  missionId: string,
  missionType: 'coding' | 'healing' = 'coding'
): Promise<any> {
  const response = await fetch(`${API_BASE}/mission-control/missions/${missionId}/execute`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ mission_type: missionType }),
  });

  return handleResponse(response);
}

/**
 * Acknowledge a mission (if endpoint exists)
 */
export async function acknowledgeMission(missionId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/mission-control/missions/${missionId}/acknowledge`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

/**
 * Get mission control status
 */
export async function fetchMissionControlStatus(): Promise<any> {
  const response = await fetch(`${API_BASE}/mission-control/status`, {
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

/**
 * Get subsystem health
 */
export async function fetchSubsystemHealth(): Promise<any> {
  const response = await fetch(`${API_BASE}/mission-control/subsystems`, {
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

/**
 * Create a new mission (if needed)
 */
export async function createMission(missionData: any): Promise<any> {
  const response = await fetch(`${API_BASE}/mission-control/missions/legacy`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(missionData),
  });

  return handleResponse(response);
}

/**
 * Get follow-up planner status (if endpoint exists)
 */
export async function fetchFollowUpPlannerStatus(): Promise<any> {
  const response = await fetch(`${API_BASE}/mission-control/follow-up-status`, {
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

/**
 * Trigger preventive mission
 */
export async function createPreventiveMission(relatedMissionId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/mission-control/missions/${relatedMissionId}/preventive`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

// Export the error class for type checking
export { MissionApiError };
