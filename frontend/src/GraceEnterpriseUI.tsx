import { useState, useEffect } from 'react';
import { CommandPalette } from './components/CommandPalette';
import { ExecutionTracePanel } from './components/ExecutionTracePanel';
import { HealthBar } from './components/HealthBar';
import { LeftSidebar } from './components/LeftSidebar';
import { ChatView } from './components/ChatView';
import { GlobalSearch } from './components/GlobalSearch';
import { GuardianWorkspace } from './components/workspaces/GuardianWorkspace';
import { CopilotWorkspace } from './components/workspaces/CopilotWorkspace';
import { GovernanceWorkspace } from './components/workspaces/GovernanceWorkspace';
import { LearningWorkspace } from './components/workspaces/LearningWorkspace';
import { MissionWorkspace } from './components/workspaces/MissionWorkspace';
import { MemoryWorkspace } from './components/workspaces/MemoryWorkspace';
import { ObservatoryWorkspace } from './components/workspaces/ObservatoryWorkspace';
import { TerminalWorkspace } from './components/workspaces/TerminalWorkspace';
import { AgenticWorkspace } from './components/workspaces/AgenticWorkspace';
import { WorldModelHub } from './components/workspaces/WorldModelHub';
import { Phase8Workspace } from './components/workspaces/Phase8Workspace';
import { MissionDesignerCanvas } from './components/MissionDesignerCanvas';
import { ApprovalInbox } from './components/ApprovalInbox';
import { LearningJobsDashboard } from './components/LearningJobsDashboard';
import './GraceEnterpriseUI.css';

export type Capability = 
  | 'guardian' 
  | 'self-healing' 
  | 'copilot' 
  | 'world-model' 
  | 'learning' 
  | 'governance' 
  | 'mission-control' 
  | 'observatory' 
  | 'memory' 
  | 'terminal'
  | 'agentic'
  | 'phase8'
  | 'mission-designer'
  | 'approval-inbox'
  | 'learning-jobs';

export interface Workspace {
  id: string;
  type: Capability;
  title: string;
  context?: any;
  createdAt: Date;
}

export interface ExecutionTrace {
  request_id: string;
  steps: ExecutionStep[];
  duration_ms: number;
  data_sources_used: string[];
  agents_involved: string[];
}

export interface ExecutionStep {
  component: string;
  action: string;
  duration_ms: number;
  data_source?: string;
  result?: any;
}

export interface HealthMetrics {
  health: number;
  trust: number;
  confidence: number;
  domains?: Record<string, number>;
}

export default function GraceEnterpriseUI() {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [executionTracePanelOpen, setExecutionTracePanelOpen] = useState(false);
  const [globalSearchOpen, setGlobalSearchOpen] = useState(false);
  const [selectedTrace, setSelectedTrace] = useState<ExecutionTrace | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  const [activeCapability, setActiveCapability] = useState<Capability | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);
  
  const [systemHealth, setSystemHealth] = useState<HealthMetrics>({
    health: 79,
    trust: 75,
    confidence: 73
  });

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setGlobalSearchOpen(prev => !prev);
      }
      
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
      }
      
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        setSidebarCollapsed(prev => !prev);
      }
      
      if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
        setExecutionTracePanelOpen(false);
        setGlobalSearchOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch('http://localhost:8054/api/metrics/summary');
        const data = await response.json();
        if (data.success) {
          setSystemHealth({
            health: data.data.health || 79,
            trust: data.data.trust || 75,
            confidence: data.data.confidence || 73,
            domains: data.data.domains
          });
        }
      } catch (error) {
        console.error('Failed to fetch health metrics:', error);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Workspace management
  const createWorkspace = (type: Capability, context?: any) => {
    const workspace: Workspace = {
      id: `ws-${Date.now()}`,
      type,
      title: getCapabilityTitle(type),
      context,
      createdAt: new Date()
    };
    setWorkspaces(prev => [...prev, workspace]);
    setActiveWorkspace(workspace);
    setActiveCapability(null); // Clear capability when workspace is active
  };

  const closeWorkspace = (id: string) => {
    setWorkspaces(prev => prev.filter(ws => ws.id !== id));
    if (activeWorkspace?.id === id) {
      setActiveWorkspace(null);
    }
  };

  const switchWorkspace = (workspace: Workspace) => {
    setActiveWorkspace(workspace);
    setActiveCapability(null);
  };

  const showExecutionTrace = (trace: ExecutionTrace) => {
    setSelectedTrace(trace);
    setExecutionTracePanelOpen(true);
  };

  const renderActiveView = () => {
    if (activeWorkspace) {
      switch (activeWorkspace.type) {
        case 'guardian':
          return <GuardianWorkspace workspace={activeWorkspace} />;
        case 'copilot':
          return <CopilotWorkspace workspace={activeWorkspace} />;
        case 'governance':
          return <GovernanceWorkspace workspace={activeWorkspace} />;
        case 'learning':
          return <LearningWorkspace workspace={activeWorkspace} />;
        case 'mission-control':
          return <MissionWorkspace workspace={activeWorkspace} />;
        case 'memory':
          return <MemoryWorkspace workspace={activeWorkspace} />;
        case 'observatory':
          return <ObservatoryWorkspace workspace={activeWorkspace} />;
        case 'terminal':
          return <TerminalWorkspace workspace={activeWorkspace} />;
        case 'world-model':
          return <WorldModelHub 
            workspace={activeWorkspace} 
            onShowTrace={(traceId) => {
              fetch(`http://localhost:8054/api/world_model_hub/trace/${traceId}`)
                .then(res => res.json())
                .then(data => {
                  setSelectedTrace({
                    request_id: traceId,
                    steps: data.events.map((e: any) => ({
                      component: e.source,
                      action: e.event_type,
                      duration_ms: 0,
                      result: e.data
                    })),
                    duration_ms: 0,
                    data_sources_used: [],
                    agents_involved: data.actions.map((a: any) => a.agent)
                  });
                  setExecutionTracePanelOpen(true);
                });
            }}
            onCreateWorkspace={(type: string, context?: any) => {
              createWorkspace(type as Capability, context);
            }}
          />;
        case 'agentic':
          return <AgenticWorkspace workspace={activeWorkspace} onShowTrace={(traceId) => {
            fetch(`http://localhost:8054/api/agentic/trace/${traceId}`)
              .then(res => res.json())
              .then(data => {
                setSelectedTrace({
                  request_id: traceId,
                  steps: data.events.map((e: any) => ({
                    component: e.source,
                    action: e.event_type,
                    duration_ms: 0,
                    result: e.data
                  })),
                  duration_ms: 0,
                  data_sources_used: [],
                  agents_involved: data.actions.map((a: any) => a.agent)
                });
                setExecutionTracePanelOpen(true);
              });
          }} />;
        case 'phase8':
          return <Phase8Workspace workspace={activeWorkspace} />;
        case 'mission-designer':
          return <MissionDesignerCanvas />;
        case 'approval-inbox':
          return <ApprovalInbox />;
        case 'learning-jobs':
          return <LearningJobsDashboard />;
        default:
          return <ChatView onShowTrace={showExecutionTrace} />;
      }
    }

    if (activeCapability) {
      return (
        <div className="capability-view">
          <div className="capability-suggestion">
            <h2>🛡️ {getCapabilityTitle(activeCapability)}</h2>
            <p>Create a workspace for focused {activeCapability} work?</p>
            <button 
              className="btn-primary"
              onClick={() => createWorkspace(activeCapability)}
            >
              Create {getCapabilityTitle(activeCapability)} Workspace
            </button>
          </div>
        </div>
      );
    }

    return <ChatView onShowTrace={showExecutionTrace} />;
  };

  return (
    <div className="grace-enterprise-ui">
      {/* Top Bar */}
      <div className="top-bar">
        <div className="top-bar-left">
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? '▶' : '◀'}
          </button>
          <div className="logo">
            <span className="logo-icon">🧠</span>
            <span className="logo-text">Grace</span>
          </div>
        </div>
        
        <div className="top-bar-center">
          <div className="global-search">
            <input 
              type="text" 
              placeholder="Search chats, files, knowledge... (⌘K)" 
              className="search-input"
              onClick={() => setGlobalSearchOpen(true)}
              readOnly
            />
          </div>
        </div>
        
        <div className="top-bar-right">
          <HealthBar 
            health={systemHealth.health}
            trust={systemHealth.trust}
            confidence={systemHealth.confidence}
          />
          <button className="user-menu-btn" title="User menu">
            👤
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Left Sidebar */}
        {!sidebarCollapsed && (
          <LeftSidebar
            activeCapability={activeCapability}
            activeWorkspace={activeWorkspace}
            workspaces={workspaces}
            onCapabilityClick={setActiveCapability}
            onWorkspaceClick={switchWorkspace}
            onWorkspaceClose={closeWorkspace}
            onCreateWorkspace={createWorkspace}
            onCommandPaletteOpen={() => setCommandPaletteOpen(true)}
          />
        )}

        {/* Main Area */}
        <div className="main-area">
          {renderActiveView()}
        </div>
      </div>

      {/* Command Palette */}
      {commandPaletteOpen && (
        <CommandPalette
          onClose={() => setCommandPaletteOpen(false)}
          onExecute={(action) => {
            console.log('Execute action:', action);
            setCommandPaletteOpen(false);
          }}
        />
      )}

      {/* Execution Trace Panel */}
      {executionTracePanelOpen && selectedTrace && (
        <ExecutionTracePanel
          trace={selectedTrace}
          onClose={() => setExecutionTracePanelOpen(false)}
        />
      )}

      {/* Global Search */}
      <GlobalSearch
        isOpen={globalSearchOpen}
        onClose={() => setGlobalSearchOpen(false)}
        onSelect={(result) => {
          console.log('Selected:', result);
        }}
      />
    </div>
  );
}

function getCapabilityTitle(capability: Capability): string {
  const titles: Record<Capability, string> = {
    'guardian': 'Guardian',
    'self-healing': 'Self-Healing',
    'copilot': 'Copilot',
    'world-model': 'World Model',
    'learning': 'Learning Engine',
    'governance': 'Governance',
    'mission-control': 'Mission Control',
    'observatory': 'Observatory',
    'memory': 'Memory',
    'terminal': 'Terminal',
    'agentic': 'Agentic Organism',
    'phase8': 'Phase 8: E2E Testing & Production Readiness',
    'mission-designer': 'Mission Designer',
    'approval-inbox': 'Approval Inbox',
    'learning-jobs': 'Learning Jobs'
  };
  return titles[capability] || capability;
}
