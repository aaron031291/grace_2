/**
 * Enhanced Chat API with structured requests and model metadata
 */

import { sendMessage as baseSendMessage, type ChatMessage, type Citation } from './chatApi';
import { queryWorldModel, askGrace, ragQuery } from './worldModelApi';

export interface StructuredChatRequest {
  message: string;
  task_type?: 'coding' | 'reasoning' | 'review' | 'research' | 'general' | 'debugging';
  model?: string;  // Override auto-selection
  context?: {
    language?: string;
    framework?: string;
    file_type?: string;
    desired_output?: 'code' | 'explanation' | 'summary' | 'analysis';
    [key: string]: any;
  };
  attachments?: File[];
}

export interface EnhancedChatResponse {
  response: string;
  model_used?: string;
  task_type?: string;
  citations?: Citation[];
  metadata?: {
    reasoning_steps?: string[];
    confidence?: number;
    alternative_models?: string[];
    [key: string]: any;
  };
  message_id?: string;
}

/**
 * Send structured chat request with task metadata
 */
export async function sendStructuredMessage(
  request: StructuredChatRequest
): Promise<EnhancedChatResponse> {
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';
  
  // Parse special commands
  const message = request.message.trim();
  
  // /ask command → World Model
  if (message.startsWith('/ask ')) {
    const question = message.substring(5);
    const result = await askGrace(question);
    return {
      response: result.response,
      model_used: 'world-model',
      citations: result.citations,
      metadata: { source: 'world_model', ...result.context },
    };
  }
  
  // /rag command → RAG query
  if (message.startsWith('/rag ')) {
    const query = message.substring(5);
    const result = await ragQuery(query);
    return {
      response: result.answer,
      model_used: 'rag-system',
      citations: result.sources?.map((s: any) => ({
        type: 'document' as const,
        id: s.id,
        title: s.title || s.filename,
        excerpt: s.excerpt,
      })),
      metadata: { source: 'rag', sources: result.sources },
    };
  }
  
  // /world command → World Model query
  if (message.startsWith('/world ')) {
    const question = message.substring(7);
    const result = await queryWorldModel(question);
    return {
      response: result.answer,
      model_used: 'world-model',
      citations: result.citations,
      metadata: { 
        source: 'world_model', 
        context_used: result.context_used 
      },
    };
  }
  
  // Regular chat with structured request
  const token = localStorage.getItem('token') || 'dev-token';
  const userId = localStorage.getItem('user_id') || 'aaron';
  
  // Upload attachments first
  let attachmentRefs: any[] = [];
  if (request.attachments && request.attachments.length > 0) {
    const formData = new FormData();
    request.attachments.forEach(file => formData.append('files', file));
    
    const uploadResponse = await fetch(`${API_BASE}/api/ingest/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-User-ID': userId,
      },
      body: formData,
    });
    
    if (uploadResponse.ok) {
      const uploadResult = await uploadResponse.json();
      attachmentRefs = [uploadResult];
    }
  }
  
  // Build structured payload
  const payload = {
    message: request.message,
    task_type: request.task_type || inferTaskType(request.message),
    model: request.model, // Override if specified
    context: {
      ...request.context,
      attachments: attachmentRefs,
      user_id: userId,
    },
  };
  
  // Send to backend
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-User-ID': userId,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
    throw new Error(`Chat failed: ${response.statusText}`);
  }
  
  const result = await response.json();
  
  return {
    response: result.response || result.message || '',
    model_used: result.model_used || result.metadata?.model,
    task_type: result.task_type || request.task_type,
    citations: extractCitations(result),
    metadata: result.metadata || {},
    message_id: result.message_id,
  };
}

/**
 * Infer task type from message content
 */
function inferTaskType(message: string): string {
  const lower = message.toLowerCase();
  
  if (lower.includes('review') || lower.includes('check') || lower.includes('audit')) {
    return 'review';
  }
  if (lower.includes('write code') || lower.includes('implement') || lower.includes('function')) {
    return 'coding';
  }
  if (lower.includes('debug') || lower.includes('fix') || lower.includes('error')) {
    return 'debugging';
  }
  if (lower.includes('research') || lower.includes('find') || lower.includes('search')) {
    return 'research';
  }
  if (lower.includes('explain') || lower.includes('why') || lower.includes('how')) {
    return 'reasoning';
  }
  
  return 'general';
}

/**
 * Extract citations from response
 */
function extractCitations(response: any): Citation[] {
  const citations: Citation[] = [];
  
  if (response.citations && Array.isArray(response.citations)) {
    citations.push(...response.citations);
  }
  
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
    
    if (response.metadata.sources) {
      response.metadata.sources.forEach((source: any) => {
        citations.push({
          type: 'document',
          id: source.id || source.artifact_id,
          title: source.title || source.filename,
          excerpt: source.excerpt,
        });
      });
    }
  }
  
  return citations;
}

export { type ChatMessage, type Citation };
