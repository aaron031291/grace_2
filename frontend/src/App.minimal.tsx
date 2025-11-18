import React from 'react';
import { ChatPanel } from './components/ChatPanel';

/**
 * Minimal Grace UI
 * 
 * Single-panel chat interface for:
 * - Conversing with Grace
 * - Uploading files (books, APIs, etc.)
 * - Approving governance actions
 * - Viewing logs and system status
 * - Persistent voice sessions
 */
export default function App() {
  return <ChatPanel />;
}
