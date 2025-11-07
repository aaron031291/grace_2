import { useState, useEffect, useRef, lazy, Suspense } from 'react';
import './AppModern.css';

// Lazy load components to avoid import errors
const KnowledgeManager = lazy(() => import('./components/Knowledge/KnowledgeManager').then(m => ({ default: m.KnowledgeManager })));
const HunterDashboard = lazy(() => import('./components/HunterDashboard').then(m => ({ default: m.HunterDashboard })));
const MetaLoopDashboard = lazy(() => import('./components/MetaLoopDashboard').then(m => ({ default: m.MetaLoopDashboard })));
const TranscendenceIDE = lazy(() => import('./components/TranscendenceIDE').then(m => ({ default: m.TranscendenceIDE })));
const MemoryBrowser = lazy(() => import('./components/MemoryBrowser').then(m => ({ default: m.MemoryBrowser })));
const ApprovalsAdmin = lazy(() => import('./components/Governance/ApprovalsAdmin').then(m => ({ default: m.ApprovalsAdmin })));

const DOMAINS = [
  { id: 'chat', name: 'Chat', icon: '💬', desc: 'Talk with Grace AI' },
  { id: 'knowledge', name: 'Knowledge', icon: '📚', desc: 'Ingest & search knowledge' },
  { id: 'security', name: 'Security', icon: '🛡️', desc: 'Hunter threat detection' },
  { id: 'metaloop', name: 'Meta Loop', icon: '🧠', desc: 'Governance & optimization' },
  { id: 'transcendence', name: 'Transcendence', icon: '💻', desc: 'Agentic development' },
  { id: 'memory', name: 'Memory', icon: '📁', desc: 'Browse agentic memory' },
  { id: 'approvals', name: 'Approvals', icon: '✅', desc: 'Constitutional AI' },
  { id: 'health', name: 'Health', icon: '❤️', desc: 'System monitoring' },
  { id: 'tasks', name: 'Tasks', icon: '📋', desc: 'Task management' },
  { id: 'metrics', name: 'Metrics', icon: '📊', desc: 'Analytics dashboard' },
];

export default function GraceClean() {
  const [domain, setDomain] = useState('chat');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([
    { role: 'assistant', content: 'Hello! I\'m Grace. How can I help you today?' }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response || 'I received your message!'
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Error connecting to backend. Make sure it\'s running at http://localhost:8000'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setMessages(prev => [...prev, { 
        role: 'user', 
        content: `📎 File uploaded: ${files[0].name}`
      }]);
    }
  };

  const currentDomain = DOMAINS.find(d => d.id === domain);

  // Render domain-specific content
  const renderDomainContent = () => {
    // Render actual components for each domain
    if (domain === 'knowledge') {
      return (
        <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading Knowledge...</div>}>
          <KnowledgeManager />
        </Suspense>
      );
    }
    
    if (domain === 'security') {
      return (
        <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading Security...</div>}>
          <HunterDashboard />
        </Suspense>
      );
    }
    
    if (domain === 'metaloop') {
      return (
        <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading Meta Loop...</div>}>
          <MetaLoopDashboard />
        </Suspense>
      );
    }
    
    if (domain === 'transcendence') {
      return (
        <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading Transcendence...</div>}>
          <TranscendenceIDE />
        </Suspense>
      );
    }
    
    if (domain === 'memory') {
      return (
        <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading Memory...</div>}>
          <MemoryBrowser />
        </Suspense>
      );
    }
    
    if (domain === 'approvals') {
      return (
        <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading Approvals...</div>}>
          <ApprovalsAdmin />
        </Suspense>
      );
    }
    
    if (domain === 'chat') {
      return (
        <>
          <div className="messages-container">
            <div className="messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{msg.content}</div>
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

          <div className="input-container">
            <form onSubmit={sendMessage} className="input-form">
              <div className="input-wrapper">
                <div className="input-actions-left">
                  <label className="icon-btn" title="Upload file">
                    📎
                    <input type="file" hidden onChange={handleFileUpload} />
                  </label>
                  <button type="button" className="icon-btn" title="Voice">🎤</button>
                  <button type="button" className="icon-btn" title="Image">🖼️</button>
                </div>

                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Message Grace..."
                  className="message-input"
                  disabled={isLoading}
                />

                <button 
                  type="submit" 
                  className="send-btn"
                  disabled={!input.trim() || isLoading}
                >
                  {isLoading ? '⏳' : '🚀'}
                </button>
              </div>
            </form>
          </div>
        </>
      );
    }

    // For domains without specific UIs yet (health, tasks, metrics)
    return (
      <div style={{ 
        padding: '60px', 
        textAlign: 'center', 
        maxWidth: '800px', 
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '70vh'
      }}>
        <div style={{ fontSize: '80px', marginBottom: '30px' }}>{currentDomain?.icon}</div>
        <h1 style={{ fontSize: '36px', marginBottom: '16px', color: '#e0e0e0' }}>
          {currentDomain?.name}
        </h1>
        <p style={{ fontSize: '18px', color: '#888', marginBottom: '40px', lineHeight: '1.6' }}>
          {currentDomain?.desc}
        </p>
        
        <div style={{ 
          background: 'rgba(102, 126, 234, 0.1)', 
          border: '1px solid rgba(102, 126, 234, 0.3)',
          borderRadius: '16px',
          padding: '30px',
          marginBottom: '30px',
          width: '100%'
        }}>
          <h3 style={{ color: '#667eea', marginBottom: '20px', fontSize: '20px' }}>
            Available via Chat & API
          </h3>
          <p style={{ color: '#b0b0b0', fontSize: '15px', lineHeight: '1.6', marginBottom: '20px' }}>
            Interface coming soon. Use Chat to interact with this domain.
          </p>
          
          <button 
            onClick={() => setDomain('chat')}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#fff',
              border: 'none',
              padding: '14px 28px',
              borderRadius: '8px',
              fontSize: '15px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            💬 Go to Chat
          </button>
        </div>
      </div>
    );
  };

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
        </div>
      </aside>

      <main className="main-content">
        <header className="content-header">
          <div className="current-domain">
            <span className="domain-icon-large">{currentDomain?.icon}</span>
            <div>
              <h2>{currentDomain?.name}</h2>
              <p className="domain-desc">{currentDomain?.desc}</p>
            </div>
          </div>
          <div className="header-actions">
            <button className="icon-btn" onClick={() => setMessages([{ role: 'assistant', content: 'New conversation started!' }])} title="New conversation">➕</button>
            <button className="icon-btn" title="History">📜</button>
            <button className="icon-btn" title="Share">🔗</button>
          </div>
        </header>

        {renderDomainContent()}
      </main>
    </div>
  );
}
