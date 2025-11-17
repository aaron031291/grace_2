import { useState, useEffect, useCallback } from 'react';
import {
  listArtifacts,
  getArtifactDetails,
  uploadFile,
  ingestText,
  reingestArtifact,
  deleteArtifact,
  downloadArtifact,
  getDomains,
  type Artifact,
  type ArtifactDetail,
  type ArtifactFilters,
  type UploadProgress,
} from '../services/memoryApi';
import './MemoryExplorer.enhanced.css';

const CATEGORIES = [
  { id: 'all', label: 'All Artifacts', icon: '📦' },
  { id: 'documents', label: 'Documents', icon: '📄' },
  { id: 'code', label: 'Code', icon: '💻' },
  { id: 'conversations', label: 'Conversations', icon: '💬' },
  { id: 'training', label: 'Training Data', icon: '🎓' },
  { id: 'knowledge', label: 'Knowledge Base', icon: '🧠' },
];

const SORT_OPTIONS = [
  { value: 'date_desc', label: 'Newest First' },
  { value: 'date_asc', label: 'Oldest First' },
  { value: 'name_asc', label: 'Name (A-Z)' },
  { value: 'name_desc', label: 'Name (Z-A)' },
  { value: 'size_desc', label: 'Largest First' },
  { value: 'size_asc', label: 'Smallest First' },
];

export default function MemoryExplorer() {
  // State
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<ArtifactDetail | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('date_desc');
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  // Upload state
  const [showUpload, setShowUpload] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);
  const [dragActive, setDragActive] = useState(false);

  /**
   * Fetch artifacts
   */
  const fetchArtifacts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const filters: ArtifactFilters = {
        search: searchQuery || undefined,
        domain: selectedCategory !== 'all' ? selectedCategory : undefined,
        limit: 100,
      };

      let results = await listArtifacts(filters);

      // Sort
      results = sortArtifacts(results, sortBy);

      setArtifacts(results);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch artifacts'));
      console.error('Failed to fetch artifacts:', err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedCategory, sortBy]);

  useEffect(() => {
    fetchArtifacts();
  }, [fetchArtifacts]);

  /**
   * Load artifact details
   */
  const loadArtifactDetails = async (artifact: Artifact) => {
    setDetailLoading(true);
    try {
      const details = await getArtifactDetails(artifact.id);
      setSelectedArtifact(details);
    } catch (err) {
      console.error('Failed to load artifact details:', err);
      // Fallback to basic artifact data
      setSelectedArtifact(artifact as ArtifactDetail);
    } finally {
      setDetailLoading(false);
    }
  };

  /**
   * Handle artifact selection
   */
  const handleSelectArtifact = (artifact: Artifact) => {
    loadArtifactDetails(artifact);
  };

  /**
   * Handle file upload
   */
  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    setUploadProgress({ status: 'uploading', progress: 0 });

    try {
      await uploadFile(file, selectedCategory !== 'all' ? selectedCategory : undefined, setUploadProgress);
      
      setUploadProgress(null);
      setShowUpload(false);
      await fetchArtifacts();
    } catch (err) {
      console.error('Upload failed:', err);
      setUploadProgress({ status: 'failed', progress: 0, message: (err as Error).message });
    }
  };

  /**
   * Handle text ingestion
   */
  const handleTextIngest = async (text: string, title: string) => {
    setUploadProgress({ status: 'processing', progress: 50 });

    try {
      await ingestText(text, title, selectedCategory !== 'all' ? selectedCategory : undefined);
      
      setUploadProgress(null);
      setShowUpload(false);
      await fetchArtifacts();
    } catch (err) {
      console.error('Text ingestion failed:', err);
      setUploadProgress({ status: 'failed', progress: 0, message: (err as Error).message });
    }
  };

  /**
   * Handle re-ingest
   */
  const handleReingest = async () => {
    if (!selectedArtifact) return;

    try {
      await reingestArtifact(selectedArtifact.id);
      alert('Re-ingestion started');
      await fetchArtifacts();
    } catch (err) {
      alert('Re-ingestion failed: ' + (err as Error).message);
    }
  };

  /**
   * Handle delete
   */
  const handleDelete = async () => {
    if (!selectedArtifact) return;
    if (!confirm('Are you sure you want to delete this artifact?')) return;

    try {
      await deleteArtifact(selectedArtifact.id);
      setSelectedArtifact(null);
      await fetchArtifacts();
    } catch (err) {
      alert('Delete failed: ' + (err as Error).message);
    }
  };

  /**
   * Handle download
   */
  const handleDownload = async () => {
    if (!selectedArtifact) return;

    try {
      await downloadArtifact(selectedArtifact.id, selectedArtifact.title || 'artifact');
    } catch (err) {
      alert('Download failed: ' + (err as Error).message);
    }
  };

  /**
   * Drag & drop handlers
   */
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  return (
    <div className="memory-explorer-enhanced">
      {/* Sidebar */}
      <div className="memory-sidebar">
        <div className="sidebar-header">
          <h3>Categories</h3>
          <button 
            className="upload-btn-icon"
            onClick={() => setShowUpload(!showUpload)}
            title="Upload file"
          >
            +
          </button>
        </div>

        <div className="category-list">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              className={`category-item ${selectedCategory === cat.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat.id)}
            >
              <span className="category-icon">{cat.icon}</span>
              <span className="category-label">{cat.label}</span>
            </button>
          ))}
        </div>

        {showUpload && (
          <UploadPanel
            onFileUpload={handleFileUpload}
            onTextIngest={handleTextIngest}
            uploadProgress={uploadProgress}
            dragActive={dragActive}
            onDrag={handleDrag}
            onDrop={handleDrop}
          />
        )}
      </div>

      {/* Main content */}
      <div className="memory-main">
        <div className="memory-header">
          <div className="header-controls">
            <input
              type="text"
              placeholder="Search artifacts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              {SORT_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>

            <button onClick={fetchArtifacts} className="refresh-btn" disabled={loading}>
              {loading ? '⟳' : '↻'}
            </button>
          </div>

          <div className="header-stats">
            <span className="stat-item">
              <strong>{artifacts.length}</strong> artifacts
            </span>
          </div>
        </div>

        <div className="artifacts-list">
          {loading && artifacts.length === 0 ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading artifacts...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h3>Failed to load artifacts</h3>
              <p>{error.message}</p>
              <button onClick={fetchArtifacts} className="retry-btn">Retry</button>
            </div>
          ) : artifacts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📦</div>
              <h3>No artifacts found</h3>
              <p>Upload a file or ingest text to get started</p>
              <button onClick={() => setShowUpload(true)} className="upload-btn-large">
                Upload File
              </button>
            </div>
          ) : (
            artifacts.map(artifact => (
              <ArtifactCard
                key={artifact.id}
                artifact={artifact}
                isSelected={selectedArtifact?.id === artifact.id}
                onClick={() => handleSelectArtifact(artifact)}
              />
            ))
          )}
        </div>
      </div>

      {/* Detail panel */}
      {selectedArtifact && (
        <DetailPanel
          artifact={selectedArtifact}
          loading={detailLoading}
          onClose={() => setSelectedArtifact(null)}
          onReingest={handleReingest}
          onDownload={handleDownload}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}

/**
 * Artifact card component
 */
interface ArtifactCardProps {
  artifact: Artifact;
  isSelected: boolean;
  onClick: () => void;
}

function ArtifactCard({ artifact, isSelected, onClick }: ArtifactCardProps) {
  const formatSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getTypeIcon = (type: string) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('image')) return '🖼️';
    if (type.includes('code')) return '💻';
    if (type.includes('text')) return '📝';
    return '📦';
  };

  return (
    <div
      className={`artifact-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="artifact-icon">{getTypeIcon(artifact.type)}</div>
      <div className="artifact-info">
        <div className="artifact-title">{artifact.title || artifact.path}</div>
        <div className="artifact-meta">
          <span className="meta-item">{artifact.domain || 'Unknown'}</span>
          <span className="meta-item">{formatSize(artifact.size_bytes)}</span>
          <span className="meta-item">{formatDate(artifact.created_at)}</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Detail panel component
 */
interface DetailPanelProps {
  artifact: ArtifactDetail;
  loading: boolean;
  onClose: () => void;
  onReingest: () => void;
  onDownload: () => void;
  onDelete: () => void;
}

function DetailPanel({ artifact, loading, onClose, onReingest, onDownload, onDelete }: DetailPanelProps) {
  if (loading) {
    return (
      <div className="detail-panel">
        <div className="detail-loading">
          <div className="loading-spinner"></div>
          <p>Loading details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-panel">
      <div className="detail-header">
        <h3>{artifact.title || artifact.path}</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="detail-body">
        <div className="detail-section">
          <h4>Information</h4>
          <div className="info-grid">
            <div className="info-row">
              <span className="label">ID:</span>
              <span className="value mono">{artifact.id}</span>
            </div>
            <div className="info-row">
              <span className="label">Type:</span>
              <span className="value">{artifact.type}</span>
            </div>
            <div className="info-row">
              <span className="label">Domain:</span>
              <span className="value">{artifact.domain || 'N/A'}</span>
            </div>
            <div className="info-row">
              <span className="label">Source:</span>
              <span className="value">{artifact.source || 'N/A'}</span>
            </div>
            <div className="info-row">
              <span className="label">Created:</span>
              <span className="value">{new Date(artifact.created_at).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {artifact.content_snippet && (
          <div className="detail-section">
            <h4>Preview</h4>
            <div className="content-preview">
              <pre>{artifact.content_snippet}</pre>
            </div>
          </div>
        )}

        {artifact.embeddings && (
          <div className="detail-section">
            <h4>Embeddings</h4>
            <div className="info-grid">
              <div className="info-row">
                <span className="label">Model:</span>
                <span className="value">{artifact.embeddings.model}</span>
              </div>
              <div className="info-row">
                <span className="label">Dimension:</span>
                <span className="value">{artifact.embeddings.dimension}</span>
              </div>
              <div className="info-row">
                <span className="label">Indexed:</span>
                <span className="value">{new Date(artifact.embeddings.indexed_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}

        {artifact.linked_missions && artifact.linked_missions.length > 0 && (
          <div className="detail-section">
            <h4>Linked Missions ({artifact.linked_missions.length})</h4>
            <div className="linked-items">
              {artifact.linked_missions.map(missionId => (
                <div key={missionId} className="linked-item">
                  🎯 {missionId}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="detail-actions">
        <button className="action-btn primary" onClick={onDownload}>
          📥 Download
        </button>
        <button className="action-btn" onClick={onReingest}>
          ⟳ Re-ingest
        </button>
        <button className="action-btn secondary">
          🚀 Open in Workspace
        </button>
        <button className="action-btn danger" onClick={onDelete}>
          🗑️ Delete
        </button>
      </div>
    </div>
  );
}

/**
 * Upload panel component
 */
interface UploadPanelProps {
  onFileUpload: (files: FileList | null) => void;
  onTextIngest: (text: string, title: string) => void;
  uploadProgress: UploadProgress | null;
  dragActive: boolean;
  onDrag: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
}

function UploadPanel({ onFileUpload, onTextIngest, uploadProgress, dragActive, onDrag, onDrop }: UploadPanelProps) {
  const [mode, setMode] = useState<'file' | 'text'>('file');
  const [textContent, setTextContent] = useState('');
  const [textTitle, setTextTitle] = useState('');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleSubmitText = () => {
    if (!textContent.trim() || !textTitle.trim()) {
      alert('Please provide both title and content');
      return;
    }
    onTextIngest(textContent, textTitle);
    setTextContent('');
    setTextTitle('');
  };

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
      </div>

      {mode === 'file' ? (
        <div
          className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={onDrag}
          onDragLeave={onDrag}
          onDragOver={onDrag}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          {uploadProgress ? (
            <UploadProgressDisplay progress={uploadProgress} />
          ) : (
            <>
              <div className="drop-zone-icon">📤</div>
              <p>Drag & drop or click to upload</p>
              <input
                ref={fileInputRef}
                type="file"
                onChange={(e) => onFileUpload(e.target.files)}
                style={{ display: 'none' }}
              />
            </>
          )}
        </div>
      ) : (
        <div className="text-ingest-form">
          <input
            type="text"
            placeholder="Title"
            value={textTitle}
            onChange={(e) => setTextTitle(e.target.value)}
            className="text-title-input"
          />
          <textarea
            placeholder="Paste or type content..."
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            className="text-content-input"
            rows={6}
          />
          <button
            onClick={handleSubmitText}
            className="submit-text-btn"
            disabled={!textContent.trim() || !textTitle.trim() || !!uploadProgress}
          >
            {uploadProgress ? 'Processing...' : 'Ingest Text'}
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * Upload progress display
 */
function UploadProgressDisplay({ progress }: { progress: UploadProgress }) {
  const getStatusLabel = (status: UploadProgress['status']) => {
    switch (status) {
      case 'uploading': return 'Uploading...';
      case 'processing': return 'Processing...';
      case 'embedding': return 'Creating embeddings...';
      case 'indexed': return 'Indexed!';
      case 'failed': return 'Failed';
    }
  };

  return (
    <div className="upload-progress">
      <div className="progress-label">{getStatusLabel(progress.status)}</div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress.progress}%` }} />
      </div>
      {progress.message && <div className="progress-message">{progress.message}</div>}
    </div>
  );
}

/**
 * Sort artifacts
 */
function sortArtifacts(artifacts: Artifact[], sortBy: string): Artifact[] {
  const sorted = [...artifacts];

  switch (sortBy) {
    case 'date_desc':
      return sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    case 'date_asc':
      return sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    case 'name_asc':
      return sorted.sort((a, b) => (a.title || a.path).localeCompare(b.title || b.path));
    case 'name_desc':
      return sorted.sort((a, b) => (b.title || b.path).localeCompare(a.title || a.path));
    case 'size_desc':
      return sorted.sort((a, b) => (b.size_bytes || 0) - (a.size_bytes || 0));
    case 'size_asc':
      return sorted.sort((a, b) => (a.size_bytes || 0) - (b.size_bytes || 0));
    default:
      return sorted;
  }
}
