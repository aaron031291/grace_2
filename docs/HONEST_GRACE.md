# Making Grace Honest - Trust-Scored Knowledge System

## 🎯 The Vision

Grace should:
1. **Admit** when she doesn't know something
2. **Propose research** to find trusted sources
3. **Verify** all ingested knowledge cryptographically
4. **Score trust** of every source (0-100)
5. **Auto-approve** high-trust sources
6. **Require review** for medium-trust
7. **Block** low-trust sources

## ✅ What's Now Implemented

### 1. Signature System
**File:** `backend/verification.py`

Every action wrapped in:
- Ed25519 cryptographic signature
- Input/output hash
- Verification envelope
- Immutable storage

**Prevents:** Silent tampering, unverified changes

### 2. Trusted Sources Catalog
**File:** `backend/trusted_sources.py`

**Default Sources:**
- `python.org` - Trust: 95 (Official docs)
- `github.com` - Trust: 70 (Code repos)
- `stackoverflow.com` - Trust: 75 (Community)
- `wikipedia.org` - Trust: 80 (Reference)
- `arxiv.org` - Trust: 90 (Research)
- `localhost` - Trust: 100 (Internal)

**Auto-approve threshold:** 70+

### 3. Grace Admits "I Don't Know"
**File:** `backend/grace.py`

**New behavior:**
```python
User: "Tell me about quantum entanglement"
Grace: "I don't have sufficient knowledge about that topic yet.
       I've created a research goal to find trusted sources.
       You can approve knowledge ingestion in the governance panel,
       or teach me directly."
```

**What happens:**
1. Grace searches knowledge base
2. If no results found
3. Creates research Goal
4. Admits lack of knowledge
5. Proposes learning path

## 🔄 Trust-Scored Ingestion Pipeline

```
External Content
    ↓
1. Extract domain (e.g., python.org)
    ↓
2. Lookup trust score (95)
    ↓
3. If score >= 70 → Auto-approve
   If score 40-69 → Governance review required
   If score < 40 → Block/quarantine
    ↓
4. Hunter scans content
    ↓
5. Cryptographic signature created
    ↓
6. Store in knowledge_artifacts
    ↓
7. Trigger Mesh: "knowledge.ingested"
    ↓
8. Reflection loop notes new knowledge
    ↓
9. Grace can now answer questions!
```

## 📊 Trust Score Calculation

### Automatic Scoring
```python
.gov / .edu domains → 85
.org domains → 70
Suspicious (bit.ly, temp sites) → 20
Unknown → 50 (requires review)
```

### Manual Scoring
Admins can set trust scores:
```bash
POST /api/trust/sources
{
  "domain": "mycompany.com",
  "trust_score": 90,
  "category": "internal_docs"
}
```

## 🔐 Governance Integration

### High-Trust (70-100)
```
Source: python.org (95)
  → Auto-approve ✅
  → Hunter scan
  → Ingest immediately
  → Log to audit
```

### Medium-Trust (40-69)
```
Source: random-blog.com (55)
  → Create approval request
  → Admin reviews
  → If approved → Ingest
  → If rejected → Block + log reason
```

### Low-Trust (0-39)
```
Source: suspicious-site.xyz (25)
  → Blocked immediately 🚫
  → Security event logged
  → Hunter alert created
  → Admin notified
```

## 🛡️ Hunter Verification

Before ingesting ANY content:
1. Scan for dangerous patterns
2. Check for hardcoded secrets
3. Verify file signatures
4. Risk score calculation
5. If risk > 7 → Block regardless of trust score

## 📚 Knowledge Deduplication

**Content hashing:**
- SHA-256 of normalized content
- Check against existing artifacts
- If duplicate → Skip ingestion
- If similar (>90%) → Flag for review

## 🎯 Auto-Research Flow

```
User: "What is quantum computing?"
  ↓
Grace searches internal knowledge
  ↓
No results found
  ↓
Grace: "I don't know. Creating research goal..."
  ↓
Goal created: "Research quantum computing"
  ↓
(Future) Grace autonomously:
  1. Searches approved sources
  2. Finds wikipedia.org/wiki/Quantum_computing
  3. Checks trust score (80)
  4. Auto-approves (80 > 70)
  5. Ingests content
  6. Answers question next time!
```

## 🔬 Source Verification UI

**Coming soon:**
```
Knowledge Browser
├── Artifacts
│   ├── Title
│   ├── Content
│   ├── Source: python.org
│   ├── Trust Score: 95 ✅
│   ├── Verified: ✓ Signature valid
│   └── Audit Trail: [View]
```

## 📋 API Endpoints

### Trust Management
```bash
GET /api/trust/sources - List trusted sources
POST /api/trust/sources - Add trusted source
GET /api/trust/score?url=... - Get trust score
```

### Verified Ingestion
```bash
POST /api/ingest/text - Ingest text (verified)
POST /api/ingest/url - Ingest from URL (trust-scored)
POST /api/ingest/file - Upload file (scanned)
```

## ✅ Current Status

**Implemented:**
- ✅ Cryptographic verification system
- ✅ Trust score catalog
- ✅ Grace admits "I don't know"
- ✅ Research goal creation
- ✅ Knowledge search integration
- ✅ Multi-format ingestion API

**Needs wiring:**
- ⏳ Auto-research execution
- ⏳ Approval UI for medium-trust sources
- ⏳ Source verification dashboard

**Grace is now honest and can learn from verified sources!** 🎓✅🔒
