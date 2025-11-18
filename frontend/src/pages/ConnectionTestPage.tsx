/**
 * Connection Test Page
 * Tests backend-frontend connection and displays execution traces
 */

import { useEffect, useState } from 'react';
import { apiUrl, WS_BASE_URL } from './config';
import type { HealthResponse, VerificationAuditResponse, ExecutionTrace, DataProvenance } from '../api/types';

export function ConnectionTestPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [audit, setAudit] = useState<VerificationAuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function testConnection() {
      try {
        // Test health endpoint
        const healthRes = await fetch(apiUrl('/health');
        const healthData = await healthRes.json();
        setHealth(healthData);

        // Test verification audit (no auth required)
        const auditRes = await fetch(apiUrl('/api/verification/audit?limit=5');
        const auditData = await auditRes.json();
        setAudit(auditData);

        setLoading(false);
      } catch (err: any) {
        setError(err.message);
        setLoading(false);
      }
    }

    testConnection();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Testing Backend Connection...</h1>
        <div className="animate-pulse">Connecting to http://localhost:8000</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4 text-red-600">❌ Connection Error</h1>
        <p className="text-red-500">{error}</p>
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 rounded">
          <h3 className="font-bold mb-2">Troubleshooting:</h3>
          <ul className="list-disc ml-5 space-y-1">
            <li>Is backend running? Check <code>http://localhost:8000/health</code></li>
            <li>CORS enabled for http://localhost:5173?</li>
            <li>Firewall blocking connection?</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">✅ Backend Connected!</h1>

      {/* Health Status */}
      <div className="mb-8 p-6 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <h2 className="text-xl font-bold mb-4">Health Check</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
            <p className="text-lg font-bold text-green-600">{health?.status}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Version</p>
            <p className="text-lg font-bold">{health?.version}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Uptime</p>
            <p className="text-lg font-bold">{Math.floor((health?.uptime_seconds ?? 0) / 60)} minutes</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">CPU</p>
            <p className="text-lg font-bold">{health?.metrics.cpu_usage_percent.toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Execution Trace Example */}
      {health?.execution_trace && (
        <div className="mb-8 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <h2 className="text-xl font-bold mb-4">🔍 Execution Trace</h2>
          <ExecutionTraceView trace={health.execution_trace} />
        </div>
      )}

      {/* Verification Audit */}
      {audit && (
        <div className="mb-8 p-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
          <h2 className="text-xl font-bold mb-4">📋 Verification Audit</h2>
          <p><strong>Total Logs:</strong> {audit.total}</p>
          <p><strong>Time Range:</strong> {audit.time_range_hours} hours</p>
          
          {audit.execution_trace && (
            <div className="mt-4">
              <h3 className="font-bold mb-2">Pipeline Trace:</h3>
              <ExecutionTraceView trace={audit.execution_trace} />
            </div>
          )}

          {audit.data_provenance && audit.data_provenance.length > 0 && (
            <div className="mt-4">
              <h3 className="font-bold mb-2">Data Provenance:</h3>
              <DataProvenanceView provenance={audit.data_provenance} />
            </div>
          )}
        </div>
      )}

      {/* Services Status */}
      <div className="p-6 bg-gray-50 dark:bg-gray-900/20 rounded-lg border border-gray-200 dark:border-gray-800">
        <h2 className="text-xl font-bold mb-4">Services Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {health && Object.entries(health.services).map(([name, service]) => (
            <div key={name} className="p-3 bg-white dark:bg-gray-800 rounded border">
              <p className="text-sm font-bold">{name}</p>
              <p className={`text-xs ${service.status === 'connected' || service.status === 'active' || service.status === 'ready' || service.status === 'autonomous' || service.status === 'enforcing' || service.status === 'monitoring' ? 'text-green-600' : 'text-red-600'}`}>
                {service.status}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Execution Trace Component
function ExecutionTraceView({ trace }: { trace: ExecutionTrace }) {
  return (
    <div className="space-y-2">
      <div className="flex gap-4 text-sm">
        <span><strong>Request ID:</strong> {trace.request_id}</span>
        <span><strong>Duration:</strong> {trace.total_duration_ms}ms</span>
        <span><strong>DB Queries:</strong> {trace.database_queries}</span>
        <span><strong>Cache Hits:</strong> {trace.cache_hits}</span>
      </div>

      <div className="mt-3">
        <p className="text-sm font-bold mb-2">Pipeline Steps:</p>
        <div className="space-y-1">
          {trace.steps.map((step, i) => (
            <div key={i} className="flex items-center gap-2 text-xs p-2 bg-white dark:bg-gray-800 rounded">
              <span className="font-mono bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">{step.step_number}</span>
              <span className="font-bold text-blue-600 dark:text-blue-400">{step.component}</span>
              <span>→</span>
              <span>{step.action}</span>
              <span className="ml-auto text-gray-500">{step.duration_ms}ms</span>
              {step.data_source && <span className="text-purple-600">📊 {step.data_source}</span>}
              {step.cache_hit && <span className="text-green-600">⚡ cached</span>}
              {step.error && <span className="text-red-600">❌ {step.error}</span>}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>
          <strong>Data Sources:</strong>
          <p className="text-xs text-gray-600">{trace.data_sources_used.join(', ')}</p>
        </div>
        <div>
          <strong>Agents Involved:</strong>
          <p className="text-xs text-gray-600">{trace.agents_involved.length > 0 ? trace.agents_involved.join(', ') : 'None'}</p>
        </div>
      </div>
    </div>
  );
}

// Data Provenance Component
function DataProvenanceView({ provenance }: { provenance: DataProvenance[] }) {
  return (
    <div className="space-y-2">
      {provenance.map((p, i) => (
        <div key={i} className="flex items-center gap-3 text-xs p-2 bg-white dark:bg-gray-800 rounded">
          <span className="font-bold text-purple-600">{p.source_type}</span>
          {p.source_id && <span className="text-gray-600">ID: {p.source_id}</span>}
          <span className={`font-bold ${p.verified ? 'text-green-600' : 'text-yellow-600'}`}>
            {p.verified ? '✅ Verified' : '⚠️ Unverified'}
          </span>
          <span className="text-blue-600">Confidence: {(p.confidence * 100).toFixed(0)}%</span>
          <span className="ml-auto text-gray-500">{new Date(p.timestamp).toLocaleTimeString()}</span>
        </div>
      ))}
    </div>
  );
}
