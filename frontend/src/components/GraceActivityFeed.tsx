/**
 * Grace Activity Feed
 * Real-time stream of Grace's autonomous actions
 */

import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import { 
  FileText, FolderPlus, Save, Trash2, Move, 
  Brain, Zap, CheckCircle, AlertCircle, Clock
} from 'lucide-react';

interface GraceAction {
  action: string;
  category?: string;
  subcategory?: string;
  file: string;
  timestamp: string;
  size?: number;
  auto_sync?: boolean;
  reason?: string;
}

export function GraceActivityFeed() {
  const [actions, setActions] = useState<GraceAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadActions();
    const interval = setInterval(loadActions, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  async function loadActions() {
    try {
      const response = await fetch(apiUrl('/api/grace/memory/actions?limit=100');
      const data = await response.json();
      setActions(data.actions || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load Grace actions:', err);
      setLoading(false);
    }
  }

  function getActionIcon(action: string) {
    switch (action) {
      case 'create_file': return <FileText size={16} color="#10b981" />;
      case 'update_file': return <Save size={16} color="#3b82f6" />;
      case 'delete_file': return <Trash2 size={16} color="#ef4444" />;
      case 'organize_file': return <Move size={16} color="#8b5cf6" />;
      case 'save_research': return <Brain size={16} color="#a78bfa" />;
      case 'save_insight': return <Zap size={16} color="#f59e0b" />;
      default: return <CheckCircle size={16} color="#6b7280" />;
    }
  }

  function getActionLabel(action: string): string {
    const labels: Record<string, string> = {
      'create_file': 'Created',
      'update_file': 'Updated',
      'delete_file': 'Deleted',
      'organize_file': 'Organized',
      'save_research': 'Saved Research',
      'save_insight': 'Saved Insight',
      'save_conversation': 'Saved Conversation'
    };
    return labels[action] || action;
  }

  function formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  }

  const filteredActions = filter === 'all' 
    ? actions 
    : actions.filter(a => a.action === filter);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: 'rgba(10,12,23,0.6)',
      borderRadius: '12px',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.1))'
      }}>
        <h3 style={{
          margin: '0 0 8px 0',
          fontSize: '1.1rem',
          color: '#a78bfa',
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Brain size={20} />
          Grace's Activity
        </h3>
        <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
          {actions.length} actions • Last 5 minutes auto-refresh
        </div>
      </div>

      {/* Filters */}
      <div style={{
        padding: '12px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        gap: '6px',
        flexWrap: 'wrap'
      }}>
        {['all', 'create_file', 'save_research', 'save_insight', 'organize_file'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '4px 12px',
              borderRadius: '6px',
              border: 'none',
              fontSize: '0.75rem',
              fontWeight: 500,
              cursor: 'pointer',
              background: filter === f ? 'rgba(139, 92, 246, 0.3)' : 'rgba(255,255,255,0.05)',
              color: filter === f ? '#a78bfa' : '#9ca3af',
              transition: 'all 0.2s'
            }}
          >
            {f === 'all' ? 'All' : f.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Activity List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '8px'
      }}>
        {loading ? (
          <div style={{
            padding: '40px',
            textAlign: 'center',
            color: '#6b7280'
          }}>
            <Clock size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
            <div>Loading Grace's activity...</div>
          </div>
        ) : filteredActions.length === 0 ? (
          <div style={{
            padding: '40px',
            textAlign: 'center',
            color: '#6b7280'
          }}>
            <Brain size={32} style={{ marginBottom: '12px', opacity: 0.3 }} />
            <div>No actions yet</div>
            <div style={{ fontSize: '0.875rem', marginTop: '8px' }}>
              Grace's autonomous actions will appear here
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredActions.map((action, idx) => (
              <ActivityCard key={idx} action={action} getIcon={getActionIcon} getLabel={getActionLabel} formatTime={formatTime} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ActivityCard({ 
  action, 
  getIcon, 
  getLabel, 
  formatTime 
}: { 
  action: GraceAction;
  getIcon: (action: string) => React.ReactNode;
  getLabel: (action: string) => string;
  formatTime: (timestamp: string) => string;
}) {
  return (
    <div style={{
      background: 'rgba(30, 30, 30, 0.6)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '8px',
      padding: '12px',
      transition: 'all 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)'}
    onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(30, 30, 30, 0.6)'}
    >
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '10px'
      }}>
        {/* Icon */}
        <div style={{
          padding: '6px',
          background: 'rgba(139, 92, 246, 0.1)',
          borderRadius: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {getIcon(action.action)}
        </div>

        {/* Content */}
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: '#e5e7ff',
            marginBottom: '4px'
          }}>
            {getLabel(action.action)}
          </div>
          
          <div style={{
            fontSize: '0.8rem',
            color: '#9ca3af',
            marginBottom: '6px',
            fontFamily: 'monospace'
          }}>
            {action.file}
          </div>

          {action.category && (
            <div style={{
              display: 'flex',
              gap: '6px',
              fontSize: '0.7rem',
              marginBottom: '6px'
            }}>
              <span style={{
                background: 'rgba(139, 92, 246, 0.2)',
                padding: '2px 6px',
                borderRadius: '4px',
                color: '#a78bfa'
              }}>
                {action.category}
              </span>
              {action.subcategory && (
                <span style={{
                  background: 'rgba(59, 130, 246, 0.2)',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  color: '#60a5fa'
                }}>
                  {action.subcategory}
                </span>
              )}
            </div>
          )}

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '0.7rem',
            color: '#6b7280'
          }}>
            <span>{formatTime(action.timestamp)}</span>
            {action.size && (
              <span>{(action.size / 1024).toFixed(1)} KB</span>
            )}
            {action.auto_sync && (
              <span style={{ color: '#10b981' }}>✓ Synced</span>
            )}
          </div>

          {action.reason && (
            <div style={{
              marginTop: '6px',
              padding: '6px 8px',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '4px',
              fontSize: '0.7rem',
              color: '#9ca3af',
              fontStyle: 'italic'
            }}>
              "{action.reason}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
