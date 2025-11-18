/**
 * Health & Trust Meter
 * 
 * Displays system health and trust metrics, polls /api/metrics/summary
 */

import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../api/config';
import './HealthMeter.css';

interface MetricsSummary {
  success?: boolean;
  data?: {
    trust?: number;
    trust_score?: number;
    confidence?: number;
    pending_approvals?: number;
    active_tasks?: number;
    system_status?: 'healthy' | 'degraded' | 'offline';
    health?: 'healthy' | 'degraded' | 'offline';
  };
  // Legacy format support
  trust_score?: number;
  confidence?: number;
  pending_approvals?: number;
  active_tasks?: number;
  system_status?: 'healthy' | 'degraded' | 'offline';
}

export const HealthMeter: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsSummary>({
    trust_score: 0,
    confidence: 0,
    pending_approvals: 0,
    active_tasks: 0,
    system_status: 'offline',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(API_ENDPOINTS.metricsSummary);
        if (response.ok) {
          const rawData = await response.json();
          
          // Handle new format: { success: true, data: {...} }
          if (rawData.success && rawData.data) {
            setMetrics({
              trust_score: rawData.data.trust || rawData.data.trust_score || 0,
              confidence: rawData.data.confidence || 0,
              pending_approvals: rawData.data.pending_approvals || 0,
              active_tasks: rawData.data.active_tasks || 0,
              system_status: rawData.data.health || rawData.data.system_status || 'offline'
            });
          } else {
            // Handle legacy format
            setMetrics(rawData);
          }
        } else {
          setMetrics((prev) => ({ ...prev, system_status: 'offline' }));
        }
      } catch (error) {
        setMetrics((prev) => ({ ...prev, system_status: 'offline' }));
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return '#4caf50';
      case 'degraded':
        return '#ff9800';
      case 'offline':
        return '#f44336';
      default:
        return '#888';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#4caf50';
    if (score >= 0.6) return '#ff9800';
    return '#f44336';
  };

  if (loading) {
    return (
      <div className="health-meter loading">
        <div className="spinner" />
        Loading metrics...
      </div>
    );
  }

  return (
    <div className="health-meter">
      <div className="health-header">
        <h3>🏥 System Health</h3>
        <div
          className="status-indicator"
          style={{ backgroundColor: getStatusColor(metrics.system_status) }}
        >
          {metrics.system_status}
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Trust Score</div>
          <div className="metric-value" style={{ color: getScoreColor(metrics.trust_score) }}>
            {(metrics.trust_score * 100).toFixed(0)}%
          </div>
          <div className="metric-bar">
            <div
              className="metric-bar-fill"
              style={{
                width: `${metrics.trust_score * 100}%`,
                backgroundColor: getScoreColor(metrics.trust_score),
              }}
            />
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Confidence</div>
          <div className="metric-value" style={{ color: getScoreColor(metrics.confidence) }}>
            {(metrics.confidence * 100).toFixed(0)}%
          </div>
          <div className="metric-bar">
            <div
              className="metric-bar-fill"
              style={{
                width: `${metrics.confidence * 100}%`,
                backgroundColor: getScoreColor(metrics.confidence),
              }}
            />
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Pending Approvals</div>
          <div className="metric-value">{metrics.pending_approvals}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label">Active Tasks</div>
          <div className="metric-value">{metrics.active_tasks}</div>
        </div>
      </div>
    </div>
  );
};
