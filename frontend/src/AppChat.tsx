/**
 * Grace Chat Application
 * 
 * Minimal chat interface with health monitoring
 */

import React, { useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { HealthMeter } from './components/HealthMeter';
import { RemoteCockpit } from './components/RemoteCockpit';
import './AppChat.css';

function AppChat() {
  const [cockpitOpen, setCockpitOpen] = useState(false);

  return (
    <div className="app-chat">
      <div className="app-sidebar">
        <div className="app-logo">
          <h1>🤖 GRACE</h1>
          <p>AI Assistant with Governance</p>
        </div>
        <HealthMeter />
        <button
          className="cockpit-toggle"
          onClick={() => setCockpitOpen(!cockpitOpen)}
        >
          🎛️ Remote Cockpit
        </button>
      </div>
      <div className="app-main">
        <ChatPanel />
      </div>
      <RemoteCockpit isOpen={cockpitOpen} onClose={() => setCockpitOpen(false)} />
    </div>
  );
}

export default AppChat;
