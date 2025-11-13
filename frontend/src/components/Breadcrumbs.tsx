/**
 * Breadcrumb Navigation Component
 * Shows current path with clickable segments for navigation
 */

import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbsProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

export function Breadcrumbs({ currentPath, onNavigate }: BreadcrumbsProps) {
  // Parse path into segments
  const segments = currentPath
    .split('/')
    .filter(s => s.length > 0);

  const handleClick = (index: number) => {
    if (index === -1) {
      // Root
      onNavigate('storage/uploads');
    } else {
      // Build path up to this segment
      const path = segments.slice(0, index + 1).join('/');
      onNavigate(path || 'storage/uploads');
    }
  };

  return (
    <div className="flex items-center gap-2 text-sm text-gray-400">
      {/* Root/Home */}
      <button
        onClick={() => handleClick(-1)}
        className="flex items-center gap-1 hover:text-blue-400 transition-colors"
      >
        <Home className="w-4 h-4" />
        <span>Root</span>
      </button>

      {/* Path segments */}
      {segments.map((segment, index) => (
        <div key={index} className="flex items-center gap-2">
          <ChevronRight className="w-4 h-4" />
          <button
            onClick={() => handleClick(index)}
            className={`hover:text-blue-400 transition-colors ${
              index === segments.length - 1 ? 'text-white font-medium' : ''
            }`}
          >
            {segment}
          </button>
        </div>
      ))}
    </div>
  );
}
