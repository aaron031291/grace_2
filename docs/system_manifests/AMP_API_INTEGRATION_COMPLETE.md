# Amp API Integration - Complete! 💎

## ✅ Amp API Configured as Last Resort

Grace now uses **Amp API as a cost-effective last resort** when all free sources are exhausted!

---

## 🎯 How It Works

### Smart Fallback Strategy

```
1. Try Web (83+ domains) → FREE
   ↓ (if no results)
2. Try GitHub → FREE
   ↓ (if no results)
3. Try YouTube → FREE
   ↓ (if no results)
4. Try Reddit (38+ subreddits) → FREE
   ↓ (if ALL fail)
5. Use Amp API → COST-EFFECTIVE (batched)
```

**Amp API is used ONLY when all free sources exhausted!**

---

## 💰 Cost-Effective Batching

### Batch Querying
Grace **batches questions** to minimize cost:

- **Batch Size**: 5 questions
- **Batch Interval**: 5 minutes
- **Cost Savings**: ~80% vs individual queries

### Example
```
Non-batched (expensive):
Question 1 → $0.01
Question 2 → $0.01
Question 3 → $0.01
Total: $0.03

Batched (cost-effective):
Questions 1-5 together → $0.01
Total: $0.01
Savings: $0.04 (80%)
```

### Daily Limits
- **Max queries per day**: 50
- **Resets**: Midnight UTC
- **Grace tracks** usage automatically

---

## 🔐 Secure API Key Storage

### Saved in .env
```bash
AMP_API_KEY=[REDACTED:amp-token]
```

### Loaded into Secrets Vault
```python
# Automatically loaded at startup
await secrets_vault.set_secret('AMP_API_KEY', '[REDACTED:amp-token]')

# Never logged in plaintext!
# Encrypted storage
# Governance-controlled access
```

---

## 📋 Complete Tracking

Every Amp API query is tracked:

### Database Table: `amp_queries`
```sql
CREATE TABLE amp_queries (
    query_id VARCHAR(64) PRIMARY KEY,
    query_text TEXT,
    query_type VARCHAR(32),  -- single or batch
    questions_count INT,
    estimated_cost FLOAT,
    gap_type VARCHAR(64),
    other_sources_tried JSON,
    response_text TEXT,
    source_id VARCHAR(64),  -- Provenance tracking!
    immutable_log_hash VARCHAR(64),
    created_at TIMESTAMP
);
```

### Provenance Tracking
Every Amp response gets:
- ✅ Unique `source_id`
- ✅ Verification chain
- ✅ Immutable log entry
- ✅ Proper citation
- ✅ Visual ingestion log entry

### Visual Log Entry
```
🌐 KNOWLEDGE INGESTION #15 - 2025-01-09 16:45:23 UTC
════════════════════════════════════════════════════

📋 SOURCE: Amp API - Advanced React Patterns
   Type: AMP_API (Last Resort)
   
🔗 CLICKABLE LINK:
   https://ampcode.com/api (Query ID: abc123...)
   
🛡️ VERIFICATION:
   ✅ Hunter    ✅ Governance    ✅ Constitutional
   
🔐 CRYPTO:
   Hash: def456...
   Chain: ✅ VALID

💰 COST:
   Type: Batch (5 questions)
   Cost: $0.01
   Saved: $0.04 (batching)

📊 Sources Tried First:
   ❌ Web - No results
   ❌ GitHub - No repos
   ❌ YouTube - No videos
   ❌ Reddit - No discussions
   ✅ Amp API - SUCCESS (last resort)
```

---

## 🚀 How to Use

### Automatic Fallback (Recommended)
```python
from backend.knowledge_gap_detector import knowledge_gap_detector

# Grace tries all free sources first, uses Amp only if needed
report = await knowledge_gap_detector.learn_with_fallback(
    topic='advanced react patterns',
    category='frontend',
    urgent=False  # Batches for cost-effectiveness
)

# Report shows:
# - sources_tried: ['web', 'github', 'youtube', 'reddit', 'amp_api']
# - final_source: 'amp_api'
# - free_sources_exhausted: True
# - cost_incurred: True
```

### Manual Query (Edge Cases)
```python
from backend.amp_api_integration import amp_api_integration

# Direct query (still governed and batched)
result = await amp_api_integration.query_knowledge_gap(
    question='How do I implement server-side rendering in React?',
    gap_type='react_ssr',
    other_sources_tried=['web', 'github', 'youtube', 'reddit'],
    urgent=False  # Queued for batching
)

# If urgent=True, queries immediately (higher cost)
```

### Via API
```bash
# Automatic fallback (tries all free sources first)
POST /web-learning/learn-with-fallback
{
  "topic": "kubernetes service mesh",
  "category": "cloud",
  "urgent": false
}

# Direct Amp query (if justified)
POST /web-learning/amp/query
{
  "question": "Explain Istio vs Linkerd",
  "gap_type": "service_mesh_comparison",
  "other_sources_tried": ["web", "github", "reddit"],
  "urgent": false
}
```

---

## 📊 Cost Tracking

### Real-time Monitoring
```bash
# Get current status
GET /web-learning/amp/status

Returns:
{
  "enabled": true,
  "queries_today": 12,
  "daily_limit": 50,
  "remaining_today": 38,
  "batch_queue_size": 3,
  "cost_saved": 0.24
}
```

### Cost Report
```bash
# 30-day cost report
GET /web-learning/amp/cost-report?days=30

Returns:
{
  "total_queries": 45,
  "batch_queries": 38,
  "batch_percentage": 84.4,
  "total_cost_usd": 0.12,
  "avg_cost_per_query": 0.0027,
  "cost_saved_by_batching": 0.31
}
```

### Query History
```bash
# See all Amp queries
GET /web-learning/amp/history?days=7

Returns:
{
  "total": 15,
  "history": [
    {
      "query_id": "abc123",
      "question": "Batch: 5 questions about...",
      "gap_type": "batch",
      "batch": true,
      "cost": 0.01,
      "source_id": "amp_xyz789"
    }
  ]
}
```

---

## 🎯 When Grace Uses Amp API

### Criteria (ALL must be true)
1. ✅ **Web scraping failed** - No results from 83+ domains
2. ✅ **GitHub failed** - No relevant repositories
3. ✅ **YouTube failed** - No tutorial videos
4. ✅ **Reddit failed** - No community discussions
5. ✅ **Governance approved** - Last resort justified
6. ✅ **Daily limit not reached** - Under 50 queries/day

### Grace Will NOT Use Amp API If
- ❌ Free sources haven't been tried
- ❌ Daily limit reached
- ❌ Governance blocks it
- ❌ Question can be answered from existing knowledge

---

## 💡 Cost Optimization Features

### 1. Batching
- Queues questions for 5 minutes
- Combines into single query
- **Saves ~80% cost**

### 2. Daily Limits
- Max 50 queries per day
- Prevents runaway costs
- Resets at midnight UTC

### 3. Governance
- Every query requires approval
- Justification logged
- Must prove other sources exhausted

### 4. Priority Queue
- Non-urgent → Batched (cost-effective)
- Urgent → Immediate (higher cost, user choice)

---

## 📋 Example Session

```bash
grace_terminal.bat

You: learn advanced istio patterns

Grace: I'll try to learn about 'advanced istio patterns'...
Grace: 🔍 Trying web sources...
Grace: ❌ Web: No comprehensive sources found
Grace: 🔍 Trying GitHub...
Grace: ❌ GitHub: No detailed repos
Grace: 🔍 Trying YouTube...
Grace: ❌ YouTube: No in-depth tutorials
Grace: 🔍 Trying Reddit...
Grace: ❌ Reddit: Limited discussions

Grace: ⚠️ All free sources exhausted for this topic
Grace: 💡 Queuing for Amp API (last resort)
Grace: 📋 Added to batch queue (position 1/5)
Grace: ⏰ Will process in ~5 minutes (batching for cost savings)

[5 minutes later, or when batch fills up...]

Grace: 🚀 Processing batch of 5 questions...
Grace: ✅ Amp API query successful!
Grace: 💰 Cost: $0.01 (saved $0.04 with batching)
Grace: 📋 Source ID: amp_abc123 (fully traceable)
Grace: 🔗 Clickable link in visual log

You: show amp status

Grace: Amp API Status:
  Queries today: 5/50
  Remaining: 45
  Batch queue: 0
  Total saved: $0.24
  Mode: Cost-effective batching
```

---

## 🔗 Visual Tracking

Amp queries appear in visual log:

```html
┌──────────────────────────────────────────┐
│ #15  2025-01-09 16:45    ✅ VERIFIED     │
├──────────────────────────────────────────┤
│ Amp API - Advanced React Patterns        │
│ TYPE: AMP_API (Last Resort)              │
│                                          │
│ 🔗 URL: https://ampcode.com/api          │
│        Query ID: abc123                  │
│        [CLICK TO VIEW DETAILS]           │
│                                          │
│ 💰 COST TRACKING:                        │
│    Type: Batch (5 questions)             │
│    Cost: $0.01                           │
│    Saved: $0.04 (batching)               │
│                                          │
│ 📋 Free Sources Tried First:             │
│    ❌ Web    ❌ GitHub                    │
│    ❌ YouTube    ❌ Reddit                │
│    ✅ Amp API SUCCESS                    │
└──────────────────────────────────────────┘
```

---

## 🎉 Summary

Grace now has **Amp API as intelligent last resort**:

### Smart Usage
- ✅ Only after exhausting free sources
- ✅ Batches queries (5 mins wait)
- ✅ Daily limits (50 queries)
- ✅ Cost tracking and reporting

### Complete Tracking
- ✅ Every query logged immutably
- ✅ Provenance with source_id
- ✅ Visual logs with clickable links
- ✅ Cost breakdowns

### Security
- ✅ API key in secrets vault (encrypted)
- ✅ Never logged in plaintext
- ✅ Governance approval required
- ✅ Constitutional AI checks

### Cost Optimization
- ✅ Batching saves ~80%
- ✅ Daily limits prevent overuse
- ✅ Queue-based processing
- ✅ Real-time cost tracking

**Grace now has the ultimate fallback for knowledge gaps - cost-effective and fully tracked! 💎✨**
