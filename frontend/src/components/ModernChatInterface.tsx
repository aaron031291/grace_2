import React, { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';
import { ChatKindSelector } from './ChatKindSelector';
import type { ChatKind } from '../types/chat';
import './ModernChatInterface.css';

export const ModernChatInterface: React.FC = () => {
  const [showKindSelector, setShowKindSelector] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const {
    projects,
    activeProjectId,
    activeThreadId,
    createProject,
    createThread,
    setActiveThread,
    addMessage,
    getActiveProject,
    getActiveThread,
  } = useChatStore();

  const activeProject = getActiveProject();
  const activeThread = getActiveThread();

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputValue]);

  // Initialize default project with Grace-specific chats
  useEffect(() => {
    if (projects.length === 0) {
      const projectId = createProject('Grace Project', 'Default Grace workspace');
      
      // Create initial chat threads
      const chatTypes: Array<{ kind: ChatKind; title: string }> = [
        { kind: 'guardian', title: '🛡️ System Health' },
        { kind: 'coding', title: '💻 Development' },
        { kind: 'governance', title: '⚖️ Governance' },
        { kind: 'research', title: '🔬 Research' },
        { kind: 'general', title: '💬 General Chat' },
      ];
      
      chatTypes.forEach(({ kind, title }) => {
        createThread(projectId, kind, title);
      });
      
      // Set first thread as active
      const project = projects.find(p => p.id === projectId);
      if (project?.threads[0]) {
        setActiveThread(project.threads[0].id);
      }
    }
  }, []);

  const handleNewChat = (kind: ChatKind) => {
    if (!activeProjectId) {
      const projectId = createProject('Grace Project', 'Default Grace workspace');
      createThread(projectId, kind);
    } else {
      createThread(activeProjectId, kind);
    }
    setShowKindSelector(false);
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || !activeProjectId || !activeThreadId) return;

    addMessage(activeProjectId, activeThreadId, {
      role: 'user',
      content: inputValue,
    });

    // TODO: Send to backend API and get response
    setTimeout(() => {
      if (activeProjectId && activeThreadId) {
        addMessage(activeProjectId, activeThreadId, {
          role: 'assistant',
          content: 'This is a placeholder response. Backend integration coming soon.',
        });
      }
    }, 500);

    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="modern-chat-interface">
      {/* Sidebar */}
      <aside className="chat-sidebar">
        <div className="sidebar-header">
          <h2>GRACE</h2>
        </div>

        <nav className="nav-list">
          {activeProject?.threads.map((thread) => (
            <button
              key={thread.id}
              className={`nav-item ${thread.id === activeThreadId ? 'active' : ''}`}
              onClick={() => setActiveThread(thread.id)}
            >
              <span className="icon">💬</span>
              <span className="nav-text">{thread.title}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="chat-main">
        {/* Top bar */}
        <div className="chat-top-bar">
          <button
            className="plus-button"
            onClick={() => setShowKindSelector(true)}
            title="New chat"
          >
            +
          </button>

          <div className="search-container">
            <input
              type="text"
              className="search-input"
              placeholder="Search conversations..."
            />
          </div>
        </div>

        {/* Chat panel */}
        <div className="chat-panel">
          <div className="chat-history">
            {activeThread?.messages.map((message) => (
              <div key={message.id} className={`message ${message.role}`}>
                <div className="avatar">
                  {message.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="content">
                  <p>{message.content}</p>
                  {message.role === 'assistant' && (
                    <div className="actions">
                      <button>👍</button>
                      <button>👎</button>
                      <button>📋 Copy</button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {(!activeThread || activeThread.messages.length === 0) && (
              <div className="empty-state">
                <div className="empty-icon">💬</div>
                <h3>Start a conversation</h3>
                <p>Choose a chat type to begin</p>
              </div>
            )}
          </div>

          {/* Input area */}
          <div className="input-area">
            <button className="input-icon" title="Attach file">
              📎
            </button>

            <textarea
              ref={textareaRef}
              className="prompt-input"
              placeholder="Message Grace..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />

            <button
              className="send-button"
              onClick={handleSendMessage}
              disabled={!inputValue.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </main>

      {/* Chat kind selector modal */}
      {showKindSelector && (
        <ChatKindSelector
          onSelect={handleNewChat}
          onCancel={() => setShowKindSelector(false)}
        />
      )}
    </div>
  );
};
