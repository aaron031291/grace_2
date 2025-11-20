import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';
import type { ReactNode } from 'react';
import './Card.css';

interface CardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  variant?: 'default' | 'elevated' | 'bordered';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export function Card({ 
  children, 
  variant = 'default', 
  padding = 'md',
  hover = false,
  className = '',
  ...props 
}: CardProps) {
  const classNames = [
    'grace-card',
    `grace-card--${variant}`,
    `grace-card--padding-${padding}`,
    hover && 'grace-card--hover',
    className
  ].filter(Boolean).join(' ');

  return (
    <motion.div
      className={classNames}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {children}
    </motion.div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  action?: ReactNode;
}

export function CardHeader({ children, action }: CardHeaderProps) {
  return (
    <div className="grace-card__header">
      <div className="grace-card__title">{children}</div>
      {action && <div className="grace-card__action">{action}</div>}
    </div>
  );
}

export function CardContent({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`grace-card__content ${className}`}>{children}</div>;
}
