/**
 * Layer 3 Intent & Learning Dashboard
 * Agentic brain goals: active intents, completion status, retrospectives,
 * playbook success rates, policy suggestions
 * Links each intent to the HTM tasks generated below
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Layer3IntentLearning.css';

interface Intent {
  intent_id: string;
  goal: string;
  status: string;
  completion_percent: number;
  created_at: string;
  htm_tasks_generated: number;
  estimated_completion: string | null;
}

interface Retrospective {
  id: string;
  cycle_name: string;
  insights: string[];
  improvements: string[];
  timestamp: string;
}

interface PlaybookStats {
  playbook_name: string;
  total_runs: number;
  success_rate_percent: number;
}

interface PolicySuggestion {
  suggestion_id: string;
  policy_area: string;
  suggestion: string;
  confidence: number;
  supporting_evidence: string[];
  created_at: string;
}

const API_BASE = 'http://localhost:8000';

export const Layer3IntentLearning: React.FC = () => {
  const [intents, setIntents] = useState<Intent[]>([]);
  const [retrospectives, setRetrospectives] = useState<Retrospective[]>([]);
  const [playbooks, setPlaybooks] = useState<PlaybookStats[]>([]);
  const [policySuggestions, setPolicySuggestions] = useState<PolicySuggestion[]>([]);
  const [selectedIntent, setSelectedIntent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchIntents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/intent/active`);
      setIntents(response.data.intents || []);
    } catch (error) {
      console.error('Failed to fetch intents:', error);
    }
  };

  const fetchRetrospectives = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/learning/retrospectives?limit=10`);
      setRetrospectives(response.data.retrospectives || []);
    } catch (error) {
      console.error('Failed to fetch retrospectives:', error);
    }
  };

  const fetchPlaybooks = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/learning/playbooks`);
      setPlaybooks(response.data.playbooks || []);
    } catch (error) {
      console.error('Failed to fetch playbooks:', error);
    }
  };

  const fetchPolicySuggestions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/telemetry/learning/policy_suggestions`);
      setPolicySuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Failed to fetch policy suggestions:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchIntents(),
        fetchRetrospectives(),
        fetchPlaybooks(),
        fetchPolicySuggestions()
      ]);
      setLoading(false);
    };

    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, 10000); // Refresh every 10 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return '#00aaff';
      case 'pending': return '#ffaa00';
      case 'completed': return '#00ff88';
      case 'failed': return '#ff4444';
      default: return '#888';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#00ff88';
    if (confidence >= 0.6) return '#ffaa00';
    return '#ff4444';
  };

  if (loading) {
    return <div className="learning-console-loading">Loading Intent & Learning Console...</div>;
  }

  return (
    <div className="layer3-intent-learning">
      <div className="console-header">
        <h1>🧠 Layer 3: Intent & Learning</h1>
        <div className="header-controls">
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (10s)
          </label>
          <button onClick={() => window.location.reload()}>Refresh All</button>
        </div>
      </div>

      {/* Active Intents */}
      <section className="intents-section">
        <h2>Active Intents</h2>
        <div className="intents-grid">
          {intents.length > 0 ? (
            intents.map((intent) => (
              <div
                key={intent.intent_id}
                className="intent-card"
                onClick={() => setSelectedIntent(intent.intent_id)}
              >
                <div className="intent-header">
                  <span
                    className="intent-status"
                    style={{ backgroundColor: getStatusColor(intent.status) }}
                  >
                    {intent.status}
                  </span>
                  <span className="intent-id">{intent.intent_id.substring(0, 8)}</span>
                </div>
                <div className="intent-goal">{intent.goal}</div>
                <div className="intent-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${intent.completion_percent}%` }}
                    ></div>
                  </div>
                  <div className="progress-text">{intent.completion_percent}% complete</div>
                </div>
                <div className="intent-meta">
                  <div className="meta-item">
                    <span>HTM Tasks:</span>
                    <strong>{intent.htm_tasks_generated}</strong>
                  </div>
                  <div className="meta-item">
                    <span>Created:</span>
                    <strong>{new Date(intent.created_at).toLocaleDateString()}</strong>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">No active intents</div>
          )}
        </div>
      </section>

      {/* Playbook Success Rates */}
      <section className="playbooks-section">
        <h2>Playbook Success Rates</h2>
        <div className="playbooks-table-container">
          <table className="playbooks-table">
            <thead>
              <tr>
                <th>Playbook Name</th>
                <th>Total Runs</th>
                <th>Success Rate</th>
                <th>Performance</th>
              </tr>
            </thead>
            <tbody>
              {playbooks.length > 0 ? (
                playbooks.map((playbook) => (
                  <tr key={playbook.playbook_name}>
                    <td className="playbook-name">{playbook.playbook_name}</td>
                    <td>{playbook.total_runs}</td>
                    <td>
                      <span
                        className="success-rate"
                        style={{ color: getConfidenceColor(playbook.success_rate_percent / 100) }}
                      >
                        {playbook.success_rate_percent}%
                      </span>
                    </td>
                    <td>
                      <div className="success-bar">
                        <div
                          className="success-fill"
                          style={{
                            width: `${playbook.success_rate_percent}%`,
                            backgroundColor: getConfidenceColor(playbook.success_rate_percent / 100)
                          }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="empty-state">No playbook data</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Learning Retrospectives */}
      <section className="retrospectives-section">
        <h2>Learning Retrospectives</h2>
        <div className="retrospectives-list">
          {retrospectives.length > 0 ? (
            retrospectives.map((retro) => (
              <div key={retro.id} className="retrospective-card">
                <div className="retro-header">
                  <h3>{retro.cycle_name}</h3>
                  <span className="retro-timestamp">
                    {new Date(retro.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="retro-content">
                  <div className="retro-section">
                    <h4>💡 Insights</h4>
                    <ul>
                      {retro.insights.map((insight, idx) => (
                        <li key={idx}>{insight}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="retro-section">
                    <h4>⬆️ Improvements</h4>
                    <ul>
                      {retro.improvements.map((improvement, idx) => (
                        <li key={idx}>{improvement}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">No retrospectives available</div>
          )}
        </div>
      </section>

      {/* Policy Suggestions */}
      <section className="policy-section">
        <h2>AI Policy Suggestions</h2>
        <div className="policy-suggestions">
          {policySuggestions.length > 0 ? (
            policySuggestions.map((suggestion) => (
              <div key={suggestion.suggestion_id} className="policy-card">
                <div className="policy-header">
                  <span className="policy-area">{suggestion.policy_area}</span>
                  <span
                    className="confidence-badge"
                    style={{ backgroundColor: getConfidenceColor(suggestion.confidence) }}
                  >
                    {Math.round(suggestion.confidence * 100)}% confidence
                  </span>
                </div>
                <div className="policy-suggestion">{suggestion.suggestion}</div>
                <div className="policy-evidence">
                  <h5>Supporting Evidence:</h5>
                  <ul>
                    {suggestion.supporting_evidence.map((evidence, idx) => (
                      <li key={idx}>{evidence}</li>
                    ))}
                  </ul>
                </div>
                <div className="policy-actions">
                  <button className="btn-accept">✓ Accept</button>
                  <button className="btn-review">👁️ Review</button>
                  <button className="btn-reject">✕ Reject</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">No pending policy suggestions</div>
          )}
        </div>
      </section>
    </div>
  );
};
