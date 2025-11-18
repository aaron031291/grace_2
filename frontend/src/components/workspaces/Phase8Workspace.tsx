/**
 * Phase 8 Workspace: End-to-End Testing & Production Readiness
 */

import React, { useState, useEffect } from 'react';
import { phase8Api, Phase8Status, ReadinessResult, SystemHealth, IntegrationResult } from '../../api/phase8Api';
import './Phase8Workspace.css';

type TabType = 'overview' | 'readiness' | 'health' | 'integrations';

export const Phase8Workspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [status, setStatus] = useState<Phase8Status | null>(null);
  const [readiness, setReadiness] = useState<ReadinessResult | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [integrations, setIntegrations] = useState<IntegrationResult | null>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statusData, readinessData, healthData, integrationsData] = await Promise.all([
        phase8Api.getStatus(),
        phase8Api.getReadinessChecks(),
        phase8Api.getSystemHealth(),
        phase8Api.validateAllIntegrations(),
      ]);
      
      setStatus(statusData);
      setReadiness(readinessData);
      setHealth(healthData);
      setIntegrations(integrationsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch Phase 8 data');
    } finally {
      setLoading(false);
    }
  };

  const renderOverview = () => {
    if (!status) return <div className="phase8-empty">No status data available</div>;

    return (
      <div className="phase8-overview">
        <div className="phase8-header">
          <h2>Phase 8: End-to-End Testing & Production Readiness</h2>
          <span className={`phase8-status-badge ${status.overall_status}`}>
            {status.overall_status}
          </span>
        </div>

        <div className="phase8-metrics-grid">
          <div className="phase8-metric-card">
            <div className="metric-icon">✓</div>
            <div className="metric-content">
              <div className="metric-label">Production Readiness</div>
              <div className="metric-value">{status.readiness.score.toFixed(1)}%</div>
              <div className="metric-detail">
                {status.readiness.passed_checks}/{status.readiness.total_checks} checks passed
              </div>
            </div>
          </div>

          <div className="phase8-metric-card">
            <div className="metric-icon">❤️</div>
            <div className="metric-content">
              <div className="metric-label">System Health</div>
              <div className="metric-value">{status.health.status}</div>
              <div className="metric-detail">
                CPU: {status.health.cpu_percent.toFixed(1)}% | Memory: {status.health.memory_percent.toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="phase8-metric-card">
            <div className="metric-icon">🔗</div>
            <div className="metric-content">
              <div className="metric-label">Integrations</div>
              <div className="metric-value">{status.integrations.success_rate.toFixed(1)}%</div>
              <div className="metric-detail">
                {status.integrations.passed_tests}/{status.integrations.total_tests} tests passed
              </div>
            </div>
          </div>

          <div className="phase8-metric-card">
            <div className="metric-icon">🧪</div>
            <div className="metric-content">
              <div className="metric-label">E2E Tests</div>
              <div className="metric-value">{status.e2e_tests.status}</div>
              <div className="metric-detail">
                {status.e2e_tests.total_tests} tests available
              </div>
            </div>
          </div>
        </div>

        <div className="phase8-info">
          <h3>Phase 8 Components</h3>
          <ul>
            <li><strong>E2E Test Suite:</strong> 50 comprehensive tests across all phases</li>
            <li><strong>Production Readiness Checker:</strong> Validates all systems are production-ready</li>
            <li><strong>Health Monitor:</strong> Real-time system health monitoring</li>
            <li><strong>Integration Validator:</strong> Validates integration between all Grace phases</li>
          </ul>
        </div>
      </div>
    );
  };

  const renderReadiness = () => {
    if (!readiness) return <div className="phase8-empty">No readiness data available</div>;

    return (
      <div className="phase8-readiness">
        <div className="readiness-summary">
          <h3>Production Readiness: {readiness.readiness_score.toFixed(1)}%</h3>
          <div className="readiness-progress">
            <div 
              className="readiness-progress-bar" 
              style={{ width: `${readiness.readiness_score}%` }}
            />
          </div>
          <div className="readiness-stats">
            <span className="stat-passed">{readiness.passed_checks} Passed</span>
            <span className="stat-failed">{readiness.failed_checks} Failed</span>
            <span className="stat-total">{readiness.total_checks} Total</span>
          </div>
        </div>

        <div className="readiness-categories">
          <h4>By Category</h4>
          {Object.entries(readiness.categories).map(([category, stats]) => (
            <div key={category} className="category-item">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className="category-score">
                  {stats.total > 0 ? ((stats.passed / stats.total) * 100).toFixed(0) : 0}%
                </span>
              </div>
              <div className="category-progress">
                <div 
                  className="category-progress-bar" 
                  style={{ width: `${stats.total > 0 ? (stats.passed / stats.total) * 100 : 0}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="readiness-checks">
          <h4>Detailed Checks</h4>
          {readiness.checks.map((check) => (
            <div key={check.id} className="check-group">
              <div className="check-group-header">
                <span className={`check-status ${check.status}`}>●</span>
                <span className="check-name">{check.name}</span>
                <span className="check-category">{check.category}</span>
              </div>
              <ul className="check-items">
                {check.checks.map((item, idx) => (
                  <li key={idx} className={`check-item ${item.status}`}>
                    <span className="check-icon">{item.status === 'passed' ? '✓' : '✗'}</span>
                    <span className="check-text">{item.name}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderHealth = () => {
    if (!health) return <div className="phase8-empty">No health data available</div>;

    return (
      <div className="phase8-health">
        <div className="health-summary">
          <h3>System Health: <span className={`health-status ${health.status}`}>{health.status}</span></h3>
          {health.warnings && health.warnings.length > 0 && (
            <div className="health-warnings">
              {health.warnings.map((warning, idx) => (
                <div key={idx} className="warning-item">⚠️ {warning}</div>
              ))}
            </div>
          )}
        </div>

        <div className="health-system">
          <h4>System Resources</h4>
          <div className="resource-item">
            <div className="resource-header">
              <span>CPU Usage</span>
              <span>{health.components.system.cpu_percent?.toFixed(1)}%</span>
            </div>
            <div className="resource-bar">
              <div 
                className="resource-fill cpu" 
                style={{ width: `${health.components.system.cpu_percent}%` }}
              />
            </div>
          </div>
          <div className="resource-item">
            <div className="resource-header">
              <span>Memory Usage</span>
              <span>{health.components.system.memory_percent?.toFixed(1)}%</span>
            </div>
            <div className="resource-bar">
              <div 
                className="resource-fill memory" 
                style={{ width: `${health.components.system.memory_percent}%` }}
              />
            </div>
          </div>
          <div className="resource-item">
            <div className="resource-header">
              <span>Disk Usage</span>
              <span>{health.components.system.disk_percent?.toFixed(1)}%</span>
            </div>
            <div className="resource-bar">
              <div 
                className="resource-fill disk" 
                style={{ width: `${health.components.system.disk_percent}%` }}
              />
            </div>
          </div>
        </div>

        <div className="health-components">
          <h4>Component Health</h4>
          <div className="components-grid">
            {Object.entries(health.components).filter(([key]) => key !== 'system').map(([key, component]) => (
              <div key={key} className={`component-card ${component.status}`}>
                <div className="component-status">●</div>
                <div className="component-name">{key.replace(/_/g, ' ')}</div>
                <div className="component-message">{component.message}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="health-metrics">
          <h4>Performance Metrics</h4>
          <div className="metrics-row">
            <div className="metric-box">
              <div className="metric-label">Uptime</div>
              <div className="metric-value">
                {Math.floor(health.metrics.uptime_seconds / 3600)}h {Math.floor((health.metrics.uptime_seconds % 3600) / 60)}m
              </div>
            </div>
            <div className="metric-box">
              <div className="metric-label">Total Requests</div>
              <div className="metric-value">{health.metrics.total_requests}</div>
            </div>
            <div className="metric-box">
              <div className="metric-label">Error Rate</div>
              <div className="metric-value">{health.metrics.error_rate.toFixed(2)}%</div>
            </div>
            <div className="metric-box">
              <div className="metric-label">Avg Response Time</div>
              <div className="metric-value">{health.metrics.avg_response_time_ms.toFixed(0)}ms</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderIntegrations = () => {
    if (!integrations) return <div className="phase8-empty">No integration data available</div>;

    return (
      <div className="phase8-integrations">
        <div className="integrations-summary">
          <h3>Integration Validation: {integrations.success_rate.toFixed(1)}%</h3>
          <div className="integrations-stats">
            <span className="stat-passed">{integrations.passed_tests} Passed</span>
            <span className="stat-failed">{integrations.failed_tests} Failed</span>
            <span className="stat-skipped">{integrations.skipped_tests} Skipped</span>
          </div>
          {integrations.critical_failures.length > 0 && (
            <div className="critical-failures">
              <h4>Critical Failures</h4>
              {integrations.critical_failures.map((failure, idx) => (
                <div key={idx} className="failure-item">⚠️ {failure}</div>
              ))}
            </div>
          )}
        </div>

        <div className="integrations-list">
          {integrations.tests.map((test) => (
            <div key={test.id} className={`integration-card ${test.status}`}>
              <div className="integration-header">
                <span className={`integration-status ${test.status}`}>●</span>
                <span className="integration-name">{test.name}</span>
                {test.critical && <span className="integration-critical">CRITICAL</span>}
              </div>
              <div className="integration-description">{test.description}</div>
              <div className="integration-phases">
                {test.phases.map((phase, idx) => (
                  <span key={idx} className="phase-badge">{phase}</span>
                ))}
              </div>
              {test.message && (
                <div className="integration-message">{test.message}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading && !status) {
    return <div className="phase8-workspace loading">Loading Phase 8 data...</div>;
  }

  if (error) {
    return (
      <div className="phase8-workspace error">
        <div className="error-message">
          <h3>Error loading Phase 8 data</h3>
          <p>{error}</p>
          <button onClick={fetchData}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="phase8-workspace">
      <div className="phase8-tabs">
        <button
          className={`phase8-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`phase8-tab ${activeTab === 'readiness' ? 'active' : ''}`}
          onClick={() => setActiveTab('readiness')}
        >
          Production Readiness
        </button>
        <button
          className={`phase8-tab ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => setActiveTab('health')}
        >
          System Health
        </button>
        <button
          className={`phase8-tab ${activeTab === 'integrations' ? 'active' : ''}`}
          onClick={() => setActiveTab('integrations')}
        >
          Integrations
        </button>
      </div>

      <div className="phase8-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'readiness' && renderReadiness()}
        {activeTab === 'health' && renderHealth()}
        {activeTab === 'integrations' && renderIntegrations()}
      </div>
    </div>
  );
};
