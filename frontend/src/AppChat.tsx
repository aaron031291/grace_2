/**
 * Grace Chat Application
 * 
 * Minimal chat interface with health monitoring
 */

import { useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { HealthMeter } from './components/HealthMeter';
import { RemoteCockpit } from './components/RemoteCockpit';
import { BackgroundTasksDrawer } from './components/BackgroundTasksDrawer';
import { TelemetryStrip } from './components/TelemetryStrip';
import { RemoteAPI } from './api/remote';
import './AppChat.css';

function AppChat() {
  const [cockpitOpen, setCockpitOpen] = useState(false);
  const [tasksOpen, setTasksOpen] = useState(false);
  const [remoteActive, setRemoteActive] = useState(false);
  const [screenShareActive, setScreenShareActive] = useState(false);
  const [remoteSessionId, setRemoteSessionId] = useState<string | null>(null);
  const [screenShareSessionId, setScreenShareSessionId] = useState<string | null>(null);

  const handleRemoteToggle = async () => {
    if (remoteActive) {
      if (remoteSessionId) {
        await RemoteAPI.stopRemoteAccess(remoteSessionId);
        setRemoteSessionId(null);
      }
      setRemoteActive(false);
    } else {
      const response = await RemoteAPI.startRemoteAccess('supervised');
      if (response.session_id || response.trace_id) {
        setRemoteSessionId(response.session_id || response.trace_id);
        setRemoteActive(true);
      }
    }
  };

  const handleScreenShareToggle = async () => {
    if (screenShareActive) {
      if (screenShareSessionId) {
        await RemoteAPI.stopScreenShare(screenShareSessionId);
        setScreenShareSessionId(null);
      }
      setScreenShareActive(false);
    } else {
      const response = await RemoteAPI.startScreenShare('medium');
      if (response.session_id) {
        setScreenShareSessionId(response.session_id);
        setScreenShareActive(true);
      }
    }
  };

  const handleDocumentUpload = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.onchange = async (e: any) => {
      const files = Array.from(e.target.files || []) as File[];
      for (const file of files) {
        try {
          await RemoteAPI.uploadDocument(file);
          alert(`✅ Uploaded: ${file.name}`);
        } catch (error) {
          alert(`❌ Failed to upload ${file.name}: ${error}`);
        }
      }
    };
    input.click();
  };

  return (
    <div className="app-chat">
      <div className="app-sidebar">
        <div className="app-logo">
          <h1>🤖 GRACE</h1>
          <p>AI Assistant with Governance</p>
        </div>
        
        <HealthMeter />
        
        <div className="sidebar-controls">
          <h3>Quick Controls</h3>
          
          <button
            className={`control-button ${remoteActive ? 'active' : ''}`}
            onClick={handleRemoteToggle}
            title="Toggle remote access"
          >
            {remoteActive ? '🔓 Remote Active' : '🔒 Remote Access'}
          </button>
          
          <button
            className={`control-button ${screenShareActive ? 'active' : ''}`}
            onClick={handleScreenShareToggle}
            title="Toggle screen share"
          >
            {screenShareActive ? '📺 Sharing Screen' : '📺 Screen Share'}
          </button>
          
          <button
            className="control-button"
            onClick={handleDocumentUpload}
            title="Upload documents"
          >
            📄 Upload Docs
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
            onClick={() => setCockpitOpen(!cockpitOpen)}
            title="Open remote cockpit"
          >
            🎛️ Cockpit
          </button>
        </div>
      </div>
      
      <div className="app-main">
        <TelemetryStrip />
        <ChatPanel />
      </div>
      
      <RemoteCockpit isOpen={cockpitOpen} onClose={() => setCockpitOpen(false)} />
      <BackgroundTasksDrawer isOpen={tasksOpen} onClose={() => setTasksOpen(false)} />
    </div>
  );
}

export default AppChat;
