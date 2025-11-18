/**
 * Chat API Client
 * 
 * Handles all chat-related API calls with proper error handling
 */

import { API_ENDPOINTS } from './config';

export interface ChatMessage {
  message: string;
  session_id?: string;
  attachments?: string[];
  user_id?: string;
}

export interface ChatResponse {
  reply: string;
  trace_id: string;
  session_id: string;
  actions: ActionProposal[];
  citations: string[];
  confidence: number;
  requires_approval: boolean;
  pending_approvals: PendingApproval[];
  timestamp: string;
}

export interface ActionProposal {
  trace_id: string;
  action_type: string;
  agent: string;
  params: Record<string, any>;
  governance_tier: string;
  timestamp: string;
  approved: boolean;
  reason: string;
}

export interface PendingApproval {
  trace_id: string;
  action_type: string;
  agent: string;
  governance_tier: string;
  params: Record<string, any>;
  reason: string;
  timestamp: string;
}

export interface ApprovalRequest {
  trace_id: string;
  approved: boolean;
  reason?: string;
  user_id?: string;
}

export class ChatAPI {
  static async sendMessage(message: ChatMessage): Promise<ChatResponse> {
    const response = await fetch(API_ENDPOINTS.chat, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Chat request failed');
    }

    return response.json();
  }

  static async approveAction(approval: ApprovalRequest): Promise<any> {
    const response = await fetch(API_ENDPOINTS.chatApprove, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(approval),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Approval request failed');
    }

    return response.json();
  }

  static async getChatHistory(sessionId: string, limit: number = 50): Promise<any> {
    const response = await fetch(`${API_ENDPOINTS.chatHistory(sessionId)}?limit=${limit}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to fetch chat history');
    }

    return response.json();
  }

  static async listSessions(): Promise<any> {
    const response = await fetch(API_ENDPOINTS.chatSessions);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || 'Failed to fetch sessions');
    }

    return response.json();
  }
}
