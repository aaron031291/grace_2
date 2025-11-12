import React, { useState, useEffect } from 'react';

interface AnalyticsData {
  activeUsers: number;
  totalWorkflows: number;
  approvedWorkflows: number;
  pendingWorkflows: number;
  automationRules: number;
  notificationsSent: number;
  collaborationScore: number;
  trendsData: Array<{ date: string; value: number }>;
}

interface CollaborationAnalyticsProps {
  token: string;
}

export const CollaborationAnalytics: React.FC<CollaborationAnalyticsProps> = ({ token }) => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    activeUsers: 12,
    totalWorkflows: 45,
    approvedWorkflows: 38,
    pendingWorkflows: 7,
    automationRules: 15,
    notificationsSent: 234,
    collaborationScore: 87,
    trendsData: [
      { date: 'Mon', value: 65 },
      { date: 'Tue', value: 72 },
      { date: 'Wed', value: 68 },
      { date: 'Thu', value: 85 },
      { date: 'Fri', value: 92 },
      { date: 'Sat', value: 78 },
      { date: 'Sun', value: 88 }
    ]
  });

  const maxTrendValue = Math.max(...analyticsData.trendsData.map(d => d.value));

  return (
    <div className="collaboration-analytics">
      <h3 className="section-title">Collaboration Analytics</h3>

      <div className="analytics-grid">
        <div className="analytics-card highlight">
          <div className="card-header">
            <span className="card-icon">🎯</span>
            <span className="card-title">Collaboration Score</span>
          </div>
          <div className="score-display">
            <div className="score-value">{analyticsData.collaborationScore}</div>
            <div className="score-max">/100</div>
          </div>
          <div className="score-bar">
            <div
              className="score-fill"
              style={{ width: `${analyticsData.collaborationScore}%` }}
            />
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-header">
            <span className="card-icon">👥</span>
            <span className="card-title">Active Users</span>
          </div>
          <div className="metric-value">{analyticsData.activeUsers}</div>
          <div className="metric-trend positive">+15% this week</div>
        </div>

        <div className="analytics-card">
          <div className="card-header">
            <span className="card-icon">📋</span>
            <span className="card-title">Total Workflows</span>
          </div>
          <div className="metric-value">{analyticsData.totalWorkflows}</div>
          <div className="metric-breakdown">
            <span className="breakdown-item">
              ✓ {analyticsData.approvedWorkflows} approved
            </span>
            <span className="breakdown-item">
              ⏳ {analyticsData.pendingWorkflows} pending
            </span>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-header">
            <span className="card-icon">🤖</span>
            <span className="card-title">Automation Rules</span>
          </div>
          <div className="metric-value">{analyticsData.automationRules}</div>
          <div className="metric-trend positive">+3 new</div>
        </div>

        <div className="analytics-card">
          <div className="card-header">
            <span className="card-icon">🔔</span>
            <span className="card-title">Notifications Sent</span>
          </div>
          <div className="metric-value">{analyticsData.notificationsSent}</div>
          <div className="metric-trend neutral">This month</div>
        </div>
      </div>

      <div className="chart-section">
        <h4 className="chart-title">Collaboration Activity Trend</h4>
        <div className="bar-chart">
          {analyticsData.trendsData.map((dataPoint, idx) => {
            const heightPercent = (dataPoint.value / maxTrendValue) * 100;
            return (
              <div key={idx} className="bar-container">
                <div className="bar-value">{dataPoint.value}</div>
                <div
                  className="bar"
                  style={{ height: `${heightPercent}%` }}
                  title={`${dataPoint.date}: ${dataPoint.value}`}
                />
                <div className="bar-label">{dataPoint.date}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="insights-section">
        <h4 className="insights-title">💡 Key Insights</h4>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">📈</div>
            <div className="insight-content">
              <div className="insight-title">Peak Collaboration</div>
              <div className="insight-text">
                Friday shows highest activity with 92 interactions
              </div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">⚡</div>
            <div className="insight-content">
              <div className="insight-title">Fast Approvals</div>
              <div className="insight-text">
                Average workflow approval time: 2.3 hours
              </div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">🎯</div>
            <div className="insight-content">
              <div className="insight-title">High Engagement</div>
              <div className="insight-text">
                84% of workflows approved on first review
              </div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">🤝</div>
            <div className="insight-content">
              <div className="insight-title">Team Collaboration</div>
              <div className="insight-text">
                Average 3.2 reviewers per workflow
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
