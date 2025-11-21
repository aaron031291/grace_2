import React, { useState, useEffect, useRef } from 'react';
import './RightPanel.css';

interface RightPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

interface Message {
  id: string;
  sender: 'user' | 'grace';
  content: string;
  timestamp: Date;
  type: 'notification' | 'question' | 'discussion' | 'task_update';
  taskContext?: TaskContext;
}

interface TaskContext {
  taskId: string;
  taskName: string;
  estimatedTime: string;
  fileSize?: string;
  complexity: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'completed';
  variables: Record<string, any>;
}

const RightPanel: React.FC<RightPanelProps> = ({ isOpen, onToggle }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'grace',
      content: 'I noticed you\'re working on the Builder API. Should I optimize the WebSocket streaming for large file transfers (>1GB)?',
      timestamp: new Date(Date.now() - 300000),
      type: 'question',
      taskContext: {
        taskId: 'task_001',
        taskName: 'Optimize Builder API',
        estimatedTime: '2 hours',
        fileSize: '1.2 GB',
        complexity: 'medium',
        status: 'pending',
        variables: {
          affectedFiles: 3,
          dependencies: ['websocket', 'streaming'],
          priority: 'high'
        }
      }
    }
  ]);
  const [input, setInput] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Simulate Grace sending notifications
  useEffect(() => {
    const interval = setInterval(() => {
      // This would be replaced with actual WebSocket connection
      // For now, just a placeholder
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: input,
      timestamp: new Date(),
      type: 'discussion'
    };

    setMessages(prev => [...prev, newMessage]);
    setInput('');

    // Simulate Grace's response
    setTimeout(() => {
      const response: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'grace',
        content: 'Got it! I\'ll handle that. Estimated completion: 15 minutes.',
        timestamp: new Date(),
        type: 'task_update',
        taskContext: {
          taskId: 'task_002',
          taskName: input,
          estimatedTime: '15 minutes',
          complexity: 'low',
          status: 'in_progress',
          variables: {}
        }
      };
      setMessages(prev => [...prev, response]);
    }, 1000);
  };

  const handleTaskAction = (action: 'approve' | 'decline' | 'discuss', messageId: string) => {
    const message = messages.find(m => m.id === messageId);
    if (!message) return;

    let responseContent = '';
    switch (action) {
      case 'approve':
        responseContent = `Perfect! I'll start working on "${message.taskContext?.taskName}" right away.`;
        break;
      case 'decline':
        responseContent = 'Understood. I\'ll skip this for now.';
        break;
      case 'discuss':
        responseContent = 'Sure! What would you like to know about this task?';
        break;
    }

    const response: Message = {
      id: Date.now().toString(),
      sender: 'grace',
      content: responseContent,
      timestamp: new Date(),
      type: 'discussion'
    };

    setMessages(prev => [...prev, response]);
  };

  return (
    <>
      {/* Collapsed Tab with Notification Badge */}
      {!isOpen && (
        <div className="right-panel-tab" onClick={onToggle}>
          <span className="tab-text">COLLAB</span>
          {unreadCount > 0 && (
            <span className="notification-badge">{unreadCount}</span>
          )}
        </div>
      )}

      {/* Expanded Panel */}
      {isOpen && (
        <div className="right-panel">
          <div className="panel-header">
            <h3>💬 Collaboration</h3>
            <button className="close-btn" onClick={onToggle}>×</button>
          </div>

          <div className="panel-content">
            {/* Messages */}
            <div className="messages-container">
              {messages.map(message => (
                <div key={message.id} className={`collab-message ${message.sender}`}>
                  <div className="message-header">
                    <span className="sender-name">
                      {message.sender === 'grace' ? '🤖 Grace' : '👤 You'}
                    </span>
                    <span className="message-time">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>

                  <div className="message-content">{message.content}</div>

                  {/* Task Context */}
                  {message.taskContext && (
                    <div className="task-context">
                      <div className="task-header">
                        <span className="task-name">{message.taskContext.taskName}</span>
                        <span className={`complexity-badge ${message.taskContext.complexity}`}>
                          {message.taskContext.complexity}
                        </span>
                      </div>
                      <div className="task-details">
                        <div className="detail-item">
                          <span className="detail-label">⏱️ Time:</span>
                          <span className="detail-value">{message.taskContext.estimatedTime}</span>
                        </div>
                        {message.taskContext.fileSize && (
                          <div className="detail-item">
                            <span className="detail-label">📦 Size:</span>
                            <span className="detail-value">{message.taskContext.fileSize}</span>
                          </div>
                        )}
                        <div className="detail-item">
                          <span className="detail-label">📊 Status:</span>
                          <span className={`status-badge ${message.taskContext.status}`}>
                            {message.taskContext.status.replace('_', ' ')}
                          </span>
                        </div>
                      </div>

                      {/* Variables */}
                      {Object.keys(message.taskContext.variables).length > 0 && (
                        <div className="task-variables">
                          {Object.entries(message.taskContext.variables).map(([key, value]) => (
                            <div key={key} className="variable-item">
                              <span className="var-key">{key}:</span>
                              <span className="var-value">{JSON.stringify(value)}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Actions for Grace's questions */}
                      {message.sender === 'grace' && message.type === 'question' && (
                        <div className="task-actions">
                          <button
                            className="task-action-btn approve"
                            onClick={() => handleTaskAction('approve', message.id)}
                          >
                            ✓ Approve
                          </button>
                          <button
                            className="task-action-btn decline"
                            onClick={() => handleTaskAction('decline', message.id)}
                          >
                            ✗ Decline
                          </button>
                          <button
                            className="task-action-btn discuss"
                            onClick={() => handleTaskAction('discuss', message.id)}
                          >
                            💬 Discuss
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="collab-input-container">
              <textarea
                className="collab-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Discuss with Grace..."
                rows={2}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
              />
              <button
                className="send-collab-btn"
                onClick={handleSend}
                disabled={!input.trim()}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RightPanel;
