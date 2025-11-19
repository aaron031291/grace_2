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
import { ModelLearningPanel } from './ModelLearningPanel';

interface MainPanelProps {
  item: NavItem;
}

export default function MainPanel({ item }: MainPanelProps) {
  // Simple kernel routing - no SystemArchitecture component
  switch (item.id) {
    // Core Infrastructure - Secret Manager
    case 'secret_manager':
      return (
        <div style={{ padding: '2rem', color: '#e0e0e0', background: '#0a0a0a', minHeight: '100vh' }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>🔐 Secret Manager</h1>
          <p style={{ color: '#888', marginBottom: '2rem' }}>Secure credential storage and management</p>
          
          <div style={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: '8px', padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Status</h2>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Encrypted Secrets:</span>
                <span style={{ color: '#10b981', fontWeight: 'bold' }}>45</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Encryption:</span>
                <span style={{ color: '#10b981', fontWeight: 'bold' }}>Fernet AES-256</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Status:</span>
                <span style={{ color: '#10b981', fontWeight: 'bold' }}>Operational</span>
              </div>
            </div>
          </div>
        </div>
      );
    
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
      return <ModelLearningPanel />;
    
    // Default for all other kernels
    default:
      return <ClarityTab />;
  }
}
