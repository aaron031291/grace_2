import { apiUrl, WS_BASE_URL } from '../config';
/**
 * Librarian API Helper Functions
 * Handles all Librarian kernel API calls with proper error handling
 */

const API_BASE = apiUrl('';

export interface LibrarianStatus {
  kernel: {
    kernel_id: string;
    status: string;
    active: boolean;
  };
  queues: {
    schema: number;
    ingestion: number;
    trust_audit: number;
  };
  agents: {
    active: number;
    total_spawned: number;
  };
  watch_paths: string[];
}

export interface SchemaProposal {
  log_id: number;
  action_type: string;
  target_path: string;
  details: string;
  timestamp: string;
}

export interface FileOperation {
  id: string;
  operation: string;
  source_path: string;
  target_path: string;
  can_undo: boolean;
  undone: boolean;
  created_at: string;
}

export interface LogEntry {
  log_id: number;
  action_type: string;
  target_path: string;
  details: string;
  timestamp: string;
}

export async function fetchLibrarianStatus(): Promise<LibrarianStatus> {
  const res = await fetch(`${API_BASE}/api/librarian/status`);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function fetchSchemaProposals(): Promise<SchemaProposal[]> {
  const res = await fetch(`${API_BASE}/api/librarian/schema-proposals`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.proposals || [];
}

export async function approveSchema(proposalId: string, approved: boolean, notes?: string) {
  const res = await fetch(`${API_BASE}/api/librarian/schema-proposals/${proposalId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ proposal_id: proposalId, approved, notes })
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchFileOperations(limit = 100): Promise<FileOperation[]> {
  const res = await fetch(`${API_BASE}/api/librarian/file-operations?limit=${limit}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.operations || [];
}

export async function fetchImmutableLogs(limit = 100, actionType?: string): Promise<LogEntry[]> {
  const url = actionType 
    ? `${API_BASE}/api/librarian/logs/immutable?limit=${limit}&action_type=${actionType}`
    : `${API_BASE}/api/librarian/logs/immutable?limit=${limit}`;
    
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.logs || [];
}

export async function tailLogs(lines = 50): Promise<LogEntry[]> {
  const res = await fetch(`${API_BASE}/api/librarian/logs/tail?lines=${lines}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.logs || [];
}

export async function fetchActivity(limit = 50) {
  const res = await fetch(`${API_BASE}/api/librarian/activity?limit=${limit}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function startLibrarian() {
  const res = await fetch(`${API_BASE}/api/librarian/start`, { method: 'POST' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function stopLibrarian() {
  const res = await fetch(`${API_BASE}/api/librarian/stop`, { method: 'POST' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
