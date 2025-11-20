import type { ReactNode } from 'react';
import './Surface.css';

interface SurfaceProps {
  children: ReactNode;
  className?: string;
}

export function Surface({ children, className = '' }: SurfaceProps) {
  return (
    <div className={`grace-surface ${className}`}>
      {children}
    </div>
  );
}
