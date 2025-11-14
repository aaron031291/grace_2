/**
 * Main Panel - Routes to appropriate panel based on selection
 */

import type { NavItem } from '../GraceShell';
import SystemArchitecture from './SystemArchitecture';
import VoiceConversation from './VoiceConversation';
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
  // Simple kernel routing - no SystemArchitecture component
  switch (item.id) {
    // Execution Layer
    case 'memory_fusion':
      return <MemoryWorkspace />;
    case 'librarian':
      return <IngestionTab />;
    case 'self_healing':
      return <HealthDashboard />;
    case 'coding_agent':
      return <ChatTab />;
    
    // Layer 3 - Agentic
    case 'agentic_spine':
      return <AgenticDashboard />;
    case 'voice_conversation':
      return <VoiceConversation />;
    case 'meta_loop':
      return <LearningTab />;
    case 'learning_integration':
      return <IntelligenceTab />;
    
    // Default for all other kernels
    default:
      return <ClarityTab />;
  }
}
