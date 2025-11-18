/**
 * Notifications Hook - Subscribe to Grace's real-time updates
 * 
 * Connects to WebSocket and receives:
 * - Task completion updates
 * - Approval requests
 * - Error alerts
 * - Healing triggers
 * - Background task progress
 */

import { useEffect, useState, useCallback } from 'react';
import { API_ENDPOINTS } from '../api/config';

export interface Notification {
  type: string;
  message: string;
  badge: string;
  timestamp: string;
  data?: any;
}

export const useNotifications = (userId: string = 'user') => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Build WebSocket URL
    const wsUrl = API_ENDPOINTS.chat
      .replace('http:', 'ws:')
      .replace('https:', 'wss:')
      .replace('/chat', `/notifications/stream?user_id=${userId}`);

    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('[Notifications] Connected');
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      console.log('[Notifications] Received:', notification);

      // Add to notifications list
      setNotifications((prev) => [...prev, notification]);
    };

    websocket.onerror = (error) => {
      console.error('[Notifications] Error:', error);
      setConnected(false);
    };

    websocket.onclose = () => {
      console.log('[Notifications] Disconnected');
      setConnected(false);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [userId]);

  const sendCommand = useCallback((type: string, data?: any) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type, ...data }));
    }
  }, [ws]);

  const listTasks = useCallback(() => {
    sendCommand('list_tasks');
  }, [sendCommand]);

  const cancelTask = useCallback((taskId: string) => {
    sendCommand('cancel_task', { task_id: taskId });
  }, [sendCommand]);

  const pauseLearning = useCallback(() => {
    sendCommand('pause_learning');
  }, [sendCommand]);

  const resumeLearning = useCallback(() => {
    sendCommand('resume_learning');
  }, [sendCommand]);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    connected,
    listTasks,
    cancelTask,
    pauseLearning,
    resumeLearning,
    clearNotifications,
  };
};
