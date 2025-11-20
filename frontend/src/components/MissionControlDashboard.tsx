import React, { useState, useEffect } from 'react';
import { HealthMeter } from './HealthMeter';
import { TelemetryStrip } from './TelemetryStrip';
import { BackgroundTasksDrawer } from './BackgroundTasksDrawer';
import { RemoteCockpit } from './RemoteCockpit';
import { IncidentsAPI, type Incident, type SelfHealingStats } from '../api/incidents';
import { LearningAPI, type WhitelistEntry, type ServiceAccount } from '../api/learning';
import { MissionControlAPI, type Mission } from '../api/missions';
import { ChaosAPI, type ChaosCampaign, type ChaosStatus } from '../api/chaos';
import './MissionControlDashboard.css';

interface LearningStatus {
  status: string;
  total_outcomes: number;
  active_learning: boolean;
  learning_rate: number;
  model_accuracy: number;
}

interface LearningOutcome {
  outcome_id: string;
  timestamp: string;
  context: string;
  action_taken: string;
  result: string;
  confidence: number;
  learned_pattern?: string;
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
  learningOutcomes: LearningOutcome[];
  snapshots: Snapshot[];
  health: HealthStatus | null;
  tasks: any[];
  externalLearning: ExternalLearningStatus | null;
  metrics: MetricsData | null;
  missionHistory: MissionHistory[];
  missingItems: MissingItem[];
  selfHealingStats: SelfHealingStats | null;
  incidents: Incident[];
  whitelist: WhitelistEntry[];
  serviceAccounts: ServiceAccount[];
  missions: Mission[];
  chaosStatus: ChaosStatus | null;
  chaosCampaigns: ChaosCampaign[];
}

export const MissionControlDashboard: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
    const [data, setData] = useState<MissionControlData>({
      learning: null,
      learningOutcomes: [],
      snapshots: [],
      health: null,
      tasks: [],
      externalLearning: null,
      metrics: null,
      missionHistory: [],
      missingItems: [],
      selfHealingStats: null,
      incidents: [],
      whitelist: [],
      serviceAccounts: [],
      missions: [],
      chaosStatus: null,
      chaosCampaigns: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [learningEvidence, setLearningEvidence] = useState<any>(null);
    const [playbookRunning, setPlaybookRunning] = useState<string | null>(null);
    const [tasksDrawerOpen, setTasksDrawerOpen] = useState(false);
    const [remoteCockpitOpen, setRemoteCockpitOpen] = useState(false);

    const fetchDashboard = async () => {
        try {
            setLoading(true);

            // Fetch learning status
            const learningRes = await fetch('http://localhost:8017/api/learning/status');
            const learning = learningRes.ok ? await learningRes.json() : null;

            // Fetch learning outcomes
            const outcomesRes = await fetch('http://localhost:8017/api/learning/outcomes');
            const outcomesData = outcomesRes.ok ? await outcomesRes.json() : { outcomes: [] };
            const learningOutcomes = outcomesData.outcomes || outcomesData.data || [];

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

            // Fetch self-healing data
            const { selfHealingStats, incidents } = await fetchSelfHealingData();

            // Fetch learning controls data
            const { whitelist, serviceAccounts } = await fetchLearningControlsData();

            // Fetch missions data
            const missions = await fetchMissions();

            // Fetch chaos data
            const { chaosStatus, chaosCampaigns } = await fetchChaosData();

            // Detect missing items
            const missingItems = detectMissingItems(externalLearning);

            setData({
              learning,
              learningOutcomes,
              snapshots: snapshotsData.snapshots || [],
              health,
              tasks: tasksData.missions || tasksData.tasks || [],
              externalLearning,
              metrics,
              missionHistory,
              missingItems,
              selfHealingStats,
              incidents,
              whitelist,
              serviceAccounts,
              missions,
              chaosStatus,
              chaosCampaigns
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

    const fetchSelfHealingData = async (): Promise<{ selfHealingStats: SelfHealingStats | null; incidents: Incident[] }> => {
      try {
        const [stats, incidentsData] = await Promise.all([
          IncidentsAPI.getStats(),
          IncidentsAPI.getIncidents(20)
        ]);

        return {
          selfHealingStats: stats,
          incidents: incidentsData.incidents || []
        };
      } catch (err) {
        console.error('Self-healing data fetch failed:', err);
        return {
          selfHealingStats: null,
          incidents: []
        };
      }
    };

    const fetchLearningControlsData = async (): Promise<{ whitelist: WhitelistEntry[]; serviceAccounts: ServiceAccount[] }> => {
      try {
        const [whitelist, serviceAccounts] = await Promise.all([
          LearningAPI.getWhitelist(),
          LearningAPI.getServiceAccounts()
        ]);

        return {
          whitelist: whitelist || [],
          serviceAccounts: serviceAccounts || []
        };
      } catch (err) {
        console.error('Learning controls data fetch failed:', err);
        return {
          whitelist: [],
          serviceAccounts: []
        };
      }
    };

    const fetchMissions = async (): Promise<Mission[]> => {
      try {
        const data = await MissionControlAPI.listMissions({ limit: 50 });
        return data.missions || [];
      } catch (err) {
        console.error('Missions fetch failed:', err);
        return [];
      }
    };

    const fetchChaosData = async (): Promise<{ chaosStatus: ChaosStatus | null; chaosCampaigns: ChaosCampaign[] }> => {
      try {
        const [status, campaigns] = await Promise.all([
          ChaosAPI.getStatus(),
          ChaosAPI.getCampaigns()
        ]);

        return {
          chaosStatus: status,
          chaosCampaigns: campaigns || []
        };
      } catch (err) {
        console.error('Chaos data fetch failed:', err);
        return {
          chaosStatus: null,
          chaosCampaigns: []
        };
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

                {/* Telemetry Strip at the top */}
                <div className="mc-telemetry-wrapper">
                    <TelemetryStrip />
                </div>

                <div className="mission-control-content">

                    {/* System Overview - HealthMeter */}
                    <div className="mc-section health-meter-section">
                        <HealthMeter />
                    </div>

                    {/* Quick Actions */}
                    <div className="mc-section quick-actions-section">
                        <h3>⚡ Quick Access</h3>
                        <div className="quick-actions-grid">
                            <button
                                className="quick-action-btn"
                                onClick={() => setTasksDrawerOpen(true)}
                            >
                                <span className="action-icon">📋</span>
                                <span className="action-label">Background Tasks</span>
                                <span className="action-badge">{data.tasks.length}</span>
                            </button>

                            <button
                                className="quick-action-btn"
                                onClick={() => setRemoteCockpitOpen(true)}
                            >
                                <span className="action-icon">🎛️</span>
                                <span className="action-label">Remote Cockpit</span>
                            </button>

                            <button
                                className="quick-action-btn"
                                onClick={runLearningEvidence}
                            >
                                <span className="action-icon">🧪</span>
                                <span className="action-label">Learning Evidence</span>
                            </button>

                            <button
                                className="quick-action-btn"
                                onClick={fetchDashboard}
                            >
                                <span className="action-icon">🔄</span>
                                <span className="action-label">Refresh All</span>
                            </button>
                        </div>
                    </div>

                    {/* Learning Controls & Service Accounts */}
                    <div className="mc-section learning-controls-section">
                      <h3>🎛️ Learning Controls</h3>
                      
                      {/* Service Account Status */}
                      <div className="service-accounts-grid">
                        {data.serviceAccounts.map((account) => {
                          const quotaPercent = account.quota_used && account.quota_limit 
                            ? (account.quota_used / account.quota_limit) * 100 
                            : null;
                          const isQuotaWarning = quotaPercent && quotaPercent > 80;
                          const isQuotaCritical = quotaPercent && quotaPercent > 95;

                          return (
                            <div key={account.name} className={`service-account-card status-${account.status}`}>
                              <div className="account-header">
                                <span className="account-name">{account.name}</span>
                                <span className={`account-status ${account.status}`}>
                                  {account.status === 'active' && '✅'}
                                  {account.status === 'missing' && '❌'}
                                  {account.status === 'expired' && '⚠️'}
                                  {account.status === 'quota_exceeded' && '🚫'}
                                </span>
                              </div>
                              
                              {quotaPercent !== null && (
                                <div className="account-quota">
                                  <div className="quota-label">
                                    Quota: {account.quota_used}/{account.quota_limit}
                                    {isQuotaCritical && ' ⚠️ CRITICAL'}
                                    {isQuotaWarning && !isQuotaCritical && ' ⚠️'}
                                  </div>
                                  <div className="quota-bar">
                                    <div 
                                      className={`quota-fill ${isQuotaCritical ? 'critical' : isQuotaWarning ? 'warning' : 'ok'}`}
                                      style={{ width: `${quotaPercent}%` }}
                                    />
                                  </div>
                                  {account.quota_reset && (
                                    <div className="quota-reset-info">
                                      Resets: {new Date(account.quota_reset).toLocaleString()}
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {account.last_used && (
                                <div className="account-last-used">
                                  Last used: {new Date(account.last_used).toLocaleTimeString()}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      {/* Learning Toggles */}
                      <div className="learning-toggles">
                        <div className="toggle-item">
                          <label className="toggle-label">
                            <input 
                              type="checkbox" 
                              checked={data.externalLearning?.web_learning_enabled || false}
                              onChange={async (e) => {
                                try {
                                  await LearningAPI.toggleWebLearning(e.target.checked);
                                  await fetchDashboard();
                                } catch (err) {
                                  console.error('Failed to toggle web learning:', err);
                                }
                              }}
                            />
                            <span className="toggle-switch"></span>
                            <span className="toggle-text">Web Learning</span>
                          </label>
                        </div>

                        <div className="toggle-item">
                          <label className="toggle-label">
                            <input 
                              type="checkbox" 
                              checked={data.externalLearning?.github_learning_enabled || false}
                              onChange={async (e) => {
                                try {
                                  await LearningAPI.toggleGitHubLearning(e.target.checked);
                                  await fetchDashboard();
                                } catch (err) {
                                  console.error('Failed to toggle GitHub learning:', err);
                                }
                              }}
                            />
                            <span className="toggle-switch"></span>
                            <span className="toggle-text">GitHub Learning</span>
                          </label>
                        </div>
                      </div>

                      {/* Whitelist Management */}
                      <div className="whitelist-section">
                        <h4 className="whitelist-title">📋 Learning Source Whitelist ({data.whitelist.length})</h4>
                        <div className="whitelist-list">
                          {data.whitelist.slice(0, 5).map((entry) => (
                            <div key={entry.id} className="whitelist-entry">
                              <div className="entry-info">
                                <span className="entry-domain">{entry.domain}</span>
                                <span className="entry-type">{entry.source_type}</span>
                                {entry.trust_score && (
                                  <span className="entry-trust">{entry.trust_score}% trust</span>
                                )}
                              </div>
                              {entry.reason && (
                                <div className="entry-reason">{entry.reason}</div>
                              )}
                              <button 
                                className="entry-remove-btn"
                                onClick={async () => {
                                  if (confirm(`Remove ${entry.domain} from whitelist?`)) {
                                    try {
                                      await LearningAPI.removeFromWhitelist(entry.id);
                                      await fetchDashboard();
                                    } catch (err) {
                                      console.error('Failed to remove whitelist entry:', err);
                                    }
                                  }
                                }}
                              >
                                Remove
                              </button>
                            </div>
                          ))}
                        </div>

                        {/* Add to Whitelist Form */}
                        <div className="whitelist-add-form">
                          <input 
                            type="text" 
                            placeholder="example.com" 
                            className="whitelist-input"
                            id="whitelist-domain-input"
                          />
                          <select className="whitelist-type-select" id="whitelist-type-select">
                            <option value="domain">Domain</option>
                            <option value="url">URL</option>
                            <option value="api">API</option>
                            <option value="repository">Repository</option>
                          </select>
                          <button 
                            className="whitelist-add-btn"
                            onClick={async () => {
                              const input = document.getElementById('whitelist-domain-input') as HTMLInputElement;
                              const select = document.getElementById('whitelist-type-select') as HTMLSelectElement;
                              
                              if (input.value.trim()) {
                                try {
                                  await LearningAPI.addToWhitelist(input.value.trim(), select.value);
                                  input.value = '';
                                  await fetchDashboard();
                                } catch (err) {
                                  console.error('Failed to add whitelist entry:', err);
                                  alert('Failed to add to whitelist');
                                }
                              }
                            }}
                          >
                            Add Source
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* External Learning Sources Summary */}
                    <div className="mc-section external-learning-section">
                      <h3>🌐 External Learning Status</h3>
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

                    {/* Learning System Status - Enhanced */}
                    <div className="mc-section learning-section">
                      <h3>🎓 Learning System</h3>
                      {data.learning ? (
                        <>
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

                          {/* Latest Learning Outcomes */}
                          {data.learningOutcomes.length > 0 && (
                            <div className="learning-outcomes">
                              <h4 className="outcomes-title">📝 Latest Learning Outcomes ({data.learningOutcomes.length})</h4>
                              <div className="outcomes-list">
                                {data.learningOutcomes.slice(0, 5).map((outcome) => (
                                  <div key={outcome.outcome_id} className="outcome-card">
                                    <div className="outcome-header">
                                      <span className="outcome-timestamp">
                                        {new Date(outcome.timestamp).toLocaleString()}
                                      </span>
                                      <span className="outcome-confidence" style={{
                                        color: outcome.confidence >= 0.8 ? '#00ff88' : outcome.confidence >= 0.6 ? '#ffaa00' : '#ff4444'
                                      }}>
                                        {(outcome.confidence * 100).toFixed(0)}% confidence
                                      </span>
                                    </div>
                                    <div className="outcome-context">{outcome.context}</div>
                                    <div className="outcome-action">
                                      <strong>Action:</strong> {outcome.action_taken}
                                    </div>
                                    <div className="outcome-result">
                                      <strong>Result:</strong> {outcome.result}
                                    </div>
                                    {outcome.learned_pattern && (
                                      <div className="outcome-pattern">
                                        💡 Pattern: {outcome.learned_pattern}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="no-data">No learning data available</div>
                      )}
                    </div>

                    {/* Self-Healing Insights - Enhanced */}
                    <div className="mc-section healing-section">
                      <h3>🔧 Self-Healing Insights</h3>
                      {data.selfHealingStats ? (
                        <>
                          <div className="healing-stats">
                            <div className="stat-item">
                              <span className="stat-label">Total Incidents:</span>
                              <span className="stat-value">{data.selfHealingStats.total_incidents}</span>
                            </div>
                            <div className="stat-item">
                              <span className="stat-label">Active Now:</span>
                              <span className="stat-value active-count">{data.selfHealingStats.active_incidents}</span>
                            </div>
                            <div className="stat-item">
                              <span className="stat-label">Resolved Today:</span>
                              <span className="stat-value resolved-count">{data.selfHealingStats.resolved_today}</span>
                            </div>
                            <div className="stat-item">
                              <span className="stat-label">MTTR:</span>
                              <span className="stat-value">{data.selfHealingStats.average_resolution_time.toFixed(1)}s</span>
                            </div>
                            <div className="stat-item">
                              <span className="stat-label">Success Rate:</span>
                              <span className="stat-value">
                                {(data.selfHealingStats.success_rate * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>

                          {/* Latest Incidents */}
                          {data.incidents.length > 0 && (
                            <div className="incidents-section">
                              <h4 className="incidents-title">
                                🚨 Recent Incidents ({data.incidents.length})
                              </h4>
                              <div className="incidents-list">
                                {data.incidents.slice(0, 5).map((incident) => {
                                  const isActive = incident.status === 'pending' || incident.status === 'healing';
                                  const detectedTime = new Date(incident.detected_at);
                                  const resolvedTime = incident.resolved_at ? new Date(incident.resolved_at) : null;
                                  const duration = resolvedTime 
                                    ? ((resolvedTime.getTime() - detectedTime.getTime()) / 1000).toFixed(1)
                                    : null;

                                  return (
                                    <div 
                                      key={incident.id} 
                                      className={`incident-card severity-${incident.severity} status-${incident.status}`}
                                    >
                                      <div className="incident-header">
                                        <div className="incident-type">
                                          <span className="incident-severity-badge">{incident.severity}</span>
                                          {incident.type}
                                        </div>
                                        <span className={`incident-status status-${incident.status}`}>
                                          {incident.status === 'pending' && '⏳ Pending'}
                                          {incident.status === 'healing' && '🔧 Healing'}
                                          {incident.status === 'resolved' && '✅ Resolved'}
                                          {incident.status === 'failed' && '❌ Failed'}
                                        </span>
                                      </div>
                                      
                                      <div className="incident-component">
                                        📦 {incident.component}
                                      </div>
                                      
                                      {incident.playbook_applied && (
                                        <div className="incident-playbook">
                                          🔖 Playbook: {incident.playbook_applied}
                                        </div>
                                      )}
                                      
                                      <div className="incident-timing">
                                        <span>Detected: {detectedTime.toLocaleTimeString()}</span>
                                        {duration && (
                                          <span className="incident-duration">
                                            ⏱️ {duration}s
                                          </span>
                                        )}
                                      </div>

                                      {isActive && (
                                        <div className="incident-active-indicator">
                                          <div className="pulse-dot"></div>
                                          In Progress...
                                        </div>
                                      )}
                                    </div>
                                  );
                                })}
                              </div>

                              {/* Last Healing Outcome */}
                              {data.incidents.filter(inc => inc.status === 'resolved').length > 0 && (
                                <div className="last-outcome">
                                  <strong>🎯 Last Successful Healing:</strong>
                                  {' '}
                                  {(() => {
                                    const lastResolved = data.incidents
                                      .filter(inc => inc.status === 'resolved')
                                      .sort((a, b) => 
                                        new Date(b.resolved_at!).getTime() - new Date(a.resolved_at!).getTime()
                                      )[0];
                                    
                                    if (!lastResolved) return 'N/A';
                                    
                                    const resolvedTime = new Date(lastResolved.resolved_at!);
                                    const detectedTime = new Date(lastResolved.detected_at);
                                    const duration = ((resolvedTime.getTime() - detectedTime.getTime()) / 1000).toFixed(1);
                                    
                                    return `${lastResolved.type} resolved in ${duration}s`;
                                  })()}
                                </div>
                              )}
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="no-data">No self-healing data available</div>
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

                    {/* Chaos Engineering Panel */}
                    <div className="mc-section chaos-section">
                      <h3>🌀 Chaos Engineering (Boot-Enabled)</h3>
                      
                      {data.chaosStatus ? (
                        <>
                          <div className="chaos-status-bar">
                            <div className="chaos-status-item">
                              <span className="chaos-label">Status:</span>
                              <span className={`chaos-value ${data.chaosStatus.config.chaos_enabled ? 'enabled' : 'disabled'}`}>
                                {data.chaosStatus.config.chaos_enabled ? '✅ Running Freely' : '⏸️ Paused'}
                              </span>
                            </div>
                            
                            <div className="chaos-status-item">
                              <span className="chaos-label">Governance:</span>
                              <span className="chaos-value disabled">
                                ❌ Not Required (Boot Mode)
                              </span>
                            </div>
                            
                            <div className="chaos-status-item">
                              <span className="chaos-label">Guardian Halt:</span>
                              <span className={`chaos-value ${data.chaosStatus.config.guardian_halt_enabled ? 'enabled' : 'disabled'}`}>
                                {data.chaosStatus.config.guardian_halt_enabled ? '✅ Enabled (Instant)' : '❌ Disabled'}
                              </span>
                            </div>

                            <div className="chaos-status-item">
                              <span className="chaos-label">Active Campaigns:</span>
                              <span className="chaos-value">{data.chaosStatus.active_campaigns}</span>
                            </div>

                            <div className="chaos-status-item">
                              <span className="chaos-label">Tracking:</span>
                              <span className="chaos-value enabled">
                                📊 KPI + Trust Score
                              </span>
                            </div>
                          </div>

                          {/* Chaos Configuration */}
                          <div className="chaos-config">
                            <div className="config-item">
                              <span className="config-label">Allowed Environments:</span>
                              <div className="config-tags">
                                {data.chaosStatus.config.allowed_environments.map((env) => (
                                  <span key={env} className="env-tag">{env}</span>
                                ))}
                              </div>
                            </div>
                            <div className="config-item">
                              <span className="config-label">Min Trust Score:</span>
                              <span className="config-value">{(data.chaosStatus.config.min_trust_score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="config-item">
                              <span className="config-label">Max Blast Radius:</span>
                              <span className="config-value">{data.chaosStatus.config.max_blast_radius}%</span>
                            </div>
                          </div>

                          {/* Active Campaigns */}
                          {data.chaosCampaigns.length > 0 && (
                            <div className="chaos-campaigns">
                              <h4 className="campaigns-title">🎯 Active Campaigns ({data.chaosCampaigns.length})</h4>
                              <div className="campaigns-list">
                                {data.chaosCampaigns.slice(0, 5).map((campaign) => (
                                  <div key={campaign.campaign_id} className={`campaign-card status-${campaign.status}`}>
                                    <div className="campaign-header">
                                      <div className="campaign-name">{campaign.name}</div>
                                      <span className={`campaign-status status-${campaign.status}`}>
                                        {campaign.status === 'running' && '⚙️ Running'}
                                        {campaign.status === 'pending_approval' && '⏳ Pending'}
                                        {campaign.status === 'approved' && '✅ Approved'}
                                        {campaign.status === 'halted' && '🛑 Halted'}
                                        {campaign.status === 'completed' && '✅ Completed'}
                                      </span>
                                    </div>

                                    <div className="campaign-details">
                                      <div className="campaign-env">
                                        <span className={`env-badge env-${campaign.environment}`}>
                                          {campaign.environment}
                                        </span>
                                      </div>
                                      <div className="campaign-targets">
                                        Targets: {campaign.targets.join(', ')}
                                      </div>
                                      <div className="campaign-failures">
                                        Failures: {campaign.failure_types.join(', ')}
                                      </div>
                                    </div>

                                    {/* KPI Tracking */}
                                    {campaign.kpis && Object.keys(campaign.kpis).length > 0 && (
                                      <div className="campaign-kpis">
                                        <div className="kpi-title">📊 KPIs:</div>
                                        <div className="kpi-grid">
                                          {campaign.kpis.mttr_seconds !== undefined && (
                                            <div className="kpi-item">
                                              <span className="kpi-label">MTTR:</span>
                                              <span className="kpi-value">{campaign.kpis.mttr_seconds}s</span>
                                            </div>
                                          )}
                                          {campaign.kpis.recovery_success_rate !== undefined && (
                                            <div className="kpi-item">
                                              <span className="kpi-label">Recovery:</span>
                                              <span className="kpi-value">{(campaign.kpis.recovery_success_rate * 100).toFixed(0)}%</span>
                                            </div>
                                          )}
                                          {campaign.kpis.incidents_triggered !== undefined && (
                                            <div className="kpi-item">
                                              <span className="kpi-label">Incidents:</span>
                                              <span className="kpi-value">{campaign.kpis.incidents_triggered}</span>
                                            </div>
                                          )}
                                          {campaign.kpis.auto_recoveries !== undefined && (
                                            <div className="kpi-item">
                                              <span className="kpi-label">Auto-Recoveries:</span>
                                              <span className="kpi-value">{campaign.kpis.auto_recoveries}</span>
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    )}

                                    {/* Trust Score Tracking */}
                                    {(campaign.trust_score_before !== undefined || campaign.trust_score_after !== undefined) && (
                                      <div className="campaign-trust">
                                        <div className="trust-title">🛡️ Trust Score:</div>
                                        <div className="trust-comparison">
                                          {campaign.trust_score_before !== undefined && (
                                            <div className="trust-item">
                                              <span className="trust-label">Before:</span>
                                              <span className="trust-value">{(campaign.trust_score_before * 100).toFixed(0)}%</span>
                                            </div>
                                          )}
                                          {campaign.trust_score_after !== undefined && (
                                            <div className="trust-item">
                                              <span className="trust-label">After:</span>
                                              <span className={`trust-value ${
                                                campaign.trust_score_after >= (campaign.trust_score_before || 0) ? 'positive' : 'negative'
                                              }`}>
                                                {(campaign.trust_score_after * 100).toFixed(0)}%
                                              </span>
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    )}

                                    {/* Campaign Actions */}
                                    <div className="campaign-actions">
                                      {campaign.status === 'running' && (
                                        <button 
                                          className="halt-btn"
                                          onClick={async () => {
                                            if (confirm(`Halt chaos campaign "${campaign.name}"?`)) {
                                              try {
                                                await ChaosAPI.haltCampaign(campaign.campaign_id, 'User requested halt');
                                                await fetchDashboard();
                                              } catch (err) {
                                                console.error('Failed to halt campaign:', err);
                                                alert('Failed to halt campaign');
                                              }
                                            }
                                          }}
                                        >
                                          🛑 Guardian Halt
                                        </button>
                                      )}
                                      {campaign.halt_reason && (
                                        <div className="halt-reason">
                                          Halt reason: {campaign.halt_reason}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Chaos Toggle */}
                          <div className="chaos-controls">
                            <button 
                              className={`chaos-toggle-btn ${data.chaosStatus.config.chaos_enabled ? 'enabled' : 'disabled'}`}
                              onClick={async () => {
                                try {
                                  await ChaosAPI.toggleChaos(!data.chaosStatus!.config.chaos_enabled);
                                  await fetchDashboard();
                                } catch (err) {
                                  console.error('Failed to toggle chaos:', err);
                                  alert('Failed to toggle chaos engineering');
                                }
                              }}
                            >
                              {data.chaosStatus.config.chaos_enabled ? '⏸️ Pause Chaos' : '▶️ Resume Chaos'}
                            </button>
                            
                            <div className="chaos-notice">
                              ℹ️ Chaos runs freely at boot. Guardian can halt instantly. KPIs & trust scores tracked.
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="no-data">Chaos engineering data unavailable</div>
                      )}
                    </div>

                    {/* Mission Registry Table */}
                    <div className="mc-section mission-registry-section">
                      <h3>📋 Mission Registry</h3>
                      {data.missions.length > 0 ? (
                        <div className="mission-registry-table">
                          <table className="missions-table">
                            <thead>
                              <tr>
                                <th>Mission ID</th>
                                <th>Owner</th>
                                <th>Subsystem</th>
                                <th>Severity</th>
                                <th>Status</th>
                                <th>Started</th>
                                <th>Resolved</th>
                                <th>Duration</th>
                              </tr>
                            </thead>
                            <tbody>
                              {data.missions.slice(0, 20).map((mission) => {
                                const startTime = new Date(mission.created_at);
                                const endTime = mission.resolved_at ? new Date(mission.resolved_at) : null;
                                const duration = endTime 
                                  ? ((endTime.getTime() - startTime.getTime()) / 1000 / 60).toFixed(1) 
                                  : ((Date.now() - startTime.getTime()) / 1000 / 60).toFixed(1);

                                return (
                                  <tr 
                                    key={mission.mission_id} 
                                    className={`mission-row severity-${mission.severity} status-${mission.status}`}
                                  >
                                    <td className="mission-id-cell">
                                      <span className="mission-id-text" title={mission.mission_id}>
                                        {mission.mission_id.substring(0, 24)}...
                                      </span>
                                    </td>
                                    <td className="owner-cell">
                                      {mission.assigned_to || mission.owner || 'Unassigned'}
                                    </td>
                                    <td className="subsystem-cell">
                                      <span className="subsystem-badge">{mission.subsystem_id}</span>
                                    </td>
                                    <td className="severity-cell">
                                      <span className={`severity-badge severity-${mission.severity}`}>
                                        {mission.severity}
                                      </span>
                                    </td>
                                    <td className="status-cell">
                                      <span className={`status-badge status-${mission.status}`}>
                                        {mission.status === 'in_progress' && '⟳ In Progress'}
                                        {mission.status === 'open' && '🔓 Open'}
                                        {mission.status === 'resolved' && '✅ Resolved'}
                                        {mission.status === 'failed' && '❌ Failed'}
                                        {mission.status === 'escalated' && '⬆️ Escalated'}
                                        {mission.status === 'awaiting_validation' && '⏳ Validating'}
                                        {mission.status === 'observing' && '👁️ Observing'}
                                      </span>
                                    </td>
                                    <td className="time-cell">
                                      {startTime.toLocaleString()}
                                    </td>
                                    <td className="time-cell">
                                      {endTime ? endTime.toLocaleString() : '-'}
                                    </td>
                                    <td className="duration-cell">
                                      {duration}m
                                      {!endTime && <span className="ongoing-indicator"> (ongoing)</span>}
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>

                          {/* Mission Summary Stats */}
                          <div className="mission-summary">
                            <div className="summary-stat">
                              <span className="summary-label">Total:</span>
                              <span className="summary-value">{data.missions.length}</span>
                            </div>
                            <div className="summary-stat">
                              <span className="summary-label">Active:</span>
                              <span className="summary-value active">
                                {data.missions.filter(m => m.status === 'open' || m.status === 'in_progress').length}
                              </span>
                            </div>
                            <div className="summary-stat">
                              <span className="summary-label">Resolved:</span>
                              <span className="summary-value resolved">
                                {data.missions.filter(m => m.status === 'resolved').length}
                              </span>
                            </div>
                            <div className="summary-stat">
                              <span className="summary-label">Critical:</span>
                              <span className="summary-value critical">
                                {data.missions.filter(m => m.severity === 'critical').length}
                              </span>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="no-data">No missions recorded</div>
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

            {/* Integrated Components */}
            <BackgroundTasksDrawer
                isOpen={tasksDrawerOpen}
                onClose={() => setTasksDrawerOpen(false)}
            />

            <RemoteCockpit
                isOpen={remoteCockpitOpen}
                onClose={() => setRemoteCockpitOpen(false)}
            />
        </div>
    );
};
