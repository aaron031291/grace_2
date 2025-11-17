/**
 * Learning Loop View
 * Shows recent builds, artifacts, and learning outcomes
 */

import { useState, useEffect } from 'react';
import './LearningLoopView.css';

interface LearningOutcome {
  id: string;
  type: 'build' | 'artifact' | 'mission' | 'knowledge';
  title: string;
  description: string;
  created_at: string;
  status: 'success' | 'in_progress' | 'failed';
  metadata?: any;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8017';

export default function LearningLoopView() {
  const [outcomes, setOutcomes] = useState<LearningOutcome[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);

  const loadLearningData = async () => {
    setLoading(true);
    try {
      const [outcomesRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/learning/outcomes`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
          },
        }),
        fetch(`${API_BASE}/api/learning/status`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || 'dev-token'}`,
          },
        }),
      ]);

      if (outcomesRes.ok) {
        const data = await outcomesRes.json();
        setOutcomes(data.outcomes || []);
      }

      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to load learning data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLearningData();
    const interval = setInterval(loadLearningData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'build': return '🔨';
      case 'artifact': return '📦';
      case 'mission': return '🎯';
      case 'knowledge': return '📚';
      default: return '📄';
    }
  };

  return (
    <div className="learning-loop-view">
      <div className="learning-header">
        {stats && (
          <div className="learning-stats">
            <div className="stat">
              <strong>{stats.total_artifacts || 0}</strong> Artifacts
            </div>
            <div className="stat">
              <strong>{stats.total_missions || 0}</strong> Missions
            </div>
            <div className="stat">
              <strong>{stats.knowledge_bases || 0}</strong> Knowledge Bases
            </div>
          </div>
        )}

        <button onClick={loadLearningData} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="outcomes-list">
        {outcomes.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔄</div>
            <div className="empty-message">No learning outcomes yet</div>
            <div className="empty-hint">
              Builds and artifacts will appear here as Grace learns
            </div>
          </div>
        ) : (
          outcomes.map(outcome => (
            <div key={outcome.id} className="outcome-card">
              <div className="outcome-header">
                <div className="outcome-type">
                  {getTypeIcon(outcome.type)} {outcome.type}
                </div>
                <div className={`outcome-status status-${outcome.status}`}>
                  {outcome.status}
                </div>
              </div>

              <h4 className="outcome-title">{outcome.title}</h4>
              <p className="outcome-description">{outcome.description}</p>

              <div className="outcome-time">
                {new Date(outcome.created_at).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
