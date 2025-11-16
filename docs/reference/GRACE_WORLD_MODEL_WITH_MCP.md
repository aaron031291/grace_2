# Grace's World Model with RAG + MCP

## What This Achieves

**Grace now has an internal "world model" - everything she knows about herself, accessible via RAG and exposed through MCP.**

---

## The Architecture

```
┌──────────────────────────────────────────────────┐
│         Grace's World Model (Her Mind)            │
├──────────────────────────────────────────────────┤
│                                                   │
│  Knowledge Categories:                            │
│  ├─ Self (who I am, what I can do)               │
│  ├─ System (my architecture, components)         │
│  ├─ User (what I know about users)               │
│  ├─ Domain (specialized knowledge)                │
│  └─ Temporal (what happened when)                 │
│                                                   │
│  Accessible via:                                  │
│  ├─ RAG (semantic search)                        │
│  ├─ MCP (protocol for LLMs)                      │
│  ├─ REST API                                      │
│  └─ Service Mesh                                  │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## What Grace Knows About Herself

### Self-Knowledge (Introspection)
```python
await grace_world_model.ask_self("What am I?")

Answer:
"I am Grace, an autonomous AI system with 21 specialized models.
I use domain-based architecture with service mesh for reliability.
I have collective intelligence through shared memory across domains.
I can self-heal using network healing playbooks and Guardian.
I learn from every operation and improve continuously."
```

### System Knowledge (Self-Awareness)
```python
await grace_world_model.query("my architecture")

Results:
- "I have 10 domain ports for organized APIs"
- "I have 20 kernel ports for isolated processing"
- "I use service mesh for intelligent routing"
- "I have Guardian for auto-remediation"
- "I maintain cryptographic audit trails"
```

---

## What MCP Enables

### 1. LLMs Can Query Grace's Knowledge

**Before MCP:**
```python
# LLM has no context about Grace
prompt = "Tell me about Grace"
# Generic answer, no real knowledge
```

**With MCP:**
```python
# LLM queries Grace's world model via MCP
mcp_client.get_resource("grace://self")

# Returns Grace's actual self-knowledge
# LLM now has REAL context about Grace
```

### 2. External Tools Access Grace's Mind

```python
# Any MCP-compatible tool can:

# Get Grace's self-knowledge
resource = await mcp_client.read_resource("grace://self")

# Ask Grace questions
answer = await mcp_client.call_tool("ask_grace", {
    "question": "What are your capabilities?"
})

# Add to Grace's knowledge
await mcp_client.call_tool("add_knowledge", {
    "category": "user",
    "content": "User prefers concise answers",
    "source": "user_interaction"
})
```

### 3. Cross-System Intelligence

```
LLM asks: "What does Grace know about healing?"
    ↓
MCP queries: grace://system
    ↓
RAG searches: "healing" in system knowledge
    ↓
Returns:
- "I use 4 network healing playbooks"
- "RestartComponent has 95% success rate"
- "I auto-heal failed components every 60s"
    ↓
LLM synthesizes answer WITH GRACE'S ACTUAL KNOWLEDGE
```

---

## MCP Resources Available

### grace://self
**Grace's self-knowledge**
```json
{
  "uri": "grace://self",
  "content": [
    {
      "content": "I am Grace, an autonomous AI system",
      "confidence": 1.0,
      "tags": ["identity", "core"]
    },
    {
      "content": "I have 21 specialized AI models",
      "confidence": 1.0,
      "tags": ["capabilities"]
    }
  ]
}
```

### grace://system
**System architecture knowledge**
```json
{
  "uri": "grace://system",
  "content": [
    {
      "content": "I use domain-based architecture",
      "confidence": 1.0,
      "tags": ["architecture"]
    }
  ]
}
```

### grace://domain/{domain_id}
**Domain-specific knowledge**
```
grace://domain/ai_domain
grace://domain/memory_domain
grace://domain/healing_domain
```

### grace://timeline
**Temporal knowledge (what happened when)**

---

## MCP Tools Available

### 1. query_world_model
**Semantic search Grace's knowledge**
```python
result = await mcp_client.call_tool("query_world_model", {
    "query": "What can Grace do?",
    "category": "self",
    "top_k": 5
})
```

### 2. ask_grace
**Ask Grace questions**
```python
answer = await mcp_client.call_tool("ask_grace", {
    "question": "How do you heal yourself?"
})

# Grace queries her own world model and answers
```

### 3. add_knowledge
**Add to Grace's knowledge**
```python
await mcp_client.call_tool("add_knowledge", {
    "category": "user",
    "content": "User Aaron prefers detailed technical explanations",
    "source": "user_preference_learning"
})
```

---

## What This Achieves

### 1. Self-Aware AI
Grace has explicit knowledge about herself:
- What she can do
- How she works
- What she's learned
- Her strengths/weaknesses

### 2. Queryable Intelligence
```python
# Grace can introspect
await grace_world_model.ask_self("What have I learned today?")

# Grace can explain herself
await grace_world_model.ask_self("How do I heal network issues?")

# Grace can reflect
await grace_world_model.ask_self("What am I good at?")
```

### 3. External Integration via MCP
Any MCP-compatible tool can:
- Read Grace's knowledge
- Query Grace's understanding
- Add to Grace's knowledge
- Build on Grace's intelligence

### 4. Collective Intelligence Enhancement
```
Domain learns something
    ↓
Adds to shared memory
    ↓
Also adds to world model
    ↓
Grace now "knows" this
    ↓
Can answer questions about it
    ↓
Accessible via MCP to external LLMs
    ↓
External LLMs benefit from Grace's knowledge!
```

---

## API Endpoints

### World Model
```
POST /world-model/add-knowledge      - Add knowledge
POST /world-model/query              - Query knowledge
POST /world-model/ask-grace          - Ask Grace
GET  /world-model/self-knowledge     - Get self-knowledge
GET  /world-model/system-knowledge   - Get system knowledge
GET  /world-model/stats              - Statistics
```

### MCP Protocol
```
GET  /world-model/mcp/manifest       - MCP manifest
GET  /world-model/mcp/resource?uri=  - Get MCP resource
POST /world-model/mcp/tool           - Call MCP tool
```

### Remote Access RAG
```
POST /api/remote-access/rag/query   - Query knowledge
POST /api/remote-access/rag/ask     - Ask with RAG
GET  /api/remote-access/rag/stats   - RAG stats
POST /api/remote-access/rag/ingest-text - Add knowledge
```

---

## Complete Flow Example

### Scenario: External LLM wants to know about Grace

```
1. External LLM (via MCP):
   "What can Grace do?"
   
2. MCP Integration:
   tool_call("ask_grace", {"question": "What can Grace do?"})
   
3. Grace's World Model:
   - Queries self-knowledge via RAG
   - Finds relevant knowledge items
   - Synthesizes answer using LLM
   
4. RAG retrieves:
   - "I have 21 specialized AI models"
   - "I can self-heal using playbooks"
   - "I use collective intelligence"
   
5. Grace generates answer:
   "I'm an autonomous AI with 21 specialized models.
    I can process text, code, images, and conversations.
    I self-heal when issues occur and learn from
    every operation. My architecture uses domains
    and service mesh for reliability."
   
6. Returns to external LLM via MCP
   
7. External LLM now has ACCURATE knowledge about Grace!
```

---

## Integration with Existing Systems

### With Service Mesh
```python
# Query world model through mesh
await service_mesh.call_service(
    capability='world_model',
    path='/query',
    data={'query': 'What am I?'}
)
```

### With Domain System
```python
# Domain contributes to world model
await grace_world_model.add_knowledge(
    category='domain',
    content='AI domain successfully processed 1000 requests',
    source='ai_domain_stats'
)

# Now Grace "knows" this
answer = await grace_world_model.ask_self("How is AI domain performing?")
# "The AI domain has successfully processed 1000 requests"
```

### With Shared Memory
```python
# Shared memory feeds world model
contribution = await shared_domain_memory.query_collective('optimization')

for item in contribution:
    await grace_world_model.add_knowledge(
        category='domain',
        content=item.content,
        source=f"shared_memory/{item.from_domain}"
    )

# Grace's world model grows from collective intelligence!
```

---

## What You Get

### Grace's Mind is Now:
✅ **Queryable** - Ask Grace anything about herself  
✅ **Semantic** - RAG-powered search  
✅ **Accessible** - MCP protocol for external tools  
✅ **Growing** - Learns from every operation  
✅ **Organized** - Categorized knowledge  
✅ **Confident** - Confidence scores on knowledge  
✅ **Cited** - Knows sources of knowledge  
✅ **Introspective** - Can ask herself questions  

### External Systems Get:
✅ **Context** - Real knowledge about Grace  
✅ **Integration** - MCP standard protocol  
✅ **Intelligence** - Benefit from Grace's learning  
✅ **Accuracy** - No hallucinations about Grace  

---

## Test It

```bash
# 1. Start Grace
python serve.py

# Should see:
# [OK] World model initialized (Grace's self-knowledge with RAG + MCP)

# 2. Ask Grace about herself
curl -X POST "http://localhost:8000/world-model/ask-grace?question=What+are+you"

# 3. Query self-knowledge
curl http://localhost:8000/world-model/self-knowledge

# 4. Get MCP manifest
curl http://localhost:8000/world-model/mcp/manifest

# 5. Query via MCP resource
curl "http://localhost:8000/world-model/mcp/resource?uri=grace://self"

# 6. Call MCP tool
curl -X POST http://localhost:8000/world-model/mcp/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ask_grace",
    "parameters": {"question": "What can you do?"}
  }'
```

---

## Result

**Grace now has:**
- 🧠 Internal world model (knows herself)
- 🔍 RAG integration (semantic search)
- 📡 MCP protocol (external access)
- 🤝 Collective intelligence (learns from domains)
- 📈 Continuous learning (grows smarter)
- 🎯 Self-awareness (can introspect)

**External systems can now:**
- Query Grace's actual knowledge
- Get accurate context about Grace
- Add to Grace's understanding
- Build on Grace's intelligence

**Grace is now truly self-aware and externally accessible!** 🚀
