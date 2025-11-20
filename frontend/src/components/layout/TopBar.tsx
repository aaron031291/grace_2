import React from 'react';
import './TopBar.css';

type Mode = 'observe' | 'learn' | 'autonomous';

type TopBarProps = {
  title: string;
  mode: Mode;
  onModeChange?: (mode: Mode) => void;
  onSelfHealing?: () => void;
  onEmergencyStop?: () => void;
};

export const TopBar: React.FC<TopBarProps> = ({
  title,
  mode,
  onModeChange,
  onSelfHealing,
  onEmergencyStop,
}) => {
  const modes: Mode[] = ['observe', 'learn', 'autonomous'];

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <h1 className="top-bar-title">{title}</h1>
        <span className="top-bar-mode-badge">
          Mode: {mode}
        </span>
      </div>

      <div className="top-bar-right">
        <div className="top-bar-mode-switcher">
          {modes.map((m) => (
            <button
              key={m}
              onClick={() => onModeChange?.(m)}
              className={`mode-btn ${mode === m ? 'active' : ''}`}
            >
              {m}
            </button>
          ))}
        </div>

        {onSelfHealing && (
          <button
            onClick={onSelfHealing}
            className="top-bar-action-btn self-healing"
            title="Trigger self-healing playbook"
          >
            🔧 Self-Heal
          </button>
        )}

        {onEmergencyStop && (
          <button
            onClick={onEmergencyStop}
            className="top-bar-action-btn emergency-stop"
            title="Emergency stop all operations"
          >
            🛑 Stop
          </button>
        )}
      </div>
    </div>
  );
};
