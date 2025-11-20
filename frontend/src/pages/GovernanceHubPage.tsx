import { Surface, Card, CardHeader, CardContent, Button, Tag, KpiTile } from '../design-system';
import { Shield, Key, CheckCircle, XCircle, Clock, Eye, Lock, AlertTriangle } from 'lucide-react';
import './GovernanceHubPage.css';

export function GovernanceHubPage() {
  const mockSecrets = [
    { id: '1', name: 'GITHUB_TOKEN', type: 'API Key', status: 'active', masked: '***************xyz' },
    { id: '2', name: 'OPENAI_API_KEY', type: 'API Key', status: 'active', masked: '***************abc' },
    { id: '3', name: 'DATABASE_PASSWORD', type: 'Password', status: 'active', masked: '***************123' },
  ];

  const mockApprovals = [
    { id: '1', request: 'Remote Access Request', status: 'pending', requestedAt: '5 min ago' },
    { id: '2', request: 'File System Write', status: 'approved', requestedAt: '2 hours ago' },
    { id: '3', request: 'External API Call', status: 'rejected', requestedAt: '1 day ago' },
  ];

  const getApprovalIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock size={16} />;
      case 'approved': return <CheckCircle size={16} />;
      case 'rejected': return <XCircle size={16} />;
      default: return null;
    }
  };

  const getApprovalVariant = (status: string) => {
    switch (status) {
      case 'pending': return 'warning' as const;
      case 'approved': return 'success' as const;
      case 'rejected': return 'error' as const;
      default: return 'neutral' as const;
    }
  };

  return (
    <Surface>
      <div className="governance-hub-page">
        <div className="governance-hub-page__header">
          <div>
            <h1 className="governance-hub-page__title">Governance & Security Hub</h1>
            <p className="governance-hub-page__subtitle">
              Manage secrets, approvals, and trust controls
            </p>
          </div>
          <div className="governance-hub-page__actions">
            <Button variant="secondary" icon={<Eye size={18} />}>
              Audit Trail
            </Button>
            <Button icon={<Key size={18} />}>
              Add Secret
            </Button>
          </div>
        </div>

        <div className="governance-hub-page__kpis">
          <KpiTile
            label="Trust Score"
            value="94%"
            icon={<Shield size={20} />}
            status="success"
            trend="up"
            trendValue="+2% this week"
          />
          <KpiTile
            label="Active Secrets"
            value={mockSecrets.length}
            icon={<Key size={20} />}
            status="info"
          />
          <KpiTile
            label="Pending Approvals"
            value={mockApprovals.filter(a => a.status === 'pending').length}
            icon={<Clock size={20} />}
            status="warning"
          />
          <KpiTile
            label="Security Events"
            value="0"
            icon={<AlertTriangle size={20} />}
            status="success"
          />
        </div>

        <div className="governance-hub-page__grid">
          <Card variant="bordered">
            <CardHeader>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Lock size={20} />
                Secrets Vault
              </div>
              <Button variant="ghost" size="sm">Manage</Button>
            </CardHeader>
            <CardContent>
              <div className="governance-hub-page__secrets">
                {mockSecrets.map((secret) => (
                  <div key={secret.id} className="governance-hub-page__secret">
                    <div className="governance-hub-page__secret-info">
                      <div className="governance-hub-page__secret-name">
                        {secret.name}
                      </div>
                      <div className="governance-hub-page__secret-type">
                        {secret.type}
                      </div>
                    </div>
                    <div className="governance-hub-page__secret-value">
                      {secret.masked}
                    </div>
                    <Tag variant="success" size="sm">
                      {secret.status}
                    </Tag>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card variant="bordered">
            <CardHeader>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle size={20} />
                Approval Workflows
              </div>
              <Button variant="ghost" size="sm">View All</Button>
            </CardHeader>
            <CardContent>
              <div className="governance-hub-page__approvals">
                {mockApprovals.map((approval) => (
                  <div key={approval.id} className="governance-hub-page__approval">
                    <div className="governance-hub-page__approval-info">
                      <div className="governance-hub-page__approval-request">
                        {approval.request}
                      </div>
                      <div className="governance-hub-page__approval-time">
                        {approval.requestedAt}
                      </div>
                    </div>
                    <Tag variant={getApprovalVariant(approval.status)} size="sm">
                      {getApprovalIcon(approval.status)}
                      {approval.status}
                    </Tag>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card variant="bordered">
          <CardHeader>
            Trust & Compliance KPIs
          </CardHeader>
          <CardContent>
            <div className="governance-hub-page__compliance">
              <div className="governance-hub-page__compliance-item">
                <div className="governance-hub-page__compliance-label">
                  Secret Rotation Policy
                </div>
                <div className="governance-hub-page__compliance-status">
                  <Tag variant="success">Compliant</Tag>
                </div>
              </div>
              <div className="governance-hub-page__compliance-item">
                <div className="governance-hub-page__compliance-label">
                  Approval Coverage
                </div>
                <div className="governance-hub-page__compliance-status">
                  <Tag variant="success">100%</Tag>
                </div>
              </div>
              <div className="governance-hub-page__compliance-item">
                <div className="governance-hub-page__compliance-label">
                  Audit Logging
                </div>
                <div className="governance-hub-page__compliance-status">
                  <Tag variant="success">Enabled</Tag>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="governance-hub-page__quick-actions">
          <Button variant="secondary">Request Approval</Button>
          <Button variant="secondary">Revoke Token</Button>
          <Button variant="secondary">View Audit Trail</Button>
          <Button variant="danger">Rotate All Secrets</Button>
        </div>
      </div>
    </Surface>
  );
}
