import React, { useState, useEffect } from 'react';

interface DashboardData {
  summary: {
    total_playbooks: number;
    success_rate: number;
    open_incidents: number;
    active_agents: number;
  };
  playbooks: any;
  recent_runs: any;
  open_incidents: any;
  active_agents: any;
  recent_insights: any;
}

export default function SelfHealingDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('playbooks');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch data from multiple endpoints
      const [statusRes, playbooksRes, activeRunsRes, metricsRes] = await Promise.all([
        fetch('/api/self-healing/status'),
        fetch('/api/self-healing/playbooks'),
        fetch('/api/self-healing/active-runs'),
        fetch('/api/self-healing/metrics')
      ]);

      const [statusData, playbooksData, activeRunsData, metricsData] = await Promise.all([
        statusRes.json(),
        playbooksRes.json(),
        activeRunsRes.json(),
        metricsRes.json()
      ]);

      // Combine data into expected format
      const combinedData = {
        summary: {
          total_playbooks: playbooksData.count || 0,
          success_rate: metricsData.performance?.average_success_rate ? Math.round(metricsData.performance.average_success_rate * 100) : 0,
          open_incidents: 0, // TODO: Add incidents endpoint
          active_agents: activeRunsData.count || 0
        },
        playbooks: playbooksData,
        recent_runs: [], // TODO: Add execution logs endpoint
        open_incidents: [], // TODO: Add incidents endpoint
        active_agents: [], // TODO: Add agents endpoint
        recent_insights: [] // TODO: Add insights endpoint
      };

      setDashboardData(combinedData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runPlaybook = async (playbookId: string) => {
    try {
      const response = await fetch(`/api/self-healing/trigger-manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ component: 'manual_trigger', error_details: { playbook_id: playbookId } })
      });
      const result = await response.json();

      if (result.status === 'triggered') {
        alert(`Self-healing triggered for playbook`);
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to trigger self-healing:', error);
      alert('Failed to trigger self-healing');
    }
  };

  if (loading) {
    return (
      <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Loading self-healing dashboard...
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#ff6b6b' }}>
        Failed to load dashboard data
      </div>
    );
  }

  const { summary, playbooks } = dashboardData;

  return (
    <div style={{ background: '#0f0f1e', minHeight: '100vh', padding: '2rem', color: '#fff' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ color: '#00d4ff', marginBottom: '0.5rem', fontSize: '2rem', fontWeight: 'bold' }}>
            Self-Healing Co-pilot
          </h1>
          <p style={{ color: '#888' }}>Collaborative autonomous remediation</p>
        </div>
        <button
          onClick={fetchDashboardData}
          style={{
            background: '#7b2cbf',
            color: '#fff',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ fontSize: '1.5rem' }}>📚</div>
            <div>
              <p style={{ color: '#7b2cbf', marginBottom: '0.25rem', fontSize: '0.875rem' }}>PLAYBOOKS</p>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>{summary.total_playbooks}</p>
            </div>
          </div>
        </div>

        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ fontSize: '1.5rem' }}>✅</div>
            <div>
              <p style={{ color: '#7b2cbf', marginBottom: '0.25rem', fontSize: '0.875rem' }}>SUCCESS RATE</p>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>{summary.success_rate}%</p>
            </div>
          </div>
        </div>

        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ fontSize: '1.5rem' }}>🚨</div>
            <div>
              <p style={{ color: '#7b2cbf', marginBottom: '0.25rem', fontSize: '0.875rem' }}>OPEN INCIDENTS</p>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>{summary.open_incidents}</p>
            </div>
          </div>
        </div>

        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ fontSize: '1.5rem' }}>🤖</div>
            <div>
              <p style={{ color: '#7b2cbf', marginBottom: '0.25rem', fontSize: '0.875rem' }}>ACTIVE AGENTS</p>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>{summary.active_agents}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.25rem', borderBottom: '1px solid #333' }}>
          {['playbooks', 'runs', 'incidents', 'agents', 'insights'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '0.75rem 1.5rem',
                background: activeTab === tab ? '#7b2cbf' : 'transparent',
                color: '#fff',
                border: 'none',
                borderRadius: '8px 8px 0 0',
                cursor: 'pointer',
                textTransform: 'capitalize'
              }}
            >
              {tab.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'playbooks' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '1.5rem' }}>
          {playbooks.playbooks?.map((playbook: any) => (
            <div
              key={playbook.id}
              style={{
                background: '#1a1a2e',
                padding: '1.5rem',
                borderRadius: '12px',
                border: '1px solid #333',
                cursor: 'pointer'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h3 style={{ color: '#00d4ff', fontSize: '1.25rem', fontWeight: 'bold' }}>
                  {playbook.playbook_name}
                </h3>
                <button
                  onClick={() => runPlaybook(playbook.id)}
                  style={{
                    background: '#00d4ff',
                    color: '#000',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  ▶️ Run
                </button>
              </div>

              <p style={{ color: '#ccc', marginBottom: '1rem', fontSize: '0.875rem' }}>
                {playbook.description}
              </p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                {playbook.target_components?.map((component: string, idx: number) => (
                  <span
                    key={idx}
                    style={{
                      background: '#7b2cbf',
                      color: '#fff',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}
                  >
                    {component}
                  </span>
                ))}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                <span>
                  Risk: <span style={{
                    color: playbook.risk_level === 'high' ? '#ff6b6b' :
                           playbook.risk_level === 'medium' ? '#ffa500' : '#4ade80'
                  }}>
                    {playbook.risk_level}
                  </span>
                </span>
                <span>
                  Success: {playbook.successful_runs || 0}/{playbook.total_runs || 0}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'runs' && (
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Recent Executions</h3>
          <p style={{ color: '#888' }}>Execution logs will appear here...</p>
        </div>
      )}

      {activeTab === 'incidents' && (
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Open Incidents</h3>
          <p style={{ color: '#888' }}>Active incidents will appear here...</p>
        </div>
      )}

      {activeTab === 'agents' && (
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Active Agents</h3>
          <p style={{ color: '#888' }}>Running self-healing agents will appear here...</p>
        </div>
      )}

      {activeTab === 'insights' && (
        <div style={{ background: '#1a1a2e', padding: '1.5rem', borderRadius: '12px', border: '1px solid #333' }}>
          <h3 style={{ color: '#00d4ff', marginBottom: '1rem' }}>Grace's Insights</h3>
          <p style={{ color: '#888' }}>AI-generated insights will appear here...</p>
        </div>
      )}
    </div>
  );
}