# Ingestion Pipeline - Fix & Test

## Current Status

### ✅ What's Implemented:
- Text ingestion endpoint (`/api/ingest/text`)
- URL ingestion with trust scoring (`/api/ingest/url`)
- File upload endpoint (`/api/ingest/file`)
- Governance checks (Layer-1 + Layer-2)
- Security scanning (Hunter)
- Deduplication (SHA-256)
- Database storage (KnowledgeArtifact)
- Revision history

### ❌ Issues Found:
1. **Auth Required** - All ingest endpoints need authentication
2. **Endpoint Timeout** - Text ingestion hangs (5+ seconds)
3. **Missing Components:**
   - No chunking system
   - No embeddings
   - No vector store
   - No PDF/DOCX extraction
   - No large file chunked upload

---

## Fix 1: Remove Auth Barrier for System Use

### Option A: Allow System Token
```python
# backend/routes/ingest.py
async def ingest_text(
    req: IngestText,
    current_user: Optional[str] = None  # Make optional
):
    actor = current_user or "system"
```

### Option B: Use Memory Kernel (No Auth)
```bash
curl -X POST http://localhost:8000/kernel/memory \
  -d '{"intent":"Ingest this document: Sales pipeline guide..."}'
```

---

## Fix 2: Debug Timeout

The endpoint is hanging. Possible causes:
- Governance check blocking
- Verification decorator hanging
- Database transaction not committing
- Missing async await

### Check:
```bash
# View backend logs
# Look for: [INGESTION] or [GOVERNANCE] or errors
```

### Temporary Fix: Remove Blocking Decorator
```python
# Change from:
@verify_action("data_ingest", lambda data: data.get("title", "unknown"))

# To (temporary):
# @verify_action("data_ingest", lambda data: data.get("title", "unknown"))
```

---

## Add Missing Components

### 1. Chunking System

Create `backend/chunking.py`:
```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(' '.join(chunk_words))
        i += chunk_size - overlap
    return chunks
```

### 2. Embedding (Simple OpenAI)

```python
# backend/embeddings.py
import openai

async def embed_text(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI"""
    response = await openai.Embedding.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [item['embedding'] for item in response['data']]
```

### 3. Vector Store (Chroma - Simple)

```python
# backend/vector_store.py
import chromadb

client = chromadb.Client()
collection = client.create_collection("grace_knowledge")

def store_chunks(chunks: List[str], embeddings: List[List[float]], metadata: List[Dict]):
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadata,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

def search(query_embedding: List[float], k: int = 10):
    return collection.query(query_embeddings=[query_embedding], n_results=k)
```

---

## Quick Test: Minimal Working Ingestion

Remove auth requirement temporarily to test:

```python
# backend/routes/ingest.py
@router.post("/text", response_model=IngestTextResponse)
async def ingest_text(
    req: IngestText,
    current_user: Optional[str] = None  # CHANGED
):
    actor = current_user or "system"  # ADDED
    # ... rest of code
```

Then test:
```bash
curl -X POST http://localhost:8000/api/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test document content",
    "title": "Test",
    "domain": "test"
  }'
```

Should return:
```json
{
  "status": "ingested",
  "artifact_id": 1,
  "execution_trace": {...},
  "data_provenance": [...]
}
```

---

## Full Ingestion Pipeline (To Build)

```
Input File/Text/URL
  ↓
[Extract] PDF/DOCX/HTML → Raw text
  ↓
[Chunk] Split into 1k token chunks with overlap
  ↓
[Embed] Generate vector embeddings
  ↓
[Store] Vector DB + PostgreSQL
  ↓
[Index] Full-text search indexing
  ↓
[Register] Memory Broker + Knowledge catalog
  ↓
[Verify] Snapshot + Contract
```

---

## Next Steps

1. Fix auth barrier on ingest endpoints
2. Debug timeout issue
3. Add chunking (simple word-based)
4. Add embeddings (OpenAI API)
5. Add vector store (Chroma local)
6. Test end-to-end ingestion → query

Want me to implement these fixes now?
