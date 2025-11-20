# Screen Share Learning System - Complete ✅

## Overview

Grace can now learn from your screen in real-time! The screen share system includes:
- **Frame Capture** - Periodic screenshot capture
- **Vision Pipeline** - OCR text extraction + metadata
- **Learning Integration** - Auto-ingest to RAG + World Model
- **Governance Controls** - Approve sensitive content before storing
- **Multiple Modes** - Learn / Observe / Consent Required
- **Persistent Toggle** - One-click on/off with mode selection

---

## 🎯 How It Works

### Learning Pipeline for Screen Shares

```
User Starts Screen Share (Learn Mode)
           ↓
Frame Captured Every 5 Seconds
           ↓
┌──────────────────────────────────┐
│      Vision Pipeline             │
├──────────────────────────────────┤
│ 1. OCR Text Extraction           │
│    - Extract visible text        │
│    - Window titles, app names    │
│    - URLs, form content          │
│                                  │
│ 2. Metadata Extraction           │
│    - App name (Chrome, VS Code)  │
│    - Window title (CRM Dashboard)│
│    - URL (https://...)           │
│    - Timestamp + Frame ID        │
│                                  │
│ 3. Sensitive Content Check       │
│    - Scan for PII, passwords     │
│    - Check for financial data    │
│    - Detect credentials          │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│     Governance Check             │
├──────────────────────────────────┤
│ IF mode = learn:                 │
│   IF sensitive detected:         │
│     → Queue for approval         │
│     → Send notification          │
│   ELSE:                          │
│     → Ingest immediately         │
│                                  │
│ IF mode = observe_only:          │
│   → Capture but DON'T store      │
│                                  │
│ IF mode = consent_required:      │
│   → Always queue for approval    │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│    Learning Ingestion            │
├──────────────────────────────────┤
│ 1. Store in RAG (searchable)     │
│    - Generate embeddings         │
│    - Store with provenance       │
│    - Source: "ScreenShare: ..."  │
│                                  │
│ 2. Update World Model            │
│    - Add knowledge entry         │
│    - Category: screen_share      │
│    - Confidence: 0.85            │
│                                  │
│ 3. Log to Insights Table         │
│    - Track what was captured     │
│    - Store metadata              │
│    - Record timestamp            │
└──────────────────────────────────┘
           ↓
Grace Can Now Answer Questions About Screen Content! ✅
```

---

## 🎮 User Interface

### Screen Share Button with Modes

#### Step 1: Click to Select Mode

When you click **📺 Screen Share**, a mode selector appears:

```
┌─────────────────────────────────┐
│ Choose Mode:                    │
├─────────────────────────────────┤
│  🧠 Learn                       │
│  Capture and store in memory    │
├─────────────────────────────────┤
│  👁️ Observe Only                │
│  Show but don't save            │
├─────────────────────────────────┤
│  🔐 Consent Required            │
│  Prompt before storing          │
│  sensitive content              │
├─────────────────────────────────┤
│         Cancel                  │
└─────────────────────────────────┘
```

#### Step 2: Mode Selected, Sharing Starts

Button updates to show active state:

```
📺 Sharing
Session: screen_5f6
🧠 Learned 12 frames
```

#### Step 3: Click Again to Stop

Screen share ends, stats shown in chat:
```
📺 Screen share ended. Grace learned from 47 of 52 captured frames.
```

---

## 📖 Mode Descriptions

### 🧠 Learn Mode (Default)

**What it does:**
- Captures frames every 5 seconds
- Extracts text via OCR
- Stores in RAG (searchable)
- Updates world model
- Records provenance

**Use when:**
- You want Grace to learn from what you show
- Content is not sensitive
- You want to be able to ask about it later

**Example:**
```
Show Grace a CRM dashboard
→ Grace captures sales pipeline data
→ Later ask: "What's the status of the Acme Corp deal?"
→ Grace knows: "Deal Value: $125,000, Stage: Proposal Sent"
```

---

### 👁️ Observe Only Mode

**What it does:**
- Captures frames but doesn't store
- No learning integration
- No memory persistence
- Temporary observation only

**Use when:**
- Showing sensitive information
- Demonstrating something temporarily
- Don't want it saved to memory

**Example:**
```
Show Grace a live customer support call
→ Grace sees it in real-time
→ Can respond based on current view
→ After session ends, nothing is stored
```

---

### 🔐 Consent Required Mode

**What it does:**
- Captures frames
- Detects sensitive content
- Prompts for approval before storing
- Only learns from approved frames

**Use when:**
- Might show sensitive data intermittently
- Want granular control
- Need to review before learning

**Example:**
```
Show Grace slides with some confidential sections
→ Grace detects "CONFIDENTIAL" watermark
→ Chat notification: "Screen capture needs approval"
→ You review: Slide 3 has sensitive data
→ Approve slides 1, 2, 4, 5
→ Reject slide 3
→ Grace learns from approved slides only
```

---

## 🔒 Governance & Privacy

### Sensitive Content Detection

Automatically detects:
- **PII**: Names, emails, phone numbers, SSN
- **Financial**: Credit cards, account numbers, salaries
- **Credentials**: Passwords, API keys, tokens
- **Proprietary**: Confidential, secret, internal

### Approval Workflow

```
Frame Captured
     ↓
Sensitive Content Detected
     ↓
Queue for Approval
     ↓
Send Notification:
"🔐 Screen capture needs approval - contains sensitive data"
     ↓
Show in Chat with Preview
     ↓
User Reviews Preview
     ↓
┌─────────────────────┐
│ Preview: "password: │
│ [REDACTED]..."      │
├─────────────────────┤
│ ✅ Approve  ❌ Reject│
└─────────────────────┘
     ↓
If Approved:
  → Ingest to learning systems
  → Frame learned count increments
  → Chat: "✅ Screen capture approved and learned"

If Rejected:
  → Frame discarded
  → Not stored anywhere
  → Chat: "❌ Screen capture rejected"
```

---

## 📊 What Gets Captured

### Text Extraction (OCR)

Grace extracts all visible text from:
- Documents and PDFs
- Spreadsheets and tables
- Web pages and forms
- Slides and presentations
- Code editors
- Terminal/console output

**Example - CRM Dashboard:**
```
Extracted Text:
"Q4 Sales Pipeline - Active Deals
 Customer: Acme Corp
 Deal Value: $125,000
 Stage: Proposal Sent
 Close Date: Dec 15, 2025"

Stored in RAG as:
Source: "ScreenShare: CRM Dashboard - Salesforce @ 2025-11-18 15:32"
```

### Metadata Extraction

For each frame, Grace captures:
- **Window Title**: "CRM Dashboard - Salesforce"
- **App Name**: "Google Chrome"
- **URL**: "https://crm.example.com/dashboard" (if browser)
- **Timestamp**: "2025-11-18T15:32:45"
- **Frame ID**: "screen_5f6g7h8i_abc123"
- **Resolution**: 1920x1080

---

## 🎯 Use Cases

### Use Case 1: Learn from Presentations

```bash
# Scenario: Show Grace a PowerPoint presentation

1. Open PowerPoint with product roadmap
2. Click "📺 Screen Share" → "🧠 Learn"
3. Navigate through slides
4. Grace captures each slide
5. Stop screen share

# Result:
- Grace learned roadmap timeline
- Grace knows Q1 2026 initiatives
- Can ask: "What's planned for Q1?"
- Grace responds with extracted slide content
```

### Use Case 2: Capture Customer Interactions

```bash
# Scenario: Show Grace a customer support session

1. Open support ticket in CRM
2. Click "📺 Screen Share" → "👁️ Observe Only"
3. Review customer issue
4. Grace sees context in real-time
5. Can help craft response
6. Stop screen share

# Result:
- Grace helped during session
- Nothing stored after session ends
- Customer privacy protected
```

### Use Case 3: Selective Learning

```bash
# Scenario: Review docs with some confidential sections

1. Open document with mixed content
2. Click "📺 Screen Share" → "🔐 Consent Required"
3. Scroll through document
4. Grace detects page 3 has "CONFIDENTIAL"
5. Chat: "🔐 Screen capture needs approval"
6. Review preview, reject page 3
7. Approve other pages

# Result:
- Grace learned from public pages
- Confidential content not stored
- Full control over what gets saved
```

### Use Case 4: Live Coding Session

```bash
# Scenario: Show Grace how to use an API

1. Open VS Code with API example
2. Click "📺 Screen Share" → "🧠 Learn"
3. Write code, add comments
4. Run tests, show output
5. Grace captures code + terminal output
6. Stop screen share

# Result:
- Grace learned API usage patterns
- Can reference your code examples
- Ask: "How did I use that API?"
- Grace shows code from screen capture
```

---

## 🔔 Notifications

All screen share events appear in chat:

### Session Started
```
📺 Screen share session started 🧠 (capturing and learning)
Session ID: screen_5f6g7h8i
```

### Frame Approval Needed
```
🔐 Screen capture needs approval - contains sensitive data

Preview: "Customer email: john.doe@example.com..."

[✅ Approve] [❌ Reject]
```

### Frame Approved
```
✅ Screen capture approved and learned
Frame ID: screen_5f6g7h8i_abc123
```

### Session Stopped
```
📺 Screen share ended. Grace learned from 47 of 52 captured frames.

What Grace learned:
- 47 text extractions
- 47 world model facts
- 3 sensitive frames rejected
```

---

## 🧪 Testing Guide

### Test Learn Mode

```bash
# 1. Start screen share in learn mode
Click "📺 Screen Share"
Select "🧠 Learn"

# 2. Open a document with text
Open a text file or web page with visible content

# 3. Wait 10 seconds
# Grace captures 2 frames (every 5 seconds)

# 4. Stop screen share
Click button again

# 5. Verify learning
# Open "📁 Files" → Check ingestion panel
# Should see screen captures being processed

# 6. Query in chat
Ask: "What was on my screen?"
Grace should mention content from captured frames
```

### Test Observe-Only Mode

```bash
# 1. Start in observe mode
Click "📺 Screen Share"
Select "👁️ Observe Only"

# 2. Show content
Open any document

# 3. Stop screen share

# 4. Verify NOT learned
Ask: "What was on my screen?"
Grace should say: "I don't have information about that"
```

### Test Consent Required Mode

```bash
# 1. Start with consent mode
Click "📺 Screen Share"
Select "🔐 Consent Required"

# 2. Show document with "password" text
Open a file containing sensitive keywords

# 3. Check for approval notification
Should see in chat:
"🔐 Screen capture needs approval - contains sensitive data"

# 4. Approve the frame
# (Would click approve button in notification)

# 5. Verify learning
Content should now be in RAG/world model
```

---

## 🛠️ API Reference

### Start Screen Share
```
POST /api/screen_share/start
```

**Request:**
```json
{
  "user_id": "user",
  "quality": "medium",
  "mode": "learn"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "screen_5f6g7h8i",
  "status": "active",
  "stream_url": "/stream/screen_5f6g7h8i",
  "quality": "medium",
  "mode": "learn",
  "learning_enabled": true
}
```

### Stop Screen Share
```
POST /api/screen_share/stop
```

**Request:**
```json
{
  "session_id": "screen_5f6g7h8i"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "screen_5f6g7h8i",
  "status": "stopped",
  "frames_captured": 52,
  "frames_learned": 47,
  "duration_seconds": 260.0
}
```

### Get Screen Share Status
```
GET /api/screen_share/status/{session_id}
```

**Response:**
```json
{
  "session_id": "screen_5f6g7h8i",
  "status": "active",
  "mode": "learn",
  "frames_captured": 12,
  "frames_learned": 10,
  "pending_approvals": 2,
  "learning_enabled": true,
  "duration_seconds": 60.0
}
```

### Approve Frame
```
POST /api/screen_share/approve/{session_id}/{approval_id}
```

**Response:**
```json
{
  "success": true,
  "approved": true,
  "frame_id": "screen_5f6g7h8i_abc123"
}
```

---

## 🔄 Learning Flow

### Frame → RAG Storage

```python
# Text extracted from screen
text = "Q4 Sales Pipeline - Active Deals..."

# Generate embedding
embedding = await embedding_service.embed_text(text)

# Store in vector database
await vector_store.store(
    text=text,
    embedding=embedding,
    metadata={
        'source': 'ScreenShare: CRM Dashboard @ 2025-11-18 15:32',
        'source_type': 'screen_share',
        'window_title': 'CRM Dashboard - Salesforce',
        'captured_at': '2025-11-18T15:32:45'
    }
)
```

### Frame → World Model

```python
# Add knowledge entry
await world_model.add_knowledge(
    content="Screen capture: Q4 Sales Pipeline data...",
    source="ScreenShare: CRM Dashboard @ 2025-11-18 15:32",
    category="screen_share",
    confidence=0.85
)
```

### Frame → Insights Table

```python
# Log capture event
table_registry.insert_row('memory_insights', {
    'insight_type': 'screen_capture',
    'source': 'ScreenShare: CRM Dashboard @ 2025-11-18 15:32',
    'content': 'Captured screen: CRM Dashboard',
    'metadata': {
        'session_id': 'screen_5f6g7h8i',
        'frame_id': 'abc123',
        'text_length': 567,
        'window_metadata': {...}
    }
})
```

---

## 💡 Provenance Tracking

Every screen capture is tracked with full provenance:

### Source Format

```
ScreenShare: {Window Title} @ {Timestamp}
```

**Examples:**
- `ScreenShare: CRM Dashboard - Salesforce @ 2025-11-18 15:32`
- `ScreenShare: Product Roadmap.pptx @ 2025-11-18 16:45`
- `ScreenShare: GitHub - sourcegraph/grace @ 2025-11-18 17:20`

### Metadata Stored

```json
{
  "source": "ScreenShare: ...",
  "source_type": "screen_share",
  "session_id": "screen_5f6g7h8i",
  "user_id": "user",
  "frame_id": "abc123",
  "window_title": "CRM Dashboard - Salesforce",
  "app_name": "Google Chrome",
  "url": "https://crm.example.com/dashboard",
  "timestamp": "2025-11-18T15:32:45",
  "resolution": {"width": 1920, "height": 1080}
}
```

### Query by Source

```python
# Later, you can ask Grace:
"What did you see in my CRM?"

# Grace queries RAG:
rag_service.retrieve(
    query="CRM dashboard",
    filters={'source_type': 'screen_share'}
)

# Returns chunks with full provenance
```

---

## 🎨 UI States

### Button States

```
📺 Screen Share           (Not sharing)
     ↓ [Click]
Mode Selector Appears
     ↓ [Select "🧠 Learn"]
⏳ Starting...           (Starting)
     ↓
📺 Sharing               (Active - Learn mode)
Session: screen_5f6
🧠 Learned 12 frames
     ↓ [Click]
⏳ Stopping...           (Stopping)
     ↓
📺 Screen Share          (Back to default)
```

### Mode Indicator Icons

```
🧠 = Learn mode (actively storing)
👁️ = Observe mode (not storing)
🔐 = Consent mode (selective storage)
📺 = Generic screen share
⏳ = Loading/processing
✅ = Frame approved
❌ = Frame rejected
```

---

## 🧪 End-to-End Test

### Complete Learning Test

```bash
# 1. Prepare test content
echo "Grace is learning from screen shares" > test_screen_content.txt
Open test_screen_content.txt in Notepad

# 2. Start screen share
Click "📺 Screen Share"
Select "🧠 Learn"
Wait for "📺 Sharing" state

# 3. Let Grace capture (wait 15 seconds)
# Should capture 3 frames

# 4. Stop screen share
Click button again
Check chat notification:
"📺 Screen share ended. Grace learned from 3 of 3 captured frames."

# 5. Verify learning
Ask in chat: "What did you see on my screen?"

Expected response:
"I saw content about screen share learning. 
 The text mentioned 'Grace is learning from screen shares.'
 Source: ScreenShare: test_screen_content.txt - Notepad @ [timestamp]"

# 6. Check provenance
Open "📁 Files" → Find ingestion with source "ScreenShare:..."
```

---

## ⚙️ Configuration

### Capture Settings

```python
# Frame capture interval
capture_interval = 5.0  # seconds

# Quality settings
quality_config = {
    'low': {'fps': 0.1, 'resolution': (1280, 720)},
    'medium': {'fps': 0.2, 'resolution': (1920, 1080)},
    'high': {'fps': 0.5, 'resolution': (2560, 1440)}
}
```

### Storage Paths

```python
# Frame storage
frame_storage_path = Path("storage/screen_captures")

# Organized by:
# storage/screen_captures/{session_id}/{frame_id}.png
```

### Trust Scoring

```python
# Screen share content gets medium confidence
confidence = 0.85  # 85% trust

# Approved frames get higher confidence
approved_confidence = 0.90  # 90% trust

# Rejected frames are not stored
```

---

## ✅ Verification Checklist

Backend:
- [x] Screen capture service with frame loop
- [x] OCR text extraction
- [x] Metadata extraction
- [x] Sensitive content detection
- [x] Governance approval queue
- [x] Learning pipeline integration
- [x] RAG storage with provenance
- [x] World model updates
- [x] Notification integration

Frontend:
- [x] Mode selector UI
- [x] Persistent toggle button
- [x] Learn/Observe/Consent modes
- [x] Status display (frames learned)
- [x] Approval UI (in chat)
- [x] Session stats on stop
- [x] Error handling

Integration:
- [x] Frames flow to RAG
- [x] Content queryable in chat
- [x] Provenance tracked
- [x] Sensitive content gated
- [x] Notifications appear in chat

---

**🎉 Screen Share Learning is Complete!**

Anything you show Grace can now feed her learning loop automatically - just like uploading a document!

**Test it:** Start screen share in Learn mode, show Grace some content, then ask about it in chat. She'll know! 🧠
