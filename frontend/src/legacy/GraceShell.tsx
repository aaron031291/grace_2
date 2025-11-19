/**
 * Grace Shell - ChatGPT-style Layout
 * Left sidebar navigation + main content panel
 */

import { useState } from 'react';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';
import FloatingVoiceWidget from './components/FloatingVoiceWidget';
import ContextualSidecar from './components/ContextualSidecar';
import './GraceShell.css';

export interface NavItem {
  type: 'kernel' | 'function';
  id: string;
  label?: string;
}

export default function GraceShell() {
  const [selected, setSelected] = useState<NavItem>({ type: 'kernel', id: 'memory_fusion' });

  return (
    <div className="grace-shell">
      <Sidebar selected={selected} onSelect={setSelected} />
      <main className="grace-main">
        <MainPanel item={selected} />
      </main>
      
      {/* Persistent voice widget - stays active across all panels */}
      <FloatingVoiceWidget />
      
      {/* Contextual sidecar - intelligent, non-intrusive context */}
      <ContextualSidecar />
    </div>
  );
}
