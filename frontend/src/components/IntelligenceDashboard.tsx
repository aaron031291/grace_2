import { useState, useEffect } from 'react';
import { Lightbulb, Activity, AlertCircle } from 'lucide-react';
import { getIntelligenceStatus, type IntelligenceStatus } from '../services/intelligenceApi';

const s = {
  bg: '#0a0a0a',
  bg2: '#1a1a1a',
  fg: '#e0e0e0',
  ac: '#8b5cf6',
  ac2: '#a78bfa'
};

export function IntelligenceDashboard() {
  const [status, setStatus] = useState<IntelligenceStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadStatus() {
    try {
      const data = await getIntelligenceStatus();
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
        <div style={{ fontSize: '1.5rem' }}>Loading Intelligence Kernel...</div>
      </div>
    );
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ color: s.ac2, marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Lightbulb size={32} />
          Intelligence Kernel
        </h1>

        {error && (
          <div style={{ background: '#991b1b', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={20} />
            Error: {error}
          </div>
        )}

        {/* Status Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <Activity size={24} style={{ color: s.ac }} />
              <h3 style={{ margin: 0, color: s.ac2 }}>Kernel Status</h3>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: status?.status === 'operational' ? '#10b981' : '#f59e0b' }}>
              {status?.status || 'Unknown'}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#888', marginTop: '0.5rem' }}>
              {status?.is_stub ? 'Running in stub mode' : 'Fully operational'}
            </div>
          </div>

          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px' }}>
            <h3 style={{ color: s.ac2, marginBottom: '1rem' }}>Kernel Type</h3>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
              {status?.kernel_type || 'N/A'}
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px' }}>
          <h2 style={{ color: s.ac, marginBottom: '1.5rem' }}>About Intelligence Kernel</h2>
          <div style={{ fontSize: '0.875rem', lineHeight: '1.6', color: '#d1d5db' }}>
            <p style={{ marginBottom: '1rem' }}>
              The Intelligence Kernel is one of Grace's 9 domain kernels. It handles:
            </p>
            <ul style={{ marginLeft: '1.5rem', marginBottom: '1rem' }}>
              <li>Cognitive reasoning and decision-making</li>
              <li>Pattern recognition and analysis</li>
              <li>Insight generation from data</li>
              <li>Strategic planning and optimization</li>
            </ul>
            {status?.is_stub && (
              <div style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid #f59e0b', padding: '1rem', borderRadius: '8px', marginTop: '1rem' }}>
                <strong style={{ color: '#f59e0b' }}>Note:</strong> Currently running in stub mode. 
                Configure the intelligence kernel in backend/kernels/intelligence_kernel.py to enable full functionality.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
