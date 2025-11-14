/**
 * Layered Dashboard - 4-Tier Monitoring System
 * 
 * Layer 1: Operations (Health, Resources, Errors)
 * Layer 2: Orchestration (HTM, Tasks, Queues, Throughput)
 * Layer 3: Intent (Goals, Outcomes, Learning)
 * Layer 4: Development (Logs, Playbooks, Diagnostics)
 */

import React, { useState } from 'react';
import { Layer1OpsDashboard } from '../components/dashboards/Layer1OpsDashboard';
import { Layer2OrchestrationDashboard } from '../components/dashboards/Layer2OrchestrationDashboard';
import { Layer3IntentDashboard } from '../components/dashboards/Layer3IntentDashboard';
import { Layer4DevDashboard } from '../components/dashboards/Layer4DevDashboard';

type LayerType = 'layer1' | 'layer2' | 'layer3' | 'layer4';

export function LayeredDashboard() {
  const [activeLayer, setActiveLayer] = useState<LayerType>('layer2');

  const layers = [
    {
      id: 'layer1' as LayerType,
      name: 'Layer 1: Operations',
      description: 'System health, resources, errors',
      icon: '🏥',
      color: 'bg-red-500'
    },
    {
      id: 'layer2' as LayerType,
      name: 'Layer 2: Orchestration',
      description: 'HTM, tasks, queues, SLAs, throughput',
      icon: '⚙️',
      color: 'bg-blue-500'
    },
    {
      id: 'layer3' as LayerType,
      name: 'Layer 3: Intent',
      description: 'Goals, outcomes, learning loop',
      icon: '🧠',
      color: 'bg-purple-500'
    },
    {
      id: 'layer4' as LayerType,
      name: 'Layer 4: Development',
      description: 'Logs, playbooks, diagnostics',
      icon: '🔧',
      color: 'bg-green-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Layer Selector */}
      <div className="border-b border-gray-700 bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="flex gap-2 py-4">
            {layers.map((layer) => (
              <button
                key={layer.id}
                onClick={() => setActiveLayer(layer.id)}
                className={`
                  px-6 py-3 rounded-lg font-medium transition-all
                  ${activeLayer === layer.id
                    ? `${layer.color} text-white shadow-lg scale-105`
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }
                `}
              >
                <span className="text-xl mr-2">{layer.icon}</span>
                {layer.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Active Layer Content */}
      <div className="container mx-auto px-4 py-6">
        {activeLayer === 'layer1' && <Layer1OpsDashboard />}
        {activeLayer === 'layer2' && <Layer2OrchestrationDashboard />}
        {activeLayer === 'layer3' && <Layer3IntentDashboard />}
        {activeLayer === 'layer4' && <Layer4DevDashboard />}
      </div>
    </div>
  );
}
