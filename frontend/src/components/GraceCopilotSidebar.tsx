import React, { useState, useEffect, useRef } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import './GraceCopilotSidebar.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface CopilotContext {
  file_path?: string;
  table_name?: string;
  row_data?: any;
}

interface GraceCopilotSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  context?: CopilotContext;
  token: string;
}

export const GraceCopilotSidebar: React.FC<GraceCopilotSidebarProps> = ({
  isOpen,
  onClose,
  context,
  token
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (context) {
      generateSuggestions();
    }
  }, [context]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateSuggestions = () => {
    const newSuggestions: string[] = [];

    if (context?.file_path) {
      newSuggestions.push('Explain this file');
      newSuggestions.push('Suggest schema for this file');
      newSuggestions.push('Find similar files');
    }

    if (context?.table_name) {
      newSuggestions.push('Show table statistics');
      newSuggestions.push('Identify missing fields');
      newSuggestions.push('Check for conflicts');
    }

    setSuggestions(newSuggestions);
  };

  const sendMessage = async (messageText?: string) => {
    const text = messageText || input.trim();
    if (!text) return;

    const userMessage: Message = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(apiUrl('/api/collaboration/copilot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: text,
          context
        })
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    if (!context) return;

    setLoading(true);
    try {
      let endpoint = '';
      let body: any = {};

      if (action === 'Explain this file' && context.file_path) {
        endpoint = '/api/collaboration/copilot/explain-file';
        body = {
          file_path: context.file_path,
          file_content: ''
        };
      } else if (action === 'Suggest schema for this file' && context.file_path) {
        endpoint = '/api/collaboration/copilot/suggest-schema';
        body = {
          file_path: context.file_path,
          file_content: ''
        };
      } else {
        sendMessage(action);
        return;
      }

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (data.success) {
        const message: Message = {
          role: 'assistant',
          content: JSON.stringify(data, null, 2),
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, message]);
      }
    } catch (error) {
      console.error('Quick action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="grace-copilot-sidebar">
      <div className="copilot-header">
        <div className="copilot-title">
          <span className="copilot-icon">✨</span>
          Grace Co-Pilot
        </div>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      {context && (
        <div className="context-indicator">
          {context.file_path && (
            <div className="context-item">
              <span className="context-label">📄 File:</span>
              <span className="context-value">{context.file_path}</span>
            </div>
          )}
          {context.table_name && (
            <div className="context-item">
              <span className="context-label">📊 Table:</span>
              <span className="context-value">{context.table_name}</span>
            </div>
          )}
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="quick-actions">
          <div className="quick-actions-title">Quick Actions</div>
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              className="quick-action-btn"
              onClick={() => handleQuickAction(suggestion)}
              disabled={loading}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <span className="empty-icon">💬</span>
            <p>Ask Grace anything about your workspace!</p>
          </div>
        )}

        {messages.map((message, idx) => (
          <div key={idx} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '✨'}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-avatar">✨</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask Grace..."
          disabled={loading}
          className="message-input"
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="send-btn"
        >
          ➤
        </button>
      </div>
    </div>
  );
};
