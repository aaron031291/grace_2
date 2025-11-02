import { useEffect, useState } from 'react';

export function HunterDashboard() {
  const token = localStorage.getItem('token');
  const [alerts, setAlerts] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);

  useEffect(() => {
    if (token) {
      const load = () => {
        fetch('http://localhost:8000/api/hunter/alerts')
          .then(r => r.json())
          .then(setAlerts);
        
        fetch('http://localhost:8000/api/hunter/rules')
          .then(r => r.json())
          .then(setRules);
      };
      load();
      const int = setInterval(load, 10000);
      return () => clearInterval(int);
    }
  }, [token]);

  const resolve = async (id: number, status: string, note: string) => {
    await fetch(`http://localhost:8000/api/hunter/alerts/${id}/resolve?status=${status}&note=${note}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    
    setAlerts(alerts.filter(a => a.id !== id));
  };

  const s = { bg: '#0f0f1e', fg: '#fff', bg2: '#1a1a2e', ac: '#7b2cbf', ac2: '#00d4ff' };

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <a href="/" style={{ color: s.ac, marginBottom: '1rem', display: 'block' }}>← Back</a>
      
      <h1 style={{ color: s.ac2, marginBottom: '2rem' }}>🛡️ Hunter Protocol</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        <div>
          <h2 style={{ color: s.ac2, fontSize: '1.25rem', marginBottom: '1rem' }}>
            Security Alerts ({alerts.filter(a => a.status === 'open').length} open)
          </h2>
          
          {alerts.length === 0 && (
            <div style={{ background: s.bg2, padding: '2rem', borderRadius: '8px', textAlign: 'center', color: '#888' }}>
              ✅ No security alerts - All systems secure
            </div>
          )}
          
          {alerts.map((alert) => (
            <div
              key={alert.id}
              style={{
                background: s.bg2,
                padding: '1.5rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                border: `1px solid ${alert.severity === 'critical' ? '#ff4444' : alert.severity === 'high' ? '#ff8844' : '#ffcc44'}`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <div>
                  <div style={{ fontSize: '1.125rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    {alert.severity === 'critical' && '🔴'} 
                    {alert.severity === 'high' && '🟠'}
                    {alert.severity === 'medium' && '🟡'}
                    {' '}{alert.action}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#888' }}>
                    {new Date(alert.created_at).toLocaleString()} · {alert.actor}
                  </div>
                </div>
                <div style={{
                  padding: '0.25rem 0.75rem',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  background: alert.status === 'open' ? 'rgba(255,200,0,0.2)' : 'rgba(0,255,136,0.2)',
                  color: alert.status === 'open' ? '#ffcc00' : '#00ff88'
                }}>
                  {alert.status}
                </div>
              </div>
              
              <div style={{ marginBottom: '0.75rem', fontSize: '0.875rem' }}>
                Resource: <code style={{ background: s.bg, padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                  {alert.resource}
                </code>
              </div>
              
              {alert.status === 'open' && (
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                  <button
                    onClick={() => resolve(alert.id, 'resolved', 'Reviewed and safe')}
                    style={{ padding: '0.5rem 1rem', background: '#00ff88', color: '#000', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 'bold' }}
                  >
                    ✓ Resolve
                  </button>
                  <button
                    onClick={() => resolve(alert.id, 'ignored', 'False positive')}
                    style={{ padding: '0.5rem 1rem', background: '#666', color: s.fg, border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem' }}
                  >
                    Ignore
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div>
          <h2 style={{ color: s.ac2, fontSize: '1.25rem', marginBottom: '1rem' }}>
            Security Rules ({rules.length})
          </h2>
          
          {rules.map((rule) => (
            <div key={rule.id} style={{ background: s.bg2, padding: '1rem', borderRadius: '8px', marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 'bold', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                {rule.name}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.5rem' }}>
                {rule.description}
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.7rem' }}>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  background: rule.severity === 'critical' ? 'rgba(255,68,68,0.2)' : 'rgba(255,200,0,0.2)',
                  color: rule.severity === 'critical' ? '#ff4444' : '#ffcc00'
                }}>
                  {rule.severity}
                </span>
                <span style={{ padding: '0.25rem 0.5rem', borderRadius: '4px', background: 'rgba(123,44,191,0.2)', color: s.ac }}>
                  {rule.action}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
