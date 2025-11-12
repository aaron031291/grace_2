/**
 * Memory API Helper Functions
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface FileTreeNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
  children?: FileTreeNode[];
}

export interface TableRow {
  id: string;
  [key: string]: any;
}

export interface SchemaProposal {
  proposal_id: string;
  file_path: string;
  recommended_table: string;
  confidence: number;
  table_exists: boolean;
  extracted_fields: Record<string, any>;
  reasoning: string;
  timestamp: string;
}

export interface AgentStatus {
  agent_id: string;
  agent_name: string;
  status: string;
  trust_score: number;
  current_task?: string;
  jobs_completed: number;
  jobs_failed: number;
}

export async function fetchFileTree(): Promise<FileTreeNode[]> {
  const res = await fetch(`${API_BASE}/api/memory/files`);
  if (!res.ok) throw new Error('Failed to fetch file tree');
  return res.json();
}

export async function fetchTableRows(pathOrTable: string, limit: number = 100): Promise<TableRow[]> {
  const res = await fetch(
    `${API_BASE}/api/memory/tables/rows?path=${encodeURIComponent(pathOrTable)}&limit=${limit}`
  );
  if (!res.ok) throw new Error('Failed to fetch table rows');
  const data = await res.json();
  return data.rows || [];
}

export async function fetchTableList(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/memory/tables/`);
  if (!res.ok) throw new Error('Failed to fetch table list');
  const data = await res.json();
  return data.tables || [];
}

export async function fetchTableSchema(tableName: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory/tables/${tableName}/schema`);
  if (!res.ok) throw new Error('Failed to fetch table schema');
  return res.json();
}

export async function fetchPendingSchemas(): Promise<SchemaProposal[]> {
  const res = await fetch(`${API_BASE}/api/memory/tables/proposals/pending`);
  if (!res.ok) throw new Error('Failed to fetch pending schemas');
  const data = await res.json();
  return data.proposals || [];
}

export async function approveSchema(proposalId: string): Promise<any> {
  const res = await fetch(
    `${API_BASE}/api/memory/tables/proposals/${proposalId}/approve`,
    { method: 'POST' }
  );
  if (!res.ok) throw new Error('Failed to approve schema');
  return res.json();
}

export async function rejectSchema(proposalId: string, reason: string = ''): Promise<any> {
  const res = await fetch(
    `${API_BASE}/api/memory/tables/proposals/${proposalId}/reject`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason })
    }
  );
  if (!res.ok) throw new Error('Failed to reject schema');
  return res.json();
}

export async function uploadFile(file: File, targetPath?: string): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  if (targetPath) {
    formData.append('target_path', targetPath);
  }
  
  const res = await fetch(`${API_BASE}/api/memory/files/upload`, {
    method: 'POST',
    body: formData
  });
  
  if (!res.ok) throw new Error('Failed to upload file');
  return res.json();
}

export async function updateTableRow(
  tableName: string,
  rowId: string,
  updates: Record<string, any>
): Promise<any> {
  const res = await fetch(
    `${API_BASE}/api/memory/tables/${tableName}/rows/${rowId}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updates })
    }
  );
  
  if (!res.ok) throw new Error('Failed to update row');
  return res.json();
}

export async function deleteTableRow(tableName: string, rowId: string): Promise<void> {
  const res = await fetch(
    `${API_BASE}/api/memory/tables/${tableName}/rows/${rowId}`,
    { method: 'DELETE' }
  );
  
  if (!res.ok) throw new Error('Failed to delete row');
}

export async function fetchActiveAgents(): Promise<AgentStatus[]> {
  const res = await fetch(`${API_BASE}/api/agent-lifecycle/agents`);
  if (!res.ok) throw new Error('Failed to fetch active agents');
  const data = await res.json();
  return data.agents || [];
}

export async function fetchAlerts(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/alerts/active`);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  const data = await res.json();
  return data.alerts || [];
}

export async function fetchTrustReport(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory/tables/trust/report`);
  if (!res.ok) throw new Error('Failed to fetch trust report');
  return res.json();
}
