# Remote Access RAG Pipeline

## Overview

Remote access now has full RAG (Retrieval-Augmented Generation) capabilities for querying Grace's knowledge base.

## New Endpoints

### 1. Query Knowledge Base
```
POST /api/remote-access/rag/query
```

**Request:**
```json
{
  "query": "How do I configure Grace?",
  "top_k": 5,
  "source_types": ["document", "recording"],
  "with_citations": true
}
```

**Response:**
```json
{
  "success": true,
  "query": "How do I configure Grace?",
  "results": [
    {
      "content": "Grace can be configured via...",
      "source": "docs/configuration.md",
      "similarity": 0.92,
      "metadata": {}
    }
  ],
  "retrieved_at": "2025-11-16T17:00:00Z"
}
```

---

### 2. Ask with RAG
```
POST /api/remote-access/rag/ask?question=...&model=qwen2.5:32b
```

**Intelligent question answering:**
- Retrieves relevant context from knowledge base
- Generates answer using LLM with context
- Returns answer with citations

**Response:**
```json
{
  "success": true,
  "question": "How do I configure Grace?",
  "answer": "Grace can be configured in three ways...",
  "context_used": [...],
  "citations": [
    "docs/configuration.md",
    "memory/setup_guide.txt"
  ],
  "model_used": "qwen2.5:32b"
}
```

---

### 3. Get RAG Stats
```
GET /api/remote-access/rag/stats
```

**Response:**
```json
{
  "initialized": true,
  "vector_store": {
    "total_vectors": 1543,
    "collections": ["documents", "code", "conversations"]
  },
  "max_context_tokens": 4000
}
```

---

### 4. Ingest Text
```
POST /api/remote-access/rag/ingest-text
```

**Request:**
```json
{
  "content": "Grace supports multiple AI models...",
  "source": "user_notes/features.txt",
  "metadata": {"author": "user", "tags": ["features"]}
}
```

**Response:**
```json
{
  "success": true,
  "source": "user_notes/features.txt",
  "ingested_at": "2025-11-16T17:00:00Z",
  "vector_id": "vec_abc123",
  "message": "Content added to knowledge base"
}
```

---

## Features

### ✅ Secure
- Requires authentication
- Governance logging
- Audit trail
- User tracking

### ✅ Intelligent
- Vector similarity search
- Context-aware retrieval
- LLM-augmented answers
- Citation tracking

### ✅ Flexible
- Filter by source types
- Control result count (top_k)
- Choose model
- With/without citations

---

## Use Cases

### 1. Knowledge Retrieval
```bash
curl -X POST http://localhost:8000/api/remote-access/rag/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What models does Grace use?",
    "top_k": 3
  }'
```

### 2. Question Answering
```bash
curl -X POST "http://localhost:8000/api/remote-access/rag/ask?question=How+to+start+Grace&model=qwen2.5:32b" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Add Knowledge
```bash
curl -X POST http://localhost:8000/api/remote-access/rag/ingest-text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Grace now has domain-based architecture with service mesh",
    "source": "session_notes/architecture_update.txt"
  }'
```

### 4. Check RAG Status
```bash
curl http://localhost:8000/api/remote-access/rag/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Integration with Service Mesh

RAG queries can route through service mesh for intelligent load balancing:

```python
# Route RAG query through service mesh
from backend.infrastructure import service_mesh

result = await service_mesh.call_service(
    capability='rag',
    path='/rag/query',
    method='POST',
    data={'query': 'How to use Grace?'}
)
```

**Service mesh provides:**
- Automatic failover
- Circuit breakers
- Load balancing
- Health-based routing

---

## What Gets Searched

### Knowledge Sources
- ✅ Documents (PDFs, text files)
- ✅ Voice recordings (transcribed)
- ✅ Code memory (indexed code)
- ✅ Conversations (chat history)
- ✅ Learning history (training data)
- ✅ Memory tables (structured data)

### Search Strategy
1. **Vector similarity** - Semantic search using embeddings
2. **Metadata filtering** - Filter by source type, date, tags
3. **Relevance ranking** - Top-k most relevant results
4. **Citation tracking** - Know where info came from

---

## Security & Governance

### Every RAG Query Logs:
- Who queried
- What they asked
- When they asked
- What was retrieved
- Full audit trail

### Governance Controls:
- Authentication required
- User permissions checked
- Query patterns monitored
- Suspicious queries flagged

---

## Performance

### Typical Latency
- **Query only:** 50-200ms
- **Ask with LLM:** 2-5 seconds (depends on model)
- **Ingest:** 100-500ms

### Caching
- Frequent queries cached
- Embeddings cached
- Context reused when possible

---

## Example Session

```python
# 1. Ingest knowledge
await ingest_text_to_rag(
    content="Grace has 21 specialized AI models",
    source="features.txt"
)

# 2. Query knowledge
results = await query_knowledge_base({
    "query": "How many models?",
    "top_k": 3
})
# Returns: "Grace has 21 specialized AI models" (from features.txt)

# 3. Ask question
answer = await ask_with_rag(
    question="What models does Grace have?",
    model="qwen2.5:32b"
)
# Answer: "Grace has 21 specialized AI models including qwen2.5:32b, deepseek-coder-v2:16b..."
# Citations: ["features.txt"]
```

---

## Remote Access RAG Complete! ✓

**Remote clients can now:**
- ✅ Query Grace's entire knowledge base
- ✅ Get AI-generated answers with context
- ✅ Add new knowledge remotely
- ✅ Full governance and security
- ✅ Citations and source tracking
