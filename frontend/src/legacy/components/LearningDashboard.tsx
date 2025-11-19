import { useState, useEffect } from 'react';
import { GraduationCap, TrendingUp, AlertCircle, Activity, Zap } from 'lucide-react';
import { getLearningStatus, type LearningStatus } from '../services/learningApi';

const s = {
  bg: '#0a0a0a',
  bg2: '#1a1a1a',
  fg: '#e0e0e0',
  ac: '#8b5cf6',
  ac2: '#a78bfa'
};

export function LearningDashboard() {
  const [status, setStatus] = useState<LearningStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadStatus() {
    try {
      const data = await getLearningStatus();
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
        <div style={{ fontSize: '1.5rem' }}>Loading learning system...</div>
      </div>
    );
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ color: s.ac2, marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <GraduationCap size={32} />
          Continuous Learning Loop
        </h1>

        {error && (
          <div style={{ background: '#991b1b', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={20} />
            Error: {error}
          </div>
        )}

        {/* Status Card */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <Activity size={24} style={{ color: s.ac }} />
            <h2 style={{ margin: 0, color: s.ac2 }}>System Status</h2>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
            <div>
              <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Status</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: status?.status === 'available' ? '#10b981' : '#f59e0b' }}>
                {status?.status || 'Unknown'}
              </div>
            </div>
            
            <div>
              <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Component</div>
              <div style={{ fontSize: '1rem', fontWeight: 'bold' }}>
                {status?.component || 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* About Learning Loop */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px' }}>
          <h2 style={{ color: s.ac, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Zap size={20} />
            About Continuous Learning
          </h2>
          
          <div style={{ fontSize: '0.875rem', lineHeight: '1.6', color: '#d1d5db' }}>
            <p style={{ marginBottom: '1rem' }}>
              Grace's Continuous Learning Loop enables the system to learn from every action:
            </p>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
              <div style={{ background: s.bg, padding: '1.5rem', borderRadius: '8px' }}>
                <div style={{ fontWeight: 'bold', color: s.ac2, marginBottom: '0.5rem' }}>Mission Learning</div>
                <div style={{ fontSize: '0.875rem', color: '#888' }}>
                  Extracts patterns from mission outcomes
                </div>
              </div>
              
              <div style={{ background: s.bg, padding: '1.5rem', borderRadius: '8px' }}>
                <div style={{ fontWeight: 'bold', color: s.ac2, marginBottom: '0.5rem' }}>Healing Learning</div>
                <div style={{ fontSize: '0.875rem', color: '#888' }}>
                  Updates playbooks from healing actions
                </div>
              </div>
              
              <div style={{ background: s.bg, padding: '1.5rem', borderRadius: '8px' }}>
                <div style={{ fontWeight: 'bold', color: s.ac2, marginBottom: '0.5rem' }}>Code Learning</div>
                <div style={{ fontSize: '0.875rem', color: '#888' }}>
                  Improves templates from generated code
                </div>
              </div>
              
              <div style={{ background: s.bg, padding: '1.5rem', borderRadius: '8px' }}>
                <div style={{ fontWeight: 'bold', color: s.ac2, marginBottom: '0.5rem' }}>Pattern Recognition</div>
                <div style={{ fontSize: '0.875rem', color: '#888' }}>
                  Identifies and reinforces successful patterns
                </div>
              </div>
            </div>

            {status?.error && (
              <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', padding: '1rem', borderRadius: '8px', marginTop: '1.5rem' }}>
                <strong style={{ color: '#ef4444' }}>Error:</strong> {status.error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
