import { useEffect, useState } from 'react';
import { useAuth } from './AuthProvider';
import './SystemMonitor.css';

interface SystemStatus {
  process: string;
  status: 'running' | 'idle' | 'working';
  lastActivity: string;
  count: number;
}

export function SystemMonitor() {
  const { token } = useAuth();
  const [processes, setProcesses] = useState<SystemStatus[]>([
    { process: 'Reflection Loop', status: 'idle', lastActivity: 'Waiting...', count: 0 },
    { process: 'Learning Engine', status: 'idle', lastActivity: 'Waiting...', count: 0 },
    { process: 'Causal Tracker', status: 'idle', lastActivity: 'Waiting...', count: 0 },
    { process: 'Confidence Evaluator', status: 'idle', lastActivity: 'Ready', count: 0 },
  ]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (!token) return;

    const checkActivity = async () => {
      try {
        const [reflections, tasks, causal] = await Promise.all([
          fetch('http://localhost:8000/api/reflections/').then(r => r.json()).catch(() => []),
          fetch('http://localhost:8000/api/tasks/', {
            headers: { Authorization: `Bearer ${token}` }
          }).then(r => r.json()).catch(() => []),
          fetch('http://localhost:8000/api/causal/patterns', {
            headers: { Authorization: `Bearer ${token}` }
          }).then(r => r.json()).catch(() => ({ total_interactions: 0 }))
        ]);

        setProcesses([
          {
            process: 'Reflection Loop',
            status: Array.isArray(reflections) && reflections.length > 0 ? 'running' : 'idle',
            lastActivity: Array.isArray(reflections) && reflections[0] 
              ? `Last: ${new Date(reflections[0].generated_at).toLocaleTimeString()}`
              : 'No reflections yet',
            count: Array.isArray(reflections) ? reflections.length : 0
          },
          {
            process: 'Learning Engine',
            status: Array.isArray(tasks) && tasks.filter((t: any) => t.auto_generated).length > 0 ? 'working' : 'idle',
            lastActivity: `${tasks.filter((t: any) => t.auto_generated).length} auto-tasks created`,
            count: Array.isArray(tasks) ? tasks.filter((t: any) => t.auto_generated).length : 0
          },
          {
            process: 'Causal Tracker',
            status: causal.total_interactions > 0 ? 'running' : 'idle',
            lastActivity: `${causal.total_interactions} events logged`,
            count: causal.total_interactions || 0
          },
          {
            process: 'Confidence Evaluator',
            status: 'idle',
            lastActivity: 'Ready to evaluate',
            count: 0
          }
        ]);
      } catch (error) {
        console.error('System monitor error:', error);
      }
    };

    checkActivity();
    const interval = setInterval(checkActivity, 5000);
    return () => clearInterval(interval);
  }, [token]);

  if (!token) return null;

  return (
    <div className={`system-monitor ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="monitor-header" onClick={() => setIsExpanded(!isExpanded)}>
        <span className="monitor-title">🔧 System Status</span>
        <span className="monitor-toggle">{isExpanded ? '▼' : '▶'}</span>
      </div>
      
      {isExpanded && (
        <div className="monitor-body">
          {processes.map((proc) => (
            <div key={proc.process} className="process-item">
              <div className="process-header">
                <span className="process-name">{proc.process}</span>
                <span className={`process-status status-${proc.status}`}>
                  {proc.status === 'running' && '🟢'}
                  {proc.status === 'working' && '🟡'}
                  {proc.status === 'idle' && '⚪'}
                  {proc.status}
                </span>
              </div>
              <div className="process-details">
                <span className="process-activity">{proc.lastActivity}</span>
                {proc.count > 0 && <span className="process-count">Count: {proc.count}</span>}
              </div>
            </div>
          ))}
          
          <div className="monitor-footer">
            <small>Updates every 5 seconds</small>
          </div>
        </div>
      )}
    </div>
  );
}
