/**
 * Memory Studio - Comprehensive Knowledge Curation Platform
 * Features: Ingestion pipelines, dashboards, governance, collaboration
 */

import { useState, useEffect } from 'react';
import { 
  Activity, BarChart3, Zap, Play, Pause, CheckCircle, XCircle,
  Clock, TrendingUp, Database, FileText, Layers, Brain, BookOpen, FolderTree
} from 'lucide-react';
import { MemoryHubPanel } from './MemoryHubPanel';
import { GraceActivityFeed } from '../components/GraceActivityFeed';
import LibrarianPanel from './LibrarianPanel';
import BookLibraryPanel from '../components/BookLibraryPanel';
import FileOrganizerPanel from '../components/FileOrganizerPanel';

interface Pipeline {
  id: string;
  name: string;
  description: string;
  file_types: string[];
  stages: number;
  output: string;
}

interface Job {
  job_id: string;
  pipeline_id: string;
  file_path: string;
  status: string;
  progress: number;
  started_at: string;
  current_stage?: number;
}

interface Metrics {
  total_jobs: number;
  complete: number;
  failed: number;
  running: number;
  average_progress: number;
  success_rate: number;
  pipeline_usage: Record<string, number>;
  active_pipelines: number;
}

import GraceOverview from '../components/GraceOverview';
import CommandPalette from '../components/CommandPalette';
import OnboardingWalkthrough from '../components/OnboardingWalkthrough';
import SelfHealingPanel from '../components/SelfHealingPanel';
import AllKernelsPanel from '../components/AllKernelsPanel';

export function MemoryStudioPanel() {
  const [view, setView] = useState<'overview' | 'workspace' | 'pipelines' | 'dashboard' | 'kernels' | 'grace' | 'librarian' | 'books' | 'organizer' | 'healing'>('overview');
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [selectedPipeline, setSelectedPipeline] = useState<string | null>(null);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(!localStorage.getItem('grace_onboarding_complete'));

  useEffect(() => {
    if (view === 'pipelines' || view === 'dashboard') {
      loadPipelines();
      loadJobs();
      loadMetrics();
    }

    // Listen for navigation events from command palette
    const handleNavigate = (e: CustomEvent) => {
      if (e.detail?.view) {
        setView(e.detail.view);
      }
    };

    window.addEventListener('navigate', handleNavigate as EventListener);
    
    // Ctrl+K for command palette
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('navigate', handleNavigate as EventListener);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [view]);

  useEffect(() => {
    // Auto-refresh jobs and metrics
    if (view === 'pipelines' || view === 'dashboard') {
      const interval = setInterval(() => {
        loadJobs();
        loadMetrics();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [view]);

  async function loadPipelines() {
    try {
      const response = await fetch('http://localhost:8000/api/ingestion/pipelines');
      const data = await response.json();
      setPipelines(data.pipelines || []);
    } catch (err) {
      console.error('Failed to load pipelines:', err);
    }
  }

  async function loadJobs() {
    try {
      const response = await fetch('http://localhost:8000/api/ingestion/jobs');
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    }
  }

  async function loadMetrics() {
    try {
      const response = await fetch('http://localhost:8000/api/ingestion/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    }
  }

  async function startPipeline(pipelineId: string, filePath: string) {
    try {
      const response = await fetch('http://localhost:8000/api/ingestion/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pipeline_id: pipelineId,
          file_path: filePath
        })
      });
      
      if (response.ok) {
        loadJobs();
      }
    } catch (err) {
      console.error('Failed to start pipeline:', err);
    }
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: '100vh', 
      background: '#0a0a0a', 
      color: '#e5e7ff'
    }}>
      {/* Top Navigation */}
      <div style={{
        display: 'flex',
        gap: '2px',
        padding: '8px 12px',
        background: 'rgba(10,12,23,0.8)',
        borderBottom: '1px solid rgba(255,255,255,0.1)'
      }}>
        <button
          onClick={() => setView('workspace')}
          style={{
            ...tabStyle,
            background: view === 'workspace' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'workspace' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <FileText size={16} />
          <span>Workspace</span>
        </button>
        <button
          onClick={() => setView('pipelines')}
          style={{
            ...tabStyle,
            background: view === 'pipelines' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'pipelines' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <Layers size={16} />
          <span>Pipelines</span>
          {jobs.filter(j => j.status.includes('running')).length > 0 && (
            <span style={{
              background: '#10b981',
              color: '#fff',
              padding: '2px 6px',
              borderRadius: '10px',
              fontSize: '0.7rem',
              fontWeight: 600
            }}>
              {jobs.filter(j => j.status.includes('running')).length}
            </span>
          )}
        </button>
        <button
          onClick={() => setView('dashboard')}
          style={{
            ...tabStyle,
            background: view === 'dashboard' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'dashboard' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <BarChart3 size={16} />
          <span>Dashboard</span>
        </button>
        <button
          onClick={() => setView('grace')}
          style={{
            ...tabStyle,
            background: view === 'grace' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'grace' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <Brain size={16} />
          <span>Grace Activity</span>
        </button>
        <button
          onClick={() => setView('librarian')}
          style={{
            ...tabStyle,
            background: view === 'librarian' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'librarian' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <BookOpen size={16} />
          <span>Librarian</span>
        </button>
        <button
          onClick={() => setView('books')}
          style={{
            ...tabStyle,
            background: view === 'books' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'books' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <BookOpen size={16} />
          <span>📚 Books</span>
        </button>
        <button
          onClick={() => setView('organizer')}
          style={{
            ...tabStyle,
            background: view === 'organizer' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'organizer' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <FolderTree size={16} />
          <span>🗂️ Organizer</span>
        </button>
        <button
          onClick={() => setView('healing')}
          style={{
            ...tabStyle,
            background: view === 'healing' ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
            color: view === 'healing' ? '#a78bfa' : '#9ca3af'
          }}
        >
          <Zap size={16} />
          <span>⚡ Self-Healing</span>
        </button>
      </div>

      {/* Content Area */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {view === 'overview' && <GraceOverview />}
        {view === 'workspace' && <MemoryHubPanel />}
        {view === 'pipelines' && <PipelinesView pipelines={pipelines} jobs={jobs} onStart={startPipeline} />}
        {view === 'dashboard' && <DashboardView metrics={metrics} jobs={jobs} />}
        {view === 'grace' && (
          <div style={{ padding: '24px', height: '100%', overflow: 'auto' }}>
            <GraceActivityFeed />
          </div>
        )}
        {view === 'librarian' && <LibrarianPanel />}
        {view === 'books' && <BookLibraryPanel />}
        {view === 'organizer' && <FileOrganizerPanel />}
        {view === 'healing' && <SelfHealingPanel />}
      </div>
      </div>
    </>
  );
}

function PipelinesView({ pipelines, jobs, onStart }: {
  pipelines: Pipeline[];
  jobs: Job[];
  onStart: (pipelineId: string, filePath: string) => void;
}) {
  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Pipeline Library */}
      <div style={{
        width: '380px',
        borderRight: '1px solid rgba(255,255,255,0.1)',
        background: 'rgba(10,12,23,0.6)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{
          padding: '16px',
          borderBottom: '1px solid rgba(255,255,255,0.1)'
        }}>
          <h3 style={{ 
            margin: 0, 
            fontSize: '1.1rem', 
            color: '#a78bfa',
            fontWeight: 700 
          }}>
            Ingestion Pipelines
          </h3>
          <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
            {pipelines.length} workflows available
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
          {pipelines.map(pipeline => (
            <div
              key={pipeline.id}
              style={{
                background: 'rgba(139, 92, 246, 0.05)',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(139, 92, 246, 0.05)'}
            >
              <div style={{
                fontWeight: 600,
                color: '#e5e7ff',
                marginBottom: '6px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <Zap size={16} color="#a78bfa" />
                {pipeline.name}
              </div>
              <div style={{
                fontSize: '0.8rem',
                color: '#9ca3af',
                marginBottom: '8px',
                lineHeight: '1.4'
              }}>
                {pipeline.description}
              </div>
              <div style={{
                display: 'flex',
                gap: '8px',
                fontSize: '0.75rem',
                color: '#6b7280'
              }}>
                <span>{pipeline.stages} stages</span>
                <span>•</span>
                <span>{pipeline.file_types.join(', ')}</span>
              </div>
              <div style={{
                marginTop: '8px',
                padding: '4px 8px',
                background: 'rgba(59, 130, 246, 0.1)',
                borderRadius: '4px',
                fontSize: '0.7rem',
                color: '#60a5fa',
                display: 'inline-block'
              }}>
                → {pipeline.output}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Jobs */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{
          padding: '16px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          background: 'rgba(10,12,23,0.6)'
        }}>
          <h3 style={{ 
            margin: 0, 
            fontSize: '1.1rem', 
            color: '#a78bfa',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Activity size={20} />
            Active Jobs
          </h3>
          <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '4px' }}>
            {jobs.length} total • {jobs.filter(j => j.status.includes('running')).length} running
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
          {jobs.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              color: '#6b7280'
            }}>
              <Activity size={48} style={{ marginBottom: '16px', opacity: 0.3 }} />
              <div>No jobs running</div>
              <div style={{ fontSize: '0.875rem', marginTop: '8px' }}>
                Start a pipeline from the Workspace
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {jobs.slice(0, 20).map(job => (
                <JobCard key={job.job_id} job={job} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function JobCard({ job }: { job: Job }) {
  const statusColor = 
    job.status === 'complete' ? '#10b981' :
    job.status === 'failed' ? '#ef4444' :
    job.status.includes('running') ? '#3b82f6' :
    '#6b7280';

  const StatusIcon = 
    job.status === 'complete' ? CheckCircle :
    job.status === 'failed' ? XCircle :
    job.status.includes('running') ? Activity :
    Clock;

  return (
    <div style={{
      background: 'rgba(30, 30, 30, 0.6)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '8px',
      padding: '14px'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '10px'
      }}>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '0.9rem',
            fontWeight: 600,
            color: '#e5e7ff',
            marginBottom: '4px'
          }}>
            {job.file_path}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
            Pipeline: {job.pipeline_id}
          </div>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          background: `${statusColor}20`,
          borderRadius: '6px',
          fontSize: '0.75rem',
          color: statusColor,
          fontWeight: 600
        }}>
          <StatusIcon size={14} />
          {job.status}
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{
        height: '6px',
        background: 'rgba(255,255,255,0.1)',
        borderRadius: '3px',
        overflow: 'hidden',
        marginBottom: '8px'
      }}>
        <div style={{
          height: '100%',
          width: `${job.progress}%`,
          background: statusColor,
          transition: 'width 0.5s'
        }} />
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.7rem',
        color: '#6b7280'
      }}>
        <span>{job.progress}% complete</span>
        <span>{new Date(job.started_at).toLocaleTimeString()}</span>
      </div>
    </div>
  );
}

function DashboardView({ metrics, jobs }: { metrics: Metrics | null; jobs: Job[] }) {
  if (!metrics) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        color: '#6b7280'
      }}>
        Loading metrics...
      </div>
    );
  }

  return (
    <div style={{
      padding: '24px',
      overflowY: 'auto',
      background: 'linear-gradient(135deg, rgba(10, 12, 23, 0.9), rgba(20, 20, 30, 0.8))'
    }}>
      <h2 style={{
        margin: '0 0 24px 0',
        fontSize: '1.5rem',
        color: '#a78bfa',
        fontWeight: 700,
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <TrendingUp size={28} />
        Ingestion Analytics
      </h2>

      {/* Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        <MetricCard
          title="Total Jobs"
          value={metrics.total_jobs}
          icon={<Database size={24} />}
          color="#3b82f6"
        />
        <MetricCard
          title="Completed"
          value={metrics.complete}
          icon={<CheckCircle size={24} />}
          color="#10b981"
          subtitle={`${metrics.success_rate}% success rate`}
        />
        <MetricCard
          title="Running"
          value={metrics.running}
          icon={<Activity size={24} />}
          color="#f59e0b"
          subtitle={`${metrics.average_progress.toFixed(0)}% avg progress`}
        />
        <MetricCard
          title="Failed"
          value={metrics.failed}
          icon={<XCircle size={24} />}
          color="#ef4444"
        />
      </div>

      {/* Pipeline Usage Chart */}
      <div style={{
        background: 'rgba(30, 30, 30, 0.6)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <h3 style={{
          margin: '0 0 16px 0',
          fontSize: '1.1rem',
          color: '#a78bfa',
          fontWeight: 600
        }}>
          Pipeline Usage
        </h3>
        {Object.entries(metrics.pipeline_usage).map(([pipeline, count]) => (
          <div key={pipeline} style={{ marginBottom: '12px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '6px',
              fontSize: '0.875rem'
            }}>
              <span style={{ color: '#e5e7ff' }}>{pipeline}</span>
              <span style={{ color: '#9ca3af' }}>{count} jobs</span>
            </div>
            <div style={{
              height: '8px',
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                height: '100%',
                width: `${(count / metrics.total_jobs) * 100}%`,
                background: 'linear-gradient(90deg, #8b5cf6, #3b82f6)',
                transition: 'width 0.5s'
              }} />
            </div>
          </div>
        ))}
      </div>

      {/* Recent Jobs */}
      <div style={{
        background: 'rgba(30, 30, 30, 0.6)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '12px',
        padding: '20px'
      }}>
        <h3 style={{
          margin: '0 0 16px 0',
          fontSize: '1.1rem',
          color: '#a78bfa',
          fontWeight: 600
        }}>
          Recent Jobs
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {jobs.slice(0, 5).map(job => (
            <JobCard key={job.job_id} job={job} />
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon, color, subtitle }: {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}) {
  return (
    <div style={{
      background: `${color}10`,
      border: `1px solid ${color}30`,
      borderRadius: '12px',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start'
      }}>
        <div style={{ color: '#9ca3af', fontSize: '0.875rem' }}>{title}</div>
        <div style={{ color }}>{icon}</div>
      </div>
      <div style={{
        fontSize: '2rem',
        fontWeight: 700,
        color: '#e5e7ff'
      }}>
        {value}
      </div>
      {subtitle && (
        <div style={{
          fontSize: '0.75rem',
          color: '#6b7280'
        }}>
          {subtitle}
        </div>
      )}
    </div>
  );
}

const tabStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '8px 16px',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  fontSize: '0.875rem',
  fontWeight: 500,
  transition: 'all 0.2s'
};
