import { useState, useEffect, useRef } from 'react';
import './GraceAgentic.css';
import { setAuthToken } from './api/client';

const DOMAINS = [
  { id: 'all', name: 'All Domains', icon: '🌐', color: '#667eea' },
  { id: 'chat', name: 'Chat', icon: '💬', color: '#667eea' },
  { id: 'self_heal', name: 'Self-Heal', icon: '🔧', color: '#00ff88' },
  { id: 'meta_loop', name: 'Meta Loop', icon: '🧠', color: '#764ba2' },
  { id: 'knowledge', name: 'Knowledge', icon: '📚', color: '#f093fb' },
  { id: 'security', name: 'Security', icon: '🛡️', color: '#ff6b6b' },
  { id: 'transcendence', name: 'Code Agent', icon: '💻', color: '#00d4ff' },
  { id: 'parliament', name: 'Parliament', icon: '⚖️', color: '#ffd700' },
  { id: 'resource', name: 'Resources', icon: '📊', color: '#ff9500' },
  { id: 'core', name: 'Core', icon: '⚡', color: '#667eea' },
];

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'event' | 'playbook' | 'metric';
  content: string;
  domain?: string;
  timestamp: Date;
  metadata?: any;
}

export default function GraceAgentic() {
  const [activeDomain, setActiveDomain] = useState('all');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [showOperationsFeed, setShowOperationsFeed] = useState(true);
  const [showContextViewer, setShowContextViewer] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [autonomyLevel, setAutonomyLevel] = useState(75);
  const [guardrailsActive, setGuardrailsActive] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
      initializeWebSocket(token);
    }
  }, []);

  const initializeWebSocket = (token: string) => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/cognition?token=${token}`);
    
    websocket.onopen = () => {
      addSystemMessage('🟢 Connected to Grace event stream', 'core');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketEvent(data);
      } catch (e) {
        console.error('WS parse error:', e);
      }
    };

    websocket.onerror = () => {
      addSystemMessage('⚠️ Event stream disconnected', 'core');
    };

    setWs(websocket);
  };

  const handleWebSocketEvent = (data: any) => {
    const msg: Message = {
      id: `evt_${Date.now()}_${Math.random()}`,
      type: 'event',
      content: data.message || data.event || 'Event received',
      domain: data.domain || data.subsystem || 'core',
      timestamp: new Date(),
      metadata: data
    };

    if (data.event_type === 'meta_loop_cycle') {
      msg.type = 'playbook';
      msg.content = `Meta Loop Cycle ${data.cycle_number || 'N/A'}: ${data.summary || 'Running'}`;
    } else if (data.event_type === 'resource_scaled') {
      msg.content = `Resource ${data.action}: ${data.resource} (${data.old_value} → ${data.new_value})`;
    } else if (data.event_type === 'playbook_executed') {
      msg.type = 'playbook';
      msg.content = `Playbook executed: ${data.playbook_name} - ${data.status}`;
    }

    setMessages(prev => [...prev, msg]);
  };

  const addSystemMessage = (content: string, domain: string = 'core') => {
    setMessages(prev => [...prev, {
      id: `sys_${Date.now()}`,
      type: 'system',
      content,
      domain,
      timestamp: new Date()
    }]);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('grace_token', data.access_token);
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        initializeWebSocket(data.access_token);
        addSystemMessage(`✅ Authenticated as ${username}`, 'core');
      } else {
        const error = await response.json();
        alert(error.detail || 'Login failed');
      }
    } catch (error) {
      alert('Backend offline - Make sure uvicorn is running on port 8000');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('grace_token', data.access_token);
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        initializeWebSocket(data.access_token);
        addSystemMessage(`✅ Account created: ${username}`, 'core');
      } else {
        alert('Registration failed');
      }
    } catch (error) {
      alert('Backend offline');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    
    // Handle slash commands
    if (userMsg.startsWith('/')) {
      handleSlashCommand(userMsg);
      setInput('');
      return;
    }

    setInput('');
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: userMsg,
      domain: activeDomain === 'all' ? 'chat' : activeDomain,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const token = localStorage.getItem('grace_token');
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message: userMsg })
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, {
        id: `assistant_${Date.now()}`,
        type: 'assistant',
        content: data.response || 'Received!',
        domain: activeDomain === 'all' ? 'chat' : activeDomain,
        timestamp: new Date()
      }]);
    } catch (error) {
      addSystemMessage('❌ Backend error', 'core');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSlashCommand = async (cmd: string) => {
    const parts = cmd.slice(1).split(' ');
    const command = parts[0];
    const args = parts.slice(1);

    addSystemMessage(`⚡ Executing: ${cmd}`, 'core');

    const token = localStorage.getItem('grace_token');
    const headers = { ...(token ? { 'Authorization': `Bearer ${token}` } : {}) };

    try {
      if (command === 'status' || command === 'health') {
        const res = await fetch('http://localhost:8000/health', { headers });
        const data = await res.json();
        addSystemMessage(`✅ Status: ${JSON.stringify(data, null, 2)}`, 'core');
      } else if (command === 'meta') {
        const res = await fetch('http://localhost:8000/api/meta/focus', { headers });
        const data = await res.json();
        addSystemMessage(`🧠 Meta Focus: ${JSON.stringify(data, null, 2)}`, 'meta_loop');
      } else if (command === 'playbook') {
        addSystemMessage('📋 Playbook command received. Integration pending.', 'self_heal');
      } else if (command === 'forecast') {
        addSystemMessage('📈 Forecast requested. Temporal reasoning integration pending.', 'core');
      } else if (command === 'memory') {
        const query = args.join(' ');
        addSystemMessage(`🔍 Searching memory for: "${query}"`, 'core');
      } else {
        addSystemMessage(`❓ Unknown command: /${command}. Try: /status, /meta, /playbook, /forecast, /memory`, 'core');
      }
    } catch (error) {
      addSystemMessage(`❌ Command failed: ${command}`, 'core');
    }
  };

  const filteredMessages = activeDomain === 'all' 
    ? messages 
    : messages.filter(m => m.domain === activeDomain);

  if (!isLoggedIn) {
    return (
      <div className="grace-agentic login-screen">
        <div className="login-card">
          <div className="login-header">
            <h1 className="logo-large">Grace AI</h1>
            <p className="tagline-large">Autonomous Intelligence Platform</p>
          </div>
          <form onSubmit={handleLogin}>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" className="login-input" />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="login-input" />
            <button type="submit" className="login-btn" disabled={isLoading}>{isLoading ? '⏳ Logging in...' : '🚀 Login'}</button>
            <button type="button" onClick={handleRegister} className="register-btn" disabled={isLoading}>✨ Register</button>
          </form>
          <p className="login-hint">Default: admin / admin123</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grace-agentic">
      {/* Left Sidebar - Domain Filter */}
      <aside className="domain-sidebar">
        <div className="sidebar-header">
          <h1 className="logo">Grace</h1>
          <div className="autonomy-indicator">
            <div className="autonomy-bar">
              <div className="autonomy-fill" style={{ width: `${autonomyLevel}%` }}></div>
            </div>
            <span className="autonomy-label">{autonomyLevel}% Autonomous</span>
          </div>
        </div>

        <div className="domain-filters">
          <div className="filter-label">Filter by Domain:</div>
          {DOMAINS.map(d => (
            <button
              key={d.id}
              className={`domain-filter ${activeDomain === d.id ? 'active' : ''}`}
              onClick={() => setActiveDomain(d.id)}
              style={{ '--domain-color': d.color } as any}
            >
              <span className="domain-icon">{d.icon}</span>
              <span className="domain-name">{d.name}</span>
              <span className="message-count">
                {messages.filter(m => d.id === 'all' || m.domain === d.id).length}
              </span>
            </button>
          ))}
        </div>

        <div className="sidebar-controls">
          <div className="guardrails-toggle">
            <label>
              <input type="checkbox" checked={guardrailsActive} onChange={() => setGuardrailsActive(!guardrailsActive)} />
              <span>🛡️ Guardrails {guardrailsActive ? 'ON' : 'OFF'}</span>
            </label>
          </div>
          <button className="btn-secondary" onClick={() => setShowContextViewer(!showContextViewer)}>
            🧠 {showContextViewer ? 'Hide' : 'Show'} Context
          </button>
          <button className="btn-secondary" onClick={() => setShowOperationsFeed(!showOperationsFeed)}>
            📡 {showOperationsFeed ? 'Hide' : 'Show'} Feed
          </button>
          <button className="btn-logout" onClick={() => { localStorage.clear(); setIsLoggedIn(false); }}>
            🚪 Logout
          </button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="main-chat">
        <header className="chat-header">
          <div className="current-filter">
            <span className="filter-icon" style={{ color: DOMAINS.find(d => d.id === activeDomain)?.color }}>
              {DOMAINS.find(d => d.id === activeDomain)?.icon}
            </span>
            <div>
              <h2>{DOMAINS.find(d => d.id === activeDomain)?.name}</h2>
              <p className="filter-desc">{filteredMessages.length} messages</p>
            </div>
          </div>
          <div className="header-actions">
            <button className="icon-btn" title="Clear conversation" onClick={() => setMessages([])}>🗑️</button>
            <button className="icon-btn" title="Export logs">📥</button>
            <a href="http://localhost:8000/docs" target="_blank" className="icon-btn" title="API Docs">📖</a>
          </div>
        </header>

        <div className="messages-area">
          {filteredMessages.map(msg => (
            <div key={msg.id} className={`message-card ${msg.type}`} data-domain={msg.domain}>
              <div className="message-meta">
                <span className="message-type-badge" style={{ background: DOMAINS.find(d => d.id === msg.domain)?.color || '#666' }}>
                  {DOMAINS.find(d => d.id === msg.domain)?.icon} {msg.domain}
                </span>
                <span className="message-time">{msg.timestamp.toLocaleTimeString()}</span>
              </div>
              
              <div className="message-body">
                {msg.type === 'user' && <div className="message-avatar">👤</div>}
                {msg.type === 'assistant' && <div className="message-avatar">🤖</div>}
                {msg.type === 'system' && <div className="message-avatar">⚙️</div>}
                {msg.type === 'event' && <div className="message-avatar">📡</div>}
                {msg.type === 'playbook' && <div className="message-avatar">📋</div>}
                {msg.type === 'metric' && <div className="message-avatar">📊</div>}
                
                <div className="message-content">
                  <pre className="message-text">{msg.content}</pre>
                  
                  {msg.metadata && (
                    <details className="metadata-details">
                      <summary>🔍 View Details</summary>
                      <pre>{JSON.stringify(msg.metadata, null, 2)}</pre>
                    </details>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-card assistant">
              <div className="message-body">
                <div className="message-avatar">🤖</div>
                <div className="typing-indicator"><span></span><span></span><span></span></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="slash-commands-hint">
            Try: <code>/status</code> <code>/meta</code> <code>/playbook</code> <code>/forecast</code> <code>/memory [query]</code>
          </div>
          <form onSubmit={sendMessage} className="input-form">
            <div className="input-row">
              <button type="button" className="input-btn" title="Attach file">📎</button>
              <button type="button" className="input-btn" title="Voice">🎤</button>
              <button type="button" className="input-btn" title="Image">🖼️</button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Message Grace (${activeDomain})... or use /commands`}
                className="chat-input"
                disabled={isLoading}
              />
              <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
                {isLoading ? '⏳' : '🚀'}
              </button>
            </div>
          </form>
        </div>
      </main>

      {/* Right Sidebar - Operations Feed & Context */}
      {(showOperationsFeed || showContextViewer) && (
        <aside className="operations-sidebar">
          {showContextViewer && (
            <div className="context-viewer">
              <h3>🧠 Context Viewer</h3>
              <div className="context-items">
                <div className="context-item">
                  <span className="context-label">Memory Loaded:</span>
                  <span className="context-value">12 patterns</span>
                </div>
                <div className="context-item">
                  <span className="context-label">Active Shards:</span>
                  <span className="context-value">3 domains</span>
                </div>
                <div className="context-item">
                  <span className="context-label">Causal Graph:</span>
                  <span className="context-value">0 nodes</span>
                </div>
              </div>
            </div>
          )}

          {showOperationsFeed && (
            <div className="operations-feed">
              <h3>📡 Live Operations</h3>
              <div className="feed-items">
                <div className="feed-item">
                  <span className="feed-icon">🔧</span>
                  <div className="feed-content">
                    <div className="feed-title">Self-Heal Scheduler</div>
                    <div className="feed-desc">Running • 30s interval</div>
                  </div>
                </div>
                <div className="feed-item">
                  <span className="feed-icon">🧠</span>
                  <div className="feed-content">
                    <div className="feed-title">Meta Loop</div>
                    <div className="feed-desc">Cycle every 2min</div>
                  </div>
                </div>
                <div className="feed-item">
                  <span className="feed-icon">📊</span>
                  <div className="feed-content">
                    <div className="feed-title">Resource Steward</div>
                    <div className="feed-desc">Monitoring capacity</div>
                  </div>
                </div>
                <div className="feed-item">
                  <span className="feed-icon">⚖️</span>
                  <div className="feed-content">
                    <div className="feed-title">Ethics Sentinel</div>
                    <div className="feed-desc">Active • {guardrailsActive ? 'Enforcing' : 'Observing'}</div>
                  </div>
                </div>
              </div>

              <div className="system-status">
                <div className="status-row">
                  <span>Autonomy Level:</span>
                  <span className="status-value">{autonomyLevel}%</span>
                </div>
                <div className="status-row">
                  <span>Guardrails:</span>
                  <span className="status-value">{guardrailsActive ? '🟢 Active' : '🟡 Passive'}</span>
                </div>
                <div className="status-row">
                  <span>WebSocket:</span>
                  <span className="status-value">{ws?.readyState === 1 ? '🟢 Connected' : '🔴 Offline'}</span>
                </div>
              </div>
            </div>
          )}
        </aside>
      )}
    </div>
  );
}
