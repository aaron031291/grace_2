import type { WorkspacePayload } from '../../hooks/useWorkspaces';
import './WorkspaceCommon.css';

interface DashboardWorkspaceProps {
  type: 'kpi-dashboard' | 'crm-dashboard' | 'sales-dashboard';
  payload: WorkspacePayload;
}

export default function DashboardWorkspace({ type, payload }: DashboardWorkspaceProps) {
  const { filters } = payload;

  const getDashboardTitle = () => {
    switch (type) {
      case 'kpi-dashboard': return 'KPI Dashboard';
      case 'crm-dashboard': return 'CRM Dashboard';
      case 'sales-dashboard': return 'Sales Dashboard';
      default: return 'Dashboard';
    }
  };

  const getDashboardIcon = () => {
    switch (type) {
      case 'kpi-dashboard': return '📈';
      case 'crm-dashboard': return '👥';
      case 'sales-dashboard': return '💰';
      default: return '📊';
    }
  };

  return (
    <div className="workspace-container dashboard-workspace">
      <div className="workspace-header">
        <h2>
          <span className="dashboard-icon">{getDashboardIcon()}</span>
          {getDashboardTitle()}
        </h2>
      </div>

      <div className="workspace-content">
        {filters && Object.keys(filters).length > 0 && (
          <div className="filters-display">
            <h4>Active Filters:</h4>
            <div className="filter-chips">
              {Object.entries(filters).map(([key, value]) => (
                <div key={key} className="filter-chip">
                  <span className="filter-key">{key}:</span>
                  <span className="filter-value">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="dashboard-placeholder">
          <div className="placeholder-icon">{getDashboardIcon()}</div>
          <h3>{getDashboardTitle()}</h3>
          <p>Connect this workspace to your actual dashboard component</p>
          <div className="placeholder-code">
            <code>
              {`// In DashboardWorkspace.tsx:\n`}
              {`import ${type === 'kpi-dashboard' ? 'KPIDashboard' : type === 'crm-dashboard' ? 'CRMDashboard' : 'SalesDashboard'} from './dashboards';\n`}
              {`return <${type === 'kpi-dashboard' ? 'KPIDashboard' : type === 'crm-dashboard' ? 'CRMDashboard' : 'SalesDashboard'} filters={filters} />;`}
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
