/**
 * Clarity Framework API Client
 * Integrates Grace Clarity endpoints with the frontend
 */

import axios from 'axios';
import { API_BASE_URL, BACKEND_URL } from '../config';

export interface ClarityStatus {
  event_bus: {
    total_events: number;
    subscriber_count: number;
    event_types: string[];
  };
  manifest: {
    total_components: number;
    active_components: number;
    trust_distribution: Record<string, number>;
  };
  mesh_config: {
    total_events: number;
    priority_events: number;
    audit_events: number;
  };
}

export interface ComponentRegistration {
  component_id: string;
  component_type: string;
  trust_level: number;
  active: boolean;
  registered_at: string;
  last_heartbeat?: string;
  role_tags: string[];
  metadata: Record<string, any>;
}

export interface Event {
  event_id: string;
  event_type: string;
  source: string;
  payload: Record<string, any>;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface LoopOutput {
  loop_id: string;
  loop_type: string;
  reasoning_chain_id: string;
  parent_loop_id?: string;
  results: Record<string, any>;
  status: string;
  confidence: number;
  metadata: Record<string, any>;
  started_at: string;
  completed_at?: string;
  component_id?: string;
  trace_context: Record<string, any>;
}

/**
 * Get clarity framework status
 */
export async function getClarityStatus(): Promise<ClarityStatus> {
  const response = await axios.get(`${API_BASE_URL}/clarity/status`);
  return response.data;
}

/**
 * Get all registered components
 */
export async function getComponents(): Promise<{
  components: ComponentRegistration[];
  stats: any;
}> {
  const response = await axios.get(`${API_BASE_URL}/clarity/components`);
  return response.data;
}

/**
 * Get recent events from event bus
 */
export async function getEvents(limit: number = 100): Promise<{
  events: Event[];
  total: number;
}> {
  const response = await axios.get(`${API_BASE_URL}/clarity/events`, {
    params: { limit }
  });
  return response.data;
}

/**
 * Get trigger mesh configuration
 */
export async function getTriggerMesh(): Promise<{
  events: any[];
  routing_rules: any;
  subscriber_groups: any;
}> {
  const response = await axios.get(`${API_BASE_URL}/clarity/mesh`);
  return response.data;
}

/**
 * Get system health
 */
export async function getHealth(): Promise<{
  status: string;
  timestamp: string;
  platform: string;
  imports_successful: boolean;
  version: string;
}> {
  const response = await axios.get(`${BACKEND_URL}/health`);
  return response.data;
}

/**
 * Get full system status
 */
export async function getSystemStatus(): Promise<any> {
  const response = await axios.get(`${API_BASE_URL}/status`);
  return response.data;
}
