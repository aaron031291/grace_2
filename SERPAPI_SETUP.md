# SerpAPI Integration - Complete ✅

Production-ready Google search via SerpAPI with throttling, provenance, and secure key management.

---

## Quick Start

### 1. Get SerpAPI Key

1. Sign up: https://serpapi.com/users/sign_up
2. Get your API key from dashboard
3. Free tier: 100 searches/month

### 2. Configure Grace

Add to `.env`:

```bash
SEARCH_PROVIDER=serpapi
SERPAPI_KEY=your-secret-key-here

# Optional: Configure throttling and quotas
SERPAPI_MONTHLY_QUOTA=100        # Default: 100 (free tier)
SERPAPI_MIN_INTERVAL=1.0         # Min 1 second between requests
SERPAPI_LOCATION=United States   # Default search location
SERPAPI_LANG=en                  # Default language
SERPAPI_COUNTRY=us               # Default country code
```

### 3. Install Package

```bash
pip install google-search-results
```

### 4. Restart Grace

```bash
python backend/main.py

# Look for:
# [GOOGLE-SEARCH] SerpAPI provider enabled
```

---

## Implementation

### File: `backend/services/serpapi_adapter.py`

**Features:**
- ✅ Secure API key from environment
- ✅ Rate limiting (respects monthly quota)
- ✅ Request throttling (min 1s between calls)
- ✅ Result normalization to Grace's format
- ✅ Provenance logging (every search tracked)
- ✅ Stats tracking (success/fail rates)
- ✅ Support for answer boxes and knowledge graphs

### Search Flow

```
query = "Python async best practices"
    ↓
Rate limit check (within quota?)
    ↓
Throttle (wait if < 1s since last request)
    ↓
Build SerpAPI params:
    q: "Python async best practices"
    location: "United States"
    hl: "en"
    gl: "us"
    api_key: [REDACTED]
    num: 10
    ↓
Execute: GoogleSearch(params).get_dict()
    ↓
Normalize results:
    - Extract organic_results
    - Extract answer_box (if present)
    - Extract knowledge_graph (if present)
    - Add trust scores
    - Add provenance metadata
    ↓
Log provenance event
    ↓
Return normalized results
```

---

## Result Format

### SerpAPI Raw Response

```json
{
  "organic_results": [
    {
      "position": 1,
      "title": "Python Async Programming Guide",
      "link": "https://example.com/python-async",
      "displayed_link": "example.com › python-async",
      "snippet": "Comprehensive guide to async programming in Python..."
    }
  ],
  "answer_box": {
    "title": "What is Python async?",
    "answer": "Python async allows concurrent execution...",
    "link": "https://docs.python.org/async"
  },
  "knowledge_graph": {
    "title": "Python (programming language)",
    "type": "Programming language",
    "description": "Python is a high-level...",
    "website": "https://python.org"
  }
}
```

### Grace's Normalized Format

```json
[
  {
    "title": "Python (programming language)",
    "link": "https://python.org",
    "snippet": "Python is a high-level...",
    "source": "serpapi",
    "provider": "google_knowledge_graph",
    "rank": 0,
    "trust_score": 0.95,
    "metadata": {
      "type": "knowledge_graph",
      "entity_type": "Programming language",
      "query": "Python async best practices"
    }
  },
  {
    "title": "What is Python async?",
    "link": "https://docs.python.org/async",
    "snippet": "Python async allows concurrent execution...",
    "source": "serpapi",
    "provider": "google_answer_box",
    "rank": 0,
    "trust_score": 0.9,
    "metadata": {
      "type": "answer_box",
      "query": "Python async best practices"
    }
  },
  {
    "title": "Python Async Programming Guide",
    "link": "https://example.com/python-async",
    "snippet": "Comprehensive guide to async programming in Python...",
    "source": "serpapi",
    "provider": "google",
    "rank": 1,
    "trust_score": 0.8,
    "metadata": {
      "position": 1,
      "displayed_link": "example.com › python-async",
      "query": "Python async best practices",
      "search_timestamp": "2025-11-19T03:00:00.000Z"
    }
  }
]
```

---

## Trust Scores

Results are automatically assigned trust scores:

| Source | Trust Score | Rationale |
|--------|-------------|-----------|
| **Knowledge Graph** | 0.95 | Google's verified entity data |
| **Answer Box** | 0.90 | Featured snippet from trusted source |
| **Organic Result** | 0.80 | Standard search result |

Trust scores can be used by:
- RAG system (weight results by trust)
- World model (cite high-trust sources)
- Governance (flag low-trust sources)

---

## Rate Limiting

### Built-in Throttling

```python
# Minimum 1 second between requests
SERPAPI_MIN_INTERVAL=1.0

# Track daily quota usage
requests_made_today = 15
daily_limit = 100 / 30  # ~3.3 per day for monthly quota

if requests_made_today >= daily_limit:
    logger.warning("Daily quota approaching limit")
```

### Quota Tracking

```python
stats = serpapi_adapter.get_stats()

# Returns:
{
  "provider": "serpapi",
  "enabled": true,
  "total_calls": 45,
  "successful_calls": 43,
  "failed_calls": 2,
  "success_rate": 0.956,
  "requests_today": 15,
  "monthly_quota": 100,
  "quota_remaining": 85
}
```

---

## Provenance Logging

Every search is logged via event bus:

```python
await event_bus.publish(Event(
    event_type=EventType.MEMORY_UPDATE,
    source="serpapi_adapter",
    data={
        "action": "search_executed",
        "query": "Python async best practices",
        "results_count": 10,
        "provider": "serpapi",
        "timestamp": "2025-11-19T03:00:00.000Z",
        "trust_scores": [0.95, 0.90, 0.80, ...]
    }
))
```

**Benefits:**
- World model knows where info came from
- RAG can cite "Source: Google (via SerpAPI)"
- Governance can audit search usage
- Trust framework tracks source reliability

---

## Integration with Learning Loop

When Grace learns from web:

```
User uploads question: "What are Python async best practices?"
    ↓
Learning loop needs context
    ↓
Calls: serpapi_adapter.search("Python async best practices")
    ↓
Gets 10 results with trust scores
    ↓
Extracts content from top 3 results
    ↓
Chunks and embeds content
    ↓
Stores in RAG with provenance:
    - source: "https://example.com/python-async"
    - provider: "serpapi"
    - trust_score: 0.8
    - search_query: "Python async best practices"
    ↓
World model updated:
    "Learned about Python async from Google search results (trust: 0.8)"
    ↓
Grace can now answer questions and cite sources
```

---

## Example Usage

### In Learning System

```python
from backend.services.serpapi_adapter import serpapi_adapter

# Search for information
results = await serpapi_adapter.search(
    query="machine learning regression techniques",
    max_results=5,
    location="United States"
)

# Results include trust scores and provenance
for result in results:
    print(f"Title: {result['title']}")
    print(f"Trust: {result['trust_score']}")
    print(f"Source: {result['source']}")
    
    # Ingest into knowledge base
    await ingest_web_content(
        url=result['link'],
        snippet=result['snippet'],
        trust_score=result['trust_score'],
        provenance={
            "search_query": "machine learning regression",
            "provider": "serpapi",
            "rank": result['rank']
        }
    )
```

### In Chat System

Grace can search and cite:

**User:** "What are the latest trends in AI?"

**Grace:** "Based on recent Google search results:

1. **Generative AI adoption** - Growing rapidly in enterprise [Trust: 0.90, Source: forbes.com via Google]
2. **Multimodal models** - Combining text, vision, audio [Trust: 0.85, Source: techcrunch.com]
3. **AI governance frameworks** - Increasing regulatory focus [Trust: 0.80, Source: nature.com]

[All sources retrieved via SerpAPI Google search]"

---

## Configuration Options

### Minimal (Free Tier)

```bash
SEARCH_PROVIDER=serpapi
SERPAPI_KEY=your-key
# Uses defaults: 100/month, 1s throttle, US location
```

### Full Configuration

```bash
SEARCH_PROVIDER=serpapi
SERPAPI_KEY=your-key
SERPAPI_MONTHLY_QUOTA=1000        # Paid tier
SERPAPI_MIN_INTERVAL=0.5          # Faster throttle (if paid)
SERPAPI_LOCATION=London, UK       # Different location
SERPAPI_LANG=en                   # Language
SERPAPI_COUNTRY=uk                # Country code
```

### Fallback Chain

```bash
SEARCH_PROVIDER_ORDER=serpapi,mock
# Try SerpAPI first, fall back to mock on failure
```

---

## Comparison

| Feature | Mock | DuckDuckGo | SerpAPI |
|---------|------|------------|---------|
| **Cost** | Free | Free | $50/mo (1000 searches) |
| **Rate Limits** | None | Blocks after ~5 | Quota-based |
| **Reliability** | 100% | ❌ 403 errors | ✅ 99.9% |
| **Result Quality** | Fake | Real but basic | Real + rich (answer boxes, knowledge graph) |
| **Trust Scores** | N/A | 0.6 | 0.8-0.95 |
| **Provenance** | ✅ | ✅ | ✅ Enhanced |
| **Good For** | Dev/Testing | N/A (blocked) | Production |

---

## Recommendation

### Current State (After Fix)
- Using: `SEARCH_PROVIDER=mock`
- Status: ✅ Working, no errors
- Good for: Development, testing

### When to Switch to SerpAPI

**Switch when:**
- Need real web search results
- Ready to spend $50/mo (or use 100 free/month)
- Want rich results (answer boxes, knowledge graphs)
- Need reliable production search

**Don't switch if:**
- Just testing locally
- Don't need real web results yet
- Want to avoid API costs

---

## Testing SerpAPI

### 1. Set Up

```bash
# Add to .env
SEARCH_PROVIDER=serpapi
SERPAPI_KEY=your-key-from-serpapi-com
```

### 2. Test

```bash
# Restart Grace
python backend/main.py

# Should see:
# [GOOGLE-SEARCH] SerpAPI provider enabled

# Test search (if endpoint available)
curl "http://localhost:8420/api/search?query=test"
```

### 3. Monitor Quota

```bash
# Check stats
curl http://localhost:8420/api/serpapi/stats

# Returns:
{
  "provider": "serpapi",
  "total_calls": 15,
  "requests_today": 15,
  "monthly_quota": 100,
  "quota_remaining": 85
}
```

---

## Summary

✅ **SerpAPI adapter created** - Full integration ready
✅ **Rate limiting implemented** - Respects quota
✅ **Throttling active** - Min 1s between requests
✅ **Provenance logged** - Every search tracked
✅ **Trust scores assigned** - 0.8-0.95 for results
✅ **Fallback to mock** - Graceful degradation
✅ **Current fix active** - Mock provider working now

**Next Step:** Keep using mock for now, switch to SerpAPI when ready for production search.
