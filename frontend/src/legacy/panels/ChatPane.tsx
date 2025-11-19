/**
 * Enhanced Chat Pane
 * With model selection and world model/RAG integration
 */

import { useState, useRef, useEffect } from 'react';
import { useChat, useChatAttachments } from '../hooks/useChat';
import { askGrace, queryWorldModel, getAvailableModels } from '../services/worldModelApi';
import type { ChatMessage, Citation } from '../services/chatApi';
import './ChatPane.css';

interface ChatPaneProps {
  onOpenWorkspace?: (citation: Citation) => void;
}

interface Model {
  name: string;
  size: string;
  available: boolean;
  capabilities?: string[];
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
    onError: (error) => console.error('Chat error:', error),
  });

  const { attachments, addAttachment, removeAttachment, clearAttachments } = useChatAttachments();

  const [input, setInput] = useState('');
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [mode, setMode] = useState<'chat' | 'world-model' | 'rag'>('chat');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const data = await getAvailableModels();
        setModels(data.models || []);
      } catch (err) {
        console.warn('Failed to load models:', err);
      }
    };
    loadModels();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() && attachments.length === 0) return;

    const messageText = input;
    const messageAttachments = [...attachments];

    setInput('');
    clearAttachments();

    // Handle special modes
    if (mode === 'world-model' && messageText.startsWith('/ask ')) {
      const question = messageText.substring(5);
      try {
        const result = await askGrace(question);
        // Add as special message type
        console.log('World Model response:', result);
      } catch (err) {
        console.error('World model error:', err);
      }
      return;
    }

    // Regular chat
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

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const quickActions = [
    { text: 'Show me the system status', icon: '📊' },
    { text: '/ask How is the CRM health?', icon: '🧠' },
    { text: 'List all open missions', icon: '🎯' },
    { text: 'What are the recent logs?', icon: '📋' },
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

        <div className="header-controls">
          <div className="mode-selector">
            <button
              className={mode === 'chat' ? 'active' : ''}
              onClick={() => setMode('chat')}
              title="Regular chat"
            >
              💬 Chat
            </button>
            <button
              className={mode === 'world-model' ? 'active' : ''}
              onClick={() => setMode('world-model')}
              title="World model queries (use /ask)"
            >
              🧠 World Model
            </button>
            <button
              className={mode === 'rag' ? 'active' : ''}
              onClick={() => setMode('rag')}
              title="RAG retrieval"
            >
              🔍 RAG
            </button>
          </div>

          {models.length > 0 && (
            <button
              className="model-selector-btn"
              onClick={() => setShowModelSelector(!showModelSelector)}
              title="Select AI model"
            >
              🤖 {selectedModel || 'Default'}
            </button>
          )}

          {!isEmpty && (
            <button onClick={clearMessages} className="clear-btn" title="Clear conversation">
              🗑️
            </button>
          )}
        </div>
      </div>

      {showModelSelector && (
        <div className="model-selector-panel">
          <h4>Select Model</h4>
          <div className="model-list">
            <button
              className={!selectedModel ? 'active' : ''}
              onClick={() => {
                setSelectedModel('');
                setShowModelSelector(false);
              }}
            >
              Default (Auto-select)
            </button>
            {models.map(model => (
              <button
                key={model.name}
                className={selectedModel === model.name ? 'active' : ''}
                onClick={() => {
                  setSelectedModel(model.name);
                  setShowModelSelector(false);
                }}
                disabled={!model.available}
              >
                <span className="model-name">{model.name}</span>
                <span className="model-size">{model.size}</span>
                {!model.available && <span className="model-unavailable">Not loaded</span>}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="messages-container">
        {isEmpty ? (
          <div className="chat-welcome">
            <h3>👋 Welcome to Grace Console</h3>
            <p>Chat mode: <strong>{mode === 'world-model' ? 'World Model' : mode === 'rag' ? 'RAG' : 'Chat'}</strong></p>
            {mode === 'world-model' && (
              <p className="mode-hint">Use <code>/ask &lt;question&gt;</code> for world model queries</p>
            )}
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
              onCitationClick={onOpenWorkspace || (() => {})}
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

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        {attachments.length > 0 && (
          <div className="attachments-preview">
            {attachments.map((file, idx) => (
              <div key={idx} className="attachment-chip">
                <span className="attachment-icon">📎</span>
                <span className="attachment-name">{file.name}</span>
                <span className="attachment-size">({(file.size / 1024).toFixed(1)} KB)</span>
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
            placeholder={
              mode === 'world-model' 
                ? '/ask How is the CRM health?'
                : mode === 'rag'
                ? 'Search knowledge base...'
                : 'Ask Grace anything...'
            }
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

function MessageBubble({ message, onCitationClick, formatTime }: any) {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <span className="message-author">{isUser ? 'You' : 'Grace'}</span>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>

      <div className="message-content">{message.content}</div>

      {message.attachments && message.attachments.length > 0 && (
        <div className="message-attachments">
          {message.attachments.map((attachment: any, idx: number) => (
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
