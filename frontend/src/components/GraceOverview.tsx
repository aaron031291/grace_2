/**
 * Grace Overview - Landing page showing complete system status
 * Metrics, activity timeline, quick actions
 */

import React, { useState, useEffect } from 'react';
import { Activity, Book, FolderTree, CheckCircle, AlertCircle, TrendingUp, Clock, Zap } from 'lucide-react';

interface SystemMetrics {
  total_documents: number;
  ingestion_backlog: number;
  pending_approvals: number;
  active_agents: number;
  trust_average: number;
  recent_activity: number;
}

interface LibrarianEvent {
  timestamp: string;
  event_type: string;
  details: string;
}

export function GraceOverview() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    total_documents: 0,
    ingestion_backlog: 0,
    pending_approvals: 0,
    active_agents: 0,
    trust_average: 0,
    recent_activity: 0
  });
  const [timeline, setTimeline] = useState<LibrarianEvent[]>([]);

  useEffect(() => {
    loadMetrics();
    loadTimeline();

    const interval = setInterval(() => {
      loadMetrics();
      loadTimeline();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      // Aggregate from multiple endpoints
      const [books, librarian, activity] = await Promise.all([
        fetch('http://localhost:8000/api/books/stats').then(r => r.json()).catch(() => ({})),
        fetch('http://localhost:8000/api/librarian/status').then(r => r.json()).catch(() => ({})),
        fetch('http://localhost:8000/api/books/activity?limit=10').then(r => r.json()).catch(() => [])
      ]);

      setMetrics({
        total_documents: books.total_books || 0,
        ingestion_backlog: (librarian.queues?.ingestion || 0) + (librarian.queues?.schema || 0),
        pending_approvals: 0, // TODO: from unified logic
        active_agents: Object.values(librarian.active_agents || {}).reduce((sum: number, count) => sum + (count as number), 0),
        trust_average: books.average_trust_score || 0,
        recent_activity: Array.isArray(activity) ? activity.length : 0
      });
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const loadTimeline = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/books/activity?limit=20');
      const data = await response.json();
      
      if (Array.isArray(data)) {
        setTimeline(data.map(item => ({
          timestamp: item.timestamp,
          event_type: item.action,
          details: item.target
        })));
      }
    } catch (error) {
      console.error('Failed to load timeline:', error);
    }
  };

  const getEventIcon = (eventType: string) => {
    if (eventType.includes('complete')) return <CheckCircle className="w-4 h-4 text-green-400" />;
    if (eventType.includes('fail')) return <AlertCircle className="w-4 h-4 text-red-400" />;
    if (eventType.includes('schema')) return <FolderTree className="w-4 h-4 text-blue-400" />;
    if (eventType.includes('ingest')) return <Book className="w-4 h-4 text-purple-400" />;
    return <Activity className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div className="grace-overview h-full overflow-auto bg-gradient-to-br from-gray-900 via-purple-900/10 to-gray-900 text-white">
      {/* Hero Section */}
      <div className="px-8 py-12 border-b border-gray-800">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Grace Intelligence Platform
          </h1>
          <p className="text-gray-400 text-lg">
            Autonomous knowledge curation with verified trust and intelligent organization
          </p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="px-8 py-8">
        <div className="max-w-7xl mx-auto grid grid-cols-6 gap-6">
          <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <Book className="w-8 h-8 text-purple-400" />
              <div className="text-xs text-gray-400 uppercase tracking-wider">Documents</div>
            </div>
            <div className="text-4xl font-bold text-white">{metrics.total_documents}</div>
            <div className="text-sm text-gray-400 mt-1">Total ingested</div>
          </div>

          <div className="bg-gradient-to-br from-yellow-900/30 to-orange-900/30 backdrop-blur-sm border border-yellow-500/30 rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <Clock className="w-8 h-8 text-yellow-400" />
              <div className="text-xs text-gray-400 uppercase tracking-wider">Backlog</div>
            </div>
            <div className="text-4xl font-bold text-white">{metrics.ingestion_backlog}</div>
            <div className="text-sm text-gray-400 mt-1">Queued for processing</div>
          </div>

          <div className="bg-gradient-to-br from-blue-900/30 to-cyan-900/30 backdrop-blur-sm border border-blue-500/30 rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <AlertCircle className="w-8 h-8 text-blue-400" />
              <div className="text-xs text-gray-400 uppercase tracking-wider">Approvals</div>
            </div>
            <div className="text-4xl font-bold text-white">{metrics.pending_approvals}</div>
            <div className="text-sm text-gray-400 mt-1">Awaiting review</div>
          </div>

          <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 backdrop-blur-sm border border-green-500/30 rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <Zap className="w-8 h-8 text-green-400" />
              <div className="text-xs text-gray-400 uppercase tracking-wider">Active Agents</div>
            </div>
            <div className="text-4xl font-bold text-white">{metrics.active_agents}</div>
            <div className="text-sm text-gray-400 mt-1">Processing now</div>
          </div>

          <div className="bg-gradient-to-br from-pink-900/30 to-purple-900/30 backdrop-blur-sm border border-pink-500/30 rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <TrendingUp className="w-8 h-8 text-pink-400" />
              <div className="text-xs text-gray-400 uppercase tracking-wider">Trust Score</div>
            </div>
            <div className="text-4xl font-bold text-white">{(metrics.trust_average * 100).toFixed(0)}%</div>
            <div className="text-sm text-gray-400 mt-1">Average trust</div>
          </div>

          <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 backdrop-blur-sm border border-indigo-500/30 rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-3">
              <Activity className="w-8 h-8 text-indigo-400" />
              <div className="text-xs text-gray-400 uppercase tracking-wider">Activity</div>
            </div>
            <div className="text-4xl font-bold text-white">{metrics.recent_activity}</div>
            <div className="text-sm text-gray-400 mt-1">Events today</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-8 py-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-4 gap-4">
            <button className="bg-purple-600 hover:bg-purple-700 px-6 py-4 rounded-lg text-left transition-all group">
              <Book className="w-6 h-6 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-semibold">Add Books</div>
              <div className="text-xs text-purple-200 mt-1">Drop PDFs to learn</div>
            </button>
            <button className="bg-blue-600 hover:bg-blue-700 px-6 py-4 rounded-lg text-left transition-all group">
              <FolderTree className="w-6 h-6 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-semibold">Organize Files</div>
              <div className="text-xs text-blue-200 mt-1">AI-powered sorting</div>
            </button>
            <button className="bg-green-600 hover:bg-green-700 px-6 py-4 rounded-lg text-left transition-all group">
              <CheckCircle className="w-6 h-6 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-semibold">Review Approvals</div>
              <div className="text-xs text-green-200 mt-1">Schema & trust</div>
            </button>
            <button className="bg-pink-600 hover:bg-pink-700 px-6 py-4 rounded-lg text-left transition-all group">
              <TrendingUp className="w-6 h-6 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-semibold">View Analytics</div>
              <div className="text-xs text-pink-200 mt-1">Trust & performance</div>
            </button>
          </div>
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-xl font-semibold mb-4">Librarian Activity Timeline</h2>
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {timeline.map((event, idx) => (
                <div key={idx} className="flex items-start gap-4 p-3 rounded-lg hover:bg-gray-700/30 transition-all">
                  <div className="mt-1">{getEventIcon(event.event_type)}</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{event.event_type.replace(/_/g, ' ').toUpperCase()}</span>
                      <span className="text-xs text-gray-500">{new Date(event.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="text-sm text-gray-400 mt-1">{event.details}</div>
                  </div>
                </div>
              ))}
              {timeline.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  No recent activity. Drop a file to see the Librarian in action!
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GraceOverview;
