import React, { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import Editor from '@monaco-editor/react';
import { X, Minus, Square, Code, Save, Play } from 'lucide-react';
import { WindowConfig } from '../../stores/windowStore';
import './Window.css';

interface BuilderWindowProps {
  window: WindowConfig;
  onClose: () => void;
  onResize: (width: number, height: number) => void;
  isActive: boolean;
}

export const BuilderWindow: React.FC<BuilderWindowProps> = ({
  window,
  onClose,
  onResize,
  isActive,
}) => {
  const [code, setCode] = useState(window.data?.code || '// Welcome to the Builder!\n// Start coding here...\n\nconsole.log("Hello, Grace!");');
  const [language, setLanguage] = useState(window.data?.language || 'javascript');
  const [fileName, setFileName] = useState(window.data?.fileName || 'untitled.js');
  const resizeRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);

  const handleSave = useCallback(() => {
    // TODO: Implement save functionality
    console.log('Saving code:', { fileName, code, language });
  }, [fileName, code, language]);

  const handleRun = useCallback(() => {
    // TODO: Implement run functionality
    console.log('Running code:', code);
  }, [code]);

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

      const newWidth = Math.max(300, startWidth + deltaX);
      const newHeight = Math.max(200, startHeight + deltaY);

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

  return (
    <div className={`window-content builder-window ${isActive ? 'active' : ''}`}>
      {/* Window Header */}
      <div className="window-header">
        <div className="window-title">
          <Code size={16} />
          <span>Builder - {fileName}</span>
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

      {/* Toolbar */}
      <div className="builder-toolbar">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="language-select"
        >
          <option value="javascript">JavaScript</option>
          <option value="typescript">TypeScript</option>
          <option value="python">Python</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
          <option value="go">Go</option>
        </select>

        <input
          type="text"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          className="filename-input"
          placeholder="filename.ext"
        />

        <div className="toolbar-actions">
          <button onClick={handleSave} className="toolbar-btn">
            <Save size={14} />
            Save
          </button>
          <button onClick={handleRun} className="toolbar-btn run">
            <Play size={14} />
            Run
          </button>
        </div>
      </div>

      {/* Editor */}
      <div className="editor-container">
        <Editor
          height="100%"
          language={language}
          value={code}
          onChange={(value) => setCode(value || '')}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
          }}
        />
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