/**
 * Librarian Suggestions Panel
 * Shows intelligent suggestions and pending actions
 */

import { useState, useEffect } from 'react';
import {
  Lightbulb,
  AlertCircle,
  TrendingDown,
  FileQuestion,
  RefreshCw,
  Check,
  X
} from 'lucide-react';

interface Suggestion {
  id: string;
  type: 'schema_approval' | 'trust_warning' | 'stale_data' | 'ingestion_needed' | 'review_needed';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  actionLabel: string;
  actionEndpoint: string;
  metadata?: any;
}

export function LibrarianSuggestions() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSuggestions();
    
    const interval = setInterval(loadSuggestions, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadSuggestions() {
    try {
      const response = await fetch('/api/librarian/suggestions');
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (err) {
      console.error('Failed to load suggestions:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(suggestion: Suggestion) {
    try {
      const response = await fetch(suggestion.actionEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ suggestion_id: suggestion.id })
      });

      if (response.ok) {
        setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
      }
    } catch (err) {
      console.error('Action failed:', err);
      alert('Action failed');
    }
  }

  async function dismissSuggestion(id: string) {
    setSuggestions(prev => prev.filter(s => s.id !== id));
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'schema_approval':
        return <AlertCircle className="w-5 h-5 text-orange-400" />;
      case 'trust_warning':
        return <TrendingDown className="w-5 h-5 text-red-400" />;
      case 'stale_data':
        return <RefreshCw className="w-5 h-5 text-yellow-400" />;
      case 'ingestion_needed':
        return <FileQuestion className="w-5 h-5 text-blue-400" />;
      default:
        return <Lightbulb className="w-5 h-5 text-purple-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-500 bg-red-900/20';
      case 'medium':
        return 'border-yellow-500 bg-yellow-900/20';
      default:
        return 'border-blue-500 bg-blue-900/20';
    }
  };

  if (loading) {
    return (
      <div className="p-4 text-center text-gray-400">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
        Loading suggestions...
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <Lightbulb className="w-12 h-12 mx-auto mb-2 opacity-30" />
        <p className="text-sm">No suggestions at the moment</p>
        <p className="text-xs mt-1">Librarian is monitoring your workspace</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-4">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-purple-400" />
        <h3 className="font-semibold">Librarian Suggests</h3>
        <span className="px-2 py-0.5 bg-purple-900 text-purple-300 text-xs rounded">
          {suggestions.length}
        </span>
      </div>

      {suggestions.map(suggestion => (
        <div
          key={suggestion.id}
          className={`p-3 rounded-lg border-l-4 ${getPriorityColor(suggestion.priority)}`}
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              {getIcon(suggestion.type)}
            </div>

            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-sm mb-1">{suggestion.title}</h4>
              <p className="text-sm text-gray-400">{suggestion.description}</p>

              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => handleAction(suggestion)}
                  className="px-3 py-1 text-xs bg-purple-600 hover:bg-purple-500 rounded transition-colors flex items-center gap-1"
                >
                  <Check className="w-3 h-3" />
                  {suggestion.actionLabel}
                </button>
                <button
                  onClick={() => dismissSuggestion(suggestion.id)}
                  className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors flex items-center gap-1"
                >
                  <X className="w-3 h-3" />
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
