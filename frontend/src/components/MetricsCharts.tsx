/**
 * Metrics Charts Component
 * 
 * Visualizes comprehensive metrics with charts and tables
 */

import React, { useState, useEffect } from 'react';
import { getComprehensiveMetrics, type ComprehensiveMetrics } from '../api/comprehensive';
import './MetricsCharts.css';

export const MetricsCharts: React.FC = () => {
  const [metrics, setMetrics] = useState<ComprehensiveMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await getComprehensiveMetrics();
      setMetrics(data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch metrics:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return <div className="metrics-loading">Loading metrics...</div>;
  }

  if (error) {
    return <div className="metrics-error">⚠️ {error}</div>;
  }

  if (!metrics) {
    return <div className="metrics-error">No metrics available</div>;
  }

  return (
    <div className="metrics-charts">
      <div className="metrics-header">
        <h2>📊 Comprehensive Metrics</h2>
        <button className="refresh-btn" onClick={fetchMetrics}>🔄 Refresh</button>
      </div>

      <div className="metrics-grid">
        {/* Self-Healing Metrics */}
        <div className="metric-card">
          <h3>🔧 Self-Healing Performance</h3>
          <div className="metric-stats">
            <div className="stat-row">
              <span className="stat-label">Total Runs:</span>
              <span className="stat-value">{metrics.self_healing.total_runs}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Success Rate:</span>
              <span className="stat-value highlight">
                {(metrics.self_healing.average_success_rate * 100).toFixed(1)}%
              </span>
              <div className="stat-bar">
                <div 
                  className="stat-bar-fill success"
                  style={{ width: `${metrics.self_healing.average_success_rate * 100}%` }}
                />
              </div>
            </div>
            <div className="stat-row">
              <span className="stat-label">MTTR:</span>
              <span className="stat-value">{metrics.self_healing.mttr_minutes.toFixed(2)} min</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Avg Execution:</span>
              <span className="stat-value">{metrics.self_healing.average_execution_time_ms.toFixed(0)} ms</span>
            </div>
          </div>
        </div>

        {/* Ingestion Metrics */}
        <div className="metric-card">
          <h3>📚 Data Ingestion</h3>
          <div className="metric-stats">
            <div className="stat-row">
              <span className="stat-label">Total Ingested:</span>
              <span className="stat-value">{metrics.ingestion.total_ingested}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Chunks Processed:</span>
              <span className="stat-value">{metrics.ingestion.chunks_processed}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Success Rate:</span>
              <span className="stat-value highlight">
                {(metrics.ingestion.success_rate * 100).toFixed(1)}%
              </span>
              <div className="stat-bar">
                <div 
                  className="stat-bar-fill success"
                  style={{ width: `${metrics.ingestion.success_rate * 100}%` }}
                />
              </div>
            </div>
            <div className="stat-row">
              <span className="stat-label">Avg Chunk Time:</span>
              <span className="stat-value">{metrics.ingestion.average_chunk_time_ms.toFixed(0)} ms</span>
            </div>
          </div>
        </div>

        {/* Verification Metrics */}
        <div className="metric-card">
          <h3>✅ Verification</h3>
          <div className="metric-stats">
            <div className="stat-row">
              <span className="stat-label">Total Verifications:</span>
              <span className="stat-value">{metrics.verification.total_verifications}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Passed:</span>
              <span className="stat-value success">{metrics.verification.passed}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Failed:</span>
              <span className="stat-value error">{metrics.verification.failed}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Pass Rate:</span>
              <span className="stat-value highlight">
                {(metrics.verification.pass_rate * 100).toFixed(1)}%
              </span>
              <div className="stat-bar">
                <div 
                  className={`stat-bar-fill ${metrics.verification.pass_rate >= 0.8 ? 'success' : 'warning'}`}
                  style={{ width: `${metrics.verification.pass_rate * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Trust Levels */}
        <div className="metric-card">
          <h3>🛡️ Trust Distribution</h3>
          <div className="metric-stats">
            <div className="stat-row">
              <span className="stat-label">High Trust:</span>
              <span className="stat-value success">{metrics.trust_levels.high_trust}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Medium Trust:</span>
              <span className="stat-value warning">{metrics.trust_levels.medium_trust}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Low Trust:</span>
              <span className="stat-value error">{metrics.trust_levels.low_trust}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Average Score:</span>
              <span className="stat-value highlight">
                {(metrics.trust_levels.average_score * 100).toFixed(1)}%
              </span>
              <div className="stat-bar">
                <div 
                  className="stat-bar-fill trust"
                  style={{ width: `${metrics.trust_levels.average_score * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Trust Distribution Chart */}
          <div className="trust-distribution-chart">
            <div className="chart-bar-group">
              <div 
                className="chart-bar high-trust"
                style={{ 
                  width: `${(metrics.trust_levels.high_trust / (metrics.trust_levels.high_trust + metrics.trust_levels.medium_trust + metrics.trust_levels.low_trust)) * 100}%` 
                }}
                title={`High Trust: ${metrics.trust_levels.high_trust}`}
              >
                {metrics.trust_levels.high_trust}
              </div>
              <div 
                className="chart-bar medium-trust"
                style={{ 
                  width: `${(metrics.trust_levels.medium_trust / (metrics.trust_levels.high_trust + metrics.trust_levels.medium_trust + metrics.trust_levels.low_trust)) * 100}%` 
                }}
                title={`Medium Trust: ${metrics.trust_levels.medium_trust}`}
              >
                {metrics.trust_levels.medium_trust}
              </div>
              <div 
                className="chart-bar low-trust"
                style={{ 
                  width: `${(metrics.trust_levels.low_trust / (metrics.trust_levels.high_trust + metrics.trust_levels.medium_trust + metrics.trust_levels.low_trust)) * 100}%` 
                }}
                title={`Low Trust: ${metrics.trust_levels.low_trust}`}
              >
                {metrics.trust_levels.low_trust}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="metrics-footer">
        <span className="metrics-timestamp">
          Last updated: {new Date(metrics.timestamp).toLocaleString()}
        </span>
      </div>
    </div>
  );
};
