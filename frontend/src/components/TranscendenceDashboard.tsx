import React, { useState, useEffect } from 'react';
import './TranscendenceDashboard.css';

interface CognitiveState {
  status: string;
  cycle_id?: string;
  current_stage?: string;
  current_substage?: string;
  reasoning?: string;
  confidence?: number;
  evidence?: string[];
  alternatives?: string[];
  decision?: string;
  progress?: {
    completed_steps: number;
    total_steps: number;
    stages: string[];
  };
}

interface Proposal {
  proposal_id: string;
  title: string;
  description: string;
  proposer: string;
  category: string;
  impact: number;
  created_at: string;
}

interface RevenueData {
  profit: {
    revenue: number;
    expenses: number;
    profit: number;
    profit_margin: number;
  };
  sources: Array<{
    source: string;
    category: string;
    total_revenue: number;
    transaction_count: number;
  }>;
  growth: {
    growth_rate: number;
    growth_direction: string;
  };
}

const TranscendenceDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('COGNITIVE');
  const [cognitiveState, setCognitiveState] = useState<CognitiveState | null>(null);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [revenueData, setRevenueData] = useState<RevenueData | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Fetch initial data
    fetchCognitiveState();
    fetchProposals();
    fetchRevenueData();

    // Setup WebSocket for real-time updates
    const token = localStorage.getItem('token');
    const websocket = new WebSocket(`ws://localhost:8000/api/dashboard/ws/cognitive?token=${token}`);
    
    websocket.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.type === 'cognitive_update') {
        setCognitiveState(update.data);
      }
    };

    setWs(websocket);

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const fetchCognitiveState = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/dashboard/cognitive/current', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setCognitiveState(data);
  };

  const fetchProposals = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/dashboard/proposals/pending', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setProposals(data.proposals || []);
  };

  const fetchRevenueData = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/dashboard/business/revenue', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setRevenueData(data);
  };

  const approveProposal = async (proposalId: string) => {
    const token = localStorage.getItem('token');
    await fetch(`http://localhost:8000/api/parliament/proposals/${proposalId}/vote`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ vote: 'approve' })
    });
    fetchProposals();
  };

  const rejectProposal = async (proposalId: string) => {
    const token = localStorage.getItem('token');
    await fetch(`http://localhost:8000/api/parliament/proposals/${proposalId}/vote`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ vote: 'reject' })
    });
    fetchProposals();
  };

  return (
    <div className="transcendence-dashboard">
      <div className="dashboard-header">
        <h1>🧠 Grace Transcendence Dashboard</h1>
        <p className="subtitle">Real-time cognitive state, business metrics, and system control</p>
      </div>

      <div className="dashboard-tabs">
        {['COGNITIVE', 'LEARNING', 'BUSINESS', 'PROPOSALS', 'PARLIAMENT', 'MEMORY', 'MODELS'].map(tab => (
          <button
            key={tab}
            className={`tab-button ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="dashboard-content">
        {activeTab === 'COGNITIVE' && (
          <div className="cognitive-panel">
            <h2>Current Cognitive State</h2>
            {cognitiveState?.status === 'active' ? (
              <div className="cognitive-active">
                <div className="cognitive-header">
                  <span className="status-badge active">THINKING</span>
                  <span className="cycle-id">Cycle: {cognitiveState.cycle_id}</span>
                </div>

                <div className="cognitive-stage">
                  <h3>Stage: {cognitiveState.current_stage}</h3>
                  {cognitiveState.current_substage && (
                    <p className="substage">{cognitiveState.current_substage}</p>
                  )}
                </div>

                {cognitiveState.reasoning && (
                  <div className="reasoning-box">
                    <h4>Grace's Reasoning:</h4>
                    <p>{cognitiveState.reasoning}</p>
                  </div>
                )}

                <div className="confidence-meter">
                  <label>Confidence:</label>
                  <div className="meter">
                    <div 
                      className="meter-fill" 
                      style={{ width: `${(cognitiveState.confidence || 0) * 100}%` }}
                    />
                  </div>
                  <span>{((cognitiveState.confidence || 0) * 100).toFixed(0)}%</span>
                </div>

                {cognitiveState.evidence && cognitiveState.evidence.length > 0 && (
                  <div className="evidence-section">
                    <h4>Evidence:</h4>
                    <ul>
                      {cognitiveState.evidence.map((ev, idx) => (
                        <li key={idx}>{ev}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {cognitiveState.alternatives && cognitiveState.alternatives.length > 0 && (
                  <div className="alternatives-section">
                    <h4>Alternatives Considered:</h4>
                    <ul>
                      {cognitiveState.alternatives.map((alt, idx) => (
                        <li key={idx}>{alt}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {cognitiveState.decision && (
                  <div className="decision-box">
                    <h4>Decision:</h4>
                    <p>{cognitiveState.decision}</p>
                  </div>
                )}

                {cognitiveState.progress && (
                  <div className="progress-section">
                    <h4>Progress:</h4>
                    <p>{cognitiveState.progress.completed_steps} / {cognitiveState.progress.total_steps} steps</p>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ 
                          width: `${(cognitiveState.progress.completed_steps / cognitiveState.progress.total_steps) * 100}%` 
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="cognitive-idle">
                <p>Grace is currently idle. Waiting for input...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'BUSINESS' && revenueData && (
          <div className="business-panel">
            <h2>Business Metrics</h2>

            <div className="metrics-grid">
              <div className="metric-card revenue">
                <h3>Revenue</h3>
                <p className="metric-value">${revenueData.profit.revenue.toFixed(2)}</p>
              </div>

              <div className="metric-card expenses">
                <h3>Expenses</h3>
                <p className="metric-value">${revenueData.profit.expenses.toFixed(2)}</p>
              </div>

              <div className="metric-card profit">
                <h3>Profit</h3>
                <p className="metric-value">${revenueData.profit.profit.toFixed(2)}</p>
                <p className="metric-subtitle">{revenueData.profit.profit_margin.toFixed(1)}% margin</p>
              </div>

              <div className="metric-card growth">
                <h3>Growth</h3>
                <p className="metric-value">{revenueData.growth.growth_rate.toFixed(1)}%</p>
                <p className={`metric-subtitle ${revenueData.growth.growth_direction}`}>
                  {revenueData.growth.growth_direction}
                </p>
              </div>
            </div>

            <div className="revenue-sources">
              <h3>Revenue Sources</h3>
              <table>
                <thead>
                  <tr>
                    <th>Source</th>
                    <th>Category</th>
                    <th>Revenue</th>
                    <th>Transactions</th>
                  </tr>
                </thead>
                <tbody>
                  {revenueData.sources.map((source, idx) => (
                    <tr key={idx}>
                      <td>{source.source}</td>
                      <td>{source.category}</td>
                      <td>${source.total_revenue.toFixed(2)}</td>
                      <td>{source.transaction_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'PROPOSALS' && (
          <div className="proposals-panel">
            <h2>Grace's Proposals</h2>
            <p className="panel-subtitle">{proposals.length} proposals awaiting your decision</p>

            <div className="proposals-list">
              {proposals.map(proposal => (
                <div key={proposal.proposal_id} className="proposal-card">
                  <div className="proposal-header">
                    <h3>{proposal.title}</h3>
                    <span className="proposal-category">{proposal.category}</span>
                  </div>

                  <p className="proposal-description">{proposal.description}</p>

                  <div className="proposal-meta">
                    <span className="proposer">Proposed by: {proposal.proposer}</span>
                    <span className="impact">Impact: {(proposal.impact * 100).toFixed(0)}%</span>
                  </div>

                  <div className="proposal-actions">
                    <button 
                      className="btn-approve"
                      onClick={() => approveProposal(proposal.proposal_id)}
                    >
                      ✓ Approve
                    </button>
                    <button 
                      className="btn-reject"
                      onClick={() => rejectProposal(proposal.proposal_id)}
                    >
                      ✗ Reject
                    </button>
                  </div>
                </div>
              ))}

              {proposals.length === 0 && (
                <div className="no-proposals">
                  <p>No pending proposals. Grace is working autonomously.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'LEARNING' && (
          <div className="learning-panel">
            <h2>8-Stage Learning Cycle</h2>
            <p>See how Grace learns and evolves</p>
            <div className="coming-soon">Coming soon: Learning cycle visualization</div>
          </div>
        )}

        {activeTab === 'PARLIAMENT' && (
          <div className="parliament-panel">
            <h2>Parliament Voting</h2>
            <p>Democratic decision-making system</p>
            <div className="coming-soon">Coming soon: Parliament interface</div>
          </div>
        )}

        {activeTab === 'MEMORY' && (
          <div className="memory-panel">
            <h2>Multi-Modal Memory</h2>
            <p>Explore Grace's memory artifacts</p>
            <div className="coming-soon">Coming soon: Memory browser</div>
          </div>
        )}

        {activeTab === 'MODELS' && (
          <div className="models-panel">
            <h2>ML/DL Models</h2>
            <p>Model performance and training</p>
            <div className="coming-soon">Coming soon: Model dashboard</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TranscendenceDashboard;
