/**
 * Coding Agent Analytics Dashboard
 * Shows success metrics, trends, and improvement recommendations
 */
import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import axios from 'axios';
import './CodingAgentAnalytics.css';

const API_BASE = apiUrl('';

export const CodingAgentAnalytics: React.FC = () => {
  const [overview, setOverview] = useState<any>(null);
  const [successMetrics, setSuccessMetrics] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [learnedCapabilities, setLearnedCapabilities] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
    const interval = setInterval(loadAnalytics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const [overviewRes, metricsRes, trendsRes, recsRes, capsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/coding_agent/analytics/overview`),
        axios.get(`${API_BASE}/api/coding_agent/analytics/success_metrics`),
        axios.get(`${API_BASE}/api/coding_agent/analytics/trends?days=30`),
        axios.get(`${API_BASE}/api/coding_agent/analytics/recommendations`),
        axios.get(`${API_BASE}/api/coding_agent/capabilities/learned`)
      ]);

      setOverview(overviewRes.data);
      setSuccessMetrics(metricsRes.data);
      setTrends(trendsRes.data);
      setRecommendations(recsRes.data);
      setLearnedCapabilities(capsRes.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
    setLoading(false);
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving': return '#00ff88';
      case 'stable': return '#ffaa00';
      case 'declining': return '#ff4444';
      default: return '#888';
    }
  };

  if (loading && !overview) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  return (
    <div className="coding-agent-analytics">
      <div className="analytics-header">
        <h2>🤖 Coding Agent Analytics</h2>
        <button onClick={loadAnalytics} className="refresh-btn">
          ↻ Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <section className="summary-section">
        <div className="summary-grid">
          <div className="summary-card">
            <div className="card-label">Total Builds</div>
            <div className="card-value">{overview?.summary.total_builds || 0}</div>
            <div className="card-subtext">
              {overview?.summary.completed || 0} completed, {overview?.summary.in_progress || 0} in progress
            </div>
          </div>
          <div className="summary-card success">
            <div className="card-label">Success Rate</div>
            <div className="card-value">{overview?.summary.success_rate_percent?.toFixed(1) || 0}%</div>
            <div className="card-subtext">
              {overview?.summary.completed || 0}/{overview?.summary.total_builds || 0} successful
            </div>
          </div>
          <div className="summary-card">
            <div className="card-label">Avg Delivery Time</div>
            <div className="card-value">{successMetrics?.time_to_deliver.avg_hours?.toFixed(1) || 0}h</div>
            <div className="card-subtext">
              Planned: {overview?.time_metrics.avg_planned_hours?.toFixed(1) || 0}h
            </div>
          </div>
          <div className="summary-card">
            <div className="card-label">Efficiency Gain</div>
            <div className="card-value">
              {overview?.time_metrics.avg_efficiency_gain_percent?.toFixed(1) || 0}%
            </div>
            <div className="card-subtext">Faster than estimated</div>
          </div>
          <div className="summary-card">
            <div className="card-label">Test Coverage</div>
            <div className="card-value">{overview?.quality_metrics.avg_test_coverage_percent?.toFixed(1) || 0}%</div>
            <div className="card-subtext">Avg across all builds</div>
          </div>
          <div className="summary-card">
            <div className="card-label">Patterns Learned</div>
            <div className="card-value">{learnedCapabilities?.total_patterns || 0}</div>
            <div className="card-subtext">Reusable components</div>
          </div>
        </div>
      </section>

      {/* Performance Trends */}
      <section className="trends-section">
        <h3>Performance Trends (30 Days)</h3>
        <div className="trends-grid">
          <div className="trend-card">
            <div className="trend-header">
              <span className="trend-label">Efficiency</span>
              <span className="trend-indicator" style={{ color: getTrendColor('improving') }}>
                ↗ Improving
              </span>
            </div>
            <div className="trend-value">
              {trends?.trends.efficiency.week_4 * 100}% faster
            </div>
            <div className="trend-change">
              +{trends?.trends.efficiency.change_percent}% from Week 1
            </div>
          </div>
          <div className="trend-card">
            <div className="trend-header">
              <span className="trend-label">Quality</span>
              <span className="trend-indicator" style={{ color: getTrendColor('improving') }}>
                ↗ Improving
              </span>
            </div>
            <div className="trend-value">
              {trends?.trends.quality.week_4}% coverage
            </div>
            <div className="trend-change">
              +{trends?.trends.quality.change_percent}% from Week 1
            </div>
          </div>
          <div className="trend-card">
            <div className="trend-header">
              <span className="trend-label">Speed</span>
              <span className="trend-indicator" style={{ color: getTrendColor('improving') }}>
                ↗ Improving
              </span>
            </div>
            <div className="trend-value">
              {trends?.trends.speed.week_4}h avg
            </div>
            <div className="trend-change">
              {trends?.trends.speed.change_percent}% from Week 1
            </div>
          </div>
          <div className="trend-card">
            <div className="trend-header">
              <span className="trend-label">Success Rate</span>
              <span className="trend-indicator" style={{ color: getTrendColor('improving') }}>
                ↗ Improving
              </span>
            </div>
            <div className="trend-value">
              {trends?.trends.success_rate.week_4}%
            </div>
            <div className="trend-change">
              +{trends?.trends.success_rate.change_percent}% from Week 1
            </div>
          </div>
        </div>
      </section>

      {/* Domain Breakdown */}
      <section className="domain-section">
        <h3>Performance by Domain</h3>
        <table className="domain-table">
          <thead>
            <tr>
              <th>Domain</th>
              <th>Builds</th>
              <th>Avg Duration</th>
              <th>Success Rate</th>
              <th>Efficiency</th>
            </tr>
          </thead>
          <tbody>
            {overview?.domain_breakdown.map((domain: any) => (
              <tr key={domain.domain}>
                <td className="domain-name">{domain.domain.replace(/_/g, ' ')}</td>
                <td>{domain.builds}</td>
                <td>{domain.avg_duration_hours.toFixed(1)}h</td>
                <td>
                  <span className={`rate-badge ${domain.success_rate === 100 ? 'perfect' : 'good'}`}>
                    {domain.success_rate}%
                  </span>
                </td>
                <td>+{(domain.efficiency_gain * 100).toFixed(0)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Recommendations */}
      <section className="recommendations-section">
        <h3>AI Recommendations</h3>
        <div className="recommendations-list">
          {recommendations?.recommendations.map((rec: any, idx: number) => (
            <div key={idx} className={`recommendation-card priority-${rec.priority}`}>
              <div className="rec-header">
                <span className={`priority-badge ${rec.priority}`}>
                  {rec.priority.toUpperCase()}
                </span>
                <span className="rec-category">{rec.category}</span>
              </div>
              <div className="rec-text">{rec.recommendation}</div>
              <div className="rec-reasoning">
                <strong>Why:</strong> {rec.reasoning}
              </div>
              <div className="rec-impact">
                <strong>Expected Impact:</strong> {rec.expected_impact}
              </div>
              <div className="rec-actions">
                <button className="btn-approve">✓ Apply</button>
                <button className="btn-defer">⏭ Defer</button>
                <button className="btn-reject">✕ Reject</button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Learned Capabilities */}
      <section className="capabilities-section">
        <h3>Learned Capabilities ({learnedCapabilities?.total_patterns} patterns)</h3>
        <div className="capabilities-grid">
          {learnedCapabilities?.capabilities.map((cap: any) => (
            <div key={cap.category} className="capability-card">
              <div className="cap-header">{cap.category.replace(/_/g, ' ')}</div>
              <div className="cap-stats">
                <div className="cap-stat">
                  <span>Patterns:</span>
                  <strong>{cap.patterns_learned}</strong>
                </div>
                <div className="cap-stat">
                  <span>Used in:</span>
                  <strong>{cap.builds_using_patterns} builds</strong>
                </div>
                <div className="cap-stat">
                  <span>Time Saved:</span>
                  <strong>{cap.avg_time_saved_hours.toFixed(1)}h avg</strong>
                </div>
              </div>
              <div className="cap-examples">
                <strong>Examples:</strong>
                <ul>
                  {cap.examples.map((ex: string, idx: number) => (
                    <li key={idx}>{ex}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
