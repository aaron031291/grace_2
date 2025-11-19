import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import './CognitiveObservatory.css';

interface ReasoningChain {
  cycle_id: string;
  stage: string;
  decision: string;
  reasoning: string;
  confidence: number;
  evidence: string[];
  alternatives: string[];
  timestamp: string;
}

interface CognitiveUpdate {
  status: string;
  current_stage?: string;
  reasoning?: string;
  confidence?: number;
  evidence?: string[];
  alternatives?: string[];
}

const CognitiveObservatory: React.FC = () => {
  const [currentState, setCurrentState] = useState<CognitiveUpdate | null>(null);
  const [reasoningChains, setReasoningChains] = useState<ReasoningChain[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    fetchReasoningChains();

    // Setup WebSocket for real-time updates
    const token = localStorage.getItem('token');
    const websocket = new WebSocket(`${WS_BASE_URL}/api/dashboard/ws/cognitive?token=${token}`);
    
    websocket.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.type === 'cognitive_update') {
        setCurrentState(update.data);
      }
    };

    setWs(websocket);

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const fetchReasoningChains = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(apiUrl('/api/dashboard/cognitive/reasoning?limit=5', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setReasoningChains(data.chains || []);
  };

  return (
    <div className="cognitive-observatory">
      <div className="observatory-header">
        <h1>🔬 Cognitive Observatory</h1>
        <p className="subtitle">Watch Grace think in real-time</p>
        <div className="status-indicator">
          <div className={`status-dot ${currentState?.status === 'active' ? 'active' : 'idle'}`}></div>
          <span>{currentState?.status === 'active' ? 'Thinking...' : 'Idle'}</span>
        </div>
      </div>

      <div className="observatory-main">
        <div className="current-thought">
          <h2>Current Thought Process</h2>
          
          {currentState?.status === 'active' ? (
            <div className="thought-container">
              <div className="thought-stage">
                <span className="stage-label">Stage:</span>
                <span className="stage-value">{currentState.current_stage}</span>
              </div>

              {currentState.reasoning && (
                <div className="thought-reasoning">
                  <h3>💭 Grace's Reasoning</h3>
                  <p className="reasoning-text">{currentState.reasoning}</p>
                </div>
              )}

              {currentState.confidence !== undefined && (
                <div className="thought-confidence">
                  <h3>Confidence Level</h3>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${currentState.confidence * 100}%` }}
                    >
                      <span className="confidence-value">
                        {(currentState.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {currentState.evidence && currentState.evidence.length > 0 && (
                <div className="thought-evidence">
                  <h3>📊 Evidence</h3>
                  <ul className="evidence-list">
                    {currentState.evidence.map((item, idx) => (
                      <li key={idx}>
                        <span className="evidence-marker">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {currentState.alternatives && currentState.alternatives.length > 0 && (
                <div className="thought-alternatives">
                  <h3>🔀 Alternatives Considered</h3>
                  <div className="alternatives-grid">
                    {currentState.alternatives.map((alt, idx) => (
                      <div key={idx} className="alternative-card">
                        <span className="alt-number">{idx + 1}</span>
                        <span className="alt-text">{alt}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="thought-idle">
              <div className="idle-icon">💤</div>
              <p>Grace is currently idle</p>
              <p className="idle-subtitle">Waiting for input or scheduled tasks...</p>
            </div>
          )}
        </div>

        <div className="reasoning-history">
          <h2>Recent Decisions</h2>
          
          <div className="chains-list">
            {reasoningChains.map((chain, idx) => (
              <div key={idx} className="chain-card">
                <div className="chain-header">
                  <span className="chain-stage">{chain.stage}</span>
                  <span className="chain-time">
                    {new Date(chain.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div className="chain-decision">
                  <strong>Decision:</strong> {chain.decision}
                </div>

                <div className="chain-reasoning">
                  <strong>Reasoning:</strong> {chain.reasoning}
                </div>

                <div className="chain-confidence">
                  <div className="mini-confidence-bar">
                    <div 
                      className="mini-confidence-fill"
                      style={{ width: `${chain.confidence * 100}%` }}
                    />
                  </div>
                  <span>{(chain.confidence * 100).toFixed(0)}%</span>
                </div>

                {chain.evidence && chain.evidence.length > 0 && (
                  <div className="chain-evidence-count">
                    <span>📊 {chain.evidence.length} evidence points</span>
                  </div>
                )}
              </div>
            ))}

            {reasoningChains.length === 0 && (
              <div className="no-chains">
                <p>No recent decision chains</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="observatory-footer">
        <p className="footer-note">
          Updates every second • Real-time WebSocket connection
        </p>
      </div>
    </div>
  );
};

export default CognitiveObservatory;
