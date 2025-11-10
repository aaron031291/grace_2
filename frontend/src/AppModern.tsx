import { useState } from 'react';
import './AppModern.css';

// Domain icons and info
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

export default function AppModern() {
  const [domain, setDomain] = useState('chat');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([
    { role: 'assistant', content: 'Hello! I\'m Grace, your autonomous AI assistant. How can I help you today?' }
  ]);
  const [isLoading, setIsLoading] = useState(false);

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
        content: 'Sorry, I encountered an error. Please make sure the backend is running.'
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
        content: `📎 Uploaded: ${files[0].name}`
      }]);
    }
  };

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
          <button className="settings-btn">⚙️ Settings</button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="content-header">
          <div className="current-domain">
            <span className="domain-icon-large">
              {DOMAINS.find(d => d.id === domain)?.icon}
            </span>
            <div>
              <h2>{DOMAINS.find(d => d.id === domain)?.name}</h2>
              <p className="domain-desc">{DOMAINS.find(d => d.id === domain)?.desc}</p>
            </div>
          </div>
          <div className="header-actions">
            <button className="icon-btn" title="New conversation">➕</button>
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
          </div>
        </div>

        {/* Input Area */}
        <div className="input-container">
          <form onSubmit={sendMessage} className="input-form">
            <div className="input-wrapper">
              {/* Multimodal Input Buttons */}
              <div className="input-actions-left">
                <label className="icon-btn" title="Upload file">
                  📎
                  <input 
                    type="file" 
                    hidden 
                    onChange={handleFileUpload}
                    accept="image/*,.pdf,.txt,.md,.json"
                  />
                </label>
                <button type="button" className="icon-btn" title="Voice input">🎤</button>
                <button type="button" className="icon-btn" title="Image">🖼️</button>
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
            Grace can help with code, knowledge, security, and more. 
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">API Docs</a>
          </p>
        </div>
      </main>
    </div>
  );
}
