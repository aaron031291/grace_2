import React from 'react';

interface PresencePanelProps {
  token: string;
  presenceData: any;
}

export const PresencePanel: React.FC<PresencePanelProps> = ({ token, presenceData }) => {
  if (!presenceData) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading presence data...</p>
      </div>
    );
  }

  const { active_users = [], files_being_viewed, files_being_edited, rows_being_edited } = presenceData;

  return (
    <div className="presence-panel">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{active_users.length}</div>
            <div className="stat-label">Active Users</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📄</div>
          <div className="stat-content">
            <div className="stat-value">{files_being_viewed}</div>
            <div className="stat-label">Files Viewed</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✏️</div>
          <div className="stat-content">
            <div className="stat-value">{files_being_edited}</div>
            <div className="stat-label">Files Editing</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{rows_being_edited}</div>
            <div className="stat-label">Rows Editing</div>
          </div>
        </div>
      </div>

      <div className="users-list">
        <h3 className="section-title">Active Users</h3>
        {active_users.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">😴</span>
            <p>No users currently active</p>
          </div>
        ) : (
          <div className="users-grid">
            {active_users.map((user: any, idx: number) => (
              <div key={idx} className="user-card">
                <div className="user-avatar">
                  {user.user_name.charAt(0).toUpperCase()}
                </div>
                <div className="user-info">
                  <div className="user-name">{user.user_name}</div>
                  {user.current_view && (
                    <div className="user-activity">
                      <span className="activity-icon">
                        {user.current_view === 'file' ? '📄' : '📊'}
                      </span>
                      <span className="activity-text">
                        {user.current_file || user.current_table || 'Browsing'}
                      </span>
                    </div>
                  )}
                  <div className="user-last-seen">
                    Last seen: {new Date(user.last_seen).toLocaleTimeString()}
                  </div>
                </div>
                <div className="user-status online"></div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
