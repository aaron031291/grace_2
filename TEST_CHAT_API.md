# Testing the Updated /api/chat Endpoint

## ✅ Changes Made

The `/api/chat` endpoint now:
1. ✅ Calls `generate_grace_response()` with OpenAI integration
2. ✅ Retrieves RAG context from vector store (top 5 relevant documents)
3. ✅ Queries world model for canonical facts (top 3 knowledge items)
4. ✅ Returns `{ reply, actions, confidence, citations }` format
5. ✅ Handles errors gracefully with logging
6. ✅ Returns friendly error messages when API key is not configured

## 🧪 How to Test

### Step 1: Ensure OpenAI API Key is Set

```bash
# Check if .env file has OPENAI_API_KEY
type .env | findstr OPENAI_API_KEY
```

If not set, follow instructions in [SETUP_OPENAI_KEY.md](file:///c:/Users/aaron/grace_2/SETUP_OPENAI_KEY.md)

### Step 2: Start the Grace Server

```bash
python server.py
```

Wait for:
```
[INFO] Server running on http://localhost:8000
```

### Step 3: Test from Command Line

**Using curl (if installed):**
```bash
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"hi grace\"}"
```

**Using Python test script:**
```bash
python test_chat_endpoint.py
```

### Step 4: Test from Frontend UI

1. Start frontend:
```bash
cd frontend
npm run dev
```

2. Open http://localhost:5173

3. Type in chat: `hi grace`

4. You should see:
   - ✅ Response from OpenAI (gpt-4o)
   - ✅ Confidence score
   - ✅ Citations (if RAG context was used)
   - ✅ Any proposed actions

## 📊 Expected Response Format

```json
{
  "reply": "Hello! I'm Grace, your AI assistant...",
  "response": "Hello! I'm Grace, your AI assistant...",
  "actions": [],
  "confidence": 0.85,
  "citations": [],
  "requires_approval": false,
  "model": "gpt-4o",
  "timestamp": "2025-11-18T..."
}
```

## 🔧 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `reply` | string | The main response text from OpenAI |
| `response` | string | Backward compatibility alias for `reply` |
| `actions` | array | Proposed actions (e.g., file operations, API calls) |
| `confidence` | float | Confidence score (0.0-1.0) based on RAG quality and hedging |
| `citations` | array | Source citations from RAG context |
| `requires_approval` | bool | Whether actions need user approval |
| `model` | string | OpenAI model used (e.g., "gpt-4o") |
| `timestamp` | string | ISO timestamp of response |

## 🐛 Error Handling

If OpenAI API key is not configured:
```json
{
  "reply": "I'm having trouble processing your request right now. Please make sure your OpenAI API key is configured in the .env file.",
  "actions": [],
  "confidence": 0.0,
  "citations": [],
  "error": "OPENAI_API_KEY not set",
  "timestamp": "..."
}
```

## 🔍 How RAG + World Model Works

### RAG Context Retrieval
```python
# Searches vector store for semantically similar content
rag_result = await rag_service.retrieve(
    query=message,
    top_k=5,  # Top 5 most relevant docs
    similarity_threshold=0.6
)
```

### World Model Query
```python
# Queries curated knowledge base
knowledge_items = await world_model.query(message, top_k=3)
# Returns canonical facts about Grace's systems
```

### Context Injection
Both RAG and world model results are injected into the OpenAI prompt:
- RAG docs appear as "RETRIEVED KNOWLEDGE"
- World model facts appear as "WORLD MODEL FACTS (canonical, verified)"

This grounds the response in Grace's actual knowledge!

## ✅ Verification Checklist

- [ ] Server starts without errors
- [ ] `/api/chat` endpoint responds
- [ ] OpenAI is called (check logs)
- [ ] RAG context is retrieved (check logs)
- [ ] World model is queried (check logs)
- [ ] Response includes `reply`, `confidence`, `citations`
- [ ] Frontend chat panel displays the response
- [ ] Error handling works when API key missing

## 🎯 Next Steps

After verifying the endpoint works:

1. **Add conversation history** - Track multi-turn conversations
2. **Implement action execution** - Execute approved actions through Action Gateway
3. **Add streaming responses** - For better UX with long responses
4. **Improve RAG filtering** - Use metadata filters for context-aware retrieval
5. **Add trust scoring** - Integrate with trust framework for confidence calibration

---

**Implementation Complete!** ✅

The chat endpoint now uses OpenAI with RAG and world-model grounding.
