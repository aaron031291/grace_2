/**
 * Overview Tab - System-wide dashboard
 */

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const s = {
  bg: '#0a0a0a',
  bg2: '#1a1a1a',
  fg: '#e0e0e0',
  ac: '#8b5cf6',
  ac2: '#a78bfa',
};

export default function OverviewTab() {
  const [status, setStatus] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [clarity, setClarity] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [statusRes, healthRes, clarityRes] = await Promise.all([
        axios.get(`${API_BASE}/api/status`),
        axios.get(`${API_BASE}/health`),
        axios.get(`${API_BASE}/api/clarity/status`),
      ]);

      setStatus(statusRes.data);
      setHealth(healthRes.data);
      setClarity(clarityRes.data);
    } catch (error) {
      console.error('Failed to load overview:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={{ background: s.bg, padding: '2rem', color: s.fg }}>
        <div style={{ textAlign: 'center', fontSize: '1.5rem' }}>Loading Grace Overview...</div>
      </div>
    );
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <h1 style={{ color: s.ac2, marginBottom: '2rem', fontSize: '2rem' }}>Grace System Overview</h1>

        {/* Status Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          {/* Health */}
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>System Health</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: health?.status === 'healthy' ? '#10b981' : '#f59e0b' }}>
              {health?.status || 'Unknown'}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.5rem' }}>
              Platform: {health?.platform || 'N/A'}
            </div>
          </div>

          {/* Imports */}
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Import Status</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: status?.imports_successful ? '#10b981' : '#ef4444' }}>
              {status?.imports_successful ? 'Success' : 'Failed'}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.5rem' }}>
              Errors: {status?.import_errors?.length || 0}
            </div>
          </div>

          {/* Components */}
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Active Components</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: s.ac2 }}>
              {clarity?.manifest?.active_components || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.5rem' }}>
              Total: {clarity?.manifest?.total_components || 0}
            </div>
          </div>

          {/* Events */}
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Events Processed</div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: s.ac2 }}>
              {clarity?.event_bus?.total_events || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.5rem' }}>
              Subscribers: {clarity?.event_bus?.subscriber_count || 0}
            </div>
          </div>
        </div>

        {/* System Details */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px', marginBottom: '2rem' }}>
          <h2 style={{ color: s.ac, marginBottom: '1.5rem' }}>System Information</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem' }}>
            <div>
              <div style={{ color: '#888', marginBottom: '0.25rem' }}>Boot ID</div>
              <div style={{ fontFamily: 'monospace', color: s.fg }}>{status?.boot_id || 'N/A'}</div>
            </div>
            <div>
              <div style={{ color: '#888', marginBottom: '0.25rem' }}>Environment</div>
              <div style={{ fontFamily: 'monospace', color: s.fg }}>{status?.environment || 'N/A'}</div>
            </div>
            <div>
              <div style={{ color: '#888', marginBottom: '0.25rem' }}>Platform</div>
              <div style={{ fontFamily: 'monospace', color: s.fg }}>{status?.platform?.platform || 'N/A'}</div>
            </div>
            <div>
              <div style={{ color: '#888', marginBottom: '0.25rem' }}>Python</div>
              <div style={{ fontFamily: 'monospace', color: s.fg }}>{status?.platform?.python || 'N/A'}</div>
            </div>
            <div>
              <div style={{ color: '#888', marginBottom: '0.25rem' }}>Started At</div>
              <div style={{ fontFamily: 'monospace', color: s.fg }}>
                {status?.started_at ? new Date(status.started_at).toLocaleString() : 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ color: '#888', marginBottom: '0.25rem' }}>Domain Kernels</div>
              <div style={{ fontFamily: 'monospace', color: '#10b981', fontWeight: 'bold' }}>
                {status?.components?.domain_kernels || 0}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px' }}>
          <h2 style={{ color: s.ac, marginBottom: '1.5rem' }}>Quick Actions</h2>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: s.ac, color: '#fff', padding: '0.75rem 1.5rem', borderRadius: '6px', textDecoration: 'none', fontWeight: 'bold' }}
            >
              📚 API Documentation
            </a>
            <a
              href="http://localhost:8000/health"
              target="_blank"
              rel="noopener noreferrer"
              style={{ background: '#10b981', color: '#fff', padding: '0.75rem 1.5rem', borderRadius: '6px', textDecoration: 'none', fontWeight: 'bold' }}
            >
              ❤️ Health Check
            </a>
            <button
              onClick={() => window.location.reload()}
              style={{ background: '#3b82f6', color: '#fff', border: 'none', padding: '0.75rem 1.5rem', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              🔄 Refresh Data
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
