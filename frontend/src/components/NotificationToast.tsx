/**
 * Notification Toast Component
 * Displays real-time notifications for book ingestion and other events
 */

import React, { useState, useEffect } from 'react';
import { X, CheckCircle, Info, AlertTriangle, AlertCircle } from 'lucide-react';
import { notifications, Notification, setupBookEventListeners } from '../utils/notifications';

export function NotificationToast() {
  const [activeNotifications, setActiveNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    // Subscribe to notifications
    const unsubscribe = notifications.subscribe((notification) => {
      setActiveNotifications(prev => [...prev, notification]);

      // Auto-dismiss after duration
      if (notification.duration) {
        setTimeout(() => {
          dismissNotification(notification.id);
        }, notification.duration);
      }
    });

    // Setup book event listeners
    const cleanup = setupBookEventListeners();

    return () => {
      unsubscribe();
      cleanup();
    };
  }, []);

  const dismissNotification = (id: string) => {
    setActiveNotifications(prev => prev.filter(n => n.id !== id));
    notifications.dismiss(id);
  };

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
    }
  };

  const getBorderColor = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return 'border-green-500/50';
      case 'info':
        return 'border-blue-500/50';
      case 'warning':
        return 'border-yellow-500/50';
      case 'error':
        return 'border-red-500/50';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {activeNotifications.map((notification, index) => (
        <div
          key={notification.id}
          className={`bg-gray-900 border-l-4 ${getBorderColor(notification.type)} rounded-lg shadow-2xl p-4 animate-slide-in`}
          style={{
            animation: `slideIn 0.3s ease-out ${index * 0.1}s both`,
          }}
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              {getIcon(notification.type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white">
                {notification.title}
              </p>
              <p className="text-sm text-gray-400 mt-1">
                {notification.message}
              </p>
              {notification.action && (
                <button
                  onClick={notification.action.onClick}
                  className="mt-2 text-xs text-blue-400 hover:text-blue-300 font-medium"
                >
                  {notification.action.label}
                </button>
              )}
            </div>
            <button
              onClick={() => dismissNotification(notification.id)}
              className="flex-shrink-0 text-gray-500 hover:text-gray-300 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}

      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

export default NotificationToast;
