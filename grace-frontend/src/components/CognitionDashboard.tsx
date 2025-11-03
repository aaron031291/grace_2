/**
 * Cognition Dashboard Component
 * Displays Grace's cognitive health across all domains
 */

import { useEffect, useState } from 'react';
import { getCognitionStatus, CognitionStatus } from '../api/graceApi';

export function CognitionDashboard() {
  const [status, setStatus] = useState<CognitionStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const data = await getCognitionStatus();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load status');
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
    const interval = setInterval(loadStatus, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="loading">Loading Grace status...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <h2>Backend Connection Error</h2>
        <p>{error}</p>
        <p>Make sure backend is running on http://localhost:8000</p>
        <code>cd grace_rebuild && py minimal_backend.py</code>
      </div>
    );
  }

  if (!status) return null;

  return (
    <div className="cognition-dashboard">
      <h1>Grace Cognition Dashboard</h1>
      
      <div className="overall-metrics">
        <MetricCard 
          label="Overall Health" 
          value={status.overall_health} 
          color={getHealthColor(status.overall_health)}
        />
        <MetricCard 
          label="Overall Trust" 
          value={status.overall_trust} 
          color={getHealthColor(status.overall_trust)}
        />
        <MetricCard 
          label="Overall Confidence" 
          value={status.overall_confidence} 
          color={getHealthColor(status.overall_confidence)}
        />
        <MetricCard 
          label="SaaS Ready" 
          value={status.saas_ready ? 'YES' : 'NO'} 
          color={status.saas_ready ? '#4ade80' : '#fbbf24'}
        />
      </div>

      <h2>Domain Performance</h2>
      <div className="domain-grid">
        {Object.entries(status.domains).map(([name, data]) => (
          <DomainCard key={name} name={name} data={data} />
        ))}
      </div>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: number | string; color: string }) {
  const displayValue = typeof value === 'number' 
    ? `${(value * 100).toFixed(1)}%` 
    : value;

  return (
    <div className="metric-card" style={{ borderColor: color }}>
      <div className="label">{label}</div>
      <div className="value" style={{ color }}>{displayValue}</div>
    </div>
  );
}

function DomainCard({ name, data }: { name: string; data: any }) {
  return (
    <div className="domain-card">
      <h3>{name.charAt(0).toUpperCase() + name.slice(1)}</h3>
      <div className="domain-metrics">
        <div>Health: {(data.health * 100).toFixed(1)}%</div>
        <div>Trust: {(data.trust * 100).toFixed(1)}%</div>
        <div>Confidence: {(data.confidence * 100).toFixed(1)}%</div>
      </div>
      <div className="kpis">
        {Object.entries(data.kpis || {}).slice(0, 3).map(([key, val]: [string, any]) => (
          <div key={key} className="kpi">
            {key}: {typeof val === 'number' && val <= 1 
              ? `${(val * 100).toFixed(0)}%` 
              : val}
          </div>
        ))}
      </div>
    </div>
  );
}

function getHealthColor(value: number): string {
  if (value >= 0.9) return '#4ade80'; // green
  if (value >= 0.7) return '#fbbf24'; // yellow
  return '#f87171'; // red
}
