/**
 * Trust Dashboard Panel
 * Visualizes trust scores, contradictions, and data quality across memory tables
 */

import { useState, useEffect } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import {
  Shield, AlertTriangle, TrendingUp, TrendingDown, Activity,
  CheckCircle, XCircle, AlertCircle, BarChart3, PieChart
} from 'lucide-react';

interface TrustReport {
  tables: Record<string, {
    avg_trust: number;
    low_trust_count: number;
    high_trust_count: number;
    total_rows: number;
  }>;
  overall: {
    avg_trust: number;
    low_trust_rows: number;
    high_trust_rows: number;
    total_rows: number;
  };
  timestamp: string;
}

interface ContradictionSummary {
  total_contradictions: number;
  by_severity: Record<string, number>;
  by_table: Record<string, number>;
  critical_count: number;
  needs_review: number;
  timestamp: string;
}

export function TrustDashboardPanel() {
  const [trustReport, setTrustReport] = useState<TrustReport | null>(null);
  const [contradictions, setContradictions] = useState<ContradictionSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedTable, setSelectedTable] = useState<string>('');

  useEffect(() => {
    loadTrustReport();
    loadContradictions();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadTrustReport();
      loadContradictions();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  async function loadTrustReport() {
    try {
      const response = await fetch(apiUrl('/api/memory/tables/trust/report');
      const data = await response.json();
      setTrustReport(data);
    } catch (err) {
      console.error('Failed to load trust report:', err);
    }
  }

  async function loadContradictions() {
    try {
      const response = await fetch(apiUrl('/api/memory/tables/contradictions/summary');
      const data = await response.json();
      setContradictions(data);
    } catch (err) {
      console.error('Failed to load contradictions:', err);
    }
  }

  async function updateTrustScores(tableName?: string) {
    setLoading(true);
    try {
      const url = tableName
        ? `http://localhost:8000/api/memory/tables/trust/update/${tableName}`
        : apiUrl('/api/memory/tables/trust/update-all';
      
      const response = await fetch(url, { method: 'POST' });
      const result = await response.json();
      
      await loadTrustReport();
      alert(`Updated ${result.updated_count || result.total_updated} trust scores`);
    } catch (err) {
      console.error('Failed to update trust scores:', err);
      alert('Failed to update trust scores');
    } finally {
      setLoading(false);
    }
  }

  async function scanContradictions() {
    setLoading(true);
    try {
      const response = await fetch(apiUrl('/api/memory/tables/contradictions/scan', {
        method: 'POST'
      });
      const result = await response.json();
      
      await loadContradictions();
      alert(`Scan complete: ${result.total_contradictions || 0} contradictions found`);
    } catch (err) {
      console.error('Failed to scan contradictions:', err);
      alert('Failed to scan contradictions');
    } finally {
      setLoading(false);
    }
  }

  const getTrustColor = (trust: number) => {
    if (trust >= 0.8) return 'text-green-400';
    if (trust >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getTrustBgColor = (trust: number) => {
    if (trust >= 0.8) return 'bg-green-900';
    if (trust >= 0.6) return 'bg-yellow-900';
    return 'bg-red-900';
  };

  const sortedTables = trustReport
    ? Object.entries(trustReport.tables).sort((a, b) => a[1].avg_trust - b[1].avg_trust)
    : [];

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Trust & Quality Dashboard
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Monitor data trust scores and detect contradictions
        </p>
      </div>

      {/* Actions */}
      <div className="p-4 border-b border-gray-700 flex gap-3">
        <button
          onClick={() => updateTrustScores()}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded flex items-center gap-2"
        >
          <Activity className="w-4 h-4" />
          Update All Trust Scores
        </button>
        <button
          onClick={scanContradictions}
          disabled={loading}
          className="px-4 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-700 rounded flex items-center gap-2"
        >
          <AlertTriangle className="w-4 h-4" />
          Scan for Contradictions
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Overall Stats */}
        {trustReport && (
          <div className="p-6">
            <h3 className="text-lg font-bold mb-4">Overall Statistics</h3>
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-800 p-4 rounded">
                <div className="text-sm text-gray-400 mb-1">Average Trust</div>
                <div className={`text-2xl font-bold ${getTrustColor(trustReport.overall.avg_trust)}`}>
                  {(trustReport.overall.avg_trust * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <div className="text-sm text-gray-400 mb-1">High Trust Rows</div>
                <div className="text-2xl font-bold text-green-400">
                  {trustReport.overall.high_trust_rows}
                </div>
                <div className="text-xs text-gray-500">
                  {((trustReport.overall.high_trust_rows / trustReport.overall.total_rows) * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <div className="text-sm text-gray-400 mb-1">Low Trust Rows</div>
                <div className="text-2xl font-bold text-red-400">
                  {trustReport.overall.low_trust_rows}
                </div>
                <div className="text-xs text-gray-500">
                  {((trustReport.overall.low_trust_rows / trustReport.overall.total_rows) * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded">
                <div className="text-sm text-gray-400 mb-1">Total Rows</div>
                <div className="text-2xl font-bold text-blue-400">
                  {trustReport.overall.total_rows}
                </div>
              </div>
            </div>

            {/* Contradictions */}
            {contradictions && contradictions.total_contradictions > 0 && (
              <div className="mb-6 p-4 bg-red-900 bg-opacity-20 border border-red-700 rounded">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="font-bold text-red-400 mb-1">
                      {contradictions.total_contradictions} Contradictions Detected
                    </div>
                    <div className="text-sm text-gray-300">
                      {contradictions.critical_count > 0 && (
                        <span className="text-red-400 font-medium">
                          {contradictions.critical_count} Critical
                        </span>
                      )}
                      {contradictions.critical_count > 0 && contradictions.needs_review > contradictions.critical_count && ' • '}
                      {contradictions.needs_review > contradictions.critical_count && (
                        <span>
                          {contradictions.needs_review - contradictions.critical_count} Need Review
                        </span>
                      )}
                    </div>
                    <div className="mt-2 flex gap-2">
                      {Object.entries(contradictions.by_severity).map(([severity, count]) => (
                        <span
                          key={severity}
                          className={`px-2 py-1 rounded text-xs ${
                            severity === 'critical'
                              ? 'bg-red-800 text-red-200'
                              : severity === 'high'
                              ? 'bg-orange-800 text-orange-200'
                              : severity === 'medium'
                              ? 'bg-yellow-800 text-yellow-200'
                              : 'bg-gray-700 text-gray-300'
                          }`}
                        >
                          {severity}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Table-by-Table Breakdown */}
            <h3 className="text-lg font-bold mb-3">Trust by Table</h3>
            <div className="space-y-3">
              {sortedTables.map(([tableName, stats]) => {
                const trustPercent = stats.avg_trust * 100;
                
                return (
                  <div
                    key={tableName}
                    className="bg-gray-800 p-4 rounded hover:bg-gray-750 cursor-pointer"
                    onClick={() => setSelectedTable(tableName)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{tableName.replace('memory_', '')}</span>
                        <span className="text-xs text-gray-400">
                          ({stats.total_rows} rows)
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          updateTrustScores(tableName);
                        }}
                        className="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs"
                      >
                        Update
                      </button>
                    </div>

                    {/* Trust Bar */}
                    <div className="mb-2">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-gray-400">Trust Score</span>
                        <span className={getTrustColor(stats.avg_trust)}>
                          {trustPercent.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full ${getTrustBgColor(stats.avg_trust)} transition-all`}
                          style={{ width: `${trustPercent}%` }}
                        />
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="flex gap-4 text-xs">
                      <div className="flex items-center gap-1 text-green-400">
                        <CheckCircle className="w-3 h-3" />
                        {stats.high_trust_count} high
                      </div>
                      <div className="flex items-center gap-1 text-red-400">
                        <XCircle className="w-3 h-3" />
                        {stats.low_trust_count} low
                      </div>
                      {contradictions && contradictions.by_table[tableName] && (
                        <div className="flex items-center gap-1 text-orange-400">
                          <AlertCircle className="w-3 h-3" />
                          {contradictions.by_table[tableName]} contradictions
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {!trustReport && !loading && (
          <div className="p-6 text-center text-gray-400">
            <Shield className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p>Click "Update All Trust Scores" to generate report</p>
          </div>
        )}
      </div>
    </div>
  );
}
