/**
 * Agentic API Client
 * Typed client for Grace's agentic organism APIs
 */

const API_BASE = import.meta.env.VITE_API_BASE || window.location.origin;

export interface AgenticEvent {
  type: string;
  source: string;
  timestamp: string;
  data: any;
  trace_id?: string;
}

export interface AgenticAction {
  agent: string;
  action_type: string;
  timestamp: string;
  approved: boolean;
  governance_tier: string;
  trace_id?: string;
  metadata?: any;
}

export interface AgenticReflection {
  agent: string;
  action_type: string;
  outcome: string;
  timestamp: string;
  trust_delta: number;
  trace_id?: string;
}

export interface TrustScore {
  agent: string;
  action_type: string;
  trust_score: number;
  success_count: number;
  failure_count: number;
}

export interface StrategyUpdate {
  agent: string;
  action_type: string;
  old_tier: string;
  new_tier: string;
  reason: string;
  timestamp: string;
}

export interface Skill {
  name: string;
  category: string;
  description: string;
  input_schema: any;
  output_schema: any;
  governance_action_type: string;
  timeout_seconds: number;
  max_retries: number;
  capability_tags: string[];
}

export interface SkillStats {
  skill_name: string;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  average_execution_time_ms: number;
  success_rate: number;
}

export interface AgenticHealth {
  event_bus: {
    total_events: number;
    subscribers: number;
  };
  action_gateway: {
    total_actions: number;
    approval_rate: number;
  };
  reflection_loop: {
    total_reflections: number;
    learning_active: boolean;
  };
  skill_registry: {
    total_skills: number;
    categories: string[];
  };
  status: string;
}

export interface TraceData {
  trace_id: string;
  events: AgenticEvent[];
  actions: AgenticAction[];
  reflections: AgenticReflection[];
  total_events: number;
  total_actions: number;
  total_reflections: number;
}

export interface SkillExecutionResult {
  success: boolean;
  result: any;
  error?: string;
  trace_id?: string;
  execution_time_ms: number;
  metadata?: any;
}

export class AgenticApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  async getEvents(limit: number = 50, eventType?: string, traceId?: string): Promise<AgenticEvent[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (eventType) params.append('event_type', eventType);
    if (traceId) params.append('trace_id', traceId);

    const response = await fetch(`${this.baseUrl}/api/agentic/events?${params}`);
    const data = await response.json();
    return data.events || [];
  }

  async getActions(limit: number = 50, agent?: string, traceId?: string): Promise<AgenticAction[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (agent) params.append('agent', agent);
    if (traceId) params.append('trace_id', traceId);

    const response = await fetch(`${this.baseUrl}/api/agentic/actions?${params}`);
    const data = await response.json();
    return data.actions || [];
  }

  async getReflections(limit: number = 50, agent?: string): Promise<AgenticReflection[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (agent) params.append('agent', agent);

    const response = await fetch(`${this.baseUrl}/api/agentic/reflections?${params}`);
    const data = await response.json();
    return data.reflections || [];
  }

  async getTrustScores(): Promise<TrustScore[]> {
    const response = await fetch(`${this.baseUrl}/api/agentic/trust_scores`);
    const data = await response.json();
    return data.trust_scores || [];
  }

  async getStrategyUpdates(limit: number = 20): Promise<StrategyUpdate[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());

    const response = await fetch(`${this.baseUrl}/api/agentic/strategy_updates?${params}`);
    const data = await response.json();
    return data.strategy_updates || [];
  }

  async getSkills(category?: string, capabilityTag?: string): Promise<Skill[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (capabilityTag) params.append('capability_tag', capabilityTag);

    const response = await fetch(`${this.baseUrl}/api/agentic/skills?${params}`);
    const data = await response.json();
    return data.skills || [];
  }

  async getSkillStats(skillName?: string): Promise<SkillStats[]> {
    const url = skillName 
      ? `${this.baseUrl}/api/agentic/skills/${skillName}/stats`
      : `${this.baseUrl}/api/agentic/skills/stats`;
    
    const response = await fetch(url);
    const data = await response.json();
    return skillName ? [data] : (data.skills || []);
  }

  async getHealth(): Promise<AgenticHealth> {
    const response = await fetch(`${this.baseUrl}/api/agentic/health`);
    return await response.json();
  }

  async getTrace(traceId: string): Promise<TraceData> {
    const response = await fetch(`${this.baseUrl}/api/agentic/trace/${traceId}`);
    return await response.json();
  }

  async executeSkill(skillName: string, agent: string, params: any): Promise<SkillExecutionResult> {
    const response = await fetch(`${this.baseUrl}/api/agentic/skills/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        skill_name: skillName,
        agent,
        params
      })
    });
    return await response.json();
  }
}

export const agenticApi = new AgenticApiClient();
