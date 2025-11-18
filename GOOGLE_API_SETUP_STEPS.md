# Google Search API - Final Setup Steps

**You have the API key! ✅**
```
AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
```

---

## Remaining Steps (2 minutes)

### Step 1: Enable the Custom Search API ✅

1. Open: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
2. Click **"Enable"** button
3. Wait 30 seconds for activation

### Step 2: Create Search Engine (Get Search Engine ID) 🔑

1. Open: https://programmablesearchengine.google.com/
2. Click **"Add"** or **"Create"** button
3. Fill in the form:
   - **Sites to search:** Leave EMPTY (to search entire web)
   - **Name:** Grace Web Learning
   - **Language:** English
   - **Search settings:** Search the entire web
4. Click **"Create"**
5. You'll see your **Search Engine ID** - it looks like:
   ```
   a1b2c3d4e5f6g7h8i9
   ```
   Copy this ID!

### Step 3: Add to .env File

**Option A: Manual (Recommended)**

Open `.env` file and add these lines:
```bash
# Google Search API
GOOGLE_SEARCH_API_KEY=AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
GOOGLE_SEARCH_ENGINE_ID=YOUR_SEARCH_ENGINE_ID_HERE
```

Replace `YOUR_SEARCH_ENGINE_ID_HERE` with the ID from Step 2.

**Option B: Automated Script**

Run the setup script:
```bash
SETUP_GOOGLE_SEARCH.bat
```

This will guide you through the process and automatically update `.env`.

### Step 4: Restart Grace

```bash
# Stop current Grace instance (Ctrl+C)
# Start Grace
START_GRACE.bat
```

Look for this message in the logs:
```
[GOOGLE-SEARCH] API credentials found, using Google Custom Search API
```

---

## Quick Links

- **Enable API:** https://console.cloud.google.com/apis/library/customsearch.googleapis.com
- **Create Search Engine:** https://programmablesearchengine.google.com/
- **API Console:** https://console.cloud.google.com/apis/credentials

---

## Test It Works

After restarting Grace, test the search:

```python
python -c "
from backend.services.google_search_service import google_search_service
import asyncio

async def test():
    await google_search_service.initialize()
    results = await google_search_service.search('python async programming')
    print(f'✅ Found {len(results)} results')
    for r in results[:3]:
        print(f'  - {r[\"title\"]}')

asyncio.run(test())
"
```

Expected output:
```
[GOOGLE-SEARCH] API credentials found, using Google Custom Search API
✅ Found 5 results
  - Python Asyncio Tutorial
  - Async/Await in Python
  - ...
```

---

## What This Enables

Once configured, Grace can:
- ✅ Fetch fresh web articles
- ✅ Search for latest documentation
- ✅ Find recent Stack Overflow answers
- ✅ Discover new learning resources
- ✅ Access engineering blogs
- ✅ Read academic papers

**100 free searches per day** - plenty for Grace's learning needs!

---

## Troubleshooting

### "API not enabled" Error

Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com  
Click "Enable"

### "Invalid Search Engine ID" Error

1. Go to: https://programmablesearchengine.google.com/
2. Click your search engine name
3. Look for "Search engine ID" in the Overview tab
4. Copy the entire ID (no spaces)

### Still Getting 403 Errors

Check that:
- API is enabled ✅
- Both credentials are in `.env` ✅
- Grace has been restarted ✅
- Check logs for "API credentials found" message ✅

---

## Your API Key (Saved for Reference)

```
GOOGLE_SEARCH_API_KEY=AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
```

**Security Note:** This key is only in `.env` (gitignored). It will NOT be committed to Git.

---

**Next Step:** Get your Search Engine ID from https://programmablesearchengine.google.com/ 🚀
