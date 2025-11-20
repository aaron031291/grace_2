/**
 * Grace Chat Application
 * 
 * Minimal chat interface with health monitoring
 */

import { useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { HealthMeter } from './components/HealthMeter';
import { RemoteCockpit } from './components/RemoteCockpitEnhanced';
import { BackgroundTasksDrawer } from './components/BackgroundTasksDrawerEnhanced';
import { TelemetryStrip } from './components/TelemetryStrip';
import { HistorySearch } from './components/HistorySearch';
import { UserPresenceBar } from './components/UserPresence';
import { FileExplorer } from './components/FileExplorer';
import { MissionControlDashboard } from './components/MissionControlDashboard';
import { SystemDashboard } from './components/SystemDashboard';
import { SystemOverview } from './components/SystemOverview';
import { MentorRoundtable } from './components/MentorRoundtable';
import { ModernChatInterface } from './components/ModernChatInterface';
import { TerminalViewer } from './components/TerminalViewer';
import { ContextPanel } from './components/panels/ContextPanel';
import { MemoryPanel } from './components/panels/MemoryPanel';
import { LogsPanel } from './components/panels/LogsPanel';
import { GovernancePanel } from './components/panels/GovernancePanel';
import { RemoteAPI } from './api/remote';
import { AppShell } from './components/layout/AppShell';
import { TopBar } from './components/layout/TopBar';
import { LeftSidebar, type NavItem } from './components/layout/LeftSidebar';
import { RightSidebar } from './components/layout/RightSidebar';
import { BottomStatusBar } from './components/layout/BottomStatusBar';
import './AppChat.css';

type Mode = 'observe' | 'learn' | 'autonomous';

function AppChat() {
  const [activeView, setActiveView] = useState<'chat' | 'dashboard' | 'overview' | 'modern' | 'mission'>('modern'); // Default to modern chat
  const [cockpitOpen, setCockpitOpen] = useState(false);
  const [tasksOpen, setTasksOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [fileExplorerOpen, setFileExplorerOpen] = useState(false);
  const [missionControlOpen, setMissionControlOpen] = useState(false);
  const [mentorOpen, setMentorOpen] = useState(false);
  const [remoteActive, setRemoteActive] = useState(false);
  const [screenShareActive, setScreenShareActive] = useState(false);
  const [remoteSessionId, setRemoteSessionId] = useState<string | null>(null);
  const [screenShareSessionId, setScreenShareSessionId] = useState<string | null>(null);
  const [remoteLoading, setRemoteLoading] = useState(false);
  const [screenShareLoading, setScreenShareLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remoteStatus, setRemoteStatus] = useState<string>('');
  const [screenShareStatus, setScreenShareStatus] = useState<string>('');
  const [requiresApproval, setRequiresApproval] = useState(false);
  const [screenShareMode, setScreenShareMode] = useState<'learn' | 'observe_only' | 'consent_required'>('learn');
  const [showModeSelector, setShowModeSelector] = useState(false);
  const [graceMode, setGraceMode] = useState<Mode>('learn');

  const handleRemoteToggle = async () => {
    setRemoteLoading(true);
    setError(null);
    
    try {
      if (remoteActive) {
        setRemoteStatus('Stopping...');
        if (remoteSessionId) {
          await RemoteAPI.stopRemoteAccess(remoteSessionId);
          setRemoteSessionId(null);
        }
        setRemoteActive(false);
        setRemoteStatus('Stopped');
        setRequiresApproval(false);
      } else {
        setRemoteStatus('Connecting...');
        const response = await RemoteAPI.startRemoteAccess('supervised');
        if (response.session_id || response.trace_id) {
          const sessionId = response.session_id || response.trace_id;
          setRemoteSessionId(sessionId);
          
          if (response.requires_approval) {
            setRequiresApproval(true);
            setRemoteStatus('Pending Approval');
            // Poll for approval
            const interval = setInterval(async () => {
              try {
                const status = await RemoteAPI.getRemoteStatus(sessionId);
                if (status.status === 'active') {
                  setRemoteActive(true);
                  setRequiresApproval(false);
                  setRemoteStatus('Connected');
                  clearInterval(interval);
                }
              } catch (err) {
                clearInterval(interval);
              }
            }, 2000);
          } else {
            setRemoteActive(true);
            setRemoteStatus('Connected');
            // Start heartbeat
            startSessionHeartbeat(sessionId);
          }
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(`Remote Access: ${errorMsg}`);
      setRemoteStatus('Failed');
      console.error('Remote access error:', err);
    } finally {
      setRemoteLoading(false);
    }
  };

  const startSessionHeartbeat = (sessionId: string) => {
    const interval = setInterval(async () => {
      try {
        await RemoteAPI.sessionHeartbeat(sessionId);
      } catch (err) {
        console.warn('Heartbeat failed:', err);
        clearInterval(interval);
      }
    }, 30000); // Every 30 seconds
    
    // Store interval to clear on stop
    (window as any).__sessionHeartbeat = interval;
  };

  const handleScreenShareToggle = async (mode?: string) => {
    if (screenShareActive) {
      // Stop screen share
      setScreenShareLoading(true);
      setError(null);
      
      try {
        setScreenShareStatus('Stopping...');
        if (screenShareSessionId) {
          const result = await RemoteAPI.stopScreenShare(screenShareSessionId);
          setScreenShareSessionId(null);
          
          // Show learning stats in chat
          if (result.frames_learned > 0) {
            const statsMsg = `📺 Screen share ended. Grace learned from ${result.frames_learned} of ${result.frames_captured} captured frames.`;
            console.log(statsMsg);
          }
        }
        setScreenShareActive(false);
        setScreenShareStatus('');
        setShowModeSelector(false);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setError(`Screen Share: ${errorMsg}`);
        setScreenShareStatus('Failed');
        console.error('Screen share error:', err);
      } finally {
        setScreenShareLoading(false);
      }
    } else {
      // Show mode selector first, or start with current mode
      if (!mode && !showModeSelector) {
        setShowModeSelector(true);
        return;
      }
      
      const selectedMode = mode || screenShareMode;
      setScreenShareLoading(true);
      setError(null);
      
      try {
        setScreenShareStatus('Starting...');
        const response = await RemoteAPI.startScreenShareWithMode('medium', selectedMode);
        if (response.session_id) {
          setScreenShareSessionId(response.session_id);
          setScreenShareActive(true);
          
          const modeLabels = {
            'learn': '🧠 Learning from screen',
            'observe_only': '👁️ Observe only',
            'consent_required': '🔐 Consent required'
          };
          
          setScreenShareStatus(modeLabels[selectedMode as keyof typeof modeLabels] || 'Active');
          setShowModeSelector(false);
          
          // Start heartbeat
          startSessionHeartbeat(response.session_id);
          
          // Poll for stats if learning mode
          if (selectedMode === 'learn') {
            const interval = setInterval(async () => {
              try {
                const status = await RemoteAPI.getScreenShareStatus(response.session_id);
                if (status.frames_learned !== undefined) {
                  setScreenShareStatus(`🧠 Learned ${status.frames_learned} frames`);
                }
                if (status.status !== 'active') {
                  clearInterval(interval);
                }
              } catch (err) {
                clearInterval(interval);
              }
            }, 5000);
          }
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setError(`Screen Share: ${errorMsg}`);
        setScreenShareStatus('Failed');
        console.error('Screen share error:', err);
      } finally {
        setScreenShareLoading(false);
      }
    }
  };

  const handleDocumentUpload = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.onchange = async (e: any) => {
      const files = Array.from(e.target.files || []) as File[];
      setUploadLoading(true);
      setError(null);
      
      let successCount = 0;
      let failCount = 0;
      
      for (const file of files) {
        try {
          await RemoteAPI.uploadDocument(file);
          successCount++;
        } catch (error) {
          failCount++;
          console.error(`Failed to upload ${file.name}:`, error);
        }
      }
      
      setUploadLoading(false);
      
      if (successCount > 0) {
        alert(`✅ Uploaded ${successCount} file(s) successfully`);
      }
      if (failCount > 0) {
        setError(`Failed to upload ${failCount} file(s)`);
      }
    };
    input.click();
  };

  // Navigation items
  const navItems: NavItem[] = [
    { id: 'modern', label: 'Modern Chat', icon: '💬' },
    { id: 'mission', label: 'Terminal', icon: '🖥️' },
    { id: 'overview', label: 'System Overview', icon: '📊' },
    { id: 'dashboard', label: 'Legacy Dashboard', icon: '📈' },
    { id: 'chat', label: 'Classic Chat', icon: '🗨️' },
  ];

  // Render main view
  const renderMainView = () => {
    switch (activeView) {
      case 'modern':
        return <ModernChatInterface />;
      case 'mission':
        return <TerminalViewer />;
      case 'overview':
        return <SystemOverview />;
      case 'dashboard':
        return <SystemDashboard />;
      case 'chat':
      default:
        return (
          <>
            <TelemetryStrip />
            <UserPresenceBar currentUser="user" />
            <ChatPanel />
          </>
        );
    }
  };

  // Logo component
  const logo = (
    <div className="app-logo">
      <h1>🤖 GRACE</h1>
      <p>AI Assistant with Governance</p>
    </div>
  );

  // Sidebar controls
  const sidebarControls = (
    <>
      <HealthMeter />
      
      <div className="sidebar-controls">
        <h3>Quick Controls</h3>
        
        {error && (
          <div className="control-error" style={{ 
            padding: '8px', 
            background: '#fee', 
            border: '1px solid #fcc',
            borderRadius: '4px',
            marginBottom: '8px',
            fontSize: '12px',
            color: '#c00'
          }}>
            ⚠️ {error}
          </div>
        )}
        
        <button
          className={`control-button ${remoteActive ? 'active' : ''} ${requiresApproval ? 'pending' : ''}`}
          onClick={handleRemoteToggle}
          disabled={remoteLoading}
          title={remoteStatus || 'Toggle remote access'}
        >
          <div className="button-content">
            <span className="button-icon">
              {remoteLoading ? '⏳' : requiresApproval ? '🔐' : remoteActive ? '🔓' : '🔒'}
            </span>
            <span className="button-text">
              {remoteLoading ? 'Loading...' : 
               requiresApproval ? 'Pending' : 
               remoteActive ? 'Connected' : 
               'Remote Access'}
            </span>
            {remoteSessionId && (
              <span className="button-session">
                {remoteSessionId.slice(0, 8)}
              </span>
            )}
          </div>
          {remoteStatus && (
            <span className="button-status">{remoteStatus}</span>
          )}
        </button>
          
          <div className="screen-share-container">
            <button
              className={`control-button ${screenShareActive ? 'active' : ''}`}
              onClick={() => handleScreenShareToggle()}
              disabled={screenShareLoading}
              title={screenShareStatus || 'Toggle screen share'}
            >
              <div className="button-content">
                <span className="button-icon">
                  {screenShareLoading ? '⏳' : screenShareActive ? '📺' : '📺'}
                </span>
                <span className="button-text">
                  {screenShareLoading ? 'Loading...' : 
                   screenShareActive ? 'Sharing' : 
                   'Screen Share'}
                </span>
                {screenShareSessionId && (
                  <span className="button-session">
                    {screenShareSessionId.slice(0, 8)}
                  </span>
                )}
              </div>
              {screenShareStatus && (
                <span className="button-status">{screenShareStatus}</span>
              )}
            </button>
            
            {showModeSelector && !screenShareActive && (
              <div className="mode-selector">
                <div className="mode-selector-header">Choose Mode:</div>
                <button
                  className="mode-option"
                  onClick={() => {
                    setScreenShareMode('learn');
                    handleScreenShareToggle('learn');
                  }}
                >
                  🧠 Learn
                  <span className="mode-desc">Capture and store in memory</span>
                </button>
                <button
                  className="mode-option"
                  onClick={() => {
                    setScreenShareMode('observe_only');
                    handleScreenShareToggle('observe_only');
                  }}
                >
                  👁️ Observe Only
                  <span className="mode-desc">Show but don't save</span>
                </button>
                <button
                  className="mode-option"
                  onClick={() => {
                    setScreenShareMode('consent_required');
                    handleScreenShareToggle('consent_required');
                  }}
                >
                  🔐 Consent Required
                  <span className="mode-desc">Prompt before storing sensitive content</span>
                </button>
                <button
                  className="mode-cancel"
                  onClick={() => setShowModeSelector(false)}
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
          
          <button
            className="control-button"
            onClick={handleDocumentUpload}
            disabled={uploadLoading}
            title="Upload documents"
          >
            {uploadLoading ? '⏳ Uploading...' : '📄 Upload Docs'}
          </button>
          
          <button
            className="control-button"
            onClick={() => setFileExplorerOpen(true)}
            title="Browse memory files"
          >
            📁 Files
          </button>
          
          <button
            className="control-button"
            onClick={() => setTasksOpen(true)}
            title="View background tasks"
          >
            📋 Tasks
          </button>
          
          <button
            className="control-button"
            onClick={() => setHistoryOpen(true)}
            title="Search conversation history"
          >
            🔍 History
          </button>
          
          <button
            className="control-button"
            onClick={() => setCockpitOpen(!cockpitOpen)}
            title="Open remote cockpit"
          >
            🎛️ Cockpit
          </button>
          
          <button
            className="control-button mission-control-btn"
            onClick={() => setMissionControlOpen(true)}
            title="Open Mission Control Dashboard"
          >
            🎯 Mission Control
          </button>
          
        <button
          className="control-button mentor-btn"
          onClick={() => setMentorOpen(true)}
          title="Consult Local Mentors"
        >
          🧙 Mentors
        </button>
      </div>
    </>
  );

  return (
    <AppShell
      topBar={
        <TopBar
          title="🤖 GRACE"
          mode={graceMode}
          onModeChange={setGraceMode}
          onSelfHealing={() => console.log('Trigger self-healing')}
        />
      }
      leftSidebar={
        <LeftSidebar
          items={navItems}
          activeId={activeView}
          onSelect={(id) => setActiveView(id as typeof activeView)}
          logo={logo}
          controls={sidebarControls}
        />
      }
      rightSidebar={
        <RightSidebar
          contextPanel={<ContextPanel />}
          memoryPanel={<MemoryPanel />}
          logsPanel={<LogsPanel />}
          governancePanel={<GovernancePanel />}
        />
      }
      bottomBar={
        <BottomStatusBar
          statusText="Ready"
          loopState="Idle"
          gpuUsage={0}
          healthStatus="healthy"
        />
      }
    >
      {renderMainView()}
      
      <RemoteCockpit isOpen={cockpitOpen} onClose={() => setCockpitOpen(false)} />
      <BackgroundTasksDrawer isOpen={tasksOpen} onClose={() => setTasksOpen(false)} />
      <HistorySearch 
        isOpen={historyOpen} 
        onClose={() => setHistoryOpen(false)}
        onSelectSession={(sessionId) => console.log('Selected session:', sessionId)}
      />
      <FileExplorer isOpen={fileExplorerOpen} onClose={() => setFileExplorerOpen(false)} />
      <MissionControlDashboard isOpen={missionControlOpen} onClose={() => setMissionControlOpen(false)} />
      <MentorRoundtable isOpen={mentorOpen} onClose={() => setMentorOpen(false)} />
    </AppShell>
  );
}

export default AppChat;
