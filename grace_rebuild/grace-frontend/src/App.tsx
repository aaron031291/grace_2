import { useState, FormEvent, useEffect } from 'react';

export default function App() {
  const [page, setPage] = useState<'chat' | 'dash'>('chat');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState('admin');
  const [pass, setPass] = useState('admin123');
  const [msgs, setMsgs] = useState<any[]>([]);
  const [inp, setInp] = useState('');
  const [metrics, setMetrics] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [refs, setRefs] = useState<any[]>([]);

  async function login(e: FormEvent) {
    e.preventDefault();
    const r = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass })
    });
    const d = await r.json();
    if (d.access_token) {
      setToken(d.access_token);
      localStorage.setItem('token', d.access_token);
    }
  }

  async function send(e: FormEvent) {
    e.preventDefault();
    if (!inp) return;
    
    setMsgs(m => [...m, { r: 'user', c: inp }]);
    const msg = inp;
    setInp('');

    const r = await fetch('http://localhost:8000/api/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ message: msg })
    });
    const d = await r.json();
    setMsgs(m => [...m, { r: 'grace', c: d.response }]);
  }

  useEffect(() => {
    if (page === 'dash' && token) {
      fetch('http://localhost:8000/api/metrics/summary').then(r => r.json()).then(setMetrics);
      fetch('http://localhost:8000/api/tasks/', { headers: { Authorization: `Bearer ${token}` }}).then(r => r.json()).then(setTasks);
      fetch('http://localhost:8000/api/reflections/').then(r => r.json()).then(setRefs);
    }
  }, [page, token]);

  const s = { bg: '#0f0f1e', fg: '#fff', bg2: '#1a1a2e', ac: '#7b2cbf', ac2: '#00d4ff' };

  if (!token) {
    return (
      <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <form onSubmit={login} style={{ background: s.bg2, padding: '2rem', borderRadius: '8px', width: '280px' }}>
          <h1 style={{ color: s.ac2, marginBottom: '1rem' }}>Grace</h1>
          <input value={user} onChange={e => setUser(e.target.value)} style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', background: s.bg, color: s.fg, border: '1px solid #333', borderRadius: '4px' }} />
          <input type="password" value={pass} onChange={e => setPass(e.target.value)} style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem', background: s.bg, color: s.fg, border: '1px solid #333', borderRadius: '4px' }} />
          <button style={{ width: '100%', padding: '0.5rem', background: s.ac, color: s.fg, border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Login</button>
        </form>
      </div>
    );
  }

  if (page === 'dash') {
    return (
      <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
        <button onClick={() => setPage('chat')} style={{ background: s.ac, color: s.fg, border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', marginBottom: '2rem', cursor: 'pointer' }}>← Chat</button>
        
        <h1 style={{ color: s.ac2, marginBottom: '2rem' }}>Dashboard</h1>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: s.ac2, fontWeight: 'bold' }}>{metrics?.total_messages || 0}</div>
            <div style={{ color: '#888' }}>Messages</div>
          </div>
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: s.ac2, fontWeight: 'bold' }}>{metrics?.active_users || 0}</div>
            <div style={{ color: '#888' }}>Users</div>
          </div>
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: s.ac2, fontWeight: 'bold' }}>{refs.length}</div>
            <div style={{ color: '#888' }}>Reflections</div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px' }}>
            <h3 style={{ color: s.ac2, marginBottom: '1rem' }}>Reflections</h3>
            {refs.slice(0, 5).map((r, i) => (
              <div key={i} style={{ background: s.bg, padding: '0.75rem', borderRadius: '6px', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                {r.summary}
              </div>
            ))}
          </div>
          
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px' }}>
            <h3 style={{ color: s.ac2, marginBottom: '1rem' }}>Tasks</h3>
            {tasks.length === 0 && <p style={{ color: '#888' }}>No tasks yet</p>}
            {tasks.slice(0, 5).map((t, i) => (
              <div key={i} style={{ background: t.auto_generated ? 'rgba(123,44,191,0.1)' : s.bg, padding: '0.75rem', borderRadius: '6px', marginBottom: '0.5rem' }}>
                <div style={{ fontWeight: 'bold', fontSize: '0.875rem' }}>{t.auto_generated && '🤖 '}{t.title}</div>
                <div style={{ fontSize: '0.75rem', color: '#888' }}>{t.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '1rem', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between' }}>
        <h1 style={{ color: s.ac2, margin: 0 }}>Grace</h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={() => setPage('dash')} style={{ background: 'none', color: s.ac, border: 'none', cursor: 'pointer' }}>📊 Dashboard</button>
          <button onClick={() => { setToken(''); localStorage.clear(); }} style={{ background: '#333', color: s.fg, border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer' }}>Logout</button>
        </div>
      </div>
      
      <div style={{ flex: 1, padding: '1rem', overflowY: 'auto' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          {msgs.map((m, i) => (
            <div key={i} style={{ marginBottom: '1rem', display: 'flex', justifyContent: m.r === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{ padding: '0.75rem', borderRadius: '8px', background: m.r === 'user' ? s.ac : s.bg2, maxWidth: '70%', color: s.fg }}>
                <b>{m.r === 'user' ? 'You' : 'Grace'}:</b> {m.c}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div style={{ padding: '1rem', borderTop: '1px solid #333' }}>
        <form onSubmit={send} style={{ maxWidth: '600px', margin: '0 auto', display: 'flex', gap: '0.5rem' }}>
          <input value={inp} onChange={e => setInp(e.target.value)} placeholder="Message..." style={{ flex: 1, padding: '0.75rem', background: s.bg2, color: s.fg, border: '1px solid #333', borderRadius: '8px' }} />
          <button style={{ padding: '0.75rem 1.5rem', background: s.ac, color: s.fg, border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>Send</button>
        </form>
      </div>
    </div>
  );
}
