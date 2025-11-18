import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';

interface Notification {
  notification_id: string;
  title: string;
  message: string;
  priority: string;
  is_read: boolean;
  created_at: string;
  action_url?: string;
  action_label?: string;
}

interface NotificationCenterProps {
  token: string;
  onCountChange: (count: number) => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ token, onCountChange }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/collaboration/notifications?unread_only=${filter === 'unread'}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      const data = await response.json();
      setNotifications(data.notifications);
      
      const unreadCount = data.notifications.filter((n: Notification) => !n.is_read).length;
      onCountChange(unreadCount);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      await fetch(
        `http://localhost:8000/api/collaboration/notifications/${notificationId}/read`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch(apiUrl('/api/collaboration/notifications/mark-all-read', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const dismiss = async (notificationId: string) => {
    try {
      await fetch(
        `http://localhost:8000/api/collaboration/notifications/${notificationId}/dismiss`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      fetchNotifications();
    } catch (error) {
      console.error('Failed to dismiss:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#ff4757';
      case 'high': return '#ffa502';
      case 'normal': return '#1e90ff';
      case 'low': return '#95afc0';
      default: return '#95afc0';
    }
  };

  return (
    <div className="notification-center">
      <div className="notification-header">
        <div className="filter-tabs">
          <button
            className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`filter-tab ${filter === 'unread' ? 'active' : ''}`}
            onClick={() => setFilter('unread')}
          >
            Unread
          </button>
        </div>

        <button className="mark-all-read-btn" onClick={markAllAsRead}>
          Mark All Read
        </button>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
        </div>
      ) : notifications.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">🔕</span>
          <p>No notifications</p>
        </div>
      ) : (
        <div className="notifications-list">
          {notifications.map((notification) => (
            <div
              key={notification.notification_id}
              className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
            >
              <div
                className="notification-priority"
                style={{ background: getPriorityColor(notification.priority) }}
              />

              <div className="notification-content">
                <div className="notification-title">{notification.title}</div>
                <div className="notification-message">{notification.message}</div>
                <div className="notification-time">
                  {new Date(notification.created_at).toLocaleString()}
                </div>

                {notification.action_url && (
                  <button className="notification-action">
                    {notification.action_label || 'View'}
                  </button>
                )}
              </div>

              <div className="notification-actions">
                {!notification.is_read && (
                  <button
                    className="action-btn"
                    onClick={() => markAsRead(notification.notification_id)}
                    title="Mark as read"
                  >
                    ✓
                  </button>
                )}
                <button
                  className="action-btn"
                  onClick={() => dismiss(notification.notification_id)}
                  title="Dismiss"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
