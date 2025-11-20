import React, { useState, useEffect } from 'react';
import './MissionControlDashboard.css';

interface LearningStatus {
  status: string;
  total_outcomes: number;
  active_learning: boolean;
  learning_rate: number;
  model_accuracy: number;
}

interface Snapshot {
  snapshot_id: string;
  timestamp: string;
  label: string;
  verified_ok: boolean;
}

interface HealthStatus {
  overall_health: number;
  incidents_count?: number;
  healing_success_rate?: number;
}

interface ExternalLearningStatus {
  web_learning_enabled: boolean;
  github_learning_enabled: boolean;
  firefox_agent_running: boolean;
  github_token_status: 'valid' | 'missing' | 'unknown';
  google_search_quota: 'ok' | 'exhausted' | 'warning' | 'unknown';
  quota_reset_date?: string;
}

interface MissingItem {
  type: 'credential' | 'playbook' | 'config';
  name: string;
  severity: 'critical' | 'warning' | 'info';
  description: string;
  fix_available: boolean;
  fix_action?: string;
  documentation_url?: string;
}

interface MetricsData {
  mttr_seconds: number;
  mttr_target_seconds: number;
  learning_event_count: number;
  success_rate_percent: number;
  missions_resolved: number;
  missions_active: number;
  missions_failed: number;
  rag_health?: number;
  htm_health?: number;
}

interface MissionHistory {
  mission_id: string;
  status: string;
  title: string;
  subsystem: string;
  created_at: string;
  completed_at?: string;
  duration_seconds?: number;
}

interface MissionControlData {
  learning: LearningStatus | null;
  snapshots: Snapshot[];
  health: HealthStatus | null;
  tasks: any[];
  externalLearning: ExternalLearningStatus | null;
  metrics: MetricsData | null;
  missionHistory: MissionHistory[];
  missingItems: MissingItem[];
}

export const MissionControlDashboard: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [data, setData] = useState<MissionControlData>({
    learning: null,
    snapshots: [],
    health: null,
    tasks: [],
    externalLearning: null,
    metrics: null,
    missionHistory: [],
    missingItems: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [learningEvidence, setLearningEvidence] = useState<any>(null);
  const [playbookRunning, setPlaybookRunning] = useState<string | null>(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      
      // Fetch learning status
      const learningRes = await fetch('http://localhost:8017/api/learning/status');
      const learning = learningRes.ok ? await learningRes.json() : null;

      // Fetch snapshots
      const snapshotsRes = await fetch('http://localhost:8017/api/snapshots/list');
      const snapshotsData = snapshotsRes.ok ? await snapshotsRes.json() : { snapshots: [] };

      // Fetch health/incidents (if available)
      const healthRes = await fetch('http://localhost:8017/api/incidents/stats');
      const health = healthRes.ok ? await healthRes.json() : null;

      // Fetch missions/tasks
      const tasksRes = await fetch('http://localhost:8017/mission-control/missions');
      const tasksData = tasksRes.ok ? await tasksRes.json() : { missions: [] };

      // Fetch external learning status
      const externalLearning = await fetchExternalLearningStatus();

      // Fetch mission history
      const missionHistory = await fetchMissionHistory();

      // Fetch metrics (MTTR, learning events, etc.) - needs tasks and learning data
      const currentTasks = tasksData.missions || tasksData.tasks || [];
      const metrics = await fetchMetrics(currentTasks, learning);

      // Detect missing items
      const missingItems = detectMissingItems(externalLearning);

      setData({
        learning,
        snapshots: snapshotsData.snapshots || [],
        health,
        tasks: tasksData.missions || tasksData.tasks || [],
        externalLearning,
        metrics,
        missionHistory,
        missingItems
      });

      setError(null);
    } catch (err: any) {
      console.error('Dashboard fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchExternalLearningStatus = async (): Promise<ExternalLearningStatus> => {
    try {
      // Check Firefox agent status
      const pcStatusRes = await fetch('http://localhost:8017/api/pc/status');
      const pcStatus = pcStatusRes.ok ? await pcStatusRes.json() : {};
      
      // Check GitHub token from playbook status
      const playbooksRes = await fetch('http://localhost:8017/api/playbooks/status');
      const playbooksData = playbooksRes.ok ? await playbooksRes.json() : { playbooks: [] };
      
      // Find GitHub token playbook status
      const githubPlaybook = playbooksData.playbooks?.find((p: any) => 
        p.name === 'github_token_missing'
      );
      
      // Find Google search quota playbook
      const quotaPlaybook = playbooksData.playbooks?.find((p: any) => 
        p.name === 'google_search_quota_exhaustion'
      );

      return {
        web_learning_enabled: true, // Always on by default
        github_learning_enabled: !githubPlaybook || githubPlaybook.last_triggered === null,
        firefox_agent_running: pcStatus.firefox?.enabled === true,
        github_token_status: githubPlaybook?.last_triggered ? 'missing' : 'valid',
        google_search_quota: quotaPlaybook?.last_triggered ? 'exhausted' : 'ok',
        quota_reset_date: quotaPlaybook?.next_reset_date
      };
    } catch (err) {
      console.error('External learning status fetch failed:', err);
      return {
        web_learning_enabled: false,
        github_learning_enabled: false,
        firefox_agent_running: false,
        github_token_status: 'unknown',
        google_search_quota: 'unknown'
      };
    }
  };

  const fetchMetrics = async (tasks: any[], learningData: LearningStatus | null): Promise<MetricsData | null> => {
    try {
      // Fetch MTTR and guardian stats
      const guardianRes = await fetch('http://localhost:8017/api/guardian/stats');
      const guardianData = guardianRes.ok ? await guardianRes.json() : {};

      // Fetch mission analytics
      const analyticsRes = await fetch('http://localhost:8017/api/analytics/mttr-trend?period_days=30');
      const analyticsData = analyticsRes.ok ? await analyticsRes.json() : {};

      // Count learning events from learning data
      const learningEventCount = learningData?.total_outcomes || 0;

      return {
        mttr_seconds: guardianData.mttr?.mttr_seconds || guardianData.overall_health?.mttr_actual_seconds || 0,
        mttr_target_seconds: guardianData.overall_health?.mttr_target_seconds || 120,
        learning_event_count: learningEventCount,
        success_rate_percent: guardianData.mttr?.success_rate_percent || 0,
        missions_resolved: tasks.filter((t: any) => t.status === 'completed' || t.status === 'resolved').length,
        missions_active: tasks.filter((t: any) => t.status === 'active' || t.status === 'in_progress').length,
        missions_failed: tasks.filter((t: any) => t.status === 'failed').length,
        rag_health: undefined, // TODO: Add RAG health API
        htm_health: undefined  // TODO: Add HTM health API
      };
    } catch (err) {
      console.error('Metrics fetch failed:', err);
      return null;
    }
  };

  const fetchMissionHistory = async (): Promise<MissionHistory[]> => {
    try {
      const res = await fetch('http://localhost:8017/mission-control/missions?limit=20');
      if (!res.ok) return [];
      
      const data = await res.json();
      const missions = data.missions || data.tasks || [];
      
      return missions.map((m: any) => ({
        mission_id: m.mission_id || m.task_id || m.id,
        status: m.status,
        title: m.title || m.mission_type || 'Unknown',
        subsystem: m.subsystem || 'general',
        created_at: m.created_at || m.timestamp,
        completed_at: m.completed_at || m.resolved_at,
        duration_seconds: m.duration_seconds
      }));
    } catch (err) {
      console.error('Mission history fetch failed:', err);
      return [];
    }
  };

  const detectMissingItems = (externalLearning: ExternalLearningStatus | null): MissingItem[] => {
    const items: MissingItem[] = [];

    if (!externalLearning) return items;

    // Check for missing GitHub token
    if (externalLearning.github_token_status === 'missing') {
      items.push({
        type: 'credential',
        name: 'GitHub Token',
        severity: 'warning',
        description: 'GitHub token is missing. Learning from GitHub repositories is disabled.',
        fix_available: true,
        fix_action: 'Run SETUP_TOKEN.bat to configure',
        documentation_url: '/SETUP_GITHUB_TOKEN.md'
      });
    }

    // Check for exhausted Google Search quota
    if (externalLearning.google_search_quota === 'exhausted') {
      items.push({
        type: 'credential',
        name: 'Google Search Quota',
        severity: 'warning',
        description: `Google Search API quota exhausted. Using fallback search methods.${externalLearning.quota_reset_date ? ` Resets: ${externalLearning.quota_reset_date}` : ''}`,
        fix_available: false,
        documentation_url: '/.env.example'
      });
    }

    // Check for stopped Firefox agent (if needed for learning)
    if (!externalLearning.firefox_agent_running && externalLearning.web_learning_enabled) {
      items.push({
        type: 'config',
        name: 'Firefox Agent',
        severity: 'info',
        description: 'Firefox agent is not running. Some web navigation features may be limited.',
        fix_available: true,
        fix_action: 'Enable via /api/pc endpoints'
      });
    }

    // Additional credential checks (can be extended)
    // TODO: Check for OPENAI_API_KEY, ANTHROPIC_API_KEY via backend API

    return items;
  };

  const handleFixAction = async (item: MissingItem) => {
    if (item.name === 'GitHub Token') {
      // Trigger GitHub token setup
      alert('Please run SETUP_TOKEN.bat script from the project root directory to configure your GitHub token.');
      if (item.documentation_url) {
        window.open(item.documentation_url, '_blank');
      }
    } else if (item.name === 'Firefox Agent') {
      // Attempt to start Firefox agent
      try {
        const res = await fetch('http://localhost:8017/api/pc/start-firefox', {
          method: 'POST'
        });
        if (res.ok) {
          alert('Firefox agent started successfully!');
          fetchDashboard(); // Refresh to update status
        } else {
          alert('Failed to start Firefox agent. Check backend logs.');
        }
      } catch (err) {
        alert('Error starting Firefox agent: ' + (err as Error).message);
      }
    }
  };

  const runLearningEvidence = async () => {
    try {
      const res = await fetch('http://localhost:8017/api/run-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          script: 'tests/show_learning_evidence.py',
          return_output: true 
        })
      });
      if (res.ok) {
        const result = await res.json();
        setLearningEvidence(result);
      }
    } catch (err) {
      console.error('Learning evidence fetch failed:', err);
    }
  };

  const triggerPlaybook = async (playbookName: string) => {
    if (playbookRunning) {
      alert('A playbook is already running. Please wait.');
      return;
    }

    try {
      setPlaybookRunning(playbookName);
      
      // Execute playbook via unified orchestrator
      const res = await fetch('http://localhost:8017/api/unified/execute-playbook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          playbook_id: playbookName,
          params: {}
        })
      });

      if (res.ok) {
        const result = await res.json();
        alert(`Playbook "${playbookName}" triggered successfully!\n\nExecution ID: ${result.execution_id || 'N/A'}\nStatus: ${result.status || 'Running'}`);
        
        // Refresh dashboard after 3 seconds
        setTimeout(() => fetchDashboard(), 3000);
      } else {
        const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
        alert(`Failed to trigger playbook "${playbookName}":\n${error.detail || error.error || 'Unknown error'}`);
      }
    } catch (err: any) {
      alert(`Error triggering playbook "${playbookName}":\n${err.message}`);
    } finally {
      setPlaybookRunning(null);
    }
  };

  const downloadEvidenceReport = async (reportType: 'learning' | 'healing') => {
    try {
      let endpoint = '';
      let filename = '';

      if (reportType === 'learning') {
        endpoint = '/api/run-script';
        filename = `learning_evidence_${new Date().toISOString().split('T')[0]}.txt`;
        
        const res = await fetch('http://localhost:8017' + endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            script: 'tests/show_learning_evidence.py',
            return_output: true 
          })
        });

        if (res.ok) {
          const result = await res.json();
          const content = result.output || result.stdout || JSON.stringify(result, null, 2);
          
          // Create download
          const blob = new Blob([content], { type: 'text/plain' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        } else {
          alert('Failed to generate learning evidence report');
        }
      } else if (reportType === 'healing') {
        // Use guardian stats to generate healing report
        endpoint = '/api/guardian/stats';
        filename = `healing_report_${new Date().toISOString().split('T')[0]}.json`;
        
        const res = await fetch('http://localhost:8017' + endpoint);
        
        if (res.ok) {
          const result = await res.json();
          
          // Create formatted report
          const report = {
            generated_at: new Date().toISOString(),
            report_type: 'Self-Healing Evidence',
            mttr: result.mttr,
            overall_health: result.overall_health,
            network_playbooks: result.network_playbooks,
            auto_healing_playbooks: result.auto_healing_playbooks,
            summary: {
              mttr_seconds: result.mttr?.mttr_seconds || 0,
              success_rate: result.mttr?.success_rate_percent || 0,
              target_met: result.overall_health?.target_met || false
            }
          };
          
          const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        } else {
          alert('Failed to generate healing report');
        }
      }
    } catch (err: any) {
      alert(`Error downloading ${reportType} report:\n${err.message}`);
    }
  };

  const viewEvidenceReport = async (reportType: 'learning' | 'healing') => {
    try {
      if (reportType === 'learning') {
        await runLearningEvidence();
        // Show in modal or new window
        alert('Learning evidence check completed. Check the console or download the report for full details.');
      } else if (reportType === 'healing') {
        const res = await fetch('http://localhost:8017/api/guardian/stats');
        if (res.ok) {
          const result = await res.json();
          
          const summary = `
=== SELF-HEALING EVIDENCE REPORT ===

MTTR (Mean Time To Recovery): ${result.mttr?.mttr_seconds?.toFixed(2) || 0}s
Target: ${result.overall_health?.mttr_target_seconds || 120}s
Target Met: ${result.overall_health?.target_met ? 'YES ✅' : 'NO ❌'}

Success Rate: ${result.mttr?.success_rate_percent?.toFixed(0) || 0}%
Overall Health: ${result.overall_health?.status || 'unknown'}

Network Playbooks: ${JSON.stringify(result.network_playbooks || {}, null, 2)}
Auto-Healing Playbooks: ${JSON.stringify(result.auto_healing_playbooks || {}, null, 2)}
          `.trim();
          
          alert(summary);
        } else {
          alert('Failed to fetch healing report');
        }
      }
    } catch (err: any) {
      alert(`Error viewing ${reportType} report:\n${err.message}`);
    }
  };

  const restoreSnapshot = async (snapshotId: string) => {
    if (!confirm(`Restore from ${snapshotId}? This will restart the system.`)) return;
    
    try {
      const res = await fetch(`http://localhost:8017/api/snapshots/restore/${snapshotId}`, {
        method: 'POST'
      });
      if (res.ok) {
        alert('Restore initiated. Server will restart.');
      } else {
        alert('Restore failed: ' + await res.text());
      }
    } catch (err: any) {
      alert('Restore error: ' + err.message);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDashboard();
      runLearningEvidence();
      const interval = setInterval(fetchDashboard, 30000); // Refresh every 30s
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="mission-control-overlay" onClick={onClose}>
      <div className="mission-control-panel" onClick={(e) => e.stopPropagation()}>
        <div className="mission-control-header">
          <h2>🎯 Mission Control</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        {loading && <div className="loading-spinner">Loading mission control...</div>}
        {error && <div className="error-banner">⚠️ {error}</div>}

        <div className="mission-control-content">
          
          {/* External Learning Controls */}
          <div className="mc-section external-learning-section">
            <h3>🌐 External Learning Sources</h3>
            {data.externalLearning ? (
              <div className="external-learning-grid">
                <div className="external-item">
                  <div className="external-label">Web Learning:</div>
                  <div className={`external-status ${data.externalLearning.web_learning_enabled ? 'enabled' : 'disabled'}`}>
                    {data.externalLearning.web_learning_enabled ? '✅ ENABLED' : '⏸️ DISABLED'}
                  </div>
                </div>

                <div className="external-item">
                  <div className="external-label">GitHub Learning:</div>
                  <div className={`external-status ${data.externalLearning.github_learning_enabled ? 'enabled' : 'disabled'}`}>
                    {data.externalLearning.github_learning_enabled ? '✅ ENABLED' : '⚠️ DISABLED'}
                  </div>
                </div>

                <div className="external-item">
                  <div className="external-label">GitHub Token:</div>
                  <div className={`token-status status-${data.externalLearning.github_token_status}`}>
                    {data.externalLearning.github_token_status === 'valid' && '✓ Valid'}
                    {data.externalLearning.github_token_status === 'missing' && '❌ Missing'}
                    {data.externalLearning.github_token_status === 'unknown' && '❓ Unknown'}
                  </div>
                </div>

                <div className="external-item">
                  <div className="external-label">Firefox Agent:</div>
                  <div className={`external-status ${data.externalLearning.firefox_agent_running ? 'running' : 'stopped'}`}>
                    {data.externalLearning.firefox_agent_running ? '🟢 RUNNING' : '🔴 STOPPED'}
                  </div>
                </div>

                <div className="external-item full-width">
                  <div className="external-label">Google Search Quota:</div>
                  <div className={`quota-status status-${data.externalLearning.google_search_quota}`}>
                    {data.externalLearning.google_search_quota === 'ok' && '✅ OK'}
                    {data.externalLearning.google_search_quota === 'warning' && '⚠️ LOW'}
                    {data.externalLearning.google_search_quota === 'exhausted' && (
                      <>
                        ❌ EXHAUSTED
                        {data.externalLearning.quota_reset_date && (
                          <span className="quota-reset"> (Resets: {data.externalLearning.quota_reset_date})</span>
                        )}
                      </>
                    )}
                    {data.externalLearning.google_search_quota === 'unknown' && '❓ Unknown'}
                  </div>
                </div>

                {data.externalLearning.github_token_status === 'missing' && (
                  <div className="external-warning">
                    ⚠️ GitHub token missing. Some learning features may be limited.
                  </div>
                )}

                {data.externalLearning.google_search_quota === 'exhausted' && (
                  <div className="external-warning">
                    ⚠️ Google Search quota exhausted. Using fallback search methods.
                  </div>
                )}
              </div>
            ) : (
              <div className="no-data">External learning status unavailable</div>
            )}
          </div>

          {/* Missing Items Alert */}
          {data.missingItems.length > 0 && (
            <div className="mc-section missing-items-section">
              <h3>⚠️ Missing Items & Configuration</h3>
              <div className="missing-items-list">
                {data.missingItems.map((item, idx) => (
                  <div 
                    key={idx} 
                    className={`missing-item severity-${item.severity}`}
                  >
                    <div className="missing-icon">
                      {item.severity === 'critical' && '🔴'}
                      {item.severity === 'warning' && '⚠️'}
                      {item.severity === 'info' && 'ℹ️'}
                    </div>
                    <div className="missing-content">
                      <div className="missing-header">
                        <span className="missing-name">{item.name}</span>
                        <span className={`missing-type type-${item.type}`}>{item.type}</span>
                      </div>
                      <div className="missing-description">{item.description}</div>
                      {item.fix_action && (
                        <div className="missing-fix-action">{item.fix_action}</div>
                      )}
                    </div>
                    <div className="missing-actions">
                      {item.fix_available && (
                        <button 
                          className="fix-btn"
                          onClick={() => handleFixAction(item)}
                        >
                          Fix
                        </button>
                      )}
                      {item.documentation_url && (
                        <button 
                          className="docs-btn"
                          onClick={() => window.open(item.documentation_url, '_blank')}
                        >
                          Docs
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metrics & Analytics */}
          <div className="mc-section metrics-section">
            <h3>📊 System Metrics</h3>
            {data.metrics ? (
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-label">MTTR</div>
                  <div className="metric-value">
                    {data.metrics.mttr_seconds.toFixed(1)}s
                  </div>
                  <div className="metric-target">
                    Target: {data.metrics.mttr_target_seconds}s
                  </div>
                  <div className="metric-bar">
                    <div 
                      className={`metric-fill ${data.metrics.mttr_seconds <= data.metrics.mttr_target_seconds ? 'good' : 'warn'}`}
                      style={{ width: `${Math.min((data.metrics.mttr_seconds / data.metrics.mttr_target_seconds) * 100, 100)}%` }}
                    />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">Success Rate</div>
                  <div className="metric-value">
                    {data.metrics.success_rate_percent.toFixed(0)}%
                  </div>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill good"
                      style={{ width: `${data.metrics.success_rate_percent}%` }}
                    />
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">Learning Events</div>
                  <div className="metric-value">
                    {data.metrics.learning_event_count}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">Missions</div>
                  <div className="mission-stats">
                    <span className="stat-resolved">✓ {data.metrics.missions_resolved}</span>
                    <span className="stat-active">⟳ {data.metrics.missions_active}</span>
                    <span className="stat-failed">✗ {data.metrics.missions_failed}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-data">No metrics available</div>
            )}
          </div>

          {/* Mission History */}
          <div className="mc-section mission-history-section">
            <h3>📜 Mission History</h3>
            {data.missionHistory.length > 0 ? (
              <div className="mission-history-list">
                <div className="history-summary">
                  <div className="summary-stat">
                    <span className="summary-label">Resolved:</span>
                    <span className="summary-value resolved-count">
                      {data.missionHistory.filter(m => m.status === 'completed' || m.status === 'resolved').length}
                    </span>
                  </div>
                  <div className="summary-stat">
                    <span className="summary-label">Active:</span>
                    <span className="summary-value active-count">
                      {data.missionHistory.filter(m => m.status === 'active' || m.status === 'in_progress').length}
                    </span>
                  </div>
                  <div className="summary-stat">
                    <span className="summary-label">Failed:</span>
                    <span className="summary-value failed-count">
                      {data.missionHistory.filter(m => m.status === 'failed').length}
                    </span>
                  </div>
                </div>
                
                <div className="history-items">
                  {data.missionHistory.slice(0, 8).map((mission) => (
                    <div 
                      key={mission.mission_id} 
                      className={`history-item status-${mission.status}`}
                      onClick={() => window.open(`/missions/${mission.mission_id}`, '_blank')}
                    >
                      <div className="history-status">
                        {mission.status === 'completed' || mission.status === 'resolved' ? '✓' : 
                         mission.status === 'failed' ? '✗' : '⟳'}
                      </div>
                      <div className="history-details">
                        <div className="history-title">{mission.title}</div>
                        <div className="history-meta">
                          <span className="history-subsystem">{mission.subsystem}</span>
                          {mission.duration_seconds && (
                            <span className="history-duration">{mission.duration_seconds.toFixed(1)}s</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="no-data">No mission history available</div>
            )}
          </div>

          {/* Learning System Status */}
          <div className="mc-section learning-section">
            <h3>🎓 Learning System</h3>
            {data.learning ? (
              <div className="learning-stats">
                <div className="stat-item">
                  <span className="stat-label">Status:</span>
                  <span className={`stat-value ${data.learning.active_learning ? 'active' : 'inactive'}`}>
                    {data.learning.active_learning ? '✅ ACTIVE' : '⚠️ INACTIVE'}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Learning Rate:</span>
                  <span className="stat-value">{(data.learning.learning_rate * 100).toFixed(0)}%</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Model Accuracy:</span>
                  <span className="stat-value">{(data.learning.model_accuracy * 100).toFixed(0)}%</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Outcomes:</span>
                  <span className="stat-value">{data.learning.total_outcomes}</span>
                </div>
                
                {learningEvidence && learningEvidence.exit_code === 0 && (
                  <div className="evidence-badge">✅ Evidence Verified</div>
                )}
              </div>
            ) : (
              <div className="no-data">No learning data available</div>
            )}
          </div>

          {/* Self-Healing Status */}
          <div className="mc-section healing-section">
            <h3>🔧 Self-Healing</h3>
            {data.health ? (
              <div className="healing-stats">
                <div className="stat-item">
                  <span className="stat-label">Incidents:</span>
                  <span className="stat-value">{data.health.incidents_count || 0}</span>
                </div>
                {data.health.healing_success_rate !== undefined && (
                  <div className="stat-item">
                    <span className="stat-label">Success Rate:</span>
                    <span className="stat-value">{(data.health.healing_success_rate * 100).toFixed(0)}%</span>
                  </div>
                )}
                <div className="stat-item">
                  <span className="stat-label">Health:</span>
                  <div className="health-bar">
                    <div 
                      className="health-fill" 
                      style={{ width: `${(data.health.overall_health || 0) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-data">No healing data available</div>
            )}
          </div>

          {/* Snapshots */}
          <div className="mc-section snapshots-section">
            <h3>📸 Boot Snapshots</h3>
            {data.snapshots.length > 0 ? (
              <div className="snapshots-list">
                {data.snapshots.slice(0, 5).map((snap) => (
                  <div key={snap.snapshot_id} className="snapshot-item">
                    <div className="snapshot-info">
                      <span className="snapshot-id">{snap.snapshot_id}</span>
                      {snap.verified_ok && <span className="verified-badge">✓ OK</span>}
                      <span className="snapshot-time">{new Date(snap.timestamp).toLocaleString()}</span>
                    </div>
                    <button 
                      className="restore-btn"
                      onClick={() => restoreSnapshot(snap.snapshot_id)}
                    >
                      Restore
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">No snapshots available</div>
            )}
          </div>

          {/* Tasks/Missions */}
          <div className="mc-section tasks-section">
            <h3>📋 Active Missions</h3>
            {data.tasks.length > 0 ? (
              <div className="tasks-list">
                {data.tasks.slice(0, 10).map((task, idx) => (
                  <div key={task.mission_id || task.task_id || idx} className="task-item">
                    <div className="task-status" data-status={task.status || 'unknown'}>
                      {task.status || 'pending'}
                    </div>
                    <div className="task-details">
                      <div className="task-title">{task.title || task.mission_type || 'Task'}</div>
                      <div className="task-meta">
                        {task.subsystem && <span className="task-subsystem">{task.subsystem}</span>}
                        {task.severity && <span className="task-severity">{task.severity}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">No active missions</div>
            )}
          </div>
        </div>

        <div className="mission-control-footer">
          <div className="footer-section">
            <button className="refresh-btn" onClick={fetchDashboard}>
              🔄 Refresh
            </button>
            <button className="evidence-btn" onClick={runLearningEvidence}>
              🧪 Check Learning Evidence
            </button>
          </div>

          <div className="footer-section playbook-triggers">
            <label>Quick Playbooks:</label>
            <button 
              className="playbook-btn"
              onClick={() => triggerPlaybook('port_inventory_cleanup')}
              disabled={playbookRunning !== null}
            >
              {playbookRunning === 'port_inventory_cleanup' ? '⏳' : '🔧'} Port Cleanup
            </button>
            <button 
              className="playbook-btn"
              onClick={() => triggerPlaybook('faiss_lock_recovery')}
              disabled={playbookRunning !== null}
            >
              {playbookRunning === 'faiss_lock_recovery' ? '⏳' : '🔓'} FAISS Unlock
            </button>
            <button 
              className="playbook-btn"
              onClick={() => triggerPlaybook('google_search_quota')}
              disabled={playbookRunning !== null}
            >
              {playbookRunning === 'google_search_quota' ? '⏳' : '🔍'} Quota Check
            </button>
          </div>

          <div className="footer-section report-downloads">
            <label>Evidence Reports:</label>
            <button 
              className="download-btn"
              onClick={() => viewEvidenceReport('learning')}
            >
              👁️ View Learning
            </button>
            <button 
              className="download-btn"
              onClick={() => downloadEvidenceReport('learning')}
            >
              ⬇️ Download Learning
            </button>
            <button 
              className="download-btn"
              onClick={() => viewEvidenceReport('healing')}
            >
              👁️ View Healing
            </button>
            <button 
              className="download-btn"
              onClick={() => downloadEvidenceReport('healing')}
            >
              ⬇️ Download Healing
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
