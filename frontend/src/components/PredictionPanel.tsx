import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Prediction {
  event_type: string;
  probability: number;
}

interface Pattern {
  pattern_type: string;
  sequence: string[];
  frequency: number;
  confidence: number;
}

interface DurationEstimate {
  task_type: string;
  avg_duration: number;
  min: number;
  max: number;
  confidence: number;
}

interface SimulationResult {
  summary: {
    response_time_change_pct: number;
    completion_rate_change_pct: number;
    resource_usage_change_pct: number;
    recommendation: string;
  };
}

const PredictionPanel: React.FC = () => {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [durations, setDurations] = useState<DurationEstimate[]>([]);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'predictions' | 'patterns' | 'durations' | 'simulation'>('predictions');

  const fetchPredictions = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/temporal/predict', {
        current_state: { last_event_type: 'task_created' },
        lookback_hours: 24
      });
      setPredictions(response.data.predictions);
      setPatterns(response.data.discovered_patterns);
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
    }
    setLoading(false);
  };

  const fetchDurations = async () => {
    try {
      const response = await axios.get('/api/temporal/durations');
      setDurations(response.data.estimates || []);
    } catch (error) {
      console.error('Failed to fetch durations:', error);
    }
  };

  const runSimulation = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/temporal/simulate', {
        action: {
          type: 'change_reflection_interval',
          current_interval: 30,
          new_interval: 60
        },
        iterations: 1000
      });
      setSimulation(response.data.simulation_result);
    } catch (error) {
      console.error('Failed to run simulation:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPredictions();
    fetchDurations();
  }, []);

  const renderPredictions = () => (
    <div className="predictions-section">
      <h3>Next Likely Events</h3>
      {predictions.length === 0 ? (
        <p>No predictions available</p>
      ) : (
        <div className="predictions-list">
          {predictions.map((pred, idx) => (
            <div key={idx} className="prediction-item">
              <div className="prediction-event">{pred.event_type}</div>
              <div className="prediction-bar">
                <div 
                  className="prediction-fill" 
                  style={{ width: `${pred.probability * 100}%` }}
                />
              </div>
              <div className="prediction-prob">{(pred.probability * 100).toFixed(1)}%</div>
            </div>
          ))}
        </div>
      )}
      <button onClick={fetchPredictions} disabled={loading}>
        {loading ? 'Loading...' : 'Refresh Predictions'}
      </button>
    </div>
  );

  const renderPatterns = () => (
    <div className="patterns-section">
      <h3>Discovered Patterns</h3>
      {patterns.length === 0 ? (
        <p>No patterns discovered yet</p>
      ) : (
        <div className="patterns-list">
          {patterns.slice(0, 5).map((pattern, idx) => (
            <div key={idx} className="pattern-item">
              <div className="pattern-sequence">
                {pattern.sequence.join(' → ')}
              </div>
              <div className="pattern-meta">
                <span>Frequency: {pattern.frequency}</span>
                <span>Confidence: {(pattern.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderDurations = () => (
    <div className="durations-section">
      <h3>Task Duration Estimates</h3>
      {durations.length === 0 ? (
        <p>No duration data available</p>
      ) : (
        <div className="durations-list">
          {durations.map((dur, idx) => (
            <div key={idx} className="duration-item">
              <div className="duration-type">{dur.task_type}</div>
              <div className="duration-stats">
                <div>Avg: {dur.avg_duration.toFixed(0)}s</div>
                <div>Range: {dur.min?.toFixed(0)}s - {dur.max?.toFixed(0)}s</div>
                <div>Confidence: {(dur.confidence * 100).toFixed(0)}%</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderSimulation = () => (
    <div className="simulation-section">
      <h3>What-If Simulation</h3>
      <button onClick={runSimulation} disabled={loading}>
        {loading ? 'Running Simulation...' : 'Simulate: Increase Interval to 60s'}
      </button>
      
      {simulation && (
        <div className="simulation-results">
          <h4>Predicted Impact</h4>
          <div className="impact-metrics">
            <div className={`metric ${simulation.summary.response_time_change_pct > 0 ? 'negative' : 'positive'}`}>
              <span>Response Time</span>
              <span>{simulation.summary.response_time_change_pct > 0 ? '+' : ''}{simulation.summary.response_time_change_pct.toFixed(1)}%</span>
            </div>
            <div className={`metric ${simulation.summary.completion_rate_change_pct < 0 ? 'negative' : 'positive'}`}>
              <span>Completion Rate</span>
              <span>{simulation.summary.completion_rate_change_pct > 0 ? '+' : ''}{simulation.summary.completion_rate_change_pct.toFixed(1)}%</span>
            </div>
            <div className={`metric ${simulation.summary.resource_usage_change_pct > 0 ? 'negative' : 'positive'}`}>
              <span>Resource Usage</span>
              <span>{simulation.summary.resource_usage_change_pct > 0 ? '+' : ''}{simulation.summary.resource_usage_change_pct.toFixed(1)}%</span>
            </div>
          </div>
          <div className="recommendation">
            <strong>Recommendation:</strong> {simulation.summary.recommendation}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="prediction-panel">
      <div className="panel-header">
        <h2>🔮 Temporal Predictions</h2>
        <p>AI-powered forecasting and simulation</p>
      </div>

      <div className="panel-tabs">
        <button 
          className={activeTab === 'predictions' ? 'active' : ''} 
          onClick={() => setActiveTab('predictions')}
        >
          Predictions
        </button>
        <button 
          className={activeTab === 'patterns' ? 'active' : ''} 
          onClick={() => setActiveTab('patterns')}
        >
          Patterns
        </button>
        <button 
          className={activeTab === 'durations' ? 'active' : ''} 
          onClick={() => setActiveTab('durations')}
        >
          Durations
        </button>
        <button 
          className={activeTab === 'simulation' ? 'active' : ''} 
          onClick={() => setActiveTab('simulation')}
        >
          Simulation
        </button>
      </div>

      <div className="panel-content">
        {activeTab === 'predictions' && renderPredictions()}
        {activeTab === 'patterns' && renderPatterns()}
        {activeTab === 'durations' && renderDurations()}
        {activeTab === 'simulation' && renderSimulation()}
      </div>

      <style>{`
        .prediction-panel {
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          padding: 20px;
          margin: 20px 0;
        }

        .panel-header h2 {
          margin: 0 0 5px 0;
          color: #333;
        }

        .panel-header p {
          margin: 0;
          color: #666;
          font-size: 14px;
        }

        .panel-tabs {
          display: flex;
          gap: 10px;
          margin: 20px 0;
          border-bottom: 2px solid #eee;
        }

        .panel-tabs button {
          padding: 10px 20px;
          border: none;
          background: none;
          cursor: pointer;
          color: #666;
          border-bottom: 2px solid transparent;
          margin-bottom: -2px;
          transition: all 0.3s;
        }

        .panel-tabs button.active {
          color: #4a90e2;
          border-bottom-color: #4a90e2;
          font-weight: 600;
        }

        .panel-tabs button:hover {
          color: #4a90e2;
        }

        .predictions-list, .patterns-list, .durations-list {
          margin: 15px 0;
        }

        .prediction-item {
          display: grid;
          grid-template-columns: 150px 1fr 60px;
          gap: 10px;
          align-items: center;
          padding: 10px;
          border-bottom: 1px solid #eee;
        }

        .prediction-event {
          font-weight: 500;
          color: #333;
        }

        .prediction-bar {
          background: #f0f0f0;
          border-radius: 4px;
          height: 8px;
          overflow: hidden;
        }

        .prediction-fill {
          background: linear-gradient(90deg, #4a90e2, #67b26f);
          height: 100%;
          transition: width 0.3s;
        }

        .prediction-prob {
          text-align: right;
          color: #666;
          font-size: 14px;
        }

        .pattern-item {
          padding: 12px;
          background: #f9f9f9;
          border-radius: 6px;
          margin-bottom: 10px;
        }

        .pattern-sequence {
          font-family: monospace;
          color: #333;
          margin-bottom: 8px;
        }

        .pattern-meta {
          display: flex;
          gap: 20px;
          font-size: 13px;
          color: #666;
        }

        .duration-item {
          display: grid;
          grid-template-columns: 200px 1fr;
          gap: 15px;
          padding: 12px;
          border-bottom: 1px solid #eee;
        }

        .duration-type {
          font-weight: 600;
          color: #333;
        }

        .duration-stats {
          display: flex;
          gap: 20px;
          font-size: 14px;
          color: #666;
        }

        .simulation-section button {
          background: #4a90e2;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          margin-bottom: 20px;
        }

        .simulation-section button:hover:not(:disabled) {
          background: #357abd;
        }

        .simulation-section button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .simulation-results {
          background: #f9f9f9;
          padding: 20px;
          border-radius: 6px;
        }

        .simulation-results h4 {
          margin: 0 0 15px 0;
          color: #333;
        }

        .impact-metrics {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 15px;
          margin-bottom: 20px;
        }

        .metric {
          display: flex;
          flex-direction: column;
          padding: 15px;
          border-radius: 6px;
          background: white;
        }

        .metric.positive {
          border-left: 4px solid #67b26f;
        }

        .metric.negative {
          border-left: 4px solid #e74c3c;
        }

        .metric span:first-child {
          font-size: 13px;
          color: #666;
          margin-bottom: 5px;
        }

        .metric span:last-child {
          font-size: 20px;
          font-weight: 600;
          color: #333;
        }

        .recommendation {
          padding: 15px;
          background: #e8f4fd;
          border-radius: 6px;
          border-left: 4px solid #4a90e2;
        }

        .recommendation strong {
          color: #333;
        }
      `}</style>
    </div>
  );
};

export default PredictionPanel;
