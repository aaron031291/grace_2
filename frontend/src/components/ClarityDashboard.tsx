/**
 * Clarity Dashboard Component
 * Displays Clarity Framework status, components, and events
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  Box,
  Zap,
  Clock,
  Shield,
  AlertCircle
} from 'lucide-react';
import {
  getClarityStatus,
  getComponents,
  getEvents,
  type ClarityStatus,
  type ComponentRegistration,
  type Event
} from '../services/clarityApi';

export function ClarityDashboard() {
  const [status, setStatus] = useState<ClarityStatus | null>(null);
  const [components, setComponents] = useState<ComponentRegistration[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadClarityData();
    const interval = setInterval(loadClarityData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  async function loadClarityData() {
    try {
      const [statusData, componentsData, eventsData] = await Promise.all([
        getClarityStatus(),
        getComponents(),
        getEvents(50)
      ]);

      setStatus(statusData);
      setComponents(componentsData.components || []);
      setEvents(eventsData.events || []);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span>Error loading clarity data: {error}</span>
        </div>
      </div>
    );
  }

  const trustLevelNames = ['Untrusted', 'Low', 'Medium', 'High', 'Verified'];
  const trustColors = ['gray', 'red', 'yellow', 'green', 'blue'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Clarity Framework</h2>
        <span className="text-sm text-gray-500">
          Auto-refreshing every 5s
        </span>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Event Bus */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg border border-gray-200 p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold">Event Bus</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Events</span>
              <span className="font-medium">{status?.event_bus.total_events || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Subscribers</span>
              <span className="font-medium">{status?.event_bus.subscriber_count || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Event Types</span>
              <span className="font-medium">{status?.event_bus.event_types?.length || 0}</span>
            </div>
          </div>
        </motion.div>

        {/* Component Manifest */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg border border-gray-200 p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <Box className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold">Components</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total</span>
              <span className="font-medium">{status?.manifest.total_components || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Active</span>
              <span className="font-medium text-green-600">
                {status?.manifest.active_components || 0}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Trigger Mesh */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg border border-gray-200 p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold">Trigger Mesh</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Events</span>
              <span className="font-medium">{status?.mesh_config.total_events || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Priority</span>
              <span className="font-medium">{status?.mesh_config.priority_events || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Audit</span>
              <span className="font-medium">{status?.mesh_config.audit_events || 0}</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Trust Distribution */}
      {status?.manifest.trust_distribution && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg border border-gray-200 p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold">Trust Distribution</h3>
          </div>
          <div className="flex gap-2">
            {Object.entries(status.manifest.trust_distribution).map(([level, count], idx) => (
              <div
                key={level}
                className={`flex-1 bg-${trustColors[idx]}-100 rounded p-3 text-center`}
              >
                <div className="text-2xl font-bold">{count}</div>
                <div className="text-xs text-gray-600">{trustLevelNames[idx]}</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Components List */}
      {components.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg border border-gray-200 p-6"
        >
          <h3 className="font-semibold mb-4">Registered Components</h3>
          <div className="space-y-2">
            {components.map((comp) => (
              <div
                key={comp.component_id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded"
              >
                <div className="flex-1">
                  <div className="font-medium">{comp.component_type}</div>
                  <div className="text-xs text-gray-500">ID: {comp.component_id.slice(0, 8)}...</div>
                </div>
                <div className="flex items-center gap-2">
                  {comp.role_tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      comp.active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {comp.active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
                    Trust: {trustLevelNames[comp.trust_level]}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Recent Events */}
      {events.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-lg border border-gray-200 p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Clock className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold">Recent Events</h3>
            <span className="text-sm text-gray-500">Last {events.length}</span>
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {events.slice(0, 20).map((event) => (
              <div
                key={event.event_id}
                className="flex items-start gap-3 p-3 bg-gray-50 rounded text-sm"
              >
                <div className="flex-shrink-0 text-xs text-gray-500 w-16">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </div>
                <div className="flex-1">
                  <div className="font-medium">{event.event_type}</div>
                  <div className="text-xs text-gray-600">
                    Source: {event.source}
                  </div>
                  {Object.keys(event.payload).length > 0 && (
                    <div className="text-xs text-gray-500 mt-1">
                      Payload: {JSON.stringify(event.payload).slice(0, 100)}...
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
