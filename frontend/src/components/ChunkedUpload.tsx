/**
 * Chunked Upload Component
 *
 * Handles large file uploads with:
 * - Automatic chunking for large files
 * - Progress tracking and resume capability
 * - Error recovery and retry logic
 * - Concurrent upload management
 * - Pause/resume functionality
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Upload, Pause, Play, X, RotateCcw, CheckCircle, AlertCircle } from 'lucide-react';
import './ChunkedUpload.css';

interface ChunkedUploadProps {
  onUploadComplete?: (result: UploadResult) => void;
  onUploadError?: (error: UploadError) => void;
  onProgress?: (progress: UploadProgress) => void;
  chunkSize?: number; // in bytes
  maxConcurrent?: number;
  maxRetries?: number;
  accept?: string;
  maxFileSize?: number; // in bytes
}

interface UploadResult {
  fileId: string;
  filename: string;
  size: number;
  chunks: number;
  checksum: string;
  uploadTime: number;
}

interface UploadError {
  fileId: string;
  filename: string;
  error: string;
  chunkIndex?: number;
  retryCount?: number;
}

interface UploadProgress {
  fileId: string;
  filename: string;
  progress: number; // 0-100
  uploadedBytes: number;
  totalBytes: number;
  speed: number; // bytes per second
  eta: number; // estimated time remaining in seconds
  status: 'uploading' | 'paused' | 'completed' | 'error' | 'retrying';
  currentChunk: number;
  totalChunks: number;
}

interface FileUploadState {
  id: string;
  file: File;
  progress: UploadProgress;
  chunks: Chunk[];
  isPaused: boolean;
  abortController: AbortController;
}

interface Chunk {
  index: number;
  start: number;
  end: number;
  size: number;
  data: Blob;
  uploaded: boolean;
  retries: number;
  checksum: string;
}

const CHUNK_SIZE = 1024 * 1024; // 1MB default
const MAX_CONCURRENT = 3;
const MAX_RETRIES = 3;

export const ChunkedUpload: React.FC<ChunkedUploadProps> = ({
  onUploadComplete,
  onUploadError,
  onProgress,
  chunkSize = CHUNK_SIZE,
  maxConcurrent = MAX_CONCURRENT,
  maxRetries = MAX_RETRIES,
  accept = '*',
  maxFileSize
}) => {
  const [uploads, setUploads] = useState<Map<string, FileUploadState>>(new Map());
  const [isDragging, setIsDragging] = useState(false);
  const [globalStats, setGlobalStats] = useState({
    totalUploads: 0,
    activeUploads: 0,
    completedUploads: 0,
    failedUploads: 0,
    totalBytes: 0,
    uploadedBytes: 0
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Calculate file checksum
  const calculateChecksum = useCallback(async (data: Blob): Promise<string> => {
    const buffer = await data.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }, []);

  // Create chunks from file
  const createChunks = useCallback(async (file: File, chunkSize: number): Promise<Chunk[]> => {
    const chunks: Chunk[] = [];
    const totalChunks = Math.ceil(file.size / chunkSize);

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, file.size);
      const data = file.slice(start, end);

      const checksum = await calculateChecksum(data);

      chunks.push({
        index: i,
        start,
        end,
        size: end - start,
        data,
        uploaded: false,
        retries: 0,
        checksum
      });
    }

    return chunks;
  }, [calculateChecksum]);

  // Upload a single chunk
  const uploadChunk = useCallback(async (
    uploadState: FileUploadState,
    chunk: Chunk,
    onProgress: (chunkIndex: number, uploaded: boolean) => void
  ): Promise<boolean> => {
    try {
      const formData = new FormData();
      formData.append('fileId', uploadState.id);
      formData.append('chunkIndex', chunk.index.toString());
      formData.append('totalChunks', uploadState.chunks.length.toString());
      formData.append('filename', uploadState.file.name);
      formData.append('chunk', chunk.data);
      formData.append('checksum', chunk.checksum);

      const response = await fetch('/api/upload/chunk', {
        method: 'POST',
        body: formData,
        signal: uploadState.abortController.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      onProgress(chunk.index, true);

      return result.success;
    } catch (error) {
      if (error.name === 'AbortError') {
        return false; // Upload was cancelled
      }

      console.error(`Chunk ${chunk.index} upload failed:`, error);
      onProgress(chunk.index, false);
      return false;
    }
  }, []);

  // Upload file with chunking
  const uploadFile = useCallback(async (file: File) => {
    if (maxFileSize && file.size > maxFileSize) {
      onUploadError?.({
        fileId: '',
        filename: file.name,
        error: `File size exceeds maximum allowed size of ${formatBytes(maxFileSize)}`
      });
      return;
    }

    const fileId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const abortController = new AbortController();

    // Create chunks
    const chunks = await createChunks(file, chunkSize);

    const uploadState: FileUploadState = {
      id: fileId,
      file,
      progress: {
        fileId,
        filename: file.name,
        progress: 0,
        uploadedBytes: 0,
        totalBytes: file.size,
        speed: 0,
        eta: 0,
        status: 'uploading',
        currentChunk: 0,
        totalChunks: chunks.length
      },
      chunks,
      isPaused: false,
      abortController
    };

    setUploads(prev => new Map(prev).set(fileId, uploadState));
    setGlobalStats(prev => ({
      ...prev,
      totalUploads: prev.totalUploads + 1,
      activeUploads: prev.activeUploads + 1,
      totalBytes: prev.totalBytes + file.size
    }));

    // Start upload process
    startChunkedUpload(uploadState);
  }, [chunkSize, maxFileSize, createChunks, onUploadError]);

  // Start chunked upload process
  const startChunkedUpload = useCallback(async (uploadState: FileUploadState) => {
    const startTime = Date.now();
    let uploadedBytes = 0;
    let lastProgressUpdate = Date.now();

    const updateProgress = (chunkIndex: number, success: boolean) => {
      setUploads(prev => {
        const newUploads = new Map(prev);
        const state = newUploads.get(uploadState.id);
        if (!state) return prev;

        const chunk = state.chunks[chunkIndex];
        if (success) {
          chunk.uploaded = true;
          uploadedBytes += chunk.size;
          state.progress.currentChunk = chunkIndex + 1;
        } else {
          chunk.retries++;
        }

        // Calculate progress
        const progress = (uploadedBytes / state.file.size) * 100;
        const now = Date.now();
        const elapsed = (now - startTime) / 1000;
        const speed = uploadedBytes / elapsed;

        state.progress.progress = progress;
        state.progress.uploadedBytes = uploadedBytes;
        state.progress.speed = speed;
        state.progress.eta = speed > 0 ? (state.file.size - uploadedBytes) / speed : 0;

        // Update status
        const failedChunks = state.chunks.filter(c => !c.uploaded && c.retries >= maxRetries).length;
        if (failedChunks > 0) {
          state.progress.status = 'error';
        } else if (uploadedBytes >= state.file.size) {
          state.progress.status = 'completed';
        } else if (state.isPaused) {
          state.progress.status = 'paused';
        } else {
          state.progress.status = 'uploading';
        }

        onProgress?.(state.progress);

        // Update global stats
        setGlobalStats(prev => {
          const completed = Array.from(newUploads.values()).filter(u => u.progress.status === 'completed').length;
          const failed = Array.from(newUploads.values()).filter(u => u.progress.status === 'error').length;
          const active = Array.from(newUploads.values()).filter(u => u.progress.status === 'uploading').length;
          const totalUploaded = Array.from(newUploads.values()).reduce((sum, u) => sum + u.progress.uploadedBytes, 0);

          return {
            ...prev,
            activeUploads: active,
            completedUploads: completed,
            failedUploads: failed,
            uploadedBytes: totalUploaded
          };
        });

        newUploads.set(uploadState.id, state);
        return newUploads;
      });
    };

    // Upload chunks concurrently
    const uploadPromises: Promise<void>[] = [];
    const semaphore = new Semaphore(maxConcurrent);

    for (let i = 0; i < uploadState.chunks.length; i++) {
      const chunk = uploadState.chunks[i];

      if (chunk.uploaded) continue;

      uploadPromises.push(
        semaphore.acquire().then(async (release) => {
          try {
            if (uploadState.isPaused || uploadState.abortController.signal.aborted) {
              return;
            }

            let success = false;
            for (let retry = 0; retry <= maxRetries && !success; retry++) {
              if (uploadState.isPaused || uploadState.abortController.signal.aborted) {
                break;
              }

              success = await uploadChunk(uploadState, chunk, updateProgress);

              if (!success && retry < maxRetries) {
                // Wait before retry with exponential backoff
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, retry) * 1000));
              }
            }

            if (!success) {
              updateProgress(i, false);
            }
          } finally {
            release();
          }
        })
      );
    }

    try {
      await Promise.allSettled(uploadPromises);

      // Check final status
      const finalState = uploads.get(uploadState.id);
      if (finalState) {
        if (finalState.progress.status === 'completed') {
          // Calculate final checksum
          const fileChecksum = await calculateChecksum(uploadState.file);

          onUploadComplete?.({
            fileId: uploadState.id,
            filename: uploadState.file.name,
            size: uploadState.file.size,
            chunks: uploadState.chunks.length,
            checksum: fileChecksum,
            uploadTime: Date.now() - startTime
          });
        } else if (finalState.progress.status === 'error') {
          onUploadError?.({
            fileId: uploadState.id,
            filename: uploadState.file.name,
            error: 'Upload failed after all retries'
          });
        }
      }
    } catch (error) {
      onUploadError?.({
        fileId: uploadState.id,
        filename: uploadState.file.name,
        error: error instanceof Error ? error.message : 'Unknown upload error'
      });
    }
  }, [maxConcurrent, maxRetries, uploadChunk, calculateChecksum, onUploadComplete, onUploadError, onProgress, uploads]);

  // Pause/resume upload
  const togglePause = useCallback((fileId: string) => {
    setUploads(prev => {
      const newUploads = new Map(prev);
      const upload = newUploads.get(fileId);
      if (upload) {
        upload.isPaused = !upload.isPaused;
        upload.progress.status = upload.isPaused ? 'paused' : 'uploading';

        if (!upload.isPaused) {
          // Resume upload
          startChunkedUpload(upload);
        }
      }
      return newUploads;
    });
  }, [startChunkedUpload]);

  // Cancel upload
  const cancelUpload = useCallback((fileId: string) => {
    setUploads(prev => {
      const newUploads = new Map(prev);
      const upload = newUploads.get(fileId);
      if (upload) {
        upload.abortController.abort();
        newUploads.delete(fileId);
      }
      return newUploads;
    });
  }, []);

  // Retry failed upload
  const retryUpload = useCallback((fileId: string) => {
    setUploads(prev => {
      const newUploads = new Map(prev);
      const upload = newUploads.get(fileId);
      if (upload) {
        // Reset failed chunks
        upload.chunks.forEach(chunk => {
          if (!chunk.uploaded && chunk.retries >= maxRetries) {
            chunk.retries = 0;
          }
        });
        upload.progress.status = 'uploading';
        upload.isPaused = false;

        startChunkedUpload(upload);
      }
      return newUploads;
    });
  }, [maxRetries, startChunkedUpload]);

  // Handle file selection
  const handleFileSelect = useCallback((files: FileList | null) => {
    if (!files) return;

    Array.from(files).forEach(file => {
      uploadFile(file);
    });
  }, [uploadFile]);

  // Drag and drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    handleFileSelect(e.dataTransfer.files);
  }, [handleFileSelect]);

  return (
    <div className="chunked-upload">
      <div className="upload-header">
        <h3 className="upload-title">
          <Upload size={20} />
          XXL File Upload
        </h3>
        <div className="upload-stats">
          <span>{globalStats.activeUploads} active</span>
          <span>{globalStats.completedUploads} completed</span>
          <span>{globalStats.failedUploads} failed</span>
        </div>
      </div>

      {/* Upload Zone */}
      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <div className="upload-zone-content">
          <div className="upload-icon">📁</div>
          <h4>Drop XXL files here</h4>
          <p>Supports large files with automatic chunking and resume</p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={accept}
            onChange={(e) => handleFileSelect(e.target.files)}
            style={{ display: 'none' }}
          />
          <button
            className="select-files-btn"
            onClick={() => fileInputRef.current?.click()}
          >
            Select Files
          </button>
        </div>
      </div>

      {/* Upload Progress */}
      {uploads.size > 0 && (
        <div className="upload-progress-list">
          {Array.from(uploads.values()).map((upload) => (
            <div key={upload.id} className="upload-item">
              <div className="upload-item-header">
                <div className="upload-filename">{upload.progress.filename}</div>
                <div className="upload-size">{formatBytes(upload.progress.totalBytes)}</div>
                <div className={`upload-status status-${upload.progress.status}`}>
                  {upload.progress.status === 'uploading' && 'Uploading...'}
                  {upload.progress.status === 'paused' && 'Paused'}
                  {upload.progress.status === 'completed' && <CheckCircle size={16} />}
                  {upload.progress.status === 'error' && <AlertCircle size={16} />}
                  {upload.progress.status === 'retrying' && 'Retrying...'}
                </div>
              </div>

              <div className="upload-progress-bar">
                <div
                  className="upload-progress-fill"
                  style={{ width: `${upload.progress.progress}%` }}
                />
              </div>

              <div className="upload-details">
                <span>{upload.progress.progress.toFixed(1)}%</span>
                <span>{formatBytes(upload.progress.uploadedBytes)} / {formatBytes(upload.progress.totalBytes)}</span>
                <span>{formatSpeed(upload.progress.speed)}</span>
                <span>ETA: {formatTime(upload.progress.eta)}</span>
                <span>Chunk: {upload.progress.currentChunk}/{upload.progress.totalChunks}</span>
              </div>

              <div className="upload-controls">
                {upload.progress.status === 'uploading' && (
                  <button
                    className="control-btn pause-btn"
                    onClick={() => togglePause(upload.id)}
                    title="Pause upload"
                  >
                    <Pause size={14} />
                  </button>
                )}
                {upload.progress.status === 'paused' && (
                  <button
                    className="control-btn resume-btn"
                    onClick={() => togglePause(upload.id)}
                    title="Resume upload"
                  >
                    <Play size={14} />
                  </button>
                )}
                {upload.progress.status === 'error' && (
                  <button
                    className="control-btn retry-btn"
                    onClick={() => retryUpload(upload.id)}
                    title="Retry upload"
                  >
                    <RotateCcw size={14} />
                  </button>
                )}
                <button
                  className="control-btn cancel-btn"
                  onClick={() => cancelUpload(upload.id)}
                  title="Cancel upload"
                >
                  <X size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Utility functions
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatSpeed(bytesPerSecond: number): string {
  return formatBytes(bytesPerSecond) + '/s';
}

function formatTime(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  return `${Math.round(seconds / 3600)}h`;
}

// Semaphore for concurrency control
class Semaphore {
  private permits: number;
  private waitQueue: Array<() => void> = [];

  constructor(permits: number) {
    this.permits = permits;
  }

  async acquire(): Promise<() => void> {
    return new Promise((resolve) => {
      if (this.permits > 0) {
        this.permits--;
        resolve(() => this.release());
      } else {
        this.waitQueue.push(() => {
          this.permits--;
          resolve(() => this.release());
        });
      }
    });
  }

  private release(): void {
    this.permits++;
    if (this.waitQueue.length > 0) {
      const next = this.waitQueue.shift();
      next?.();
    }
  }
}