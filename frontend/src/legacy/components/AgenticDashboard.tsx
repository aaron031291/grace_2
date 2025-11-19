import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Clock, TrendingUp, Activity, Zap } from 'lucide-react';

interface MetricData {
  metric_id: string;
  category: string;
  value: number;
  unit: string;
  status: 'good' | 'warning' | 'critical';
  timestamp: string;
}

interface AgenticAction {
  id: string;
  type: string;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  description: string;
  timestamp: string;
  risk_score: number;
}

interface SystemHealth {
  overall_health: number;
  overall_trust: number;
  overall_confidence: number;
  subsystems_running: number;
  total_subsystems: number;
}

export const AgenticDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [actions, setActions] = useState<AgenticAction[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [metricsRes, actionsRes, healthRes] = await Promise.all([
        fetch('/api/metrics/recent'),
        fetch('/api/agentic/actions'),
        fetch('/api/status')
      ]);

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData.metrics || []);
      }

      if (actionsRes.ok) {
        const actionsData = await actionsRes.json();
        setActions(actionsData.actions || []);
      }

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setHealth(healthData);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
      case 'completed':
        return { backgroundColor: '#10b981', color: '#fff' };
      case 'warning':
      case 'pending':
        return { backgroundColor: '#f59e0b', color: '#fff' };
      case 'critical':
      case 'failed':
        return { backgroundColor: '#ef4444', color: '#fff' };
      case 'executing':
        return { backgroundColor: '#8b5cf6', color: '#fff' };
      default:
        return { backgroundColor: '#6b7280', color: '#fff' };
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good':
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'warning':
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case 'critical':
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'executing':
        return <Activity className="w-4 h-4 text-blue-600" />;
      default:
        return <TrendingUp className="w-4 h-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      <a href="/" style={{ color: '#7b2cbf', marginBottom: '1rem', display: 'block' }}>← Back to Chat</a>

      <h1 style={{ color: '#00d4ff', marginBottom: '2rem' }}>🤖 Agentic Dashboard</h1>

      {/* System Health Overview */}
      {health && (
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
          <h3 style={{ color: '#00d4ff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap style={{ width: '20px', height: '20px' }} />
            System Health Overview
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
                {health.overall_health.toFixed(1)}%
              </div>
              <div style={{ fontSize: '0.875rem', color: '#7b2cbf' }}>Health Score</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
                {health.overall_trust.toFixed(1)}%
              </div>
              <div style={{ fontSize: '0.875rem', color: '#7b2cbf' }}>Trust Score</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
                {health.overall_confidence.toFixed(1)}%
              </div>
              <div style={{ fontSize: '0.875rem', color: '#7b2cbf' }}>Confidence</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
                {health.subsystems_running}/{health.total_subsystems}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#7b2cbf' }}>Systems Running</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Metrics */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h3 style={{ color: '#00d4ff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <TrendingUp style={{ width: '20px', height: '20px' }} />
          Recent Metrics
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {metrics.slice(0, 10).map((metric) => (
            <div key={metric.metric_id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', border: '1px solid #333', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {getStatusIcon(metric.status)}
                <div>
                  <div style={{ fontWeight: '500' }}>{metric.metric_id.replace(/_/g, ' ')}</div>
                  <div style={{ fontSize: '0.875rem', color: '#888' }}>{metric.category}</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 'bold' }}>{metric.value.toFixed(2)} {metric.unit}</div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    {new Date(metric.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  ...getStatusColor(metric.status)
                }}>
                  {metric.status}
                </span>
              </div>
            </div>
          ))}
          {metrics.length === 0 && (
            <div style={{ textAlign: 'center', color: '#888', padding: '2rem' }}>
              No metrics data available
            </div>
          )}
        </div>
      </div>

      {/* Agentic Actions */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333', marginBottom: '2rem' }}>
        <h3 style={{ color: '#00d4ff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity style={{ width: '20px', height: '20px' }} />
          Agentic Actions
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {actions.slice(0, 10).map((action) => (
            <div key={action.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', border: '1px solid #333', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {getStatusIcon(action.status)}
                <div>
                  <div style={{ fontWeight: '500' }}>{action.type.replace(/_/g, ' ')}</div>
                  <div style={{ fontSize: '0.875rem', color: '#888' }}>{action.description}</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    Risk: {action.risk_score.toFixed(2)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    {new Date(action.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  ...getStatusColor(action.status)
                }}>
                  {action.status}
                </span>
              </div>
            </div>
          ))}
          {actions.length === 0 && (
            <div style={{ textAlign: 'center', color: '#888', padding: '2rem' }}>
              No agentic actions recorded
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
        <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Quick Actions</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem' }}>
          <button style={{
            height: '80px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '1rem',
            border: '1px solid #333',
            borderRadius: '8px',
            background: 'transparent',
            color: '#fff',
            cursor: 'pointer'
          }}>
            <Activity style={{ width: '20px', height: '20px' }} />
            <span style={{ fontSize: '0.75rem' }}>View Logs</span>
          </button>
          <button style={{
            height: '80px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '1rem',
            border: '1px solid #333',
            borderRadius: '8px',
            background: 'transparent',
            color: '#fff',
            cursor: 'pointer'
          }}>
            <CheckCircle style={{ width: '20px', height: '20px' }} />
            <span style={{ fontSize: '0.75rem' }}>Health Check</span>
          </button>
          <button style={{
            height: '80px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '1rem',
            border: '1px solid #333',
            borderRadius: '8px',
            background: 'transparent',
            color: '#fff',
            cursor: 'pointer'
          }}>
            <TrendingUp style={{ width: '20px', height: '20px' }} />
            <span style={{ fontSize: '0.75rem' }}>Metrics</span>
          </button>
          <button style={{
            height: '80px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '1rem',
            border: '1px solid #333',
            borderRadius: '8px',
            background: 'transparent',
            color: '#fff',
            cursor: 'pointer'
          }}>
            <Zap style={{ width: '20px', height: '20px' }} />
            <span style={{ fontSize: '0.75rem' }}>Force Action</span>
          </button>
        </div>
      </div>
    </div>
  );
};
