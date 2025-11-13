/**
 * Complete 12 Kernels Panel - All domain kernels including Librarian
 * Comprehensive dashboard for monitoring and controlling all kernels
 */

import React, { useState, useEffect } from 'react';
import { Cpu, PlayCircle, Square, Activity, Database, Code, Shield, Brain, Network, Zap, BookOpen, Upload } from 'lucide-react';

interface Kernel {
  name: string;
  status: string;
  active: boolean;
  metrics: any;
}

const KERNEL_INFO = {
  memory: { icon: <Database className="w-5 h-5" />, color: 'purple', desc: 'Knowledge storage & retrieval' },
  core: { icon: <Cpu className="w-5 h-5" />, color: 'blue', desc: 'Core system operations' },
  code: { icon: <Code className="w-5 h-5" />, color: 'green', desc: 'Code analysis & generation' },
  governance: { icon: <Shield className="w-5 h-5" />, color: 'yellow', desc: 'Policy & compliance' },
  verification: { icon: <Activity className="w-5 h-5" />, color: 'pink', desc: 'Trust & validation' },
  intelligence: { icon: <Brain className="w-5 h-5" />, color: 'indigo', desc: 'AI reasoning & learning' },
  infrastructure: { icon: <Network className="w-5 h-5" />, color: 'cyan', desc: 'System management' },
  federation: { icon: <Network className="w-5 h-5" />, color: 'orange', desc: 'Multi-system coordination' },
  ml_dl: { icon: <Brain className="w-5 h-5" />, color: 'red', desc: 'Machine learning ops' },
  self_healing: { icon: <Zap className="w-5 h-5" />, color: 'lime', desc: 'Autonomous recovery' },
  librarian: { icon: <BookOpen className="w-5 h-5" />, color: 'violet', desc: 'File watching & organization' },
  ingestion: { icon: <Upload className="w-5 h-5" />, color: 'teal', desc: 'Content ingestion pipelines' }
};

export function Complete12KernelsPanel() {
  const [kernels, setKernels] = useState<Kernel[]>([]);
  const [stats, setStats] = useState({ total: 12, active: 0 });
  const [selectedKernel, setSelectedKernel] = useState<Kernel | null>(null);

  useEffect(() => {
    loadKernels();
    const interval = setInterval(loadKernels, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadKernels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/kernels');
      if (response.ok) {
        const data = await response.json();
        setKernels(data.kernels || []);
        setStats({ total: data.total || 12, active: data.active || 0 });
      }
    } catch (error) {
      console.error('Failed to load kernels:', error);
    }
  };

  return (
    <div className="kernels-panel h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          All 12 Domain Kernels
        </h1>
        <p className="text-gray-400">
          {stats.active} of {stats.total} kernels active • Auto-refresh every 5s
        </p>
      </div>

      {/* Kernel Grid */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {Object.entries(KERNEL_INFO).map(([name, info]) => {
          const kernel = kernels.find(k => k.name === name);
          const isActive = kernel?.active || false;
          
          return (
            <div
              key={name}
              onClick={() => setSelectedKernel(kernel || null)}
              className={`bg-gray-800/50 rounded-lg p-4 border cursor-pointer transition-all ${
                selectedKernel?.name === name ? 'border-purple-500 ring-2 ring-purple-500/50' : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-600'}`} />
                <div className="text-gray-400">{info.icon}</div>
              </div>
              <h3 className="font-semibold capitalize mb-1">{name.replace('_', ' ')}</h3>
              <p className="text-xs text-gray-500">{info.desc}</p>
              <div className="mt-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  isActive ? 'bg-green-900/50 text-green-300' : 'bg-gray-700 text-gray-400'
                }`}>
                  {kernel?.status || 'unknown'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Kernel Details */}
      {selectedKernel && (
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold mb-4 capitalize">
            {selectedKernel.name.replace('_', ' ')} Kernel Details
          </h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-400 mb-3">Status</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${selectedKernel.active ? 'bg-green-400' : 'bg-gray-600'}`} />
                  <span>{selectedKernel.active ? 'Active & Running' : 'Inactive'}</span>
                </div>
                <div className="text-sm text-gray-400">State: {selectedKernel.status}</div>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-400 mb-3">Metrics</h4>
              <div className="space-y-1 text-sm">
                {selectedKernel.metrics && Object.entries(selectedKernel.metrics).length > 0 ? (
                  Object.entries(selectedKernel.metrics).slice(0, 5).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-400">{key}:</span>
                      <span className="text-white font-mono text-xs">{JSON.stringify(value).substring(0, 30)}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500">No metrics available</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Kernel Descriptions */}
      <div className="mt-6 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-400 mb-2">About the 12 Kernels</h4>
        <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs text-gray-400">
          {Object.entries(KERNEL_INFO).map(([name, info]) => (
            <div key={name}>
              <strong className="text-white capitalize">{name.replace('_', ' ')}:</strong> {info.desc}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Complete12KernelsPanel;
