import { useState, useEffect, useRef } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import './GraceAgentic.css';
import { setAuthToken } from './api/client';

const DOMAINS = [
  { id: 'all', name: 'All', icon: '🌐', color: '#667eea' },
  { id: 'chat', name: 'Chat', icon: '💬', color: '#667eea' },
  { id: 'self_heal', name: 'Self-Heal', icon: '🔧', color: '#00ff88' },
  { id: 'meta_loop', name: 'Meta Loop', icon: '🧠', color: '#764ba2' },
  { id: 'knowledge', name: 'Knowledge', icon: '📚', color: '#f093fb' },
  { id: 'security', name: 'Security', icon: '🛡️', color: '#ff6b6b' },
  { id: 'transcendence', name: 'Code', icon: '💻', color: '#00d4ff' },
  { id: 'resource', name: 'Resources', icon: '📊', color: '#ff9500' },
  { id: 'core', name: 'Core', icon: '⚡', color: '#ffd700' },
];

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'notification' | 'question' | 'idea' | 'consensus_request' | 'subagent';
  content: string;
  domain: string;
  from?: string;
  timestamp: Date;
  requires_response?: boolean;
  metadata?: any;
  options?: string[];
}

interface Subagent {
  task_id: string;
  agent_type: string;
  task: string;
  domain: string;
  status: string;
  progress: number;
}

export default function GraceBidirectional() {
  const [activeDomain, setActiveDomain] = useState('all');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [subagents, setSubagents] = useState<Subagent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [proactiveWs, setProactiveWs] = useState<WebSocket | null>(null);
  const [subagentWs, setSubagentWs] = useState<WebSocket | null>(null);
  const [showSubagents, setShowSubagents] = useState(true);
  const [notificationCount, setNotificationCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
      initializeConnections(token);
    }
  }, []);

  const initializeConnections = (token: string) => {
    // Proactive messaging WebSocket
    const proactive = new WebSocket(`${WS_BASE_URL}/api/proactive/ws?token=${token}`);
    
    proactive.onopen = () => {
      addMessage({
        id: 'sys_conn',
        type: 'assistant',
        content: '🟢 Connected to Grace. I can now reach out to you proactively!',
        domain: 'core',
        from: 'grace',
        timestamp: new Date()
      });
    };

    proactive.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleProactiveMessage(data);
    };

    setProactiveWs(proactive);

    // Subagent monitoring WebSocket
    const subagent = new WebSocket(`${WS_BASE_URL}/api/subagents/ws?token=${token}`);
    
    subagent.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'subagent_status' && data.agents) {
        setSubagents(Object.values(data.agents));
      } else if (data.type === 'subagent_spawned') {
        addMessage({
          id: `subagent_${Date.now()}`,
          type: 'subagent',
          content: `🤖 Spawned ${data.agent.agent_type} for: ${data.agent.task}`,
          domain: data.agent.domain,
          timestamp: new Date(),
          metadata: data.agent
        });
        playNotificationSound();
      } else if (data.type === 'subagent_completed') {
        addMessage({
          id: `subagent_done_${Date.now()}`,
          type: 'subagent',
          content: `✅ Subagent completed: ${data.task_id}`,
          domain: 'core',
          timestamp: new Date()
        });
      }
    };

    setSubagentWs(subagent);
  };

  const handleProactiveMessage = (data: any) => {
    const msg: Message = {
      id: `grace_${Date.now()}`,
      type: data.type || 'notification',
      content: data.content,
      domain: data.domain || 'core',
      from: 'grace',
      timestamp: new Date(data.timestamp),
      requires_response: data.requires_response,
      metadata: data.context || data.rationale,
      options: data.options
    };

    setMessages(prev => [...prev, msg]);
    
    // Play notification sound
    if (data.type !== 'system') {
      playNotificationSound();
      setNotificationCount(prev => prev + 1);
      
      // Browser notification
      if (Notification.permission === 'granted') {
        new Notification('Grace AI', {
          body: data.content.substring(0, 100),
          icon: '/vite.svg'
        });
      }
    }
  };

  const playNotificationSound = () => {
    if (audioRef.current) {
      audioRef.current.play().catch(() => {});
    }
  };

  const addMessage = (msg: Message) => {
    setMessages(prev => [...prev, msg]);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch(apiUrl('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('grace_token', data.access_token);
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        initializeConnections(data.access_token);
        
        // Request notification permission
        if (Notification.permission === 'default') {
          Notification.requestPermission();
        }
      } else {
        alert('Login failed');
      }
    } catch (error) {
      alert('Backend offline');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(apiUrl('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('grace_token', data.access_token);
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        initializeConnections(data.access_token);
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
    setInput('');
    
    addMessage({
      id: `user_${Date.now()}`,
      type: 'user',
      content: userMsg,
      domain: activeDomain === 'all' ? 'chat' : activeDomain,
      timestamp: new Date()
    });
    
    setIsLoading(true);

    // Hardening: AbortController for network timeout
    const abortController = new AbortController();
    const timeoutId = setTimeout(() => abortController.abort(), 30000); // 30s timeout

    try {
      const token = localStorage.getItem('grace_token');
      const response = await fetch(apiUrl('/api/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message: userMsg }),
        signal: abortController.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      addMessage({
        id: `assistant_${Date.now()}`,
        type: 'assistant',
        content: data.response || 'Received!',
        domain: activeDomain === 'all' ? 'chat' : activeDomain,
        from: 'grace',
        timestamp: new Date()
      });
    } catch (error) {
      clearTimeout(timeoutId);
      
      let errorMessage = '❌ Backend error';
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = '⏱️ Request timed out. Please try again.';
        } else {
          errorMessage = `❌ Error: ${error.message}`;
        }
      }
      
      addMessage({
        id: `error_${Date.now()}`,
        type: 'notification',
        content: errorMessage,
        domain: 'core',
        timestamp: new Date()
      });
    } finally {
      setIsLoading(false);
    }
  };

  const respondToGrace = async (originalMsgId: string, response: string) => {
    // Send response back to Grace via WebSocket
    if (proactiveWs && proactiveWs.readyState === 1) {
      proactiveWs.send(JSON.stringify({
        type: 'response',
        original_id: originalMsgId,
        content: response,
        timestamp: new Date().isoformat()
      }));
    }
    
    addMessage({
      id: `user_response_${Date.now()}`,
      type: 'user',
      content: response,
      domain: 'chat',
      timestamp: new Date()
    });
  };

  const filteredMessages = activeDomain === 'all' 
    ? messages 
    : messages.filter(m => m.domain === activeDomain);

  const runningSubagents = subagents.filter(s => s.status === 'running').length;

  if (!isLoggedIn) {
    return (
      <div className="grace-agentic login-screen">
        <div className="login-card">
          <div className="login-header">
            <h1 className="logo-large">Grace AI</h1>
            <p className="tagline-large">Bidirectional Autonomous Intelligence</p>
          </div>
          <form onSubmit={handleLogin}>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" className="login-input" />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="login-input" />
            <button type="submit" className="login-btn" disabled={isLoading}>{isLoading ? '⏳' : '🚀 Login'}</button>
            <button type="button" onClick={handleRegister} className="register-btn" disabled={isLoading}>✨ Register</button>
          </form>
          <p className="login-hint">Default: admin / admin123</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grace-agentic">
      <audio ref={audioRef} src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIGGi78OScTgwOUKfk77RgGwU7k9n1xnMpBSh+zPLaizsKGGS36+mhUhELTKXh8bllHAU2jdXzzn0vBSl+zPDZizwLGGS36ueaUBEMTKXh8LhlHQU2jdXy0H4wBSh+zPDYizwLF2S25+mhUBEMTKXh77dmHQU3jdXy0H4wBSh9y/DYizwLF2S25+mgUBEMTKXh77dmHQU3jdXy0H4wBSh9y/DYizwLF2S25+mgUBEMTKXh77dmHQU3jdXy0H4wBSh9y/DYizwLF2S25+mgUBEMTKXh77dmHQU3jdXy0H4wBSh9y/DYizwLF2S25+mgUBEMTKXh77dmHQU3jdXy0H4wBSh9y/DYizwLF2S25+mgUBEMTKXh77dmHQU3jdXy0H4wBSh9y/DYizwLF2S25+mgUBEMTKXh77dmHQU3jdXy0H4wBSh9y/DYizwLF2S25+mgUBEMTKXh77dmHQU3jdXy0H4w" />
      
      <aside className="domain-sidebar">
        <div className="sidebar-header">
          <h1 className="logo">Grace AI</h1>
          <p style={{ fontSize: '11px', color: '#888', marginTop: '5px' }}>🔄 Bidirectional Mode</p>
        </div>

        <div className="domain-filters">
          <div className="filter-label">Domains</div>
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
          <div className="connection-status">
            <div style={{fontSize: '11px', color: '#666', marginBottom: '8px'}}>Connections:</div>
            <div style={{fontSize: '11px', display: 'flex', justifyContent: 'space-between', marginBottom: '4px'}}>
              <span>Proactive:</span>
              <span style={{color: proactiveWs?.readyState === 1 ? '#00ff88' : '#ff6b6b'}}>
                {proactiveWs?.readyState === 1 ? '🟢 Live' : '🔴 Off'}
              </span>
            </div>
            <div style={{fontSize: '11px', display: 'flex', justifyContent: 'space-between'}}>
              <span>Subagents:</span>
              <span style={{color: subagentWs?.readyState === 1 ? '#00ff88' : '#ff6b6b'}}>
                {subagentWs?.readyState === 1 ? '🟢 Live' : '🔴 Off'}
              </span>
            </div>
          </div>
          
          <button className="btn-secondary" onClick={() => setShowSubagents(!showSubagents)}>
            {showSubagents ? '🤖 Hide' : '🤖 Show'} Subagents ({runningSubagents})
          </button>
          
          <button className="btn-logout" onClick={() => { localStorage.clear(); setIsLoggedIn(false); }}>
            🚪 Logout
          </button>
        </div>
      </aside>

      <main className="main-chat">
        <header className="chat-header">
          <div className="current-filter">
            <span className="filter-icon" style={{ color: DOMAINS.find(d => d.id === activeDomain)?.color }}>
              {DOMAINS.find(d => d.id === activeDomain)?.icon}
            </span>
            <div>
              <h2>{DOMAINS.find(d => d.id === activeDomain)?.name}</h2>
              <p className="filter-desc">{filteredMessages.length} messages • {runningSubagents} subagents active</p>
            </div>
          </div>
          <div className="header-actions">
            {notificationCount > 0 && (
              <div className="notification-badge">{notificationCount}</div>
            )}
            <button className="icon-btn" onClick={() => { setMessages([]); setNotificationCount(0); }}>🗑️</button>
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
                <div className="message-avatar">
                  {msg.from === 'grace' ? '🤖' : msg.type === 'user' ? '👤' : msg.type === 'subagent' ? '⚙️' : '📡'}
                </div>
                
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                  
                  {msg.requires_response && (
                    <div className="response-actions">
                      <button 
                        className="quick-response-btn approve"
                        onClick={() => respondToGrace(msg.id, 'Yes, proceed')}
                      >
                        ✅ Approve
                      </button>
                      <button 
                        className="quick-response-btn deny"
                        onClick={() => respondToGrace(msg.id, 'No, skip this')}
                      >
                        ❌ Decline
                      </button>
                      <button 
                        className="quick-response-btn discuss"
                        onClick={() => setInput(`Regarding "${msg.content.substring(0, 30)}...": `)}
                      >
                        💬 Discuss
                      </button>
                    </div>
                  )}
                  
                  {msg.options && (
                    <div className="consensus-options">
                      {msg.options.map((opt, idx) => (
                        <button
                          key={idx}
                          className="option-btn"
                          onClick={() => respondToGrace(msg.id, opt)}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  )}
                  
                  {msg.metadata && (
                    <details className="metadata-details">
                      <summary>🔍 Details</summary>
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
            Commands: <code>/status</code> <code>/meta</code> <code>/spawn [agent] [task]</code>
          </div>
          <form onSubmit={sendMessage} className="input-form">
            <div className="input-row">
              <button type="button" className="input-btn">📎</button>
              <button type="button" className="input-btn">🎤</button>
              <button type="button" className="input-btn">🖼️</button>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Talk with Grace (${activeDomain})...`}
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

      {showSubagents && (
        <aside className="operations-sidebar">
          <div className="operations-feed">
            <h3>🤖 Parallel Subagents ({runningSubagents} active)</h3>
            <div className="feed-items">
              {subagents.length === 0 && (
                <div style={{textAlign: 'center', padding: '20px', color: '#666', fontSize: '13px'}}>
                  No active subagents
                </div>
              )}
              {subagents.map(agent => (
                <div key={agent.task_id} className="subagent-card">
                  <div className="subagent-header">
                    <span className="subagent-type">{agent.agent_type}</span>
                    <span className={`subagent-status status-${agent.status}`}>
                      {agent.status === 'running' ? '🔄' : agent.status === 'completed' ? '✅' : '⏸️'}
                    </span>
                  </div>
                  <div className="subagent-task">{agent.task}</div>
                  <div className="subagent-domain" style={{ color: DOMAINS.find(d => d.id === agent.domain)?.color }}>
                    {DOMAINS.find(d => d.id === agent.domain)?.icon} {agent.domain}
                  </div>
                  {agent.status === 'running' && (
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${agent.progress}%` }}></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </aside>
      )}
    </div>
  );
}
