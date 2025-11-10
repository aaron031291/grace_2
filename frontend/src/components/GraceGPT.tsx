import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { setAuthToken } from '../api/client';
import { ApprovalModal } from './ApprovalModal';
import './GraceGPT.css';

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

const SLASH_COMMANDS = [
  { cmd: '/self_heal', desc: 'Trigger self-healing analysis', domain: 'self_heal' },
  { cmd: '/meta', desc: 'Run meta-loop cycle', domain: 'meta_loop' },
  { cmd: '/playbook', desc: 'Execute domain playbook', domain: 'core' },
  { cmd: '/scan', desc: 'Security vulnerability scan', domain: 'security' },
  { cmd: '/learn', desc: 'Knowledge discovery cycle', domain: 'knowledge' },
  { cmd: '/status', desc: 'System health status', domain: 'core' },
];

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'notification' | 'question' | 'subagent';
  content: string;
  domain: string;
  from?: string;
  timestamp: Date;
  requires_response?: boolean;
  metadata?: any;
  options?: string[];
  streaming?: boolean;
}

interface Subagent {
  task_id: string;
  agent_type: string;
  task: string;
  domain: string;
  status: string;
  progress: number;
}

interface ActivityEvent {
  id: string;
  type: 'meta' | 'heal' | 'resource' | 'playbook' | 'alert';
  content: string;
  severity: 'info' | 'warning' | 'critical';
  timestamp: Date;
  domain: string;
}

export default function GraceGPT() {
  const [activeDomain, setActiveDomain] = useState('all');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [subagents, setSubagents] = useState<Subagent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [subagentWs, setSubagentWs] = useState<WebSocket | null>(null);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [commandFilter, setCommandFilter] = useState('');
  const [showSidebar, setShowSidebar] = useState(true);
  const [showActivity, setShowActivity] = useState(true);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [reviewMode, setReviewMode] = useState(false);
  const [pendingAction, setPendingAction] = useState<any>(null);
  const [showApprovals, setShowApprovals] = useState(false);
  const [approvalCount, setApprovalCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
      initializeConnections(token);
      pollApprovals(token);
    }

    // Request notification permission
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const pollApprovals = (token: string) => {
    const checkApprovals = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/autonomy/approvals', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        const count = Array.isArray(data) ? data.length : 0;
        setApprovalCount(count);
      } catch (err) {
        console.error('Failed to fetch approvals:', err);
      }
    };

    checkApprovals();
    setInterval(checkApprovals, 5000);
  };

  const initializeConnections = (token: string) => {
    const proactive = new WebSocket(`ws://localhost:8000/api/proactive/ws?token=${token}`);
    
    proactive.onopen = () => {
      addMessage({
        id: 'sys_conn',
        type: 'system',
        content: 'Connected to Grace. Ready to assist with full autonomous capabilities.',
        domain: 'core',
        from: 'system',
        timestamp: new Date()
      });
    };

    proactive.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleProactiveMessage(data);
    };

    proactive.onerror = () => {
      addActivity({
        id: `err_${Date.now()}`,
        type: 'alert',
        content: 'WebSocket connection error',
        severity: 'critical',
        timestamp: new Date(),
        domain: 'core'
      });
    };

    setWs(proactive);

    const subagent = new WebSocket(`ws://localhost:8000/api/subagents/ws?token=${token}`);
    
    subagent.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'subagent_status' && data.agents) {
        setSubagents(Object.values(data.agents));
      } else if (data.type === 'subagent_spawned') {
        addMessage({
          id: `subagent_${Date.now()}`,
          type: 'subagent',
          content: `Spawned ${data.agent.agent_type} for: ${data.agent.task}`,
          domain: data.agent.domain,
          timestamp: new Date(),
          metadata: data.agent
        });
        addActivity({
          id: `act_spawn_${Date.now()}`,
          type: 'playbook',
          content: `Subagent: ${data.agent.agent_type}`,
          severity: 'info',
          timestamp: new Date(),
          domain: data.agent.domain
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
    
    if (data.type !== 'system') {
      addActivity({
        id: `act_${Date.now()}`,
        type: data.type === 'question' ? 'alert' : 'meta',
        content: data.content.substring(0, 60),
        severity: data.requires_response ? 'warning' : 'info',
        timestamp: new Date(),
        domain: data.domain
      });

      if (Notification.permission === 'granted') {
        new Notification('Grace AI', {
          body: data.content.substring(0, 100)
        });
      }
    }
  };

  const addMessage = (msg: Message) => {
    setMessages(prev => [...prev, msg]);
  };

  const addActivity = (event: ActivityEvent) => {
    setActivity(prev => [event, ...prev].slice(0, 50));
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.access_token) {
        localStorage.setItem('grace_token', data.access_token);
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        initializeConnections(data.access_token);
      }
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: input,
      domain: activeDomain,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    const prompt = input;
    setInput('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('grace_token');
      const res = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: prompt, domain: activeDomain })
      });
      const data = await res.json();

      const assistantMsg: Message = {
        id: `assistant_${Date.now()}`,
        type: 'assistant',
        content: data.response,
        domain: data.domain || activeDomain,
        from: 'grace',
        timestamp: new Date(),
        metadata: data.metadata
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Send failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === '/' && input === '') {
      e.preventDefault();
      setShowCommandPalette(true);
      setCommandFilter('');
    }
  };

  const executeSlashCommand = (cmd: string) => {
    setInput(cmd + ' ');
    setShowCommandPalette(false);
    inputRef.current?.focus();
  };

  const handleResponseToGrace = async (msgId: string, response: string) => {
    if (!ws) return;
    
    ws.send(JSON.stringify({
      type: 'user_response',
      message_id: msgId,
      response
    }));

    addMessage({
      id: `user_resp_${Date.now()}`,
      type: 'user',
      content: response,
      domain: 'core',
      timestamp: new Date()
    });
  };

  const handleApprove = () => {
    if (pendingAction) {
      ws?.send(JSON.stringify({
        type: 'approval',
        action_id: pendingAction.id,
        approved: true
      }));
      setPendingAction(null);
    }
  };

  const handleDecline = () => {
    if (pendingAction) {
      ws?.send(JSON.stringify({
        type: 'approval',
        action_id: pendingAction.id,
        approved: false
      }));
      setPendingAction(null);
    }
  };

  const filteredMessages = activeDomain === 'all'
    ? messages
    : messages.filter(m => m.domain === activeDomain || m.type === 'system');

  const filteredCommands = SLASH_COMMANDS.filter(c =>
    c.cmd.includes(commandFilter) || c.desc.toLowerCase().includes(commandFilter.toLowerCase())
  );

  if (!isLoggedIn) {
    return (
      <div className={`grace-gpt-login ${theme}`}>
        <div className="login-card">
          <div className="login-header">
            <div className="grace-logo">⚡</div>
            <h1>Grace AI</h1>
            <p>Autonomous Intelligence Platform</p>
          </div>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              className="login-input"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="login-input"
            />
            <button type="submit" className="login-button">
              Sign In
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className={`grace-gpt ${theme}`}>
      {/* Sidebar */}
      {showSidebar && (
        <div className="sidebar">
          <div className="sidebar-header">
            <div className="grace-brand">
              <span className="brand-icon">⚡</span>
              <span className="brand-name">Grace</span>
            </div>
            <button className="toggle-btn" onClick={() => setShowSidebar(false)}>×</button>
          </div>

          <div className="sidebar-section">
            <h3>Active Domain</h3>
            <div className="domain-selector">
              {DOMAINS.map(d => (
                <button
                  key={d.id}
                  className={`domain-chip ${activeDomain === d.id ? 'active' : ''}`}
                  style={{ '--domain-color': d.color } as any}
                  onClick={() => setActiveDomain(d.id)}
                >
                  <span className="domain-icon">{d.icon}</span>
                  <span className="domain-name">{d.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="sidebar-section">
            <h3>Controls</h3>
            <label className="toggle-option">
              <input
                type="checkbox"
                checked={reviewMode}
                onChange={e => setReviewMode(e.target.checked)}
              />
              <span>Review before execute</span>
            </label>
            <label className="toggle-option">
              <input
                type="checkbox"
                checked={showActivity}
                onChange={e => setShowActivity(e.target.checked)}
              />
              <span>Show activity feed</span>
            </label>
          </div>

          <div className="sidebar-section">
            <h3>Subagents ({subagents.length})</h3>
            <div className="subagents-list">
              {subagents.slice(0, 5).map(s => (
                <div key={s.task_id} className="subagent-item">
                  <div className="subagent-header">
                    <span className="subagent-type">{s.agent_type}</span>
                    <span className={`subagent-status ${s.status}`}>{s.status}</span>
                  </div>
                  <div className="subagent-progress">
                    <div className="progress-bar" style={{ width: `${s.progress}%` }}></div>
                  </div>
                  <div className="subagent-task">{s.task}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-footer">
            <button className="theme-toggle" onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <button className="logout-btn" onClick={() => {
              localStorage.clear();
              setIsLoggedIn(false);
              ws?.close();
              subagentWs?.close();
            }}>
              Logout
            </button>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="main-chat">
        <div className="chat-header">
          {!showSidebar && (
            <button className="toggle-btn" onClick={() => setShowSidebar(true)}>☰</button>
          )}
          <h2>Grace AI Chat</h2>
          <div className="header-actions">
            {approvalCount > 0 && (
              <button className="approval-badge" onClick={() => setShowApprovals(true)}>
                ✋ {approvalCount} Approval{approvalCount > 1 ? 's' : ''}
              </button>
            )}
            <span className="status-indicator">🟢 Connected</span>
          </div>
        </div>

        <div className="messages-container">
          {filteredMessages.map(msg => (
            <div key={msg.id} className={`message-wrapper ${msg.type}`}>
              {msg.type !== 'user' && (
                <div className="message-avatar">
                  {msg.type === 'assistant' || msg.type === 'notification' || msg.type === 'question'
                    ? '⚡'
                    : msg.type === 'subagent'
                    ? '🤖'
                    : 'ℹ️'}
                </div>
              )}
              <div className="message-bubble">
                <div className="message-header">
                  <span className="message-from">
                    {msg.type === 'user' ? 'You' : msg.from || 'Grace'}
                  </span>
                  <span className="message-time">
                    {msg.timestamp.toLocaleTimeString()}
                  </span>
                  {msg.domain !== 'core' && (
                    <span className="message-domain">{msg.domain}</span>
                  )}
                </div>
                <div className="message-content">
                  {msg.streaming ? (
                    <span className="typing-indicator">●●●</span>
                  ) : (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
                {msg.requires_response && msg.options && (
                  <div className="message-actions">
                    {msg.options.map((opt, i) => (
                      <button
                        key={i}
                        className="action-btn"
                        onClick={() => handleResponseToGrace(msg.id, opt)}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                )}
                {msg.metadata && (
                  <button className="explain-btn" onClick={() => alert(JSON.stringify(msg.metadata, null, 2))}>
                    Explain
                  </button>
                )}
              </div>
              {msg.type === 'user' && (
                <div className="message-avatar user-avatar">👤</div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="message-wrapper assistant">
              <div className="message-avatar">⚡</div>
              <div className="message-bubble">
                <div className="typing-indicator">●●●</div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          {showCommandPalette && (
            <div className="command-palette">
              {filteredCommands.map(cmd => (
                <div
                  key={cmd.cmd}
                  className="command-item"
                  onClick={() => executeSlashCommand(cmd.cmd)}
                >
                  <span className="command-name">{cmd.cmd}</span>
                  <span className="command-desc">{cmd.desc}</span>
                </div>
              ))}
            </div>
          )}
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Grace... (press / for commands)"
              className="message-input"
              rows={1}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              ↑
            </button>
          </div>
          <div className="input-hint">
            {reviewMode && <span className="hint-badge">Review mode enabled</span>}
            <span className="hint-text">Shift+Enter for newline</span>
          </div>
        </div>
      </div>

      {/* Activity Rail */}
      {showActivity && (
        <div className="activity-rail">
          <div className="activity-header">
            <h3>Live Activity</h3>
            <button className="close-btn" onClick={() => setShowActivity(false)}>×</button>
          </div>
          <div className="activity-list">
            {activity.map(act => (
              <div key={act.id} className={`activity-item ${act.severity}`}>
                <div className="activity-icon">
                  {act.type === 'meta' ? '🧠' :
                   act.type === 'heal' ? '🔧' :
                   act.type === 'resource' ? '📊' :
                   act.type === 'playbook' ? '📋' : '⚠️'}
                </div>
                <div className="activity-content">
                  <div className="activity-text">{act.content}</div>
                  <div className="activity-time">{act.timestamp.toLocaleTimeString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Approval Modal */}
      <ApprovalModal
        isOpen={showApprovals}
        onClose={() => setShowApprovals(false)}
        token={localStorage.getItem('grace_token') || ''}
      />
    </div>
  );
}
