import { useState } from 'react';
import './HealthBar.css';

interface HealthBarProps {
  health: number;
  trust: number;
  confidence: number;
}

export function HealthBar({ health, trust, confidence }: HealthBarProps) {
  const [expanded, setExpanded] = useState(false);

  const getColor = (value: number) => {
    if (value >= 90) return 'var(--color-success)';
    if (value >= 70) return 'var(--color-warning)';
    return 'var(--color-error)';
  };

  const getStatusIcon = (value: number) => {
    if (value >= 90) return '🟢';
    if (value >= 70) return '🟡';
    return '🔴';
  };

  return (
    <div className="health-bar-container">
      <button 
        className="health-bar-btn"
        onClick={() => setExpanded(!expanded)}
        title="System Health"
      >
        <span className="health-status-icon">{getStatusIcon(Math.min(health, trust, confidence))}</span>
        <span className="health-metric">
          <span className="health-label">H:</span>
          <span className="health-value" style={{ color: getColor(health) }}>{health}%</span>
        </span>
        <span className="health-divider">|</span>
        <span className="health-metric">
          <span className="health-label">T:</span>
          <span className="health-value" style={{ color: getColor(trust) }}>{trust}%</span>
        </span>
        <span className="health-divider">|</span>
        <span className="health-metric">
          <span className="health-label">C:</span>
          <span className="health-value" style={{ color: getColor(confidence) }}>{confidence}%</span>
        </span>
      </button>

      {expanded && (
        <div className="health-bar-expanded">
          <div className="health-bar-header">
            <h3>System Health</h3>
            <button 
              className="health-bar-close"
              onClick={() => setExpanded(false)}
            >
              ×
            </button>
          </div>
          
          <div className="health-metrics-detailed">
            <div className="health-metric-card">
              <div className="metric-header">
                <span className="metric-icon">{getStatusIcon(health)}</span>
                <span className="metric-name">Health</span>
              </div>
              <div className="metric-value-large" style={{ color: getColor(health) }}>
                {health}%
              </div>
              <div className="metric-bar">
                <div 
                  className="metric-bar-fill"
                  style={{ 
                    width: `${health}%`,
                    background: getColor(health)
                  }}
                />
              </div>
            </div>

            <div className="health-metric-card">
              <div className="metric-header">
                <span className="metric-icon">{getStatusIcon(trust)}</span>
                <span className="metric-name">Trust</span>
              </div>
              <div className="metric-value-large" style={{ color: getColor(trust) }}>
                {trust}%
              </div>
              <div className="metric-bar">
                <div 
                  className="metric-bar-fill"
                  style={{ 
                    width: `${trust}%`,
                    background: getColor(trust)
                  }}
                />
              </div>
            </div>

            <div className="health-metric-card">
              <div className="metric-header">
                <span className="metric-icon">{getStatusIcon(confidence)}</span>
                <span className="metric-name">Confidence</span>
              </div>
              <div className="metric-value-large" style={{ color: getColor(confidence) }}>
                {confidence}%
              </div>
              <div className="metric-bar">
                <div 
                  className="metric-bar-fill"
                  style={{ 
                    width: `${confidence}%`,
                    background: getColor(confidence)
                  }}
                />
              </div>
            </div>
          </div>

          <div className="health-bar-footer">
            <button className="view-observatory-btn">
              View Observatory →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
