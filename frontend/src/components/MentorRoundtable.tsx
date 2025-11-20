/**
 * Mentor Roundtable - Local Model Consultation Interface
 * 
 * Features:
 * - Start mentor roundtables
 * - View mentor responses
 * - See consensus and confidence
 * - Browse past roundtables
 * - Run benchmarks
 */

import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import './MentorRoundtable.css';

interface MentorProfile {
  specialization: string[];
  strengths: string;
  confidence_weight: number;
}

interface MentorResponse {
  model: string;
  response: string;
  confidence: number;
  specialization: string[];
  timestamp: string;
}

interface AggregatedInsights {
  consensus: string;
  consensus_model: string;
  average_confidence: number;
  total_mentors: number;
  response_spread: Record<string, number>;
}

interface RoundtableResult {
  task_id: string;
  task_type: string;
  models_queried: string[];
  responses: MentorResponse[];
  aggregated_insights: AggregatedInsights;
  stored_in_learning_memory: boolean;
}

interface MentorRoundtableProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MentorRoundtable: React.FC<MentorRoundtableProps> = ({ isOpen, onClose }) => {
  const [taskDescription, setTaskDescription] = useState('');
  const [taskType, setTaskType] = useState('general');
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [availableModels, setAvailableModels] = useState<Record<string, MentorProfile>>({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RoundtableResult | null>(null);
  const [recentRoundtables, setRecentRoundtables] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadAvailableModels();
      loadRecentRoundtables();
    }
  }, [isOpen]);

  const loadAvailableModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mentor/models`);
      const data = await response.json();
      setAvailableModels(data.profiles || {});
    } catch (err) {
      console.error('Failed to load models:', err);
    }
  };

  const loadRecentRoundtables = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mentor/recent`);
      const data = await response.json();
      setRecentRoundtables(data || []);
    } catch (err) {
      console.error('Failed to load recent roundtables:', err);
    }
  };

  const handleRunRoundtable = async () => {
    if (!taskDescription.trim()) {
      setError('Please enter a task description');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/mentor/roundtable`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_description: taskDescription,
          task_type: taskType,
          models: selectedModels.length > 0 ? selectedModels : null,
          store_results: true
        })
      });

      if (!response.ok) {
        throw new Error('Roundtable failed');
      }

      const data = await response.json();
      setResult(data.result);
      
      // Reload recent list
      await loadRecentRoundtables();

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run roundtable');
    } finally {
      setLoading(false);
    }
  };

  const toggleModel = (model: string) => {
    setSelectedModels(prev =>
      prev.includes(model)
        ? prev.filter(m => m !== model)
        : [...prev, model]
    );
  };

  if (!isOpen) return null;

  return (
    <div className="mentor-overlay" onClick={onClose}>
      <div className="mentor-panel" onClick={(e) => e.stopPropagation()}>
        <div className="mentor-header">
          <h2>🧙 Mentor Roundtable</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="mentor-content">
          {/* Input Section */}
          <div className="mentor-input-section">
            <h3>Consult Local Mentors</h3>
            
            <div className="form-group">
              <label>Task Description</label>
              <textarea
                className="task-input"
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                placeholder="Describe the task or question... (e.g., 'Design architecture for mobile app with offline sync')"
                rows={4}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Task Type</label>
              <select
                className="task-type-select"
                value={taskType}
                onChange={(e) => setTaskType(e.target.value)}
                disabled={loading}
              >
                <option value="general">General</option>
                <option value="code">Code</option>
                <option value="architecture">Architecture</option>
                <option value="planning">Planning</option>
                <option value="review">Code Review</option>
                <option value="debugging">Debugging</option>
                <option value="optimization">Optimization</option>
                <option value="ux">UX Design</option>
              </select>
            </div>

            <div className="form-group">
              <label>Select Mentors (leave empty for auto-select)</label>
              <div className="model-selection">
                {Object.entries(availableModels).map(([model, profile]) => (
                  <div
                    key={model}
                    className={`model-card ${selectedModels.includes(model) ? 'selected' : ''}`}
                    onClick={() => toggleModel(model)}
                  >
                    <div className="model-name">{model}</div>
                    <div className="model-spec">
                      {profile.specialization.join(', ')}
                    </div>
                    <div className="model-strength">{profile.strengths}</div>
                  </div>
                ))}
              </div>
            </div>

            <button
              className="run-roundtable-btn"
              onClick={handleRunRoundtable}
              disabled={loading || !taskDescription.trim()}
            >
              {loading ? '⏳ Consulting Mentors...' : '🚀 Run Roundtable'}
            </button>

            {error && (
              <div className="mentor-error">⚠️ {error}</div>
            )}
          </div>

          {/* Results Section */}
          {result && (
            <div className="mentor-results">
              <h3>🎯 Roundtable Results</h3>
              
              <div className="results-summary">
                <div className="summary-card">
                  <span className="summary-label">Models Queried</span>
                  <span className="summary-value">{result.models_queried.length}</span>
                </div>
                <div className="summary-card">
                  <span className="summary-label">Avg Confidence</span>
                  <span className="summary-value">
                    {(result.aggregated_insights.average_confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="summary-card">
                  <span className="summary-label">Consensus Model</span>
                  <span className="summary-value">{result.aggregated_insights.consensus_model}</span>
                </div>
              </div>

              <div className="consensus-section">
                <h4>💡 Consensus Recommendation</h4>
                <div className="consensus-text">
                  {result.aggregated_insights.consensus}
                </div>
              </div>

              <div className="responses-section">
                <h4>📋 Individual Mentor Responses</h4>
                {result.responses.map((response, idx) => (
                  <div key={idx} className="response-card">
                    <div className="response-header">
                      <span className="response-model">{response.model}</span>
                      <span className="response-confidence">
                        {(response.confidence * 100).toFixed(0)}% confident
                      </span>
                    </div>
                    <div className="response-specialization">
                      Specializations: {response.specialization.join(', ')}
                    </div>
                    <div className="response-text">{response.response}</div>
                  </div>
                ))}
              </div>

              {result.stored_in_learning_memory && (
                <div className="storage-notice">
                  ✅ Results stored in Learning Memory for future reference
                </div>
              )}
            </div>
          )}

          {/* Recent Roundtables */}
          {recentRoundtables.length > 0 && !result && (
            <div className="recent-section">
              <h3>📚 Recent Roundtables</h3>
              {recentRoundtables.map((rt, idx) => (
                <div key={idx} className="recent-item">
                  <div className="recent-header">
                    <span className="recent-type">{rt.task_type}</span>
                    <span className="recent-date">
                      {new Date(rt.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="recent-stats">
                    <span>{rt.models_queried} models</span>
                    <span>{(rt.consensus_confidence * 100).toFixed(0)}% confidence</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
