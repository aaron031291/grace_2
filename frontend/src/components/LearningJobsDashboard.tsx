/**
 * Learning Jobs Dashboard - Monitor and Manage Autonomous Learning
 * 
 * Features:
 * - View learning job queue
 * - Monitor job progress
 * - Failed job triage
 * - Retry/cancel jobs
 * - Learning metrics and analytics
 * - Domain coverage visualization
 */

import React, { useState, useEffect } from 'react';
import { 
  Play, Pause, RefreshCw, XCircle, CheckCircle, 
  Clock, AlertTriangle, TrendingUp, BookOpen, Target 
} from 'lucide-react';
import './LearningJobsDashboard.css';

interface LearningJob {
  id: string;
  domain: string;
  source: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  started_at?: string;
  completed_at?: string;
  duration?: number;
  metrics: {
    documents_processed?: number;
    knowledge_entries?: number;
    confidence_score?: number;
  };
  error?: string;
}

interface LearningMetrics {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  avg_duration: number;
  knowledge_entries_added: number;
  domains_learned: number;
}

export function LearningJobsDashboard() {
  const [jobs, setJobs] = useState<LearningJob[]>([]);
  const [metrics, setMetrics] = useState<LearningMetrics>({
    total_jobs: 0,
    completed_jobs: 0,
    failed_jobs: 0,
    avg_duration: 0,
    knowledge_entries_added: 0,
    domains_learned: 0,
  });
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [selectedJob, setSelectedJob] = useState<LearningJob | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchMetrics();
    const interval = setInterval(() => {
      fetchJobs();
      fetchMetrics();
    }, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    setIsLoading(true);
    try {
      const mockJobs: LearningJob[] = [
        {
          id: 'job-001',
          domain: 'kubernetes',
          source: 'https://kubernetes.io/docs',
          status: 'running',
          progress: 65,
          started_at: new Date(Date.now() - 300000).toISOString(),
          metrics: {
            documents_processed: 32,
            knowledge_entries: 156,
            confidence_score: 0.87,
          },
        },
        {
          id: 'job-002',
          domain: 'docker',
          source: 'https://docs.docker.com',
          status: 'completed',
          progress: 100,
          started_at: new Date(Date.now() - 600000).toISOString(),
          completed_at: new Date(Date.now() - 300000).toISOString(),
          duration: 300,
          metrics: {
            documents_processed: 45,
            knowledge_entries: 203,
            confidence_score: 0.92,
          },
        },
        {
          id: 'job-003',
          domain: 'terraform',
          source: 'https://www.terraform.io/docs',
          status: 'failed',
          progress: 35,
          started_at: new Date(Date.now() - 900000).toISOString(),
          completed_at: new Date(Date.now() - 800000).toISOString(),
          duration: 100,
          metrics: {
            documents_processed: 12,
            knowledge_entries: 45,
            confidence_score: 0.65,
          },
          error: 'Failed to fetch documentation: Connection timeout',
        },
        {
          id: 'job-004',
          domain: 'ansible',
          source: 'https://docs.ansible.com',
          status: 'queued',
          progress: 0,
          metrics: {},
        },
      ];
      setJobs(mockJobs);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      setMetrics({
        total_jobs: 47,
        completed_jobs: 38,
        failed_jobs: 5,
        avg_duration: 245,
        knowledge_entries_added: 8542,
        domains_learned: 23,
      });
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const handleRetryJob = async (jobId: string) => {
    try {
      console.log('Retrying job:', jobId);
      await fetchJobs();
    } catch (error) {
      console.error('Failed to retry job:', error);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      console.log('Cancelling job:', jobId);
      setJobs(prev => prev.map(j => 
        j.id === jobId ? { ...j, status: 'cancelled' as const } : j
      ));
    } catch (error) {
      console.error('Failed to cancel job:', error);
    }
  };

  const filteredJobs = jobs.filter(j => 
    filterStatus === 'all' || j.status === filterStatus
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued': return <Clock className="w-4 h-4" />;
      case 'running': return <Play className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <XCircle className="w-4 h-4" />;
      case 'cancelled': return <Pause className="w-4 h-4" />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued': return '#64748b';
      case 'running': return '#3b82f6';
      case 'completed': return '#10b981';
      case 'failed': return '#ef4444';
      case 'cancelled': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="learning-dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-left">
          <h2>Learning Jobs Dashboard</h2>
        </div>
        <div className="header-right">
          <button className="refresh-btn" onClick={fetchJobs} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'spinning' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#3b82f6' }}>
            <Target className="w-6 h-6" />
          </div>
          <div className="metric-content">
            <div className="metric-label">Total Jobs</div>
            <div className="metric-value">{metrics.total_jobs}</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#10b981' }}>
            <CheckCircle className="w-6 h-6" />
          </div>
          <div className="metric-content">
            <div className="metric-label">Completed</div>
            <div className="metric-value">{metrics.completed_jobs}</div>
            <div className="metric-trend">
              {((metrics.completed_jobs / metrics.total_jobs) * 100).toFixed(0)}% success rate
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#ef4444' }}>
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div className="metric-content">
            <div className="metric-label">Failed</div>
            <div className="metric-value">{metrics.failed_jobs}</div>
            <div className="metric-trend">Need attention</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#8b5cf6' }}>
            <BookOpen className="w-6 h-6" />
          </div>
          <div className="metric-content">
            <div className="metric-label">Knowledge Entries</div>
            <div className="metric-value">{metrics.knowledge_entries_added.toLocaleString()}</div>
            <div className="metric-trend">
              <TrendingUp className="w-3 h-3" />
              Growing
            </div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#f59e0b' }}>
            <Target className="w-6 h-6" />
          </div>
          <div className="metric-content">
            <div className="metric-label">Domains Learned</div>
            <div className="metric-value">{metrics.domains_learned}</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#06b6d4' }}>
            <Clock className="w-6 h-6" />
          </div>
          <div className="metric-content">
            <div className="metric-label">Avg Duration</div>
            <div className="metric-value">{formatDuration(metrics.avg_duration)}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="dashboard-filters">
        <button
          className={`filter-btn ${filterStatus === 'all' ? 'active' : ''}`}
          onClick={() => setFilterStatus('all')}
        >
          All ({jobs.length})
        </button>
        <button
          className={`filter-btn ${filterStatus === 'queued' ? 'active' : ''}`}
          onClick={() => setFilterStatus('queued')}
        >
          Queued ({jobs.filter(j => j.status === 'queued').length})
        </button>
        <button
          className={`filter-btn ${filterStatus === 'running' ? 'active' : ''}`}
          onClick={() => setFilterStatus('running')}
        >
          Running ({jobs.filter(j => j.status === 'running').length})
        </button>
        <button
          className={`filter-btn ${filterStatus === 'completed' ? 'active' : ''}`}
          onClick={() => setFilterStatus('completed')}
        >
          Completed ({jobs.filter(j => j.status === 'completed').length})
        </button>
        <button
          className={`filter-btn ${filterStatus === 'failed' ? 'active' : ''}`}
          onClick={() => setFilterStatus('failed')}
        >
          Failed ({jobs.filter(j => j.status === 'failed').length})
        </button>
      </div>

      {/* Jobs List */}
      <div className="jobs-list">
        {filteredJobs.length === 0 ? (
          <div className="empty-state">
            <BookOpen className="w-12 h-12 text-gray-600" />
            <p>No learning jobs found</p>
            <span>Start a new learning job to begin</span>
          </div>
        ) : (
          filteredJobs.map(job => (
            <div
              key={job.id}
              className="job-card"
              onClick={() => setSelectedJob(job)}
            >
              <div className="job-header">
                <div className="job-title-section">
                  <div 
                    className="job-status-icon" 
                    style={{ color: getStatusColor(job.status) }}
                  >
                    {getStatusIcon(job.status)}
                  </div>
                  <div>
                    <h3>{job.domain}</h3>
                    <p className="job-source">{job.source}</p>
                  </div>
                </div>
                <div className="job-status" style={{ color: getStatusColor(job.status) }}>
                  {job.status}
                </div>
              </div>

              {job.status === 'running' && (
                <div className="job-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${job.progress}%`,
                        background: getStatusColor(job.status)
                      }}
                    />
                  </div>
                  <span className="progress-text">{job.progress}%</span>
                </div>
              )}

              <div className="job-metrics">
                {job.metrics.documents_processed !== undefined && (
                  <div className="job-metric">
                    <span className="metric-label">Documents:</span>
                    <span className="metric-value">{job.metrics.documents_processed}</span>
                  </div>
                )}
                {job.metrics.knowledge_entries !== undefined && (
                  <div className="job-metric">
                    <span className="metric-label">Entries:</span>
                    <span className="metric-value">{job.metrics.knowledge_entries}</span>
                  </div>
                )}
                {job.metrics.confidence_score !== undefined && (
                  <div className="job-metric">
                    <span className="metric-label">Confidence:</span>
                    <span className="metric-value">{(job.metrics.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                )}
                {job.duration !== undefined && (
                  <div className="job-metric">
                    <span className="metric-label">Duration:</span>
                    <span className="metric-value">{formatDuration(job.duration)}</span>
                  </div>
                )}
              </div>

              {job.error && (
                <div className="job-error">
                  <AlertTriangle className="w-4 h-4" />
                  <span>{job.error}</span>
                </div>
              )}

              <div className="job-actions">
                {job.status === 'failed' && (
                  <button
                    className="job-action-btn retry"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRetryJob(job.id);
                    }}
                  >
                    <RefreshCw className="w-4 h-4" />
                    Retry
                  </button>
                )}
                {job.status === 'running' && (
                  <button
                    className="job-action-btn cancel"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCancelJob(job.id);
                    }}
                  >
                    <XCircle className="w-4 h-4" />
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Detail Panel */}
      {selectedJob && (
        <div className="detail-panel-overlay" onClick={() => setSelectedJob(null)}>
          <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
            <div className="detail-header">
              <h3>{selectedJob.domain}</h3>
              <button onClick={() => setSelectedJob(null)}>×</button>
            </div>
            <div className="detail-content">
              <div className="detail-section">
                <h4>Source</h4>
                <p>{selectedJob.source}</p>
              </div>
              <div className="detail-section">
                <h4>Status</h4>
                <div style={{ color: getStatusColor(selectedJob.status) }}>
                  {getStatusIcon(selectedJob.status)}
                  <span style={{ marginLeft: '0.5rem' }}>{selectedJob.status}</span>
                </div>
              </div>
              {selectedJob.started_at && (
                <div className="detail-section">
                  <h4>Started At</h4>
                  <p>{new Date(selectedJob.started_at).toLocaleString()}</p>
                </div>
              )}
              {selectedJob.completed_at && (
                <div className="detail-section">
                  <h4>Completed At</h4>
                  <p>{new Date(selectedJob.completed_at).toLocaleString()}</p>
                </div>
              )}
              <div className="detail-section">
                <h4>Metrics</h4>
                <ul>
                  {Object.entries(selectedJob.metrics).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key.replace(/_/g, ' ')}:</strong> {value}
                    </li>
                  ))}
                </ul>
              </div>
              {selectedJob.error && (
                <div className="detail-section">
                  <h4>Error</h4>
                  <div className="error-box">
                    <AlertTriangle className="w-4 h-4" />
                    <p>{selectedJob.error}</p>
                  </div>
                </div>
              )}
            </div>
            {selectedJob.status === 'failed' && (
              <div className="detail-actions">
                <button
                  className="detail-btn retry"
                  onClick={() => {
                    handleRetryJob(selectedJob.id);
                    setSelectedJob(null);
                  }}
                >
                  <RefreshCw className="w-4 h-4" />
                  Retry Job
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default LearningJobsDashboard;
