/**
 * Memory Explorer - Part 2: Upload Panel and Helper Components
 */

import React from 'react';
import type { IngestionProgress } from '../types/memory.types';

// ========== Upload Panel ==========

interface UploadPanelProps {
  mode: 'text' | 'file' | 'voice';
  setMode: (mode: 'text' | 'file' | 'voice') => void;
  textTitle: string;
  setTextTitle: (title: string) => void;
  textContent: string;
  setTextContent: (content: string) => void;
  voiceTitle: string;
  setVoiceTitle: (title: string) => void;
  recording: boolean;
  audioBlob: Blob | null;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onFileSelect: (files: FileList | null) => void;
  onTextSubmit: () => void;
  onVoiceSubmit: () => void;
  uploadProgress: IngestionProgress | null;
  dragActive: boolean;
  onDrag: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  fileInputRef: React.RefObject<HTMLInputElement>;
  uploading: boolean;
}

export function UploadPanel(props: UploadPanelProps) {
  const {
    mode,
    setMode,
    textTitle,
    setTextTitle,
    textContent,
    setTextContent,
    voiceTitle,
    setVoiceTitle,
    recording,
    audioBlob,
    onStartRecording,
    onStopRecording,
    onFileSelect,
    onTextSubmit,
    onVoiceSubmit,
    uploadProgress,
    dragActive,
    onDrag,
    onDrop,
    fileInputRef,
    uploading,
  } = props;

  return (
    <div className="upload-panel">
      <div className="upload-tabs">
        <button
          className={mode === 'file' ? 'active' : ''}
          onClick={() => setMode('file')}
        >
          📁 File
        </button>
        <button
          className={mode === 'text' ? 'active' : ''}
          onClick={() => setMode('text')}
        >
          📝 Text
        </button>
        <button
          className={mode === 'voice' ? 'active' : ''}
          onClick={() => setMode('voice')}
        >
          🎤 Voice
        </button>
      </div>

      <div className="upload-content">
        {uploadProgress ? (
          <ProgressDisplay progress={uploadProgress} />
        ) : mode === 'file' ? (
          <FileUploadZone
            dragActive={dragActive}
            onDrag={onDrag}
            onDrop={onDrop}
            onFileSelect={onFileSelect}
            fileInputRef={fileInputRef}
          />
        ) : mode === 'text' ? (
          <TextUploadForm
            title={textTitle}
            setTitle={setTextTitle}
            content={textContent}
            setContent={setTextContent}
            onSubmit={onTextSubmit}
            disabled={uploading}
          />
        ) : (
          <VoiceUploadForm
            title={voiceTitle}
            setTitle={setVoiceTitle}
            recording={recording}
            audioBlob={audioBlob}
            onStart={onStartRecording}
            onStop={onStopRecording}
            onSubmit={onVoiceSubmit}
            disabled={uploading}
          />
        )}
      </div>
    </div>
  );
}

function FileUploadZone({ dragActive, onDrag, onDrop, onFileSelect, fileInputRef }: any) {
  return (
    <div
      className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
      onDragEnter={onDrag}
      onDragLeave={onDrag}
      onDragOver={onDrag}
      onDrop={onDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <div className="drop-zone-icon">📤</div>
      <h4>Upload File</h4>
      <p>Drag & drop or click to browse</p>
      <p className="supported-formats">PDF, DOCX, TXT, MD, Images, Audio</p>
      <input
        ref={fileInputRef}
        type="file"
        onChange={(e) => onFileSelect(e.target.files)}
        style={{ display: 'none' }}
        accept=".pdf,.doc,.docx,.txt,.md,.png,.jpg,.jpeg,.mp3,.wav"
      />
    </div>
  );
}

function TextUploadForm({ title, setTitle, content, setContent, onSubmit, disabled }: any) {
  return (
    <div className="text-upload-form">
      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="text-title-input"
        disabled={disabled}
      />
      <textarea
        placeholder="Paste or type content here..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="text-content-input"
        rows={8}
        disabled={disabled}
      />
      <button
        onClick={onSubmit}
        className="submit-btn"
        disabled={disabled || !title.trim() || !content.trim()}
      >
        {disabled ? 'Uploading...' : 'Ingest Text'}
      </button>
    </div>
  );
}

function VoiceUploadForm({ title, setTitle, recording, audioBlob, onStart, onStop, onSubmit, disabled }: any) {
  return (
    <div className="voice-upload-form">
      <input
        type="text"
        placeholder="Recording title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="voice-title-input"
        disabled={disabled || recording}
      />
      
      <div className="recording-controls">
        {!recording && !audioBlob && (
          <button onClick={onStart} className="record-btn" disabled={disabled}>
            🎤 Start Recording
          </button>
        )}
        
        {recording && (
          <button onClick={onStop} className="record-btn recording">
            ⏹️ Stop Recording
          </button>
        )}
        
        {audioBlob && !recording && (
          <>
            <div className="audio-ready">✅ Recording ready</div>
            <button
              onClick={onSubmit}
              className="submit-btn"
              disabled={disabled || !title.trim()}
            >
              Upload Voice
            </button>
          </>
        )}
      </div>
      
      {recording && (
        <div className="recording-indicator">
          <span className="pulse-dot"></span>
          Recording...
        </div>
      )}
    </div>
  );
}

function ProgressDisplay({ progress }: { progress: IngestionProgress }) {
  const getStatusLabel = (status: IngestionProgress['status']) => {
    const labels = {
      uploading: 'Uploading file...',
      parsing: 'Parsing content...',
      chunking: 'Creating chunks...',
      embedding: 'Generating embeddings...',
      indexing: 'Indexing vectors...',
      complete: 'Complete!',
      failed: 'Failed',
    };
    return labels[status] || status;
  };

  return (
    <div className="upload-progress-display">
      <div className="progress-status">{getStatusLabel(progress.status)}</div>
      <div className="progress-bar-container">
        <div 
          className="progress-bar-fill" 
          style={{ 
            width: `${progress.progress}%`,
            background: progress.status === 'failed' ? '#ff4444' : 'linear-gradient(90deg, #00ccff, #00ff88)'
          }}
        />
      </div>
      <div className="progress-percentage">{progress.progress}%</div>
      {progress.message && <div className="progress-message">{progress.message}</div>}
      {progress.chunks_processed !== undefined && (
        <div className="progress-chunks">
          {progress.chunks_processed} / {progress.chunks_total} chunks
        </div>
      )}
    </div>
  );
}

function DetailSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="detail-section">
      <h4>{title}</h4>
      <div className="section-content">{children}</div>
    </div>
  );
}

function InfoRow({ label, value, mono, badge }: any) {
  return (
    <div className="info-row">
      <span className="info-label">{label}:</span>
      <span className={`info-value ${mono ? 'mono' : ''} ${badge ? 'badge' : ''}`}>
        {value}
      </span>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="state-container loading-state">
      <div className="loading-spinner"></div>
      <p>Loading artifacts...</p>
    </div>
  );
}

function ErrorState({ error, onRetry }: any) {
  return (
    <div className="state-container error-state">
      <div className="state-icon">⚠️</div>
      <h3>Failed to load artifacts</h3>
      <p className="error-message">{error.message}</p>
      <button onClick={onRetry} className="retry-btn">Retry</button>
    </div>
  );
}

function EmptyState({ onUpload }: { onUpload: () => void }) {
  return (
    <div className="state-container empty-state">
      <div className="state-icon">📦</div>
      <h3>No artifacts found</h3>
      <p>Upload files or ingest text to build Grace's knowledge base</p>
      <button onClick={onUpload} className="upload-btn-large">
        + Add Knowledge
      </button>
    </div>
  );
}

// ========== Helpers ==========

function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    pdf: '📄',
    text: '📝',
    audio: '🎵',
    image: '🖼️',
    code: '💻',
    json: '📋',
    markdown: '📝',
    'web-page': '🌐',
    'chat-log': '💬',
  };
  return icons[type] || '📦';
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

export { UploadPanel, DetailSection, InfoRow, LoadingState, ErrorState, EmptyState };
