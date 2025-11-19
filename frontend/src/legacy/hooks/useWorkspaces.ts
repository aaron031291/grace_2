/**
 * useWorkspaces Hook
 * Manages dynamic workspace tabs/panels
 * 
 * Features:
 * - Create/close workspaces
 * - Track active workspace
 * - Unique ID generation
 * - Type-based workspace data
 */

import { useState, useCallback } from 'react';

export interface Workspace {
  id: string;
  title: string;
  type: WorkspaceType;
  payload: WorkspacePayload;
  createdAt: string;
}

export type WorkspaceType = 
  | 'mission-detail'
  | 'kpi-dashboard'
  | 'crm-dashboard'
  | 'sales-dashboard'
  | 'artifact-viewer'
  | 'code-diff'
  | 'log-viewer'
  | 'memory-preview'
  | 'custom';

export interface WorkspacePayload {
  // Mission detail
  missionId?: string;
  
  // Dashboard
  filters?: Record<string, any>;
  timeRange?: string;
  
  // Artifact viewer
  artifactId?: string;
  artifactType?: string;
  
  // Code diff
  filePath?: string;
  commitSha?: string;
  
  // Log viewer
  logSource?: string;
  logLevel?: string;
  
  // Custom
  component?: React.ReactNode;
  data?: any;
}

export interface UseWorkspacesResult {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  
  openWorkspace: (type: WorkspaceType, title: string, payload: WorkspacePayload) => string;
  closeWorkspace: (id: string) => void;
  setActiveWorkspace: (id: string) => void;
  clearWorkspaces: () => void;
  
  hasWorkspace: (type: WorkspaceType, matchPayload?: Partial<WorkspacePayload>) => boolean;
  getWorkspaceById: (id: string) => Workspace | null;
}

/**
 * Generate unique workspace ID
 */
function generateWorkspaceId(): string {
  return `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Check if two payloads match
 */
function payloadsMatch(payload1: WorkspacePayload, payload2: Partial<WorkspacePayload>): boolean {
  for (const key in payload2) {
    if (payload1[key as keyof WorkspacePayload] !== payload2[key as keyof WorkspacePayload]) {
      return false;
    }
  }
  return true;
}

export function useWorkspaces(): UseWorkspacesResult {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);

  /**
   * Open a new workspace
   */
  const openWorkspace = useCallback((
    type: WorkspaceType,
    title: string,
    payload: WorkspacePayload = {}
  ): string => {
    const id = generateWorkspaceId();
    
    const workspace: Workspace = {
      id,
      title,
      type,
      payload,
      createdAt: new Date().toISOString(),
    };

    setWorkspaces(prev => [...prev, workspace]);
    setActiveWorkspaceId(id);
    
    return id;
  }, []);

  /**
   * Close a workspace
   */
  const closeWorkspace = useCallback((id: string) => {
    setWorkspaces(prev => {
      const filtered = prev.filter(w => w.id !== id);
      
      // If closing active workspace, switch to last workspace
      if (activeWorkspaceId === id && filtered.length > 0) {
        setActiveWorkspaceId(filtered[filtered.length - 1].id);
      } else if (filtered.length === 0) {
        setActiveWorkspaceId(null);
      }
      
      return filtered;
    });
  }, [activeWorkspaceId]);

  /**
   * Set active workspace
   */
  const setActiveWorkspace = useCallback((id: string) => {
    setActiveWorkspaceId(id);
  }, []);

  /**
   * Clear all workspaces
   */
  const clearWorkspaces = useCallback(() => {
    setWorkspaces([]);
    setActiveWorkspaceId(null);
  }, []);

  /**
   * Check if workspace exists
   */
  const hasWorkspace = useCallback((
    type: WorkspaceType,
    matchPayload?: Partial<WorkspacePayload>
  ): boolean => {
    return workspaces.some(w => {
      if (w.type !== type) return false;
      if (!matchPayload) return true;
      return payloadsMatch(w.payload, matchPayload);
    });
  }, [workspaces]);

  /**
   * Get workspace by ID
   */
  const getWorkspaceById = useCallback((id: string): Workspace | null => {
    return workspaces.find(w => w.id === id) || null;
  }, [workspaces]);

  const activeWorkspace = activeWorkspaceId 
    ? getWorkspaceById(activeWorkspaceId)
    : null;

  return {
    workspaces,
    activeWorkspace,
    openWorkspace,
    closeWorkspace,
    setActiveWorkspace,
    clearWorkspaces,
    hasWorkspace,
    getWorkspaceById,
  };
}

/**
 * Hook for workspace navigation helpers
 */
export function useWorkspaceActions(openWorkspace: UseWorkspacesResult['openWorkspace']) {
  const openMissionDetail = useCallback((missionId: string, title?: string) => {
    return openWorkspace('mission-detail', title || `Mission ${missionId}`, { missionId });
  }, [openWorkspace]);

  const openKPIDashboard = useCallback((filters?: Record<string, any>) => {
    return openWorkspace('kpi-dashboard', 'KPI Dashboard', { filters });
  }, [openWorkspace]);

  const openCRMDashboard = useCallback((filters?: Record<string, any>) => {
    return openWorkspace('crm-dashboard', 'CRM Dashboard', { filters });
  }, [openWorkspace]);

  const openSalesDashboard = useCallback((filters?: Record<string, any>) => {
    return openWorkspace('sales-dashboard', 'Sales Dashboard', { filters });
  }, [openWorkspace]);

  const openArtifactViewer = useCallback((artifactId: string, title?: string) => {
    return openWorkspace('artifact-viewer', title || `Artifact ${artifactId}`, { artifactId });
  }, [openWorkspace]);

  const openCodeDiff = useCallback((filePath: string, commitSha?: string) => {
    return openWorkspace('code-diff', `Diff: ${filePath}`, { filePath, commitSha });
  }, [openWorkspace]);

  const openLogViewer = useCallback((logSource: string, logLevel?: string) => {
    return openWorkspace('log-viewer', `Logs: ${logSource}`, { logSource, logLevel });
  }, [openWorkspace]);

  const openMemoryPreview = useCallback((data: any, title: string = 'Memory Preview') => {
    return openWorkspace('memory-preview', title, { data });
  }, [openWorkspace]);

  return {
    openMissionDetail,
    openKPIDashboard,
    openCRMDashboard,
    openSalesDashboard,
    openArtifactViewer,
    openCodeDiff,
    openLogViewer,
    openMemoryPreview,
  };
}
