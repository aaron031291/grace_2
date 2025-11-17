import { useState, useEffect } from 'react';
import { Workspace } from '../../GraceEnterpriseUI';
import { agenticApi, AgenticEvent, AgenticAction, AgenticReflection, Skill, SkillStats, AgenticHealth } from '../../api/agenticApi';
import '../WorkspaceCommon.css';
import './AgenticWorkspace.css';

interface AgenticWorkspaceProps {
  workspace: Workspace;
  onShowTrace?: (traceId: string) => void;
}

type TabType = 'events' | 'actions' | 'reflections' | 'skills' | 'health';

export function AgenticWorkspace({ workspace, onShowTrace }: AgenticWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<TabType>('events');
  const [events, setEvents] = useState<AgenticEvent[]>([]);
  const [actions, setActions] = useState<AgenticAction[]>([]);
  const [reflections, setReflections] = useState<AgenticReflection[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [skillStats, setSkillStats] = useState<SkillStats[]>([]);
  const [health, setHealth] = useState<AgenticHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchData, 3000);
      return () => clearInterval(interval);
    }
  }, [activeTab, autoRefresh]);

  const fetchData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'events':
          const eventsData = await agenticApi.getEvents(200);
          setEvents(eventsData);
          break;
        case 'actions':
          const actionsData = await agenticApi.getActions(200);
          setActions(actionsData);
          break;
        case 'reflections':
          const reflectionsData = await agenticApi.getReflections(200);
          setReflections(reflectionsData);
          break;
        case 'skills':
          const skillsData = await agenticApi.getSkills();
          const statsData = await agenticApi.getSkillStats();
          setSkills(skillsData);
          setSkillStats(statsData);
          break;
        case 'health':
          const healthData = await agenticApi.getHealth();
          setHealth(healthData);
          break;
      }
    } catch (error) {
      console.error('Failed to fetch agentic data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTraceClick = (traceId?: string) => {
    if (traceId && onShowTrace) {
      onShowTrace(traceId);
    }
  };

  const renderEvents = () => (
    <div className="agentic-table-container">
      <div className="agentic-table-header">
        <h3>Event Bus Log</h3>
        <div className="agentic-controls">
          <label>
            <input 
              type="checkbox" 
              checked={autoRefresh} 
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (3s)
          </label>
          <button onClick={fetchData} disabled={loading}>
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>
      <table className="agentic-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Type</th>
            <th>Source</th>
            <th>Trace ID</th>
            <th>Data</th>
          </tr>
        </thead>
        <tbody>
          {events.length === 0 ? (
            <tr>
              <td colSpan={5} className="empty-state">No events yet</td>
            </tr>
          ) : (
            events.slice().reverse().map((event, idx) => (
              <tr key={idx} onClick={() => handleTraceClick(event.trace_id)} className={event.trace_id ? 'clickable' : ''}>
                <td className="timestamp">{new Date(event.timestamp).toLocaleTimeString()}</td>
                <td><span className="badge badge-event">{event.type}</span></td>
                <td>{event.source}</td>
                <td className="trace-id">{event.trace_id || '-'}</td>
                <td className="data-preview">{JSON.stringify(event.data).substring(0, 100)}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );

  const renderActions = () => (
    <div className="agentic-table-container">
      <div className="agentic-table-header">
        <h3>Action Gateway Log</h3>
        <div className="agentic-controls">
          <label>
            <input 
              type="checkbox" 
              checked={autoRefresh} 
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (3s)
          </label>
          <button onClick={fetchData} disabled={loading}>
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>
      <table className="agentic-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Agent</th>
            <th>Action</th>
            <th>Approved</th>
            <th>Tier</th>
            <th>Trace ID</th>
          </tr>
        </thead>
        <tbody>
          {actions.length === 0 ? (
            <tr>
              <td colSpan={6} className="empty-state">No actions yet</td>
            </tr>
          ) : (
            actions.slice().reverse().map((action, idx) => (
              <tr key={idx} onClick={() => handleTraceClick(action.trace_id)} className={action.trace_id ? 'clickable' : ''}>
                <td className="timestamp">{new Date(action.timestamp).toLocaleTimeString()}</td>
                <td>{action.agent}</td>
                <td>{action.action_type}</td>
                <td>
                  <span className={`badge ${action.approved ? 'badge-success' : 'badge-error'}`}>
                    {action.approved ? '✓ Approved' : '✗ Denied'}
                  </span>
                </td>
                <td><span className="badge badge-tier">{action.governance_tier}</span></td>
                <td className="trace-id">{action.trace_id || '-'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );

  const renderReflections = () => (
    <div className="agentic-table-container">
      <div className="agentic-table-header">
        <h3>Reflection Loop Log</h3>
        <div className="agentic-controls">
          <label>
            <input 
              type="checkbox" 
              checked={autoRefresh} 
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (3s)
          </label>
          <button onClick={fetchData} disabled={loading}>
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>
      <table className="agentic-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Agent</th>
            <th>Action</th>
            <th>Outcome</th>
            <th>Trust Δ</th>
            <th>Trace ID</th>
          </tr>
        </thead>
        <tbody>
          {reflections.length === 0 ? (
            <tr>
              <td colSpan={6} className="empty-state">No reflections yet</td>
            </tr>
          ) : (
            reflections.slice().reverse().map((reflection, idx) => (
              <tr key={idx} onClick={() => handleTraceClick(reflection.trace_id)} className={reflection.trace_id ? 'clickable' : ''}>
                <td className="timestamp">{new Date(reflection.timestamp).toLocaleTimeString()}</td>
                <td>{reflection.agent}</td>
                <td>{reflection.action_type}</td>
                <td>
                  <span className={`badge ${reflection.outcome === 'success' ? 'badge-success' : 'badge-error'}`}>
                    {reflection.outcome}
                  </span>
                </td>
                <td className={reflection.trust_delta > 0 ? 'trust-positive' : 'trust-negative'}>
                  {reflection.trust_delta > 0 ? '+' : ''}{reflection.trust_delta.toFixed(2)}
                </td>
                <td className="trace-id">{reflection.trace_id || '-'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );

  const renderSkills = () => (
    <div className="agentic-skills-container">
      <div className="agentic-table-header">
        <h3>Skill Registry</h3>
        <div className="agentic-controls">
          <button onClick={fetchData} disabled={loading}>
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>
      <div className="skills-grid">
        {skills.map((skill) => {
          const stats = skillStats.find(s => s.skill_name === skill.name);
          return (
            <div key={skill.name} className="skill-card">
              <div className="skill-header">
                <h4>{skill.name}</h4>
                <span className="badge badge-category">{skill.category}</span>
              </div>
              <p className="skill-description">{skill.description}</p>
              <div className="skill-meta">
                <div className="skill-meta-item">
                  <span className="label">Governance:</span>
                  <span className="value">{skill.governance_action_type}</span>
                </div>
                <div className="skill-meta-item">
                  <span className="label">Timeout:</span>
                  <span className="value">{skill.timeout_seconds}s</span>
                </div>
                <div className="skill-meta-item">
                  <span className="label">Max Retries:</span>
                  <span className="value">{skill.max_retries}</span>
                </div>
              </div>
              {stats && (
                <div className="skill-stats">
                  <div className="stat">
                    <span className="stat-label">Executions:</span>
                    <span className="stat-value">{stats.total_executions}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Success Rate:</span>
                    <span className="stat-value">{(stats.success_rate * 100).toFixed(1)}%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Avg Time:</span>
                    <span className="stat-value">{stats.average_execution_time_ms.toFixed(0)}ms</span>
                  </div>
                </div>
              )}
              {skill.capability_tags.length > 0 && (
                <div className="skill-tags">
                  {skill.capability_tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderHealth = () => {
    if (!health) return <div>Loading health data...</div>;

    return (
      <div className="agentic-health-container">
        <div className="agentic-table-header">
          <h3>Agentic Organism Health</h3>
          <div className="agentic-controls">
            <span className={`status-badge status-${health.status}`}>{health.status}</span>
            <button onClick={fetchData} disabled={loading}>
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
        </div>
        
        <div className="health-grid">
          <div className="health-card">
            <h4>🔄 Event Bus</h4>
            <div className="health-stats">
              <div className="health-stat">
                <span className="label">Status:</span>
                <span className={`value status-${health.components.event_bus.status}`}>
                  {health.components.event_bus.status}
                </span>
              </div>
              <div className="health-stat">
                <span className="label">Total Events:</span>
                <span className="value">{health.components.event_bus.total_events}</span>
              </div>
              <div className="health-stat">
                <span className="label">Subscribers:</span>
                <span className="value">{health.components.event_bus.subscribers}</span>
              </div>
            </div>
          </div>

          <div className="health-card">
            <h4>🛡️ Action Gateway</h4>
            <div className="health-stats">
              <div className="health-stat">
                <span className="label">Status:</span>
                <span className={`value status-${health.components.action_gateway.status}`}>
                  {health.components.action_gateway.status}
                </span>
              </div>
              <div className="health-stat">
                <span className="label">Total Actions:</span>
                <span className="value">{health.components.action_gateway.total_actions}</span>
              </div>
              <div className="health-stat">
                <span className="label">Governance Rules:</span>
                <span className="value">{health.components.action_gateway.governance_rules}</span>
              </div>
            </div>
          </div>

          <div className="health-card">
            <h4>🧠 Reflection Loop</h4>
            <div className="health-stats">
              <div className="health-stat">
                <span className="label">Status:</span>
                <span className={`value status-${health.components.reflection_loop.status}`}>
                  {health.components.reflection_loop.status}
                </span>
              </div>
              <div className="health-stat">
                <span className="label">Total Reflections:</span>
                <span className="value">{health.components.reflection_loop.total_reflections}</span>
              </div>
              <div className="health-stat">
                <span className="label">Trust Scores:</span>
                <span className="value">{health.components.reflection_loop.trust_scores}</span>
              </div>
            </div>
          </div>

          <div className="health-card">
            <h4>⚡ Skill Registry</h4>
            <div className="health-stats">
              <div className="health-stat">
                <span className="label">Status:</span>
                <span className={`value status-${health.components.skill_registry.status}`}>
                  {health.components.skill_registry.status}
                </span>
              </div>
              <div className="health-stat">
                <span className="label">Total Skills:</span>
                <span className="value">{health.components.skill_registry.total_skills}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="workspace-container agentic-workspace">
      <div className="workspace-header">
        <h2>🤖 Agentic Organism</h2>
        <p>Real-time view of Grace's unified agentic organism</p>
      </div>

      <div className="workspace-tabs">
        <button 
          className={activeTab === 'events' ? 'active' : ''}
          onClick={() => setActiveTab('events')}
        >
          Events
        </button>
        <button 
          className={activeTab === 'actions' ? 'active' : ''}
          onClick={() => setActiveTab('actions')}
        >
          Actions
        </button>
        <button 
          className={activeTab === 'reflections' ? 'active' : ''}
          onClick={() => setActiveTab('reflections')}
        >
          Reflections
        </button>
        <button 
          className={activeTab === 'skills' ? 'active' : ''}
          onClick={() => setActiveTab('skills')}
        >
          Skills
        </button>
        <button 
          className={activeTab === 'health' ? 'active' : ''}
          onClick={() => setActiveTab('health')}
        >
          Health
        </button>
      </div>

      <div className="workspace-content">
        {activeTab === 'events' && renderEvents()}
        {activeTab === 'actions' && renderActions()}
        {activeTab === 'reflections' && renderReflections()}
        {activeTab === 'skills' && renderSkills()}
        {activeTab === 'health' && renderHealth()}
      </div>
    </div>
  );
}
