/**
 * Grace Co-Pilot Sidebar
 * Context-aware AI assistance docked to Memory panel
 */

import { useState, useEffect, useRef } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import {
  MessageSquare,
  Send,
  Sparkles,
  FileText,
  Table,
  Wand2,
  AlertTriangle,
  CheckCircle,
  Loader
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

interface Context {
  file_path?: string;
  table_name?: string;
  row_data?: any;
}

interface GraceCopilotProps {
  context?: Context;
  onSuggestSchema?: () => void;
  onRecommendPlan?: () => void;
  onFlagConflicts?: () => void;
}

export function GraceCopilot({ 
  context, 
  onSuggestSchema,
  onRecommendPlan,
  onFlagConflicts
}: GraceCopilotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Add context change notification
    if (context?.file_path || context?.table_name) {
      const contextMsg: Message = {
        role: 'system',
        content: context.file_path 
          ? `Now viewing: ${context.file_path}`
          : `Now viewing table: ${context.table_name}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, contextMsg]);
    }
  }, [context?.file_path, context?.table_name]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(apiUrl('/api/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'current_user',  // Would come from auth
          message: input,
          context
        })
      });

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || 'I apologize, but I encountered an error.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat failed:', err);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    setLoading(true);
    
    try {
      let endpoint = '';
      let body = {};
      
      switch (action) {
        case 'suggest_schema':
          if (context?.file_path) {
            endpoint = '/api/copilot/suggest-schema';
            body = { file_path: context.file_path };
          }
          break;
        
        case 'recommend_plan':
          endpoint = '/api/copilot/recommend-plan';
          body = { file_paths: [context?.file_path] };
          break;
        
        case 'flag_conflicts':
          if (context?.table_name && context?.row_data) {
            endpoint = '/api/copilot/flag-conflicts';
            body = { table_name: context.table_name, row_data: context.row_data };
          }
          break;
      }
      
      if (endpoint) {
        const response = await fetch(`http://localhost:8000${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        const resultMessage: Message = {
          role: 'assistant',
          content: JSON.stringify(data, null, 2),
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, resultMessage]);
      }
    } catch (err) {
      console.error('Quick action failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 border-l border-gray-700 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="font-bold">Grace Co-Pilot</h3>
        </div>
        
        {context && (
          <div className="mt-2 text-xs text-gray-400">
            {context.file_path && (
              <div className="flex items-center gap-1">
                <FileText className="w-3 h-3" />
                <span className="truncate">{context.file_path}</span>
              </div>
            )}
            {context.table_name && (
              <div className="flex items-center gap-1">
                <Table className="w-3 h-3" />
                <span>{context.table_name.replace('memory_', '')}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        <div className="text-xs text-gray-400 mb-2">Quick Actions</div>
        
        <button
          onClick={() => handleQuickAction('suggest_schema')}
          disabled={!context?.file_path || loading}
          className="
            w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 
            disabled:bg-gray-700 disabled:text-gray-500 
            rounded text-sm flex items-center gap-2 justify-center
          "
        >
          <Wand2 className="w-4 h-4" />
          Generate Schema
        </button>
        
        <button
          onClick={() => handleQuickAction('recommend_plan')}
          disabled={!context?.file_path || loading}
          className="
            w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 
            disabled:bg-gray-700 disabled:text-gray-500 
            rounded text-sm flex items-center gap-2 justify-center
          "
        >
          <CheckCircle className="w-4 h-4" />
          Recommend Plan
        </button>
        
        <button
          onClick={() => handleQuickAction('flag_conflicts')}
          disabled={!context?.table_name || loading}
          className="
            w-full px-3 py-2 bg-orange-600 hover:bg-orange-700 
            disabled:bg-gray-700 disabled:text-gray-500 
            rounded text-sm flex items-center gap-2 justify-center
          "
        >
          <AlertTriangle className="w-4 h-4" />
          Flag Conflicts
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 py-12">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Ask Grace about this file or table</p>
            <p className="text-xs mt-2">Try: "Explain this file" or "Identify missing fields"</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`
                ${msg.role === 'user' 
                  ? 'ml-8 bg-blue-900 bg-opacity-30' 
                  : msg.role === 'system'
                  ? 'bg-gray-800 border border-gray-700'
                  : 'mr-8 bg-gray-800'
                } 
                p-3 rounded
              `}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-gray-400">
                  {msg.role === 'user' ? 'You' : msg.role === 'system' ? 'System' : 'Grace'}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="text-sm text-gray-200 whitespace-pre-wrap">
                {msg.content}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask Grace anything..."
            disabled={loading}
            className="
              flex-1 bg-gray-800 border border-gray-700 rounded 
              px-3 py-2 text-sm text-white
              disabled:opacity-50
            "
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="
              px-3 py-2 bg-purple-600 hover:bg-purple-700 
              disabled:bg-gray-700 disabled:text-gray-500 
              rounded flex items-center gap-2
            "
          >
            {loading ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
