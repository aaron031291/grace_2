import { useState, useEffect, useRef, lazy, Suspense } from 'react';
import './AppModern.css';
import { setAuthToken } from './api/client';

// Lazy load components
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

export default function GraceFinal() {
  const [domain, setDomain] = useState('chat');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [loginError, setLoginError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const token = localStorage.getItem('grace_token');
    if (token) {
      setIsLoggedIn(true);
      setAuthToken(token);
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('grace_token', data.access_token);
        setAuthToken(data.access_token);
        setIsLoggedIn(true);
        setMessages([{ role: 'assistant', content: `Welcome, ${username}! I'm Grace. How can I assist you today?` }]);
      } else {
        setLoginError('Invalid credentials');
      }
    } catch (error) {
      setLoginError('Backend offline');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
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
        setMessages([{ role: 'assistant', content: `Account created! Welcome, ${username}!` }]);
      } else {
        setLoginError('Registration failed');
      }
    } catch (error) {
      setLoginError('Backend offline');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('grace_token');
    setAuthToken(null);
    setIsLoggedIn(false);
    setDomain('chat');
    setMessages([]);
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
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
        role: 'assistant', 
        content: data.response || 'Received!'
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Backend error'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const currentDomain = DOMAINS.find(d => d.id === domain);

  if (!isLoggedIn) {
    return (
      <div className="app-modern" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div style={{background: '#1a1a2e', padding: '40px', borderRadius: '16px', width: '400px', border: '1px solid #2a2a3e'}}>
          <div style={{ textAlign: 'center', marginBottom: '30px' }}>
            <h1 style={{ fontSize: '36px', marginBottom: '10px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Grace AI</h1>
            <p style={{ fontSize: '14px', color: '#888' }}>Autonomous Intelligence</p>
          </div>

          <form onSubmit={handleLogin} style={{ marginBottom: '20px' }}>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" style={{width: '100%', padding: '12px', background: '#0f0f1e', border: '1px solid #2a2a3e', borderRadius: '8px', color: '#e0e0e0', marginBottom: '12px'}} />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" style={{width: '100%', padding: '12px', background: '#0f0f1e', border: '1px solid #2a2a3e', borderRadius: '8px', color: '#e0e0e0', marginBottom: '12px'}} />
            {loginError && <div style={{background: 'rgba(255, 68, 68, 0.1)', border: '1px solid rgba(255, 68, 68, 0.3)', padding: '12px', borderRadius: '8px', color: '#ff6b6b', fontSize: '13px', marginBottom: '16px'}}>{loginError}</div>}
            <button type="submit" style={{width: '100%', padding: '14px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '15px', fontWeight: '500', cursor: 'pointer', marginBottom: '12px'}}>{isLoading ? '⏳ Logging in...' : '🚀 Login'}</button>
            <button type="button" onClick={handleRegister} style={{width: '100%', padding: '14px', background: '#2a2a3e', border: '1px solid #3a3a4e', borderRadius: '8px', color: '#e0e0e0', fontSize: '15px', fontWeight: '500', cursor: 'pointer'}}>✨ Register</button>
          </form>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    if (domain === 'knowledge') return <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading...</div>}><KnowledgeManager /></Suspense>;
    if (domain === 'security') return <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading...</div>}><HunterDashboard /></Suspense>;
    if (domain === 'metaloop') return <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading...</div>}><MetaLoopDashboard /></Suspense>;
    if (domain === 'transcendence') return <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading...</div>}><TranscendenceIDE /></Suspense>;
    if (domain === 'memory') return <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading...</div>}><MemoryBrowser /></Suspense>;
    if (domain === 'approvals') return <Suspense fallback={<div style={{padding: '40px', textAlign: 'center', color: '#888'}}>Loading...</div>}><ApprovalsAdmin /></Suspense>;
    
    if (domain === 'chat') {
      return (
        <>
          <div className="messages-container"><div className="messages">{messages.map((msg, idx) => (<div key={idx} className={`message ${msg.role}`}><div className="message-avatar">{msg.role === 'user' ? '👤' : '🤖'}</div><div className="message-content"><div className="message-text">{msg.content}</div></div></div>))}{isLoading && (<div className="message assistant"><div className="message-avatar">🤖</div><div className="message-content"><div className="typing-indicator"><span></span><span></span><span></span></div></div></div>)}<div ref={messagesEndRef} /></div></div>
          <div className="input-container"><form onSubmit={sendMessage} className="input-form"><div className="input-wrapper"><div className="input-actions-left"><label className="icon-btn" title="Upload">📎<input type="file" hidden /></label><button type="button" className="icon-btn">🎤</button><button type="button" className="icon-btn">🖼️</button></div><input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Message Grace..." className="message-input" disabled={isLoading} /><button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>{isLoading ? '⏳' : '🚀'}</button></div></form></div>
        </>
      );
    }
    
    return <div style={{padding: '60px', textAlign: 'center', color: '#888'}}>Coming soon</div>;
  };

  return (
    <div className="app-modern">
      <aside className="sidebar">
        <div className="sidebar-header"><h1 className="logo">Grace AI</h1><p className="tagline">Autonomous Intelligence</p></div>
        <nav className="domain-nav">{DOMAINS.map(d => (<button key={d.id} className={`domain-btn ${domain === d.id ? 'active' : ''}`} onClick={() => setDomain(d.id)} title={d.desc}><span className="domain-icon">{d.icon}</span><span className="domain-name">{d.name}</span></button>))}</nav>
        <div className="sidebar-footer"><div className="status-indicator"><div className="status-dot"></div><span>Online</span></div><button className="settings-btn" onClick={handleLogout}>🚪 Logout</button></div>
      </aside>
      <main className="main-content">
        <header className="content-header"><div className="current-domain"><span className="domain-icon-large">{currentDomain?.icon}</span><div><h2>{currentDomain?.name}</h2><p className="domain-desc">{currentDomain?.desc}</p></div></div><div className="header-actions"><button className="icon-btn" onClick={() => setMessages([{ role: 'assistant', content: 'New conversation!' }])}>➕</button></div></header>
        {renderContent()}
      </main>
    </div>
  );
}
