import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { X, Minus, Square, Activity, Cpu, HardDrive, Wifi, Zap } from 'lucide-react';
import { type WindowConfig } from '../../stores/windowStore';
import './Window.css';

interface HealthWindowProps {
  window: WindowConfig;
  onClose: () => void;
  onResize: (width: number, height: number) => void;
  isActive: boolean;
}

interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  uptime: number;
  temperature: number;
}

export const HealthWindow: React.FC<HealthWindowProps> = ({
  window,
  onClose,
  onResize,
  isActive,
}) => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: 45,
    memory: 67,
    disk: 23,
    network: 12,
    uptime: 86400, // 24 hours in seconds
    temperature: 42,
  });

  const resizeRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);

  // Simulate real-time metrics updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        cpu: Math.max(0, Math.min(100, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(0, Math.min(100, prev.memory + (Math.random() - 0.5) * 5)),
        disk: Math.max(0, Math.min(100, prev.disk + (Math.random() - 0.5) * 2)),
        network: Math.max(0, Math.min(100, prev.network + (Math.random() - 0.5) * 15)),
        uptime: prev.uptime + 1,
        temperature: Math.max(30, Math.min(80, prev.temperature + (Math.random() - 0.5) * 2)),
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!resizeRef.current) return;

    isResizing.current = true;
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = window.width;
    const startHeight = window.height;

    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing.current) return;

      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;

      const newWidth = Math.max(400, startWidth + deltaX);
      const newHeight = Math.max(300, startHeight + deltaY);

      onResize(newWidth, newHeight);
    };

    const handleMouseUp = () => {
      isResizing.current = false;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [window.width, window.height, onResize]);

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const getStatusColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'critical';
    if (value >= thresholds.warning) return 'warning';
    return 'normal';
  };

  const MetricCard = ({ icon: Icon, label, value, unit, thresholds }: {
    icon: any;
    label: string;
    value: number;
    unit: string;
    thresholds: { warning: number; critical: number };
  }) => (
    <div className={`metric-card ${getStatusColor(value, thresholds)}`}>
      <div className="metric-header">
        <Icon size={20} />
        <span className="metric-label">{label}</span>
      </div>
      <div className="metric-value">
        {value.toFixed(1)}{unit}
      </div>
      <div className="metric-bar">
        <div
          className="metric-fill"
          style={{ width: `${Math.min(100, value)}%` }}
        />
      </div>
    </div>
  );

  return (
    <div className={`window-content health-window ${isActive ? 'active' : ''}`}>
      {/* Window Header */}
      <div className="window-header">
        <div className="window-title">
          <Activity size={16} />
          <span>System Health Monitor</span>
        </div>
        <div className="window-controls">
          <button className="window-btn minimize">
            <Minus size={12} />
          </button>
          <button className="window-btn maximize">
            <Square size={12} />
          </button>
          <button className="window-btn close" onClick={onClose}>
            <X size={12} />
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="health-metrics">
        <MetricCard
          icon={Cpu}
          label="CPU Usage"
          value={metrics.cpu}
          unit="%"
          thresholds={{ warning: 70, critical: 90 }}
        />
        <MetricCard
          icon={HardDrive}
          label="Memory"
          value={metrics.memory}
          unit="%"
          thresholds={{ warning: 80, critical: 95 }}
        />
        <MetricCard
          icon={HardDrive}
          label="Disk Usage"
          value={metrics.disk}
          unit="%"
          thresholds={{ warning: 85, critical: 95 }}
        />
        <MetricCard
          icon={Wifi}
          label="Network"
          value={metrics.network}
          unit="%"
          thresholds={{ warning: 70, critical: 90 }}
        />
        <MetricCard
          icon={Zap}
          label="Temperature"
          value={metrics.temperature}
          unit="°C"
          thresholds={{ warning: 60, critical: 75 }}
        />

        {/* Uptime Display */}
        <div className="metric-card uptime">
          <div className="metric-header">
            <Activity size={20} />
            <span className="metric-label">Uptime</span>
          </div>
          <div className="metric-value uptime-value">
            {formatUptime(metrics.uptime)}
          </div>
        </div>
      </div>

      {/* Status Summary */}
      <div className="health-status">
        <div className="status-indicator">
          <div className="status-light healthy"></div>
          <span>All Systems Operational</span>
        </div>
        <div className="last-updated">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Resize Handle */}
      <div
        ref={resizeRef}
        className="resize-handle"
        onMouseDown={handleMouseDown}
      />
    </div>
  );
};