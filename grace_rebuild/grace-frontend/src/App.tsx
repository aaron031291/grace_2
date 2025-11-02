import { useState, FormEvent } from 'react';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState('admin');
  const [pass, setPass] = useState('admin123');
  const [msgs, setMsgs] = useState<any[]>([]);
  const [inp, setInp] = useState('');

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

    try {
      const r = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ message: msg })
      });
      const d = await r.json();
      setMsgs(m => [...m, { r: 'grace', c: d.response }]);
    } catch {
      setMsgs(m => [...m, { r: 'grace', c: 'Error' }]);
    }
  }

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

  return (
    <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '1rem', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between' }}>
        <h1 style={{ color: s.ac2, margin: 0 }}>Grace</h1>
        <button onClick={() => { setToken(''); localStorage.clear(); }} style={{ background: '#333', color: s.fg, border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer' }}>Logout</button>
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
          <button style={{ padding: '0.75rem 1.5rem', background: s.ac, color: s.fg, border: 'none', borderRadius: '8px', cursor: 'pointer' }}>Send</button>
        </form>
      </div>
    </div>
  );
}
