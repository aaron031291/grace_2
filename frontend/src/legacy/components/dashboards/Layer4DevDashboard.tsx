/**
 * Layer 4: Development Dashboard
 * 
 * Shows:
 * - Recent logs
 * - Playbook execution
 * - Diagnostic messages
 * - Self-healing actions
 * - Debug controls
 */

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface LogEntry {
  timestamp: string;
  level: string;
  source: string;
  message: string;
  metadata?: any;
}

interface PlaybookExecution {
  playbook_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  success?: boolean;
}

export function Layer4DevDashboard() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [playbooks, setPlaybooks] = useState<PlaybookExecution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const logsResponse = await axios.get('/api/logs/recent?limit=50');
        setLogs(logsResponse.data.logs || []);

        const playbooksResponse = await axios.get('/api/playbooks/executions?limit=20');
        setPlaybooks(playbooksResponse.data.executions || []);
      } catch (error) {
        console.error('Failed to fetch dev data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 20000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-center py-12">Loading dev data...</div>;
  }

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR': case 'CRITICAL': return 'text-red-400 bg-red-500/20';
      case 'WARNING': case 'WARN': return 'text-yellow-400 bg-yellow-500/20';
      case 'INFO': return 'text-blue-400 bg-blue-500/20';
      case 'DEBUG': return 'text-gray-400 bg-gray-500/20';
      default: return 'text-gray-300 bg-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Playbook Executions */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Recent Playbook Executions</h3>
        <div className="space-y-2">
          {playbooks.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No recent playbook executions</p>
          ) : (
            playbooks.map((pb, idx) => (
              <div key={idx} className="bg-gray-700 p-3 rounded flex justify-between items-center">
                <div>
                  <p className="font-mono text-sm">{pb.playbook_id}</p>
                  <p className="text-xs text-gray-400">{pb.started_at}</p>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    pb.success === true ? 'bg-green-500/20 text-green-400' :
                    pb.success === false ? 'bg-red-500/20 text-red-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {pb.status}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Log Stream */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Log Stream</h3>
        <div className="space-y-1 font-mono text-xs max-h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No recent logs</p>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className={`p-2 rounded ${getLevelColor(log.level)}`}>
                <span className="text-gray-500">{log.timestamp}</span>
                {' '}
                <span className="font-bold">[{log.level}]</span>
                {' '}
                <span className="text-gray-400">{log.source}:</span>
                {' '}
                <span>{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
