/**
 * Layer 3 Dashboard - MVP
 * Learning & Intent Console with kernel terminals and simple intent creation
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { KernelTerminal } from '../components/KernelTerminal';
import { CoPilotPane } from '../components/CoPilotPane';
import './Layer3DashboardMVP.css';

interface Intent {
  intent_id: string;
  goal: string;
  status: string;
  completion_percent: number;
  created_at: string;
  htm_tasks_generated: number;
}

interface Retrospective {
  id: string;
  cycle_name: string;
  insights: string[];
  improvements: string[];
  timestamp: string;
}

const API_BASE = 'http://localhost:8000';

export const Layer3DashboardMVP: React.FC = () => {
  const [kernels, setKernels] = useState([]);
  const [intents, setIntents] = useState<Intent[]>([]);
  const [retrospectives, setRetrospectives] = useState<Retrospective[]>([]);
  const [showIntentForm, setShowIntentForm] = useState(false);
  const [newIntent, setNewIntent] = useState({
    goal: '',
    data_source: 'uploaded_files',
    priority: 'normal'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchKernels(),
        fetchIntents(),
        fetchRetrospectives()
      ]);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
    setLoading(false);
  };

  const fetchKernels = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/kernels/layer3/status`);
      setKernels(response.data.kernels || []);
    } catch (error) {
      console.error('Failed to fetch kernels:', error);
    }
  };

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
      const response = await axios.get(`${API_BASE}/api/telemetry/learning/retrospectives?limit=5`);
      setRetrospectives(response.data.retrospectives || []);
    } catch (error) {
      console.error('Failed to fetch retrospectives:', error);
    }
  };

  const handleCreateIntent = async () => {
    if (!newIntent.goal.trim()) {
      alert('Please enter a goal');
      return;
    }

    try {
      await axios.post(`${API_BASE}/api/intent/create`, newIntent);
      setShowIntentForm(false);
      setNewIntent({ goal: '', data_source: 'uploaded_files', priority: 'normal' });
      await fetchIntents();
      alert('Intent created successfully');
    } catch (error) {
      console.error('Failed to create intent:', error);
      alert('Failed to create intent');
    }
  };

  const handleKernelAction = async (kernelId: string, action: string) => {
    try {
      await axios.post(`${API_BASE}/api/kernels/${kernelId}/action`, { action });
      await fetchKernels();
      alert(`Action '${action}' executed successfully`);
    } catch (error) {
      console.error('Kernel action failed:', error);
    }
  };

  const handleCoPilotAction = async (action: string) => {
    if (action === 'create_intent') {
      setShowIntentForm(true);
    } else if (action === 'review_policies') {
      alert('Policy review (feature coming soon)');
    } else if (action === 'generate_retro') {
      alert('Generate retrospective (feature coming soon)');
    } else if (action === 'export_learning') {
      alert('Export learning report (feature coming soon)');
    }
  };

  if (loading && intents.length === 0) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <div>Loading Layer 3 Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="layer3-dashboard-mvp">
      <div className="dashboard-main">
        {/* Header */}
        <div className="dashboard-header">
          <h1>🧠 Layer 3: Intent & Learning</h1>
          <div className="header-actions">
            <button onClick={loadData}>{loading ? '⟳ Refreshing...' : '↻ Refresh'}</button>
          </div>
        </div>

        {/* Active Intents */}
        <section className="intents-section">
          <div className="section-header">
            <h2>Active Intents</h2>
            <button className="create-btn" onClick={() => setShowIntentForm(true)}>
              + Create Intent
            </button>
          </div>
          <div className="intents-table">
            {intents.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th>Intent ID</th>
                    <th>Goal</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th>HTM Tasks</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {intents.map((intent) => (
                    <tr key={intent.intent_id}>
                      <td className="intent-id">{intent.intent_id}</td>
                      <td className="intent-goal">{intent.goal}</td>
                      <td>
                        <span className={`status-badge ${intent.status}`}>
                          {intent.status}
                        </span>
                      </td>
                      <td>
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${intent.completion_percent}%` }}
                          ></div>
                          <span>{intent.completion_percent}%</span>
                        </div>
                      </td>
                      <td>{intent.htm_tasks_generated}</td>
                      <td>{new Date(intent.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-state">No active intents. Create one to get started!</div>
            )}
          </div>
        </section>

        {/* Retrospectives */}
        <section className="retrospectives-section">
          <h2>Recent Learning Cycles</h2>
          <div className="retrospectives-list">
            {retrospectives.length > 0 ? (
              retrospectives.map((retro) => (
                <div key={retro.id} className="retrospective-card">
                  <div className="retro-header">
                    <h3>{retro.cycle_name}</h3>
                    <span className="retro-time">
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

        {/* Agentic Brain Kernels */}
        <section className="kernels-section">
          <h2>Agentic Brain Kernels</h2>
          <div className="kernels-list">
            {kernels.map((kernel: any) => (
              <KernelTerminal
                key={kernel.kernel_id}
                kernel={kernel}
                onAction={handleKernelAction}
                showQuickActions={true}
                showConfig={false}
              />
            ))}
          </div>
        </section>
      </div>

      {/* Intent Creation Form Modal */}
      {showIntentForm && (
        <div className="modal-overlay" onClick={() => setShowIntentForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Intent</h3>
              <button className="close-btn" onClick={() => setShowIntentForm(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Goal</label>
                <textarea
                  rows={3}
                  placeholder="E.g., Analyze Q4 financial data and generate insights"
                  value={newIntent.goal}
                  onChange={(e) => setNewIntent({ ...newIntent, goal: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Data Source</label>
                <select
                  value={newIntent.data_source}
                  onChange={(e) => setNewIntent({ ...newIntent, data_source: e.target.value })}
                >
                  <option value="uploaded_files">Uploaded Files</option>
                  <option value="database">Database</option>
                  <option value="external_api">External API</option>
                  <option value="real_time">Real-time Stream</option>
                </select>
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={newIntent.priority}
                  onChange={(e) => setNewIntent({ ...newIntent, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowIntentForm(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleCreateIntent}>
                Create Intent
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Co-Pilot Pane */}
      <CoPilotPane
        currentLayer="layer3"
        onAction={handleCoPilotAction}
      />
    </div>
  );
};
