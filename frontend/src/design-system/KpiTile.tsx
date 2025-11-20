import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import './KpiTile.css';

interface KpiTileProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  status?: 'success' | 'warning' | 'error' | 'info';
  onClick?: () => void;
}

export function KpiTile({ 
  label, 
  value, 
  icon, 
  trend, 
  trendValue, 
  status,
  onClick 
}: KpiTileProps) {
  const classNames = [
    'grace-kpi-tile',
    status && `grace-kpi-tile--${status}`,
    onClick && 'grace-kpi-tile--clickable'
  ].filter(Boolean).join(' ');

  return (
    <motion.div
      className={classNames}
      onClick={onClick}
      whileHover={onClick ? { scale: 1.02 } : {}}
      whileTap={onClick ? { scale: 0.98 } : {}}
    >
      <div className="grace-kpi-tile__header">
        <span className="grace-kpi-tile__label">{label}</span>
        {icon && <span className="grace-kpi-tile__icon">{icon}</span>}
      </div>
      <div className="grace-kpi-tile__value">{value}</div>
      {(trend || trendValue) && (
        <div className={`grace-kpi-tile__trend grace-kpi-tile__trend--${trend || 'neutral'}`}>
          {trendValue}
        </div>
      )}
    </motion.div>
  );
}
