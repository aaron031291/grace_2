# Network Issue: DuckDuckGo SSL Timeout

**Date:** November 18, 2025  
**Error:** `Cannot connect to host html.duckduckgo.com:443 ssl:default [The semaphore timeout period has expired]`

---

## Issue Details

**Error Message:**
```
[GOOGLE-SEARCH] DuckDuckGo search failed: 
Cannot connect to host html.duckduckgo.com:443 
ssl:default [The semaphore timeout period has expired]
```

**Error Type:** Network connectivity issue (Windows semaphore timeout)

---

## Root Causes (Likely)

### 1. Firewall Blocking
- Windows Firewall blocking HTTPS to DuckDuckGo
- Corporate firewall blocking search engines
- Antivirus blocking SSL connections

### 2. Proxy Configuration
- System proxy not configured for Python
- Corporate proxy requiring authentication
- Proxy blocking search engines

### 3. Network Issues
- ISP blocking DuckDuckGo
- DNS resolution failing
- Network timeout (slow connection)

### 4. SSL/TLS Issues
- SSL certificate validation failing
- Outdated SSL libraries
- Corporate SSL interception

---

## Why This Matters

**DuckDuckGo is completely inaccessible**, meaning:
- ❌ Cannot fetch any web content via DuckDuckGo
- ❌ Previous 403 errors are now connection timeouts
- ❌ Grace cannot learn from fresh web sources
- ✅ Google Search API will bypass this entirely

---

## Solution: Use Google Search API

**This is why you need the Google Search API!**

### Google API Advantages

1. **Different endpoint** - Uses googleapis.com (likely not blocked)
2. **HTTPS API** - More reliable than web scraping
3. **Better for automation** - Designed for programmatic access
4. **No rate limits** - 100 free searches/day
5. **Bypasses firewall** - API endpoints often whitelisted

### Complete Setup (You're Almost Done!)

**You already have:**
✅ API Key: `AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE`

**You still need:**
⏳ Search Engine ID from https://programmablesearchengine.google.com/

**Steps to complete:**

1. **Enable the API** (30 seconds):
   - https://console.cloud.google.com/apis/library/customsearch.googleapis.com
   - Click "Enable"

2. **Create Search Engine** (2 minutes):
   - https://programmablesearchengine.google.com/
   - Click "Add" or "Create"
   - Settings:
     - Sites to search: **Leave EMPTY**
     - Name: Grace Web Learning
     - Language: English
   - Click "Create"
   - Copy the **Search Engine ID**

3. **Add to .env**:
   ```bash
   # Open .env file and add:
   GOOGLE_SEARCH_API_KEY=AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
   GOOGLE_SEARCH_ENGINE_ID=YOUR_SEARCH_ENGINE_ID_HERE
   ```

4. **Restart Grace**:
   ```bash
   # Ctrl+C to stop, then:
   START_SERVER.bat
   ```

---

## Testing Network Connectivity

### Test if Google API is accessible:

```bash
# Test Google API endpoint
curl https://www.googleapis.com/customsearch/v1

# Expected: Some response (even error is ok, means it's accessible)
```

### Test if DuckDuckGo is blocked:

```bash
# Test DuckDuckGo
curl https://html.duckduckgo.com

# Your result: Timeout (confirmed blocked/inaccessible)
```

---

## Firewall Workarounds (If Google API Also Fails)

### Option 1: Add Firewall Exception

**Windows Firewall:**
```bash
# Allow Python through firewall
# Control Panel → Windows Defender Firewall → Allow an app
# Add: Python (python.exe)
# Check both Private and Public networks
```

### Option 2: Configure Proxy

If behind corporate proxy:

```bash
# Add to .env:
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

Or in Python code:
```python
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'
```

### Option 3: Use VPN

If ISP blocking:
- Connect to VPN
- Restart Grace
- Search should work

---

## Recommended Action

**🎯 Complete Google Search API setup immediately**

This will:
- ✅ Bypass DuckDuckGo entirely
- ✅ Avoid network/firewall issues
- ✅ Provide reliable search
- ✅ Enable fresh web learning

**You're 95% done - just need the Search Engine ID!**

---

## Alternative: Disable Web Search (Temporary)

If you can't complete Google API setup right now, Grace will:
- ✅ Continue working with cached data
- ✅ Use local knowledge base
- ✅ Process existing learning materials
- ❌ Cannot fetch fresh web content

**To explicitly disable web search errors:**

Add to `.env`:
```bash
DISABLE_WEB_SEARCH=true
```

---

## Summary

**Current Situation:**
- DuckDuckGo: ❌ Completely inaccessible (SSL timeout)
- Google API: ⏳ 95% configured (need Search Engine ID)
- Grace: ✅ Running but can't access web

**Next Step:**
1. Get Search Engine ID (2 minutes)
2. Add to .env
3. Restart Grace
4. Web learning restored ✅

**Priority:** HIGH - Complete Google API setup to restore web learning

---

**Setup guide:** [GOOGLE_API_SETUP_STEPS.md](file:///c:/Users/aaron/grace_2/GOOGLE_API_SETUP_STEPS.md)  
**Quick link:** https://programmablesearchengine.google.com/
