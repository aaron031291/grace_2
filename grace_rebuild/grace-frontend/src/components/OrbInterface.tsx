import { FormEvent, useState } from 'react';
import { useAuth } from './AuthProvider';
import { ReflectionsPanel } from './ReflectionsPanel';
import { TasksPanel } from './TasksPanel';
import { SystemMonitor } from './SystemMonitor';
import { BackgroundMonitor } from './BackgroundMonitor';

interface ChatMessage {
  role: 'user' | 'grace';
  content: string;
}

export function OrbInterface() {
  const { token, login, logout } = useAuth();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeTab, setActiveTab] = useState<'chat' | 'intelligence'>('chat');

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    await login(username, password);
  }

  async function handleSend(e: FormEvent) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    const userMessage: ChatMessage = { role: 'user', content: chatInput };
    setMessages((prev) => [...prev, userMessage]);
    setChatInput('');
    
    try {
      const res = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userMessage.content }),
      });
      
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      const graceMsg: ChatMessage = { role: 'grace', content: data.response || 'No response' };
      setMessages((prev) => [...prev, graceMsg]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'grace', content: 'Error connecting to backend' }]);
    }
  }

  if (!token) {
    return (
      <div style={{ background: '#0f0f1e', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <form onSubmit={handleLogin} style={{ background: '#1a1a2e', padding: '2rem', borderRadius: '8px', minWidth: '320px', border: '1px solid #333' }}>
          <h1 style={{ color: '#00d4ff', marginBottom: '1.5rem' }}>Grace Login</h1>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="username"
            style={{ width: '100%', padding: '0.75rem', marginBottom: '0.75rem', background: '#0f0f1e', color: '#fff', border: '1px solid #333', borderRadius: '6px' }}
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="password"
            style={{ width: '100%', padding: '0.75rem', marginBottom: '1rem', background: '#0f0f1e', color: '#fff', border: '1px solid #333', borderRadius: '6px' }}
          />
          <button type="submit" style={{ width: '100%', padding: '0.75rem', background: '#7b2cbf', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}>
            Login
          </button>
        </form>
      </div>
    );
  }

  return (
    <>
      <BackgroundMonitor />
      <div style={{ background: '#0f0f1e', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header style={{ padding: '1rem', borderBottom: '1px solid #333', background: '#0f0f1e' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#fff' }}>
            <h1 style={{ margin: 0, color: '#00d4ff' }}>Grace</h1>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <a href="/dashboard" style={{ color: '#7b2cbf', textDecoration: 'none' }}>📊 Dashboard</a>
              <button onClick={logout} style={{ background: '#333', color: '#fff', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer' }}>Logout</button>
            </div>
          </div>
        </header>

        <div style={{ display: 'flex', borderBottom: '1px solid #333', background: '#1a1a2e' }}>
          <button
            onClick={() => setActiveTab('chat')}
            style={{
              padding: '1rem 2rem',
              background: activeTab === 'chat' ? '#0f0f1e' : 'transparent',
              color: activeTab === 'chat' ? '#00d4ff' : '#888',
              border: 'none',
              borderBottom: activeTab === 'chat' ? '2px solid #00d4ff' : 'none',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            💬 Chat
          </button>
          <button
            onClick={() => setActiveTab('intelligence')}
            style={{
              padding: '1rem 2rem',
              background: activeTab === 'intelligence' ? '#0f0f1e' : 'transparent',
              color: activeTab === 'intelligence' ? '#7b2cbf' : '#888',
              border: 'none',
              borderBottom: activeTab === 'intelligence' ? '2px solid #7b2cbf' : 'none',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            🧠 Intelligence
          </button>
        </div>

        <main style={{ flex: 1, padding: '1.5rem', overflowY: 'auto', background: '#0f0f1e' }}>
          {activeTab === 'chat' && (
            <div style={{ maxWidth: '700px', margin: '0 auto' }}>
              {messages.length === 0 && <p style={{ textAlign: 'center', color: '#888' }}>Start chatting with Grace...</p>}
              {messages.map((msg, idx) => (
                <div key={idx} style={{ marginBottom: '1rem', display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  <div style={{
                    padding: '0.75rem 1rem',
                    borderRadius: '12px',
                    background: msg.role === 'user' ? '#7b2cbf' : '#1a1a2e',
                    maxWidth: '70%',
                    color: '#fff',
                    border: msg.role === 'grace' ? '1px solid #333' : 'none'
                  }}>
                    <strong>{msg.role === 'user' ? 'You' : 'Grace'}:</strong> {msg.content}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'intelligence' && (
            <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem' }}>
              <ReflectionsPanel />
              <TasksPanel />
              <SystemMonitor />
            </div>
          )}
        </main>

        <footer style={{ padding: '1rem', borderTop: '1px solid #333', background: '#0f0f1e' }}>
          <form onSubmit={handleSend} style={{ maxWidth: '700px', margin: '0 auto', display: 'flex', gap: '0.75rem' }}>
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Message Grace..."
              style={{ flex: 1, padding: '0.875rem', background: '#1a1a2e', color: '#fff', border: '1px solid #333', borderRadius: '8px', fontSize: '14px' }}
            />
            <button type="submit" style={{ padding: '0.875rem 2rem', background: '#7b2cbf', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>
              Send
            </button>
          </form>
        </footer>
      </div>
    </>
  );
}
