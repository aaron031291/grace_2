import type { ReactNode } from 'react';
import './Tag.css';

interface TagProps {
  children: ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
}

export function Tag({ children, variant = 'neutral', size = 'md' }: TagProps) {
  return (
    <span className={`grace-tag grace-tag--${variant} grace-tag--${size}`}>
      {children}
    </span>
  );
}
