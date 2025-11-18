# Web Search Setup Guide

**Enable Grace to fetch fresh web articles and latest documentation**

---

## Problem

Grace currently experiences HTTP 403 (rate limiting) from DuckDuckGo:
```
[GOOGLE-SEARCH] DuckDuckGo retry failed with status 403
```

**Impact:**
- ❌ Cannot fetch fresh web articles
- ❌ Cannot search for latest docs online
- ✅ Can still learn from cached data and local sources

---

## Solution: Add Google Search API

Grace now supports **Google Custom Search API** with automatic fallback:

```
Search Priority:
1. Check cache (24-hour TTL) ✅
2. Google Search API (if configured) ✅
3. DuckDuckGo (with rate limiting) ✅
4. Return cached results ✅
```

**Benefits:**
- ✅ 100 free searches per day
- ✅ No rate limiting
- ✅ Fresh results
- ✅ Automatic caching
- ✅ Graceful fallback to DuckDuckGo

---

## Setup Instructions (5 minutes)

### Step 1: Get Google API Key (FREE)

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project (or select existing)
3. Click **"Create Credentials"** → **"API Key"**
4. Copy your API key

**Free tier:** 100 searches/day (sufficient for Grace)

### Step 2: Enable Custom Search API

1. Go to [Custom Search API](https://console.cloud.google.com/apis/library/customsearch.googleapis.com)
2. Click **"Enable"**
3. Wait for activation (30 seconds)

### Step 3: Create Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **"Add"** or **"Create"**
3. Configure:
   - **Sites to search:** Leave empty (search entire web)
   - **Name:** "Grace Web Learning"
   - **Language:** English
4. Click **"Create"**
5. Copy your **Search Engine ID** (starts with something like `a1b2c3d4e5...`)

### Step 4: Add to Grace

**Option A: Environment Variables (Recommended)**

Add to your `.env` file:
```bash
GOOGLE_SEARCH_API_KEY=AIzaSy...your-key-here
GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5...your-id-here
```

**Option B: System Environment Variables**

```bash
# Windows
setx GOOGLE_SEARCH_API_KEY "AIzaSy...your-key-here"
setx GOOGLE_SEARCH_ENGINE_ID "a1b2c3d4e5...your-id-here"

# Linux/Mac
export GOOGLE_SEARCH_API_KEY="AIzaSy...your-key-here"
export GOOGLE_SEARCH_ENGINE_ID="a1b2c3d4e5...your-id-here"
```

### Step 5: Restart Grace

```bash
# Stop Grace (Ctrl+C)
# Start Grace
START_GRACE.bat
# Or
python backend/main.py
```

**Look for this log message:**
```
[GOOGLE-SEARCH] API credentials found, using Google Custom Search API
```

---

## Verify It's Working

### Test Search Functionality

```bash
# Via API
curl -X POST http://localhost:8000/api/web_learning/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python async programming", "num_results": 5}'

# Via Python
from backend.services.google_search_service import google_search_service
import asyncio

async def test():
    await google_search_service.initialize()
    results = await google_search_service.search("latest python features")
    print(f"Found {len(results)} results")

asyncio.run(test())
```

**Expected output:**
```
[GOOGLE-SEARCH] API credentials found, using Google Custom Search API
[GOOGLE-SEARCH] Searching via API: latest python features
Found 5 results
```

---

## Features Now Enabled

### 1. Rate Limiting Protection ✅
```python
# Automatic 2-second delay between searches
min_search_interval = 2.0
```

**Prevents:**
- DuckDuckGo 403 errors
- API quota exhaustion
- Service blocks

### 2. Result Caching ✅
```python
# 24-hour cache TTL
cache_ttl = 86400  # seconds
```

**Benefits:**
- Faster responses for repeated queries
- Reduces API usage
- Works offline for cached queries

### 3. Automatic Fallback ✅
```
Search Flow:
1. Check cache → If hit, return immediately ✅
2. Try Google API → If configured and works ✅
3. Try DuckDuckGo → With rate limiting ✅
4. Return cached → If previous search exists ✅
5. Return empty → Graceful degradation ✅
```

### 4. Better User-Agent ✅
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
```

---

## Cost & Quotas

### Google Custom Search API

**Free Tier:**
- 100 queries per day
- $0 cost
- No credit card required

**If you exceed 100/day:**
- $5 per 1,000 additional queries
- Set billing alerts
- Grace will fallback to DuckDuckGo

**Grace's typical usage:**
- ~10-50 searches per day
- Well within free tier

### Monitor Usage

Check your quota:
```bash
# Via API
curl http://localhost:8000/api/web_learning/search_stats

# Via logs
grep "GOOGLE-SEARCH" logs/grace.log | grep "API search"
```

---

## Troubleshooting

### "API credentials found" but no results

**Check API is enabled:**
1. Go to [API Library](https://console.cloud.google.com/apis/library/customsearch.googleapis.com)
2. Verify "Custom Search API" shows "Enabled"

**Check Search Engine ID:**
1. Go to [Programmable Search](https://programmablesearchengine.google.com/)
2. Click your search engine
3. Copy the correct ID (not the public URL)

### "API search failed" error

**Check API Key permissions:**
```bash
# Test manually
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_KEY&cx=YOUR_CX&q=test"
```

**Expected response:** JSON with search results  
**Error response:** Check error message for details

### Still getting 403 from DuckDuckGo

This is normal if:
- Google API not configured (falls back to DuckDuckGo)
- Cache miss (tries DuckDuckGo after API)

**Solution:** Add Google API credentials (see Step 1-4)

---

## Alternative: Wait for Rate Limit Reset

**If you don't want to set up Google API:**

DuckDuckGo rate limits typically reset after:
- **1-24 hours** automatically
- Grace will auto-retry
- Learning continues from cached/local sources

**Current behavior:**
- ✅ System stays operational
- ✅ Logs reduced to DEBUG level (less spam)
- ✅ Graceful degradation
- ⏳ Fresh searches resume when limit resets

---

## What Grace Learns From

**With Google API configured:**
1. ✅ Fresh web articles and blogs
2. ✅ Latest official documentation
3. ✅ Recent Stack Overflow answers
4. ✅ GitHub repositories and code
5. ✅ Academic papers (ArXiv)
6. ✅ Technical tutorials

**Without Google API (current state):**
1. ✅ Cached web content (24 hours)
2. ✅ Local knowledge base
3. ✅ Existing documentation
4. ✅ Provided learning materials
5. ⏳ Fresh content (when rate limit resets)

---

## Summary

**Quick Setup (5 minutes):**
1. Get Google API key (free)
2. Enable Custom Search API
3. Create search engine
4. Add to `.env` file
5. Restart Grace

**Result:**
- ✅ Fetch fresh web articles
- ✅ Search latest docs online
- ✅ 100 free searches/day
- ✅ No rate limiting
- ✅ Automatic caching

**Optional:** Can continue without API (uses cached data)

---

**Setup URL:** https://developers.google.com/custom-search/v1/overview  
**Cost:** $0 (free tier: 100/day)  
**Time:** 5 minutes  
**Benefit:** Fresh web learning restored ✅
