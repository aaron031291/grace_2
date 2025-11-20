import { useNavigate } from 'react-router-dom';
import { Surface, Card, CardHeader, CardContent, KpiTile, Button } from '../design-system';
import { SystemOverview } from '../components/SystemOverview';
import { Activity, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import './SystemHealthPage.css';

export function SystemHealthPage() {
  const navigate = useNavigate();

  return (
    <Surface>
      <div className="system-health-page">
        <div className="system-health-page__header">
          <h1 className="system-health-page__title">System Health Overview</h1>
          <p className="system-health-page__subtitle">
            Monitor Grace's operational status and performance metrics
          </p>
        </div>

        <div className="system-health-page__kpis">
          <KpiTile
            label="System Status"
            value="Operational"
            icon={<CheckCircle size={20} />}
            status="success"
            onClick={() => navigate('/')}
          />
          <KpiTile
            label="Active Tasks"
            value="12"
            icon={<Activity size={20} />}
            status="info"
            trend="up"
            trendValue="+3 from yesterday"
            onClick={() => navigate('/tasks')}
          />
          <KpiTile
            label="Memory Files"
            value="1,247"
            icon={<TrendingUp size={20} />}
            status="info"
            trend="up"
            trendValue="+142 this week"
            onClick={() => navigate('/memory')}
          />
          <KpiTile
            label="Pending Approvals"
            value="2"
            icon={<AlertCircle size={20} />}
            status="warning"
            onClick={() => navigate('/governance')}
          />
        </div>

        <Card variant="bordered">
          <CardHeader>
            Live System Metrics
          </CardHeader>
          <CardContent>
            <SystemOverview />
          </CardContent>
        </Card>

        <div className="system-health-page__quick-actions">
          <Button onClick={() => navigate('/tasks')}>View All Tasks</Button>
          <Button variant="secondary" onClick={() => navigate('/memory')}>
            Browse Memory
          </Button>
          <Button variant="secondary" onClick={() => navigate('/governance')}>
            Governance Console
          </Button>
        </div>
      </div>
    </Surface>
  );
}
