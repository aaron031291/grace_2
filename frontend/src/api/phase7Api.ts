/**
 * Phase 7 API Client
 * Typed client for Grace's SaaS Readiness & Business Workflows APIs
 */

const API_BASE = import.meta.env.VITE_API_BASE || window.location.origin;

export interface ProductTemplate {
  template_id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  features: TemplateFeature[];
  components: TemplateComponent[];
  tech_stack: Record<string, string>;
  estimated_setup_time: number;
  tags: string[];
  icon?: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateFeature {
  name: string;
  description: string;
  enabled: boolean;
  config: Record<string, any>;
}

export interface TemplateComponent {
  name: string;
  type: string;
  image: string;
  config: Record<string, any>;
  dependencies: string[];
}

export interface TemplateInstance {
  instance_id: string;
  template_id: string;
  tenant_id: string;
  instance_name: string;
  status: string;
  config: Record<string, any>;
  deployment_url?: string;
  created_at: string;
  deployed_at?: string;
  last_health_check?: string;
}

export interface Subscription {
  subscription_id: string;
  tenant_id: string;
  plan: string;
  status: string;
  billing_email: string;
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  invoice_id: string;
  subscription_id: string;
  tenant_id: string;
  amount_due: number;
  amount_paid: number;
  currency: string;
  status: string;
  due_date: string;
  paid_at?: string;
  line_items: InvoiceLineItem[];
  created_at: string;
}

export interface InvoiceLineItem {
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

export interface UsageRecord {
  record_id: string;
  tenant_id: string;
  record_type: string;
  quantity: number;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface Role {
  role_id: string;
  name: string;
  description: string;
  permissions: string[];
  parent_role_id?: string;
  inherits_permissions: boolean;
  is_system_role: boolean;
  tenant_id?: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  user_id: string;
  email: string;
  name: string;
  tenant_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoleAssignment {
  assignment_id: string;
  user_id: string;
  role_id: string;
  tenant_id: string;
  assigned_by: string;
  assigned_at: string;
  expires_at?: string;
}

export interface AccessLog {
  log_id: string;
  user_id: string;
  action: string;
  resource: string;
  allowed: boolean;
  reason?: string;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface Backup {
  backup_id: string;
  tenant_id: string;
  backup_type: string;
  status: string;
  size_bytes: number;
  description?: string;
  storage_location?: string;
  retention_days: number;
  created_at: string;
  completed_at?: string;
  expires_at: string;
}

export interface RestoreJob {
  job_id: string;
  backup_id: string;
  tenant_id: string;
  status: string;
  target_environment: string;
  initiated_by: string;
  initiated_at: string;
  completed_at?: string;
  verification_status?: string;
}

export interface ChaosTest {
  test_id: string;
  tenant_id: string;
  test_type: string;
  status: string;
  description: string;
  target_service?: string;
  scheduled_at: string;
  started_at?: string;
  completed_at?: string;
  results?: Record<string, any>;
}

export interface DRRunbook {
  runbook_id: string;
  name: string;
  description: string;
  scenario_type: string;
  severity: string;
  steps: RunbookStep[];
  primary_contact?: string;
  escalation_contacts: string[];
  rto_minutes: number;
  rpo_minutes: number;
  last_tested_at?: string;
  test_frequency_days: number;
  created_at: string;
  updated_at: string;
}

export interface RunbookStep {
  step: number;
  action: string;
}

export interface Phase7Summary {
  phase: string;
  status: string;
  components: {
    product_templates: {
      total_templates: number;
      total_instances: number;
      categories: string[];
    };
    billing: {
      total_subscriptions: number;
      total_invoices: number;
      total_usage_records: number;
      plans: string[];
    };
    rbac: {
      total_roles: number;
      total_users: number;
      total_permissions: number;
      total_assignments: number;
      total_access_logs: number;
    };
    disaster_recovery: {
      total_backups: number;
      total_restore_jobs: number;
      total_chaos_tests: number;
      total_runbooks: number;
    };
  };
  endpoints: {
    product_templates: number;
    billing: number;
    rbac: number;
    disaster_recovery: number;
    total: number;
  };
}

export class Phase7ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  async getSummary(): Promise<Phase7Summary> {
    const response = await fetch(`${this.baseUrl}/api/phase7/summary`);
    return await response.json();
  }

  async getTemplates(category?: string): Promise<ProductTemplate[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    
    const response = await fetch(`${this.baseUrl}/api/phase7/templates?${params}`);
    return await response.json();
  }

  async getTemplate(templateId: string): Promise<ProductTemplate> {
    const response = await fetch(`${this.baseUrl}/api/phase7/templates/${templateId}`);
    return await response.json();
  }

  async getTemplateInstances(tenantId: string): Promise<TemplateInstance[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/templates/instances?tenant_id=${tenantId}`);
    return await response.json();
  }

  async getSubscriptions(tenantId: string): Promise<Subscription[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/subscriptions?tenant_id=${tenantId}`);
    return await response.json();
  }

  async getInvoices(tenantId: string): Promise<Invoice[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/invoices?tenant_id=${tenantId}`);
    return await response.json();
  }

  async getUsage(tenantId: string, startDate: string, endDate: string): Promise<UsageRecord[]> {
    const response = await fetch(
      `${this.baseUrl}/api/phase7/usage?tenant_id=${tenantId}&start_date=${startDate}&end_date=${endDate}`
    );
    return await response.json();
  }

  async getRoles(): Promise<Role[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/roles`);
    return await response.json();
  }

  async getUsers(tenantId: string): Promise<User[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/users?tenant_id=${tenantId}`);
    return await response.json();
  }

  async getRoleAssignments(tenantId: string): Promise<RoleAssignment[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/role-assignments?tenant_id=${tenantId}`);
    return await response.json();
  }

  async getAccessLogs(tenantId: string, limit: number = 100): Promise<{ logs: AccessLog[] }> {
    const response = await fetch(`${this.baseUrl}/api/phase7/access-logs?tenant_id=${tenantId}&limit=${limit}`);
    return await response.json();
  }

  async getBackups(tenantId: string): Promise<Backup[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/backups?tenant_id=${tenantId}`);
    return await response.json();
  }

  async getRestoreJobs(tenantId: string): Promise<RestoreJob[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/restore-jobs?tenant_id=${tenantId}`);
    return await response.json();
  }

  async getChaosTests(): Promise<ChaosTest[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/chaos-tests`);
    return await response.json();
  }

  async getRunbooks(): Promise<DRRunbook[]> {
    const response = await fetch(`${this.baseUrl}/api/phase7/runbooks`);
    return await response.json();
  }
}

export const phase7Api = new Phase7ApiClient();
