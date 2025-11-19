/**
 * Grace App - Simplified Tab-Based Architecture
 */

import { useState } from 'react';
import { Tabs, type Tab } from './components/Tabs';
import OverviewTab from './tabs/OverviewTab';
import ChatTab from './tabs/ChatTab';
import ClarityTab from './tabs/ClarityTab';
import LLMTab from './tabs/LLMTab';
import IntelligenceTab from './tabs/IntelligenceTab';
import IngestionTab from './tabs/IngestionTab';
import LearningTab from './tabs/LearningTab';
import { MemoryBrowser } from './components/MemoryBrowser';
import { HunterDashboard } from './components/HunterDashboard';
import { KnowledgeManager } from './components/Knowledge/KnowledgeManager';
import { MetaLoopDashboard } from './components/MetaLoopDashboard';
import { ApprovalsAdmin } from './components/Governance/ApprovalsAdmin';
import { AgenticDashboard } from './components/AgenticDashboard';
import { TranscendenceIDE } from './components/TranscendenceIDE';

const s = {
  bg: '#0a0a0a',
  fg: '#e0e0e0',
  ac: '#8b5cf6',
  ac2: '#a78bfa',
};

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [token, setToken] = useState(localStorage.getItem('token') || '');

  // Define all tabs
  const tabs: Tab[] = [
    { key: 'overview', label: 'Overview', icon: '📊', element: <OverviewTab /> },
    { key: 'chat', label: 'Chat', icon: '💬', element: <ChatTab /> },
    { key: 'clarity', label: 'Clarity', icon: '🔍', element: <ClarityTab /> },
    { key: 'llm', label: 'LLM', icon: '🧠', element: <LLMTab /> },
    { key: 'intelligence', label: 'Intel', icon: '💡', element: <IntelligenceTab /> },
    { key: 'ingestion', label: 'Ingest', icon: '📥', element: <IngestionTab /> },
    { key: 'learning', label: 'Learn', icon: '🎓', element: <LearningTab /> },
    { key: 'memory', label: 'Memory', icon: '📁', element: <MemoryBrowser /> },
    { key: 'hunter', label: 'Hunter', icon: '🛡️', element: <HunterDashboard /> },
    { key: 'knowledge', label: 'Knowledge', icon: '📚', element: <KnowledgeManager /> },
    { key: 'metaloop', label: 'Meta', icon: '🔮', element: <MetaLoopDashboard /> },
    { key: 'approvals', label: 'Approvals', icon: '✅', element: <ApprovalsAdmin /> },
    { key: 'agentic', label: 'Agentic', icon: '🤖', element: <AgenticDashboard /> },
    { key: 'ide', label: 'IDE', icon: '💻', element: <TranscendenceIDE /> },
  ];

  const currentTab = tabs.find((t) => t.key === activeTab) || tabs[0];

  // Simple login check
  if (!token) {
    return (
      <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: s.fg }}>
        <div style={{ background: '#1a1a1a', padding: '2rem', borderRadius: '12px', maxWidth: '400px', width: '100%' }}>
          <h1 style={{ color: s.ac2, marginBottom: '1.5rem', textAlign: 'center' }}>Grace Login</h1>
          <button
            onClick={() => {
              // Simple bypass for development
              setToken('dev-token');
              localStorage.setItem('token', 'dev-token');
            }}
            style={{
              width: '100%',
              background: s.ac,
              color: '#fff',
              border: 'none',
              padding: '1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '1rem',
            }}
          >
            Enter Grace
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: s.bg, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ padding: '1rem', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ color: s.ac2, margin: 0, fontSize: '1.5rem' }}>Grace Control Center</h1>
        <button
          onClick={() => {
            setToken('');
            localStorage.clear();
            window.location.reload();
          }}
          style={{
            background: '#333',
            color: s.fg,
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          Logout
        </button>
      </div>

      {/* Tabs Navigation */}
      <Tabs tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Tab Content */}
      <main style={{ flex: 1, overflow: 'auto' }}>
        {currentTab.element}
      </main>
    </div>
  );
}
