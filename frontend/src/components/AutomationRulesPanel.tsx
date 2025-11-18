import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';

interface AutomationRule {
  rule_id: string;
  name: string;
  description: string;
  trigger_type: string;
  enabled: boolean;
  trigger_count: number;
  last_triggered: string | null;
}

interface AutomationRulesPanelProps {
  token: string;
}

export const AutomationRulesPanel: React.FC<AutomationRulesPanelProps> = ({ token }) => {
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const response = await fetch(apiUrl('/api/collaboration/automation/rules', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setRules(data.rules || []);
    } catch (error) {
      console.error('Failed to fetch automation rules:', error);
      setRules([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleRule = async (ruleId: string, enabled: boolean) => {
    const action = enabled ? 'disable' : 'enable';
    try {
      await fetch(`http://localhost:8000/api/collaboration/automation/rules/${ruleId}/${action}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchRules();
    } catch (error) {
      console.error(`Failed to ${action} rule:`, error);
    }
  };

  const deleteRule = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this rule?')) return;

    try {
      await fetch(`http://localhost:8000/api/collaboration/automation/rules/${ruleId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchRules();
    } catch (error) {
      console.error('Failed to delete rule:', error);
    }
  };

  const getTriggerIcon = (triggerType: string) => {
    switch (triggerType) {
      case 'file_changed': return '📝';
      case 'workflow_approved': return '✅';
      case 'quality_threshold': return '📊';
      case 'time_based': return '⏰';
      default: return '🔔';
    }
  };

  return (
    <div className="automation-rules-panel">
      <div className="panel-header">
        <h3 className="section-title">Automation Rules</h3>
        <button className="create-btn">+ Create Rule</button>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
        </div>
      ) : rules.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">🤖</span>
          <p>No automation rules configured</p>
          <button className="create-btn-lg">Create Your First Rule</button>
        </div>
      ) : (
        <div className="rules-list">
          {rules.map((rule) => (
            <div key={rule.rule_id} className={`rule-card ${rule.enabled ? 'enabled' : 'disabled'}`}>
              <div className="rule-header">
                <div className="rule-title-section">
                  <span className="rule-icon">{getTriggerIcon(rule.trigger_type)}</span>
                  <div>
                    <div className="rule-name">{rule.name}</div>
                    <div className="rule-trigger">{rule.trigger_type.replace('_', ' ')}</div>
                  </div>
                </div>

                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={rule.enabled}
                    onChange={() => toggleRule(rule.rule_id, rule.enabled)}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>

              <div className="rule-description">{rule.description}</div>

              <div className="rule-stats">
                <div className="stat">
                  <span className="stat-label">Triggered:</span>
                  <span className="stat-value">{rule.trigger_count} times</span>
                </div>
                {rule.last_triggered && (
                  <div className="stat">
                    <span className="stat-label">Last:</span>
                    <span className="stat-value">
                      {new Date(rule.last_triggered).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="rule-actions">
                <button className="rule-action-btn edit">Edit</button>
                <button
                  className="rule-action-btn delete"
                  onClick={() => deleteRule(rule.rule_id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
