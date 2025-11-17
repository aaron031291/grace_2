import { useState } from 'react';
import './InlineActionCard.css';

export type ActionCardType = 
  | 'approval_request'
  | 'mission_proposal'
  | 'learning_job'
  | 'file_upload'
  | 'code_change'
  | 'knowledge_update';

interface ActionCardProps {
  type: ActionCardType;
  data: any;
  onAction: (action: string, data?: any) => void;
}

export function InlineActionCard({ type, data, onAction }: ActionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (type === 'approval_request') {
    return (
      <div className="action-card approval-card">
        <div className="card-header">
          <span className="card-icon">🔧</span>
          <h3 className="card-title">Self-Healing Action Required</h3>
          <span className={`risk-badge risk-${data.risk_level || 'medium'}`}>
            {data.risk_level || 'Medium'} Risk (Tier {data.tier || 2})
          </span>
        </div>

        <div className="card-body">
          <div className="card-field">
            <label>Playbook:</label>
            <span>{data.playbook_name || 'Unknown'}</span>
          </div>

          <div className="card-field">
            <label>Reason:</label>
            <span>{data.reason || 'No reason provided'}</span>
          </div>

          {data.expected_effects && data.expected_effects.length > 0 && (
            <div className="card-section">
              <h4>Expected Effects:</h4>
              <ul className="effects-list">
                {data.expected_effects.map((effect: string, idx: number) => (
                  <li key={idx}>{effect}</li>
                ))}
              </ul>
            </div>
          )}

          {data.rollback_plan && data.rollback_plan.length > 0 && (
            <div className="card-section">
              <h4>Rollback Plan:</h4>
              <ul className="effects-list">
                {data.rollback_plan.map((step: string, idx: number) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
            </div>
          )}

          {data.kpis && data.kpis.length > 0 && (
            <div className="card-section">
              <h4>KPIs to Improve:</h4>
              <ul className="kpi-list">
                {data.kpis.map((kpi: any, idx: number) => (
                  <li key={idx}>
                    {kpi.name}: {kpi.current} → {kpi.target}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="card-actions">
          <button 
            className="action-btn approve-btn"
            onClick={() => onAction('approve', data)}
          >
            Approve
          </button>
          <button 
            className="action-btn simulate-btn"
            onClick={() => onAction('simulate', data)}
          >
            Simulate
          </button>
          <button 
            className="action-btn reject-btn"
            onClick={() => onAction('reject', data)}
          >
            Reject
          </button>
          <button 
            className="action-btn details-btn"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Hide' : 'View'} Details
          </button>
        </div>

        {isExpanded && (
          <div className="card-details">
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        )}
      </div>
    );
  }

  if (type === 'mission_proposal') {
    return (
      <div className="action-card mission-card">
        <div className="card-header">
          <span className="card-icon">🎯</span>
          <h3 className="card-title">Mission Proposal</h3>
          <span className="trust-badge">
            Trust: {data.trust_score || 0}%
          </span>
        </div>

        <div className="card-body">
          <div className="card-field">
            <label>Goal:</label>
            <span>{data.goal || 'No goal specified'}</span>
          </div>

          <div className="card-field">
            <label>Estimated Duration:</label>
            <span>{data.estimated_duration || 'Unknown'}</span>
          </div>

          {data.steps && data.steps.length > 0 && (
            <div className="card-section">
              <h4>Steps ({data.steps.length}):</h4>
              <ol className="steps-list">
                {data.steps.map((step: string, idx: number) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>

        <div className="card-actions">
          <button 
            className="action-btn approve-btn"
            onClick={() => onAction('start_mission', data)}
          >
            Start Mission
          </button>
          <button 
            className="action-btn details-btn"
            onClick={() => onAction('view_plan', data)}
          >
            View Plan
          </button>
          <button 
            className="action-btn reject-btn"
            onClick={() => onAction('decline', data)}
          >
            Decline
          </button>
        </div>
      </div>
    );
  }

  if (type === 'learning_job') {
    return (
      <div className="action-card learning-card">
        <div className="card-header">
          <span className="card-icon">🧠</span>
          <h3 className="card-title">Learning Job</h3>
        </div>

        <div className="card-body">
          <div className="card-field">
            <label>Domain:</label>
            <span>{data.domain || 'Unknown'}</span>
          </div>

          <div className="card-field">
            <label>Source:</label>
            <span>{data.source || 'Unknown'}</span>
          </div>

          <div className="card-field">
            <label>Estimated Time:</label>
            <span>{data.estimated_time || 'Unknown'}</span>
          </div>
        </div>

        <div className="card-actions">
          <button 
            className="action-btn approve-btn"
            onClick={() => onAction('start_learning', data)}
          >
            Start Learning
          </button>
          <button 
            className="action-btn secondary-btn"
            onClick={() => onAction('add_to_queue', data)}
          >
            Add to Queue
          </button>
          <button 
            className="action-btn reject-btn"
            onClick={() => onAction('skip', data)}
          >
            Skip
          </button>
        </div>
      </div>
    );
  }

  if (type === 'code_change') {
    return (
      <div className="action-card code-card">
        <div className="card-header">
          <span className="card-icon">💻</span>
          <h3 className="card-title">Code Change Proposal</h3>
        </div>

        <div className="card-body">
          <div className="card-field">
            <label>File:</label>
            <span className="code-path">{data.file_path || 'Unknown'}</span>
          </div>

          <div className="card-field">
            <label>Changes:</label>
            <span>{data.changes_summary || 'No summary'}</span>
          </div>

          {data.diff && (
            <div className="card-section">
              <h4>Diff Preview:</h4>
              <pre className="code-diff">{data.diff}</pre>
            </div>
          )}
        </div>

        <div className="card-actions">
          <button 
            className="action-btn approve-btn"
            onClick={() => onAction('apply', data)}
          >
            Apply
          </button>
          <button 
            className="action-btn details-btn"
            onClick={() => onAction('view_diff', data)}
          >
            View Full Diff
          </button>
          <button 
            className="action-btn reject-btn"
            onClick={() => onAction('reject', data)}
          >
            Reject
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="action-card generic-card">
      <div className="card-header">
        <span className="card-icon">📋</span>
        <h3 className="card-title">Action Required</h3>
      </div>
      <div className="card-body">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  );
}
