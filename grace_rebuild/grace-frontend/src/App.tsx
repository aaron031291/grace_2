import { useState, FormEvent } from 'react';
import { Dashboard } from './components/Dashboard';

export default function App() {
  const [page, setPage] = useState<'chat' | 'dashboard'>('chat');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.access_token) {
      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
    }
  }

  async function sendMessage(e: FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages(m => [...m, { role: 'user', content: input }]);
    const userMsg = input;
    setInput('');

    const res = await fetch('http://localhost:8000/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message: userMsg })
    });
    const data = await res.json();
    setMessages(m => [...m, { role: 'grace', content: data.response }]);
  }

  if (!token) {
    return (
      <div style={{ background: '#0f0f1e', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <form onSubmit={handleLogin} style={{ background: '#1a1a2e', padding: '2rem', borderRadius: '12px', width: '300px' }}>
          <h1 style={{ color: '#00d4ff', marginBottom: '1.5rem', textAlign: 'center' }}>Grace</h1>
          <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" style={{ width: '100%', padding: '0.75rem', marginBottom: '0.75rem', background: '#0f0f1e', color: '#fff', border: '1px solid #444', borderRadius: '6px' }} />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" style={{ width: '100%', padding: '0.75rem', marginBottom: '1rem', background: '#0f0f1e', color: '#fff', border: '1px solid #444', borderRadius: '6px' }} />
          <button type="submit" style={{ width: '100%', padding: '0.75rem', background: '#7b2cbf', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>Login</button>
        </form>
      </div>
    );
  }

  if (page === 'dashboard') {
    return <Dashboard />;
  }

  return (
    <div style={{ background: '#0f0f1e', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '1rem', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ color: '#00d4ff', margin: 0 }}>Grace</h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={() => setPage('dashboard')} style={{ background: 'none', color: '#7b2cbf', border: 'none', cursor: 'pointer' }}>📊 Dashboard</button>
          <button onClick={() => { setToken(''); localStorage.removeItem('token'); }} style={{ padding: '0.5rem 1rem', background: '#333', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Logout</button>
        </div>
      </header>

      <main style={{ flex: 1, padding: '1.5rem', overflowY: 'auto' }}>
        <div style={{ maxWidth: '700px', margin: '0 auto' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ marginBottom: '1rem', display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{ padding: '0.75rem 1rem', borderRadius: '12px', background: msg.role === 'user' ? '#7b2cbf' : '#1a1a2e', maxWidth: '75%', color: '#fff' }}>
                <strong>{msg.role === 'user' ? 'You' : 'Grace'}:</strong> {msg.content}
              </div>
            </div>
          ))}
        </div>
      </main>

      <footer style={{ padding: '1rem', borderTop: '1px solid #333' }}>
        <form onSubmit={sendMessage} style={{ maxWidth: '700px', margin: '0 auto', display: 'flex', gap: '0.75rem' }}>
          <input value={input} onChange={e => setInput(e.target.value)} placeholder="Message Grace..." style={{ flex: 1, padding: '0.875rem', background: '#1a1a2e', color: '#fff', border: '1px solid #444', borderRadius: '8px' }} />
          <button type="submit" style={{ padding: '0.875rem 2rem', background: '#7b2cbf', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }}>Send</button>
        </form>
      </footer>
    </div>
  );
}
