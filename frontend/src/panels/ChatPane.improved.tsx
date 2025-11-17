/**
 * Improved Chat Pane
 * - Integrated world model/RAG commands (no separate tabs)
 * - Persistent state via context
 * - Structured requests with task_type
 * - Model metadata display
 * - Feedback loop
 */

import { useState, useRef, useEffect } from 'react';
import { useChatContext } from '../context/ChatContext';
import { sendStructuredMessage, type StructuredChatRequest } from '../services/chatApi.enhanced';
import { getAvailableModels, approveModelOutput, type ModelInfo } from '../services/modelsApi';
import type { Citation } from '../services/chatApi';
import './ChatPane.css';

interface ChatPaneProps {
  onOpenWorkspace?: (citation: Citation) => void;
}

const TASK_TYPES = [
  { value: 'general', label: 'General', icon: '💬' },
  { value: 'coding', label: 'Coding', icon: '💻' },
  { value: 'review', label: 'Code Review', icon: '🔍' },
  { value: 'debugging', label: 'Debugging', icon: '🐛' },
  { value: 'reasoning', label: 'Reasoning', icon: '🧠' },
  { value: 'research', label: 'Research', icon: '📚' },
];

export default function ChatPane({ onOpenWorkspace }: ChatPaneProps) {
  const {
    messages,
    loading,
    error: chatError,
    isEmpty,
    clearMessages,
  } = useChatContext();

  const [input, setInput] = useState('');
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('auto');
  const [selectedTaskType, setSelectedTaskType] = useState<string>('general');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadModels = async () => {
      const modelsList = await getAvailableModels();
      setModels(modelsList);
    };
    loadModels();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() && attachments.length === 0) return;

    const request: StructuredChatRequest = {
      message: input,
      task_type: selectedTaskType as any,
      model: selectedModel !== 'auto' ? selectedModel : undefined,
      context: {
        user_interface: 'grace-console',
      },
      attachments,
    };

    setInput('');
    setAttachments([]);

    try {
      await sendStructuredMessage(request);
    } catch (err) {
      console.error('Chat error:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFeedback = async (messageId: string, modelUsed: string, approved: boolean) => {
    try {
      await approveModelOutput(modelUsed, messageId, approved);
      console.log(`Feedback sent: ${approved ? '👍' : '👎'}`);
    } catch (err) {
      console.error('Failed to send feedback:', err);
    }
  };

  const quickCommands = [
    { text: 'Show system status', type: 'general' },
    { text: '/ask How is the CRM health?', type: 'research' },
    { text: '/rag Search for sales documentation', type: 'research' },
    { text: 'Review this code for bugs', type: 'review' },
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
          <select
            value={selectedTaskType}
            onChange={(e) => setSelectedTaskType(e.target.value)}
            className="task-type-select"
            title="Task type helps Grace choose the right model"
          >
            {TASK_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.icon} {type.label}
              </option>
            ))}
          </select>

          {models.length > 0 && (
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="model-select"
              title="Select model (auto = intelligent selection)"
            >
              <option value="auto">🤖 Auto-select</option>
              {models.filter(m => m.available).map(model => (
                <option key={model.name} value={model.name}>
                  {getModelIcon(model.type)} {model.name}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="advanced-btn"
            title="Show advanced options"
          >
            {showAdvanced ? '▼' : '▶'}
          </button>

          {!isEmpty && (
            <button onClick={clearMessages} className="clear-btn" title="Clear conversation">
              🗑️
            </button>
          )}
        </div>
      </div>

      {showAdvanced && (
        <div className="advanced-options">
          <div className="command-help">
            <strong>Commands:</strong>
            <code>/ask &lt;question&gt;</code> - Query world model
            <code>/rag &lt;query&gt;</code> - Search knowledge base
            <code>/world &lt;question&gt;</code> - World model analysis
          </div>
        </div>
      )}

      <div className="messages-container">
        {isEmpty ? (
          <div className="chat-welcome">
            <h3>👋 Welcome to Grace Console</h3>
            <p>Unified AI interface with intelligent model selection</p>
            <div className="feature-hints">
              <div className="hint">💬 Regular chat with auto model selection</div>
              <div className="hint">🧠 Use <code>/ask</code> for world model queries</div>
              <div className="hint">🔍 Use <code>/rag</code> to search knowledge</div>
              <div className="hint">🤖 Select model manually or let Grace choose</div>
            </div>
            <div className="quick-actions">
              {quickCommands.map((cmd, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setInput(cmd.text);
                    setSelectedTaskType(cmd.type);
                  }}
                  className="quick-action-btn"
                >
                  {TASK_TYPES.find(t => t.value === cmd.type)?.icon} {cmd.text}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <EnhancedMessageBubble
              key={message.id}
              message={message}
              onCitationClick={onOpenWorkspace || (() => {})}
              onFeedback={handleFeedback}
            />
          ))
        )}

        {loading && (
          <div className="message assistant-message typing-indicator">
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
                <span>📎 {file.name}</span>
                <button onClick={() => setAttachments(a => a.filter((_, i) => i !== idx))}>
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
            disabled={loading}
          >
            📎
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Grace... (try /ask or /rag commands)"
            className="chat-input"
            disabled={loading}
          />

          <button 
            onClick={handleSend} 
            className="send-btn"
            disabled={loading || (!input.trim() && attachments.length === 0)}
          >
            📤
          </button>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={(e) => {
              if (e.target.files) {
                setAttachments(prev => [...prev, ...Array.from(e.target.files!)]);
              }
            }}
            style={{ display: 'none' }}
          />
        </div>
      </div>
    </div>
  );
}

function EnhancedMessageBubble({ message, onCitationClick, onFeedback }: any) {
  const [feedbackGiven, setFeedbackGiven] = useState(false);

  const handleFeedback = (approved: boolean) => {
    if (message.metadata?.model_used && message.id) {
      onFeedback(message.id, message.metadata.model_used, approved);
      setFeedbackGiven(true);
    }
  };

  return (
    <div className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <span className="message-author">{message.role === 'user' ? 'You' : 'Grace'}</span>
        {message.metadata?.model_used && (
          <span className="model-badge" title="Model used for this response">
            🤖 {message.metadata.model_used}
          </span>
        )}
        <span className="message-time">
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
      </div>

      <div className="message-content">{message.content}</div>

      {message.metadata?.reasoning_steps && (
        <details className="reasoning-steps">
          <summary>🧠 Reasoning Steps</summary>
          <ol>
            {message.metadata.reasoning_steps.map((step: string, idx: number) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </details>
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
              >
                {getCitationIcon(citation.type)} {citation.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {message.role === 'assistant' && message.metadata?.model_used && !feedbackGiven && (
        <div className="message-feedback">
          <span className="feedback-label">Was this helpful?</span>
          <button
            onClick={() => handleFeedback(true)}
            className="feedback-btn thumbs-up"
            title="Good response - helps Grace learn"
          >
            👍
          </button>
          <button
            onClick={() => handleFeedback(false)}
            className="feedback-btn thumbs-down"
            title="Poor response - helps Grace improve"
          >
            👎
          </button>
        </div>
      )}
    </div>
  );
}

function getModelIcon(type: string): string {
  const icons: Record<string, string> = {
    coding: '💻',
    reasoning: '🧠',
    'long-context': '📄',
    vision: '👁️',
    general: '🤖',
  };
  return icons[type] || '🤖';
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
