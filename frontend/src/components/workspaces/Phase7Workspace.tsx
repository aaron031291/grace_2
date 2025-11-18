import { useState, useEffect } from 'react';
import type { Workspace } from '../../GraceEnterpriseUI';
import { phase7Api } from '../../api/phase7Api';
import type {
  ProductTemplate,
  TemplateInstance,
  Subscription,
  Invoice,
  UsageRecord,
  Role,
  User,
  RoleAssignment,
  AccessLog,
  Backup,
  RestoreJob,
  ChaosTest,
  DRRunbook,
  Phase7Summary
} from '../../api/phase7Api';
import './WorkspaceCommon.css';
import './Phase7Workspace.css';

interface Phase7WorkspaceProps {
  workspace: Workspace;
}

type TabType = 'templates' | 'billing' | 'rbac' | 'disaster-recovery';

export function Phase7Workspace({ workspace }: Phase7WorkspaceProps) {
  const [activeTab, setActiveTab] = useState<TabType>('templates');
  const [summary, setSummary] = useState<Phase7Summary | null>(null);
  const [loading, setLoading] = useState(false);
  const [tenantId] = useState('default-tenant'); // TODO: Get from auth context

  const [templates, setTemplates] = useState<ProductTemplate[]>([]);
  const [templateInstances, setTemplateInstances] = useState<TemplateInstance[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ProductTemplate | null>(null);

  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [usageRecords, setUsageRecords] = useState<UsageRecord[]>([]);

  const [roles, setRoles] = useState<Role[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [roleAssignments, setRoleAssignments] = useState<RoleAssignment[]>([]);
  const [accessLogs, setAccessLogs] = useState<AccessLog[]>([]);

  const [backups, setBackups] = useState<Backup[]>([]);
  const [restoreJobs, setRestoreJobs] = useState<RestoreJob[]>([]);
  const [chaosTests, setChaosTests] = useState<ChaosTest[]>([]);
  const [runbooks, setRunbooks] = useState<DRRunbook[]>([]);

  useEffect(() => {
    fetchSummary();
    fetchData();
  }, [activeTab]);

  const fetchSummary = async () => {
    try {
      const data = await phase7Api.getSummary();
      setSummary(data);
    } catch (error) {
      console.error('Failed to fetch Phase 7 summary:', error);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      switch (activeTab) {
        case 'templates':
          const templatesData = await phase7Api.getTemplates();
          setTemplates(templatesData);
          try {
            const instancesData = await phase7Api.getTemplateInstances(tenantId);
            setTemplateInstances(instancesData);
          } catch (e) {
            setTemplateInstances([]);
          }
          break;
        case 'billing':
          try {
            const subsData = await phase7Api.getSubscriptions(tenantId);
            setSubscriptions(subsData);
          } catch (e) {
            setSubscriptions([]);
          }
          try {
            const invoicesData = await phase7Api.getInvoices(tenantId);
            setInvoices(invoicesData);
          } catch (e) {
            setInvoices([]);
          }
          break;
        case 'rbac':
          const rolesData = await phase7Api.getRoles();
          setRoles(rolesData);
          try {
            const usersData = await phase7Api.getUsers(tenantId);
            setUsers(usersData);
          } catch (e) {
            setUsers([]);
          }
          try {
            const assignmentsData = await phase7Api.getRoleAssignments(tenantId);
            setRoleAssignments(assignmentsData);
          } catch (e) {
            setRoleAssignments([]);
          }
          try {
            const logsData = await phase7Api.getAccessLogs(tenantId, 50);
            setAccessLogs(logsData.logs);
          } catch (e) {
            setAccessLogs([]);
          }
          break;
        case 'disaster-recovery':
          const backupsData = await phase7Api.getBackups(tenantId);
          setBackups(backupsData);
          try {
            const restoreData = await phase7Api.getRestoreJobs(tenantId);
            setRestoreJobs(restoreData);
          } catch (e) {
            setRestoreJobs([]);
          }
          const chaosData = await phase7Api.getChaosTests();
          setChaosTests(chaosData);
          const runbooksData = await phase7Api.getRunbooks();
          setRunbooks(runbooksData);
          break;
      }
    } catch (error) {
      console.error('Failed to fetch Phase 7 data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderTemplatesTab = () => (
    <div className="phase7-tab-content">
      <div className="phase7-header">
        <h3>🎨 Product Templates</h3>
        <div className="phase7-stats">
          <span className="stat-badge">{templates.length} Templates</span>
          <span className="stat-badge">{templateInstances.length} Instances</span>
        </div>
      </div>

      <div className="templates-grid">
        {templates.map((template) => (
          <div 
            key={template.template_id} 
            className={`template-card ${selectedTemplate?.template_id === template.template_id ? 'selected' : ''}`}
            onClick={() => setSelectedTemplate(template)}
          >
            <div className="template-header">
              <span className="template-icon">{template.icon || '📦'}</span>
              <h4>{template.name}</h4>
              <span className="template-category">{template.category}</span>
            </div>
            <p className="template-description">{template.description}</p>
            <div className="template-meta">
              <span className="template-time">⏱️ {template.estimated_setup_time}min</span>
              <span className="template-version">v{template.version}</span>
            </div>
            <div className="template-tags">
              {template.tags.slice(0, 3).map((tag) => (
                <span key={tag} className="tag">{tag}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {selectedTemplate && (
        <div className="template-details">
          <h4>Template Details: {selectedTemplate.name}</h4>
          <div className="details-section">
            <h5>Features ({selectedTemplate.features.length})</h5>
            <ul>
              {selectedTemplate.features.map((feature, idx) => (
                <li key={idx}>
                  <strong>{feature.name}:</strong> {feature.description}
                </li>
              ))}
            </ul>
          </div>
          <div className="details-section">
            <h5>Tech Stack</h5>
            <div className="tech-stack">
              {Object.entries(selectedTemplate.tech_stack).map(([key, value]) => (
                <div key={key} className="tech-item">
                  <span className="tech-key">{key}:</span>
                  <span className="tech-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="details-section">
            <h5>Components ({selectedTemplate.components.length})</h5>
            <ul>
              {selectedTemplate.components.map((component, idx) => (
                <li key={idx}>
                  <strong>{component.name}</strong> ({component.type}): {component.image}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );

  const renderBillingTab = () => (
    <div className="phase7-tab-content">
      <div className="phase7-header">
        <h3>💳 Billing & Subscriptions</h3>
        <div className="phase7-stats">
          <span className="stat-badge">{subscriptions.length} Subscriptions</span>
          <span className="stat-badge">{invoices.length} Invoices</span>
        </div>
      </div>

      <div className="billing-section">
        <h4>Subscription Plans</h4>
        <div className="plans-grid">
          <div className="plan-card free">
            <h5>FREE</h5>
            <div className="plan-price">$0<span>/month</span></div>
            <ul className="plan-features">
              <li>1,000 API calls/month</li>
              <li>1 GB storage</li>
              <li>1 team member</li>
            </ul>
          </div>
          <div className="plan-card starter">
            <h5>STARTER</h5>
            <div className="plan-price">$29<span>/month</span></div>
            <ul className="plan-features">
              <li>10,000 API calls/month</li>
              <li>10 GB storage</li>
              <li>5 team members</li>
            </ul>
          </div>
          <div className="plan-card professional">
            <h5>PROFESSIONAL</h5>
            <div className="plan-price">$99<span>/month</span></div>
            <ul className="plan-features">
              <li>100,000 API calls/month</li>
              <li>100 GB storage</li>
              <li>20 team members</li>
            </ul>
          </div>
          <div className="plan-card enterprise">
            <h5>ENTERPRISE</h5>
            <div className="plan-price">$499<span>/month</span></div>
            <ul className="plan-features">
              <li>Unlimited API calls</li>
              <li>1 TB storage</li>
              <li>Unlimited team members</li>
            </ul>
          </div>
        </div>
      </div>

      {subscriptions.length > 0 && (
        <div className="billing-section">
          <h4>Active Subscriptions</h4>
          <table className="phase7-table">
            <thead>
              <tr>
                <th>Plan</th>
                <th>Status</th>
                <th>Billing Email</th>
                <th>Current Period</th>
                <th>Auto-Renew</th>
              </tr>
            </thead>
            <tbody>
              {subscriptions.map((sub) => (
                <tr key={sub.subscription_id}>
                  <td><span className={`badge badge-${sub.plan.toLowerCase()}`}>{sub.plan}</span></td>
                  <td><span className={`status-${sub.status.toLowerCase()}`}>{sub.status}</span></td>
                  <td>{sub.billing_email}</td>
                  <td>{new Date(sub.current_period_start).toLocaleDateString()} - {new Date(sub.current_period_end).toLocaleDateString()}</td>
                  <td>{sub.cancel_at_period_end ? '❌' : '✅'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {invoices.length > 0 && (
        <div className="billing-section">
          <h4>Recent Invoices</h4>
          <table className="phase7-table">
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Due Date</th>
                <th>Paid At</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.invoice_id}>
                  <td className="mono">{invoice.invoice_id.substring(0, 8)}...</td>
                  <td>${invoice.amount_due.toFixed(2)} {invoice.currency}</td>
                  <td><span className={`status-${invoice.status.toLowerCase()}`}>{invoice.status}</span></td>
                  <td>{new Date(invoice.due_date).toLocaleDateString()}</td>
                  <td>{invoice.paid_at ? new Date(invoice.paid_at).toLocaleDateString() : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderRBACTab = () => (
    <div className="phase7-tab-content">
      <div className="phase7-header">
        <h3>🔐 Role-Based Access Control</h3>
        <div className="phase7-stats">
          <span className="stat-badge">{roles.length} Roles</span>
          <span className="stat-badge">{users.length} Users</span>
          <span className="stat-badge">{roleAssignments.length} Assignments</span>
        </div>
      </div>

      <div className="rbac-section">
        <h4>System Roles</h4>
        <div className="roles-grid">
          {roles.map((role) => (
            <div key={role.role_id} className={`role-card ${role.is_system_role ? 'system-role' : ''}`}>
              <div className="role-header">
                <h5>{role.name}</h5>
                {role.is_system_role && <span className="system-badge">System</span>}
              </div>
              <p className="role-description">{role.description}</p>
              <div className="role-permissions">
                <strong>{role.permissions.length} Permissions:</strong>
                <div className="permissions-list">
                  {role.permissions.slice(0, 5).map((perm) => (
                    <span key={perm} className="permission-badge">{perm}</span>
                  ))}
                  {role.permissions.length > 5 && (
                    <span className="permission-badge more">+{role.permissions.length - 5} more</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {users.length > 0 && (
        <div className="rbac-section">
          <h4>Users</h4>
          <table className="phase7-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.user_id}>
                  <td>{user.name}</td>
                  <td>{user.email}</td>
                  <td><span className={`status-${user.is_active ? 'active' : 'inactive'}`}>{user.is_active ? 'Active' : 'Inactive'}</span></td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {accessLogs.length > 0 && (
        <div className="rbac-section">
          <h4>Recent Access Logs</h4>
          <table className="phase7-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {accessLogs.slice(0, 20).map((log) => (
                <tr key={log.log_id}>
                  <td className="timestamp">{new Date(log.timestamp).toLocaleTimeString()}</td>
                  <td className="mono">{log.user_id.substring(0, 8)}...</td>
                  <td><span className="badge">{log.action}</span></td>
                  <td>{log.resource}</td>
                  <td>{log.allowed ? '✅ Allowed' : '❌ Denied'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderDisasterRecoveryTab = () => (
    <div className="phase7-tab-content">
      <div className="phase7-header">
        <h3>🚨 Disaster Recovery</h3>
        <div className="phase7-stats">
          <span className="stat-badge">{backups.length} Backups</span>
          <span className="stat-badge">{runbooks.length} Runbooks</span>
          <span className="stat-badge">{chaosTests.length} Chaos Tests</span>
        </div>
      </div>

      <div className="dr-section">
        <h4>DR Runbooks</h4>
        <div className="runbooks-grid">
          {runbooks.map((runbook) => (
            <div key={runbook.runbook_id} className={`runbook-card severity-${runbook.severity}`}>
              <div className="runbook-header">
                <h5>{runbook.name}</h5>
                <span className={`severity-badge ${runbook.severity}`}>{runbook.severity}</span>
              </div>
              <p className="runbook-description">{runbook.description}</p>
              <div className="runbook-meta">
                <div className="meta-item">
                  <span className="meta-label">RTO:</span>
                  <span className="meta-value">{runbook.rto_minutes} min</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">RPO:</span>
                  <span className="meta-value">{runbook.rpo_minutes} min</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Steps:</span>
                  <span className="meta-value">{runbook.steps.length}</span>
                </div>
              </div>
              <div className="runbook-steps">
                <strong>Steps:</strong>
                <ol>
                  {runbook.steps.slice(0, 3).map((step) => (
                    <li key={step.step}>{step.action}</li>
                  ))}
                  {runbook.steps.length > 3 && <li>... +{runbook.steps.length - 3} more steps</li>}
                </ol>
              </div>
            </div>
          ))}
        </div>
      </div>

      {backups.length > 0 && (
        <div className="dr-section">
          <h4>Recent Backups</h4>
          <table className="phase7-table">
            <thead>
              <tr>
                <th>Backup ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Size</th>
                <th>Created</th>
                <th>Expires</th>
              </tr>
            </thead>
            <tbody>
              {backups.map((backup) => (
                <tr key={backup.backup_id}>
                  <td className="mono">{backup.backup_id.substring(0, 8)}...</td>
                  <td><span className="badge">{backup.backup_type}</span></td>
                  <td><span className={`status-${backup.status.toLowerCase()}`}>{backup.status}</span></td>
                  <td>{(backup.size_bytes / 1024 / 1024).toFixed(2)} MB</td>
                  <td>{new Date(backup.created_at).toLocaleDateString()}</td>
                  <td>{new Date(backup.expires_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {chaosTests.length > 0 && (
        <div className="dr-section">
          <h4>Chaos Engineering Tests</h4>
          <table className="phase7-table">
            <thead>
              <tr>
                <th>Test Type</th>
                <th>Status</th>
                <th>Description</th>
                <th>Scheduled</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              {chaosTests.map((test) => (
                <tr key={test.test_id}>
                  <td><span className="badge">{test.test_type}</span></td>
                  <td><span className={`status-${test.status.toLowerCase()}`}>{test.status}</span></td>
                  <td>{test.description}</td>
                  <td>{new Date(test.scheduled_at).toLocaleDateString()}</td>
                  <td>{test.completed_at ? new Date(test.completed_at).toLocaleDateString() : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  return (
    <div className="workspace-container phase7-workspace">
      <div className="workspace-header">
        <h2>🚀 Phase 7: SaaS Readiness</h2>
        {summary && (
          <div className="summary-stats">
            <span className="stat">📦 {summary.components.product_templates.total_templates} Templates</span>
            <span className="stat">💳 {summary.components.billing.plans.length} Plans</span>
            <span className="stat">🔐 {summary.components.rbac.total_roles} Roles</span>
            <span className="stat">🚨 {summary.components.disaster_recovery.total_runbooks} Runbooks</span>
          </div>
        )}
      </div>

      <div className="workspace-tabs">
        <button
          className={`tab-button ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          🎨 Templates
        </button>
        <button
          className={`tab-button ${activeTab === 'billing' ? 'active' : ''}`}
          onClick={() => setActiveTab('billing')}
        >
          💳 Billing
        </button>
        <button
          className={`tab-button ${activeTab === 'rbac' ? 'active' : ''}`}
          onClick={() => setActiveTab('rbac')}
        >
          🔐 RBAC
        </button>
        <button
          className={`tab-button ${activeTab === 'disaster-recovery' ? 'active' : ''}`}
          onClick={() => setActiveTab('disaster-recovery')}
        >
          🚨 Disaster Recovery
        </button>
      </div>

      <div className="workspace-content">
        {loading ? (
          <div className="loading-state">Loading...</div>
        ) : (
          <>
            {activeTab === 'templates' && renderTemplatesTab()}
            {activeTab === 'billing' && renderBillingTab()}
            {activeTab === 'rbac' && renderRBACTab()}
            {activeTab === 'disaster-recovery' && renderDisasterRecoveryTab()}
          </>
        )}
      </div>
    </div>
  );
}
