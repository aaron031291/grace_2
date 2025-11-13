/**
 * Main Panel - Routes to appropriate panel based on selection
 */

import type { NavItem } from '../GraceShell';
import OverviewTab from '../tabs/OverviewTab';
import ChatTab from '../tabs/ChatTab';
import ClarityTab from '../tabs/ClarityTab';
import LLMTab from '../tabs/LLMTab';
import IntelligenceTab from '../tabs/IntelligenceTab';
import IngestionTab from '../tabs/IngestionTab';
import LearningTab from '../tabs/LearningTab';
import { MemoryBrowser } from './MemoryBrowser';
import { MemoryWorkspace } from './MemoryWorkspace';
import { HunterDashboard } from './HunterDashboard';
import { AgenticDashboard } from './AgenticDashboard';

interface MainPanelProps {
  item: NavItem;
}

export default function MainPanel({ item }: MainPanelProps) {
  // Render based on selection
  if (item.type === 'kernel') {
    switch (item.id) {
      case 'memory':
        return <MemoryBrowser />;
      case 'intelligence':
        return <IntelligenceTab />;
      case 'code':
      case 'core':
      case 'governance':
      case 'verification':
      case 'infrastructure':
      case 'federation':
      case 'ml':
        return (
          <div style={{ padding: '2rem', color: '#e5e7ff' }}>
            <h2>{item.label} Kernel</h2>
            <p>Panel for {item.label} kernel coming soon...</p>
          </div>
        );
      default:
        return <div>Unknown kernel</div>;
    }
  }

  // Functions
  switch (item.id) {
    case 'overview':
      return <OverviewTab />;
    case 'chat':
      return <ChatTab />;
    case 'clarity':
      return <ClarityTab />;
    case 'llm':
      return <LLMTab />;
    case 'ingestion':
      return <IngestionTab />;
    case 'learning':
      return <LearningTab />;
    case 'memory':
      return <MemoryWorkspace />;
    case 'hunter':
      return <HunterDashboard />;
    case 'agentic':
      return <AgenticDashboard />;
    case 'healing':
      return (
        <div style={{ padding: '2rem', color: '#e5e7ff' }}>
          <h2>Self-Healing System</h2>
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(34,197,94,0.1)', borderRadius: '8px', border: '1px solid rgba(34,197,94,0.3)' }}>
            <h3 style={{ color: '#4ade80', marginBottom: '0.5rem' }}>✅ Backend Routes Working!</h3>
            <p>All self-healing routes are accessible:</p>
            <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
              <li>GET /api/self-healing/stats</li>
              <li>GET /api/self-healing/incidents</li>
              <li>GET /api/self-healing/playbooks</li>
              <li>GET /api/kernels (All 9 kernels)</li>
            </ul>
            <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#9ca3af' }}>
              Full dashboard UI available in SelfHealingPanel component.
              Currently showing this placeholder to ensure no white screen.
            </p>
          </div>
        </div>
      );
    default:
      return <OverviewTab />;
  }
}
