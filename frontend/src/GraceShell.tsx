/**
 * Grace Shell - ChatGPT-style Layout
 * Left sidebar navigation + main content panel
 */

import { useState } from 'react';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';
import './GraceShell.css';

export interface NavItem {
  type: 'kernel' | 'function';
  id: string;
  label?: string;
}

export default function GraceShell() {
  const [selected, setSelected] = useState<NavItem>({ type: 'function', id: 'overview' });

  return (
    <div className="grace-shell">
      <Sidebar selected={selected} onSelect={setSelected} />
      <main className="grace-main">
        <MainPanel item={selected} />
      </main>
    </div>
  );
}
