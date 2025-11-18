# Get Google Search Engine ID - Step by Step

**You need to sign in with your Google account to create the search engine.**

---

## Steps (2 minutes)

### 1. Open the Programmable Search Page

Go to: **https://programmablesearchengine.google.com/controlpanel/create**

(This requires Google account sign-in)

---

### 2. Fill in the Form

After signing in, you'll see a form. Fill it out like this:

**Search engine name:**
```
Grace Web Learning
```

**What to search:**
- Select: ☑ **"Search the entire web"**
- OR leave "Sites to search" EMPTY

**Language:**
```
English
```

**Search engine keywords:**
```
ai learning autonomous
```
(Optional, can leave blank)

---

### 3. Create the Search Engine

Click the **"Create"** button at the bottom

---

### 4. Get Your Search Engine ID

After creating, you'll be redirected to the control panel.

Look for one of these:
- **"Search engine ID"** field
- **"CX"** value
- Code snippet showing something like `cx: 'a1b2c3d4e5f6g7h8i9'`

**Copy the entire ID** (looks like random letters/numbers)

Example format:
```
a1b2c3d4e5f6g7h8i9
```
OR
```
012345678901234567890:abcdefghijk
```

---

### 5. Add to Grace Configuration

**Open `.env` file** in Grace's root directory and add these two lines:

```bash
GOOGLE_SEARCH_API_KEY=AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
GOOGLE_SEARCH_ENGINE_ID=paste-your-id-here
```

Replace `paste-your-id-here` with the ID you copied.

**Save the file.**

---

### 6. Restart Grace

```bash
# Stop Grace (Ctrl+C in the terminal)
# Start Grace again
python server.py
```

**Look for this message:**
```
[GOOGLE-SEARCH] API credentials found, using Google Custom Search API
```

---

## Visual Guide

### What the Form Looks Like:

```
┌─────────────────────────────────────────────┐
│ Name of the search engine:                  │
│ Grace Web Learning                          │
├─────────────────────────────────────────────┤
│ What to search:                             │
│ ○ Search only included sites                │
│ ● Search the entire web                     │
│                                             │
│ Sites to search (leave empty):              │
│ [                                         ] │
├─────────────────────────────────────────────┤
│ Language:                                   │
│ English ▼                                   │
├─────────────────────────────────────────────┤
│                      [Create]               │
└─────────────────────────────────────────────┘
```

### After Creation:

```
┌─────────────────────────────────────────────┐
│ Search engine: Grace Web Learning           │
├─────────────────────────────────────────────┤
│ Search engine ID: a1b2c3d4e5f6g7h8i9       │  ← Copy this!
├─────────────────────────────────────────────┤
│ Public URL: https://cse.google.com/cse?... │
└─────────────────────────────────────────────┘
```

---

## Quick Reference

| Step | What | Where |
|------|------|-------|
| 1 | Sign in | https://programmablesearchengine.google.com/controlpanel/create |
| 2 | Name | "Grace Web Learning" |
| 3 | Search | "Search the entire web" |
| 4 | Create | Click "Create" button |
| 5 | Copy ID | Copy "Search engine ID" value |
| 6 | Add to .env | Both API key and Search Engine ID |
| 7 | Restart | `python server.py` |

---

## What You Already Have

✅ **Google API Key:**
```
AIzaSyDC5fDHP42rV4g_PO-QY76aX63N_qMnNwE
```

⏳ **Search Engine ID:**
```
Need to get from: https://programmablesearchengine.google.com/controlpanel/create
```

---

## After Setup

Grace will show:
```
[GOOGLE-SEARCH] API credentials found, using Google Custom Search API
[GOOGLE-SEARCH] Search service initialized with 10 trusted domains
```

And you'll be able to:
- ✅ Fetch fresh web articles
- ✅ Search for latest documentation
- ✅ Learn from recent blog posts
- ✅ Access Stack Overflow answers
- ✅ 100 free searches per day

**No more network timeouts or 403 errors!**

---

## Need Help?

**Can't find Search Engine ID after creating?**
- Go to: https://programmablesearchengine.google.com/controlpanel/all
- Click your search engine name
- Look in the "Setup" or "Basics" tab for "Search engine ID"

**Getting errors when creating?**
- Make sure you're signed into a Google account
- Try different browser if issues persist
- Or create in incognito mode

---

**Direct link:** https://programmablesearchengine.google.com/controlpanel/create  
**Status:** Waiting for your Search Engine ID to complete setup  
**Time needed:** 2 minutes
