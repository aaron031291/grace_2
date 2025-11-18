import { useState } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import type { ExecutionTrace } from '../GraceEnterpriseUI';
import './ChatView.css';

interface Message {
  id: string;
  role: 'user' | 'grace';
  content: string;
  timestamp: Date;
  execution_trace?: ExecutionTrace;
}

interface ChatViewProps {
  onShowTrace: (trace: ExecutionTrace) => void;
}

export function ChatView({ onShowTrace }: ChatViewProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(apiUrl('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();

      const graceMessage: Message = {
        id: `msg-${Date.now()}-grace`,
        role: 'grace',
        content: data.response || 'I received your message!',
        timestamp: new Date(),
        execution_trace: data.execution_trace,
      };

      setMessages(prev => [...prev, graceMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now()}-error`,
        role: 'grace',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-view">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">🧠</div>
            <h2>Welcome to Grace</h2>
            <p>I'm your autonomous AI assistant. How can I help you today?</p>
            <div className="chat-suggestions">
              <button className="suggestion-btn" onClick={() => setInput('Show me system health')}>
                Show me system health
              </button>
              <button className="suggestion-btn" onClick={() => setInput('What are my pending approvals?')}>
                What are my pending approvals?
              </button>
              <button className="suggestion-btn" onClick={() => setInput('Run a network scan')}>
                Run a network scan
              </button>
            </div>
          </div>
        ) : (
          <div className="chat-messages-list">
            {messages.map((message) => (
              <div key={message.id} className={`chat-message chat-message-${message.role}`}>
                <div className="message-avatar">
                  {message.role === 'user' ? '👤' : '🧠'}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  {message.execution_trace && (
                    <button
                      className="message-trace-btn"
                      onClick={() => onShowTrace(message.execution_trace!)}
                    >
                      <span className="trace-btn-icon">🔍</span>
                      <span className="trace-btn-text">Why/How</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chat-message chat-message-grace">
                <div className="message-avatar">🧠</div>
                <div className="message-content">
                  <div className="message-loading">
                    <span className="loading-dot"></span>
                    <span className="loading-dot"></span>
                    <span className="loading-dot"></span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <div className="chat-input-container">
          <textarea
            className="chat-input"
            placeholder="Message Grace..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <div className="chat-input-actions">
            <button className="chat-input-btn" title="Attach file">
              📎
            </button>
            <button className="chat-input-btn" title="Voice input">
              🎤
            </button>
            <button
              className="chat-send-btn"
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
            >
              ↑
            </button>
          </div>
        </div>
        <div className="chat-input-hint">
          Press <kbd>Ctrl</kbd>+<kbd>Enter</kbd> to send
        </div>
      </div>
    </div>
  );
}
