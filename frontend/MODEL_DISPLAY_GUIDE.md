# Model Metadata Display - Implementation Guide

## 🎯 How Model Info Flows

```
Backend                          Frontend
────────────────────────────────────────────────────────

1. User sends message
                    ──────────►
                                2. Task type detected
                                   (coding, reasoning, etc.)

3. Orchestrator selects model
   (deepseek for coding, etc.)

4. Model generates response

5. Return with metadata:
   {
     "response": "...",
     "model_used": "qwen2.5:32b",  ✅
     "task_type": "reasoning",
     "reasoning_steps": [...],
     "citations": [...]
   }
                    ◄──────────
                                6. Display in UI:
                                   - Message content
                                   - Model badge
                                   - Reasoning steps
                                   - Citations
                                   - Feedback buttons
```

---

## ✅ Backend Implementation

### Step 1: Update Chat Response Schema

**File:** `backend/routes/chat.py`

```python
class ChatResponse(BaseModel):
    response: str
    model_used: str = None  # ✅ ADD THIS
    task_type: str = "general"
    reasoning_steps: list = []
    citations: list = []
    metadata: dict = {}
```

### Step 2: Include Model in Response

```python
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    from backend.model_orchestrator import model_orchestrator
    
    # Select model
    task_type = req.get("task_type", "general")
    selected_model = model_orchestrator.select_model_for_task(task_type)
    
    # Generate response
    response_text = await model_orchestrator.generate(
        model=selected_model,
        prompt=req.message
    )
    
    # ✅ Return with model info
    return ChatResponse(
        response=response_text,
        model_used=selected_model,  # ✅ INCLUDE THIS
        task_type=task_type
    )
```

### Step 3: Handle Fallbacks

```python
# If model not loaded
if not is_model_loaded(selected_model):
    fallback = get_fallback_model(task_type)
    print(f"[CHAT] Using fallback: {fallback}")
    selected_model = fallback

# Return which model was actually used
return ChatResponse(
    response=response_text,
    model_used=selected_model,  # Actual model used (may be fallback)
    metadata={
        "requested_model": original_model,
        "fallback_used": selected_model != original_model
    }
)
```

---

## ✅ Frontend Display

### Already Implemented in ChatPane.improved.tsx

**Message Header:**
```tsx
<div className="message-header">
  <span className="message-author">Grace</span>
  
  {/* ✅ Model badge */}
  {message.metadata?.model_used && (
    <span className="model-badge">
      🤖 {message.metadata.model_used}
    </span>
  )}
  
  <span className="message-time">10:30 AM</span>
</div>
```

**Visual Result:**
```
┌────────────────────────────────────┐
│ Grace    🤖 qwen2.5:32b    10:30 AM │
├────────────────────────────────────┤
│ Here's my analysis of the code...  │
└────────────────────────────────────┘
```

### Model Icon by Type

```typescript
function getModelIcon(type: string): string {
  return {
    'coding': '💻',
    'reasoning': '🧠',
    'long-context': '📄',
    'vision': '👁️',
    'general': '🤖',
  }[type] || '🤖';
}

// Usage:
<span className="model-badge">
  {getModelIcon(modelType)} {modelName}
</span>
```

**Result:**
```
💻 deepseek-coder-v2:16b  (for coding)
🧠 qwen2.5:32b            (for reasoning)
👁️ llava:34b              (for vision)
```

---

## 🎯 Complete Example

### Backend Response

```json
{
  "response": "The function has a potential race condition...",
  "model_used": "deepseek-coder-v2:16b",
  "task_type": "review",
  "reasoning_steps": [
    "Analyzed variable access patterns",
    "Identified shared state without locks",
    "Checked for data races"
  ],
  "citations": [
    {
      "type": "code",
      "id": "file:///src/app.py",
      "title": "app.py line 45"
    }
  ],
  "metadata": {
    "model_selection": "auto",
    "confidence": 0.92,
    "alternative_models": ["qwen2.5:32b"]
  }
}
```

### Frontend Display

```tsx
┌──────────────────────────────────────────────────┐
│ Grace    💻 deepseek-coder-v2:16b    10:30 AM    │
├──────────────────────────────────────────────────┤
│ The function has a potential race condition...   │
│                                                   │
│ 🧠 Reasoning Steps ▼                             │
│   1. Analyzed variable access patterns           │
│   2. Identified shared state without locks       │
│   3. Checked for data races                      │
│                                                   │
│ References:                                       │
│ [💻 app.py line 45]                              │
│                                                   │
│ Was this helpful? [👍] [👎]                      │
└──────────────────────────────────────────────────┘
```

---

## 📋 Integration Checklist

### Backend Changes

**File:** `backend/routes/chat.py`

- [ ] Import model_orchestrator
- [ ] Detect task_type from request
- [ ] Call select_model_for_task()
- [ ] Generate with selected model
- [ ] Include model_used in response
- [ ] Add reasoning_steps if available
- [ ] Add citations if any

**Example:**
```python
from backend.model_orchestrator import model_orchestrator

selected_model = model_orchestrator.select_model_for_task(
    task_type=req.task_type or "general"
)

response = await model_orchestrator.generate(
    model=selected_model,
    prompt=req.message
)

return {
    "response": response,
    "model_used": selected_model,  # ✅
}
```

### Frontend Changes

**File:** `frontend/src/main.tsx`

- [x] ✅ Wrap in ChatProvider (already done)

**File:** `frontend/src/panels/ChatPane.tsx`

- [ ] Use ChatPane.improved.tsx version
- [x] ✅ Display model badge (implemented)
- [x] ✅ Show reasoning steps (implemented)
- [x] ✅ Feedback buttons (implemented)

**To apply:**
```bash
cd frontend/src/panels
copy /Y ChatPane.improved.tsx ChatPane.tsx
```

---

## 🎨 UI Examples

### Model Badge Styles

**CSS already includes:**
```css
.model-badge {
  padding: 0.25rem 0.625rem;
  background: rgba(0, 204, 255, 0.15);
  border: 1px solid rgba(0, 204, 255, 0.3);
  border-radius: 12px;
  font-size: 0.7rem;
  color: #00ccff;
  font-weight: 500;
}
```

**Visual:**
```
🤖 qwen2.5:32b     (cyan badge)
💻 deepseek-coder  (cyan badge)
🧠 qwen2.5:32b     (cyan badge)
👁️ llava:34b       (cyan badge)
```

### Reasoning Steps Display

**CSS:**
```css
.reasoning-steps {
  margin-top: 0.75rem;
  padding: 0.875rem;
  background: rgba(0, 255, 136, 0.05);
  border: 1px solid rgba(0, 255, 136, 0.2);
  border-radius: 6px;
}

.reasoning-steps summary {
  cursor: pointer;
  color: #00ff88;
}
```

**Visual:**
```
🧠 Reasoning Steps ▼
  1. Analyzed the problem
  2. Considered edge cases
  3. Generated solution
```

---

## 🧪 Testing Model Display

### Test 1: Model Badge Shows

```
1. Send message: "Review this code"
2. Wait for response
3. Check message header
4. Should see: 🤖 deepseek-coder-v2:16b
✓ Model badge displayed
```

### Test 2: Model Selection Works

```
1. Select task type: "Coding"
2. Select model: "Auto-select"
3. Send coding question
4. Response should use coding model
5. Badge shows: 💻 deepseek-coder
✓ Auto-selection works
```

### Test 3: Manual Override

```
1. Select model: "qwen2.5:32b"
2. Send coding question
3. Badge should show: 🧠 qwen2.5:32b
✓ Override works
```

### Test 4: Fallback Display

```
1. Select unavailable model
2. Send message
3. Badge shows fallback model
4. Metadata shows: "fallback_used": true
✓ Fallback transparent
```

---

## 🎯 Quick Integration

### Apply to Your Backend

**Edit:** `backend/routes/chat.py`

```python
# Add at top
from backend.model_orchestrator import model_orchestrator

# In chat_endpoint function, before return:
selected_model = model_orchestrator.select_model_for_task(
    task_type=request.get("task_type", "general")
)

# In return statement:
return ChatResponse(
    response=result,
    model_used=selected_model  # ✅ ADD THIS LINE
)
```

### Apply to Your Frontend

**Already done!** Just use the improved version:

```bash
cd frontend/src/panels
copy /Y ChatPane.improved.tsx ChatPane.tsx
```

---

## 📊 Data Flow Example

### User Message
```json
POST /api/chat
{
  "message": "Explain async/await in Python",
  "task_type": "reasoning"
}
```

### Backend Processing
```
1. Receive request
2. Detect task_type: "reasoning"
3. Select model: qwen2.5:32b (reasoning specialist)
4. Check loaded: Yes ✓
5. Generate response
6. Extract reasoning steps
7. Build response
```

### Backend Response
```json
{
  "response": "Async/await in Python...",
  "model_used": "qwen2.5:32b",
  "task_type": "reasoning",
  "reasoning_steps": [
    "Analyzed async fundamentals",
    "Compared to traditional threading",
    "Identified key concepts"
  ],
  "metadata": {
    "model_selection": "auto",
    "confidence": 0.91
  }
}
```

### Frontend Display
```
┌────────────────────────────────────┐
│ Grace  🧠 qwen2.5:32b   10:30 AM   │
├────────────────────────────────────┤
│ Async/await in Python...           │
│                                     │
│ 🧠 Reasoning Steps ▼               │
│   1. Analyzed async fundamentals   │
│   2. Compared to threading         │
│   3. Identified key concepts       │
│                                     │
│ Was this helpful? [👍] [👎]        │
└────────────────────────────────────┘
```

---

## 🎉 Summary

✅ **Backend:** Return `model_used` in all responses  
✅ **Frontend:** Display model badge in message header  
✅ **Icons:** Match model type (💻🧠👁️📄🤖)  
✅ **Reasoning:** Show steps if complex  
✅ **Feedback:** Track model performance  
✅ **Transparency:** Users know which AI answered  

**Complete model transparency implemented!** 🚀

**Frontend is ready - just needs backend to return `model_used` field!**
