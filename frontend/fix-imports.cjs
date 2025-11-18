const fs = require('fs');
const path = require('path');

// Files and their correct import paths
const fixes = [
  // API files (one level deep)
  { file: 'src/api/client.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/api/comprehensive.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/api/factory.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/api/librarian.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/api/memory.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/api/phase8Api.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  
  // Components (one level deep)
  { file: 'src/components/AgenticBuilderForm.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/AllKernelsPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/ApprovalModal.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/AutomationRulesPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/BookLibraryPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/BusinessMetrics.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/ChatView.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/CodingAgentAnalytics.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/CognitiveObservatory.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/CollaborationDashboard.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/CommandPalette.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/Complete12KernelsPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/ContextualSidecar.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/CoPilotPane.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/Dashboard.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/FileOrganizerPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/FileTreeWorking.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/FloatingVoiceWidget.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/GraceActivityFeed.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/GraceCopilot.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/GraceCopilotSidebar.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/GraceGPT.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/GraceOverview.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/HealthDashboard.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/HunterDashboard.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/KernelTerminal.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/KnowledgeIngestion.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/LibrarianCopilot.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/MemoryBrowser.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/MemoryPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/MemoryWorkspace.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/MetaLoopDashboard.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/ModelIndicator.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/ModelLearningPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/ModelsPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/NotificationCenter.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/PatchTrackingPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/SecurityRulesList.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/Sidebar.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/SystemArchitecture.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/TemplateSelector.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/TranscendenceDashboard.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/TranscendenceIDE.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/VoiceConversation.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/components/WorkflowManager.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  
  // Workspaces (two levels deep)
  { file: 'src/components/workspaces/FullStackDashboard.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../../config';` },
  { file: 'src/components/workspaces/WorldModelHub.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../../config';` },
  
  // Services (one level deep)
  { file: 'src/services/clarityApi.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/services/ingestionApi.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/services/intelligenceApi.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/services/learningApi.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/services/llmApi.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  
  // Tabs (one level deep)
  { file: 'src/tabs/ChatTab.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/tabs/OverviewTab.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  
  // Panels (one level deep)
  { file: 'src/panels/AlertsPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/panels/MemoryHubPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/panels/MemoryStudioPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/panels/SchemaApprovalPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/panels/TableEditorPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/panels/TrustDashboardPanel.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  
  // Pages (one level deep)
  { file: 'src/pages/ConnectionTestPage.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/pages/Layer1DashboardMVP.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/pages/Layer1OpsConsole.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/pages/Layer2DashboardMVP.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/pages/Layer2HTMConsole.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/pages/Layer3DashboardMVP.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/pages/Layer3IntentLearning.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  { file: 'src/pages/Layer4DevOSView.tsx', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
  
  // Utils (one level deep)
  { file: 'src/utils/notifications.ts', from: `import { apiUrl, WS_BASE_URL } from './config';`, to: `import { apiUrl, WS_BASE_URL } from '../config';` },
];

let fixedCount = 0;

fixes.forEach(({ file, from, to }) => {
  const filePath = path.join(__dirname, file);
  
  try {
    if (!fs.existsSync(filePath)) {
      console.log(`⚠️ File not found: ${file}`);
      return;
    }
    
    let content = fs.readFileSync(filePath, 'utf8');
    if (content.includes(from)) {
      content = content.replace(from, to);
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ Fixed: ${file}`);
      fixedCount++;
    }
  } catch (error) {
    console.log(`❌ Error processing ${file}:`, error.message);
  }
});

console.log(`\n✅ Fixed ${fixedCount} files`);
