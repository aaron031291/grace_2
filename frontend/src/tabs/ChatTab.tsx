/**
 * Chat Tab - Main chat interface
 */

import { useState, type FormEvent } from 'react';
import axios from 'axios';
import { ModelIndicator } from '../components/ModelIndicator';
import { API_BASE_URL } from '../config';

const s = {
  bg: '#0a0a0a',
  bg2: '#1a1a1a',
  fg: '#e0e0e0',
  ac: '#8b5cf6',
  ac2: '#a78bfa',
};

interface Message {
  r: 'user' | 'grace';
  c: string;
}

export default function ChatTab() {
  const [msgs, setMsgs] = useState<Message[]>([]);
  const [inp, setInp] = useState('');
  const [loading, setLoading] = useState(false);

  async function send(e: FormEvent) {
    e.preventDefault();
    if (!inp || loading) return;

    setMsgs((m) => [...m, { r: 'user', c: inp }]);
    const msg = inp;
    setInp('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, { message: msg });
      setMsgs((m) => [...m, { r: 'grace', c: response.data.response }]);
    } catch (error) {
      setMsgs((m) => [...m, { r: 'grace', c: 'Error: Failed to send message' }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header with model indicator */}
      <div style={{ padding: '1rem', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, color: s.fg }}>💻 Coding Agent</h2>
        <ModelIndicator kernelId="coding_agent" />
      </div>
      
      <div style={{ flex: 1, padding: '1rem', overflowY: 'auto' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          {msgs.map((m, i) => (
            <div
              key={i}
              style={{
                marginBottom: '1rem',
                textAlign: m.r === 'user' ? 'right' : 'left',
              }}
            >
              <div
                style={{
                  display: 'inline-block',
                  background: m.r === 'user' ? s.ac : s.bg2,
                  color: s.fg,
                  padding: '0.75rem 1rem',
                  borderRadius: '12px',
                  maxWidth: '80%',
                  textAlign: 'left',
                }}
              >
                {m.c}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ textAlign: 'center', color: '#888', fontSize: '0.875rem' }}>
              Grace is thinking...
            </div>
          )}
        </div>
      </div>

      <div style={{ padding: '1rem', borderTop: '1px solid #333' }}>
        <form onSubmit={send} style={{ maxWidth: '600px', margin: '0 auto', display: 'flex', gap: '0.5rem' }}>
          <input
            value={inp}
            onChange={(e) => setInp(e.target.value)}
            placeholder="Message Grace..."
            disabled={loading}
            style={{
              flex: 1,
              background: s.bg2,
              color: s.fg,
              border: '1px solid #333',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              fontSize: '1rem',
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              background: s.ac,
              color: '#fff',
              border: 'none',
              padding: '0.75rem 2rem',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              opacity: loading ? 0.5 : 1,
            }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
