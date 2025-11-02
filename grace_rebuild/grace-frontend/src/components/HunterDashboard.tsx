import { useState, useEffect } from 'react';
import axios from 'axios';
import { SecurityRulesList } from './SecurityRulesList';
import './HunterDashboard.css';

interface SecurityAlert {
    id: number;
    timestamp: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    rule_name: string;
    action_taken: string;
    details: string;
    user_id?: number;
}

interface Task {
    title: string;
    description: string;
    priority: 'critical' | 'high' | 'medium' | 'low';
}

export function HunterDashboard() {
    const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
    const [filteredAlerts, setFilteredAlerts] = useState<SecurityAlert[]>([]);
    const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
    const [selectedAlert, setSelectedAlert] = useState<SecurityAlert | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [taskCreated, setTaskCreated] = useState<string>('');
    const [activeTab, setActiveTab] = useState<'alerts' | 'rules'>('alerts');

    const fetchAlerts = async () => {
        try {
            setIsLoading(true);
            setError('');
            const response = await axios.get('http://localhost:8000/api/hunter/alerts?limit=50');
            setAlerts(response.data);
            setIsLoading(false);
        } catch (err) {
            setError('Failed to fetch alerts');
            setIsLoading(false);
            console.error('Error fetching alerts:', err);
        }
    };

    useEffect(() => {
        fetchAlerts();
        const interval = setInterval(fetchAlerts, 5000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (selectedSeverity === 'all') {
            setFilteredAlerts(alerts);
        } else {
            setFilteredAlerts(alerts.filter(alert => alert.severity === selectedSeverity));
        }
    }, [alerts, selectedSeverity]);

    const createTaskFromAlert = async (alert: SecurityAlert) => {
        try {
            const task: Task = {
                title: `Security Alert: ${alert.rule_name}`,
                description: `${alert.details}\n\nAction Taken: ${alert.action_taken}\n\nTimestamp: ${alert.timestamp}`,
                priority: alert.severity
            };

            await axios.post('http://localhost:8000/api/tasks', task);
            setTaskCreated(`Task created for alert #${alert.id}`);
            setTimeout(() => setTaskCreated(''), 3000);
        } catch (err) {
            setError('Failed to create task');
            console.error('Error creating task:', err);
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return '#dc2626';
            case 'high': return '#ea580c';
            case 'medium': return '#ca8a04';
            case 'low': return '#65a30d';
            default: return '#6b7280';
        }
    };

    return (
        <div className="hunter-dashboard">
            <div className="dashboard-header">
                <h1>🛡️ Hunter Security Dashboard</h1>
                <div className="refresh-indicator">
                    {isLoading && <span className="loading-spinner">⟳</span>}
                    <span className="last-update">Auto-refresh: 5s</span>
                </div>
            </div>

            {error && <div className="error-banner">{error}</div>}
            {taskCreated && <div className="success-banner">{taskCreated}</div>}

            <div className="tabs">
                <button
                    className={`tab-btn ${activeTab === 'alerts' ? 'active' : ''}`}
                    onClick={() => setActiveTab('alerts')}
                >
                    🚨 Security Alerts
                </button>
                <button
                    className={`tab-btn ${activeTab === 'rules' ? 'active' : ''}`}
                    onClick={() => setActiveTab('rules')}
                >
                    🔒 Security Rules
                </button>
            </div>

            {activeTab === 'rules' ? (
                <SecurityRulesList />
            ) : (
                <>

                    <div className="filter-controls">
                        <label>Severity Filter:</label>
                        <select value={selectedSeverity} onChange={(e) => setSelectedSeverity(e.target.value)}>
                            <option value="all">All Severities</option>
                            <option value="critical">Critical</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                        <span className="alert-count">{filteredAlerts.length} alerts</span>
                    </div>

                    <div className="alerts-grid">
                        {filteredAlerts.length === 0 ? (
                            <div className="no-alerts">No alerts found</div>
                        ) : (
                            filteredAlerts.map((alert) => (
                                <div
                                    key={alert.id}
                                    className="alert-card"
                                    style={{ borderLeftColor: getSeverityColor(alert.severity) }}
                                    onClick={() => setSelectedAlert(alert)}
                                >
                                    <div className="alert-header">
                                        <span
                                            className={`severity-badge severity-${alert.severity}`}
                                            style={{ backgroundColor: getSeverityColor(alert.severity) }}
                                        >
                                            {alert.severity.toUpperCase()}
                                        </span>
                                        <span className="alert-timestamp">
                                            {new Date(alert.timestamp).toLocaleString()}
                                        </span>
                                    </div>
                                    <h3 className="alert-rule">{alert.rule_name}</h3>
                                    <p className="alert-action">{alert.action_taken}</p>
                                    <button
                                        className="create-task-btn"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            createTaskFromAlert(alert);
                                        }}
                                    >
                                        Create Task
                                    </button>
                                </div>
                            ))
                        )}
                    </div>

                    {selectedAlert && (
                        <div className="modal-overlay" onClick={() => setSelectedAlert(null)}>
                            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                                <div className="modal-header">
                                    <h2>Alert Details</h2>
                                    <button className="close-btn" onClick={() => setSelectedAlert(null)}>×</button>
                                </div>
                                <div className="modal-body">
                                    <div className="detail-row">
                                        <strong>Alert ID:</strong> {selectedAlert.id}
                                    </div>
                                    <div className="detail-row">
                                        <strong>Severity:</strong>
                                        <span
                                            className={`severity-badge severity-${selectedAlert.severity}`}
                                            style={{ backgroundColor: getSeverityColor(selectedAlert.severity) }}
                                        >
                                            {selectedAlert.severity.toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="detail-row">
                                        <strong>Rule Triggered:</strong> {selectedAlert.rule_name}
                                    </div>
                                    <div className="detail-row">
                                        <strong>Action Taken:</strong> {selectedAlert.action_taken}
                                    </div>
                                    <div className="detail-row">
                                        <strong>Timestamp:</strong> {new Date(selectedAlert.timestamp).toLocaleString()}
                                    </div>
                                    <div className="detail-row">
                                        <strong>Details:</strong>
                                        <p className="details-text">{selectedAlert.details}</p>
                                    </div>
                                    {selectedAlert.user_id && (
                                        <div className="detail-row">
                                            <strong>User ID:</strong> {selectedAlert.user_id}
                                        </div>
                                    )}
                                </div>
                                <div className="modal-footer">
                                    <button
                                        className="create-task-btn-large"
                                        onClick={() => {
                                            createTaskFromAlert(selectedAlert);
                                            setSelectedAlert(null);
                                        }}
                                    >
                                        Create Task from Alert
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
      )}
                </div>
            );
}
