# Drag & Drop File Ingestion - Complete Guide

## Overview

Grace now has a **unified drag-and-drop file ingestion system** that automatically processes and ingests files into the training corpus when dropped into specific folders.

## Key Features

### 🎯 Automatic Modality Detection
Files are automatically categorized by type:
- **API** - JSON, XML, YAML
- **Web** - HTML, Markdown
- **Audio** - MP3, WAV, M4A, FLAC
- **Video** - MP4, AVI, MOV, MKV
- **Code** - Python, JavaScript, TypeScript, etc.
- **Books** - PDF, EPUB (existing pipeline)
- **Upload** - General files

### 🧠 Learning Folder Auto-Processing
Files dropped into `storage/memory/learning/` automatically:
1. ✅ Trigger full ML/DL pipeline
2. ✅ Generate embeddings
3. ✅ Create summaries/insights
4. ✅ Tag as standard training corpus
5. ✅ Publish to event bus
6. ✅ Update trust scores

### 📥 Storage Structure
```
storage/memory/
├── learning/          # Auto-ingest + ML/DL pipeline
│   └── *.*           # Files here = training corpus
├── raw/
│   ├── api/          # API responses
│   ├── web/          # Web scrapes
│   ├── audio/        # Audio files
│   ├── video/        # Video files
│   ├── code/         # Code repos/files
│   ├── xxl/          # Extra-large files (>100MB)
│   └── upload/       # General uploads
└── processed/
    ├── transcripts/  # Audio/video transcriptions
    └── frames/       # Video frame extractions
```

## Frontend Components

### FileDropZone Component

**Location:** `frontend/src/components/FileDropZone.tsx`

**Usage:**
```tsx
import { FileDropZone } from './components/FileDropZone';

// Basic usage
<FileDropZone />

// Learning folder with auto-ingestion
<FileDropZone 
  folder="learning" 
  autoIngest={true}
  onUploadComplete={(results) => {
    console.log('Upload complete:', results);
  }}
/>

// Specific modality folder
<FileDropZone 
  folder="api"
  autoIngest={true}
/>
```

**Props:**
- `folder?: string` - Destination folder (default: 'upload')
- `autoIngest?: boolean` - Auto-trigger ingestion (default: false)
- `onUploadComplete?: (results) => void` - Callback on completion

### Integration Examples

#### In System Overview
```tsx
// Add to SystemOverview.tsx detail drawer
{activeDrawer === 'ingestion' && (
  <div className="ingestion-details">
    <FileDropZone folder="learning" autoIngest={true} />
    <IngestionDetails stats={ingestionStats} files={recentFiles} />
  </div>
)}
```

#### In File Explorer
```tsx
// Add to FileExplorer.tsx
{currentFolder === 'Learning Memory' && (
  <FileDropZone 
    folder="learning"
    autoIngest={true}
    onUploadComplete={refreshFileList}
  />
)}
```

## Backend Architecture

### FileIngestionAgent

**Location:** `backend/kernels/agents/file_ingestion_agent.py`

**Workflow:**
1. **Detect modality** - Auto-detect file type
2. **Store file** - Move to appropriate folder
3. **Extract metadata** - Size, hash, mime-type
4. **Create document entry** - Add to `memory_documents`
5. **Process by modality:**
   - API: Parse JSON/XML structure
   - Web: Extract links, text
   - Audio: Queue transcription (Whisper)
   - Video: Queue frame extraction + transcription
   - Code: Trigger code analysis
   - XXL: Enable streaming processing
6. **Trigger embeddings** - Send to ML pipeline
7. **Queue verification** - Auto-verify quality
8. **Publish events** - Notify downstream systems

### API Endpoints

**Upload with Auto-Ingestion:**
```http
POST /api/ingestion/upload
Content-Type: multipart/form-data

Parameters:
  - file: File (required)
  - folder: string (default: 'upload')
  - modality: string (optional override)
  - title: string (optional)
  - description: string (optional)

Response:
{
  "status": "success",
  "document_id": "uuid-1234",
  "modality": "audio",
  "storage_path": "storage/memory/learning/podcast.mp3",
  "auto_ingested": true,
  "is_learning_corpus": true,
  "message": "File 'podcast.mp3' added to learning corpus and ingested successfully"
}
```

**Get Ingestion Stats:**
```http
GET /api/ingestion/stats

Response:
{
  "total_files": 1247,
  "by_modality": {
    "book": 150,
    "audio": 45,
    "video": 23,
    "code": 890,
    "api": 89,
    "web": 50
  },
  "trust_levels": {
    "high": 1100,
    "medium": 120,
    "low": 27
  },
  "recent_ingestions_7d": 67,
  "total_chunks": 45230,
  "average_trust_score": 0.891
}
```

**Get Recent Files:**
```http
GET /api/ingestion/recent?limit=20&modality=audio

Response:
[
  {
    "document_id": "uuid-5678",
    "title": "podcast_episode_42.mp3",
    "modality": "audio",
    "trust_score": 0.95,
    "ingested_at": "2025-01-20T10:30:00Z",
    "file_path": "storage/memory/learning/podcast_episode_42.mp3",
    "metadata": {
      "is_standard_training": true,
      "transcription_path": "storage/memory/processed/transcripts/uuid-5678.txt"
    }
  }
]
```

## Event System

### Published Events

**File Ingestion Started:**
```python
Event(
    event_type="file.ingestion.started",
    source="file_ingestion_agent",
    payload={
        "file": "storage/memory/learning/data.json",
        "modality": "api",
        "is_xxl": false
    }
)
```

**Learning Corpus File Added:**
```python
Event(
    event_type="learning.corpus.file_added",
    source="file_ingestion_api",
    payload={
        "document_id": "uuid-9012",
        "modality": "audio",
        "file_path": "storage/memory/learning/lecture.mp3",
        "auto_ml_enabled": true
    }
)
```

**ML Embedding Requested:**
```python
Event(
    event_type="ml.embedding.requested",
    source="file_ingestion_agent",
    payload={
        "document_id": "uuid-9012",
        "modality": "audio",
        "priority": "normal"
    }
)
```

**Audio Transcription Requested:**
```python
Event(
    event_type="file.processing.audio",
    source="file_ingestion_agent",
    payload={
        "document_id": "uuid-9012",
        "action": "transcription_requested"
    }
)
```

## Modality-Specific Processing

### Audio Files
1. Upload to `storage/memory/learning/`
2. Auto-trigger Whisper transcription
3. Save transcript to `storage/memory/processed/transcripts/`
4. Chunk transcript text
5. Generate embeddings
6. Create insights
7. Update `memory_documents` with both paths

### Video Files
1. Upload to `storage/memory/learning/`
2. Extract frames at intervals
3. Transcribe audio track
4. Save to `storage/memory/processed/frames/` and `.../transcripts/`
5. Generate image embeddings
6. Generate text embeddings
7. Link all artifacts

### Code Files
1. Upload to `storage/memory/raw/code/`
2. Trigger `code_memory.py` pipeline
3. Parse syntax, extract functions
4. Build knowledge graph
5. Link to tests, documentation
6. Update code catalog

### XXL Files (>100MB)
1. Detect size threshold
2. Enable streaming upload
3. Save to `storage/memory/raw/xxl/`
4. Process in chunks with checkpoints
5. Resume on failure

## Usage Examples

### Example 1: Upload Audio for Transcription
```tsx
// Frontend
<FileDropZone 
  folder="learning"
  autoIngest={true}
  onUploadComplete={(results) => {
    results.forEach(r => {
      if (r.modality === 'audio') {
        console.log('Audio file queued for transcription:', r.document_id);
      }
    });
  }}
/>
```

Result:
- File saved to `storage/memory/learning/podcast.mp3`
- Event `file.processing.audio` published
- Whisper transcription job queued
- Transcript saved to `storage/memory/processed/transcripts/{doc_id}.txt`
- Both paths stored in `memory_documents`

### Example 2: Upload API Response
```tsx
// Frontend
<FileDropZone 
  folder="api"
  autoIngest={true}
/>
```

Result:
- File saved to `storage/memory/raw/api/response.json`
- JSON structure parsed
- Entities extracted
- Metadata includes source URL, timestamp
- Embeddings generated

### Example 3: Upload Training Video
```tsx
// Frontend
<FileDropZone 
  folder="learning"
  autoIngest={true}
/>
```

Result:
- File saved to `storage/memory/learning/tutorial.mp4`
- Frames extracted to `storage/memory/processed/frames/{doc_id}/`
- Audio transcribed to `storage/memory/processed/transcripts/{doc_id}.txt`
- Tagged as `is_standard_training: true`
- Event `learning.corpus.file_added` published

## Database Schema

### memory_documents Table
```sql
id (uuid)
title (text)
source_type (text)  -- modality: 'audio', 'video', 'api', etc.
file_path (text)    -- original file path
metadata (jsonb)    -- includes:
  - is_standard_training: boolean
  - source_folder: string
  - transcription_path: string (for audio/video)
  - frame_extraction_path: string (for video)
  - original_filename: string
trust_score (float)
last_synced_at (timestamp)
```

### memory_document_chunks Table
```sql
id (uuid)
document_id (uuid FK)
chunk_index (int)
content (text)
embedding (vector)
metadata (jsonb)
```

## Monitoring & Metrics

### System Overview Tile
The **File Ingestion** tile in System Overview shows:
- Total files ingested
- Files ingested this week
- Breakdown by modality
- Average trust score
- Recent uploads

**Click tile to open drawer with:**
- Full stats breakdown
- Modality distribution chart
- Recent files list
- Trust score trends

## Testing

### Manual Test
1. Open frontend: http://localhost:5173
2. Navigate to System Overview
3. Click **📥 File Ingestion** tile
4. Drag audio file onto drop zone
5. Watch progress bar
6. See "Complete!" status
7. Check backend logs for events

### Backend Test
```python
# Test ingestion agent directly
from backend.kernels.agents.file_ingestion_agent import FileIngestionAgent
from pathlib import Path

agent = FileIngestionAgent()
await agent.activate()

result = await agent.process_file(
    file_path=Path("test.mp3"),
    metadata={"is_standard_training": True},
    modality="audio"
)

print(result)
# {
#   "status": "completed",
#   "document_id": "uuid-...",
#   "modality": "audio",
#   "processed_artifacts": {
#     "type": "audio",
#     "transcription_queued": True
#   }
# }
```

## Summary

✅ **Unified ingestion system** for all file types
✅ **Drag-and-drop UI** with progress tracking
✅ **Auto-detection** of modality
✅ **Learning folder** triggers full ML/DL pipeline
✅ **Event-driven** processing
✅ **Metadata tagging** for training corpus
✅ **Monitoring dashboard** in System Overview

**Drop files into `storage/memory/learning/` and they're automatically ingested, processed, embedded, and added to Grace's training corpus!** 🚀
