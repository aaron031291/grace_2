/**
 * Grace Comprehensive Layout
 * Full-featured UI with top bar, sidebar, main content, co-pilot dock, and footer
 */

import React, { useState, useEffect } from 'react';
import {
  Search, Bell, Users, HelpCircle, Menu, Home, ChevronRight,
  Folder, File, Upload, Plus, Settings, Activity, Zap, TrendingUp
} from 'lucide-react';
import { SelfHealingPanel } from './components/SelfHealingPanel';
import { api } from './api/factory';

type Tab = 'overview' | 'memory' | 'books' | 'trusted-sources' | 'self-healing' | 'verification' | 'automation';

interface Breadcrumb {
  label: string;
  path: string;
}

export function GraceComprehensive() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([
    { label: 'Home', path: '/' },
    { label: 'Documents', path: '/documents' },
  ]);
  const [metrics, setMetrics] = useState<any>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showCoPilot, setShowCoPilot] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    loadMetrics();
    loadSystemHealth();
    const interval = setInterval(() => {
      loadMetrics();
      loadSystemHealth();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      const data = await api.system.getMetrics();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const loadSystemHealth = async () => {
    try {
      const data = await api.system.getHealth();
      setSystemHealth(data);
    } catch (error) {
      console.error('Failed to load system health:', error);
    }
  };

  const tabs = [
    { id: 'overview' as Tab, label: 'Overview', icon: Home },
    { id: 'memory' as Tab, label: 'Memory', icon: Activity },
    { id: 'books' as Tab, label: 'Books', icon: Folder },
    { id: 'trusted-sources' as Tab, label: 'Trusted Sources', icon: Settings },
    { id: 'self-healing' as Tab, label: 'Self-Healing', icon: Zap },
    { id: 'verification' as Tab, label: 'Verification', icon: TrendingUp },
    { id: 'automation' as Tab, label: 'Automation', icon: Settings },
  ];

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white">
      {/* Top Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Breadcrumbs */}
          <div className="flex items-center gap-2 text-sm">
            {breadcrumbs.map((crumb, idx) => (
              <React.Fragment key={idx}>
                <button className="text-gray-400 hover:text-white transition-colors">
                  {crumb.label}
                </button>
                {idx < breadcrumbs.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Center: Search */}
          <div className="flex-1 max-w-xl mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search or run command (Ctrl+K)..."
                className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          {/* Right: Metrics & Actions */}
          <div className="flex items-center gap-4">
            {/* Mini Metrics */}
            {metrics && (
              <div className="flex gap-3 text-xs">
                <div className="bg-gray-700 px-3 py-1.5 rounded">
                  <span className="text-gray-400">Books:</span>{' '}
                  <span className="text-cyan-400 font-semibold">{metrics.ingestion.total_ingested}</span>
                </div>
                <div className="bg-gray-700 px-3 py-1.5 rounded">
                  <span className="text-gray-400">Trust:</span>{' '}
                  <span className="text-green-400 font-semibold">{(metrics.trust_levels.average_score * 100).toFixed(0)}%</span>
                </div>
                <div className="bg-gray-700 px-3 py-1.5 rounded">
                  <span className="text-gray-400">Queue:</span>{' '}
                  <span className="text-yellow-400 font-semibold">5</span>
                </div>
              </div>
            )}

            {/* Presence */}
            <div className="flex -space-x-2">
              <div className="w-8 h-8 rounded-full bg-blue-600 border-2 border-gray-800 flex items-center justify-center text-xs font-bold">
                U
              </div>
              <div className="w-8 h-8 rounded-full bg-purple-600 border-2 border-gray-800 flex items-center justify-center text-xs font-bold">
                L
              </div>
            </div>

            {/* Notifications */}
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Bell className="w-5 h-5" />
              {notifications.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>

            {/* Help */}
            <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <HelpCircle className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
          {/* Logo */}
          <div className="px-6 py-4 border-b border-gray-700">
            <h1 className="text-xl font-bold text-cyan-400">GRACE</h1>
            <p className="text-xs text-gray-500">Autonomous AI System</p>
          </div>

          {/* Navigation Tabs */}
          <div className="flex-1 overflow-y-auto py-4">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full px-6 py-3 flex items-center gap-3 transition-all ${
                    activeTab === tab.id
                      ? 'bg-cyan-600 text-white border-l-4 border-cyan-400'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-white border-l-4 border-transparent'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-gray-700">
            <button className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg flex items-center justify-center gap-2 transition-colors">
              <Upload className="w-4 h-4" />
              <span className="font-medium">Upload File</span>
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {renderMainContent(activeTab)}
        </div>

        {/* Co-Pilot Dock */}
        {showCoPilot && (
          <div className="w-96 bg-gray-800 border-l border-gray-700 flex flex-col">
            {/* Dock Header */}
            <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                  <span className="text-lg font-bold">L</span>
                </div>
                <div>
                  <div className="font-semibold">Librarian</div>
                  <div className="text-xs text-gray-400">Trust: 0.92</div>
                </div>
              </div>
              <button
                onClick={() => setShowCoPilot(false)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">Librarian</div>
                <p className="text-sm">Book ingestion completed for "The Lean Startup". Would you like me to generate flashcards?</p>
              </div>
              <div className="bg-cyan-600 rounded-lg p-3 ml-8">
                <p className="text-sm">Yes, create flashcards</p>
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">Librarian</div>
                <p className="text-sm">Created 15 flashcards. They're now in the Insights tab.</p>
              </div>
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-700">
              <div className="mb-2 flex gap-2 flex-wrap">
                <button className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded">
                  Summarize
                </button>
                <button className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded">
                  Create Quiz
                </button>
                <button className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded">
                  Approve Schema
                </button>
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Ask Grace..."
                  className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
                />
                <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-sm font-medium">
                  Send
                </button>
              </div>
            </div>

            {/* Status Timeline */}
            <div className="px-4 pb-4">
              <div className="text-xs font-semibold text-gray-400 mb-2">Recent Events</div>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                <div className="text-xs bg-gray-700 rounded p-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full" />
                    <span className="text-gray-300">Book ingestion completed</span>
                  </div>
                  <div className="text-gray-500 mt-1">2 minutes ago</div>
                </div>
                <div className="text-xs bg-gray-700 rounded p-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full" />
                    <span className="text-gray-300">Schema approved</span>
                  </div>
                  <div className="text-gray-500 mt-1">5 minutes ago</div>
                </div>
                <div className="text-xs bg-gray-700 rounded p-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-red-400 rounded-full" />
                    <span className="text-gray-300">Self-healing triggered</span>
                  </div>
                  <div className="text-gray-500 mt-1">12 minutes ago</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer Status */}
      <div className="bg-gray-800 border-t border-gray-700 px-6 py-2">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <span className="text-gray-400">
              Status: <span className="text-green-400">Librarian Active</span>
            </span>
            <span className="text-gray-400">
              {systemHealth && `Uptime: ${formatUptime(systemHealth.uptime_seconds)}`}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="text-gray-400 hover:text-white">View Logs</button>
            <button className="text-gray-400 hover:text-white">Theme</button>
            <div className={`w-2 h-2 rounded-full ${
              systemHealth?.status === 'healthy' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
            }`} />
          </div>
        </div>
      </div>
    </div>
  );
}

function renderMainContent(tab: Tab) {
  switch (tab) {
    case 'overview':
      return <OverviewContent />;
    case 'self-healing':
      return <SelfHealingPanel />;
    case 'books':
      return <BooksContent />;
    case 'trusted-sources':
      return <TrustedSourcesContent />;
    default:
      return <PlaceholderContent tab={tab} />;
  }
}

function OverviewContent() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [health, metrics, ingestionStatus, librarianStatus] = await Promise.all([
        api.system.getHealth(),
        api.system.getMetrics(),
        api.ingestion.getStatus(),
        api.librarian.getStatus(),
      ]);

      setStats({ health, metrics, ingestionStatus, librarianStatus });
    } catch (error) {
      console.error('Failed to load overview stats:', error);
    }
  };

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-full">
        <Activity className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-6">
      <h2 className="text-2xl font-bold mb-6">System Overview</h2>

      {/* Metrics Grid */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-cyan-400">{stats.metrics.ingestion.total_ingested}</div>
          <div className="text-sm text-gray-400 mt-1">Books Ingested</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-green-400">
            {(stats.metrics.trust_levels.average_score * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-400 mt-1">Avg Trust</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-yellow-400">{stats.ingestionStatus.queue_size}</div>
          <div className="text-sm text-gray-400 mt-1">Ingestion Queue</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-purple-400">{stats.librarianStatus.stats.files_organized}</div>
          <div className="text-sm text-gray-400 mt-1">Files Organized</div>
        </div>
      </div>

      {/* Component Status */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Component Status</h3>
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(stats.health.components).map(([name, comp]: [string, any]) => (
            <div key={name} className="bg-gray-800 rounded-lg p-3 border border-gray-700">
              <div className="flex items-center justify-between">
                <span className="font-medium capitalize">{name.replace(/_/g, ' ')}</span>
                <span className={`text-xs px-2 py-1 rounded ${
                  comp.status === 'healthy' || comp.status === 'active'
                    ? 'bg-green-900/50 text-green-300'
                    : 'bg-red-900/50 text-red-300'
                }`}>
                  {comp.status}
                </span>
              </div>
              {comp.response_time_ms !== undefined && (
                <div className="text-xs text-gray-400 mt-1">{comp.response_time_ms}ms</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Recent Activity</h3>
        <div className="space-y-2">
          <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 flex items-center gap-3">
            <div className="w-2 h-2 bg-green-400 rounded-full" />
            <div className="flex-1">
              <div className="text-sm font-medium">Book ingestion completed</div>
              <div className="text-xs text-gray-400">lean_startup.pdf → 450 chunks processed</div>
            </div>
            <div className="text-xs text-gray-500">2m ago</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 flex items-center gap-3">
            <div className="w-2 h-2 bg-yellow-400 rounded-full" />
            <div className="flex-1">
              <div className="text-sm font-medium">Schema proposal approved</div>
              <div className="text-xs text-gray-400">customer_feedback table created</div>
            </div>
            <div className="text-xs text-gray-500">5m ago</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BooksContent() {
  return (
    <div className="h-full overflow-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Books Library</h2>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Upload Book
          </button>
          <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center gap-2">
            <Plus className="w-4 h-4" />
            New Folder
          </button>
        </div>
      </div>

      {/* File Grid */}
      <div className="grid grid-cols-3 gap-4">
        {['The Lean Startup', 'Zero to One', 'AI Fundamentals'].map((book, idx) => (
          <div key={idx} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-cyan-500 transition-all cursor-pointer">
            <div className="flex items-start justify-between mb-2">
              <File className="w-8 h-8 text-blue-400" />
              <span className="text-xs px-2 py-1 bg-green-900/50 text-green-300 rounded">
                Verified
              </span>
            </div>
            <div className="font-medium mb-1">{book}.pdf</div>
            <div className="text-xs text-gray-400">2.4 MB • 450 chunks</div>
            <div className="mt-3 pt-3 border-t border-gray-700 flex gap-2">
              <button className="text-xs px-2 py-1 bg-cyan-600 hover:bg-cyan-700 rounded">
                Open
              </button>
              <button className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded">
                Insights
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrustedSourcesContent() {
  const [sources, setSources] = useState<any[]>([]);

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      const data = await api.trustedSources.list();
      setSources(data.sources || []);
    } catch (error) {
      console.error('Failed to load sources:', error);
    }
  };

  return (
    <div className="h-full overflow-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Trusted Sources</h2>
        <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Source
        </button>
      </div>

      <div className="space-y-3">
        {sources.map(source => (
          <div key={source.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="font-semibold text-lg">{source.source_name}</div>
                <div className="text-sm text-gray-400 mt-1">{source.url_pattern}</div>
                <div className="flex gap-2 mt-2">
                  {source.domains.map((domain: string) => (
                    <span key={domain} className="text-xs px-2 py-1 bg-gray-700 rounded">
                      {domain}
                    </span>
                  ))}
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-400">
                  {(source.trust_score * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-400">Trust Score</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PlaceholderContent({ tab }: { tab: Tab }) {
  return (
    <div className="h-full flex items-center justify-center p-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2 capitalize">{tab.replace('-', ' ')}</h2>
        <p className="text-gray-400">Panel coming soon...</p>
      </div>
    </div>
  );
}

export default GraceComprehensive;
