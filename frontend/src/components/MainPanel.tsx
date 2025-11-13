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
import { SelfHealingPanel } from './SelfHealingPanel';
import { IncidentPanel } from './IncidentPanel';
import { HealthDashboard } from './HealthDashboard';

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
      return <HealthDashboard />;
    default:
      return <OverviewTab />;
  }
}
