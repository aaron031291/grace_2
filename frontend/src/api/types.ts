/**
 * Grace API TypeScript Types
 * Auto-generated from backend Pydantic schemas
 * Includes execution_trace and data_provenance for all responses
 */

// ============ Core Traceability Types ============

export interface ExecutionStep {
  step_number: number;
  component: string;
  action: string;
  duration_ms: number;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  data_source?: string;
  cache_hit: boolean;
  governance_checked: boolean;
  error?: string;
}

export interface ExecutionTrace {
  request_id: string;
  total_duration_ms: number;
  steps: ExecutionStep[];
  data_sources_used: string[];
  agents_involved: string[];
  governance_checks: number;
  cache_hits: number;
  database_queries: number;
  external_api_calls?: number;
}

export interface DataProvenance {
  source_type: string;
  source_id?: string;
  timestamp: string;
  confidence: number;
  verified: boolean;
}

// ============ Generic Response Types ============

export interface SuccessResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
  operation_id?: string;
  timestamp: string;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
  request_id?: string;
  suggestions: string[];
  documentation_url?: string;
  timestamp: string;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

// ============ Health Response ============

export interface ServiceHealth {
  status: string;
  last_check: string;
  uptime_seconds?: number;
  metrics?: Record<string, any>;
}

export interface SystemMetrics {
  total_requests: number;
  active_sessions: number;
  memory_usage_mb: number;
  cpu_usage_percent: number;
  database_connections: number;
  event_queue_size: number;
}

export interface HealthResponse {
  status: string;
  message: string;
  version: string;
  uptime_seconds: number;
  services: Record<string, ServiceHealth>;
  metrics: SystemMetrics;
  timestamp: string;
}

// ============ Verification Responses ============

export interface VerificationAuditResponse {
  audit_logs: Array<Record<string, any>>;
  total: number;
  time_range_hours: number;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

export interface VerificationMissionDetailResponse {
  mission_id: string;
  mission_name: string;
  mission_goal?: string;
  status: string;
  progress_ratio: number;
  confidence_score: number;
  completed_actions: number;
  total_planned_actions: number;
  started_at: string;
  completed_at?: string;
  contracts: Array<Record<string, any>>;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

// ============ Memory Responses ============

export interface MemoryArtifact {
  id: number;
  path: string;
  domain: string;
  category: string;
  status: string;
  version: number;
  size?: number;
  updated_at?: string;
}

export interface MemoryTreeResponse {
  tree: Record<string, any>;
  flat_list: MemoryArtifact[];
}

// ============ Task Responses ============

export interface TaskResponse {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  auto_generated: boolean;
  created_at: string;
  completed_at?: string;
  created_by?: string;
  assigned_to?: string;
  execution_trace?: ExecutionTrace;
}

// ============ Chat Responses ============

export interface ChatMetadata {
  operation_id: string;
  duration_ms: number;
  user_memory_id?: number;
  grace_memory_id?: number;
  intent_detected?: string;
  intent_confidence?: number;
  agents_consulted: string[];
  memory_items_retrieved: number;
  governance_checks: number;
  agentic_hops: number;
}

export interface ChatResponseEnhanced {
  response: string;
  domain?: string;
  metadata: ChatMetadata;
  degraded: boolean;
  request_id?: string;
  suggestions: string[];
  code_snippets: Array<{language: string; code: string}>;
  files_referenced: string[];
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

// ============ Ingest Responses ============

export interface IngestTextResponse {
  status: string;
  artifact_id: number;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

export interface IngestArtifactsListResponse {
  artifacts: Array<Record<string, any>>;
  count: number;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

// ============ Plugin Responses ============

export interface PluginsListResponse {
  plugins: Array<Record<string, any>>;
  count: number;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

export interface PluginActionResponse {
  status: string;
  plugin: string;
  message: string;
  execution_trace?: ExecutionTrace;
  data_provenance: DataProvenance[];
}

// ============ Add more as needed ============
