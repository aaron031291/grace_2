/**
 * Notification Toast Component
 * Shows visual notifications with optional vibration
 */

import { useEffect, useState } from 'react';
import './NotificationToast.css';

export interface Toast {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'grace';
  duration?: number; // ms, 0 = permanent until clicked
  onClick?: () => void;
  vibrate?: boolean;
}

interface NotificationToastProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

export default function NotificationToast({ toasts, onDismiss }: NotificationToastProps) {
  useEffect(() => {
    toasts.forEach(toast => {
      // Vibrate if supported and enabled
      if (toast.vibrate && 'vibrate' in navigator) {
        navigator.vibrate([50, 20, 50]);
      }

      // Auto-dismiss if duration is set
      if (toast.duration && toast.duration > 0) {
        const timer = setTimeout(() => {
          onDismiss(toast.id);
        }, toast.duration);

        return () => clearTimeout(timer);
      }
    });
  }, [toasts, onDismiss]);

  if (toasts.length === 0) return null;

  const getIcon = (type: string) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'grace': return '🤖';
      default: return '💬';
    }
  };

  return (
    <div className="notification-toast-container">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`notification-toast toast-${toast.type}`}
          onClick={() => {
            if (toast.onClick) toast.onClick();
            onDismiss(toast.id);
          }}
        >
          <div className="toast-icon">{getIcon(toast.type)}</div>
          <div className="toast-message">{toast.message}</div>
          <button
            className="toast-close"
            onClick={(e) => {
              e.stopPropagation();
              onDismiss(toast.id);
            }}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

// Hook for managing toasts
export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (
    message: string,
    type: Toast['type'] = 'info',
    options: Partial<Toast> = {}
  ) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const newToast: Toast = {
      id,
      message,
      type,
      duration: 5000, // Default 5 seconds
      vibrate: type === 'grace' || type === 'warning', // Vibrate for Grace messages and warnings
      ...options,
    };

    setToasts(prev => [...prev, newToast]);
    return id;
  };

  const dismissToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const clearAll = () => {
    setToasts([]);
  };

  return {
    toasts,
    showToast,
    dismissToast,
    clearAll,
  };
}
