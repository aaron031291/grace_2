# File Explorer - Implementation Tasks

**Goal**: Build the Explorer shell with sidebar filters, artifact list, preview panel, and dynamic workspace integration

---

## 📋 Phase 1: Explorer Shell (Week 1)

### 1.1 Build Sidebar Filters
- [ ] Create `FilterSidebar` component
  - [ ] Category tree (Documents, Recordings, Code, etc.)
  - [ ] Date range picker
  - [ ] Tag multi-select
  - [ ] File type filter (PDF, MD, Audio, etc.)
  - [ ] Size filter
  - [ ] "Clear Filters" button
- [ ] Wire category tree to `grace_training/` directory structure
- [ ] Implement expand/collapse for nested categories
- [ ] Add category counts (e.g., "Documents (45)")
- [ ] Style with Tailwind CSS

**API Integration**:
```typescript
// Fetch categories with counts
GET /api/knowledge/categories
Response: {
  "documents": 45,
  "recordings": 12,
  "conversations": 34,
  "code": 28,
  ...
}
```

---

### 1.2 Build Artifact List
- [ ] Create `ArtifactList` component
  - [ ] Card layout for each artifact
  - [ ] Show metadata: filename, category, date, size, tags
  - [ ] Checkbox for multi-select
  - [ ] Sort controls (name, date, size, relevance)
  - [ ] Pagination or infinite scroll
  - [ ] Loading states
  - [ ] Empty state (no results)
- [ ] Implement artifact card design
  - [ ] File icon based on type
  - [ ] Metadata badges
  - [ ] Quick action buttons
  - [ ] Selection highlight
- [ ] Add bulk selection controls
  - [ ] Select all
  - [ ] Select none
  - [ ] Invert selection

**API Integration**:
```typescript
// Fetch artifacts with filters
GET /api/knowledge/list?category=documents&tags=sales&limit=50
Response: {
  "artifacts": [
    {
      "id": "art_123",
      "filename": "sales_playbook.md",
      "category": "documents/sales",
      "size_bytes": 156000,
      "tags": ["sales", "process"],
      "uploaded_at": "2025-11-14T10:30:00Z",
      "chunk_count": 48,
      "embedding_status": "indexed"
    },
    ...
  ],
  "total": 234,
  "page": 1
}
```

---

### 1.3 Build Preview Panel
- [ ] Create `PreviewPanel` component
  - [ ] Renders when artifact selected
  - [ ] Shows full metadata
  - [ ] Content preview (scrollable)
  - [ ] Action buttons (preview, notes, re-ingest, delete)
  - [ ] Close/minimize button
- [ ] Implement preview renderers
  - [ ] Markdown renderer (for .md files)
  - [ ] PDF viewer (for .pdf files)
  - [ ] Code viewer with syntax highlighting
  - [ ] Audio player (for voice notes)
  - [ ] Image viewer
  - [ ] Plain text viewer
- [ ] Add "View Full" button → opens in dynamic workspace
- [ ] Style preview panel with proper spacing

**API Integration**:
```typescript
// Get artifact content for preview
GET /api/knowledge/preview/{artifact_id}
Response: {
  "id": "art_123",
  "filename": "sales_playbook.md",
  "content": "# Sales Playbook\n\n...",
  "content_type": "markdown",
  "metadata": {...}
}
```

---

## 📋 Phase 2: Wire to Knowledge/Vector APIs (Week 1-2)

### 2.1 List/Search Integration
- [ ] Create `useKnowledgeArtifacts` hook
  - [ ] Fetches from `/api/knowledge/list`
  - [ ] Supports filters (category, tags, date range)
  - [ ] Caches results with React Query
  - [ ] Auto-refreshes on upload
- [ ] Create `useKnowledgeSearch` hook
  - [ ] RAG-powered semantic search
  - [ ] Calls `/api/knowledge/search`
  - [ ] Returns ranked results
  - [ ] Highlights matching chunks
- [ ] Wire search bar to search API
  - [ ] Debounce input (500ms)
  - [ ] Show loading indicator
  - [ ] Display results with relevance scores
  - [ ] Click result → preview

**Implementation**:
```typescript
// useKnowledgeArtifacts.ts
export const useKnowledgeArtifacts = (filters: Filters) => {
  return useQuery({
    queryKey: ['knowledge', 'list', filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        category: filters.category || '',
        tags: filters.tags?.join(',') || '',
        after: filters.after || '',
        before: filters.before || '',
        limit: '50'
      });
      
      const response = await fetch(`/api/knowledge/list?${params}`);
      return response.json();
    },
    refetchInterval: 30000  // Refresh every 30s
  });
};

// useKnowledgeSearch.ts
export const useKnowledgeSearch = () => {
  return useMutation({
    mutationFn: async (query: string) => {
      const response = await fetch('/api/knowledge/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          top_k: 10,
          threshold: 0.7
        })
      });
      return response.json();
    }
  });
};
```

---

### 2.2 Check for Duplicates
- [ ] Implement duplicate detection before upload
- [ ] Show warning if similar content exists
- [ ] Allow user to:
  - [ ] View existing file
  - [ ] Upload anyway (new version)
  - [ ] Cancel upload
  - [ ] Merge with existing

**Implementation**:
```typescript
const checkDuplicateBeforeUpload = async (file: File) => {
  // Search for similar filename
  const byName = await fetch(`/api/knowledge/check-exists`, {
    method: 'POST',
    body: JSON.stringify({ filename: file.name })
  });
  
  if (byName.exists) {
    return showDuplicateDialog({
      type: 'exact_match',
      existing: byName.artifact,
      newFile: file
    });
  }
  
  // Search for similar content (for text files)
  if (isTextFile(file)) {
    const content = await file.text();
    const similar = await fetch(`/api/knowledge/find-similar`, {
      method: 'POST',
      body: JSON.stringify({ text: content, threshold: 0.9 })
    });
    
    if (similar.count > 0) {
      return showDuplicateDialog({
        type: 'similar_content',
        existing: similar.artifacts[0],
        newFile: file
      });
    }
  }
  
  return true;  // No duplicates, safe to upload
};
```

---

## 📋 Phase 3: Upload/Re-ingest Controls (Week 2)

### 3.1 Single File Upload
- [ ] Create `UploadButton` component
  - [ ] Opens file picker
  - [ ] Shows upload progress
  - [ ] Auto-triggers ingestion
- [ ] Implement upload handler
  - [ ] Check for duplicates
  - [ ] Upload to server
  - [ ] Trigger auto-ingest
  - [ ] Update artifact list
- [ ] Add category selector on upload
- [ ] Add tag input on upload

**Implementation**:
```typescript
const handleSingleUpload = async (file: File, category: string, tags: string[]) => {
  // 1. Check duplicates
  const canUpload = await checkDuplicateBeforeUpload(file);
  if (!canUpload) return;
  
  // 2. Upload
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);
  formData.append('tags', JSON.stringify(tags));
  formData.append('auto_ingest', 'true');
  
  const response = await fetch('/api/knowledge/upload', {
    method: 'POST',
    body: formData
  });
  
  // 3. Show progress
  showNotification(`Uploading ${file.name}...`);
  
  // 4. Trigger ingestion
  const result = await response.json();
  
  // 5. Update UI
  if (result.success) {
    showNotification(`✅ ${file.name} ingested (${result.chunk_count} chunks)`);
    refreshArtifactList();
  }
};
```

---

### 3.2 Drag & Drop Upload
- [ ] Create `DropZone` component
  - [ ] Full panel or designated drop area
  - [ ] Visual feedback on drag-over
  - [ ] Support multiple files
  - [ ] Show upload queue
- [ ] Implement drag handlers
  - [ ] `onDragEnter` - highlight drop zone
  - [ ] `onDragOver` - prevent default
  - [ ] `onDrop` - handle files
  - [ ] `onDragLeave` - remove highlight
- [ ] Add upload queue UI
  - [ ] Show all files being uploaded
  - [ ] Progress bars per file
  - [ ] Cancel individual uploads

**Implementation**:
```typescript
const DropZone = ({ onDrop }) => {
  const [isDragging, setIsDragging] = useState(false);
  
  const handleDrop = async (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    
    // Process each file
    for (const file of files) {
      await uploadFile(file);
    }
  };
  
  return (
    <div
      className={`drop-zone ${isDragging ? 'dragging' : ''}`}
      onDragEnter={() => setIsDragging(true)}
      onDragLeave={() => setIsDragging(false)}
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      {isDragging ? (
        <p>📤 Drop files to upload</p>
      ) : (
        <p>Drag & drop files here</p>
      )}
    </div>
  );
};
```

---

### 3.3 Bulk Upload
- [ ] Create `BulkUploadModal` component
  - [ ] File picker (multi-select)
  - [ ] Category selector
  - [ ] Tag input (applies to all)
  - [ ] File list with remove buttons
  - [ ] "Upload All" button
- [ ] Implement bulk upload handler
  - [ ] Queue all files
  - [ ] Upload sequentially or parallel
  - [ ] Show overall progress
  - [ ] Handle errors gracefully
- [ ] Trigger `vector_integration.embed_all()` after all uploads

**Implementation**:
```typescript
const handleBulkUpload = async (
  files: File[], 
  category: string, 
  tags: string[]
) => {
  // Call bulk upload endpoint
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('files', file);
  });
  formData.append('category', category);
  formData.append('tags', JSON.stringify(tags));
  formData.append('auto_embed', 'true');
  
  const response = await fetch('/api/knowledge/bulk-upload', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  showNotification(
    `✅ Uploaded ${result.uploaded_count} files (${result.total_chunks} chunks)`
  );
  
  refreshArtifactList();
};
```

---

### 3.4 Text Paste & Ingest
- [ ] Create `AddTextNoteModal` component
  - [ ] Title input
  - [ ] Category selector
  - [ ] Tag input
  - [ ] Markdown editor
  - [ ] Preview toggle
  - [ ] "Save & Ingest" button
- [ ] Wire to `/api/remote-access/rag/ingest-text`
- [ ] Auto-chunk and embed on save
- [ ] Show in artifact list immediately

**Implementation**:
```typescript
const handleTextNote = async (
  title: string,
  content: string,
  category: string,
  tags: string[]
) => {
  const response = await fetch('/api/remote-access/rag/ingest-text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: content,
      category,
      tags,
      metadata: { title, source: 'user_note' }
    })
  });
  
  const result = await response.json();
  
  showNotification(`✅ Note saved and indexed (${result.chunk_count} chunks)`);
  refreshArtifactList();
};
```

---

### 3.5 Voice Recording
- [ ] Create `VoiceRecorder` component
  - [ ] Record button (start/stop)
  - [ ] Waveform visualization
  - [ ] Playback before save
  - [ ] Discard/save buttons
- [ ] Implement browser audio recording
  - [ ] Use MediaRecorder API
  - [ ] Convert to WAV/MP3
  - [ ] Show recording duration
- [ ] Upload to `/api/speech/upload-voice-note`
- [ ] Auto-transcribe and index

**Implementation**:
```typescript
const VoiceRecorder = ({ onSave }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    
    recorder.ondataavailable = (e) => {
      setAudioBlob(e.data);
    };
    
    recorder.start();
    setIsRecording(true);
  };
  
  const stopRecording = () => {
    // recorder.stop() in actual implementation
    setIsRecording(false);
  };
  
  const saveRecording = async () => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice_note.wav');
    formData.append('category', 'recordings');
    formData.append('auto_transcribe', 'true');
    
    await fetch('/api/speech/upload-voice-note', {
      method: 'POST',
      body: formData
    });
    
    onSave();
  };
  
  // UI implementation...
};
```

---

### 3.6 Re-ingest Control
- [ ] Add "Re-ingest" button to artifact actions
- [ ] Show re-ingestion progress
- [ ] Update artifact metadata after re-ingest
- [ ] Show diff if chunking changed

**Implementation**:
```typescript
const handleReIngest = async (artifactId: string) => {
  // Trigger re-ingestion
  const response = await fetch(`/api/knowledge/${artifactId}/re-ingest`, {
    method: 'POST'
  });
  
  showNotification('Re-ingesting... This may take a moment.');
  
  // Poll for completion
  const checkStatus = setInterval(async () => {
    const status = await fetch(`/api/knowledge/${artifactId}/status`);
    const data = await status.json();
    
    if (data.embedding_status === 'indexed') {
      clearInterval(checkStatus);
      showNotification(`✅ Re-ingested (${data.chunk_count} chunks)`);
      refreshArtifactList();
    }
  }, 2000);
};
```

---

## 📋 Phase 4: Dynamic Workspace Integration (Week 2)

### 4.1 Tie Selection to Workspaces
- [ ] Add "Open in Workspace" action to artifact
- [ ] Spawn appropriate workspace type based on file:
  - [ ] PDF → Document Viewer workspace
  - [ ] Code → Code Editor workspace
  - [ ] Audio → Audio Player workspace
  - [ ] Data → Data Explorer workspace
- [ ] Pass artifact ID to workspace
- [ ] Workspace fetches full content

**Implementation**:
```typescript
const openInWorkspace = (artifact: Artifact) => {
  // Determine workspace type
  const workspaceType = getWorkspaceType(artifact.file_type);
  
  // Spawn workspace
  workspaceManager.spawn({
    type: workspaceType,
    title: artifact.filename,
    config: {
      artifactId: artifact.id,
      filePath: artifact.source_path,
      category: artifact.category
    }
  });
};

const getWorkspaceType = (fileType: string) => {
  const typeMap = {
    'pdf': 'document_viewer',
    'md': 'code_editor',
    'py': 'code_editor',
    'js': 'code_editor',
    'mp3': 'audio_player',
    'wav': 'audio_player',
    'png': 'image_viewer',
    'jpg': 'image_viewer'
  };
  
  return typeMap[fileType] || 'generic_viewer';
};
```

---

### 4.2 Deeper Views via Workspace
- [ ] Create `DocumentViewerWorkspace` component
  - [ ] Full-screen PDF viewer
  - [ ] Navigate pages
  - [ ] Search within document
  - [ ] Highlight annotations
  - [ ] Export/download
- [ ] Create `CodeEditorWorkspace` component
  - [ ] Monaco editor
  - [ ] Syntax highlighting
  - [ ] Edit mode (if permitted)
  - [ ] Save changes
  - [ ] Git integration
- [ ] Create `AudioPlayerWorkspace` component
  - [ ] Audio player controls
  - [ ] Show transcript alongside
  - [ ] Jump to timestamp
  - [ ] Add timestamp notes
- [ ] Create `ImageViewerWorkspace` component
  - [ ] Zoom/pan
  - [ ] OCR results overlay
  - [ ] Annotations
  - [ ] Download

**Implementation**:
```typescript
// DocumentViewerWorkspace.tsx
export const DocumentViewerWorkspace = ({ artifactId }) => {
  const { data: artifact } = useQuery({
    queryKey: ['artifact', artifactId],
    queryFn: () => fetch(`/api/knowledge/${artifactId}`).then(r => r.json())
  });
  
  return (
    <div className="document-workspace">
      <h2>{artifact.filename}</h2>
      
      <PDFViewer 
        url={`/api/knowledge/${artifactId}/content`}
        onPageChange={handlePageChange}
      />
      
      <div className="sidebar">
        <h3>Metadata</h3>
        <MetadataDisplay data={artifact.metadata} />
        
        <h3>Actions</h3>
        <button onClick={downloadArtifact}>Download</button>
        <button onClick={addNotes}>Add Notes</button>
      </div>
    </div>
  );
};
```

---

### 4.3 Cross-Workspace Linking
- [ ] Enable links from artifact to related content
  - [ ] "View references" → shows citing artifacts
  - [ ] "View sources" → shows source documents
  - [ ] "Related files" → semantic similarity
- [ ] Click link → spawns new workspace
- [ ] Breadcrumb navigation between linked workspaces

**Implementation**:
```typescript
// In artifact preview
const RelatedFiles = ({ artifactId }) => {
  const { data: related } = useQuery({
    queryKey: ['related', artifactId],
    queryFn: () => 
      fetch(`/api/knowledge/${artifactId}/related`).then(r => r.json())
  });
  
  return (
    <div className="related-files">
      <h4>Related Files</h4>
      {related.map(file => (
        <div key={file.id} onClick={() => openInWorkspace(file)}>
          📄 {file.filename} ({file.similarity}% similar)
        </div>
      ))}
    </div>
  );
};
```

---

## 📋 Phase 5: Governance & Audit (Week 2-3)

### 5.1 Access Control
- [ ] Implement `@require_auth` decorator on all endpoints
- [ ] Check user permissions before actions
- [ ] Show permission errors gracefully
- [ ] Hide actions user can't perform

**Backend**:
```python
from backend.security.auth import require_auth, check_permission

@router.post("/api/knowledge/upload")
@require_auth
async def upload_knowledge(
    file: UploadFile,
    category: str,
    user_id: str = Depends(get_current_user)
):
    # Check permission
    if not await check_permission(user_id, 'knowledge:write'):
        raise HTTPException(403, "Permission denied")
    
    # Log action
    await log_knowledge_access(
        user_id=user_id,
        action='upload',
        resource=file.filename
    )
    
    # Process upload
    result = await process_upload(file, category)
    return result
```

---

### 5.2 Audit Logging
- [ ] Log every action to immutable log
- [ ] Show audit trail in UI
  - [ ] "View History" button per artifact
  - [ ] Shows: who accessed, when, what action
- [ ] Export audit logs
- [ ] Filter audit logs by user/action/date

**Implementation**:
```typescript
const AuditTrail = ({ artifactId }) => {
  const { data: audit } = useQuery({
    queryKey: ['audit', artifactId],
    queryFn: () => 
      fetch(`/api/knowledge/${artifactId}/audit`).then(r => r.json())
  });
  
  return (
    <div className="audit-trail">
      <h4>Audit Trail</h4>
      {audit.logs.map(log => (
        <div key={log.id} className="audit-entry">
          <span className="timestamp">{log.timestamp}</span>
          <span className="user">{log.user_id}</span>
          <span className="action">{log.action}</span>
        </div>
      ))}
    </div>
  );
};
```

---

### 5.3 Credential Vault Integration
- [ ] Request credentials through vault for remote file access
- [ ] Show consent prompt if approval needed
- [ ] Never expose credentials in UI
- [ ] Log credential usage

**Implementation**:
```typescript
const fetchRemoteFile = async (filePath: string) => {
  // Request through governance
  const response = await fetch('/api/knowledge/fetch-remote', {
    method: 'POST',
    body: JSON.stringify({
      file_path: filePath,
      user_id: 'admin'
    })
  });
  
  // If credentials needed, user gets consent prompt
  // If approved, file returned
  // If denied, error shown
  
  if (response.status === 403) {
    showError('Approval required to access remote file');
  }
  
  return response.blob();
};
```

---

## 📋 Detailed Component Breakdown

### Main File Explorer Component
```typescript
// FileExplorer.tsx (Main container)
export const FileExplorer = () => {
  return (
    <div className="file-explorer">
      <ExplorerHeader />
      <SearchBar />
      
      <div className="explorer-body">
        <FilterSidebar />      {/* Categories, filters */}
        <ArtifactList />       {/* File cards */}
        <PreviewPanel />       {/* Selected file preview */}
      </div>
      
      <DropZone />             {/* Drag & drop area */}
      <ActionBar />            {/* Upload, add text, record */}
    </div>
  );
};
```

### Sub-Components
```
components/FileExplorer/
├── FileExplorer.tsx           # Main container
├── ExplorerHeader.tsx         # Title, stats, settings
├── SearchBar.tsx              # Search input with suggestions
├── FilterSidebar.tsx          # Category tree + filters
├── ArtifactList.tsx           # List of artifacts
├── ArtifactCard.tsx           # Single artifact card
├── PreviewPanel.tsx           # Preview selected artifact
├── DropZone.tsx               # Drag & drop area
├── ActionBar.tsx              # Upload, add text, record buttons
├── UploadModal.tsx            # Single upload dialog
├── BulkUploadModal.tsx        # Bulk upload dialog
├── AddTextNoteModal.tsx       # Add text note
├── VoiceRecorder.tsx          # Voice recording
├── AuditTrail.tsx             # Audit log viewer
├── DuplicateDialog.tsx        # Duplicate warning
└── styles/
    └── file-explorer.css
```

---

## 🔗 API Endpoints Required

### Backend Routes to Create
```python
# backend/routes/knowledge_explorer_api.py

@router.get("/api/knowledge/categories")
async def get_categories():
    """Get all categories with file counts"""

@router.get("/api/knowledge/list")
async def list_artifacts(category, tags, after, before, limit):
    """List artifacts with filters"""

@router.get("/api/knowledge/{id}")
async def get_artifact_detail(id):
    """Get full artifact metadata"""

@router.get("/api/knowledge/preview/{id}")
async def preview_artifact(id):
    """Get artifact content for preview"""

@router.post("/api/knowledge/upload")
async def upload_artifact(file, category, tags, auto_ingest):
    """Upload single file with auto-ingest"""

@router.post("/api/knowledge/bulk-upload")
async def bulk_upload(files, category, tags, auto_embed):
    """Bulk upload multiple files"""

@router.post("/api/knowledge/{id}/notes")
async def add_notes(id, notes):
    """Add user notes to artifact"""

@router.post("/api/knowledge/{id}/re-ingest")
async def re_ingest(id):
    """Re-process artifact"""

@router.delete("/api/knowledge/{id}")
async def delete_artifact(id):
    """Soft delete artifact"""

@router.post("/api/knowledge/search")
async def search_knowledge(query, top_k, categories, threshold):
    """RAG-powered semantic search"""

@router.post("/api/knowledge/check-exists")
async def check_exists(filename):
    """Check if filename exists"""

@router.post("/api/knowledge/find-similar")
async def find_similar(text, threshold):
    """Find similar content"""

@router.get("/api/knowledge/{id}/related")
async def get_related(id):
    """Get related artifacts"""

@router.get("/api/knowledge/{id}/audit")
async def get_audit_trail(id):
    """Get audit log for artifact"""

@router.get("/api/knowledge/{id}/status")
async def get_status(id):
    """Get processing status"""
```

---

## ✅ Acceptance Criteria

### For Phase 1 (Explorer Shell)
- [ ] Can browse all categories in sidebar
- [ ] Can see all artifacts in main list
- [ ] Can preview selected artifact
- [ ] Filters work correctly
- [ ] UI is responsive and fast

### For Phase 2 (API Integration)
- [ ] List refreshes on filter change
- [ ] Search returns relevant results
- [ ] Duplicate detection works
- [ ] Data loads within 1 second

### For Phase 3 (Upload/Ingest)
- [ ] Drag & drop uploads and ingests file
- [ ] Bulk upload processes all files
- [ ] Text notes are searchable immediately
- [ ] Voice notes are transcribed correctly
- [ ] Re-ingest updates embeddings

### For Phase 4 (Workspaces)
- [ ] Clicking artifact opens workspace
- [ ] Workspace type matches file type
- [ ] Can edit files in Code Editor workspace
- [ ] Can navigate related files
- [ ] Closing workspace doesn't affect explorer

### For Phase 5 (Governance)
- [ ] Access control enforced
- [ ] Every action logged
- [ ] Audit trail visible
- [ ] Credential vault integrated
- [ ] No secrets exposed

---

## 🚀 Quick Start Guide

### 1. Create Backend API
```bash
# Create file
touch backend/routes/knowledge_explorer_api.py

# Implement endpoints (see above)
# Add to main.py:
from backend.routes.knowledge_explorer_api import router as knowledge_router
app.include_router(knowledge_router)
```

### 2. Create Frontend Component
```bash
cd frontend/console
mkdir -p src/components/FileExplorer
touch src/components/FileExplorer/FileExplorer.tsx
# Implement components (see above)
```

### 3. Wire Together
```typescript
// In App.tsx or ConsoleLayout.tsx
import { FileExplorer } from './components/FileExplorer';

// Add to dynamic workspaces
const workspaceTypes = {
  'file_explorer': FileExplorer,
  'document_viewer': DocumentViewerWorkspace,
  'code_editor': CodeEditorWorkspace,
  // ...
};
```

### 4. Test
```bash
# Start backend
python serve.py

# Start frontend
cd frontend/console
npm start

# Open browser: http://localhost:3000
# Click "Knowledge Explorer" or Cmd+K → "knowledge"
# Upload test file
# Verify ingestion
# Search for file
# Open in workspace
```

---

## 📊 Progress Tracking

**Update checklist as tasks complete**

**Current Status**:
- [ ] Backend API: Not started
- [ ] Frontend UI: Not started
- [ ] API Integration: Not started
- [ ] Workspace Integration: Not started
- [ ] Governance: Not started

**Track in**: `docs/ui/FILE_EXPLORER_PROGRESS.md`

---

**Next Step**: Start with backend API endpoints, then build frontend shell. 🚀
