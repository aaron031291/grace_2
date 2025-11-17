/**
 * Complete Memory Explorer
 * Full implementation with governance, multi-modal upload, and workspace integration
 */

import { useState, useRef } from 'react';
import { useMemoryArtifacts, useArtifactDetails } from '../hooks/useMemoryArtifacts';
import type { 
  MemoryArtifact, 
  ArtifactCategory,
  EmbeddingStatus,
  IngestTextRequest,
  UploadFileRequest,
  UploadVoiceRequest,
} from '../types/memory.types';
import './MemoryExplorer.complete.css';

interface MemoryExplorerProps {
  onOpenWorkspace?: (artifact: MemoryArtifact) => void;
}

const CATEGORIES: Array<{ id: ArtifactCategory | 'all'; label: string; icon: string }> = [
  { id: 'all', label: 'All Artifacts', icon: '📦' },
  { id: 'knowledge', label: 'Knowledge Base', icon: '🧠' },
  { id: 'documents', label: 'Documents', icon: '📄' },
  { id: 'recordings', label: 'Recordings', icon: '🎤' },
  { id: 'retrospectives', label: 'Retrospectives', icon: '🔄' },
  { id: 'mission-outcomes', label: 'Mission Outcomes', icon: '🎯' },
  { id: 'conversations', label: 'Conversations', icon: '💬' },
  { id: 'training-data', label: 'Training Data', icon: '🎓' },
  { id: 'code-snippets', label: 'Code Snippets', icon: '💻' },
];

const EMBEDDING_STATUSES: Array<{ value: EmbeddingStatus; label: string; color: string }> = [
  { value: 'indexed', label: 'Indexed', color: '#00ff88' },
  { value: 'processing', label: 'Processing', color: '#00ccff' },
  { value: 'pending', label: 'Pending', color: '#ffaa00' },
  { value: 'failed', label: 'Failed', color: '#ff4444' },
  { value: 'stale', label: 'Stale', color: '#888' },
];

export default function MemoryExplorer({ onOpenWorkspace }: MemoryExplorerProps) {
  // Filters state
  const [selectedCategories, setSelectedCategories] = useState<ArtifactCategory[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<EmbeddingStatus[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // UI state
  const [selectedArtifactId, setSelectedArtifactId] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadMode, setUploadMode] = useState<'text' | 'file' | 'voice'>('file');
  const [dragActive, setDragActive] = useState(false);
  
  // Upload form state
  const [textTitle, setTextTitle] = useState('');
  const [textContent, setTextContent] = useState('');
  const [voiceTitle, setVoiceTitle] = useState('');
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Data hook
  const {
    artifacts,
    total,
    availableTags,
    stats,
    loading,
    error,
    isEmpty,
    uploading,
    uploadProgress,
    refresh,
    setFilters,
    searchSemantic,
    uploadTextArtifact,
    uploadFileArtifact,
    uploadVoiceArtifact,
    reingestArtifact,
    deleteArtifact,
  } = useMemoryArtifacts({
    filters: {
      category: selectedCategories.length > 0 ? selectedCategories : undefined,
      embedding_status: selectedStatuses.length > 0 ? selectedStatuses : undefined,
      search: searchQuery || undefined,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
      limit: 100,
    },
    autoRefresh: false,
    onError: (err) => {
      console.error('[Memory Explorer] Error:', err);
    },
    onUploadComplete: (artifactId) => {
      console.log('[Memory Explorer] Upload complete:', artifactId);
      setShowUpload(false);
      setTextTitle('');
      setTextContent('');
      setVoiceTitle('');
      setAudioBlob(null);
    },
  });

  // Artifact details hook
  const {
    artifact: selectedArtifact,
    loading: detailLoading,
    error: detailError,
    refresh: refreshDetails,
  } = useArtifactDetails(selectedArtifactId);

  // Category toggle
  const toggleCategory = (category: ArtifactCategory) => {
    setSelectedCategories(prev => 
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  // Status toggle
  const toggleStatus = (status: EmbeddingStatus) => {
    setSelectedStatuses(prev =>
      prev.includes(status)
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
  };

  // Tag toggle
  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  // Upload handlers
  const handleTextUpload = async () => {
    if (!textTitle.trim() || !textContent.trim()) {
      alert('Please provide both title and content');
      return;
    }

    try {
      const request: IngestTextRequest = {
        text: textContent,
        title: textTitle,
        category: selectedCategories[0] || 'knowledge',
        tags: selectedTags,
        source: 'console-text-input',
      };

      await uploadTextArtifact(request);
    } catch (err) {
      console.error('Text upload failed:', err);
    }
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];

    try {
      const request: UploadFileRequest = {
        file,
        category: selectedCategories[0] || 'documents',
        tags: selectedTags,
        metadata: {
          original_name: file.name,
          size: file.size,
          type: file.type,
        },
      };

      await uploadFileArtifact(request);
    } catch (err) {
      console.error('File upload failed:', err);
    }
  };

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      alert('Microphone access denied');
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleVoiceUpload = async () => {
    if (!audioBlob || !voiceTitle.trim()) {
      alert('Please record audio and provide a title');
      return;
    }

    try {
      const request: UploadVoiceRequest = {
        audio: audioBlob,
        title: voiceTitle,
        category: selectedCategories[0] || 'recordings',
        transcribe: true,
        tags: selectedTags,
      };

      await uploadVoiceArtifact(request);
    } catch (err) {
      console.error('Voice upload failed:', err);
    }
  };

  // Actions
  const handleReingest = async () => {
    if (!selectedArtifact) return;

    if (!confirm(`Re-ingest "${selectedArtifact.name}"? This will rebuild embeddings.`)) {
      return;
    }

    try {
      await reingestArtifact(selectedArtifact.id);
      await refreshDetails();
      alert('Re-ingestion started');
    } catch (err) {
      alert('Re-ingestion failed: ' + (err as Error).message);
    }
  };

  const handleDelete = async () => {
    if (!selectedArtifact) return;

    const reason = prompt('Reason for deletion (for audit log):');
    if (reason === null) return;

    try {
      await deleteArtifact(selectedArtifact.id, reason);
      setSelectedArtifactId(null);
      alert('Artifact deleted');
    } catch (err) {
      alert('Deletion failed: ' + (err as Error).message);
    }
  };

  const handleOpenInWorkspace = () => {
    if (!selectedArtifact) return;
    
    if (onOpenWorkspace) {
      onOpenWorkspace(selectedArtifact);
    } else {
      console.log('Open in workspace:', selectedArtifact);
    }
  };

  // Drag & drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
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
    <div className="memory-explorer-complete">
      {/* Sidebar */}
      <div className="memory-sidebar">
        <div className="sidebar-section">
          <div className="section-header">
            <h3>Categories</h3>
            {selectedCategories.length > 0 && (
              <button
                className="clear-filter-btn"
                onClick={() => setSelectedCategories([])}
                title="Clear category filter"
              >
                Clear
              </button>
            )}
          </div>
          <div className="category-list">
            {CATEGORIES.map(cat => {
              const isSelected = cat.id === 'all' 
                ? selectedCategories.length === 0
                : selectedCategories.includes(cat.id as ArtifactCategory);
              
              const count = cat.id === 'all'
                ? total
                : stats?.by_category?.[cat.id] || 0;

              return (
                <button
                  key={cat.id}
                  className={`category-item ${isSelected ? 'active' : ''}`}
                  onClick={() => {
                    if (cat.id === 'all') {
                      setSelectedCategories([]);
                    } else {
                      toggleCategory(cat.id as ArtifactCategory);
                    }
                  }}
                >
                  <span className="category-icon">{cat.icon}</span>
                  <span className="category-label">{cat.label}</span>
                  <span className="category-count">{count}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="sidebar-section">
          <div className="section-header">
            <h3>Embedding Status</h3>
          </div>
          <div className="filter-chips">
            {EMBEDDING_STATUSES.map(status => (
              <button
                key={status.value}
                className={`filter-chip ${selectedStatuses.includes(status.value) ? 'active' : ''}`}
                onClick={() => toggleStatus(status.value)}
                style={{ borderColor: status.color }}
              >
                <span className="chip-dot" style={{ background: status.color }}></span>
                {status.label}
              </button>
            ))}
          </div>
        </div>

        {availableTags.length > 0 && (
          <div className="sidebar-section">
            <div className="section-header">
              <h3>Tags</h3>
            </div>
            <div className="tag-list">
              {availableTags.slice(0, 10).map(tag => (
                <button
                  key={tag}
                  className={`tag-chip ${selectedTags.includes(tag) ? 'active' : ''}`}
                  onClick={() => toggleTag(tag)}
                >
                  #{tag}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="sidebar-section">
          <button
            className="upload-btn-large"
            onClick={() => setShowUpload(!showUpload)}
          >
            {showUpload ? '✕ Close Upload' : '+ Add Knowledge'}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="memory-main">
        {/* Header */}
        <div className="memory-header">
          <div className="header-row">
            <input
              type="text"
              placeholder="Search artifacts by name or content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && searchQuery.trim()) {
                  searchSemantic(searchQuery);
                }
              }}
            />
            
            <button
              className="semantic-search-btn"
              onClick={() => searchQuery.trim() && searchSemantic(searchQuery)}
              disabled={!searchQuery.trim()}
              title="Semantic search"
            >
              🔍
            </button>
          </div>

          <div className="header-row">
            <div className="filter-summary">
              {selectedCategories.length > 0 && (
                <span className="filter-badge">
                  {selectedCategories.length} category filter{selectedCategories.length > 1 ? 's' : ''}
                </span>
              )}
              {selectedStatuses.length > 0 && (
                <span className="filter-badge">
                  {selectedStatuses.length} status filter{selectedStatuses.length > 1 ? 's' : ''}
                </span>
              )}
              {selectedTags.length > 0 && (
                <span className="filter-badge">
                  {selectedTags.length} tag{selectedTags.length > 1 ? 's' : ''}
                </span>
              )}
            </div>

            <select
              value={`${sortBy}_${sortOrder}`}
              onChange={(e) => {
                const [by, order] = e.target.value.split('_');
                setSortBy(by as any);
                setSortOrder(order as any);
              }}
              className="sort-select"
            >
              <option value="date_desc">Newest First</option>
              <option value="date_asc">Oldest First</option>
              <option value="name_asc">Name (A-Z)</option>
              <option value="name_desc">Name (Z-A)</option>
              <option value="size_desc">Largest First</option>
              <option value="size_asc">Smallest First</option>
            </select>

            <button onClick={() => refresh()} className="refresh-btn" disabled={loading}>
              {loading ? '⟳' : '↻'}
            </button>
          </div>

          {stats && (
            <div className="stats-row">
              <span className="stat">{stats.total_artifacts || total} artifacts</span>
              <span className="stat">{formatBytes(stats.total_size_bytes || 0)}</span>
              <span className="stat">{stats.total_chunks || 0} chunks</span>
            </div>
          )}
        </div>

        {/* Upload Panel */}
        {showUpload && (
          <UploadPanel
            mode={uploadMode}
            setMode={setUploadMode}
            textTitle={textTitle}
            setTextTitle={setTextTitle}
            textContent={textContent}
            setTextContent={setTextContent}
            voiceTitle={voiceTitle}
            setVoiceTitle={setVoiceTitle}
            recording={recording}
            audioBlob={audioBlob}
            onStartRecording={startVoiceRecording}
            onStopRecording={stopVoiceRecording}
            onFileSelect={handleFileUpload}
            onTextSubmit={handleTextUpload}
            onVoiceSubmit={handleVoiceUpload}
            uploadProgress={uploadProgress}
            dragActive={dragActive}
            onDrag={handleDrag}
            onDrop={handleDrop}
            fileInputRef={fileInputRef}
            uploading={uploading}
          />
        )}

        {/* Artifact List */}
        <div className="artifacts-container">
          {loading && artifacts.length === 0 ? (
            <LoadingState />
          ) : error ? (
            <ErrorState error={error} onRetry={refresh} />
          ) : isEmpty ? (
            <EmptyState onUpload={() => setShowUpload(true)} />
          ) : (
            <div className="artifacts-grid">
              {artifacts.map(artifact => (
                <ArtifactCard
                  key={artifact.id}
                  artifact={artifact}
                  isSelected={selectedArtifactId === artifact.id}
                  onClick={() => setSelectedArtifactId(artifact.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Detail Panel */}
      {selectedArtifact && (
        <DetailPanel
          artifact={selectedArtifact}
          loading={detailLoading}
          error={detailError}
          onClose={() => setSelectedArtifactId(null)}
          onReingest={handleReingest}
          onDelete={handleDelete}
          onOpenWorkspace={handleOpenInWorkspace}
          onRefresh={refreshDetails}
        />
      )}
    </div>
  );
}

// ========== Sub-components ==========

function ArtifactCard({ artifact, isSelected, onClick }: any) {
  const getStatusColor = (status: EmbeddingStatus) => {
    const statusMap: Record<EmbeddingStatus, string> = {
      indexed: '#00ff88',
      processing: '#00ccff',
      pending: '#ffaa00',
      queued: '#ffaa00',
      failed: '#ff4444',
      stale: '#888',
    };
    return statusMap[status] || '#888';
  };

  return (
    <div className={`artifact-card ${isSelected ? 'selected' : ''}`} onClick={onClick}>
      <div className="card-header">
        <span className="artifact-type-icon">{getTypeIcon(artifact.type)}</span>
        <span 
          className="embedding-status-dot" 
          style={{ background: getStatusColor(artifact.embedding_status) }}
          title={artifact.embedding_status}
        ></span>
      </div>
      
      <div className="card-body">
        <div className="artifact-name">{artifact.name}</div>
        <div className="artifact-category">{artifact.category}</div>
        
        {artifact.tags && artifact.tags.length > 0 && (
          <div className="artifact-tags">
            {artifact.tags.slice(0, 3).map(tag => (
              <span key={tag} className="mini-tag">#{tag}</span>
            ))}
          </div>
        )}
        
        <div className="artifact-meta">
          <span>{formatDate(artifact.updated_at)}</span>
          {artifact.size_bytes && <span>{formatBytes(artifact.size_bytes)}</span>}
          {artifact.chunk_count && <span>{artifact.chunk_count} chunks</span>}
        </div>
      </div>
    </div>
  );
}

function DetailPanel({ artifact, loading, error, onClose, onReingest, onDelete, onOpenWorkspace, onRefresh }: any) {
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

  if (error) {
    return (
      <div className="detail-panel">
        <div className="detail-error">
          <p>Failed to load details</p>
          <button onClick={onRefresh}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-panel">
      <div className="detail-header">
        <h3>{artifact.name}</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="detail-scroll">
        {/* Info */}
        <DetailSection title="Information">
          <InfoRow label="ID" value={artifact.id} mono />
          <InfoRow label="Category" value={artifact.category} />
          <InfoRow label="Type" value={artifact.type} />
          <InfoRow label="Status" value={artifact.embedding_status} badge />
          <InfoRow label="Created" value={new Date(artifact.created_at).toLocaleString()} />
          <InfoRow label="Source" value={artifact.source || 'N/A'} />
        </DetailSection>

        {/* Preview */}
        {artifact.content_snippet && (
          <DetailSection title="Content Preview">
            <div className="content-preview">
              <pre>{artifact.content_snippet}</pre>
            </div>
          </DetailSection>
        )}

        {/* Embeddings */}
        {artifact.embeddings && (
          <DetailSection title="Embeddings">
            <InfoRow label="Model" value={artifact.embeddings.model} />
            <InfoRow label="Dimension" value={artifact.embeddings.dimension.toString()} />
            <InfoRow label="Chunks" value={artifact.embeddings.chunk_count.toString()} />
            <InfoRow label="Indexed" value={new Date(artifact.embeddings.indexed_at).toLocaleString()} />
          </DetailSection>
        )}

        {/* Linked Missions */}
        {artifact.linked_missions_detail && artifact.linked_missions_detail.length > 0 && (
          <DetailSection title={`Linked Missions (${artifact.linked_missions_detail.length})`}>
            {artifact.linked_missions_detail.map((mission: any) => (
              <div key={mission.mission_id} className="linked-mission">
                🎯 {mission.mission_id}
                <span className="mission-status">{mission.status}</span>
              </div>
            ))}
          </DetailSection>
        )}

        {/* Tags */}
        {artifact.tags && artifact.tags.length > 0 && (
          <DetailSection title="Tags">
            <div className="tag-pills">
              {artifact.tags.map((tag: string) => (
                <span key={tag} className="tag-pill">#{tag}</span>
              ))}
            </div>
          </DetailSection>
        )}

        {/* Governance */}
        {artifact.governance && (
          <DetailSection title="Governance">
            <InfoRow label="Access Level" value={artifact.governance.access_level} />
            {artifact.governance.approved_by && (
              <>
                <InfoRow label="Approved By" value={artifact.governance.approved_by} />
                <InfoRow label="Approved At" value={new Date(artifact.governance.approved_at!).toLocaleString()} />
              </>
            )}
          </DetailSection>
        )}
      </div>

      {/* Actions */}
      <div className="detail-actions">
        <button className="action-btn primary" onClick={onOpenWorkspace}>
          🚀 Open in Workspace
        </button>
        <button className="action-btn" onClick={onReingest}>
          ⟳ Re-ingest
        </button>
        <button className="action-btn">
          📥 Download
        </button>
        <button className="action-btn danger" onClick={onDelete}>
          🗑️ Delete
        </button>
      </div>
    </div>
  );
}

// Continued in next file...
