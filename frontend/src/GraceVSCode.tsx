import { useState, useEffect, useRef } from 'react';
import { setAuthToken } from './api/client';
import './GraceVSCode.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Panel {
  id: string;
  title: string;
  icon: string;
  component: string;
  visible: boolean;
  collapsed: boolean;
}

export default function GraceVSCode() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatCollapsed, setChatCollapsed] = useState(false);
  const [chatHeight, setChatHeight] = useState(300);
  const [panels, setPanels] = useState<Panel[]>([
    { id: 'memory', title: 'Memory', icon: '🧠', component: 'memory', visible: true, collapsed: false },
    { id: 'tasks', title: 'Tasks', icon: '📋', component: 'tasks', visible: true, collapsed: false },
    { id: 'agents', title: 'Agents', icon: '🤖', component: 'agents', visible: true, collapsed: false },
    { id: 'files', title: 'Files', icon: '📁', component: 'files', visible: false, collapsed: true },
  ]);
  const [activeModel, setActiveModel] = useState('grace-default');
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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
      }
    } catch (error) {
      alert('Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    
    setMessages(prev => [...prev, {
      id: `user_${Date.now()}`,
      role: 'user',
      content: userMsg,
      timestamp: new Date()
    }]);
    
    setIsLoading(true);

    try {
      const token = localStorage.getItem('grace_token');
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMsg, domain: 'all' })
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          id: `assistant_${Date.now()}`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date()
        }]);
        
        // Speak response if voice enabled
        if (voiceEnabled) {
          speakResponse(data.response);
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: '❌ Connection error. Backend may be offline.',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const speakResponse = async (text: string) => {
    try {
      const token = localStorage.getItem('grace_token');
      const response = await fetch('http://localhost:8000/api/speech/tts', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ text })
      });
      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
      }
    } catch (error) {
      console.error('TTS error:', error);
    }
  };

  const togglePanel = (panelId: string) => {
    setPanels(prev => prev.map(p => 
      p.id === panelId ? { ...p, collapsed: !p.collapsed } : p
    ));
  };

  const startResize = (e: React.MouseEvent) => {
    e.preventDefault();
    const startY = e.clientY;
    const startHeight = chatHeight;

    const handleMouseMove = (e: MouseEvent) => {
      const delta = startY - e.clientY;
      const newHeight = Math.max(150, Math.min(600, startHeight + delta));
      setChatHeight(newHeight);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  if (!isLoggedIn) {
    return (
      <div className="vscode-login">
        <div className="login-box">
          <h1>Grace AI</h1>
          <p>VSCode-Style Interface</p>
          <form onSubmit={handleLogin}>
            <input 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="Username"
              className="input-field"
            />
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Password"
              className="input-field"
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="vscode-container">
      {/* Top Menu Bar */}
      <div className="menu-bar">
        <div className="menu-left">
          <span className="menu-item">Grace AI</span>
          <span className="menu-item">File</span>
          <span className="menu-item">Edit</span>
          <span className="menu-item">View</span>
          <span className="menu-item">Tools</span>
        </div>
        <div className="menu-right">
          <span className="menu-item">Model: {activeModel}</span>
          <button className="icon-btn" onClick={() => setVoiceEnabled(!voiceEnabled)}>
            {voiceEnabled ? '🔊' : '🔇'}
          </button>
          <button className="icon-btn" onClick={() => { localStorage.clear(); setIsLoggedIn(false); }}>
            ⏻
          </button>
        </div>
      </div>

      <div className="main-layout">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-icons">
            <div className="icon-btn active" title="Chat">💬</div>
            <div className="icon-btn" title="Memory">🧠</div>
            <div className="icon-btn" title="Files">📁</div>
            <div className="icon-btn" title="Tasks">✓</div>
            <div className="icon-btn" title="Agents">🤖</div>
            <div className="icon-btn" title="Settings">⚙️</div>
          </div>
        </div>

        {/* Content Area */}
        <div className="content-area">
          {/* Top Panels */}
          <div className="panels-container">
            {panels.filter(p => p.visible).map(panel => (
              <div key={panel.id} className={`panel ${panel.collapsed ? 'collapsed' : ''}`}>
                <div className="panel-header" onClick={() => togglePanel(panel.id)}>
                  <span>{panel.icon} {panel.title}</span>
                  <span className="collapse-icon">{panel.collapsed ? '▼' : '▲'}</span>
                </div>
                {!panel.collapsed && (
                  <div className="panel-content">
                    {panel.component === 'memory' && (
                      <div className="memory-view">
                        <div className="memory-item">Long-term: 47 items</div>
                        <div className="memory-item">Working: 12 items</div>
                        <div className="memory-item">Context: Active</div>
                      </div>
                    )}
                    {panel.component === 'tasks' && (
                      <div className="tasks-view">
                        <div className="task-item">✓ Backend integration</div>
                        <div className="task-item">⏳ UI enhancement</div>
                      </div>
                    )}
                    {panel.component === 'agents' && (
                      <div className="agents-view">
                        <div className="agent-item">🤖 Code Agent: Ready</div>
                        <div className="agent-item">🔧 Self-Heal: Active</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Bottom Chat Panel */}
          <div 
            className={`chat-panel-bottom ${chatCollapsed ? 'collapsed' : ''}`}
            style={{ height: chatCollapsed ? '40px' : `${chatHeight}px` }}
          >
            <div 
              className="chat-panel-header"
              onDoubleClick={() => setChatCollapsed(!chatCollapsed)}
            >
              <div className="header-left">
                <span onClick={() => setChatCollapsed(!chatCollapsed)} style={{ cursor: 'pointer' }}>
                  {chatCollapsed ? '▲' : '▼'} Chat with Grace
                </span>
                <span className="chat-status">
                  {isLoading ? '⏳ Thinking...' : `${messages.length} messages`}
                </span>
              </div>
              <div 
                className="resize-handle"
                onMouseDown={startResize}
                style={{ cursor: 'ns-resize', padding: '0 8px' }}
              >
                ⋮⋮
              </div>
            </div>

            {!chatCollapsed && (
              <>
                <div className="chat-messages">
                  {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.role}`}>
                      <div className="message-header">
                        <span className="message-role">
                          {msg.role === 'user' ? '👤 You' : '🤖 Grace'}
                        </span>
                        <span className="message-time">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="message-content">{msg.content}</div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                <form onSubmit={sendMessage} className="chat-input-form">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask Grace anything..."
                    className="chat-input"
                    disabled={isLoading}
                  />
                  <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
                    {isLoading ? '⏳' : '➤'}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
