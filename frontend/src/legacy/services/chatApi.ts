/**
 * Chat API Service
 * Handles all chat-related API calls with Grace
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    citations?: Citation[];
    missions?: string[];
    kpis?: string[];
    suggestions?: string[];
    actions?: Action[];
    [key: string]: any;
  };
  attachments?: Attachment[];
}

export interface Citation {
  type: 'mission' | 'kpi' | 'document' | 'code' | 'url';
  id: string;
  title: string;
  url?: string;
  excerpt?: string;
}

export interface Action {
  type: 'open_workspace' | 'execute_mission' | 'view_logs' | 'custom';
  label: string;
  payload: any;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  size?: number;
  url?: string;
  reference?: string; // Reference ID after upload
}

export interface SendMessageRequest {
  message: string;
  attachments?: File[];
  context?: {
    currentMission?: string;
    currentWorkspace?: string;
    [key: string]: any;
  };
}

export interface ChatResponse {
  response: string;
  citations?: Citation[];
  metadata?: {
    missions?: string[];
    kpis?: string[];
    suggestions?: string[];
    actions?: Action[];
    [key: string]: any;
  };
  message_id?: string;
}

export interface UploadAttachmentResponse {
  reference: string;
  filename: string;
  artifact_id?: string;
  url?: string;
}

class ChatApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ChatApiError';
  }
}

/**
 * Get authentication headers
 */
function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token') || 'dev-token';
  return {
    'Authorization': `Bearer ${token}`,
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

    throw new ChatApiError(errorMessage, response.status, errorDetails);
  }

  return response.json();
}

/**
 * Upload attachment to remote access/librarian
 */
export async function uploadAttachment(file: File): Promise<UploadAttachmentResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', 'chat-attachment');

  const response = await fetch(`${API_BASE}/api/ingest/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  const result = await handleResponse<any>(response);

  return {
    reference: result.artifact_id || result.file_id || file.name,
    filename: file.name,
    artifact_id: result.artifact_id,
    url: result.url,
  };
}

/**
 * Send chat message to Grace
 */
export async function sendMessage(request: SendMessageRequest): Promise<ChatResponse> {
  // Upload attachments first if any
  let attachmentReferences: UploadAttachmentResponse[] = [];
  if (request.attachments && request.attachments.length > 0) {
    attachmentReferences = await Promise.all(
      request.attachments.map(file => uploadAttachment(file))
    );
  }

  // Build the chat payload
  const payload: any = {
    message: request.message,
    context: request.context || {},
  };

  // Include attachment references in the message
  if (attachmentReferences.length > 0) {
    payload.attachments = attachmentReferences.map(ref => ({
      reference: ref.reference,
      filename: ref.filename,
      artifact_id: ref.artifact_id,
    }));
    
    // Also append to message for Grace to see
    payload.message += `\n\n[Attachments: ${attachmentReferences.map(r => r.filename).join(', ')}]`;
  }

  // Send to chat endpoint
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const result = await handleResponse<any>(response);

  // Parse response and extract metadata
  return {
    response: result.response || result.message || result.text || '',
    citations: extractCitations(result),
    metadata: extractMetadata(result),
    message_id: result.message_id || result.id,
  };
}

/**
 * Extract citations from response
 */
function extractCitations(response: any): Citation[] {
  const citations: Citation[] = [];

  // Check for explicit citations field
  if (response.citations && Array.isArray(response.citations)) {
    citations.push(...response.citations);
  }

  // Check for references in metadata
  if (response.metadata) {
    if (response.metadata.missions) {
      response.metadata.missions.forEach((missionId: string) => {
        citations.push({
          type: 'mission',
          id: missionId,
          title: `Mission ${missionId}`,
        });
      });
    }

    if (response.metadata.kpis) {
      response.metadata.kpis.forEach((kpiId: string) => {
        citations.push({
          type: 'kpi',
          id: kpiId,
          title: `KPI: ${kpiId}`,
        });
      });
    }

    if (response.metadata.documents) {
      response.metadata.documents.forEach((doc: any) => {
        citations.push({
          type: 'document',
          id: doc.id || doc.artifact_id,
          title: doc.title || doc.filename,
          url: doc.url,
          excerpt: doc.excerpt,
        });
      });
    }
  }

  // Parse citations from response text (e.g., [mission:abc123])
  const text = response.response || response.message || '';
  const missionMatches = text.matchAll(/\[mission:(\S+)\]/g);
  for (const match of missionMatches) {
    citations.push({
      type: 'mission',
      id: match[1],
      title: `Mission ${match[1]}`,
    });
  }

  const kpiMatches = text.matchAll(/\[kpi:(\S+)\]/g);
  for (const match of kpiMatches) {
    citations.push({
      type: 'kpi',
      id: match[1],
      title: `KPI: ${match[1]}`,
    });
  }

  return citations;
}

/**
 * Extract metadata from response
 */
function extractMetadata(response: any): any {
  const metadata: any = {};

  if (response.metadata) {
    Object.assign(metadata, response.metadata);
  }

  // Extract suggestions
  if (response.suggestions) {
    metadata.suggestions = response.suggestions;
  }

  // Extract actions
  if (response.actions) {
    metadata.actions = response.actions;
  }

  // Parse follow-up questions
  if (response.follow_up_questions) {
    metadata.suggestions = response.follow_up_questions;
  }

  return metadata;
}

/**
 * Get conversation history (if backend supports it)
 */
export async function getConversationHistory(limit: number = 50): Promise<ChatMessage[]> {
  try {
    const response = await fetch(`${API_BASE}/api/chat/history?limit=${limit}`, {
      headers: getAuthHeaders(),
    });

    const result = await handleResponse<any>(response);
    return result.messages || [];
  } catch (error) {
    console.warn('Chat history not available:', error);
    return [];
  }
}

/**
 * Clear conversation history
 */
export async function clearConversationHistory(): Promise<void> {
  try {
    await fetch(`${API_BASE}/api/chat/history`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
  } catch (error) {
    console.warn('Failed to clear chat history:', error);
  }
}

export { ChatApiError };
