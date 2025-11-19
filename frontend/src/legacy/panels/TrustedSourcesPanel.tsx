/**
 * Trusted Sources Management Panel
 * UI for managing curated external data sources with trust scoring
 */

import { useState, useEffect } from 'react';
import {
  Shield,
  Plus,
  Check,
  X,
  RefreshCw,
  ExternalLink,
  AlertCircle,
  TrendingUp,
  Clock
} from 'lucide-react';

interface TrustedSource {
  id: string;
  source_name: string;
  source_type: 'website' | 'api' | 'dataset' | 'feed' | 'internal_document' | 'other';
  url_pattern: string;
  description?: string;
  domains: string[];
  trust_score: number;
  quality_metrics: Record<string, any>;
  status: 'active' | 'pending' | 'rejected' | 'archived';
  last_reviewed_at?: string;
  reviewer?: string;
  auto_ingest: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface TrustedSourcesPanelProps {
  onSourceApprove?: (id: string) => void;
  onSourceReject?: (id: string, reason: string) => void;
}

export function TrustedSourcesPanel({ onSourceApprove, onSourceReject }: TrustedSourcesPanelProps) {
  const [sources, setSources] = useState<TrustedSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'active' | 'pending' | 'rejected'>('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedSource, setSelectedSource] = useState<TrustedSource | null>(null);

  // Form state for new source
  const [newSource, setNewSource] = useState({
    source_name: '',
    source_type: 'website' as TrustedSource['source_type'],
    url_pattern: '',
    description: '',
    domains: [] as string[],
    auto_ingest: false,
    notes: ''
  });

  useEffect(() => {
    loadSources();
  }, []);

  async function loadSources() {
    setLoading(true);
    try {
      const response = await fetch('/api/memory/tables/memory_trusted_sources/rows?limit=1000');
      
      // Check if response is OK
      if (!response.ok) {
        console.warn('Trusted sources endpoint not available:', response.status);
        setSources([]);
        return;
      }
      
      // Check content type to avoid JSON parse errors
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.warn('Trusted sources endpoint returned non-JSON response');
        setSources([]);
        return;
      }
      
      const data = await response.json();
      setSources(data.rows || []);
    } catch (err) {
      console.error('Failed to load trusted sources:', err);
      setSources([]); // Set empty array on error to prevent crashes
    } finally {
      setLoading(false);
    }
  }

  async function handleAddSource() {
    try {
      const response = await fetch('/api/memory/tables/memory_trusted_sources/rows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newSource,
          status: 'pending',
          trust_score: 0.0,
          quality_metrics: {}
        })
      });

      if (response.ok) {
        await loadSources();
        setShowAddForm(false);
        resetForm();
      }
    } catch (err) {
      console.error('Failed to add source:', err);
      alert('Failed to add source');
    }
  }

  async function handleApprove(id: string) {
    try {
      await fetch(`/api/memory/tables/memory_trusted_sources/rows/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'active',
          last_reviewed_at: new Date().toISOString(),
          reviewer: 'user'
        })
      });
      
      await loadSources();
      if (onSourceApprove) onSourceApprove(id);
    } catch (err) {
      console.error('Failed to approve source:', err);
    }
  }

  async function handleReject(id: string) {
    const reason = prompt('Reason for rejection:');
    if (!reason) return;

    try {
      await fetch(`/api/memory/tables/memory_trusted_sources/rows/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'rejected',
          notes: reason,
          last_reviewed_at: new Date().toISOString(),
          reviewer: 'user'
        })
      });
      
      await loadSources();
      if (onSourceReject) onSourceReject(id, reason);
    } catch (err) {
      console.error('Failed to reject source:', err);
    }
  }

  function resetForm() {
    setNewSource({
      source_name: '',
      source_type: 'website',
      url_pattern: '',
      description: '',
      domains: [],
      auto_ingest: false,
      notes: ''
    });
  }

  const filteredSources = sources.filter(s => 
    filter === 'all' || s.status === filter
  );

  const getTrustBadgeColor = (score: number) => {
    if (score >= 0.8) return 'text-green-400 bg-green-900/30';
    if (score >= 0.5) return 'text-yellow-400 bg-yellow-900/30';
    return 'text-red-400 bg-red-900/30';
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      active: 'text-green-400 bg-green-900/30',
      pending: 'text-yellow-400 bg-yellow-900/30',
      rejected: 'text-red-400 bg-red-900/30',
      archived: 'text-gray-400 bg-gray-900/30'
    };
    return colors[status as keyof typeof colors] || colors.archived;
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-blue-400" />
            <div>
              <h2 className="text-xl font-semibold">Trusted Sources</h2>
              <p className="text-sm text-gray-400">Curated data sources with trust scoring</p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={loadSources}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add Source
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          {(['all', 'active', 'pending', 'rejected'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
              {f !== 'all' && (
                <span className="ml-2 text-xs opacity-75">
                  {sources.filter(s => s.status === f).length}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Add Source Form */}
      {showAddForm && (
        <div className="p-4 border-b border-gray-700 bg-gray-800">
          <h3 className="text-lg font-semibold mb-4">Add New Source</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Source Name *</label>
              <input
                type="text"
                value={newSource.source_name}
                onChange={e => setNewSource({ ...newSource, source_name: e.target.value })}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                placeholder="e.g., Financial Times"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Type *</label>
              <select
                value={newSource.source_type}
                onChange={e => setNewSource({ ...newSource, source_type: e.target.value as TrustedSource['source_type'] })}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
              >
                <option value="website">Website</option>
                <option value="api">API</option>
                <option value="dataset">Dataset</option>
                <option value="feed">Feed</option>
                <option value="internal_document">Internal Document</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="col-span-2">
              <label className="block text-sm text-gray-400 mb-1">URL Pattern *</label>
              <input
                type="text"
                value={newSource.url_pattern}
                onChange={e => setNewSource({ ...newSource, url_pattern: e.target.value })}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                placeholder="https://example.com/*"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <textarea
                value={newSource.description}
                onChange={e => setNewSource({ ...newSource, description: e.target.value })}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                rows={2}
                placeholder="Brief description of this source..."
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm text-gray-400 mb-1">Domains (comma-separated)</label>
              <input
                type="text"
                value={newSource.domains.join(', ')}
                onChange={e => setNewSource({ ...newSource, domains: e.target.value.split(',').map(d => d.trim()).filter(Boolean) })}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                placeholder="finance, economics, news"
              />
            </div>

            <div className="col-span-2 flex items-center gap-2">
              <input
                type="checkbox"
                checked={newSource.auto_ingest}
                onChange={e => setNewSource({ ...newSource, auto_ingest: e.target.checked })}
                className="w-4 h-4"
              />
              <label className="text-sm text-gray-400">Auto-ingest from this source</label>
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={handleAddSource}
              disabled={!newSource.source_name || !newSource.url_pattern}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add Source
            </button>
            <button
              onClick={() => { setShowAddForm(false); resetForm(); }}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Sources List */}
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-400" />
          </div>
        ) : filteredSources.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Shield className="w-16 h-16 mb-4 opacity-50" />
            <p>No sources found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredSources.map(source => (
              <div
                key={source.id}
                className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer"
                onClick={() => setSelectedSource(source)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{source.source_name}</h3>
                    <p className="text-sm text-gray-400">{source.source_type}</p>
                  </div>
                  
                  <div className="flex gap-2">
                    <span className={`px-2 py-1 text-xs rounded ${getTrustBadgeColor(source.trust_score)}`}>
                      <TrendingUp className="w-3 h-3 inline mr-1" />
                      {(source.trust_score * 100).toFixed(0)}%
                    </span>
                    <span className={`px-2 py-1 text-xs rounded ${getStatusBadge(source.status)}`}>
                      {source.status}
                    </span>
                  </div>
                </div>

                <div className="mb-3">
                  <a
                    href={source.url_pattern}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                    onClick={e => e.stopPropagation()}
                  >
                    {source.url_pattern}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>

                {source.description && (
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">{source.description}</p>
                )}

                {source.domains.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {source.domains.map((domain, i) => (
                      <span key={i} className="px-2 py-1 text-xs bg-gray-700 rounded">
                        {domain}
                      </span>
                    ))}
                  </div>
                )}

                {source.last_reviewed_at && (
                  <div className="text-xs text-gray-500 flex items-center gap-1 mb-2">
                    <Clock className="w-3 h-3" />
                    Reviewed: {new Date(source.last_reviewed_at).toLocaleDateString()}
                    {source.reviewer && ` by ${source.reviewer}`}
                  </div>
                )}

                {source.status === 'pending' && (
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleApprove(source.id); }}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-500 rounded text-sm transition-colors"
                    >
                      <Check className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleReject(source.id); }}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-500 rounded text-sm transition-colors"
                    >
                      <X className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected Source Detail Modal */}
      {selectedSource && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setSelectedSource(null)}
        >
          <div
            className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-semibold">{selectedSource.source_name}</h2>
                <p className="text-gray-400">{selectedSource.source_type}</p>
              </div>
              <button
                onClick={() => setSelectedSource(null)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400">URL Pattern</label>
                <p className="text-blue-400">{selectedSource.url_pattern}</p>
              </div>

              {selectedSource.description && (
                <div>
                  <label className="text-sm text-gray-400">Description</label>
                  <p>{selectedSource.description}</p>
                </div>
              )}

              <div>
                <label className="text-sm text-gray-400">Trust Score</label>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        selectedSource.trust_score >= 0.8 ? 'bg-green-500' :
                        selectedSource.trust_score >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${selectedSource.trust_score * 100}%` }}
                    />
                  </div>
                  <span>{(selectedSource.trust_score * 100).toFixed(0)}%</span>
                </div>
              </div>

              {Object.keys(selectedSource.quality_metrics).length > 0 && (
                <div>
                  <label className="text-sm text-gray-400">Quality Metrics</label>
                  <pre className="text-xs bg-gray-900 p-2 rounded overflow-auto">
                    {JSON.stringify(selectedSource.quality_metrics, null, 2)}
                  </pre>
                </div>
              )}

              {selectedSource.notes && (
                <div>
                  <label className="text-sm text-gray-400">Notes</label>
                  <p className="text-sm">{selectedSource.notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrustedSourcesPanel;
