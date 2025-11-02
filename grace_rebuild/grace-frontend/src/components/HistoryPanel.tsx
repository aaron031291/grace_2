import { useEffect, useState } from 'react';
import { useAuth } from './AuthProvider';

interface HistoryMessage {
  id: number;
  user: string;
  role: string;
  content: string;
  created_at: string;
}

export function HistoryPanel() {
  const { token } = useAuth();
  const [history, setHistory] = useState<HistoryMessage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    
    const fetchHistory = () => {
      fetch("http://localhost:8000/api/memory/history?limit=50", {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then((res) => res.json())
        .then(setHistory)
        .catch(console.error)
        .finally(() => setLoading(false));
    };

    fetchHistory();
    const interval = setInterval(fetchHistory, 15000);
    return () => clearInterval(interval);
  }, [token]);

  if (!token) return null;
  if (loading) return <div style={{ padding: '1rem', color: '#888' }}>Loading history...</div>;

  return (
    <section style={{ marginTop: '1rem', padding: '1rem', background: '#1a1a2e', borderRadius: '8px', border: '1px solid #333' }}>
      <h3 style={{ margin: '0 0 1rem 0', color: '#00d4ff', fontSize: '1rem' }}>Conversation History</h3>
      <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
        {history.length === 0 && <p style={{ color: '#888', fontSize: '0.875rem' }}>No history yet.</p>}
        {history.map((msg) => (
          <div key={msg.id} style={{ marginBottom: '0.75rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>
              {new Date(msg.created_at).toLocaleString()} · {msg.role.toUpperCase()}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#e0e0e0', whiteSpace: 'pre-wrap' }}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
