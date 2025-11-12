/**
 * Grace VS Code Style Interface
 * Complete IDE-like experience with sidebar, chat, and panels
 */

import { useState } from 'react';
import { 
  MessageSquare, FileText, Settings, Activity, Database, 
  GitBranch, Terminal, X, Menu, ChevronRight, Layers
} from 'lucide-react';
import { GraceChat } from './GraceChat';
import { MemoryWorkspace } from './components/MemoryWorkspace';
import { MemoryBrowser } from './components/MemoryBrowser';

type View = 'chat' | 'memory' | 'tasks' | 'verification' | 'metrics' | 'settings';

export default function GraceVSCode() {
  const [activeView, setActiveView] = useState<View>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [bottomPanelOpen, setBottomPanelOpen] = useState(false);

  return (
    <div className="flex h-screen bg-[#1e1e1e] text-gray-100">
      {/* Activity Bar (Left) */}
      <div className="w-12 bg-[#333333] flex flex-col items-center py-2 space-y-1">
        <button
          onClick={() => { setActiveView('chat'); setSidebarOpen(true); }}
          className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
            activeView === 'chat' ? 'bg-[#1e1e1e] border-l-2 border-blue-500' : 'hover:bg-[#2a2a2a]'
          }`}
          title="Chat"
        >
          <MessageSquare className="w-5 h-5" />
        </button>

        <button
          onClick={() => { setActiveView('memory'); setSidebarOpen(true); }}
          className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
            activeView === 'memory' ? 'bg-[#1e1e1e] border-l-2 border-blue-500' : 'hover:bg-[#2a2a2a]'
          }`}
          title="Memory"
        >
          <Database className="w-5 h-5" />
        </button>

        <button
          onClick={() => { setActiveView('tasks'); setSidebarOpen(true); }}
          className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
            activeView === 'tasks' ? 'bg-[#1e1e1e] border-l-2 border-blue-500' : 'hover:bg-[#2a2a2a]'
          }`}
          title="Tasks"
        >
          <FileText className="w-5 h-5" />
        </button>

        <button
          onClick={() => { setActiveView('verification'); setSidebarOpen(true); }}
          className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
            activeView === 'verification' ? 'bg-[#1e1e1e] border-l-2 border-blue-500' : 'hover:bg-[#2a2a2a]'
          }`}
          title="Verification"
        >
          <GitBranch className="w-5 h-5" />
        </button>

        <button
          onClick={() => { setActiveView('metrics'); setSidebarOpen(true); }}
          className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
            activeView === 'metrics' ? 'bg-[#1e1e1e] border-l-2 border-blue-500' : 'hover:bg-[#2a2a2a]'
          }`}
          title="Metrics"
        >
          <Activity className="w-5 h-5" />
        </button>

        <div className="flex-1" />

        <button
          onClick={() => { setActiveView('settings'); setSidebarOpen(true); }}
          className={`w-10 h-10 flex items-center justify-center rounded transition-colors ${
            activeView === 'settings' ? 'bg-[#1e1e1e] border-l-2 border-blue-500' : 'hover:bg-[#2a2a2a]'
          }`}
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>

      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-64 bg-[#252526] border-r border-[#3e3e42] flex flex-col">
          <div className="p-3 border-b border-[#3e3e42] flex items-center justify-between">
            <h2 className="font-semibold text-sm uppercase tracking-wide text-gray-400">
              {activeView}
            </h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-400 hover:text-gray-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-3">
            {activeView === 'chat' && <ChatSidebar />}
            {activeView === 'memory' && <MemorySidebar />}
            {activeView === 'tasks' && <TasksSidebar />}
            {activeView === 'verification' && <VerificationSidebar />}
            {activeView === 'metrics' && <MetricsSidebar />}
            {activeView === 'settings' && <SettingsSidebar />}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="h-12 bg-[#252526] border-b border-[#3e3e42] flex items-center px-4 gap-2">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-400 hover:text-gray-200"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium">Grace AI - {activeView}</span>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          <GraceChat />
        </div>

        {/* Bottom Panel (Optional) */}
        {bottomPanelOpen && (
          <div className="h-64 bg-[#1e1e1e] border-t border-[#3e3e42] p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold">Terminal</h3>
              <button onClick={() => setBottomPanelOpen(false)}>
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="font-mono text-xs text-green-400">
              $ grace --status
              <br />
              Grace AI is operational
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Sidebar Components
function ChatSidebar() {
  return (
    <div className="space-y-2 text-sm">
      <button className="w-full text-left px-3 py-2 rounded hover:bg-[#2a2d2e] flex items-center gap-2">
        <ChevronRight className="w-3 h-3" />
        <span>New Chat</span>
      </button>
      <div className="text-xs text-gray-500 px-3 py-1">Recent</div>
      <div className="text-xs text-gray-600 px-3 py-2">No recent chats</div>
    </div>
  );
}

function MemorySidebar() {
  return (
    <div className="h-full flex flex-col">
      <div className="text-xs text-gray-500 mb-2 px-2">Memory Workspace</div>
      <div className="flex-1 overflow-hidden">
        <MemoryWorkspaceIntegrated />
      </div>
    </div>
  );
}

function MemoryWorkspaceIntegrated() {
  const [view, setView] = useState<'browser' | 'workspace'>('workspace');
  
  return (
    <div className="h-full flex flex-col bg-[#1e1e1e]">
      <div className="flex gap-2 p-2 border-b border-gray-700">
        <button
          onClick={() => setView('workspace')}
          className={`px-3 py-1 text-xs rounded ${
            view === 'workspace' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
          }`}
        >
          Files
        </button>
        <button
          onClick={() => setView('browser')}
          className={`px-3 py-1 text-xs rounded ${
            view === 'browser' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
          }`}
        >
          Artifacts
        </button>
      </div>
      <div className="flex-1 overflow-hidden">
        {view === 'workspace' ? <MemoryWorkspace /> : <MemoryBrowser />}
      </div>
    </div>
  );
}

function TasksSidebar() {
  return (
    <div className="text-sm">
      <div className="text-xs text-gray-500 mb-2">Active Tasks</div>
      <div className="space-y-1">
        <div className="px-2 py-1 text-xs">Loading...</div>
      </div>
    </div>
  );
}

function VerificationSidebar() {
  return (
    <div className="text-sm">
      <div className="text-xs text-gray-500 mb-2">Recent Verifications</div>
      <div className="space-y-1">
        <div className="px-2 py-1 text-xs">Loading...</div>
      </div>
    </div>
  );
}

function MetricsSidebar() {
  return (
    <div className="text-sm">
      <div className="text-xs text-gray-500 mb-2">System Metrics</div>
      <div className="space-y-1">
        <div className="px-2 py-1 text-xs">Loading...</div>
      </div>
    </div>
  );
}

function SettingsSidebar() {
  return (
    <div className="text-sm">
      <div className="text-xs text-gray-500 mb-2">Settings</div>
      <div className="space-y-2">
        <div className="px-2 py-1 text-xs">API Base: http://localhost:8000</div>
        <div className="px-2 py-1 text-xs">Show Traces: Enabled</div>
      </div>
    </div>
  );
}
