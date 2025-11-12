/**
 * Memory File System API Client
 * Handles all file operations for Grace's training corpus
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  modified?: string;
  extension?: string;
  children?: FileNode[];
}

export interface FileContent {
  path: string;
  content: string;
  size: number;
  modified: string;
  extension: string;
}

export interface FileSystemStatus {
  component_id: string;
  status: string;
  root_path: string;
  total_files: number;
  total_size_bytes: number;
  total_size_mb: number;
}

/**
 * List files and folders in a directory
 */
export async function listFiles(path: string = ''): Promise<FileNode> {
  const response = await axios.get(`${API_BASE}/api/memory/files`, {
    params: { path }
  });
  return response.data;
}

/**
 * Read a file's content
 */
export async function readFile(path: string): Promise<FileContent> {
  const response = await axios.get(`${API_BASE}/api/memory/file`, {
    params: { path }
  });
  return response.data;
}

/**
 * Save or create a file
 */
export async function saveFile(path: string, content: string): Promise<void> {
  await axios.post(`${API_BASE}/api/memory/file`, null, {
    params: { path, content }
  });
}

/**
 * Delete a file or folder
 */
export async function deleteFile(path: string, recursive: boolean = false): Promise<void> {
  await axios.delete(`${API_BASE}/api/memory/file`, {
    params: { path, recursive }
  });
}

/**
 * Create a new folder
 */
export async function createFolder(path: string): Promise<void> {
  await axios.post(`${API_BASE}/api/memory/folder`, null, {
    params: { path }
  });
}

/**
 * Get filesystem status (file count, storage size)
 */
export async function getStatus(): Promise<FileSystemStatus> {
  const response = await axios.get(`${API_BASE}/api/memory/status`);
  return response.data;
}

/**
 * Upload a file
 */
export async function uploadFile(path: string, file: File): Promise<void> {
  const content = await file.text();
  await saveFile(path, content);
}
