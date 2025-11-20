# Issue Report: DuckDuckGo 403 & Storage Detection

**Date:** November 18, 2025  
**Status:** Identified and Documented

---

## Issue 1: DuckDuckGo Search 403 Error

### Observed Behavior
```
[GOOGLE-SEARCH] DuckDuckGo retry failed with status 403
```

### Root Cause
**HTTP 403 Forbidden** - DuckDuckGo is blocking the request

**Likely reasons:**
1. **Rate Limiting** - Too many requests in short time
2. **Bot Detection** - User-agent or request pattern flagged as automated
3. **IP-based Blocking** - IP address temporarily blocked
4. **Missing Headers** - Request headers don't match browser behavior

### Current Implementation
**File:** `backend/services/google_search_service.py` (Lines 155-175)

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
async with self.session.post(url, data=params, headers=headers) as response:
    if response.status not in [200, 202]:
        logger.warning(f"[GOOGLE-SEARCH] DuckDuckGo returned status {response.status}")
        return []
```

**Issues:**
- ❌ Incomplete User-Agent header
- ❌ No request throttling
- ❌ No retry backoff
- ❌ No request rotation

### Impact
- **Severity:** Low (non-critical feature)
- **Fallback:** Search functionality gracefully degrades
- **User Impact:** Web learning features limited

### Recommended Fixes

#### Short-term (Quick Fix)
1. **Add rate limiting:**
```python
import time
last_request_time = 0
min_request_interval = 2.0  # 2 seconds between requests

async def _search_duckduckgo(self, query: str):
    global last_request_time
    elapsed = time.time() - last_request_time
    if elapsed < min_request_interval:
        await asyncio.sleep(min_request_interval - elapsed)
    
    # Make request...
    last_request_time = time.time()
```

2. **Improve User-Agent:**
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
```

3. **Add exponential backoff:**
```python
for attempt in range(3):
    response = await make_request()
    if response.status == 403:
        backoff = 2 ** attempt  # 1s, 2s, 4s
        await asyncio.sleep(backoff)
        continue
    break
```

#### Long-term (Better Solution)
1. **Use official search APIs:**
   - Google Custom Search API (100 free queries/day)
   - Bing Search API
   - SerpAPI (commercial)

2. **Implement search provider rotation:**
   - Try DuckDuckGo first
   - Fallback to Bing
   - Fallback to Google API if available

3. **Add request caching:**
   - Cache search results for 24 hours
   - Reduce duplicate requests

---

## Issue 2: Storage Detection Inaccuracy

### Observed Behavior
```
[OK] Storage tracker initialized (24.27 GB used, 0.976 TB remaining)
```

**User reports:** "I have 2.5 TB available"  
**System reports:** 0.976 TB remaining

**Discrepancy:** ~1.5 TB missing

### Root Cause
**Hardcoded 1TB limit** instead of actual disk space detection

**File:** `backend/services/storage_tracker.py` (Line 22)

```python
def __init__(self):
    self.total_capacity_tb = 1.0  # 1TB available (configurable)
```

**Calculation:**
```python
remaining_tb = total_capacity_tb - used_tb
# remaining_tb = 1.0 TB - 0.024 TB = 0.976 TB
```

**The tracker is measuring used space correctly (24.27 GB), but comparing against a hardcoded 1TB limit instead of your actual 2.5TB disk.**

### Current Implementation Issues
1. ❌ Hardcoded 1TB capacity
2. ❌ Doesn't detect actual system disk space
3. ❌ Only tracks Grace's data directories (not system-wide)
4. ✅ Correctly calculates used space in tracked directories

### Recommended Fix

**Use `shutil.disk_usage()` to get actual disk space:**

```python
import shutil
from pathlib import Path

def __init__(self):
    # Auto-detect disk capacity
    try:
        # Get disk usage for project root
        root_path = Path(__file__).parent.parent.parent
        usage = shutil.disk_usage(root_path)
        
        # Convert to TB
        self.total_capacity_tb = usage.total / (1024 ** 4)
        self.used_capacity_tb = (usage.total - usage.free) / (1024 ** 4)
        
        logger.info(f"[STORAGE] Detected {self.total_capacity_tb:.2f} TB total disk space")
    except Exception as e:
        logger.warning(f"[STORAGE] Could not detect disk space: {e}")
        self.total_capacity_tb = 1.0  # Fallback to 1TB
```

### Impact
- **Severity:** Low (cosmetic/informational)
- **Functionality:** No impact on actual storage usage
- **Accuracy:** Reports incorrect remaining space

---

## Fixes Implementation

### File 1: Fix DuckDuckGo Search
**File:** `backend/services/google_search_service.py`

**Changes needed:**
1. Add rate limiting (2 seconds between requests)
2. Improve User-Agent headers
3. Add exponential backoff for 403 errors
4. Add request caching

### File 2: Fix Storage Detection
**File:** `backend/services/storage_tracker.py`

**Changes needed:**
1. Replace hardcoded 1TB with `shutil.disk_usage()`
2. Detect actual system disk capacity
3. Support configuration override via environment variable
4. Add Windows drive letter detection

---

## Priority

| Issue | Severity | Priority | ETA |
|-------|----------|----------|-----|
| DuckDuckGo 403 | Low | Medium | Week 2 |
| Storage Detection | Low | Low | Week 2 |

Both issues are **non-critical** and don't affect core functionality.

---

## Workarounds

### DuckDuckGo 403
**Workaround:** The system gracefully degrades to no search results. Web learning features continue to work with other data sources.

**Manual fix:** Set Google API credentials in environment:
```bash
export GOOGLE_API_KEY="your-key"
export GOOGLE_CX="your-cx"
```

### Storage Detection
**Workaround:** The 0.976 TB is just a display issue. Actual storage usage is correctly tracked.

**Manual override:** Edit `backend/services/storage_tracker.py` line 22:
```python
self.total_capacity_tb = 2.5  # Your actual TB
```

---

## Summary

✅ **Both issues identified and understood**  
✅ **Root causes documented**  
✅ **Fixes designed**  
⏳ **Implementation scheduled for Week 2**

Neither issue is blocking production deployment.
