/**
 * MCP (Model Context Protocol) API Service
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

function getAuthHeaders(): Record<string, string> {
  return {
    'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
  };
}

export interface MCPResource {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}

/**
 * Get MCP manifest
 */
export async function getMCPManifest(): Promise<{
  resources: MCPResource[];
  tools: MCPTool[];
}> {
  const response = await fetch(`${API_BASE}/world-model/mcp/manifest`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) throw new Error('Failed to get MCP manifest');
  return response.json();
}

/**
 * Get MCP resource
 */
export async function getMCPResource(uri: string): Promise<{
  uri: string;
  content: string;
  mimeType: string;
}> {
  const response = await fetch(
    `${API_BASE}/world-model/mcp/resource?uri=${encodeURIComponent(uri)}`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) throw new Error('Failed to get MCP resource');
  return response.json();
}

/**
 * Invoke MCP tool
 */
export async function invokeMCPTool(
  toolName: string,
  parameters: Record<string, any>
): Promise<{
  result: any;
  success: boolean;
  error?: string;
}> {
  const response = await fetch(`${API_BASE}/world-model/mcp/tool`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tool_name: toolName,
      parameters,
    }),
  });

  if (!response.ok) throw new Error('MCP tool invocation failed');
  return response.json();
}
