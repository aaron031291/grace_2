import React, { useRef, useCallback } from 'react';
import { motion, PanInfo } from 'framer-motion';
import { useWindowStore, WindowConfig } from '../../stores/windowStore';
import { BuilderWindow } from './BuilderWindow';
import { HealthWindow } from './HealthWindow';
import { MemoryWindow } from './MemoryWindow';
import './WindowManager.css';

interface WindowManagerProps {
  className?: string;
}

export const WindowManager: React.FC<WindowManagerProps> = ({ className }) => {
  const { windows, activeWindowId, setActiveWindow, updateWindow, closeWindow } = useWindowStore();
  const containerRef = useRef<HTMLDivElement>(null);

  const handleWindowClick = useCallback((windowId: string) => {
    setActiveWindow(windowId);
  }, [setActiveWindow]);

  const handleDragEnd = useCallback((windowId: string, event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const window = windows.find(w => w.id === windowId);
    if (!window) return;

    const newX = Math.max(0, window.x + info.offset.x);
    const newY = Math.max(0, window.y + info.offset.y);

    updateWindow(windowId, { x: newX, y: newY });
  }, [windows, updateWindow]);

  const handleResize = useCallback((windowId: string, width: number, height: number) => {
    updateWindow(windowId, { width, height });
  }, [updateWindow]);

  const renderWindow = (window: WindowConfig) => {
    const isActive = activeWindowId === window.id;
    const isMinimized = window.minimized;
    const isMaximized = window.maximized;

    if (isMinimized) return null;

    const windowStyle = isMaximized
      ? { x: 0, y: 0, width: '100%', height: '100%' }
      : { x: window.x, y: window.y, width: window.width, height: window.height };

    let WindowComponent: React.ComponentType<any>;

    switch (window.type) {
      case 'builder':
        WindowComponent = BuilderWindow;
        break;
      case 'health':
        WindowComponent = HealthWindow;
        break;
      case 'memory':
        WindowComponent = MemoryWindow;
        break;
      default:
        return null;
    }

    return (
      <motion.div
        key={window.id}
        className={`window ${isActive ? 'active' : ''} ${isMaximized ? 'maximized' : ''}`}
        style={{
          zIndex: window.zIndex,
          position: 'absolute',
        }}
        initial={windowStyle}
        animate={windowStyle}
        drag={!isMaximized}
        dragMomentum={false}
        dragConstraints={containerRef}
        onDragEnd={(event, info) => handleDragEnd(window.id, event, info)}
        onClick={() => handleWindowClick(window.id)}
        transition={{ type: 'tween', duration: 0.1 }}
      >
        <WindowComponent
          window={window}
          onClose={() => closeWindow(window.id)}
          onResize={(width, height) => handleResize(window.id, width, height)}
          isActive={isActive}
        />
      </motion.div>
    );
  };

  return (
    <div ref={containerRef} className={`window-manager ${className || ''}`}>
      {windows.map(renderWindow)}
    </div>
  );
};