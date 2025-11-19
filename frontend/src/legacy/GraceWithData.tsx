/**
 * Grace Interface - With Real Data Integration
 * All panels wired up with comprehensive API
 */

import React, { useState } from 'react';
import { SelfHealingPanel } from './components/SelfHealingPanel';
import { SystemHealthPanel } from './panels/SystemHealthPanel';
import { ComprehensiveMetricsPanel } from './panels/ComprehensiveMetricsPanel';
import { Activity, Zap, Server, BarChart3 } from 'lucide-react';

type View = 'self-healing' | 'health' | 'metrics';

export function GraceWithData() {
  const [activeView, setActiveView] = useState<View>('self-healing');

  const views = [
    { id: 'self-healing' as View, label: 'Self-Healing', icon: Zap, color: 'text-yellow-400' },
    { id: 'health' as View, label: 'System Health', icon: Server, color: 'text-blue-400' },
    { id: 'metrics' as View, label: 'Metrics', icon: BarChart3, color: 'text-purple-400' },
  ];

  const renderView = () => {
    switch (activeView) {
      case 'self-healing':
        return <SelfHealingPanel />;
      case 'health':
        return <SystemHealthPanel />;
      case 'metrics':
        return <ComprehensiveMetricsPanel />;
      default:
        return null;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Top Navigation */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity className="w-8 h-8 text-cyan-400" />
            <h1 className="text-2xl font-bold text-white">GRACE</h1>
            <span className="text-sm text-gray-400">Comprehensive Dashboard</span>
          </div>
          
          <div className="flex gap-2">
            {views.map(view => {
              const Icon = view.icon;
              return (
                <button
                  key={view.id}
                  onClick={() => setActiveView(view.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                    activeView === view.id
                      ? 'bg-cyan-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${view.color}`} />
                  {view.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {renderView()}
      </div>
    </div>
  );
}

export default GraceWithData;
