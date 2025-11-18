import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import { RecommendationCard } from './RecommendationCard';

interface Recommendation {
  id: string;
  type: string;
  component: string;
  current_value: number;
  proposed_value: number;
  predicted_impact: number;
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
  reasoning: string;
}

interface AppliedChange {
  id: string;
  recommendation_id: string;
  type: string;
  component: string;
  old_value: number;
  new_value: number;
  applied_at: string;
  approved_by: string;
  before_metrics: any;
  after_metrics: any;
  improvement_pct: number;
}

interface PerformanceData {
  effectiveness_over_time: Array<{ timestamp: string; score: number }>;
  acceptance_rate: number;
  avg_improvement: number;
  component_trends: Record<string, Array<{ timestamp: string; value: number }>>;
}

export function MetaLoopDashboard() {
  const [activeTab, setActiveTab] = useState<'pending' | 'applied' | 'performance'>('pending');
  const [pending, setPending] = useState<Recommendation[]>([]);
  const [applied, setApplied] = useState<AppliedChange[]>([]);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [token] = useState(localStorage.getItem('token') || '');
  const [ws, setWs] = useState<WebSocket | null>(null);

  const s = { bg: '#0f0f1e', fg: '#fff', bg2: '#1a1a2e', ac: '#7b2cbf', ac2: '#00d4ff' };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);

    try {
      const socket = new WebSocket(`${WS_BASE_URL}/ws/meta-updates?token=${token}`);
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'new_recommendation') {
          setPending(prev => [data.recommendation, ...prev]);
        } else if (data.type === 'recommendation_applied') {
          setPending(prev => prev.filter(r => r.id !== data.recommendation_id));
          loadData();
        }
      };
      socket.onerror = (error) => {
        console.log('WebSocket error, will rely on polling');
      };
      setWs(socket);

      return () => {
        clearInterval(interval);
        socket.close();
      };
    } catch (e) {
      console.log('WebSocket not available, using polling only');
      return () => clearInterval(interval);
    }
  }, [token]);

  async function loadData() {
    try {
      const [pendingRes, appliedRes, perfRes] = await Promise.all([
        fetch(apiUrl('/api/meta/recommendations/pending', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(apiUrl('/api/meta/recommendations/applied', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(apiUrl('/api/meta/performance', {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      if (pendingRes.ok) {
        const data = await pendingRes.json();
        setPending(data.recommendations || []);
      }

      if (appliedRes.ok) {
        const data = await appliedRes.json();
        setApplied(data.changes || []);
      }

      if (perfRes.ok) {
        const data = await perfRes.json();
        setPerformance(data);
      }
    } catch (err) {
      console.error('Failed to load meta-loop data:', err);
    }
  }

  async function handleApprove(id: string) {
    try {
      const res = await fetch(`http://localhost:8000/api/meta/recommendations/${id}/approve`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        await loadData();
      }
    } catch (err) {
      console.error('Failed to approve:', err);
    }
  }

  async function handleReject(id: string) {
    try {
      const res = await fetch(`http://localhost:8000/api/meta/recommendations/${id}/reject`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        setPending(prev => prev.filter(r => r.id !== id));
      }
    } catch (err) {
      console.error('Failed to reject:', err);
    }
  }

  async function handleRollback(changeId: string) {
    try {
      const res = await fetch(`http://localhost:8000/api/meta/changes/${changeId}/rollback`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        await loadData();
      }
    } catch (err) {
      console.error('Failed to rollback:', err);
    }
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ color: s.ac2, margin: 0 }}>🧠 Meta-Loop Control Center</h1>
        <a href="/" style={{ background: s.ac, color: s.fg, border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', textDecoration: 'none' }}>← Back</a>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '2px solid #333' }}>
        <button
          onClick={() => setActiveTab('pending')}
          style={{
            background: activeTab === 'pending' ? s.ac : 'transparent',
            color: s.fg,
            border: 'none',
            padding: '1rem 2rem',
            cursor: 'pointer',
            borderBottom: activeTab === 'pending' ? `3px solid ${s.ac2}` : 'none',
            fontSize: '1rem',
            fontWeight: activeTab === 'pending' ? 'bold' : 'normal'
          }}
        >
          ⏳ Pending ({pending.length})
        </button>
        <button
          onClick={() => setActiveTab('applied')}
          style={{
            background: activeTab === 'applied' ? s.ac : 'transparent',
            color: s.fg,
            border: 'none',
            padding: '1rem 2rem',
            cursor: 'pointer',
            borderBottom: activeTab === 'applied' ? `3px solid ${s.ac2}` : 'none',
            fontSize: '1rem',
            fontWeight: activeTab === 'applied' ? 'bold' : 'normal'
          }}
        >
          ✅ Applied ({applied.length})
        </button>
        <button
          onClick={() => setActiveTab('performance')}
          style={{
            background: activeTab === 'performance' ? s.ac : 'transparent',
            color: s.fg,
            border: 'none',
            padding: '1rem 2rem',
            cursor: 'pointer',
            borderBottom: activeTab === 'performance' ? `3px solid ${s.ac2}` : 'none',
            fontSize: '1rem',
            fontWeight: activeTab === 'performance' ? 'bold' : 'normal'
          }}
        >
          📈 Performance
        </button>
      </div>

      {activeTab === 'pending' && (
        <div>
          <h2 style={{ color: s.ac2, marginBottom: '1.5rem' }}>Pending Recommendations</h2>
          {pending.length === 0 && (
            <div style={{ background: s.bg2, padding: '3rem', borderRadius: '8px', textAlign: 'center', color: '#888' }}>
              <p style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🎉</p>
              <p>No pending recommendations. The meta-loop is satisfied with current settings.</p>
            </div>
          )}
          {pending.map(rec => (
            <RecommendationCard
              key={rec.id}
              recommendation={rec}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}

      {activeTab === 'applied' && (
        <div>
          <h2 style={{ color: s.ac2, marginBottom: '1.5rem' }}>Applied Changes History</h2>
          {applied.length === 0 && (
            <div style={{ background: s.bg2, padding: '3rem', borderRadius: '8px', textAlign: 'center', color: '#888' }}>
              <p>No applied changes yet.</p>
            </div>
          )}
          {applied.map(change => {
            const improvement = change.improvement_pct;
            const isPositive = improvement > 0;
            
            return (
              <div key={change.id} style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', marginBottom: '1rem', border: '1px solid #333' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ color: s.ac2, margin: '0 0 0.5rem 0' }}>{change.component}</h3>
                    <div style={{ fontSize: '0.875rem', color: '#888' }}>
                      {change.type} • Applied {new Date(change.applied_at).toLocaleString()} • By {change.approved_by}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: 'bold',
                      color: isPositive ? '#00ff88' : '#ff4444'
                    }}>
                      {isPositive ? '↑' : '↓'} {Math.abs(improvement).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div style={{ background: s.bg, padding: '1rem', borderRadius: '6px', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', gap: '2rem', marginBottom: '0.5rem' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.25rem' }}>Before</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{change.old_value}</div>
                    </div>
                    <div style={{ fontSize: '1.5rem', color: s.ac2, alignSelf: 'center' }}>→</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.25rem' }}>After</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: s.ac2 }}>{change.new_value}</div>
                    </div>
                  </div>
                </div>

                {change.before_metrics && change.after_metrics && (
                  <div style={{ background: s.bg, padding: '1rem', borderRadius: '6px', marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Performance Metrics</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#888' }}>Response Time</div>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <span>{change.before_metrics.response_time?.toFixed(2) || 'N/A'}ms</span>
                          <span style={{ color: s.ac2 }}>→</span>
                          <span style={{ color: s.ac2 }}>{change.after_metrics.response_time?.toFixed(2) || 'N/A'}ms</span>
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#888' }}>Success Rate</div>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <span>{change.before_metrics.success_rate?.toFixed(1) || 'N/A'}%</span>
                          <span style={{ color: s.ac2 }}>→</span>
                          <span style={{ color: s.ac2 }}>{change.after_metrics.success_rate?.toFixed(1) || 'N/A'}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {!isPositive && (
                  <button
                    onClick={() => handleRollback(change.id)}
                    style={{
                      background: '#ff4444',
                      color: s.fg,
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.875rem'
                    }}
                  >
                    ⚠️ Rollback (Performance Degraded)
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}

      {activeTab === 'performance' && (
        <div>
          <h2 style={{ color: s.ac2, marginBottom: '1.5rem' }}>Meta-Loop Performance Analytics</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
            <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Acceptance Rate</div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: s.ac2 }}>
                {performance?.acceptance_rate?.toFixed(1) || 0}%
              </div>
            </div>
            <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Avg Improvement</div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#00ff88' }}>
                +{performance?.avg_improvement?.toFixed(1) || 0}%
              </div>
            </div>
            <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Total Optimizations</div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: s.ac2 }}>
                {applied.length}
              </div>
            </div>
          </div>

          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
            <h3 style={{ color: s.ac2, marginBottom: '1rem' }}>Effectiveness Over Time</h3>
            <div style={{ height: '200px', display: 'flex', alignItems: 'flex-end', gap: '4px' }}>
              {performance?.effectiveness_over_time?.map((point, i) => (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    background: s.ac,
                    height: `${point.score}%`,
                    borderRadius: '4px 4px 0 0',
                    minHeight: '8px',
                    position: 'relative'
                  }}
                  title={`${new Date(point.timestamp).toLocaleString()}: ${point.score.toFixed(1)}%`}
                />
              ))}
            </div>
            {(!performance?.effectiveness_over_time || performance.effectiveness_over_time.length === 0) && (
              <div style={{ textAlign: 'center', color: '#888', padding: '2rem' }}>
                Not enough data yet. Performance tracking starts after first optimization.
              </div>
            )}
          </div>

          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '8px' }}>
            <h3 style={{ color: s.ac2, marginBottom: '1rem' }}>Component Performance Trends</h3>
            {performance?.component_trends && Object.keys(performance.component_trends).length > 0 ? (
              Object.entries(performance.component_trends).map(([component, trends]) => (
                <div key={component} style={{ marginBottom: '1.5rem' }}>
                  <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>{component}</div>
                  <div style={{ height: '80px', display: 'flex', alignItems: 'flex-end', gap: '2px' }}>
                    {trends.map((point, i) => (
                      <div
                        key={i}
                        style={{
                          flex: 1,
                          background: s.ac2,
                          height: `${(point.value / Math.max(...trends.map(t => t.value))) * 100}%`,
                          borderRadius: '2px 2px 0 0',
                          minHeight: '4px'
                        }}
                        title={`${new Date(point.timestamp).toLocaleString()}: ${point.value.toFixed(2)}`}
                      />
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', color: '#888', padding: '2rem' }}>
                No component trends available yet.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
