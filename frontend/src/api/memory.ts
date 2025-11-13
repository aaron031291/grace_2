const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type MemoryTreeNode = {
  name: string;
  path: string;
  type: "file" | "folder";
  size?: number;
  modified?: string;
};

export async function fetchFileTree(path = "/") {
  const url = `${API_BASE}/api/memory/files?path=${encodeURIComponent(path)}`;
  console.log('Fetching tree from:', url);
  const res = await fetch(url);
  if (!res.ok) {
    const error = await res.text();
    console.error('API error:', error);
    throw new Error("Failed to load file tree");
  }
  const data = await res.json();
  console.log('Tree data received:', data);
  return data as {
    path: string;
    folders: MemoryTreeNode[];
    files: MemoryTreeNode[];
  };
}

export async function fetchFileContent(path: string) {
  const res = await fetch(`${API_BASE}/api/memory/files/content?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error("Failed to load file content");
  const data = await res.json();
  return data.content as string;
}

export async function fetchRowsByPath(path: string) {
  const res = await fetch(`${API_BASE}/api/memory/tables/by-path?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error("Failed to load table rows");
  return res.json() as Promise<{
    table: string;
    rows: Record<string, unknown>[];
  }>;
}

export async function fetchPendingSchemas() {
  const res = await fetch(`${API_BASE}/api/memory/schemas/pending`);
  if (!res.ok) throw new Error("Failed to load schema proposals");
  return res.json() as Promise<
    Array<{ proposal_id: string; table: string; summary: string; diff: Record<string, unknown> }>
  >;
}

export async function approveSchema(proposalId: string, approved: boolean, notes?: string) {
  const res = await fetch(`${API_BASE}/api/memory/schemas/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ proposal_id: proposalId, approved, notes }),
  });
  if (!res.ok) throw new Error("Failed to submit approval");
  return res.json();
}

export async function saveFile(path: string, content: string) {
  const res = await fetch(`${API_BASE}/api/memory/files/content?path=${encodeURIComponent(path)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error("Failed to save file");
  return res.json();
}

export async function createFolder(parentPath: string, folderName: string) {
  const fullPath = `${parentPath}/${folderName}`.replace(/\/+/g, '/');
  const res = await fetch(`${API_BASE}/api/memory/files/create?path=${encodeURIComponent(fullPath)}&is_directory=true`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to create folder");
  return res.json();
}

export async function createFile(parentPath: string, fileName: string) {
  const fullPath = `${parentPath}/${fileName}`.replace(/\/+/g, '/');
  const res = await fetch(`${API_BASE}/api/memory/files/create?path=${encodeURIComponent(fullPath)}&is_directory=false`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to create file");
  return res.json();
}

export async function renamePath(oldPath: string, newPath: string) {
  const res = await fetch(`${API_BASE}/api/memory/files/rename?old_path=${encodeURIComponent(oldPath)}&new_path=${encodeURIComponent(newPath)}`, {
    method: "PATCH",
  });
  if (!res.ok) throw new Error("Failed to rename path");
  return res.json();
}

export async function deletePath(path: string) {
  const res = await fetch(`${API_BASE}/api/memory/files/delete?path=${encodeURIComponent(path)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete path");
  return res.json();
}

export async function uploadFile(file: File, targetPath: string) {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_BASE}/api/memory/files/upload?target_path=${encodeURIComponent(targetPath)}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload file");
  return res.json();
}
