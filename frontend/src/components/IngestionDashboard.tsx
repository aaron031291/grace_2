import { useState, useEffect } from 'react';
import { Download, Play, Square, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import {
  getIngestionStatus,
  getIngestionTasks,
  startIngestion,
  stopIngestion,
  type IngestionStatus,
  type IngestionTask
} from '../services/ingestionApi';

const s = {
  bg: '#0a0a0a',
  bg2: '#1a1a1a',
  fg: '#e0e0e0',
  ac: '#8b5cf6',
  ac2: '#a78bfa'
};

export function IngestionDashboard() {
  const [status, setStatus] = useState<IngestionStatus | null>(null);
  const [tasks, setTasks] = useState<IngestionTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // New task form
  const [newTaskType, setNewTaskType] = useState('github');
  const [newSource, setNewSource] = useState('');

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 2000); // Fast refresh for progress
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [statusData, tasksData] = await Promise.all([
        getIngestionStatus(),
        getIngestionTasks()
      ]);
      setStatus(statusData);
      setTasks(tasksData);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleStartIngestion(e: React.FormEvent) {
    e.preventDefault();
    if (!newSource) return;
    
    try {
      await startIngestion(newTaskType, newSource);
      setNewSource('');
      await loadData();
    } catch (err: any) {
      alert('Failed to start ingestion: ' + err.message);
    }
  }

  async function handleStopTask(taskId: string) {
    try {
      await stopIngestion(taskId);
      await loadData();
    } catch (err: any) {
      alert('Failed to stop task: ' + err.message);
    }
  }

  const getStatusColor = (taskStatus: string) => {
    switch (taskStatus) {
      case 'completed': return '#10b981';
      case 'running': return '#3b82f6';
      case 'failed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: s.fg }}>
        <div style={{ fontSize: '1.5rem' }}>Loading ingestion data...</div>
      </div>
    );
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', padding: '2rem', color: s.fg }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ color: s.ac2, marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Download size={32} />
          Knowledge Ingestion
        </h1>

        {error && (
          <div style={{ background: '#991b1b', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={20} />
            Error: {error}
          </div>
        )}

        {/* Status Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Total Tasks</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: s.ac2 }}>{status?.total_tasks || 0}</div>
          </div>
          
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Active</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#3b82f6' }}>{status?.active_tasks || 0}</div>
          </div>
          
          <div style={{ background: s.bg2, padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.875rem', color: '#888', marginBottom: '0.5rem' }}>Max Concurrent</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: s.ac }}>{status?.max_concurrent || 0}</div>
          </div>
        </div>

        {/* New Task Form */}
        <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px', marginBottom: '2rem' }}>
          <h2 style={{ color: s.ac, marginBottom: '1.5rem' }}>Start New Ingestion</h2>
          <form onSubmit={handleStartIngestion} style={{ display: 'flex', gap: '1rem', alignItems: 'end' }}>
            <div style={{ flex: '0 0 200px' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: '#888' }}>
                Task Type
              </label>
              <select
                value={newTaskType}
                onChange={(e) => setNewTaskType(e.target.value)}
                style={{ width: '100%', background: s.bg, color: s.fg, border: '1px solid #333', padding: '0.75rem', borderRadius: '6px' }}
              >
                <option value="github">GitHub</option>
                <option value="reddit">Reddit</option>
                <option value="youtube">YouTube</option>
                <option value="web">Web Scraping</option>
              </select>
            </div>
            
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: '#888' }}>
                Source URL
              </label>
              <input
                type="text"
                value={newSource}
                onChange={(e) => setNewSource(e.target.value)}
                placeholder="https://github.com/user/repo"
                style={{ width: '100%', background: s.bg, color: s.fg, border: '1px solid #333', padding: '0.75rem', borderRadius: '6px' }}
              />
            </div>
            
            <button
              type="submit"
              style={{ background: s.ac, color: '#fff', border: 'none', padding: '0.75rem 2rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 'bold' }}
            >
              <Play size={16} />
              Start
            </button>
          </form>
        </div>

        {/* Active Tasks */}
        {tasks.length > 0 && (
          <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px' }}>
            <h2 style={{ color: s.ac, marginBottom: '1.5rem' }}>Ingestion Tasks</h2>
            <div style={{ space: '1rem' }}>
              {tasks.map((task) => (
                <div
                  key={task.task_id}
                  style={{ background: s.bg, padding: '1.5rem', borderRadius: '8px', marginBottom: '1rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '1.125rem', fontWeight: 'bold' }}>{task.task_type}</span>
                        <span
                          style={{
                            padding: '0.25rem 0.75rem',
                            borderRadius: '12px',
                            fontSize: '0.75rem',
                            fontWeight: 'bold',
                            background: getStatusColor(task.status),
                            color: '#fff'
                          }}
                        >
                          {task.status}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#888' }}>{task.source}</div>
                      {task.started_at && (
                        <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                          <Clock size={12} style={{ display: 'inline', marginRight: '0.25rem' }} />
                          Started: {new Date(task.started_at).toLocaleString()}
                        </div>
                      )}
                    </div>
                    
                    {task.status === 'running' && (
                      <button
                        onClick={() => handleStopTask(task.task_id)}
                        style={{ background: '#ef4444', color: '#fff', border: 'none', padding: '0.5rem 1rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                      >
                        <Square size={14} />
                        Stop
                      </button>
                    )}
                  </div>
                  
                  {/* Progress Bar */}
                  <div style={{ marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#888', marginBottom: '0.25rem' }}>
                      <span>Progress</span>
                      <span>{Math.round(task.progress)}%</span>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: '#333', borderRadius: '4px', overflow: 'hidden' }}>
                      <div
                        style={{
                          width: `${task.progress}%`,
                          height: '100%',
                          background: `linear-gradient(90deg, ${s.ac} 0%, ${s.ac2} 100%)`,
                          transition: 'width 0.3s ease'
                        }}
                      ></div>
                    </div>
                  </div>
                  
                  {task.error && (
                    <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', padding: '0.75rem', borderRadius: '6px', fontSize: '0.875rem', color: '#fca5a5' }}>
                      Error: {task.error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Modules Status */}
        {status && status.modules_loaded && status.modules_loaded.length > 0 && (
          <div style={{ background: s.bg2, padding: '2rem', borderRadius: '12px', marginTop: '2rem' }}>
            <h2 style={{ color: s.ac, marginBottom: '1.5rem' }}>Available Modules</h2>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {status.modules_loaded.map((module) => (
                <div
                  key={module}
                  style={{ background: s.bg, padding: '0.75rem 1.5rem', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  <CheckCircle size={16} style={{ color: '#10b981' }} />
                  {module}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
