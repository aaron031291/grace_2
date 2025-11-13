/**
 * Comprehensive Metrics Panel - View all system metrics in one place
 */

import React, { useState, useEffect } from 'react';
import { BarChart3, Zap, BookOpen, Shield, TrendingUp } from 'lucide-react';
import { api, type ComprehensiveMetrics } from '../api/comprehensive';

export function ComprehensiveMetricsPanel() {
  const [metrics, setMetrics] = useState<ComprehensiveMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      const data = await api.system.getMetrics();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to load comprehensive metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 text-white">
        <BarChart3 className="w-8 h-8 animate-spin" />
        <span className="ml-3">Loading metrics...</span>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 text-white">
        <p>Failed to load metrics</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6 overflow-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <BarChart3 className="w-8 h-8 text-purple-400" />
          <h2 className="text-3xl font-bold">Comprehensive Metrics</h2>
        </div>
        <p className="text-gray-400">
          Last updated: {new Date(metrics.timestamp).toLocaleString()}
        </p>
      </div>

      <div className="space-y-6">
        {/* Self-Healing Metrics */}
        <div>
          <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
            <Zap className="w-6 h-6 text-yellow-400" />
            Self-Healing Performance
          </h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-blue-400">{metrics.self_healing.total_runs}</div>
              <div className="text-sm text-gray-400 mt-1">Total Runs</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-green-400">
                {(metrics.self_healing.average_success_rate * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-400 mt-1">Success Rate</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-purple-400">
                {metrics.self_healing.mttr_minutes.toFixed(1)}m
              </div>
              <div className="text-sm text-gray-400 mt-1">MTTR</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-orange-400">
                {metrics.self_healing.average_execution_time_ms}ms
              </div>
              <div className="text-sm text-gray-400 mt-1">Avg Execution Time</div>
            </div>
          </div>
        </div>

        {/* Ingestion Metrics */}
        <div>
          <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-blue-400" />
            Ingestion Performance
          </h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-blue-400">{metrics.ingestion.total_ingested}</div>
              <div className="text-sm text-gray-400 mt-1">Books Ingested</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-green-400">{metrics.ingestion.chunks_processed}</div>
              <div className="text-sm text-gray-400 mt-1">Chunks Processed</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-purple-400">
                {metrics.ingestion.average_chunk_time_ms}ms
              </div>
              <div className="text-sm text-gray-400 mt-1">Avg Chunk Time</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-yellow-400">
                {(metrics.ingestion.success_rate * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-400 mt-1">Success Rate</div>
            </div>
          </div>
        </div>

        {/* Verification Metrics */}
        <div>
          <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
            <Shield className="w-6 h-6 text-green-400" />
            Verification Performance
          </h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-blue-400">{metrics.verification.total_verifications}</div>
              <div className="text-sm text-gray-400 mt-1">Total Verifications</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-green-400">{metrics.verification.passed}</div>
              <div className="text-sm text-gray-400 mt-1">Passed</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-red-400">{metrics.verification.failed}</div>
              <div className="text-sm text-gray-400 mt-1">Failed</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-yellow-400">
                {(metrics.verification.pass_rate * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-400 mt-1">Pass Rate</div>
            </div>
          </div>
        </div>

        {/* Trust Levels */}
        <div>
          <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-purple-400" />
            Trust Distribution
          </h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-green-400">{metrics.trust_levels.high_trust}</div>
              <div className="text-sm text-gray-400 mt-1">High Trust</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-yellow-400">{metrics.trust_levels.medium_trust}</div>
              <div className="text-sm text-gray-400 mt-1">Medium Trust</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-red-400">{metrics.trust_levels.low_trust}</div>
              <div className="text-sm text-gray-400 mt-1">Low Trust</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-3xl font-bold text-blue-400">
                {(metrics.trust_levels.average_score * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-400 mt-1">Avg Score</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComprehensiveMetricsPanel;
