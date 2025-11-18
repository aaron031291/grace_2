/**
 * All Kernels Panel - Unified dashboard for all 11 domain kernels
 * Similar to Memory Fusion interface
 */

import React, { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from '../config';
import { Cpu, PlayCircle, Square, Activity, TrendingUp, AlertCircle } from 'lucide-react';

interface Kernel {
  name: string;
  status: string;
  active: boolean;
  metrics: any;
}

interface KernelStats {
  total: number;
  active: number;
  kernels: Kernel[];
}

export function AllKernelsPanel() {
  const [stats, setStats] = useState<KernelStats>({ total: 0, active: 0, kernels: [] });
  const [selectedKernel, setSelectedKernel] = useState<Kernel | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadKernels();
    const interval = setInterval(loadKernels, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadKernels = async () => {
    try {
      const response = await fetch(apiUrl('/api/kernels');
      if (response.ok && response.headers.get('content-type')?.includes('json')) {
        const data = await response.json();
        setStats(data);
        if (!selectedKernel && data.kernels.length > 0) {
          setSelectedKernel(data.kernels[0]);
        }
      }
    } catch (error) {
      console.error('Failed to load kernels:', error);
    }
  };

  const startKernel = async (kernelName: string) => {
    setLoading(true);
    try {
      await fetch(`http://localhost:8000/api/kernels/${kernelName}/start`, { method: 'POST' });
      await loadKernels();
      alert(`${kernelName} kernel started`);
    } catch (error) {
      console.error('Failed to start kernel:', error);
    } finally {
      setLoading(false);
    }
  };

  const stopKernel = async (kernelName: string) => {
    setLoading(true);
    try {
      await fetch(`http://localhost:8000/api/kernels/${kernelName}/stop`, { method: 'POST' });
      await loadKernels();
      alert(`${kernelName} kernel stopped`);
    } catch (error) {
      console.error('Failed to stop kernel:', error);
    } finally {
      setLoading(false);
    }
  };

  const getKernelColor = (name: string) => {
    const colors: Record<string, string> = {
      memory: 'purple',
      core: 'blue',
      code: 'green',
      governance: 'yellow',
      verification: 'pink',
      intelligence: 'indigo',
      infrastructure: 'cyan',
      federation: 'orange',
      ml_dl: 'red',
      self_healing: 'lime',
      librarian: 'violet'
    };
    return colors[name] || 'gray';
  };

  return (
    <div className="all-kernels-panel h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Cpu className="w-6 h-6 text-cyan-400" />
            <h2 className="text-2xl font-bold">Domain Kernels</h2>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-gray-400">{stats.active} / {stats.total} Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-3 gap-4">
          {stats.kernels.map(kernel => (
            <div
              key={kernel.name}
              onClick={() => setSelectedKernel(kernel)}
              className={`bg-gray-800/50 rounded-lg p-4 border cursor-pointer transition-all ${
                selectedKernel?.name === kernel.name
                  ? `border-${getKernelColor(kernel.name)}-500`
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${kernel.active ? 'bg-green-400 animate-pulse' : 'bg-gray-600'}`} />
                  <h3 className="font-semibold capitalize">{kernel.name.replace('_', ' ')}</h3>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  kernel.status === 'active' ? 'bg-green-900/50 text-green-300' :
                  kernel.status === 'starting' ? 'bg-yellow-900/50 text-yellow-300' :
                  'bg-gray-700 text-gray-400'
                }`}>
                  {kernel.status}
                </span>
              </div>

              <div className="flex gap-2">
                {!kernel.active ? (
                  <button
                    onClick={(e) => { e.stopPropagation(); startKernel(kernel.name); }}
                    disabled={loading}
                    className="flex-1 bg-green-600 hover:bg-green-700 px-3 py-2 rounded text-xs font-medium transition-all disabled:opacity-50 flex items-center justify-center gap-1"
                  >
                    <PlayCircle className="w-3 h-3" />
                    Start
                  </button>
                ) : (
                  <button
                    onClick={(e) => { e.stopPropagation(); stopKernel(kernel.name); }}
                    disabled={loading}
                    className="flex-1 bg-red-600 hover:bg-red-700 px-3 py-2 rounded text-xs font-medium transition-all disabled:opacity-50 flex items-center justify-center gap-1"
                  >
                    <Square className="w-3 h-3" />
                    Stop
                  </button>
                )}
              </div>

              {kernel.metrics && Object.keys(kernel.metrics).length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <div className="text-xs text-gray-400">
                    {Object.entries(kernel.metrics).slice(0, 2).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span>{key}:</span>
                        <span className="text-white">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Selected Kernel Details */}
        {selectedKernel && (
          <div className="mt-6 bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-bold mb-4 capitalize">{selectedKernel.name.replace('_', ' ')} Kernel</h3>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Status</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${selectedKernel.active ? 'bg-green-400' : 'bg-gray-600'}`} />
                    <span>{selectedKernel.active ? 'Active' : 'Inactive'}</span>
                  </div>
                  <div className="text-sm text-gray-400">State: {selectedKernel.status}</div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Metrics</h4>
                <div className="space-y-1 text-sm">
                  {Object.entries(selectedKernel.metrics || {}).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-400">{key}:</span>
                      <span className="text-white">{JSON.stringify(value)}</span>
                    </div>
                  ))}
                  {Object.keys(selectedKernel.metrics || {}).length === 0 && (
                    <div className="text-gray-500">No metrics available</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AllKernelsPanel;
