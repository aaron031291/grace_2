/**
 * Orb API Client - Frontend interface for Orb = World Model Hub
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8107';

export interface OrbSession {
  session_id: string;
  user_id: string;
  start_time: string;
  duration_seconds: number;
  duration_formatted: string;
  message_count: number;
  key_topics: Array<{
    topic: string;
    count: number;
    score: number;
  }>;
  status: string;
}

export interface MediaSession {
  session_id: string;
  status: string;
  message: string;
}

export interface VoiceStatus {
  voice_enabled: boolean;
  user_id: string;
  message: string;
}

export interface BackgroundTask {
  task_id: string;
  status: string;
  message: string;
}

export interface OrbStats {
  sessions: {
    active: number;
    total: number;
  };
  memory: {
    total_fragments: number;
    average_trust_score: number;
    total_size: number;
  };
  intelligence: {
    version: string;
    domain_pods: number;
    models_available: number;
  };
  governance: {
    total_tasks: number;
    pending_tasks: number;
  };
  notifications: {
    total: number;
    unread: number;
  };
  multimodal: {
    active_sessions: number;
    background_tasks: number;
    voice_enabled_users: number;
  };
}

export interface SandboxExperiment {
  experiment_id: string;
  status: string;
  title: string;
  description: string;
  metrics: Record<string, any>;
  progress: number;
}

export interface ConsensusVote {
  role: string;
  avatar: string;
  vote: string;
  confidence: number;
}

export interface FeedbackItem {
  id: string;
  title: string;
  description: string;
  priority: string;
  created_at: string;
}

export interface SovereigntyMetrics {
  autonomy_level: number;
  autonomous_decisions_30d: number;
  success_rate: number;
  learning_velocity: number;
  trust_calibration: number;
  active_sandboxes: number;
  trust_score: number;
  pending_reviews: number;
}

class OrbApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}/api/world_model_hub${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  async createSession(userId: string = 'user', metadata?: Record<string, any>) {
    return this.request<{ session_id: string; status: string; message: string }>(
      '/session/create',
      {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, metadata }),
      }
    );
  }

  async getSessionInfo(sessionId: string) {
    return this.request<OrbSession>(`/session/${sessionId}/info`);
  }

  async closeSession(sessionId: string) {
    return this.request<{ status: string; summary: any; message: string }>(
      `/session/${sessionId}/close`,
      { method: 'POST' }
    );
  }

  async startScreenShare(userId: string = 'user', qualitySettings?: Record<string, any>) {
    return this.request<MediaSession>('/multimodal/screen-share/start', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, quality_settings: qualitySettings || {} }),
    });
  }

  async stopScreenShare(sessionId: string) {
    return this.request<{ status: string; session_id: string; message: string }>(
      `/multimodal/screen-share/stop?session_id=${sessionId}`,
      { method: 'POST' }
    );
  }

  async startRecording(
    userId: string = 'user',
    mediaType: string = 'screen_recording',
    metadata?: Record<string, any>
  ) {
    return this.request<MediaSession>('/multimodal/recording/start', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, media_type: mediaType, metadata: metadata || {} }),
    });
  }

  async stopRecording(sessionId: string) {
    return this.request<{
      status: string;
      session_id: string;
      file_path: string;
      duration: number;
      message: string;
    }>(`/multimodal/recording/stop?session_id=${sessionId}`, { method: 'POST' });
  }

  async toggleVoice(userId: string = 'user', enable: boolean) {
    return this.request<VoiceStatus>(
      `/multimodal/voice/toggle?user_id=${userId}&enable=${enable}`,
      { method: 'POST' }
    );
  }

  async listExperiments() {
    return this.request<{ experiments: SandboxExperiment[]; count: number }>(
      '/sandbox/experiments'
    );
  }

  async getConsensus() {
    return this.request<{ consensus: ConsensusVote[]; count: number }>('/sandbox/consensus');
  }

  async getFeedbackQueue() {
    return this.request<{ feedback: FeedbackItem[]; count: number }>('/sandbox/feedback');
  }

  async getSovereigntyMetrics() {
    return this.request<SovereigntyMetrics>('/sandbox/sovereignty');
  }

  async createTask(taskType: string, metadata?: Record<string, any>) {
    return this.request<BackgroundTask>('/tasks', {
      method: 'POST',
      body: JSON.stringify({ task_type: taskType, metadata: metadata || {} }),
    });
  }

  async getTaskStatus(taskId: string) {
    return this.request<any>(`/tasks/${taskId}`);
  }

  async getStats() {
    return this.request<OrbStats>('/stats');
  }
}

export const orbApi = new OrbApiClient();
