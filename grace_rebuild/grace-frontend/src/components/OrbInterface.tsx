import { FormEvent, useState } from 'react';
import { useAuth } from './AuthProvider';
import { ReflectionsPanel } from './ReflectionsPanel';
import { BackgroundMonitor } from './BackgroundMonitor';
import { SystemMonitor } from './SystemMonitor';

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
  const [status, setStatus] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'chat' | 'reflections'>('chat');

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    setStatus('Logging in...');
    const ok = await login(username, password);
    setStatus(ok ? 'Logged in!' : 'Login failed');
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
          Authorization: token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });
      if (!res.ok) throw new Error('Chat request failed');
      const data = await res.json();
      const graceMessage: ChatMessage = {
        role: 'grace',
        content: data.response ?? JSON.stringify(data),
      };
      setMessages((prev) => [...prev, graceMessage]);
    } catch (error: any) {
      setStatus(error.message ?? 'Chat failed');
    }
  }

  if (!token) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', minHeight: '100vh', background: '#0f0f1e' }}>
        <form
          onSubmit={handleLogin}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            padding: '2rem',
            border: '1px solid #333',
            borderRadius: '8px',
            minWidth: '320px',
            background: '#1a1a2e',
            color: '#fff',
          }}
        >
          <h1 style={{ margin: 0 }}>Grace Login</h1>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="username"
            style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #333', background: '#0f0f1e', color: '#fff' }}
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="password"
            style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #333', background: '#0f0f1e', color: '#fff' }}
          />
          <button type="submit" style={{ padding: '0.5rem', borderRadius: '4px', background: '#7b2cbf', color: '#fff', border: 'none', cursor: 'pointer' }}>Login</button>
          {status && <div style={{ fontSize: '0.875rem', color: '#00d4ff' }}>{status}</div>}
        </form>
      </div>
    );
  }

  return (
    <>
      <BackgroundMonitor />
      <SystemMonitor />
      <div style={{ display: 'grid', gridTemplateRows: 'auto auto 1fr auto', minHeight: '100vh', background: '#0f0f1e', color: '#fff' }}>
        <header style={{ padding: '1rem', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0 }}>Grace Orb</h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <a href="/dashboard" style={{ color: '#7b2cbf', textDecoration: 'none', fontSize: '0.875rem' }}>📊 Dashboard</a>
            {status && <span style={{ fontSize: '0.875rem', color: '#00d4ff' }}>{status}</span>}
            <button onClick={logout} style={{ padding: '0.5rem 1rem', borderRadius: '4px', background: '#333', color: '#fff', border: 'none', cursor: 'pointer' }}>Log out</button>
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
              borderBottom: activeTab === 'chat' ? '2px solid #00d4ff' : '2px solid transparent',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: 600
            }}
          >
            💬 Chat
          </button>
          <button
            onClick={() => setActiveTab('reflections')}
            style={{
              padding: '1rem 2rem',
              background: activeTab === 'reflections' ? '#0f0f1e' : 'transparent',
              color: activeTab === 'reflections' ? '#7b2cbf' : '#888',
              border: 'none',
              borderBottom: activeTab === 'reflections' ? '2px solid #7b2cbf' : '2px solid transparent',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: 600
            }}
          >
            🔍 Reflections
          </button>
        </div>

        <main style={{ padding: '1rem', overflowY: 'auto' }}>
          {activeTab === 'chat' && (
            <div style={{ maxWidth: '600px', margin: '0 auto' }}>
              {messages.length === 0 && (
                <p style={{ textAlign: 'center', color: '#888' }}>Ask Grace anything to get started.</p>
              )}
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    marginBottom: '0.5rem',
                  }}
                >
                  <div
                    style={{
                      background: msg.role === 'user' ? '#7b2cbf' : '#1a1a2e',
                      color: '#fff',
                      padding: '0.75rem',
                      borderRadius: '12px',
                      maxWidth: '70%',
                      whiteSpace: 'pre-wrap',
                      border: msg.role === 'grace' ? '1px solid #333' : 'none',
                    }}
                  >
                    <strong>{msg.role === 'user' ? 'You' : 'Grace'}:</strong>{' '}
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'reflections' && (
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              <ReflectionsPanel />
            </div>
          )}
        </main>

        <footer style={{ padding: '1rem', borderTop: '1px solid #333' }}>
          <form
            onSubmit={handleSend}
            style={{ display: 'flex', gap: '0.5rem', maxWidth: '600px', margin: '0 auto' }}
          >
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Type a message..."
              style={{ flex: 1, padding: '0.75rem', borderRadius: '12px', border: '1px solid #333', background: '#1a1a2e', color: '#fff' }}
            />
            <button type="submit" style={{ padding: '0.75rem 1.5rem', borderRadius: '12px', background: '#7b2cbf', color: '#fff', border: 'none', cursor: 'pointer' }}>
              Send
            </button>
          </form>
        </footer>
      </div>
    </>
  );
}
