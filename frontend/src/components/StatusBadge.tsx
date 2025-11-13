/**
 * Status Badge Component
 * Shows routing/ingestion status for files and folders
 */

import { Clock, CheckCircle, AlertCircle, Zap, Eye, Loader } from 'lucide-react';

export type BadgeStatus = 
  | 'waiting'
  | 'enqueued'
  | 'ingested'
  | 'running_ml'
  | 'needs_approval'
  | 'trusted'
  | 'untrusted'
  | 'synced';

export interface StatusBadgeProps {
  status: BadgeStatus;
  size?: 'sm' | 'md';
}

export function StatusBadge({ status, size = 'sm' }: StatusBadgeProps) {
  const configs = {
    waiting: {
      icon: Clock,
      label: 'Waiting',
      colors: 'bg-gray-700 text-gray-300'
    },
    enqueued: {
      icon: Loader,
      label: 'Queued',
      colors: 'bg-blue-900 text-blue-300 animate-pulse'
    },
    ingested: {
      icon: CheckCircle,
      label: 'Ingested',
      colors: 'bg-green-900 text-green-300'
    },
    running_ml: {
      icon: Zap,
      label: 'Processing',
      colors: 'bg-purple-900 text-purple-300 animate-pulse'
    },
    needs_approval: {
      icon: AlertCircle,
      label: 'Needs Approval',
      colors: 'bg-orange-900 text-orange-300'
    },
    trusted: {
      icon: CheckCircle,
      label: 'Trusted',
      colors: 'bg-green-900 text-green-300'
    },
    untrusted: {
      icon: AlertCircle,
      label: 'Untrusted',
      colors: 'bg-red-900 text-red-300'
    },
    synced: {
      icon: CheckCircle,
      label: 'Synced',
      colors: 'bg-blue-900 text-blue-300'
    }
  };

  const config = configs[status];
  const Icon = config.icon;
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  const textSize = size === 'sm' ? 'text-xs' : 'text-sm';

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded ${config.colors} ${textSize}`}
      title={config.label}
    >
      <Icon className={iconSize} />
      <span>{config.label}</span>
    </span>
  );
}
