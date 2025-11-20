import React, { useState } from 'react';
import './RightSidebar.css';

export type TabId = 'context' | 'memory' | 'logs';

type RightSidebarProps = {
  contextPanel: React.ReactNode;
  memoryPanel: React.ReactNode;
  logsPanel: React.ReactNode;
};

export const RightSidebar: React.FC<RightSidebarProps> = ({
  contextPanel,
  memoryPanel,
  logsPanel,
}) => {
  const [tab, setTab] = useState<TabId>('context');

  return (
    <div className="right-sidebar">
      <div className="right-sidebar-tabs">
        {(['context', 'memory', 'logs'] as TabId[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`tab-btn ${tab === t ? 'active' : ''}`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="right-sidebar-content">
        {tab === 'context' && contextPanel}
        {tab === 'memory' && memoryPanel}
        {tab === 'logs' && logsPanel}
      </div>
    </div>
  );
};
