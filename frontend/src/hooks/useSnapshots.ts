/**
 * useSnapshots Hook
 * 
 * Custom hook for managing system snapshots
 */

import { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL } from '../config';

export interface SnapshotItem {
  id: string;
  snapshot_id?: string;
  snapshot_type: string;
  status: string;
  is_golden: boolean;
  is_validated: boolean;
  system_health_score?: number;
  created_at: string;
  validated_at?: string;
  restored_at?: string;
  triggered_by: string;
  notes?: string;
  label?: string;
  verified_ok?: boolean;
  timestamp?: string;
}

export interface SnapshotStats {
  total_snapshots: number;
  golden_snapshots: number;
  validated_snapshots: number;
  latest_snapshot_id?: string;
  latest_golden_id?: string;
}

export interface SnapshotEvent {
  event_type: 'SNAPSHOT_CREATED' | 'SNAPSHOT_RESTORED' | 'SNAPSHOT_VALIDATED';
  snapshot_id: string;
  timestamp: string;
  triggered_by: string;
  message: string;
}

export const useSnapshots = () => {
  const [snapshots, setSnapshots] = useState<SnapshotItem[]>([]);
  const [goldenSnapshot, setGoldenSnapshot] = useState<SnapshotItem | null>(null);
  const [stats, setStats] = useState<SnapshotStats | null>(null);
  const [events, setEvents] = useState<SnapshotEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSnapshots = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Try verification snapshots first, fallback to boot snapshots
      let snapshotsData;
      try {
        const verificationRes = await fetch(`${API_BASE_URL}/api/verification/snapshots?limit=50`);
        if (verificationRes.ok) {
          const data = await verificationRes.json();
          snapshotsData = data.snapshots || [];
        } else {
          throw new Error('Verification snapshots not available');
        }
      } catch {
        // Fallback to boot snapshots
        const bootRes = await fetch(`${API_BASE_URL}/api/snapshots/list`);
        if (bootRes.ok) {
          const data = await bootRes.json();
          snapshotsData = data.snapshots || [];
        } else {
          throw new Error('Failed to fetch snapshots');
        }
      }

      // Get golden snapshot
      try {
        const goldenRes = await fetch(`${API_BASE_URL}/api/verification/snapshots/golden/latest`);
        if (goldenRes.ok) {
          const golden = await goldenRes.json();
          setGoldenSnapshot(golden);
        }
      } catch {
        // No golden snapshot available
        setGoldenSnapshot(null);
      }

      // Get stats
      try {
        const statsRes = await fetch(`${API_BASE_URL}/api/snapshots/stats`);
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
      } catch {
        // Stats not available
        setStats(null);
      }

      setSnapshots(snapshotsData);
    } catch (err: any) {
      console.error('Failed to fetch snapshots:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const restoreSnapshot = useCallback(async (snapshotId: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/snapshots/restore/${snapshotId}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to restore snapshot: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Add event
      setEvents(prev => [{
        event_type: 'SNAPSHOT_RESTORED',
        snapshot_id: snapshotId,
        timestamp: new Date().toISOString(),
        triggered_by: 'user',
        message: `Snapshot ${snapshotId} restored`
      }, ...prev]);
      
      return result.restored || result.success || true;
    } catch (err: any) {
      console.error('Failed to restore snapshot:', err);
      throw err;
    }
  }, []);

  const createSnapshot = useCallback(async (label: string, notes?: string): Promise<string> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/snapshots/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ label, notes })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create snapshot: ${response.statusText}`);
      }
      
      const result = await response.json();
      const snapshotId = result.snapshot_id || result.id;
      
      // Add event
      setEvents(prev => [{
        event_type: 'SNAPSHOT_CREATED',
        snapshot_id: snapshotId,
        timestamp: new Date().toISOString(),
        triggered_by: 'user',
        message: `Snapshot created: ${label}`
      }, ...prev]);
      
      // Refresh list
      await fetchSnapshots();
      
      return snapshotId;
    } catch (err: any) {
      console.error('Failed to create snapshot:', err);
      throw err;
    }
  }, [fetchSnapshots]);

  useEffect(() => {
    fetchSnapshots();
    const interval = setInterval(fetchSnapshots, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchSnapshots]);

  return {
    snapshots,
    goldenSnapshot,
    stats,
    events,
    loading,
    error,
    refresh: fetchSnapshots,
    restoreSnapshot,
    createSnapshot
  };
};
