import React from 'react';
import { ChatPanel } from './components/ChatPanel';

/**
 * Minimal Grace UI
 * 
 * Single-panel chat interface for:
 * - Conversing with Grace (via World Model)
 * - Uploading files (books, APIs, etc.)
 * - Approving governance actions
 * - Viewing logs and system status
 * - Persistent voice sessions
 * 
 * World Model Integration:
 * - Uses /api/world_model_hub/chat endpoint
 * - Grace's world model handles context, memory, reasoning
 * - Approvals flow through /api/world_model_hub/approve
 */
export default function App() {
  return (
    <div style={{ height: '100vh', background: '#1a1a1a' }}>
      <ChatPanel />
    </div>
  );
}
