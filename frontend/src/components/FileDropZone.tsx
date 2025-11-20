/**
 * File Drop Zone - Drag & Drop Upload Component
 * 
 * Supports:
 * - Drag and drop files
 * - Multiple file upload
 * - Automatic modality detection
 * - Learning folder auto-ingestion
 * - Progress tracking
 */

import React, { useState, useCallback } from 'react';
import { IngestionAPI } from '../api/ingestion';
import './FileDropZone.css';

interface FileDropZoneProps {
  folder?: string;
  autoIngest?: boolean;
  onUploadComplete?: (results: UploadResult[]) => void;
}

interface UploadResult {
  filename: string;
  status: 'success' | 'error';
  document_id?: string;
  modality?: string;
  error?: string;
}

interface UploadProgress {
  filename: string;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  message: string;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({
  folder = 'upload',
  autoIngest = false,
  onUploadComplete
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploads, setUploads] = useState<Map<string, UploadProgress>>(new Map());
  const [results, setResults] = useState<UploadResult[]>([]);

  const isLearningFolder = folder.startsWith('learning');

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

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    await uploadFiles(files);
  }, [folder, autoIngest]);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      await uploadFiles(files);
    }
  }, [folder, autoIngest]);

  const uploadFiles = async (files: File[]) => {
    const uploadResults: UploadResult[] = [];

    for (const file of files) {
      // Initialize progress
      setUploads(prev => new Map(prev).set(file.name, {
        filename: file.name,
        status: 'uploading',
        progress: 0,
        message: 'Uploading...'
      }));

      try {
        // Upload with ingestion if in learning folder or auto-ingest enabled
        const shouldIngest = isLearningFolder || autoIngest;

        const result = await IngestionAPI.uploadFile(file, {
          title: file.name,
          description: shouldIngest 
            ? `Auto-ingested from ${folder}` 
            : `Uploaded to ${folder}`,
          folder: folder  // Pass folder to backend
        });

        // Update progress
        setUploads(prev => new Map(prev).set(file.name, {
          filename: file.name,
          status: 'processing',
          progress: 50,
          message: shouldIngest ? 'Processing and ingesting...' : 'Upload complete'
        }));

        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 500));

        // Complete
        setUploads(prev => new Map(prev).set(file.name, {
          filename: file.name,
          status: 'complete',
          progress: 100,
          message: 'Complete!'
        }));

        uploadResults.push({
          filename: file.name,
          status: 'success',
          document_id: result.document_id,
          modality: result.modality
        });

      } catch (error) {
        setUploads(prev => new Map(prev).set(file.name, {
          filename: file.name,
          status: 'error',
          progress: 0,
          message: error instanceof Error ? error.message : 'Upload failed'
        }));

        uploadResults.push({
          filename: file.name,
          status: 'error',
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    setResults(uploadResults);
    
    if (onUploadComplete) {
      onUploadComplete(uploadResults);
    }

    // Clear progress after 3 seconds
    setTimeout(() => {
      setUploads(new Map());
    }, 3000);
  };

  return (
    <div className="file-drop-zone-container">
      <div
        className={`file-drop-zone ${isDragging ? 'dragging' : ''} ${isLearningFolder ? 'learning' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <div className="drop-zone-content">
          <div className="drop-zone-icon">
            {isLearningFolder ? '🧠' : '📥'}
          </div>
          <h3 className="drop-zone-title">
            {isLearningFolder ? 'Learning Memory Upload' : 'File Upload'}
          </h3>
          <p className="drop-zone-description">
            {isLearningFolder 
              ? 'Drop files here to auto-ingest into training corpus'
              : 'Drop files here or click to browse'}
          </p>
          {isLearningFolder && (
            <div className="drop-zone-badge">
              ✨ Auto ML/DL Processing Enabled
            </div>
          )}
          <input
            type="file"
            id="file-input"
            multiple
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input" className="file-select-btn">
            Choose Files
          </label>
        </div>
      </div>

      {/* Upload Progress */}
      {uploads.size > 0 && (
        <div className="upload-progress-container">
          <h4>Upload Progress</h4>
          {Array.from(uploads.values()).map((upload) => (
            <div key={upload.filename} className="upload-progress-item">
              <div className="upload-progress-header">
                <span className="upload-filename">{upload.filename}</span>
                <span className={`upload-status status-${upload.status}`}>
                  {upload.status === 'uploading' && '⏳'}
                  {upload.status === 'processing' && '⚙️'}
                  {upload.status === 'complete' && '✅'}
                  {upload.status === 'error' && '❌'}
                </span>
              </div>
              <div className="upload-progress-bar">
                <div 
                  className="upload-progress-fill" 
                  style={{ width: `${upload.progress}%` }}
                />
              </div>
              <div className="upload-message">{upload.message}</div>
            </div>
          ))}
        </div>
      )}

      {/* Results Summary */}
      {results.length > 0 && uploads.size === 0 && (
        <div className="upload-results">
          <h4>Upload Summary</h4>
          <div className="results-stats">
            <span className="result-success">
              ✅ {results.filter(r => r.status === 'success').length} succeeded
            </span>
            {results.filter(r => r.status === 'error').length > 0 && (
              <span className="result-error">
                ❌ {results.filter(r => r.status === 'error').length} failed
              </span>
            )}
          </div>
          <button 
            className="clear-results-btn"
            onClick={() => setResults([])}
          >
            Clear
          </button>
        </div>
      )}
    </div>
  );
};
