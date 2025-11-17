/**
 * Verification Script
 * Checks all required files are in place
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Grace Console - Implementation Verification\n');

const requiredFiles = {
  'Core Panels': [
    'src/panels/ChatPane.tsx',
    'src/panels/TaskManager.tsx',
    'src/panels/MemoryExplorer.tsx',
    'src/panels/LogsPane.tsx',
    'src/panels/WorkspaceManager.tsx',
    'src/panels/GovernanceConsole.tsx',
    'src/panels/MCPToolsPanel.tsx',
  ],
  'Hooks': [
    'src/hooks/useChat.ts',
    'src/hooks/useMissions.ts',
    'src/hooks/useMemoryArtifacts.ts',
    'src/hooks/useWorkspaces.ts',
  ],
  'Services': [
    'src/services/chatApi.ts',
    'src/services/missionApi.ts',
    'src/services/memoryApi.complete.ts',
    'src/services/governanceApi.ts',
    'src/services/mcpApi.ts',
    'src/services/worldModelApi.ts',
  ],
  'Types': [
    'src/types/memory.types.ts',
  ],
  'Workspace Components': [
    'src/components/workspaces/MissionDetailWorkspace.tsx',
    'src/components/workspaces/DashboardWorkspace.tsx',
    'src/components/workspaces/ArtifactViewerWorkspace.tsx',
  ],
  'Main Shell': [
    'src/GraceConsole.tsx',
    'src/main.tsx',
  ],
  'Documentation': [
    'INDEX.md',
    'START_HERE.md',
    'QUICK_START_CONSOLE.md',
    'GRACE_CONSOLE_COMPLETE.md',
  ],
};

let totalFiles = 0;
let foundFiles = 0;
let missingFiles = [];

console.log('Checking required files...\n');

for (const [category, files] of Object.entries(requiredFiles)) {
  console.log(`📁 ${category}:`);
  
  for (const file of files) {
    totalFiles++;
    const filePath = path.join(__dirname, file);
    
    if (fs.existsSync(filePath)) {
      console.log(`  ✅ ${file}`);
      foundFiles++;
    } else {
      console.log(`  ❌ ${file} - MISSING`);
      missingFiles.push(file);
    }
  }
  console.log('');
}

console.log('━'.repeat(60));
console.log(`\n📊 Summary:`);
console.log(`   Total files checked: ${totalFiles}`);
console.log(`   Found: ${foundFiles}`);
console.log(`   Missing: ${missingFiles.length}`);
console.log('');

if (missingFiles.length === 0) {
  console.log('✅ ALL FILES PRESENT!');
  console.log('');
  console.log('🎉 Grace Console is ready to launch!');
  console.log('');
  console.log('To start:');
  console.log('  npm run dev');
  console.log('');
  console.log('Then open: http://localhost:5173');
  console.log('');
  process.exit(0);
} else {
  console.log('⚠️  Some files are missing:');
  missingFiles.forEach(file => console.log(`   - ${file}`));
  console.log('');
  console.log('These files may be optional or using different names.');
  console.log('Check the documentation for details.');
  console.log('');
  process.exit(1);
}
