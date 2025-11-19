/**
 * Grace Nexus OS - Enterprise Dashboard Interface
 * Datadog/Kubernetes style with Grace Kernel and Domains
 */

import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { 
  Cpu, Database, Network, Activity, Settings, Terminal, Shield, 
  MessageSquare, Search, Bell, Moon, Sun, Layers, TrendingUp,
  HardDrive, Zap, GitBranch, BarChart3
} from 'lucide-react';

interface MetricCard {
  label: string;
  value: string;
  subtext: string;
  icon: any;
  color: string;
}

interface DomainHealth {
  domain_id: string;
  health: number;
  trust: number;
  confidence: number;
}

export default function GraceNexus() {
  const [activeNav, setActiveNav] = useState('kernel');
  const [activeTab, setActiveTab] = useState('performance');
  const [systemMetrics, setSystemMetrics] = useState<any>(null);
  const [domains, setDomains] = useState<DomainHealth[]>([]);

  useEffect(() => {
    // Fetch health data
    fetch(apiUrl('/health')
      .then(r => r.json())
      .then(data => setSystemMetrics(data))
      .catch(console.error);

    // Fetch domain status
    fetch(apiUrl('/api/cognition/status')
      .then(r => r.json())
      .then(data => {
        if (data.domains) {
          setDomains(Object.values(data.domains));
        }
      })
      .catch(console.error);
  }, []);

  const metrics: MetricCard[] = [
    {
      label: 'CPU Usage',
      value: systemMetrics ? `${systemMetrics.metrics?.cpu_usage_percent?.toFixed(1)}%` : '--',
      subtext: '12 Cores / Active',
      icon: Cpu,
      color: 'cyan'
    },
    {
      label: 'Memory',
      value: systemMetrics ? `${((systemMetrics.metrics?.memory_usage_mb || 0) / 1024).toFixed(1)} GB` : '--',
      subtext: systemMetrics ? `${systemMetrics.metrics?.memory_usage_mb?.toFixed(0)} MB` : '--',
      icon: Database,
      color: 'purple'
    },
    {
      label: 'Active Sessions',
      value: systemMetrics ? `${systemMetrics.metrics?.active_sessions || 0}` : '--',
      subtext: `${systemMetrics?.metrics?.database_connections || 0} DB Connections`,
      icon: Network,
      color: 'green'
    }
  ];

  const navItems = [
    { id: 'kernel', label: 'Grace Kernel', icon: Layers },
    { id: 'domains', label: 'Domains', icon: GitBranch },
    { id: 'diagnostics', label: 'Diagnostics', icon: Activity },
    { id: 'datacenter', label: 'Data Center', icon: Database },
    { id: 'network', label: 'Network', icon: Network },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'console', label: 'Console', icon: Terminal },
    { id: 'communications', label: 'Comms', icon: MessageSquare },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0d1117] to-[#111827] text-gray-100">
      {/* Left Sidebar */}
      <aside className="w-64 bg-[#0d1117] border-r border-gray-800 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Layers className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-cyan-400">GRACE OS</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-wider">Kernel v3.0</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-all ${
                activeNav === item.id
                  ? 'bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-500 shadow-lg shadow-cyan-500/20'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
              }`}
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* System Status at bottom */}
        <div className="p-4 border-t border-gray-800">
          <div className="text-xs text-gray-500 mb-2">Core Systems</div>
          <div className="relative h-2 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="absolute h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-1000"
              style={{ width: '82%' }}
            />
          </div>
          <div className="text-xs text-gray-400 mt-1">82% Operational</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-[#0d1117]/80 backdrop-blur border-b border-gray-800 flex items-center px-6 gap-4">
          {/* Search */}
          <div className="flex-1 max-w-xl">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input
                type="text"
                placeholder="Search systems..."
                className="w-full bg-gray-900/50 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Right Icons */}
          <button className="p-2 text-gray-400 hover:text-gray-200 rounded-lg hover:bg-gray-800">
            <Bell className="w-5 h-5" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-200 rounded-lg hover:bg-gray-800">
            <Moon className="w-5 h-5" />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500" />
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Title Section */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-100">System Overview</h2>
              <p className="text-sm text-gray-500 mt-1">Real-time telemetry and diagnostics</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/30 rounded-full">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-cyan-400 uppercase tracking-wide">LIVE</span>
            </div>
          </div>

          {/* Metric Cards */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            {metrics.map((metric, i) => (
              <div
                key={i}
                className="bg-gray-900/40 backdrop-blur border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-all hover:shadow-lg"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`w-10 h-10 rounded-lg bg-${metric.color}-500/10 flex items-center justify-center`}>
                    <metric.icon className={`w-5 h-5 text-${metric.color}-400`} />
                  </div>
                  <TrendingUp className="w-4 h-4 text-green-400" />
                </div>
                <div className="text-3xl font-bold text-gray-100 mb-1">{metric.value}</div>
                <div className="text-xs text-gray-500 mb-2">{metric.label}</div>
                <div className="text-xs text-gray-400">{metric.subtext}</div>
              </div>
            ))}
          </div>

          {/* Tab Pills */}
          <div className="flex items-center gap-2 mb-4">
            {['performance', 'processes', 'storage'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  activeTab === tab
                    ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30'
                    : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {/* Chart Area */}
          <div className="bg-gray-900/40 backdrop-blur border border-gray-800 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-200">System Performance</h3>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-blue-500" />
                  <span className="text-gray-400">CPU</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-purple-500" />
                  <span className="text-gray-400">Memory</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-cyan-500" />
                  <span className="text-gray-400">Network</span>
                </div>
              </div>
            </div>

            {/* Chart Placeholder */}
            <div className="h-64 flex items-end gap-1">
              {Array.from({ length: 50 }).map((_, i) => (
                <div
                  key={i}
                  className="flex-1 bg-gradient-to-t from-cyan-500/30 to-cyan-500/10 rounded-t"
                  style={{ height: `${Math.random() * 100}%` }}
                />
              ))}
            </div>

            <div className="mt-4 flex justify-between text-xs text-gray-500">
              <span>00:00</span>
              <span>12:00</span>
              <span>Now</span>
            </div>
          </div>

          {/* Domains Grid (if domains nav active) */}
          {activeNav === 'domains' && domains.length > 0 && (
            <div className="grid grid-cols-4 gap-4 mt-6">
              {domains.map((domain) => (
                <div
                  key={domain.domain_id}
                  className="bg-gray-900/40 backdrop-blur border border-gray-800 rounded-xl p-4 hover:border-gray-700 transition-all"
                >
                  <div className="text-sm font-semibold text-gray-200 mb-2 capitalize">
                    {domain.domain_id}
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Health</span>
                      <span className="text-cyan-400">{(domain.health * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Trust</span>
                      <span className="text-purple-400">{(domain.trust * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Confidence</span>
                      <span className="text-green-400">{(domain.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
