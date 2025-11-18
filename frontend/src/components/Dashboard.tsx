import { useEffect, useState } from 'react';
import { apiUrl, WS_BASE_URL } from './config';

export function Dashboard() {
  const token = localStorage.getItem('token');
  const [metrics, setMetrics] = useState<any>(null);
  const [causal, setCausal] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [reflections, setReflections] = useState<any[]>([]);

  useEffect(() => {
    fetch(apiUrl('/api/metrics/summary')
      .then(r => r.json())
      .then(setMetrics);
    
    if (token) {
      fetch(apiUrl('/api/causal/patterns', {
        headers: { Authorization: `Bearer ${token}` }
      }).then(r => r.json()).then(setCausal);

      fetch(apiUrl('/api/tasks/', {
        headers: { Authorization: `Bearer ${token}` }
      }).then(r => r.json()).then(setTasks);

      fetch(apiUrl('/api/reflections/')
        .then(r => r.json())
        .then(setReflections);
    }
  }, [token]);

  return (
    <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      <a href="/" style={{ color: '#7b2cbf', marginBottom: '1rem', display: 'block' }}>← Back to Chat</a>
      
      <h1 style={{ color: '#00d4ff', marginBottom: '2rem' }}>Grace Analytics Dashboard</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', textAlign: 'center' }}>
          <div style={{ fontSize: '0.875rem', color: '#7b2cbf', marginBottom: '0.5rem' }}>MESSAGES</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#00d4ff' }}>{metrics?.total_messages || 0}</div>
        </div>
        
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', textAlign: 'center' }}>
          <div style={{ fontSize: '0.875rem', color: '#7b2cbf', marginBottom: '0.5rem' }}>USERS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#00d4ff' }}>{metrics?.active_users || 0}</div>
        </div>
        
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', textAlign: 'center' }}>
          <div style={{ fontSize: '0.875rem', color: '#7b2cbf', marginBottom: '0.5rem' }}>INTERACTIONS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#00d4ff' }}>{causal?.total_interactions || 0}</div>
        </div>
        
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', textAlign: 'center' }}>
          <div style={{ fontSize: '0.875rem', color: '#7b2cbf', marginBottom: '0.5rem' }}>UNHANDLED</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#00d4ff' }}>{causal?.unhandled_rate || 0}%</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Reflections ({reflections.length})</h3>
          {reflections.slice(0, 5).map((r, i) => (
            <div key={i} style={{ background: 'rgba(0,212,255,0.05)', padding: '1rem', borderRadius: '8px', marginBottom: '0.75rem', border: '1px solid rgba(0,212,255,0.2)' }}>
              <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>{r.summary}</div>
              {r.insight && <div style={{ fontSize: '0.75rem', color: '#7b2cbf', fontStyle: 'italic' }}>{r.insight}</div>}
            </div>
          ))}
        </div>

        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Tasks ({tasks.filter(t => t.auto_generated).length} auto)</h3>
          {tasks.length === 0 && <p style={{ color: '#888' }}>Chat more to generate tasks...</p>}
          {tasks.slice(0, 5).map((t, i) => (
            <div key={i} style={{ background: t.auto_generated ? 'rgba(123,44,191,0.1)' : 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '8px', marginBottom: '0.75rem', border: '1px solid ' + (t.auto_generated ? '#7b2cbf' : '#333') }}>
              <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>{t.auto_generated && '🤖 '}{t.title}</div>
              <div style={{ fontSize: '0.75rem', color: '#888' }}>{t.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
