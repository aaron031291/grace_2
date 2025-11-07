import { useState, useEffect, useRef } from 'react';
import './AppModern.css';

// Import actual components (lazy loaded to avoid import errors)
import { setAuthToken } from './api/client';

// Domain configuration - components loaded on demand
const DOMAINS = [
  { id: 'chat', name: 'Chat', icon: '💬', desc: 'Talk with Grace AI', component: null },
  { id: 'knowledge', name: 'Knowledge', icon: '📚', desc: 'Ingest & search knowledge (coming soon)', component: null },
  { id: 'security', name: 'Security', icon: '🛡️', desc: 'Hunter threat detection (coming soon)', component: null },
  { id: 'metaloop', name: 'Meta Loop', icon: '🧠', desc: 'Governance & optimization (coming soon)', component: null },
  { id: 'transcendence', name: 'Transcendence', icon: '💻', desc: 'Agentic development (coming soon)', component: null },
  { id: 'memory', name: 'Memory', icon: '📁', desc: 'Browse agentic memory (coming soon)', component: null },
  { id: 'approvals', name: 'Approvals', icon: '✅', desc: 'Constitutional AI (coming soon)', component: null },
  { id: 'health', name: 'Health', icon: '❤️', desc: 'System monitoring (coming soon)', component: null },
  { id: 'tasks', name: 'Tasks', icon: '📋', desc: 'Task management (coming soon)', component: null },
  { id: 'metrics', name: 'Metrics', icon: '📊', desc: 'Analytics dashboard (coming soon)', component: null },
];

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: Date;
}

export default function GraceModern() {
  const [domain, setDomain] = useState('chat');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I\'m Grace, your autonomous AI assistant. I can help with code, knowledge management, security monitoring, and more. What would you like to do today?', timestamp: new Date() }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('grace_token') || '');
  const [isRecording, setIsRecording] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Set auth token on mount
  useEffect(() => {
    if (token) {
      setAuthToken(token);
    }
  }, [token]);

  // Send chat message
  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date() }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message: userMsg })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response || data.message || 'I received your message!',
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: `⚠️ Error: ${error instanceof Error ? error.message : 'Could not connect to backend'}. Make sure the backend is running at http://localhost:8000`,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // File upload handler
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: `📎 Uploading: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`,
      timestamp: new Date()
    }]);
    setIsLoading(true);

    try {
      // For text files, read and ingest
      if (file.type.startsWith('text/') || file.name.endsWith('.md') || file.name.endsWith('.txt')) {
        const text = await file.text();
        const response = await fetch('http://localhost:8000/api/ingest/text', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify({ 
            content: text, 
            title: file.name,
            artifact_type: 'document',
            domain: 'general'
          })
        });
        
        const data = await response.json();
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `✅ Successfully ingested "${file.name}" into knowledge base! Artifact ID: ${data.artifact_id || 'unknown'}`,
          timestamp: new Date()
        }]);
      } else if (file.type.startsWith('image/')) {
        // For images, show preview (actual upload would need FormData)
        const reader = new FileReader();
        reader.onload = (e) => {
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: `📷 Image received: ${file.name}. (Image processing coming soon!)`,
            timestamp: new Date()
          }]);
        };
        reader.readAsDataURL(file);
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `📁 File received: ${file.name}. Processing for this file type is being implemented.`,
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: `❌ Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Voice recording handler
  const toggleVoiceRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: '🎤 Voice recording stopped. (Speech-to-text integration coming soon!)',
        timestamp: new Date()
      }]);
    } else {
      setIsRecording(true);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: '🎤 Recording... (Speech recognition will be integrated with backend)',
        timestamp: new Date()
      }]);
    }
  };

  // New conversation
  const startNewConversation = () => {
    setMessages([
      { role: 'assistant', content: 'New conversation started! How can I help you?', timestamp: new Date() }
    ]);
  };

  // Get current domain info
  const currentDomain = DOMAINS.find(d => d.id === domain);

  // Handle non-chat domains with placeholder
  if (domain !== 'chat') {
    return (
      <div className="app-modern">
        <aside className="sidebar">
          <div className="sidebar-header">
            <h1 className="logo">Grace AI</h1>
            <p className="tagline">Autonomous Intelligence</p>
          </div>

          <nav className="domain-nav">
            {DOMAINS.map(d => (
              <button
                key={d.id}
                className={`domain-btn ${domain === d.id ? 'active' : ''}`}
                onClick={() => setDomain(d.id)}
                title={d.desc}
              >
                <span className="domain-icon">{d.icon}</span>
                <span className="domain-name">{d.name}</span>
              </button>
            ))}
          </nav>

          <div className="sidebar-footer">
            <div className="status-indicator">
              <div className="status-dot"></div>
              <span>All Systems Online</span>
            </div>
            <button className="settings-btn" onClick={() => setDomain('chat')}>
              💬 Back to Chat
            </button>
          </div>
        </aside>

        <main className="main-content" style={{ overflow: 'auto', padding: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', maxWidth: '600px' }}>
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>{currentDomain?.icon}</div>
            <h1 style={{ fontSize: '32px', marginBottom: '12px', color: '#e0e0e0' }}>
              {currentDomain?.name}
            </h1>
            <p style={{ fontSize: '16px', color: '#888', marginBottom: '30px' }}>
              {currentDomain?.desc}
            </p>
            <div style={{ 
              background: 'rgba(102, 126, 234, 0.1)', 
              border: '1px solid rgba(102, 126, 234, 0.3)',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '20px'
            }}>
              <p style={{ color: '#b0b0b0', fontSize: '14px' }}>
                🚧 This domain interface is being integrated. 
                In the meantime, you can interact with this domain through the Chat interface.
              </p>
            </div>
            <button 
              onClick={() => setDomain('chat')}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#fff',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                fontSize: '14px',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              💬 Go to Chat
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Render chat interface
  return (
    <div className="app-modern">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1 className="logo">Grace AI</h1>
          <p className="tagline">Autonomous Intelligence</p>
        </div>

        <nav className="domain-nav">
          {DOMAINS.map(d => (
            <button
              key={d.id}
              className={`domain-btn ${domain === d.id ? 'active' : ''}`}
              onClick={() => setDomain(d.id)}
              title={d.desc}
            >
              <span className="domain-icon">{d.icon}</span>
              <span className="domain-name">{d.name}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>All Systems Online</span>
          </div>
          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            rel="noopener noreferrer"
            className="settings-btn"
            style={{ textAlign: 'center', display: 'block', textDecoration: 'none' }}
          >
            📖 API Docs
          </a>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="content-header">
          <div className="current-domain">
            <span className="domain-icon-large">{currentDomain?.icon}</span>
            <div>
              <h2>{currentDomain?.name}</h2>
              <p className="domain-desc">{currentDomain?.desc}</p>
            </div>
          </div>
          <div className="header-actions">
            <button className="icon-btn" title="New conversation" onClick={startNewConversation}>
              ➕
            </button>
            <button className="icon-btn" title="History">📜</button>
            <button className="icon-btn" title="Share">🔗</button>
          </div>
        </header>

        {/* Messages Area */}
        <div className="messages-container">
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : msg.role === 'system' ? '⚙️' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                  {msg.timestamp && (
                    <div className="message-time">
                      {msg.timestamp.toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="input-container">
          <form onSubmit={sendMessage} className="input-form">
            <div className="input-wrapper">
              {/* Multimodal Input Buttons */}
              <div className="input-actions-left">
                <label className="icon-btn" title="Upload file (text, PDF, images)">
                  📎
                  <input 
                    ref={fileInputRef}
                    type="file" 
                    hidden 
                    onChange={handleFileUpload}
                    accept="image/*,.pdf,.txt,.md,.json,.py,.js,.ts,.tsx"
                  />
                </label>
                <button 
                  type="button" 
                  className={`icon-btn ${isRecording ? 'recording' : ''}`}
                  title="Voice input" 
                  onClick={toggleVoiceRecording}
                >
                  {isRecording ? '🔴' : '🎤'}
                </button>
                <button type="button" className="icon-btn" title="Image generation">🖼️</button>
              </div>

              {/* Text Input */}
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Message Grace..."
                className="message-input"
                disabled={isLoading}
              />

              {/* Send Button */}
              <button 
                type="submit" 
                className="send-btn"
                disabled={!input.trim() || isLoading}
              >
                {isLoading ? '⏳' : '🚀'}
              </button>
            </div>
          </form>
          
          <p className="input-hint">
            Grace can help with code, knowledge ingestion, security, governance, and more. 
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
              View API Docs
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}
