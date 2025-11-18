import { apiUrl, WS_BASE_URL } from '../config';
// API helpers for memory management endpoints

const API_BASE = import.meta.env.VITE_API_URL || apiUrl('';

export interface FileNode {
  path: string;
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  size?: number;
  modified?: string;
}

export interface FileContent {
  path: string;
  content: string;
  encoding: string;
  size: number;
  modified: string;
}

export interface TableRow {
  id: string;
  [key: string]: any;
}

export interface SchemaProposal {
  proposal_id: string;
  table_name: string;
  proposed_schema: Record<string, any>;
  confidence: number;
  sample_rows: any[];
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

// File Operations
export async function listFiles(path: string = ''): Promise<FileNode[]> {
  const response = await fetch(`${API_BASE}/api/memory/files/list?path=${encodeURIComponent(path)}`);
  if (!response.ok) throw new Error('Failed to list files');
  return response.json();
}

export async function getFileContent(path: string): Promise<FileContent> {
  const response = await fetch(`${API_BASE}/api/memory/files/content?path=${encodeURIComponent(path)}`);
  if (!response.ok) throw new Error('Failed to get file content');
  return response.json();
}

export async function saveFileContent(path: string, content: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/files/content`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, content }),
  });
  if (!response.ok) throw new Error('Failed to save file');
}

export async function createFile(path: string, content: string = ''): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/files/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, content }),
  });
  if (!response.ok) throw new Error('Failed to create file');
}

export async function createFolder(path: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/files/folder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path }),
  });
  if (!response.ok) throw new Error('Failed to create folder');
}

export async function deleteFile(path: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/files/delete`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path }),
  });
  if (!response.ok) throw new Error('Failed to delete file');
}

export async function renameFile(oldPath: string, newPath: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/files/rename`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ old_path: oldPath, new_path: newPath }),
  });
  if (!response.ok) throw new Error('Failed to rename file');
}

export async function uploadFile(path: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('path', path);

  const response = await fetch(`${API_BASE}/api/memory/files/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to upload file');
}

// Table Operations
export async function listTables(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/memory/tables/list`);
  if (!response.ok) throw new Error('Failed to list tables');
  return response.json();
}

export async function getTableData(tableName: string, limit: number = 100): Promise<TableRow[]> {
  const response = await fetch(`${API_BASE}/api/memory/tables/${tableName}?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to get table data');
  return response.json();
}

export async function getLinkedRows(filePath: string): Promise<TableRow[]> {
  const response = await fetch(`${API_BASE}/api/memory/tables/linked?file_path=${encodeURIComponent(filePath)}`);
  if (!response.ok) throw new Error('Failed to get linked rows');
  return response.json();
}

export async function insertTableRow(tableName: string, data: Record<string, any>): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/tables/${tableName}/insert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to insert row');
}

export async function updateTableRow(tableName: string, id: string, data: Record<string, any>): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/tables/${tableName}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update row');
}

export async function deleteTableRow(tableName: string, id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/tables/${tableName}/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete row');
}

// Schema Proposals
export async function getPendingSchemas(): Promise<SchemaProposal[]> {
  const response = await fetch(`${API_BASE}/api/memory/schemas/pending`);
  if (!response.ok) throw new Error('Failed to get pending schemas');
  return response.json();
}

export async function approveSchema(proposalId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/schemas/${proposalId}/approve`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to approve schema');
}

export async function rejectSchema(proposalId: string, reason?: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/memory/schemas/${proposalId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
  if (!response.ok) throw new Error('Failed to reject schema');
}

// Search
export async function searchMemory(query: string): Promise<any[]> {
  const response = await fetch(`${API_BASE}/api/memory/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Failed to search');
  return response.json();
}
