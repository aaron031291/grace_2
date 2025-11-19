# Intelligent File Learning System ✅

## Overview

Grace's file system now includes intelligent learning capabilities:
- **"What did you learn?"** - Query what Grace extracted from any file
- **Quick Actions** - One-click operations (whitelist, mark sensitive, sandbox test, re-train)
- **Trust Scoring** - Automatic trust level assignment
- **Inline Knowledge Display** - See learned facts, RAG chunks, and insights

---

## 🧠 "What Did You Learn?" Feature

### How It Works

When you upload a file, Grace automatically:
1. Extracts text content
2. Generates embeddings
3. Stores in RAG (searchable chunks)
4. Creates world model facts
5. Logs insights to tables

You can then ask **"What did Grace learn from this file?"** to see everything.

### Using the Feature

#### In File Explorer

1. **Upload a document**
   ```
   Drag doc.txt into File Explorer
   Wait for ingestion to complete (100%)
   ```

2. **Click "🧠 What Learned?"**
   ```
   Select the file in tree view
   Click "🧠 What Learned?" button in preview header
   ```

3. **View Results**
   ```
   See inline display with:
   - Summary (total items learned)
   - World Model Facts (with confidence scores)
   - RAG Documents (searchable chunks)
   - Table Entries (structured insights)
   ```

#### Example Response

```
🧠 What Grace Learned

Grace learned 12 things from this file: 5 facts, 4 document chunks, 3 insights

💡 World Model Facts (5)
┌─────────────────────────────────────────┐
│ User uploaded file: sales_report.pdf    │
│ Confidence: 90% | Category: document    │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ File whitelisted: sales_report.pdf      │
│ Confidence: 100% | Category: trust      │
└─────────────────────────────────────────┘

📚 RAG Documents (4)
┌─────────────────────────────────────────┐
│ Q4 sales exceeded targets by 15%...     │
│ Trust: 85%                              │
└─────────────────────────────────────────┘

📊 Table Entries (3)
┌─────────────────────────────────────────┐
│ File uploaded and learned: sales...     │
│ Type: file_upload                       │
└─────────────────────────────────────────┘
```

---

## ⚡ Quick Actions

Quick actions provide one-click operations on files to integrate them into Grace's learning workflow.

### Available Actions

#### 1. ✅ Whitelist

**Purpose**: Mark file as trusted source

**What It Does:**
- Adds file to trusted sources in world model
- Sets confidence = 100%
- Future content from this file will be highly trusted
- Useful for official documents, verified sources

**Usage:**
```
1. Select file in File Explorer
2. Click "✅ Whitelist" in quick actions bar
3. Confirmation: "Added [file] to whitelist"
```

**Backend Effect:**
```json
{
  "content": "File whitelisted: company_policy.pdf",
  "source": "whitelist:storage/company_policy.pdf",
  "category": "trust",
  "confidence": 1.0
}
```

---

#### 2. 🔒 Mark Sensitive

**Purpose**: Flag files containing sensitive data

**What It Does:**
- Records sensitivity in world model
- Prompts for reason (e.g., "Contains PII", "Financial data")
- Grace will handle with extra caution
- Useful for compliance, privacy

**Usage:**
```
1. Select file
2. Click "🔒 Mark Sensitive"
3. Enter reason in prompt
4. Confirmation: "Marked [file] as sensitive"
```

**Backend Effect:**
```json
{
  "content": "Sensitive file: employee_data.xlsx - Contains PII",
  "source": "sensitive:storage/employee_data.xlsx",
  "category": "security",
  "confidence": 0.95
}
```

---

#### 3. 🧪 Sandbox Test

**Purpose**: Test file in isolated sandbox environment

**What It Does:**
- Queues file for sandbox analysis
- Runs in isolated environment to check for:
  - Malicious code
  - Data quality issues
  - Schema validation
- Results logged to insights table

**Usage:**
```
1. Select file
2. Click "🧪 Sandbox Test"
3. Confirmation: "Queued [file] for sandbox testing"
4. Check results in insights
```

**Backend Effect:**
```json
{
  "insight_type": "sandbox_request",
  "source": "file_quick_action",
  "content": "Sandbox test requested for: storage/unknown_script.py",
  "metadata": {
    "file_path": "storage/unknown_script.py",
    "action": "sandbox_test"
  }
}
```

---

#### 4. 🔄 Re-train

**Purpose**: Re-run learning pipeline on file

**What It Does:**
- Creates new ingestion record
- Runs full learning pipeline again:
  - Schema inference
  - RAG embedding
  - World model update
  - Table ingestion
- Useful when:
  - Initial ingestion failed
  - File was updated
  - Want to refresh learned knowledge

**Usage:**
```
1. Select file
2. Click "🔄 Re-train"
3. Watch progress in ingestion status panel
```

**Backend Effect:**
- New ingestion ID created
- Progress tracked: queued → processing → completed
- All learning steps re-executed

---

## 📊 Learning Pipeline Details

### What Gets Extracted

When a file is ingested, Grace extracts:

#### 1. World Model Facts
```
- File metadata (name, size, path, upload time)
- Semantic understanding
- Relationships to other knowledge
- Trust/sensitivity markers
```

#### 2. RAG Documents
```
- Text chunks (optimized for search)
- Embeddings for semantic search
- Source attribution
- Trust scores
```

#### 3. Table Entries
```
- Structured data (if CSV/JSON/Excel)
- Schema inference results
- Insights and analysis
- Auto-detected patterns
```

---

## 🎯 Use Cases

### Use Case 1: Onboarding Company Knowledge

```bash
# Upload company handbook
1. Drag company_handbook.pdf to File Explorer
2. Wait for ingestion to complete
3. Click "✅ Whitelist" to mark as trusted
4. Click "🧠 What Learned?" to verify content extracted

# Result: Grace can now answer questions like:
- "What's our vacation policy?"
- "How do I submit expenses?"
- "What are the code review guidelines?"
```

### Use Case 2: Handling Sensitive Data

```bash
# Upload customer data file
1. Upload customer_database.csv
2. Click "🔒 Mark Sensitive"
3. Reason: "Contains customer PII"

# Result: Grace knows to:
- Not log this data in plaintext
- Apply extra privacy controls
- Request approval before accessing
```

### Use Case 3: Debugging Failed Ingestion

```bash
# If file didn't learn properly
1. Check ingestion status - shows "failed" or low progress
2. Click "🧠 What Learned?" - shows no results
3. Click "🔄 Re-train" to try again
4. Monitor new ingestion progress

# Common fixes:
- File encoding issues → Fixed on retry
- Temporary RAG service down → Works after restart
- Large file timeout → Retrain with more time
```

### Use Case 4: Verifying Learning Quality

```bash
# After uploading technical documentation
1. Upload api_docs.md
2. Wait for completion
3. Click "🧠 What Learned?"
4. Verify:
   ✓ All API endpoints extracted (RAG documents)
   ✓ Key concepts in world model (facts)
   ✓ Code examples captured (table entries)

# If missing content:
- Click "🔄 Re-train"
- Check file format compatibility
- Review error logs
```

---

## 🔍 Knowledge Display Format

### Summary Line
```
Grace learned {total} things from this file: {breakdown}
```

Examples:
- `Grace learned 12 things: 5 facts, 4 document chunks, 3 insights`
- `Grace hasn't learned anything from this file yet. It may still be processing.`

### World Model Facts

Each fact shows:
- **Content**: What Grace learned
- **Confidence**: How certain (0-100%)
- **Category**: Type of knowledge (document, trust, security, etc.)

```
┌─────────────────────────────────────┐
│ User uploaded file: report.pdf      │
│ Confidence: 90% | Category: document│
└─────────────────────────────────────┘
```

### RAG Documents

Each chunk shows:
- **Text**: Excerpt from file (truncated to 200 chars)
- **Trust Score**: How much to trust this chunk (0-100%)

```
┌──────────────────────────────────────────┐
│ The quarterly results show a 15%...     │
│ Trust: 85%                               │
└──────────────────────────────────────────┘
```

### Table Entries

Each entry shows:
- **Content**: Insight or structured data
- **Type**: Classification (file_upload, analysis, etc.)

```
┌────────────────────────────────────────┐
│ File uploaded and learned: data.csv    │
│ Type: file_upload                      │
└────────────────────────────────────────┘
```

---

## 🛠️ API Reference

### Get Learned Knowledge

```
GET /api/memory/files/learned?file_path={path}
```

**Response:**
```json
{
  "file_path": "storage/document.pdf",
  "world_model_facts": [
    {
      "content": "User uploaded file: document.pdf",
      "confidence": 0.9,
      "source": "file_upload:storage/document.pdf",
      "category": "document",
      "created_at": "2025-11-18T12:00:00"
    }
  ],
  "rag_documents": [
    {
      "text": "Chapter 1: Introduction...",
      "trust_score": 0.85,
      "source": "document:storage/document.pdf"
    }
  ],
  "table_entries": [
    {
      "type": "file_upload",
      "content": "File uploaded and learned: document.pdf"
    }
  ],
  "summary": "Grace learned 3 things from this file: 1 fact, 1 document chunk, 1 insight"
}
```

---

### Execute Quick Action

```
POST /api/memory/files/quick-action
```

**Request Body:**
```json
{
  "file_path": "storage/file.pdf",
  "action": "whitelist",
  "metadata": {
    "reason": "Official company document"
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "whitelist",
  "file_path": "storage/file.pdf",
  "message": "Added file.pdf to whitelist. Future content from this file will be trusted."
}
```

**Supported Actions:**
- `whitelist` - Add to trusted sources
- `mark_sensitive` - Flag as sensitive data
- `sandbox_test` - Queue for sandbox testing
- `retrain` - Re-run learning pipeline

---

## 🎨 UI Workflow

### Standard Upload → Learn → Query Flow

```
┌─────────────────────────────────────────┐
│ 1. Upload File                          │
│    - Drag & drop OR click Upload        │
│    - File saved to storage/             │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. Learning Pipeline (Auto)             │
│    - Schema inference    (10-30%)       │
│    - RAG embedding      (30-60%)        │
│    - World model        (60-80%)        │
│    - Table ingestion    (80-100%)       │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. Status Display                       │
│    ✓ Processing: 65% - "Added to RAG"  │
│    → Watch progress bar in real-time    │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. Query Learning                       │
│    - Click file in tree                 │
│    - Click "🧠 What Learned?"          │
│    - See inline knowledge display       │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. Quick Actions (Optional)             │
│    ✅ Whitelist - Mark as trusted      │
│    🔒 Sensitive - Flag for privacy     │
│    🧪 Sandbox - Test in isolation      │
│    🔄 Re-train - Refresh learning      │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing Guide

### Test "What Learned?" Feature

```bash
# 1. Create test file
echo "Grace is an AI assistant with 20 kernels." > test.txt

# 2. Upload via File Explorer
- Open File Explorer (click 📁 Files)
- Drag test.txt into tree view
- Wait for ingestion to complete

# 3. Query learning
- Click test.txt in tree
- Click "🧠 What Learned?" button
- Should see:
  ✓ World Model Facts: "User uploaded file: test.txt"
  ✓ RAG Documents: "Grace is an AI assistant..."
  ✓ Summary shows total learned items

# 4. Verify in chat
- Ask Grace: "What do you know about yourself?"
- Should mention "20 kernels" from the file
```

### Test Quick Actions

```bash
# Test Whitelist
1. Select any file
2. Click "✅ Whitelist"
3. Check alert: "Added [file] to whitelist"
4. Query learning → Should see trust fact

# Test Mark Sensitive
1. Select file with "sensitive" data
2. Click "🔒 Mark Sensitive"
3. Enter reason: "Test sensitive data"
4. Query learning → Should see security category

# Test Re-train
1. Select previously uploaded file
2. Click "🔄 Re-train"
3. Watch ingestion panel → New progress bar appears
4. Wait for completion
5. Query learning → Should have fresh results
```

---

## 🔧 Configuration

### Trust Scoring Defaults

```python
# Whitelisted files
confidence = 1.0  # 100% trust

# Sensitive files
confidence = 0.95  # 95% trust (high but flagged)

# Normal uploads
confidence = 0.9  # 90% trust (standard)
```

### RAG Chunk Size

```python
# Text extraction
max_chars = 5000  # First 5000 characters

# Display truncation
max_display = 200  # Show 200 chars + "..."
```

---

## 🐛 Troubleshooting

### Issue: "Grace hasn't learned anything"

**Possible Causes:**
1. File still processing (< 100%)
2. Ingestion failed
3. Unsupported file type
4. Empty file

**Solution:**
```
1. Check ingestion status panel
2. Look for error message
3. Try "🔄 Re-train"
4. Check backend logs
```

### Issue: Only partial learning

**Symptoms:**
- RAG docs present but no world model facts
- Facts present but no RAG docs

**Solution:**
```
One pipeline step may have failed.
Click "🔄 Re-train" to run full pipeline again.
```

### Issue: Quick action does nothing

**Check:**
1. File selected?
2. Action button enabled?
3. Backend running?
4. Check browser console for errors

---

## ✅ Success Indicators

You know it's working when:

- [x] Upload shows progress 0% → 100%
- [x] "🧠 What Learned?" shows knowledge
- [x] World model facts have >0 items
- [x] RAG documents searchable in chat
- [x] Quick actions show confirmation messages
- [x] Re-train creates new ingestion record

---

## 🚀 Next Steps

After mastering these features:

1. **Batch Operations**
   - Select multiple files
   - Bulk whitelist/sensitivity marking
   - Mass re-training

2. **Advanced Queries**
   - "Compare what you learned from files A and B"
   - "Find contradictions in uploaded docs"
   - "Summarize all customer feedback files"

3. **Automated Workflows**
   - Auto-whitelist from trusted folders
   - Auto-mark sensitive based on content
   - Scheduled re-training for updated files

---

**Your files are now intelligent learning sources for Grace!** 🧠✨
