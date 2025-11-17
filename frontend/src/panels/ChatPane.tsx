import { useState, useRef, useEffect } from 'react';
import { useChat, useChatAttachments } from '../hooks/useChat';
import type { ChatMessage, Citation } from '../services/chatApi';
import './ChatPane.css';

interface ChatPaneProps {
  onOpenWorkspace?: (type: string, data: any) => void;
}

export default function ChatPane({ onOpenWorkspace }: ChatPaneProps) {
  const {
    messages,
    loading,
    error: chatError,
    isEmpty,
    sendMessage,
    clearMessages,
  } = useChat({
    persistMessages: true,
    loadHistory: false,
    onError: (error) => {
      console.error('Chat error:', error);
    },
  });

  const {
    attachments,
    addAttachment,
    removeAttachment,
    clearAttachments,
  } = useChatAttachments();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() && attachments.length === 0) return;

    const messageText = input;
    const messageAttachments = [...attachments];

    // Clear input and attachments immediately
    setInput('');
    clearAttachments();

    // Send message
    await sendMessage(messageText, messageAttachments);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      Array.from(e.target.files).forEach(file => addAttachment(file));
    }
  };

  const handleCitationClick = (citation: Citation) => {
    if (onOpenWorkspace) {
      onOpenWorkspace(citation.type, citation);
    } else {
      console.log('Open citation:', citation);
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const quickActions = [
    { text: 'Show me the system status', icon: '📊' },
    { text: 'List all open missions', icon: '🎯' },
    { text: 'What are the recent logs?', icon: '📋' },
    { text: 'Show critical KPIs', icon: '📈' },
  ];

  return (
    <div className="chat-pane">
      <div className="chat-header">
        <div className="header-left">
          <h2>Grace Console</h2>
          <div className="chat-status">
            <span className={`status-indicator ${loading ? 'status-busy' : 'status-ready'}`}></span>
            <span>{loading ? 'Thinking...' : 'Ready'}</span>
          </div>
        </div>
        {!isEmpty && (
          <button onClick={clearMessages} className="clear-btn" title="Clear conversation">
            🗑️ Clear
          </button>
        )}
      </div>

      <div className="messages-container">
        {isEmpty ? (
          <div className="chat-welcome">
            <h3>👋 Welcome to Grace Console</h3>
            <p>How can I help you today?</p>
            <div className="quick-actions">
              {quickActions.map((action, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(action.text)}
                  className="quick-action-btn"
                >
                  <span className="action-icon">{action.icon}</span>
                  <span>{action.text}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onCitationClick={handleCitationClick}
              formatTime={formatTime}
            />
          ))
        )}

        {loading && (
          <div className="message assistant-message typing-indicator">
            <div className="message-header">
              <span className="message-author">Grace</span>
            </div>
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        {chatError && messages.length > 0 && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{chatError.message}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        {attachments.length > 0 && (
          <div className="attachments-preview">
            {attachments.map((file, idx) => (
              <div key={idx} className="attachment-chip">
                <span className="attachment-icon">📎</span>
                <span className="attachment-name">{file.name}</span>
                <span className="attachment-size">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
                <button onClick={() => removeAttachment(idx)} className="remove-attachment">
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="input-container">
          <button 
            className="attach-btn"
            onClick={() => fileInputRef.current?.click()}
            title="Attach files"
            disabled={loading}
          >
            📎
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Grace anything..."
            className="chat-input"
            rows={1}
            disabled={loading}
          />

          <button 
            onClick={handleSend} 
            className="send-btn"
            disabled={loading || (!input.trim() && attachments.length === 0)}
          >
            {loading ? '⏳' : '📤'}
          </button>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>
      </div>
    </div>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
  onCitationClick: (citation: Citation) => void;
  formatTime: (timestamp: string) => string;
}

function MessageBubble({ message, onCitationClick, formatTime }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isError = message.metadata?.error;

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'} ${isError ? 'error-message-bubble' : ''}`}>
      <div className="message-header">
        <span className="message-author">
          {isUser ? 'You' : 'Grace'}
        </span>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>

      <div className="message-content">
        {message.content}
      </div>

      {message.attachments && message.attachments.length > 0 && (
        <div className="message-attachments">
          {message.attachments.map((attachment, idx) => (
            <div key={idx} className="attached-file">
              <span className="file-icon">📎</span>
              <span className="file-name">{attachment.name}</span>
            </div>
          ))}
        </div>
      )}

      {message.metadata?.citations && message.metadata.citations.length > 0 && (
        <div className="message-citations">
          <div className="citations-label">References:</div>
          <div className="citations-list">
            {message.metadata.citations.map((citation: Citation, idx: number) => (
              <button
                key={idx}
                onClick={() => onCitationClick(citation)}
                className={`citation-pill citation-${citation.type}`}
                title={citation.excerpt || citation.title}
              >
                <span className="citation-icon">{getCitationIcon(citation.type)}</span>
                <span className="citation-text">{citation.title}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {message.metadata?.suggestions && message.metadata.suggestions.length > 0 && (
        <div className="message-suggestions">
          <div className="suggestions-label">Suggestions:</div>
          <div className="suggestions-list">
            {message.metadata.suggestions.map((suggestion: string, idx: number) => (
              <button key={idx} className="suggestion-btn">
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {message.metadata?.actions && message.metadata.actions.length > 0 && (
        <div className="message-actions">
          {message.metadata.actions.map((action: any, idx: number) => (
            <button key={idx} className="action-btn-inline">
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function getCitationIcon(type: string): string {
  switch (type) {
    case 'mission': return '🎯';
    case 'kpi': return '📈';
    case 'document': return '📄';
    case 'code': return '💻';
    case 'url': return '🔗';
    default: return '📌';
  }
}
