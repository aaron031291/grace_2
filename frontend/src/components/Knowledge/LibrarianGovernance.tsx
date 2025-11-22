import React, { useState } from 'react';
import './LibrarianGovernance.css';

interface GovernanceMetric {
    label: string;
    value: number;
    unit: string;
    status: 'optimal' | 'warning' | 'critical';
    trend: 'up' | 'down' | 'stable';
}

const LibrarianGovernance: React.FC = () => {
    const [metrics] = useState<GovernanceMetric[]>([
        { label: 'Trust Score', value: 92, unit: '%', status: 'optimal', trend: 'up' },
        { label: 'Chaos Level', value: 12, unit: '%', status: 'optimal', trend: 'down' },
        { label: 'Storage Efficiency', value: 85, unit: '%', status: 'optimal', trend: 'stable' },
        { label: 'Retrieval Latency', value: 45, unit: 'ms', status: 'optimal', trend: 'stable' }
    ]);

    const [activeAlerts] = useState([
        { id: 1, type: 'info', message: 'Daily integrity scan completed. No errors found.' },
        { id: 2, type: 'warning', message: '3 unverified artifacts in Limbo state.' }
    ]);

    return (
        <div className="librarian-governance">
            <div className="governance-header">
                <h3>Librarian Governance</h3>
                <span className="status-badge optimal">System Optimal</span>
            </div>

            <div className="metrics-grid">
                {metrics.map((metric, index) => (
                    <div key={index} className={`metric-card ${metric.status}`}>
                        <div className="metric-header">
                            <span className="metric-label">{metric.label}</span>
                            <span className={`metric-trend ${metric.trend}`}>
                                {metric.trend === 'up' ? '↑' : metric.trend === 'down' ? '↓' : '→'}
                            </span>
                        </div>
                        <div className="metric-value">
                            {metric.value}
                            <span className="metric-unit">{metric.unit}</span>
                        </div>
                        <div className="metric-bar-container">
                            <div
                                className={`metric-bar-fill ${metric.status}`}
                                style={{ width: `${metric.value}%` }}
                            ></div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="governance-alerts">
                <h4>Active Alerts</h4>
                {activeAlerts.map(alert => (
                    <div key={alert.id} className={`alert-item ${alert.type}`}>
                        <span className="alert-icon">
                            {alert.type === 'info' ? 'ℹ️' : alert.type === 'warning' ? '⚠️' : '🚨'}
                        </span>
                        <span className="alert-message">{alert.message}</span>
                    </div>
                ))}
            </div>

            <div className="governance-actions">
                <button className="action-btn">Run Integrity Scan</button>
                <button className="action-btn">Review Limbo State</button>
                <button className="action-btn">Optimize Storage</button>
            </div>
        </div>
    );
};

export default LibrarianGovernance;
