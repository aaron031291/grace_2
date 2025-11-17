# Complete Memory Explorer - Implementation Guide

Production-grade Memory Explorer meeting all Grace criteria with governance, multi-modal upload, and full integration.

## Architecture Overview

```
┌─────── Sidebar (280px) ────────┬────────── Main Content ─────────┬─── Detail Panel (380px) ───┐
│                                 │                                  │                            │
│ Categories (with counts)        │ Search & Filters                 │ Artifact Info              │
│ ├─ 📦 All Artifacts (150)      │ ┌────────────────────────────┐  │ ├─ ID, Type, Status       │
│ ├─ 🧠 Knowledge (45)           │ │ Search: [____________] 🔍 │  │ ├─ Created, Source        │
│ ├─ 📄 Documents (32)           │ └────────────────────────────┘  │ └─ Size, Chunks           │
│ ├─ 🎤 Recordings (12)          │                                  │                            │
│ ├─ 🔄 Retrospectives (8)       │ Sort: [Newest First ▼]  [↻]    │ Content Preview            │
│ ├─ 🎯 Mission Outcomes (18)    │ ───────────────────────────────  │ ┌────────────────────────┐ │
│ └─ ... more                     │                                  │ │ First 500 chars of     │ │
│                                 │ 📦 150 artifacts | 45.2 MB       │ │ artifact content...    │ │
│ Embedding Status                │ ───────────────────────────────  │ └────────────────────────┘ │
│ ├─ ● Indexed (120)             │                                  │                            │
│ ├─ ● Processing (5)            │ [Artifact Card 1]                │ Embeddings                 │
│ └─ ● Pending (10)              │ [Artifact Card 2]                │ ├─ Model: text-embedding  │
│                                 │ [Artifact Card 3]                │ ├─ Dimension: 1536       │
│ Tags                            │ [Artifact Card 4]                │ └─ Chunks: 12            │
│ #sales #crm #training           │                                  │                            │
│                                 │                                  │ Linked Missions (2)        │
│ [+ Add Knowledge]               │                                  │ ├─ 🎯 mission_123        │
│ ┌─────────────────────────┐    │                                  │ └─ 🎯 mission_456        │
│ │ 📁 File | 📝 Text | 🎤   │    │                                  │                            │
│ ├─────────────────────────┤    │                                  │ Governance                 │
│ │ [Drag & Drop Zone]       │    │                                  │ ├─ Access: internal      │
│ └─────────────────────────┘    │                                  │ └─ Approved by: aaron    │
│                                 │                                  │                            │
└─────────────────────────────────┴──────────────────────────────────┤ Actions                    │
                                                                      │ [🚀 Open in Workspace]    │
                                                                      │ [⟳ Re-ingest]             │
                                                                      │ [📥 Download]             │
                                                                      │ [🗑️ Delete]               │
                                                                      └────────────────────────────┘
```

## 1. Data Contracts (Types)

### Core Types

**File:** `types/memory.types.ts`

```typescript
// Artifact summary (list view)
interface MemoryArtifact {
  id: string;
  name: string;
  type: ArtifactType;
  category: ArtifactCategory;
  tags: string[];
  updated_at: string;
  created_at: string;
  embedding_status: EmbeddingStatus;
  linked_missions?: string[];
  linked_kpis?: string[];
  size_bytes?: number;
  chunk_count?: number;
  source?: string;
}

// Full artifact details (detail view)
interface MemoryArtifactDetail extends MemoryArtifact {
  content_snippet: string;
  full_content?: string;
  embeddings: {
    model: string;
    dimension: number;
    indexed_at: string;
    chunk_count: number;
    status: EmbeddingStatus;
  };
  linked_missions_detail?: Array<{
    mission_id: string;
    subsystem: string;
    status: string;
    relevance_score?: number;
  }>;
  governance?: {
    approved_by?: string;
    approved_at?: string;
    access_level: 'public' | 'internal' | 'restricted';
  };
  ingestion_history?: Array<{
    timestamp: string;
    action: 'created' | 'updated' | 're-indexed' | 'deleted';
    user: string;
    result: 'success' | 'failed';
  }>;
}

// Filters
interface MemoryArtifactFilters {
  category?: ArtifactCategory[];
  type?: ArtifactType[];
  tags?: string[];
  search?: string;
  embedding_status?: EmbeddingStatus[];
  date_from?: string;
  date_to?: string;
  linked_to_mission?: string;
  linked_to_kpi?: string;
  limit?: number;
  sort_by?: 'name' | 'date' | 'size' | 'relevance';
  sort_order?: 'asc' | 'desc';
}
```

### Enums

```typescript
type EmbeddingStatus = 'pending' | 'queued' | 'processing' | 'indexed' | 'failed' | 'stale';

type ArtifactCategory = 
  | 'knowledge'
  | 'documents'
  | 'recordings'
  | 'retrospectives'
  | 'mission-outcomes'
  | 'conversations'
  | 'training-data'
  | 'code-snippets'
  | 'external-sources';

type ArtifactType = 
  | 'pdf' | 'text' | 'audio' | 'image' | 'code' 
  | 'json' | 'markdown' | 'web-page' | 'chat-log';
```

## 2. API Endpoints

**File:** `services/memoryApi.complete.ts`

### READ Operations

```typescript
// List artifacts with filters
GET /api/ingest/artifacts?category=documents&search=sales&embedding_status=indexed
Response: MemoryArtifactsResponse {
  artifacts: MemoryArtifact[],
  total: number,
  limit: number,
  offset: number,
  filters_applied: MemoryArtifactFilters
}

// Get artifact details
GET /api/ingest/artifacts/{id}
Response: MemoryArtifactDetail (full object with snippet, embeddings, links)

// Semantic search
POST /api/vectors/search
Body: { query: string, top_k: number, filters: {...} }
Response: SemanticSearchResult[]

// Get available tags
GET /api/memory/tags
Response: { tags: string[] }

// Get statistics
GET /api/ingest/stats
Response: {
  total_artifacts: number,
  by_category: Record<string, number>,
  by_status: Record<string, number>,
  total_size_bytes: number,
  total_chunks: number
}
```

### CREATE Operations

```typescript
// Upload file
POST /api/ingest/upload
Body: FormData {
  file: File,
  domain: string,
  tags: string[] (JSON),
  metadata: object (JSON)
}
Response: { artifact_id: string, status: string }

// Ingest text
POST /api/remote-access/rag/ingest-text
Body: {
  text: string,
  title: string,
  domain: string,
  tags: string[],
  source: string,
  metadata: object
}
Response: { artifact_id: string, chunks: number }

// Upload voice
POST /api/voice/upload
Body: FormData {
  audio: Blob,
  title: string,
  category: string,
  transcribe: boolean,
  tags: string[] (JSON)
}
Response: { artifact_id: string, transcription?: string }
```

### UPDATE Operations

```typescript
// Re-ingest artifact
POST /api/ingest/artifacts/{id}/reingest
Body: { force?: boolean, embeddings_only?: boolean }
Response: { status: string, message: string }

// Update metadata
PATCH /api/ingest/artifacts/{id}
Body: { name?: string, category?: string, tags?: string[], metadata?: object }
Response: MemoryArtifact (updated)

// Link to mission
POST /api/memory/artifacts/{id}/link-mission
Body: { mission_id: string }
Response: { status: string }
```

### DELETE Operations

```typescript
// Delete artifact (with governance)
DELETE /api/ingest/artifacts/{id}
Body: { reason: string, soft_delete?: boolean }
Response: { status: string, audit_log_id?: string }

// Batch operations
POST /api/memory/artifacts/batch
Body: {
  artifact_ids: string[],
  operation: 'delete' | 'reingest' | 'tag' | 'categorize',
  params?: object
}
Response: { success_count: number, failed_count: number, results: [...] }
```

### GOVERNANCE Operations

```typescript
// Get audit log
GET /api/memory/artifacts/{id}/audit-log
Response: { logs: Array<{timestamp, action, user, result, details}> }

// Request approval (for destructive ops)
POST /api/governance/request-approval
Body: { operation: string, resource_type: string, resource_id: string, reason: string }
Response: { approval_id: string, status: 'pending' | 'auto_approved' }
```

## 3. React Hook (`useMemoryArtifacts`)

### Usage

```typescript
import { useMemoryArtifacts } from '../hooks/useMemoryArtifacts';

function MemoryExplorer() {
  const {
    // Data
    artifacts,
    total,
    availableTags,
    stats,
    
    // State
    loading,
    error,
    isEmpty,
    uploading,
    uploadProgress,
    
    // Actions - List
    refresh,
    setFilters,
    searchSemantic,
    
    // Actions - Upload
    uploadTextArtifact,
    uploadFileArtifact,
    uploadVoiceArtifact,
    
    // Actions - Management
    reingestArtifact,
    deleteArtifact,
    batchDelete,
    batchReingest,
    
    // Config
    setAutoRefresh,
  } = useMemoryArtifacts({
    filters: {
      category: ['knowledge', 'documents'],
      embedding_status: ['indexed'],
      tags: ['sales'],
      search: 'CRM',
      sort_by: 'date',
      sort_order: 'desc',
      limit: 100,
    },
    autoRefresh: false,
    refreshInterval: 60000,
    onError: (error) => {
      console.error('Memory error:', error);
    },
    onUploadComplete: (artifactId) => {
      console.log('Upload complete:', artifactId);
    },
  });
}
```

### Upload Actions

```typescript
// Upload text
const artifactId = await uploadTextArtifact({
  text: 'Content here...',
  title: 'My Note',
  category: 'knowledge',
  tags: ['sales', 'crm'],
  source: 'console-input',
});

// Upload file with progress
const artifactId = await uploadFileArtifact({
  file: selectedFile,
  category: 'documents',
  tags: ['training'],
  metadata: { original_name: file.name },
});

// Upload voice with transcription
const result = await uploadVoiceArtifact({
  audio: audioBlob,
  title: 'Meeting Notes',
  category: 'recordings',
  transcribe: true,
  tags: ['meeting'],
});
```

## 4. Complete UI Shell

### Sidebar (Left Panel)

**Categories Section:**
- All categories with icons and counts
- Multi-select (click to toggle)
- Active state highlighting
- Clear filter button

**Embedding Status Section:**
- Filter chips for each status
- Color-coded dots (indexed=green, processing=cyan, etc.)
- Multi-select

**Tags Section:**
- Top 10 most common tags
- Click to toggle filter
- Shows count of artifacts per tag

**Upload Section:**
- Large "Add Knowledge" button
- Toggles upload panel

### Main Content (Center Panel)

**Header:**
- Search input (with Enter key support)
- Semantic search button (🔍)
- Sort dropdown (6 options)
- Refresh button
- Filter summary badges
- Statistics row (count, size, chunks)

**Upload Panel (when active):**
- Tab selector: 📁 File | 📝 Text | 🎤 Voice
- Mode-specific UI
- Progress tracker

**Artifact List:**
- Grid layout (auto-fill, min 280px)
- Cards with icon, status dot, name, category, tags
- Hover effects
- Selected state (green border)
- Loading/error/empty states

### Detail Panel (Right Panel)

**Header:**
- Artifact name
- Close button (×)

**Scrollable Body:**
- **Information:** ID, category, type, status, created, source
- **Content Preview:** First 500 chars in code block
- **Embeddings:** Model, dimension, chunks, indexed time
- **Linked Missions:** Mission cards with status
- **Tags:** Tag pills
- **Governance:** Access level, approval info
- **Ingestion History:** Timeline of operations

**Actions Footer:**
- 🚀 Open in Workspace (primary)
- ⟳ Re-ingest
- 📥 Download
- 🗑️ Delete (danger)

## 5. Upload Modes

### Mode 1: File Upload

**UI:**
- Drag & drop zone
- Click to browse
- Visual feedback on drag
- Supported formats displayed

**Process:**
```
1. User drops file
2. Status: "Uploading..." (0%)
3. Status: "Parsing document..." (30%)
4. Status: "Creating chunks..." (50%)
5. Status: "Generating embeddings..." (75%)
6. Status: "Indexing vectors..." (95%)
7. Status: "Complete!" (100%)
8. List refreshes, new artifact appears
```

**Governance:**
- User ID included in headers (`X-User-ID`)
- Operation logged with timestamp
- File metadata preserved

### Mode 2: Text Ingestion

**UI:**
- Title input field
- Multi-line textarea (8 rows)
- Submit button (disabled when empty)

**Process:**
```
1. User pastes text
2. Enters title
3. Clicks "Ingest Text"
4. API: POST /api/remote-access/rag/ingest-text
5. Progress: "Parsing..." → "Chunking..." → "Embedding..."
6. Success, list refreshes
```

**Governance:**
- Source: "console-text-input"
- Category from selected filter
- Tags included if any selected

### Mode 3: Voice Recording

**UI:**
- Title input
- "Start Recording" button
- Recording indicator (pulsing dot)
- "Stop Recording" button
- "Upload Voice" button

**Process:**
```
1. User clicks "Start Recording"
2. Browser requests mic permission
3. MediaRecorder starts
4. User speaks
5. User clicks "Stop Recording"
6. Audio blob ready (✅ checkmark)
7. User enters title
8. Clicks "Upload Voice"
9. API: POST /api/voice/upload (with transcribe=true)
10. Progress: "Uploading..." → "Transcribing..." → "Embedding..."
11. Success, artifact created with transcription
```

**Features:**
- Automatic transcription
- Transcription included in metadata
- Both audio + text searchable

## 6. Governance Logging

All destructive operations include governance tracking:

### Delete Operation

```typescript
await deleteArtifact({
  artifact_id: 'abc123',
  reason: 'Outdated training data',  // Required for audit
  soft_delete: true,                  // Default (tombstone)
});

// Backend logs:
{
  timestamp: '2025-11-17T10:30:00Z',
  action: 'delete_artifact',
  user: 'aaron',
  resource_id: 'abc123',
  reason: 'Outdated training data',
  result: 'success',
  audit_log_id: 'log_xyz789'
}
```

### Re-ingest Operation

```typescript
await reingestArtifact({ artifact_id: 'abc123', force: true });

// Backend logs:
{
  timestamp: '2025-11-17T10:31:00Z',
  action: 're-index_embeddings',
  user: 'aaron',
  resource_id: 'abc123',
  result: 'success',
  details: { chunks_reprocessed: 15, model: 'text-embedding-3-large' }
}
```

### Upload Operation

```typescript
// Automatically logged with user context
await uploadFileArtifact({ file, category: 'documents' });

// Backend logs:
{
  timestamp: '2025-11-17T10:32:00Z',
  action: 'upload_artifact',
  user: 'aaron',
  resource_id: 'artifact_new123',
  result: 'success',
  details: { 
    filename: 'sales_data.pdf',
    size_bytes: 524288,
    chunks_created: 12,
    embedding_model: 'text-embedding-3-large'
  }
}
```

### Viewing Audit Log

In detail panel, optionally show ingestion history:

```tsx
{artifact.ingestion_history?.map(entry => (
  <div className="history-entry">
    <span className="entry-time">{entry.timestamp}</span>
    <span className="entry-action">{entry.action}</span>
    <span className="entry-user">{entry.user}</span>
    <span className={`entry-result ${entry.result}`}>{entry.result}</span>
  </div>
))}
```

## 7. Integration with Console

### Open Memory Explorer

```typescript
// In GraceConsole navigation
<button onClick={() => swapPanel('main', 'memory')}>
  🧠 Memory
</button>
```

### Open Specific Artifact

From another component:

```typescript
// From chat citation
if (citation.type === 'document') {
  // First open Memory Explorer
  setLayout(prev => ({ ...prev, main: 'memory' }));
  
  // Then navigate to artifact (pass via query param or state)
  // OR: Open in workspace directly
  workspaceActions.openArtifactViewer(citation.id, citation.title);
}
```

### From Mission Card

```typescript
// Mission references an artifact
<button onClick={() => {
  // Option 1: Open in Memory Explorer
  navigateToMemory(artifact.id);
  
  // Option 2: Open in workspace
  workspaceActions.openArtifactViewer(artifact.id);
}}>
  View Knowledge Artifact
</button>
```

## 8. Advanced Features

### Semantic Search

Instead of text matching, use vector similarity:

```typescript
const handleSemanticSearch = async () => {
  await searchSemantic('Sales pipeline documentation');
  // Returns most relevant artifacts by embedding similarity
};
```

**Button in UI:**
```tsx
<button
  className="semantic-search-btn"
  onClick={() => searchSemantic(searchQuery)}
  title="AI-powered semantic search"
>
  🔍
</button>
```

### Batch Operations

Select multiple artifacts:

```typescript
const [selectedIds, setSelectedIds] = useState<string[]>([]);

// Batch re-ingest
await batchReingest(selectedIds);

// Batch delete
await batchDelete(selectedIds);
```

### Link to Mission

From detail panel:

```typescript
<button onClick={async () => {
  await linkArtifactToMission(artifact.id, 'mission_123');
  refresh();
}}>
  Link to Mission
</button>
```

## 9. User Flows

### Flow 1: Upload Document

```
1. User selects "Documents" category
2. Clicks "+ Add Knowledge"
3. Upload panel expands
4. Selects "File" tab
5. Drags PDF file into drop zone
6. Progress bar: Uploading... (0% → 100%)
7. Panel closes automatically
8. List refreshes
9. New document appears in grid
10. Status dot shows "indexed" (green)
```

### Flow 2: Search and Preview

```
1. User types "sales pipeline" in search
2. Presses Enter or clicks 🔍
3. Semantic search runs
4. List shows 5 most relevant artifacts
5. User clicks artifact card
6. Detail panel slides in from right
7. Shows: preview, embeddings, linked missions
8. User clicks "Open in Workspace"
9. New workspace tab opens with full viewer
```

### Flow 3: Re-ingest Stale Embedding

```
1. User filters by status: "Stale"
2. List shows artifacts with old embeddings
3. Clicks artifact
4. Detail panel shows: Indexed 90 days ago
5. User clicks "⟳ Re-ingest"
6. Confirmation dialog appears
7. User confirms
8. API call initiated
9. Status updates to "processing"
10. After completion, status → "indexed"
11. Timestamp updates
```

### Flow 4: Delete with Governance

```
1. User selects artifact to delete
2. Clicks "🗑️ Delete"
3. Browser prompt: "Reason for deletion (for audit log):"
4. User enters: "Duplicate content"
5. Confirms deletion
6. API call includes reason
7. Backend creates audit log entry
8. Artifact soft-deleted (tombstoned)
9. Removed from list
10. Audit log preserves: who, when, why
```

## 10. Best Practices

### Always Include User Context

```typescript
// In API service
function getAuthHeaders() {
  return {
    'Authorization': `Bearer ${token}`,
    'X-User-ID': userId,        // For governance
    'X-Client': 'grace-console', // Track source
  };
}
```

### Prompt for Deletion Reason

```typescript
const handleDelete = async () => {
  const reason = prompt('Reason for deletion (for audit log):');
  if (reason === null) return; // User cancelled
  
  await deleteArtifact(artifact.id, reason);
};
```

### Show Progress for Long Operations

```typescript
const [progress, setProgress] = useState<IngestionProgress | null>(null);

await uploadFile(file, category, (prog) => {
  setProgress(prog);
  // UI automatically shows progress bar
});
```

### Use Soft Deletes

```typescript
// Default behavior - creates tombstone
await deleteArtifact({ artifact_id: id, soft_delete: true });

// Hard delete requires approval
await deleteArtifact({ artifact_id: id, soft_delete: false });
```

## 11. Testing

### Manual Testing

```
1. Upload file → Check appears in list
2. Upload text → Check creates artifact
3. Record voice → Check transcription works
4. Search artifacts → Check filters work
5. Select artifact → Check details load
6. Re-ingest → Check embeddings rebuild
7. Delete → Check requires reason, creates audit log
8. Download → Check file downloads
9. Open in workspace → Check workspace opens
```

### API Testing

```bash
# List artifacts
curl -H "Authorization: Bearer dev-token" \
  http://localhost:8017/api/ingest/artifacts?category=documents

# Upload text
curl -X POST -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test","title":"Test"}' \
  http://localhost:8017/api/remote-access/rag/ingest-text

# Re-ingest
curl -X POST -H "Authorization: Bearer dev-token" \
  http://localhost:8017/api/ingest/artifacts/{id}/reingest
```

## Summary

✅ **Complete data contracts** - Comprehensive TypeScript interfaces  
✅ **Full API layer** - All endpoints with governance  
✅ **3-panel shell** - Sidebar, main content, detail panel  
✅ **Smart filtering** - Category, status, tags, search, date range  
✅ **Sorting** - 6 options (date, name, size)  
✅ **Multi-modal upload** - File, text, voice  
✅ **Progress tracking** - Visual feedback for uploads  
✅ **Preview & actions** - Content snippets, linked missions, operations  
✅ **Governance logging** - All operations tracked with user + reason  
✅ **Batch operations** - Multi-select and batch actions  
✅ **Semantic search** - Vector similarity search  
✅ **Workspace integration** - Open artifacts in viewer  

The Memory Explorer is **production-ready** and meets all Grace criteria! 🧠🚀
