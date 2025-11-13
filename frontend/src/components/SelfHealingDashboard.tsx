import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Play, AlertTriangle, CheckCircle, Clock, Users, BookOpen } from 'lucide-react';

interface DashboardData {
  summary: {
    total_playbooks: number;
    success_rate: number;
    open_incidents: number;
    active_agents: number;
  };
  playbooks: any;
  recent_runs: any;
  open_incidents: any;
  active_agents: any;
  recent_insights: any;
}

export default function SelfHealingDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPlaybook, setSelectedPlaybook] = useState<any>(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/self_healing/dashboard');
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runPlaybook = async (playbookId: string) => {
    try {
      const response = await fetch(`/api/self_healing/playbooks/${playbookId}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const result = await response.json();
      
      if (result.status === 'started') {
        alert(`Playbook execution started: ${result.execution_id}`);
        fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to run playbook:', error);
      alert('Failed to run playbook');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading self-healing dashboard...</div>;
  }

  if (!dashboardData) {
    return <div className="text-red-500">Failed to load dashboard data</div>;
  }

  const { summary, playbooks, recent_runs, open_incidents, active_agents, recent_insights } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Self-Healing Co-pilot</h1>
          <p className="text-muted-foreground">Collaborative autonomous remediation</p>
        </div>
        <Button onClick={fetchDashboardData}>Refresh</Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Playbooks</p>
                <p className="text-2xl font-bold">{summary.total_playbooks}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold">{summary.success_rate}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <div>
                <p className="text-sm text-muted-foreground">Open Incidents</p>
                <p className="text-2xl font-bold">{summary.open_incidents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm text-muted-foreground">Active Agents</p>
                <p className="text-2xl font-bold">{summary.active_agents}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="playbooks" className="space-y-4">
        <TabsList>
          <TabsTrigger value="playbooks">Playbooks</TabsTrigger>
          <TabsTrigger value="runs">Recent Runs</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="insights">Grace's Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="playbooks" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {playbooks.rows?.map((playbook: any) => (
              <Card key={playbook.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{playbook.playbook_name}</CardTitle>
                    <Button
                      size="sm"
                      onClick={() => runPlaybook(playbook.id)}
                      className="flex items-center space-x-1"
                    >
                      <Play className="h-4 w-4" />
                      <span>Run</span>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{playbook.description}</p>
                  
                  <div className="flex flex-wrap gap-2 mb-3">
                    {playbook.target_components?.map((component: string, idx: number) => (
                      <Badge key={idx} variant="secondary">{component}</Badge>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>Risk: <Badge variant={playbook.risk_level === 'high' ? 'destructive' : 'default'}>{playbook.risk_level}</Badge></span>
                    <span>Success: {playbook.execution_stats?.successful_runs || 0}/{playbook.execution_stats?.total_runs || 0}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="runs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Executions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recent_runs.rows?.map((run: any) => (
                  <div key={run.id} className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        run.status === 'success' ? 'bg-green-500' :
                        run.status === 'failed' ? 'bg-red-500' :
                        run.status === 'running' ? 'bg-blue-500' : 'bg-gray-500'
                      }`} />
                      <div>
                        <p className="font-medium">{run.playbook_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {run.triggered_by} • {new Date(run.started_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={run.status === 'success' ? 'default' : run.status === 'failed' ? 'destructive' : 'secondary'}>
                        {run.status}
                      </Badge>
                      {run.duration_ms && (
                        <p className="text-sm text-muted-foreground mt-1">{run.duration_ms}ms</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="incidents" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {open_incidents.rows?.map((incident: any) => (
              <Card key={incident.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{incident.title}</CardTitle>
                    <Badge variant={
                      incident.severity === 'critical' ? 'destructive' :
                      incident.severity === 'high' ? 'destructive' :
                      incident.severity === 'medium' ? 'default' : 'secondary'
                    }>
                      {incident.severity}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{incident.description}</p>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>Status: <Badge variant="outline">{incident.status}</Badge></span>
                    <span>{new Date(incident.created_at).toLocaleDateString()}</span>
                  </div>
                  
                  {incident.affected_services?.length > 0 && (
                    <div className="mt-3">
                      <p className="text-sm font-medium mb-1">Affected Services:</p>
                      <div className="flex flex-wrap gap-1">
                        {incident.affected_services.map((service: string, idx: number) => (
                          <Badge key={idx} variant="outline" className="text-xs">{service}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {active_agents.rows?.map((agent: any) => (
              <Card key={agent.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{agent.agent_name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{agent.mission}</p>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Status:</span>
                      <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
                        {agent.status}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span>Trust Score:</span>
                      <span className="font-medium">{agent.trust_score || 'N/A'}</span>
                    </div>
                    
                    {agent.capabilities && (
                      <div>
                        <p className="text-sm font-medium mb-1">Capabilities:</p>
                        <div className="flex flex-wrap gap-1">
                          {agent.capabilities.map((cap: string, idx: number) => (
                            <Badge key={idx} variant="outline" className="text-xs">{cap}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <div className="space-y-4">
            {recent_insights.rows?.map((insight: any) => (
              <Card key={insight.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{insight.title}</CardTitle>
                    <Badge variant="outline">
                      {Math.round(insight.confidence * 100)}% confidence
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm mb-3">{insight.description}</p>
                  
                  {insight.recommendations && (
                    <div>
                      <p className="text-sm font-medium mb-2">Grace's Recommendations:</p>
                      <ul className="text-sm space-y-1">
                        {insight.recommendations.map((rec: string, idx: number) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <span className="text-blue-500">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-muted-foreground mt-3">
                    <span>Generated: {new Date(insight.created_at).toLocaleString()}</span>
                    <span>Status: {insight.status || 'pending'}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}