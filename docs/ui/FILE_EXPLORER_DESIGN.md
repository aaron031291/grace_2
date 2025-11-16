# File Explorer UI - Design Specification

**Purpose**: Browse, manage, and ingest knowledge artifacts with full governance

---

## 🎯 Overview

A file explorer panel (or dynamic workspace tab) that shows knowledge artifact categories and embedded files from the database and `grace_training/` storage.

**Key Features**:
- Browse knowledge artifacts by category
- View metadata (source path, tags, ingestion date)
- Actions: preview, re-ingest, append notes
- Drag-drop upload with auto-chunking/embedding
- Search/filter via RAG
- Zero-trust access control

---

## 🗂️ File Explorer Panel

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│  Knowledge Explorer                                    [⚙️] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Search: [___________________________] [🔍]                 │
│  Filter: [All Categories ▼] [Last 7 days ▼]               │
│                                                              │
│  Categories:                    Files (23):                 │
│  ┌──────────────────┐          ┌────────────────────────┐  │
│  │ 📚 Documents (45) │          │ □ company_vision_2025  │  │
│  │ 🎙️ Recordings (12)│          │   📄 PDF, 2.3MB       │  │
│  │ 💬 Conversations  │          │   📅 Nov 14, 2025     │  │
│  │ 📊 Training Data  │          │   🏷️ strategy, vision │  │
│  │ 📖 Books (8)      │          │   [Preview] [Notes]   │  │
│  │ 🧠 Insights       │          │                        │  │
│  │ 🔐 Governance     │          │ □ sales_playbook      │  │
│  │ 🌐 Web Learnings  │          │   📄 MD, 156KB        │  │
│  │ 💾 Code Memories  │          │   📅 Nov 12, 2025     │  │
│  └──────────────────┘          │   🏷️ sales, process   │  │
│                                 │   [Preview] [Notes]   │  │
│  Actions:                       │                        │  │
│  [📤 Upload Files]              │ □ pricing_strategy    │  │
│  [📝 Add Text Note]             │   📄 MD, 89KB         │  │
│  [🎤 Record Voice]              │   📅 Nov 10, 2025     │  │
│  [🔄 Bulk Re-index]            │   🏷️ finance, pricing │  │
│                                 │   [Preview] [Notes]   │  │
│                                 └────────────────────────┘  │
│                                                              │
│  [Drag & Drop files here to upload]                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 File Entry Metadata

### Display Format
```
┌────────────────────────────────────────────────────────────┐
│ □ company_vision_2025.pdf                            [⋮]  │
├────────────────────────────────────────────────────────────┤
│ 📄 Type: PDF                    Size: 2.3MB                │
│ 📅 Uploaded: Nov 14, 2025       By: admin                  │
│ 📂 Category: Documents/Strategy                            │
│ 🏷️ Tags: strategy, vision, 2025, company                  │
│ 📊 Chunks: 48                   Embeddings: 48             │
│ 🔍 Searchable: Yes             Indexed: Yes                │
│ 🔐 Access: Admin only           Governance: Approved       │
│                                                             │
│ Source Path: grace_training/documents/company_vision_2025  │
│ Vector ID: vec_abc123...                                    │
│ Ingested: 2025-11-14T10:30:00Z                            │
│                                                             │
│ Actions:                                                    │
│ [👁️ Preview] [✏️ Add Notes] [🔄 Re-ingest] [🗑️ Delete]  │
│ [📊 View Embeddings] [🔗 View Citations] [⬇️ Download]    │
└────────────────────────────────────────────────────────────┘
```

---

## 🎬 Actions

### Preview
**Opens**: Preview modal or workspace tab

**Displays**:
- Full content (rendered for PDFs/Markdown)
- Extracted text for images
- Transcript for audio/video
- Syntax highlighting for code

**Implementation**:
```typescript
const onPreview = async (file: KnowledgeArtifact) => {
  const content = await fetch(`/api/knowledge/preview/${file.id}`);
  showPreviewModal(content);
};
```

---

### Add Notes
**Opens**: Notes editor modal

**Features**:
- Append user notes to artifact
- Markdown editor
- Auto-saves
- Searchable via RAG

**Implementation**:
```typescript
const onAddNotes = async (file: KnowledgeArtifact, notes: string) => {
  await fetch(`/api/knowledge/${file.id}/notes`, {
    method: 'POST',
    body: JSON.stringify({ notes })
  });
  
  // Re-index with notes included
  await fetch(`/api/knowledge/${file.id}/re-index`);
};
```

---

### Re-ingest
**Purpose**: Re-process file with updated chunking/embedding

**Use cases**:
- Better embedding model available
- Chunking strategy improved
- Metadata updated

**Implementation**:
```typescript
const onReIngest = async (file: KnowledgeArtifact) => {
  await fetch(`/api/knowledge/${file.id}/re-ingest`, {
    method: 'POST'
  });
  
  showNotification('Re-ingesting... This may take a moment.');
};
```

---

### Delete
**Purpose**: Remove artifact from knowledge base

**Safety**:
- Confirmation dialog
- Soft delete (can restore)
- Removes from vector index
- Archives original file

**Implementation**:
```typescript
const onDelete = async (file: KnowledgeArtifact) => {
  const confirmed = await confirmDialog(
    'Delete this knowledge artifact?',
    'This will remove it from search but archive the file.'
  );
  
  if (confirmed) {
    await fetch(`/api/knowledge/${file.id}`, {
      method: 'DELETE'
    });
  }
};
```

---

## 📤 Upload/Ingest Controls

### Drag & Drop Upload
```typescript
const onDrop = async (files: File[], category: string) => {
  for (const file of files) {
    // Upload file
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('auto_ingest', 'true');
    
    const response = await fetch('/api/knowledge/upload', {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      // Auto-triggers chunking/embedding
      showNotification(`✅ Uploaded and ingesting ${file.name}`);
    }
  }
};
```

### Integration with Existing Endpoints

**Text Upload**:
```
POST /api/remote-access/rag/ingest-text
- Body: { text, category, tags, metadata }
- Auto-chunks and embeds immediately
```

**Document Upload**:
```
POST /api/ingestion/upload-document
- Supports: PDF, DOCX, TXT, MD
- Extracts text → chunks → embeds
- Stores in grace_training/documents/
```

**Voice Upload**:
```
POST /api/speech/upload-voice-note
- Transcribes audio → text
- Embeds transcript
- Stores audio in audio_messages/
```

**Bulk Upload to Category**:
```
POST /api/knowledge/bulk-upload
- Body: { files[], category, auto_embed: true }
- Stores in appropriate grace_training/ folder
- Triggers vector_integration to embed all
```

---

## 🔍 Search/Filter

### RAG-Powered Search
```
┌────────────────────────────────────────────────────────────┐
│ Search: [memory leak python]                        [🔍]  │
├────────────────────────────────────────────────────────────┤
│ 📊 Results: 8 artifacts (ranked by relevance)              │
│                                                             │
│ 1. debugging_memory_leaks.md (95% match)                   │
│    "...Python memory profiling with tracemalloc..."        │
│    Category: Training Data  |  Nov 10, 2025                │
│    [View] [Open in Editor]                                 │
│                                                             │
│ 2. memory_optimization_notes.txt (89% match)               │
│    "...garbage collection and weak references..."          │
│    Category: Code Memories  |  Nov 8, 2025                 │
│    [View] [Open in Editor]                                 │
│                                                             │
│ 3. python_performance_guide.pdf (84% match)                │
│    "...memory allocation strategies..."                    │
│    Category: Documents  |  Nov 5, 2025                     │
│    [View] [Download]                                        │
│                                                             │
│ [Load More...]                                              │
└────────────────────────────────────────────────────────────┘
```

### Search Implementation
```typescript
const searchKnowledge = async (query: string) => {
  const response = await fetch('/api/knowledge/search', {
    method: 'POST',
    body: JSON.stringify({
      query,
      top_k: 10,
      threshold: 0.7,
      categories: selectedCategories  // Filter by category
    })
  });
  
  const results = await response.json();
  return results.artifacts;
};
```

### Verify Before Upload
**Prevent duplicates**: Search before adding new files

```typescript
const checkDuplicate = async (filename: string) => {
  // Search for existing file by name
  const existing = await fetch(`/api/knowledge/check-exists`, {
    method: 'POST',
    body: JSON.stringify({ filename })
  });
  
  if (existing.exists) {
    return confirmDialog(
      `File "${filename}" already exists. Upload anyway?`,
      'This will create a new version.'
    );
  }
  
  return true;
};
```

---

## 🔐 Access & Permissions

### Zero-Trust Integration

**Backend Security**:
```python
# backend/routes/knowledge_explorer_api.py

from backend.security.auth import require_auth
from backend.security.secrets_vault import verify_access
from backend.core.immutable_log import log_knowledge_access

@router.get("/api/knowledge/list")
@require_auth
async def list_knowledge_artifacts(
    user_id: str,
    category: Optional[str] = None
):
    """
    List knowledge artifacts with access control
    """
    # Verify user has permission
    has_access = await verify_access(
        user_id=user_id,
        resource="knowledge_base",
        action="read"
    )
    
    if not has_access:
        raise HTTPException(403, "Access denied")
    
    # Log access
    await log_knowledge_access(
        user_id=user_id,
        action="list",
        category=category
    )
    
    # Return artifacts
    artifacts = await get_knowledge_artifacts(category=category)
    return {"artifacts": artifacts}
```

### Credential Vault Integration
**For remote file access**:

```python
# Access files from remote storage
from backend.security.secure_credential_vault import secure_credential_vault

async def fetch_remote_file(file_path: str, user_id: str):
    # Request credentials through governance
    creds = await secure_credential_vault.retrieve_secret(
        key="REMOTE_STORAGE_TOKEN",
        requesting_service="knowledge_explorer",
        purpose=f"Fetch file: {file_path}",
        user_id=user_id
    )
    
    # Consent prompt shown to user
    # If approved, credentials provided
    # If denied, exception raised
    
    # Credentials NEVER logged or exposed
    return await download_with_creds(file_path, creds)
```

### Audit Trail
**Every action logged**:
```python
# All operations logged to immutable log
await log_knowledge_access(
    user_id="admin",
    action="upload",
    artifact_id="art_123",
    metadata={
        "filename": "sales_playbook.md",
        "category": "training_data",
        "size_bytes": 156000,
        "tags": ["sales", "process"]
    }
)

await log_knowledge_access(
    user_id="admin",
    action="delete",
    artifact_id="art_456",
    reason="outdated_content"
)
```

---

## 📤 Upload/Ingest Workflow

### Drag & Drop Upload
```
User: [Drags sales_playbook.pdf into Explorer]
      [Drops into "Training Data" category]

Grace:
1. Checks for duplicates
   → "sales_playbook.pdf already exists. Upload new version?"
   
2. User confirms
   
3. Upload file:
   POST /api/knowledge/upload
   - file: sales_playbook.pdf
   - category: training_data
   - tags: sales, process
   - auto_ingest: true

4. Store in: grace_training/documents/sales_playbook.pdf

5. Trigger ingestion:
   POST /api/ingestion/ingest-document
   - Extracts text from PDF
   - Chunks into paragraphs
   - Generates embeddings
   - Stores in vector database

6. Update UI:
   Explorer shows: "✅ sales_playbook.pdf ingested (48 chunks)"
```

### Paste Text Directly
```
User: Clicks [📝 Add Text Note]

Modal opens:
┌────────────────────────────────────────────────────┐
│ Add Knowledge Note                             [×] │
├────────────────────────────────────────────────────┤
│ Title: [________________________]                  │
│ Category: [Documents ▼]                            │
│ Tags: [_________________________]                  │
│                                                     │
│ Content:                                            │
│ ┌────────────────────────────────────────────────┐ │
│ │ [Markdown editor with preview]                 │ │
│ │                                                 │ │
│ │                                                 │ │
│ └────────────────────────────────────────────────┘ │
│                                                     │
│ [Cancel] [Save & Ingest]                           │
└────────────────────────────────────────────────────┘

User: Writes content, clicks "Save & Ingest"

Grace:
1. POST /api/remote-access/rag/ingest-text
   - text: user content
   - category: documents
   - tags: parsed from input
   
2. Chunks text immediately
3. Generates embeddings
4. Adds to RAG index
5. Shows: "✅ Note added and indexed"
```

### Bulk Upload
```
User: Selects multiple files (Ctrl+Click)
      Clicks [📤 Upload to Category]

Modal:
┌────────────────────────────────────────────────────┐
│ Bulk Upload (5 files)                          [×] │
├────────────────────────────────────────────────────┤
│ Files:                                              │
│ • report_q1.pdf (2.3MB)                            │
│ • report_q2.pdf (2.1MB)                            │
│ • report_q3.pdf (2.4MB)                            │
│ • summary.docx (156KB)                             │
│ • analysis.xlsx (892KB)                            │
│                                                     │
│ Upload to: [Documents/Reports ▼]                   │
│ Tags: [__________________________]                  │
│ Auto-ingest: [✓] Yes  [ ] No                       │
│                                                     │
│ [Cancel] [Upload All]                              │
└────────────────────────────────────────────────────┘

User: Clicks "Upload All"

Grace:
1. POST /api/knowledge/bulk-upload
   - files: [5 files]
   - category: documents/reports
   - auto_embed: true
   
2. Stores each file in grace_training/documents/reports/
3. Triggers vector_integration.embed_all()
4. Shows progress: "Ingesting 5 files... (2/5 complete)"
5. Completes: "✅ All files ingested (234 total chunks)"
```

---

## 🔍 Search/Filter Features

### Search by Content (RAG)
```typescript
// Search knowledge using RAG query
const searchResults = await fetch('/api/knowledge/search', {
  method: 'POST',
  body: JSON.stringify({
    query: 'memory leak python',
    top_k: 10,
    categories: ['documents', 'code_memories'],
    min_score: 0.7
  })
});

// Results ranked by semantic similarity
// Shows: filename, chunk preview, relevance score
```

### Filter by Metadata
```typescript
// Filter by category, date, tags
const filtered = await fetch('/api/knowledge/list', {
  method: 'GET',
  params: {
    category: 'documents',
    tags: 'sales,strategy',
    after: '2025-11-01',
    before: '2025-11-30',
    limit: 50
  }
});
```

### Check Before Upload
```typescript
// Verify if knowledge already exists
const checkExists = async (content: string) => {
  const similar = await fetch('/api/knowledge/find-similar', {
    method: 'POST',
    body: JSON.stringify({
      text: content,
      threshold: 0.9  // 90% similarity = likely duplicate
    })
  });
  
  if (similar.count > 0) {
    showWarning(`Similar content exists: ${similar.artifacts[0].title}`);
  }
};
```

---

## 🗂️ Categories & Storage

### Knowledge Categories
```
grace_training/
├── documents/           # PDFs, DOCX, MD files
│   ├── company_vision_2025.pdf
│   ├── product_strategy_q1.md
│   └── investor_update_q1.md
│
├── conversations/       # Chat transcripts, meeting notes
│   └── (auto-generated from chat history)
│
├── code/               # Code snippets, examples
│   ├── architect.md
│   ├── debug.md
│   └── deep-research-agent.md
│
├── domain_knowledge/   # Domain-specific knowledge
│   └── README.md
│
├── safety/            # Ethics, safety policies
│   ├── ethics_board_minutes.md
│   └── ai_safety_review_2025.md
│
├── governance/        # Governance documents
│   ├── privacy_impact_assessment.md
│   └── compliance_review_notes.md
│
├── research/          # Research papers, findings
│   └── README.md
│
├── sales/             # Sales materials
│   ├── sales_playbook.md
│   └── pricing_strategy.md
│
├── finance/           # Financial documents
│   ├── pricing_strategy.md
│   └── investor_update_q1.md
│
├── marketing/         # Marketing content
│   └── content_calendar.md
│
├── configuration/     # Config documentation
│   └── README.md
│
├── playbooks/         # Operational playbooks
│   ├── coding_agent_guidelines.md
│   └── sub_agent_handbook.md
│
├── agents/            # Agent documentation
│   └── self_healing_lifecycle.md
│
├── learning/          # Learning logs, insights
│   └── README.md
│
├── insights/          # Generated insights
│   └── README.md
│
├── crypto/            # Cryptographic audit trails
│   └── README.md
│
└── immutable_logs/    # Immutable audit logs
    └── README.md
```

### Category Mapping
| Category | Storage Path | Ingest Endpoint |
|----------|-------------|-----------------|
| Documents | `grace_training/documents/` | `/api/ingestion/upload-document` |
| Voice Notes | `audio_messages/` | `/api/speech/upload-voice-note` |
| Conversations | `grace_training/conversations/` | Auto-generated |
| Code | `grace_training/code/` | `/api/knowledge/upload` |
| Training Data | `grace_training/` | `/api/remote-access/rag/ingest-text` |
| Books | `grace_training/documents/books/` | `/api/ingestion/upload-book` |

---

## 🎯 Workflow Examples

### Example 1: Upload Company Document
```
1. User opens File Explorer (Cmd+K → "knowledge explorer")
2. Drags "company_strategy_2026.pdf" into explorer
3. Drops into "Documents/Strategy" category
4. Grace:
   - Checks for duplicates (none found)
   - Uploads to grace_training/documents/
   - Extracts text from PDF
   - Chunks into 52 segments
   - Generates embeddings
   - Indexes in vector database
5. Explorer shows: "✅ Indexed (52 chunks)"
6. User can now search: "what's our 2026 strategy?"
7. Grace retrieves relevant chunks from RAG
```

### Example 2: Add Voice Note
```
1. User clicks [🎤 Record Voice] in File Explorer
2. Records 2-minute voice note about bug fix
3. Clicks "Save"
4. Grace:
   - Saves audio to audio_messages/
   - Transcribes using Whisper
   - Embeds transcript
   - Makes searchable
5. Later, user asks: "How did I fix that bug?"
6. Grace: "Based on your voice note from Nov 14..."
   [Shows transcript with timestamp]
```

### Example 3: Search Before Adding
```
1. User has idea for sales process improvement
2. Opens File Explorer
3. Searches: "sales process improvement"
4. Results show:
   - sales_playbook.md (already has this!)
   - sales_optimization_notes.txt (similar idea)
5. User reviews existing content
6. Decides to append notes instead of creating new file
7. Clicks [✏️ Add Notes] on sales_playbook.md
8. Adds new insights
9. Grace re-indexes with new content
```

---

## 🔌 Backend API Endpoints

### Knowledge Explorer API
```python
# backend/routes/knowledge_explorer_api.py

router = APIRouter(prefix="/api/knowledge", tags=["knowledge_explorer"])

@router.get("/list")
async def list_artifacts(category: str = None, tags: str = None):
    """List all knowledge artifacts with filters"""
    pass

@router.get("/{artifact_id}")
async def get_artifact_detail(artifact_id: str):
    """Get full metadata for artifact"""
    pass

@router.get("/preview/{artifact_id}")
async def preview_artifact(artifact_id: str):
    """Get artifact content for preview"""
    pass

@router.post("/upload")
async def upload_artifact(file: UploadFile, category: str, tags: List[str]):
    """Upload and auto-ingest new artifact"""
    pass

@router.post("/bulk-upload")
async def bulk_upload(files: List[UploadFile], category: str):
    """Bulk upload multiple files"""
    pass

@router.post("/{artifact_id}/notes")
async def add_notes(artifact_id: str, notes: str):
    """Append user notes to artifact"""
    pass

@router.post("/{artifact_id}/re-ingest")
async def re_ingest_artifact(artifact_id: str):
    """Re-process artifact with latest pipeline"""
    pass

@router.delete("/{artifact_id}")
async def delete_artifact(artifact_id: str):
    """Soft delete artifact"""
    pass

@router.post("/search")
async def search_knowledge(query: str, top_k: int = 10):
    """RAG-powered semantic search"""
    pass

@router.post("/check-exists")
async def check_duplicate(filename: str):
    """Check if file already exists"""
    pass

@router.post("/find-similar")
async def find_similar(text: str, threshold: float = 0.9):
    """Find similar existing content"""
    pass
```

---

## 🛡️ Governance & Audit

### Every Action Logged
```python
# Immutable audit log
{
  "timestamp": "2025-11-16T10:30:00Z",
  "user_id": "admin",
  "action": "upload",
  "resource": "knowledge_base",
  "artifact_id": "art_123",
  "metadata": {
    "filename": "company_vision_2025.pdf",
    "category": "documents/strategy",
    "size_bytes": 2300000,
    "tags": ["strategy", "vision", "2025"]
  },
  "access_method": "file_explorer_ui",
  "ip_address": "192.168.1.100",
  "governance_approved": true
}
```

### Access Control
```python
# Permission levels
PERMISSIONS = {
    "read": ["admin", "operator", "viewer"],
    "write": ["admin", "operator"],
    "delete": ["admin"],
    "ingest": ["admin", "operator"]
}

# Check permission
def check_permission(user_id: str, action: str) -> bool:
    user_role = get_user_role(user_id)
    return user_role in PERMISSIONS.get(action, [])
```

---

## 🎨 UI Implementation

### Component Structure
```typescript
// FileExplorer.tsx
export const FileExplorer = () => {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  return (
    <div className="file-explorer">
      <SearchBar onSearch={setSearchQuery} />
      <FilterBar onCategoryChange={setSelectedCategory} />
      
      <div className="explorer-content">
        <CategoryTree 
          onSelect={setSelectedCategory}
          counts={categoryCounts}
        />
        
        <FileList
          artifacts={filteredArtifacts}
          onPreview={handlePreview}
          onAddNotes={handleAddNotes}
          onReIngest={handleReIngest}
          onDelete={handleDelete}
        />
      </div>
      
      <DropZone onDrop={handleUpload} />
      
      <ActionBar
        onUpload={handleManualUpload}
        onAddText={handleAddText}
        onRecordVoice={handleRecordVoice}
      />
    </div>
  );
};
```

---

## 📊 Integration with Existing Systems

### With Ingestion Pipeline
```
File Explorer → Upload → Existing Ingestion Services
- Documents: POST /api/ingestion/upload-document
- Voice: POST /api/speech/upload-voice-note
- Text: POST /api/remote-access/rag/ingest-text
- Books: POST /api/ingestion/upload-book
```

### With RAG System
```
File Explorer Search → RAG Query API
- Semantic search across all ingested content
- Returns chunks with relevance scores
- Links back to source artifacts
```

### With Vector Integration
```
Bulk Upload → vector_integration.embed_all()
- Auto-triggers embedding generation
- Updates vector database
- Makes content searchable immediately
```

### With World Model
```
File Explorer → World Model Knowledge Store
- All uploads become part of Grace's knowledge
- Searchable via world model queries
- Used for autonomous decision-making
```

---

## 🚀 Implementation Tasks

### Backend (Week 1-2)
- [ ] Create `/api/knowledge/explorer` API routes
- [ ] Implement file listing with metadata
- [ ] Add upload handler with auto-ingest
- [ ] Wire to existing ingestion endpoints
- [ ] Add RAG search integration
- [ ] Implement access control
- [ ] Add audit logging

### Frontend (Week 2-3)
- [ ] Build FileExplorer component
- [ ] Implement CategoryTree
- [ ] Create FileList with cards
- [ ] Add DropZone for drag-drop
- [ ] Implement search UI
- [ ] Add preview modal
- [ ] Create upload/bulk upload flows
- [ ] Add notes editor

### Integration (Week 3-4)
- [ ] Connect to existing ingestion pipeline
- [ ] Wire RAG search
- [ ] Implement governance checks
- [ ] Add audit trail
- [ ] Test with real files
- [ ] Performance optimization

---

## 📋 Configuration

### Enable in .env
```bash
# File Explorer Settings
GRACE_FILE_EXPLORER_ENABLED=true
GRACE_KNOWLEDGE_BASE_PATH=grace_training/
GRACE_AUDIO_PATH=audio_messages/
GRACE_MAX_UPLOAD_SIZE_MB=50
GRACE_AUTO_INGEST_ON_UPLOAD=true
GRACE_ENABLE_BULK_UPLOAD=true
```

---

## ✅ Benefits

**For Users**:
- 📂 Visual file management (no CLI needed)
- 🔍 Powerful search (semantic, not just filename)
- ⚡ Quick upload (drag-drop or paste)
- 👁️ Preview before indexing
- 📝 Add context with notes
- 🔄 Re-ingest with better models

**For Grace**:
- 🧠 Organized knowledge base
- 🔎 Everything searchable via RAG
- 📊 Metadata for intelligent retrieval
- 🔐 Governed access with audit trail
- 📈 Tracks knowledge growth over time
- 🎯 Better answers from richer knowledge

---

**Status**: File Explorer fully specified. Ready for implementation alongside Unified Console! 🎉
