import { useEffect, useState } from 'react';
import { useAuth } from './AuthProvider';
import './Dashboard.css';

interface Metrics {
  total_messages: number;
  active_users: number;
  registered_users: number;
}

interface CausalPatterns {
  total_interactions: number;
  event_types: Record<string, number>;
  outcomes: Record<string, number>;
  unhandled_rate: number;
  most_common_event: string;
}

interface Task {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  auto_generated: boolean;
  created_at: string;
}

export function Dashboard() {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [patterns, setPatterns] = useState<CausalPatterns | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    const fetchData = async () => {
      try {
        const [metricsRes, patternsRes, tasksRes] = await Promise.all([
          fetch('http://localhost:8000/api/metrics/summary'),
          fetch('http://localhost:8000/api/causal/patterns', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          fetch('http://localhost:8000/api/tasks/', {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        const [metricsData, patternsData, tasksData] = await Promise.all([
          metricsRes.json(),
          patternsRes.json(),
          tasksRes.json()
        ]);

        setMetrics(metricsData);
        setPatterns(patternsData);
        setTasks(tasksData);
      } catch (error) {
        console.error('Dashboard fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [token]);

  if (!token) return null;
  if (loading) return <div className="dashboard-loading">Loading dashboard...</div>;

  return (
    <div className="dashboard">
      <div style={{ marginBottom: '1rem' }}>
        <a href="/" style={{ color: '#7b2cbf', textDecoration: 'none', fontSize: '0.875rem' }}>← Back to Chat</a>
      </div>
      <h2>Grace Analytics Dashboard</h2>
      
      <div className="dashboard-grid">
        <div className="metric-card">
          <h3>Messages</h3>
          <div className="metric-value">{metrics?.total_messages || 0}</div>
          <div className="metric-label">Total Conversations</div>
        </div>

        <div className="metric-card">
          <h3>Active Users</h3>
          <div className="metric-value">{metrics?.active_users || 0}</div>
          <div className="metric-label">Chatting with Grace</div>
        </div>

        <div className="metric-card">
          <h3>Interactions</h3>
          <div className="metric-value">{patterns?.total_interactions || 0}</div>
          <div className="metric-label">Logged Events</div>
        </div>

        <div className="metric-card">
          <h3>Unhandled Rate</h3>
          <div className="metric-value">{patterns?.unhandled_rate || 0}%</div>
          <div className="metric-label">Learning Opportunities</div>
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Causal Event Types</h3>
        <div className="causal-grid">
          {patterns?.event_types && Object.entries(patterns.event_types).map(([type, count]) => (
            <div key={type} className="causal-item">
              <span className="causal-type">{type}</span>
              <span className="causal-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Response Outcomes</h3>
        <div className="outcome-grid">
          {patterns?.outcomes && Object.entries(patterns.outcomes).map(([outcome, count]) => (
            <div key={outcome} className="outcome-item">
              <span className="outcome-name">{outcome}</span>
              <div className="outcome-bar" style={{
                width: `${(count / (patterns?.total_interactions || 1)) * 100}%`
              }}></div>
              <span className="outcome-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Autonomous Tasks ({tasks.filter(t => t.auto_generated).length} auto-generated)</h3>
        <div className="tasks-list">
          {tasks.length === 0 && <p className="empty-state">No tasks yet. Chat more and Grace will create them!</p>}
          {tasks.slice(0, 10).map((task) => (
            <div key={task.id} className={`task-item ${task.auto_generated ? 'auto' : 'manual'}`}>
              <div className="task-header">
                <span className="task-title">{task.title}</span>
                <span className={`task-status status-${task.status}`}>{task.status}</span>
              </div>
              {task.description && <div className="task-description">{task.description}</div>}
              <div className="task-meta">
                {task.auto_generated && <span className="auto-badge">🤖 Auto-generated</span>}
                <span className="task-priority">Priority: {task.priority}</span>
                <span className="task-date">{new Date(task.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
