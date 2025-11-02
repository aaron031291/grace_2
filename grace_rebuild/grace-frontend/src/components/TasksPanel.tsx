import { useEffect, useState } from 'react';
import { useAuth } from './AuthProvider';

interface Task {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  auto_generated: boolean;
  created_at: string;
}

export function TasksPanel() {
  const { token } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    
    const fetchTasks = () => {
      fetch("http://localhost:8000/api/tasks/", {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then((res) => res.json())
        .then(setTasks)
        .catch(console.error)
        .finally(() => setLoading(false));
    };

    fetchTasks();
    const interval = setInterval(fetchTasks, 10000);
    return () => clearInterval(interval);
  }, [token]);

  if (!token) return null;
  if (loading) return <div style={{ padding: '1rem', color: '#888' }}>Loading tasks...</div>;

  return (
    <div style={{ padding: '1rem', background: '#1a1a2e', borderRadius: '8px', border: '1px solid #333' }}>
      <h3 style={{ margin: '0 0 1rem 0', color: '#00d4ff', fontSize: '1rem' }}>
        Tasks ({tasks.filter(t => t.auto_generated).length} auto)
      </h3>
      
      {tasks.length === 0 && (
        <p style={{ color: '#888', fontSize: '0.875rem' }}>
          No tasks yet. Chat about topics repeatedly and Grace will create them!
        </p>
      )}
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {tasks.slice(0, 5).map((task) => (
          <div 
            key={task.id} 
            style={{ 
              background: task.auto_generated 
                ? 'rgba(123, 44, 191, 0.1)' 
                : 'rgba(255, 255, 255, 0.03)',
              border: task.auto_generated 
                ? '1px solid rgba(123, 44, 191, 0.3)' 
                : '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '6px',
              padding: '0.75rem'
            }}
          >
            <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem', color: '#e0e0e0' }}>
              {task.auto_generated && '🤖 '}
              {task.title}
            </div>
            {task.description && (
              <div style={{ fontSize: '0.75rem', color: '#a0a0a0', marginBottom: '0.5rem' }}>
                {task.description}
              </div>
            )}
            <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.7rem' }}>
              <span style={{ 
                padding: '2px 6px', 
                borderRadius: '4px', 
                background: task.status === 'pending' ? 'rgba(255,200,0,0.2)' : 'rgba(0,255,136,0.2)',
                color: task.status === 'pending' ? '#ffcc00' : '#00ff88'
              }}>
                {task.status}
              </span>
              <span style={{ color: '#666' }}>
                {new Date(task.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
