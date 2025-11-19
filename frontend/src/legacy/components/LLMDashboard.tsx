import { useState, useEffect } from 'react';
import { Brain, Zap, TrendingUp, AlertCircle } from 'lucide-react';
import { getLLMStatus, type LLMStatus } from '../services/llmApi';

const s = {
  bg: '#0a0a0a',
  bg2: '#1a1a1a',
  fg: '#e0e0e0',
  ac: '#8b5cf6',
  ac2: '#a78bfa'
};

export function LLMDashboard() {
  const [status, setStatus] = useState<LLMStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadStatus() {
    try {
      const data = await getLLMStatus();
      setStatus(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: s.fg }}>
        <div style={{ fontSize: '1.5rem' }}>Loading LLM status...</div>
      </div>
    );
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ color: s.ac2, marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Brain size={32} />
          Grace LLM System
        </h1>

        {error && (
          <div style={{ background: '#991b1b', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={20} />
            Error: {error}
          </div>
        )}

        {/* Status Card */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px', marginBottom: '2rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
            <div>
              <div style={{ color: '#888', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Status</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  background: status?.status === 'operational' ? '#10b981' : '#f59e0b'
                }}></div>
                <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: s.ac2 }}>
                  {status?.status || 'Unknown'}
                </span>
              </div>
            </div>

            <div>
              <div style={{ color: '#888', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Model</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{status?.model || 'N/A'}</div>
            </div>

            <div>
              <div style={{ color: '#888', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Mode</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
                {status?.is_stub ? 'Stub Mode' : 'Live'}
              </div>
            </div>

            <div>
              <div style={{ color: '#888', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Available</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: status?.available ? '#10b981' : '#ef4444' }}>
                {status?.available ? 'Yes' : 'No'}
              </div>
            </div>
          </div>
        </div>

        {/* Info Card */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px' }}>
          <h2 style={{ color: s.ac, marginBottom: '1.5rem' }}>LLM Configuration</h2>
          
          {status?.is_stub ? (
            <div style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid #f59e0b', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'start', gap: '0.75rem' }}>
                <Zap size={20} style={{ color: '#f59e0b', flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: '#f59e0b' }}>
                    Stub Mode Active
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#d1d5db' }}>
                    The LLM system is running in stub mode. This means responses are simulated.
                    To enable real LLM integration, configure the grace_llm module in backend/grace_llm.py
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10b981', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'start', gap: '0.75rem' }}>
                <TrendingUp size={20} style={{ color: '#10b981', flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: '#10b981' }}>
                    LLM System Operational
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#d1d5db' }}>
                    The Grace LLM system is running and processing requests.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
