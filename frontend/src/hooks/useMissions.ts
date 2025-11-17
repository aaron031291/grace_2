/**
 * useMissions Hook
 * React hook for fetching and managing missions data
 * 
 * Features:
 * - Auto-refresh with configurable interval
 * - Loading, error, and empty states
 * - Optimistic updates
 * - Action handlers (execute, acknowledge, etc.)
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  fetchMissions,
  fetchMissionDetails,
  executeMission as executeMissionApi,
  acknowledgeMission as acknowledgeMissionApi,
  type Mission,
  type MissionDetail,
  type MissionFilters,
  MissionApiError,
} from '../services/missionApi';

export interface UseMissionsOptions {
  filters?: MissionFilters;
  autoRefresh?: boolean;
  refreshInterval?: number; // milliseconds
  onError?: (error: Error) => void;
}

export interface UseMissionsResult {
  // Data
  missions: Mission[];
  total: number;
  
  // State
  loading: boolean;
  error: Error | null;
  isEmpty: boolean;
  
  // Actions
  refresh: () => Promise<void>;
  executeMission: (missionId: string, missionType?: 'coding' | 'healing') => Promise<void>;
  acknowledgeMission: (missionId: string) => Promise<void>;
  getMissionDetails: (missionId: string) => Promise<MissionDetail | null>;
  
  // Config
  setFilters: (filters: MissionFilters) => void;
  setAutoRefresh: (enabled: boolean) => void;
}

const DEFAULT_REFRESH_INTERVAL = 30000; // 30 seconds

export function useMissions(options: UseMissionsOptions = {}): UseMissionsResult {
  const {
    filters: initialFilters = {},
    autoRefresh: initialAutoRefresh = true,
    refreshInterval = DEFAULT_REFRESH_INTERVAL,
    onError,
  } = options;

  const [missions, setMissions] = useState<Mission[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [filters, setFilters] = useState<MissionFilters>(initialFilters);
  const [autoRefresh, setAutoRefresh] = useState(initialAutoRefresh);

  // Use ref to avoid recreating refresh function
  const filtersRef = useRef(filters);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  /**
   * Fetch missions from API
   */
  const refresh = useCallback(async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
    }
    setError(null);

    try {
      const response = await fetchMissions(filtersRef.current);
      setMissions(response.missions);
      setTotal(response.total);
      setError(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch missions');
      setError(error);
      
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      
      console.error('Failed to fetch missions:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Execute a mission with optimistic update
   */
  const executeMission = useCallback(async (
    missionId: string,
    missionType: 'coding' | 'healing' = 'coding'
  ) => {
    // Optimistic update
    setMissions(prev => prev.map(m =>
      m.mission_id === missionId
        ? { ...m, status: 'in_progress' as const }
        : m
    ));

    try {
      await executeMissionApi(missionId, missionType);
      // Refresh to get actual server state
      await refresh(false);
    } catch (err) {
      // Revert optimistic update on error
      await refresh(false);
      
      const error = err instanceof Error ? err : new Error('Failed to execute mission');
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      throw error;
    }
  }, [refresh]);

  /**
   * Acknowledge a mission
   */
  const acknowledgeMission = useCallback(async (missionId: string) => {
    try {
      await acknowledgeMissionApi(missionId);
      await refresh(false);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to acknowledge mission');
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      throw error;
    }
  }, [refresh]);

  /**
   * Get detailed information for a specific mission
   */
  const getMissionDetails = useCallback(async (missionId: string): Promise<MissionDetail | null> => {
    try {
      return await fetchMissionDetails(missionId);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch mission details');
      if (onErrorRef.current) {
        onErrorRef.current(error);
      }
      console.error('Failed to fetch mission details:', error);
      return null;
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    refresh();
  }, [refresh]);

  // Auto-refresh setup
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refresh(false); // Silent refresh (no loading spinner)
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refresh]);

  const isEmpty = !loading && missions.length === 0;

  return {
    // Data
    missions,
    total,
    
    // State
    loading,
    error,
    isEmpty,
    
    // Actions
    refresh,
    executeMission,
    acknowledgeMission,
    getMissionDetails,
    
    // Config
    setFilters,
    setAutoRefresh,
  };
}

/**
 * Hook for fetching a single mission's details
 */
export function useMissionDetails(missionId: string | null) {
  const [mission, setMission] = useState<MissionDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    if (!missionId) {
      setMission(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const details = await fetchMissionDetails(missionId);
      setMission(details);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch mission details');
      setError(error);
      console.error('Failed to fetch mission details:', error);
    } finally {
      setLoading(false);
    }
  }, [missionId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    mission,
    loading,
    error,
    refresh,
  };
}

/**
 * Hook for mission statistics
 */
export function useMissionStats(missions: Mission[]) {
  return {
    total: missions.length,
    byStatus: missions.reduce((acc, m) => {
      acc[m.status] = (acc[m.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    bySeverity: missions.reduce((acc, m) => {
      acc[m.severity] = (acc[m.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    bySubsystem: missions.reduce((acc, m) => {
      acc[m.subsystem_id] = (acc[m.subsystem_id] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
  };
}
