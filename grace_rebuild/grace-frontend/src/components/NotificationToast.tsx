import { useEffect, useState } from 'react';
import './NotificationToast.css';

interface Notification {
  id: number;
  message: string;
  type: 'info' | 'success' | 'warning';
}

let notificationId = 0;
const notifications: Notification[] = [];
const listeners: Set<(notifications: Notification[]) => void> = new Set();

export function addNotification(message: string, type: 'info' | 'success' | 'warning' = 'info') {
  const notification: Notification = {
    id: notificationId++,
    message,
    type
  };
  notifications.push(notification);
  listeners.forEach(listener => listener([...notifications]));
  
  setTimeout(() => {
    const index = notifications.findIndex(n => n.id === notification.id);
    if (index > -1) {
      notifications.splice(index, 1);
      listeners.forEach(listener => listener([...notifications]));
    }
  }, 5000);
}

export function NotificationToast() {
  const [items, setItems] = useState<Notification[]>([]);

  useEffect(() => {
    listeners.add(setItems);
    return () => {
      listeners.delete(setItems);
    };
  }, []);

  return (
    <div className="notification-container">
      {items.map((notification) => (
        <div key={notification.id} className={`notification ${notification.type}`}>
          <span className="notification-icon">
            {notification.type === 'success' && '✓'}
            {notification.type === 'info' && 'ℹ'}
            {notification.type === 'warning' && '⚠'}
          </span>
          <span className="notification-message">{notification.message}</span>
        </div>
      ))}
    </div>
  );
}
