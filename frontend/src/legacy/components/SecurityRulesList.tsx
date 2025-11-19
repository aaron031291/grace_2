import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import axios from 'axios';
import './SecurityRulesList.css';

interface SecurityRule {
    id: number;
    name: string;
    description: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    enabled: boolean;
    pattern?: string;
    action: string;
    created_at: string;
}

export function SecurityRulesList() {
    const [rules, setRules] = useState<SecurityRule[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>('');

    const fetchRules = async () => {
        try {
            setIsLoading(true);
            setError('');
            const response = await axios.get(apiUrl('/api/hunter/rules');
            setRules(response.data);
            setIsLoading(false);
        } catch (err) {
            setError('Failed to fetch security rules');
            setIsLoading(false);
            console.error('Error fetching rules:', err);
        }
    };

    useEffect(() => {
        fetchRules();
    }, []);

    const toggleRule = async (ruleId: number, currentState: boolean) => {
        try {
            await axios.patch(`http://localhost:8000/api/hunter/rules/${ruleId}`, {
                enabled: !currentState
            });
            fetchRules();
        } catch (err) {
            setError('Failed to update rule');
            console.error('Error updating rule:', err);
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

    const activeRules = rules.filter(r => r.enabled);
    const inactiveRules = rules.filter(r => !r.enabled);

    return (
        <div className="security-rules-list">
            <div className="rules-header">
                <h2>🔒 Active Security Rules</h2>
                <div className="rules-stats">
                    <span className="stat-active">{activeRules.length} Active</span>
                    <span className="stat-inactive">{inactiveRules.length} Inactive</span>
                </div>
            </div>

            {error && <div className="error-banner">{error}</div>}

            {isLoading ? (
                <div className="loading-state">Loading rules...</div>
            ) : (
                <>
                    <div className="rules-section">
                        <h3 className="section-title">Active Rules ({activeRules.length})</h3>
                        {activeRules.length === 0 ? (
                            <div className="no-rules">No active rules</div>
                        ) : (
                            <div className="rules-grid">
                                {activeRules.map((rule) => (
                                    <div
                                        key={rule.id}
                                        className="rule-card"
                                        style={{ borderLeftColor: getSeverityColor(rule.severity) }}
                                    >
                                        <div className="rule-header">
                                            <h4 className="rule-name">{rule.name}</h4>
                                            <label className="toggle-switch">
                                                <input
                                                    type="checkbox"
                                                    checked={rule.enabled}
                                                    onChange={() => toggleRule(rule.id, rule.enabled)}
                                                />
                                                <span className="toggle-slider"></span>
                                            </label>
                                        </div>
                                        <p className="rule-description">{rule.description}</p>
                                        <div className="rule-details">
                                            <span
                                                className={`severity-badge severity-${rule.severity}`}
                                                style={{ backgroundColor: getSeverityColor(rule.severity) }}
                                            >
                                                {rule.severity.toUpperCase()}
                                            </span>
                                            <span className="rule-action">{rule.action}</span>
                                        </div>
                                        {rule.pattern && (
                                            <div className="rule-pattern">
                                                <strong>Pattern:</strong> <code>{rule.pattern}</code>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {inactiveRules.length > 0 && (
                        <div className="rules-section">
                            <h3 className="section-title">Inactive Rules ({inactiveRules.length})</h3>
                            <div className="rules-grid">
                                {inactiveRules.map((rule) => (
                                    <div
                                        key={rule.id}
                                        className="rule-card rule-card-inactive"
                                        style={{ borderLeftColor: getSeverityColor(rule.severity) }}
                                    >
                                        <div className="rule-header">
                                            <h4 className="rule-name">{rule.name}</h4>
                                            <label className="toggle-switch">
                                                <input
                                                    type="checkbox"
                                                    checked={rule.enabled}
                                                    onChange={() => toggleRule(rule.id, rule.enabled)}
                                                />
                                                <span className="toggle-slider"></span>
                                            </label>
                                        </div>
                                        <p className="rule-description">{rule.description}</p>
                                        <div className="rule-details">
                                            <span
                                                className={`severity-badge severity-${rule.severity}`}
                                                style={{ backgroundColor: getSeverityColor(rule.severity) }}
                                            >
                                                {rule.severity.toUpperCase()}
                                            </span>
                                            <span className="rule-action">{rule.action}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
