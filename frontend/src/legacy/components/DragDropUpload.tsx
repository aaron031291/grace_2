import { useState, useCallback, DragEvent } from 'react';
import './DragDropUpload.css';

interface DragDropUploadProps {
  onFilesDropped: (files: File[]) => void;
  children: React.ReactNode;
  acceptedTypes?: string[];
  maxFiles?: number;
  maxSizeMB?: number;
}

export function DragDropUpload({
  onFilesDropped,
  children,
  acceptedTypes = [],
  maxFiles = 10,
  maxSizeMB = 100,
}: DragDropUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);

  const handleDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(prev => prev + 1);
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(prev => {
      const newCount = prev - 1;
      if (newCount === 0) {
        setIsDragging(false);
      }
      return newCount;
    });
  }, []);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    setDragCounter(0);

    const files = Array.from(e.dataTransfer.files);
    
    if (files.length === 0) return;

    if (files.length > maxFiles) {
      alert(`Maximum ${maxFiles} files allowed`);
      return;
    }

    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    const oversizedFiles = files.filter(f => f.size > maxSizeBytes);
    if (oversizedFiles.length > 0) {
      alert(`Some files exceed ${maxSizeMB}MB limit: ${oversizedFiles.map(f => f.name).join(', ')}`);
      return;
    }

    if (acceptedTypes.length > 0) {
      const invalidFiles = files.filter(f => {
        const ext = '.' + f.name.split('.').pop()?.toLowerCase();
        return !acceptedTypes.includes(ext);
      });
      if (invalidFiles.length > 0) {
        alert(`Invalid file types: ${invalidFiles.map(f => f.name).join(', ')}\nAccepted: ${acceptedTypes.join(', ')}`);
        return;
      }
    }

    onFilesDropped(files);
  }, [onFilesDropped, acceptedTypes, maxFiles, maxSizeMB]);

  return (
    <div
      className="drag-drop-container"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {children}
      {isDragging && (
        <div className="drag-overlay">
          <div className="drag-overlay-content">
            <div className="drag-icon">📁</div>
            <div className="drag-text">Drop files here to upload</div>
            <div className="drag-subtext">
              {acceptedTypes.length > 0 && (
                <span>Accepted: {acceptedTypes.join(', ')}</span>
              )}
              {maxFiles > 1 && (
                <span>Max {maxFiles} files, {maxSizeMB}MB each</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface FileUploadPreviewProps {
  files: File[];
  onSave: (destination: string) => void;
  onIngest: () => void;
  onAttach: () => void;
  onDiscard: () => void;
}

export function FileUploadPreview({
  files,
  onSave,
  onIngest,
  onAttach,
  onDiscard,
}: FileUploadPreviewProps) {
  const [destination, setDestination] = useState('grace_training/documents');

  const totalSize = files.reduce((sum, f) => sum + f.size, 0);
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="file-upload-preview">
      <div className="preview-header">
        <h3>Files Ready to Upload</h3>
        <span className="file-count">{files.length} file{files.length !== 1 ? 's' : ''} ({formatSize(totalSize)})</span>
      </div>

      <div className="preview-files">
        {files.map((file, idx) => (
          <div key={idx} className="preview-file-item">
            <span className="file-icon">📄</span>
            <div className="file-info">
              <div className="file-name">{file.name}</div>
              <div className="file-meta">{formatSize(file.size)} • {file.type || 'unknown'}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="preview-actions">
        <div className="destination-selector">
          <label>Save to:</label>
          <select value={destination} onChange={(e) => setDestination(e.target.value)}>
            <option value="grace_training/documents">Documents</option>
            <option value="grace_training/codebases">Codebases</option>
            <option value="grace_training/datasets">Datasets</option>
            <option value="grace_training/playbooks">Playbooks</option>
            <option value="grace_training/governance">Governance</option>
          </select>
          <button className="action-btn primary-btn" onClick={() => onSave(destination)}>
            Save to Memory
          </button>
        </div>

        <div className="action-buttons">
          <button className="action-btn secondary-btn" onClick={onIngest}>
            Ingest as Knowledge
          </button>
          <button className="action-btn secondary-btn" onClick={onAttach}>
            Attach to Message
          </button>
          <button className="action-btn danger-btn" onClick={onDiscard}>
            Discard
          </button>
        </div>
      </div>
    </div>
  );
}
