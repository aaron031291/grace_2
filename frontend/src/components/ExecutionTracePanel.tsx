import { useState } from 'react';
import type { ExecutionTrace } from '../GraceEnterpriseUI';
import './ExecutionTracePanel.css';

interface ExecutionTracePanelProps {
  trace: ExecutionTrace;
  onClose: () => void;
}

export function ExecutionTracePanel({ trace, onClose }: ExecutionTracePanelProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set([0]));

  const toggleStep = (index: number) => {
    setExpandedSteps(prev => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const copyTraceId = () => {
    navigator.clipboard.writeText(trace.request_id);
  };

  return (
    <div className="execution-trace-panel">
      <div className="trace-panel-header">
        <h3>Execution Trace</h3>
        <button className="trace-panel-close" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="trace-panel-content">
        {/* Overview */}
        <div className="trace-section">
          <div className="trace-section-header">Overview</div>
          <div className="trace-overview">
            <div className="trace-overview-item">
              <span className="trace-label">Request ID:</span>
              <span className="trace-value">
                {trace.request_id.substring(0, 8)}...
                <button className="copy-btn" onClick={copyTraceId} title="Copy full ID">
                  📋
                </button>
              </span>
            </div>
            <div className="trace-overview-item">
              <span className="trace-label">Duration:</span>
              <span className="trace-value">{trace.duration_ms.toFixed(2)}ms</span>
            </div>
            <div className="trace-overview-item">
              <span className="trace-label">Steps:</span>
              <span className="trace-value">{trace.steps.length}</span>
            </div>
          </div>
        </div>

        {/* Steps */}
        <div className="trace-section">
          <div className="trace-section-header">Execution Steps</div>
          <div className="trace-steps">
            {trace.steps.map((step, index) => (
              <div key={index} className="trace-step">
                <button
                  className="trace-step-header"
                  onClick={() => toggleStep(index)}
                >
                  <span className="trace-step-icon">
                    {expandedSteps.has(index) ? '▼' : '▶'}
                  </span>
                  <span className="trace-step-number">{index + 1}.</span>
                  <span className="trace-step-title">{step.action}</span>
                  <span className="trace-step-duration">{step.duration_ms.toFixed(2)}ms</span>
                </button>

                {expandedSteps.has(index) && (
                  <div className="trace-step-details">
                    <div className="trace-detail-row">
                      <span className="trace-detail-label">Component:</span>
                      <span className="trace-detail-value">{step.component}</span>
                    </div>
                    {step.data_source && (
                      <div className="trace-detail-row">
                        <span className="trace-detail-label">Data Source:</span>
                        <span className="trace-detail-value">{step.data_source}</span>
                      </div>
                    )}
                    {step.result && (
                      <div className="trace-detail-row">
                        <span className="trace-detail-label">Result:</span>
                        <pre className="trace-detail-code">
                          {JSON.stringify(step.result, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Data Sources */}
        <div className="trace-section">
          <div className="trace-section-header">Data Sources Used</div>
          <div className="trace-data-sources">
            {trace.data_sources_used.map((source, index) => (
              <div key={index} className="trace-data-source-item">
                <span className="trace-source-icon">📊</span>
                <span className="trace-source-name">{source}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Agents */}
        <div className="trace-section">
          <div className="trace-section-header">Agents Involved</div>
          <div className="trace-agents">
            {trace.agents_involved.map((agent, index) => (
              <div key={index} className="trace-agent-item">
                <span className="trace-agent-icon">🤖</span>
                <span className="trace-agent-name">{agent}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="trace-section">
          <div className="trace-section-header">Actions</div>
          <div className="trace-actions">
            <button className="trace-action-btn">
              📋 View Logs
            </button>
            <button className="trace-action-btn">
              📦 View Artifacts
            </button>
            <button className="trace-action-btn">
              💾 Export Trace
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
