import React, { useState, useEffect } from 'react';

interface MetricsData {
  self_healing: {
    total_runs: number;
    successful_runs: number;
    average_success_rate: number;
    average_execution_time_ms: number;
    mttr_minutes: number;
  };
  ingestion: {
    total_ingested: number;
    throughput_per_hour: number;
    average_processing_time_ms: number;
    success_rate: number;
  };
  verification: {
    total_verifications: number;
    passed_verifications: number;
    average_trust_score: number;
    anomalies_detected: number;
  };
  trust_levels: {
    overall_trust: number;
    librarian_trust: number;
    verification_trust: number;
    recent_dips: any[];
  };
}

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/self-healing/comprehensive-metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Loading metrics dashboard...
      </div>
    );
  }

  if (!metrics) {
    return (
      <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#ff6b6b' }}>
        Failed to load metrics data
      </div>
    );
  }

  const { self_healing, ingestion, verification, trust_levels } = metrics;

  return (
    <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ color: '#00d4ff', marginBottom: '0.5rem', fontSize: '2rem', fontWeight: 'bold' }}>
            Grace Metrics Dashboard
          </h1>
          <p style={{ color: '#888' }}>System performance and trust monitoring</p>
        </div>
        <button
          onClick={fetchMetrics}
          style={{
            background: '#7b2cbf',
            color: '#fff',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Refresh
        </button>
      </div>

      {/* Trust Overview */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h2 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Trust Levels</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
              {Math.round(trust_levels.overall_trust * 100)}%
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Overall Trust</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4ade80' }}>
              {Math.round(trust_levels.librarian_trust * 100)}%
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Librarian Trust</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fbbf24' }}>
              {Math.round(trust_levels.verification_trust * 100)}%
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Verification Trust</div>
          </div>
        </div>

        {trust_levels.recent_dips.length > 0 && (
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(255, 107, 107, 0.1)', borderRadius: '8px', border: '1px solid #ff6b6b' }}>
            <h3 style={{ color: '#ff6b6b', marginBottom: '0.5rem' }}>⚠️ Recent Trust Dips</h3>
            {trust_levels.recent_dips.slice(0, 3).map((dip: any, idx: number) => (
              <div key={idx} style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                {dip.component}: {Math.round(dip.old_trust * 100)}% → {Math.round(dip.new_trust * 100)}%
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Self-Healing Metrics */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h2 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Self-Healing Performance</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
              {self_healing.total_runs}
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Total Runs</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4ade80' }}>
              {Math.round(self_healing.average_success_rate * 100)}%
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Success Rate</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fbbf24' }}>
              {Math.round(self_healing.mttr_minutes)}m
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Mean Time to Recovery</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#a78bfa' }}>
              {Math.round(self_healing.average_execution_time_ms)}ms
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Avg Execution Time</div>
          </div>
        </div>
      </div>

      {/* Ingestion Metrics */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h2 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Ingestion Pipeline</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
              {ingestion.total_ingested}
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Total Ingested</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4ade80' }}>
              {ingestion.throughput_per_hour}
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Throughput/hr</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fbbf24' }}>
              {Math.round(ingestion.average_processing_time_ms)}ms
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Avg Processing Time</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#a78bfa' }}>
              {Math.round(ingestion.success_rate * 100)}%
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Success Rate</div>
          </div>
        </div>
      </div>

      {/* Verification Metrics */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h2 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Verification & Trust</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
              {verification.total_verifications}
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Total Verifications</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4ade80' }}>
              {Math.round((verification.passed_verifications / Math.max(verification.total_verifications, 1)) * 100)}%
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Pass Rate</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fbbf24' }}>
              {Math.round(verification.average_trust_score * 100)}%
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Avg Trust Score</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ff6b6b' }}>
              {verification.anomalies_detected}
            </div>
            <div style={{ color: '#888', fontSize: '0.875rem' }}>Anomalies Detected</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
        <h2 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Recent Activity</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          <div>
            <h3 style={{ color: '#7b2cbf', marginBottom: '0.5rem' }}>Latest Self-Healing Runs</h3>
            <div style={{ color: '#ccc', fontSize: '0.875rem' }}>
              Self-healing execution logs will appear here...
            </div>
          </div>
          <div>
            <h3 style={{ color: '#7b2cbf', marginBottom: '0.5rem' }}>Ingestion Activity</h3>
            <div style={{ color: '#ccc', fontSize: '0.875rem' }}>
              Recent ingestion jobs and throughput metrics...
            </div>
          </div>
          <div>
            <h3 style={{ color: '#7b2cbf', marginBottom: '0.5rem' }}>Trust Changes</h3>
            <div style={{ color: '#ccc', fontSize: '0.875rem' }}>
              Recent trust score changes and anomalies...
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}