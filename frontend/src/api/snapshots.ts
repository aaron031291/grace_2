/**
 * Snapshots API Client
 * 
 * Provides access to system snapshots for rollback/restore
 */

import { API_BASE_URL } from '../config';

export interface Snapshot {
  snapshot_id: string;
  timestamp: string;
  label: string;
  verified_ok: boolean;
  config_hash?: string;
  git_sha?: string;
  size_mb?: number;
  description?: string;
}

export interface SnapshotsResponse {
  snapshots: Snapshot[];
  count: number;
}

export const SnapshotAPI = {
  /**
   * List all snapshots
   */
  async listSnapshots(): Promise<SnapshotsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/snapshots/list`);
    if (!response.ok) {
      throw new Error(`Failed to fetch snapshots: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Create a new snapshot
   */
  async createSnapshot(label: string, description?: string): Promise<Snapshot> {
    const response = await fetch(`${API_BASE_URL}/api/snapshots/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ label, description })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create snapshot: ${response.statusText}`);
    }
    
    return response.json();
  },

  /**
   * Restore from a snapshot
   */
  async restoreSnapshot(snapshotId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/snapshots/restore/${snapshotId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to restore snapshot: ${response.statusText}`);
    }
  },

  /**
   * Delete a snapshot
   */
  async deleteSnapshot(snapshotId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/snapshots/delete/${snapshotId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete snapshot: ${response.statusText}`);
    }
  },

  /**
   * Verify a snapshot
   */
  async verifySnapshot(snapshotId: string): Promise<{ verified: boolean; issues?: string[] }> {
    const response = await fetch(`${API_BASE_URL}/api/snapshots/verify/${snapshotId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to verify snapshot: ${response.statusText}`);
    }
    
    return response.json();
  }
};
