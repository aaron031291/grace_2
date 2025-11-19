/**
 * CoPilotPane Component
 * Grace's persistent AI assistant interface
 * Features: Notifications, bi-directional chat, multi-modal input, quick actions
 */
import React, { useState, useEffect, useRef } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import axios from 'axios';
import './CoPilotPane.css';

interface Notification {
  id: string;
  type: 'alert' | 'pending' | 'info';
  severity: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  actions: NotificationAction[];
  created_at: string;
}

interface NotificationAction {
  label: string;
  action: string;
  params?: Record<string, any>;
}

interface ChatMessage {
  id: string;
  sender: 'grace' | 'user';
  text: string;
  rich_content?: any;
  actions?: MessageAction[];
  timestamp: string;
}

interface MessageAction {
  label: string;
  action: string;
  params?: Record<string, any>;
}

interface QuickAction {
  label: string;
  action: string;
  icon?: string;
}

interface CoPilotPaneProps {
  currentLayer: 'layer1' | 'layer2' | 'layer3' | 'layer4';
  onAction?: (action: string, params?: any) => void;
}

const API_BASE = apiUrl('';

export const CoPilotPane: React.FC<CoPilotPaneProps> = ({ currentLayer, onAction }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [graceStatus, setGraceStatus] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');
  const [notificationsExpanded, setNotificationsExpanded] = useState(true);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [quickActions, setQuickActions] = useState<QuickAction[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchNotifications();
    fetchQuickActions();

    const notifInterval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(notifInterval);
  }, []);

  useEffect(() => {
    fetchQuickActions();
  }, [currentLayer]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/copilot/notifications`);
      setNotifications(response.data.notifications || []);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const fetchQuickActions = async () => {
    const actionsMap: Record<string, QuickAction[]> = {
      layer1: [
        { label: 'Restart All Kernels', action: 'restart_all_kernels', icon: '↻' },
        { label: 'Run Full Stress Test', action: 'run_stress_test', icon: '⚡' },
        { label: 'Check Crypto Health', action: 'check_crypto', icon: '🔐' },
        { label: 'View System Logs', action: 'view_system_logs', icon: '📋' },
      ],
      layer2: [
        { label: 'Spawn Extra Agent', action: 'spawn_agent', icon: '🤖' },
        { label: 'Defer Low Priority', action: 'defer_low_priority', icon: '⏸' },
        { label: 'Clear Completed', action: 'clear_completed', icon: '🗑️' },
        { label: 'Export Queue Snapshot', action: 'export_queue', icon: '📊' },
      ],
      layer3: [
        { label: '🤖 New Coding Build', action: 'new_build', icon: '🤖' },
        { label: 'Create Intent', action: 'create_intent', icon: '🎯' },
        { label: 'Review Policies', action: 'review_policies', icon: '📜' },
        { label: 'Generate Retro', action: 'generate_retro', icon: '🎓' },
      ],
      layer4: [
        { label: 'Add New Secret', action: 'add_secret', icon: '🔐' },
        { label: 'Ingest All Recordings', action: 'ingest_all_recordings', icon: '🎙️' },
        { label: 'Run System Stress Test', action: 'run_stress_test', icon: '⚡' },
        { label: 'View Deployment Status', action: 'view_deployment', icon: '🚀' },
      ],
    };

    setQuickActions(actionsMap[currentLayer] || []);
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: inputText,
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, userMessage]);
    setInputText('');
    setGraceStatus('thinking');

    try {
      const response = await axios.post(`${API_BASE}/api/copilot/chat/send`, {
        message: inputText,
        context: {
          current_layer: currentLayer,
          conversation_history: messages.slice(-5),
        },
      });

      const graceMessage: ChatMessage = {
        id: response.data.message_id,
        sender: 'grace',
        text: response.data.grace_response.text,
        rich_content: response.data.grace_response.rich_content,
        actions: response.data.grace_response.actions,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, graceMessage]);
      setGraceStatus('idle');
    } catch (error) {
      console.error('Failed to send message:', error);
      setGraceStatus('idle');
    }
  };

  const handleNotificationAction = async (notificationId: string, action: string, params?: any) => {
    try {
      await axios.post(`${API_BASE}/api/copilot/notifications/${notificationId}/action`, {
        action,
        params,
      });

      setNotifications(notifications.filter((n) => n.id !== notificationId));

      if (onAction) {
        onAction(action, params);
      }
    } catch (error) {
      console.error('Failed to execute notification action:', error);
    }
  };

  const dismissNotification = async (notificationId: string) => {
    try {
      await axios.delete(`${API_BASE}/api/copilot/notifications/${notificationId}`);
      setNotifications(notifications.filter((n) => n.id !== notificationId));
    } catch (error) {
      console.error('Failed to dismiss notification:', error);
    }
  };

  const handleVoiceInput = async () => {
    setIsVoiceMode(true);
    setGraceStatus('listening');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        try {
          const response = await axios.post(`${API_BASE}/api/copilot/voice/transcribe`, formData);
          setInputText(response.data.transcription);
          setIsVoiceMode(false);
          setGraceStatus('idle');
        } catch (error) {
          console.error('Voice transcription failed:', error);
          setIsVoiceMode(false);
          setGraceStatus('idle');
        }
      };

      mediaRecorder.start();

      setTimeout(() => {
        mediaRecorder.stop();
        stream.getTracks().forEach((track) => track.stop());
      }, 5000);
    } catch (error) {
      console.error('Voice input failed:', error);
      setIsVoiceMode(false);
      setGraceStatus('idle');
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setGraceStatus('thinking');

    axios.post(`${API_BASE}/api/copilot/upload`, formData)
      .then((response) => {
        const graceMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          sender: 'grace',
          text: `Analyzed ${file.name}: ${response.data.analysis.summary}`,
          actions: response.data.suggested_actions,
          timestamp: new Date().toISOString(),
        };
        setMessages([...messages, graceMessage]);
        setGraceStatus('idle');
      })
      .catch((error) => {
        console.error('File upload failed:', error);
        setGraceStatus('idle');
      });
  };

  const handleQuickAction = async (action: string) => {
    if (onAction) {
      onAction(action);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle': return '#00ff88';
      case 'listening': return '#ffaa00';
      case 'thinking': return '#00aaff';
      case 'speaking': return '#ff00ff';
      default: return '#888888';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'idle': return 'Ready';
      case 'listening': return 'Listening...';
      case 'thinking': return 'Thinking...';
      case 'speaking': return 'Responding...';
      default: return 'Unknown';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return '🔴';
      case 'warning': return '🟡';
      case 'info': return '🔵';
      default: return '⚪';
    }
  };

  return (
    <div className="copilot-pane">
      {/* Header */}
      <div className="copilot-header">
        <div className="grace-avatar">
          <div className={`avatar-circle ${graceStatus}`}></div>
        </div>
        <div className="grace-info">
          <div className="grace-name">Grace</div>
          <div className="grace-status" style={{ color: getStatusColor(graceStatus) }}>
            {getStatusText(graceStatus)}
          </div>
        </div>
      </div>

      {/* Notifications Panel */}
      <div className="notifications-panel">
        <div className="notifications-header" onClick={() => setNotificationsExpanded(!notificationsExpanded)}>
          <h3>Notifications ({notifications.length})</h3>
          <button className="toggle-btn">{notificationsExpanded ? '▼' : '▶'}</button>
        </div>
        {notificationsExpanded && (
          <div className="notifications-list">
            {notifications.length > 0 ? (
              notifications.map((notif) => (
                <div key={notif.id} className={`notification-card ${notif.severity}`}>
                  <div className="notification-header">
                    <span className="notification-icon">{getSeverityIcon(notif.severity)}</span>
                    <span className="notification-title">{notif.title}</span>
                    <button
                      className="dismiss-btn"
                      onClick={() => dismissNotification(notif.id)}
                    >
                      ✕
                    </button>
                  </div>
                  <div className="notification-message">{notif.message}</div>
                  {notif.actions.length > 0 && (
                    <div className="notification-actions">
                      {notif.actions.map((action, idx) => (
                        <button
                          key={idx}
                          className="notif-action-btn"
                          onClick={() => handleNotificationAction(notif.id, action.action, action.params)}
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}
                  <div className="notification-time">
                    {new Date(notif.created_at).toLocaleTimeString()}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-notifications">No notifications</div>
            )}
          </div>
        )}
      </div>

      {/* Chat Interface */}
      <div className="chat-interface">
        <div className="chat-messages">
          {messages.length > 0 ? (
            messages.map((msg) => (
              <div key={msg.id} className={`chat-message ${msg.sender}`}>
                <div className="message-header">
                  <span className="message-sender">
                    {msg.sender === 'grace' ? 'Grace' : 'You'}
                  </span>
                  <span className="message-time">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-content">
                  {msg.text}
                  {msg.rich_content && (
                    <div className="rich-content">
                      {/* Render tables, code, charts here */}
                      <pre>{JSON.stringify(msg.rich_content, null, 2)}</pre>
                    </div>
                  )}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="message-actions">
                      {msg.actions.map((action, idx) => (
                        <button
                          key={idx}
                          className="message-action-btn"
                          onClick={() => onAction && onAction(action.action, action.params)}
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="no-messages">
              <div className="grace-welcome">👋</div>
              <div>Hi! I'm Grace, your AI assistant.</div>
              <div>Ask me anything or use quick actions below.</div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <div className="input-controls">
          <button
            className="input-control-btn"
            title="Attach file"
            onClick={() => fileInputRef.current?.click()}
          >
            📎
          </button>
          <button
            className={`input-control-btn ${isVoiceMode ? 'active' : ''}`}
            title="Voice input"
            onClick={handleVoiceInput}
          >
            🎤
          </button>
          <button
            className="input-control-btn"
            title="Screenshot"
            onClick={() => {/* Implement screenshot capture */}}
          >
            📸
          </button>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
        </div>
        <div className="input-field-container">
          <input
            type="text"
            className="chat-input-field"
            placeholder={isVoiceMode ? 'Listening...' : 'Ask Grace anything...'}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={isVoiceMode}
          />
          <button
            className="send-btn"
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isVoiceMode}
          >
            Send
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-panel">
        <h4>Quick Actions</h4>
        <div className="quick-actions-list">
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              className="quick-action-btn"
              onClick={() => handleQuickAction(action.action)}
            >
              {action.icon && <span className="action-icon">{action.icon}</span>}
              {action.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
