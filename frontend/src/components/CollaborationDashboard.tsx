import React, { useState, useEffect } from 'react';
import './CollaborationDashboard.css';
import { GraceCopilotSidebar } from './GraceCopilotSidebar';
import { PresencePanel } from './PresencePanel';
import { NotificationCenter } from './NotificationCenter';
import { WorkflowManager } from './WorkflowManager';
import { AutomationRulesPanel } from './AutomationRulesPanel';
import { CollaborationAnalytics } from './CollaborationAnalytics';

interface CollaborationDashboardProps {
  token: string;
  userId: string;
}

type ActiveView = 'presence' | 'workflows' | 'notifications' | 'automation' | 'analytics';

export const CollaborationDashboard: React.FC<CollaborationDashboardProps> = ({ token, userId }) => {
  const [activeView, setActiveView] = useState<ActiveView>('presence');
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [presenceData, setPresenceData] = useState<any>(null);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    connectWebSocket();
    fetchUnreadCount();

    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const connectWebSocket = () => {
    const websocket = new WebSocket(`ws://localhost:8000/api/collaboration/ws?token=${token}`);

    websocket.onopen = () => {
      setConnected(true);
      console.log('Connected to collaboration WebSocket');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    websocket.onerror = () => {
      setConnected(false);
    };

    websocket.onclose = () => {
      setConnected(false);
      setTimeout(connectWebSocket, 5000);
    };

    setWs(websocket);
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'user_joined':
      case 'user_left':
        fetchPresenceData();
        break;
      case 'notification':
        setUnreadCount(prev => prev + 1);
        break;
      case 'workflow_update':
        break;
    }
  };

  const fetchPresenceData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/collaboration/presence/all', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setPresenceData(data);
    } catch (error) {
      console.error('Failed to fetch presence:', error);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/collaboration/notifications/unread-count', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUnreadCount(data.count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  };

  useEffect(() => {
    if (activeView === 'presence') {
      fetchPresenceData();
    }
  }, [activeView]);

  return (
    <div className="collaboration-dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">
          <span className="title-icon">👥</span>
          Collaboration Hub
        </h1>

        <div className="header-actions">
          <div className={`connection-indicator ${connected ? 'connected' : 'disconnected'}`}>
            <span className="indicator-dot"></span>
            {connected ? 'Connected' : 'Disconnected'}
          </div>

          <button
            className="copilot-toggle-btn"
            onClick={() => setCopilotOpen(!copilotOpen)}
          >
            <span className="btn-icon">✨</span>
            Grace Co-Pilot
          </button>
        </div>
      </div>

      <div className="dashboard-nav">
        <button
          className={`nav-btn ${activeView === 'presence' ? 'active' : ''}`}
          onClick={() => setActiveView('presence')}
        >
          <span className="nav-icon">👥</span>
          Presence
          {presenceData?.total_sessions > 0 && (
            <span className="nav-badge">{presenceData.total_sessions}</span>
          )}
        </button>

        <button
          className={`nav-btn ${activeView === 'workflows' ? 'active' : ''}`}
          onClick={() => setActiveView('workflows')}
        >
          <span className="nav-icon">📋</span>
          Workflows
        </button>

        <button
          className={`nav-btn ${activeView === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveView('notifications')}
        >
          <span className="nav-icon">🔔</span>
          Notifications
          {unreadCount > 0 && (
            <span className="nav-badge">{unreadCount}</span>
          )}
        </button>

        <button
          className={`nav-btn ${activeView === 'automation' ? 'active' : ''}`}
          onClick={() => setActiveView('automation')}
        >
          <span className="nav-icon">🤖</span>
          Automation
        </button>

        <button
          className={`nav-btn ${activeView === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveView('analytics')}
        >
          <span className="nav-icon">📊</span>
          Analytics
        </button>
      </div>

      <div className="dashboard-content">
        {activeView === 'presence' && (
          <PresencePanel token={token} presenceData={presenceData} />
        )}

        {activeView === 'workflows' && (
          <WorkflowManager token={token} userId={userId} />
        )}

        {activeView === 'notifications' && (
          <NotificationCenter
            token={token}
            onCountChange={setUnreadCount}
          />
        )}

        {activeView === 'automation' && (
          <AutomationRulesPanel token={token} />
        )}

        {activeView === 'analytics' && (
          <CollaborationAnalytics token={token} />
        )}
      </div>

      <GraceCopilotSidebar
        isOpen={copilotOpen}
        onClose={() => setCopilotOpen(false)}
        token={token}
      />
    </div>
  );
};
