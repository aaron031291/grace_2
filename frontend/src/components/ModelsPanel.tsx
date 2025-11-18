/**
 * Models Panel
 * ML/DL model registry with deployment stages and governance
 */

import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import { Brain, CheckCircle, XCircle, TrendingUp, AlertTriangle, Eye, Play } from 'lucide-react';

export function ModelsPanel() {
  const [models, setModels] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [selectedModel, setSelectedModel] = useState<any>(null);
  const [stageFilter, setStageFilter] = useState('all');

  useEffect(() => {
    loadModels();
    loadStats();
    const interval = setInterval(() => {
      loadModels();
      loadStats();
    }, 10000);
    return () => clearInterval(interval);
  }, [stageFilter]);

  const loadModels = async () => {
    try {
      const url = stageFilter === 'all' 
        ? apiUrl('/api/model-registry/models'
        : `http://localhost:8000/api/model-registry/models?stage=${stageFilter}`;
      
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setModels(data.models || []);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const loadStats = async () => {
    try {
      const res = await fetch(apiUrl('/api/model-registry/stats');
      if (res.ok) {
        setStats(await res.json());
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'production': return 'bg-green-900/50 text-green-300 border-green-500/30';
      case 'canary': return 'bg-yellow-900/50 text-yellow-300 border-yellow-500/30';
      case 'sandbox': return 'bg-blue-900/50 text-blue-300 border-blue-500/30';
      case 'rollback': return 'bg-red-900/50 text-red-300 border-red-500/30';
      default: return 'bg-gray-900/50 text-gray-300 border-gray-500/30';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Brain className="w-7 h-7 text-purple-400" />
            <div>
              <h2 className="text-2xl font-bold">Model Registry</h2>
              <p className="text-sm text-gray-400">ML/DL deployment & governance</p>
            </div>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-5 gap-3">
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-purple-400">{stats.total_models}</div>
              <div className="text-xs text-gray-400">Total Models</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-400">{stats.by_stage.production}</div>
              <div className="text-xs text-gray-400">Production</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-yellow-400">{stats.by_stage.canary}</div>
              <div className="text-xs text-gray-400">Canary</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-cyan-400">{stats.governance.constitutional_passed}</div>
              <div className="text-xs text-gray-400">Compliant</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-blue-400">{stats.governance.bias_passed}</div>
              <div className="text-xs text-gray-400">Bias Checked</div>
            </div>
          </div>
        )}

        {/* Stage Filter */}
        <div className="flex gap-2 mt-4">
          {['all', 'production', 'canary', 'sandbox', 'development'].map(stage => (
            <button
              key={stage}
              onClick={() => setStageFilter(stage)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                stageFilter === stage
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {stage.charAt(0).toUpperCase() + stage.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Models List */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-2 gap-4">
          {models.map((model: any) => (
            <div
              key={model.model_id}
              onClick={() => setSelectedModel(model)}
              className="bg-gray-800/50 rounded-lg p-4 border border-gray-700 hover:border-purple-500 transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-bold text-lg">{model.name}</h3>
                  <div className="text-sm text-gray-400">v{model.version} • {model.framework}</div>
                </div>
                <span className={`px-3 py-1 rounded border text-xs font-semibold ${getStageColor(model.deploy_status)}`}>
                  {model.deploy_status}
                </span>
              </div>

              <div className="text-sm text-gray-400 mb-3">{model.description}</div>

              {/* Governance Badges */}
              <div className="flex gap-2 mb-3">
                {model.constitutional_compliance ? (
                  <div className="flex items-center gap-1 text-xs text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    Constitutional
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <XCircle className="w-3 h-3" />
                    Not verified
                  </div>
                )}
                {model.bias_check_passed ? (
                  <div className="flex items-center gap-1 text-xs text-green-400">
                    <CheckCircle className="w-3 h-3" />
                    Bias checked
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <XCircle className="w-3 h-3" />
                    Unchecked
                  </div>
                )}
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-3 gap-2 pt-3 border-t border-gray-700 text-xs">
                <div>
                  <div className="text-gray-500">Team</div>
                  <div className="font-medium">{model.team}</div>
                </div>
                <div>
                  <div className="text-gray-500">Type</div>
                  <div className="font-medium">{model.model_type}</div>
                </div>
                <div>
                  <div className="text-gray-500">Samples</div>
                  <div className="font-medium">{model.training_dataset_size?.toLocaleString() || 'N/A'}</div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 mt-3">
                <button className="flex-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 rounded text-xs">
                  <Eye className="w-3 h-3 inline mr-1" />
                  Details
                </button>
                {model.deploy_status === 'development' && (
                  <button className="flex-1 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 rounded text-xs">
                    <Play className="w-3 h-3 inline mr-1" />
                    Promote
                  </button>
                )}
              </div>
            </div>
          ))}

          {models.length === 0 && (
            <div className="col-span-2 bg-gray-800/50 rounded-lg p-12 text-center border border-gray-700">
              <Brain className="w-16 h-16 mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400">No models registered yet</p>
              <button className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm">
                Register Your First Model
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ModelsPanel;
