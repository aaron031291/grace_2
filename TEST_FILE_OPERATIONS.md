# 🧪 Test File Operations - Step by Step

## After Restart: Test Everything Works

### Test 1: Verify Backend Routes (30 seconds)

Open a new terminal:
```bash
cd c:\Users\aaron\grace_2
python test_api.py
```

**Expected output:**
```
✓ /api/books/stats → 200
✓ /api/books/recent → 200
✓ /api/librarian/file-operations → 200
✓ /api/librarian/organization-suggestions → 200
```

**If you see 404s:** Backend didn't load routes. Check backend terminal for errors.

---

### Test 2: Create File Operations (2 minutes)

Create test files to populate the organizer:

```bash
# Create several test files in wrong locations
echo "Bitcoin trading strategies" > grace_training\crypto_guide.txt
echo "Startup failure analysis" > grace_training\startup_notes.txt
echo "Sales techniques" > grace_training\sales_tips.txt
echo "Python code examples" > grace_training\code_sample.py
```

**Now in UI:**
1. Open http://localhost:5173
2. Click "Memory Studio"
3. Click "🗂️ Organizer" tab
4. Click "Scan for Unorganized Files" button (bottom)
5. Wait 2-3 seconds

**You should see:**
- Left panel: 4 suggestions appear
- Each with confidence score
- Reasoning bullets
- [Apply] [Dismiss] buttons

6. Click "Apply" on one suggestion
7. Right panel: Operation appears with **YELLOW "UNDO" BUTTON**

---

### Test 3: Test UNDO (1 minute)

**In Organizer tab, right panel:**

1. Find the operation you just applied
2. Click the **yellow "UNDO" button**
3. Watch for notification: "✅ Undo successful"
4. Operation shows "UNDONE" badge
5. File is restored to original location

**Verify:**
```bash
# Check file is back
dir grace_training\crypto_guide.txt
# Should exist again
```

---

### Test 4: Test Co-pilot (1 minute)

**Bottom-right corner:**

1. Click purple "Librarian Co-pilot" button
2. Chat interface opens
3. Click quick action: "Check book ingestion status"
4. See response: "You have 0 books. 0 have high trust scores."
5. Type question: "how do I undo?"
6. Get response explaining Organizer tab

---

### Test 5: Test Command Palette (30 seconds)

**Anywhere in app:**

1. Press **Ctrl+K**
2. Command palette opens
3. Type "organizer"
4. See: "Go to File Organizer"
5. Press Enter
6. Organizer tab opens

---

### Test 6: Add a Real Book (5 minutes)

**Create a test PDF:**
```bash
echo %PDF-1.4
Test Book: Business Strategies
Author: Test Author

Chapter 1: Introduction
This book covers essential business strategies for startups.

Chapter 2: Growth
Focus on sustainable growth and customer acquisition.

Chapter 3: Scaling
Learn how to scale your operations effectively. > grace_training\documents\books\test_business_book.pdf
```

**In UI:**
1. Watch top-right: Notification "📚 Book Detected"
2. Click "📚 Books" tab
3. Click "Progress" sub-tab
4. Watch activity feed update in real-time
5. Stats should update: Total Books: 0 → 1
6. After ~30 seconds: "✅ Ingestion Complete"

**Then:**
7. Click "Library" sub-tab
8. See your book listed
9. Click on it
10. Details panel opens on right
11. Click "Summarize" button
12. Co-pilot query triggers

---

### Test 7: Test Onboarding (1 minute)

**Clear onboarding flag:**
```javascript
// In browser console (F12):
localStorage.removeItem('grace_onboarding_complete');
// Then refresh page
```

**Should see:**
- Onboarding overlay appears
- 5-step walkthrough
- Progress bar at top
- Can skip or step through

---

## ✅ Success Checklist

After all tests, you should have verified:

- [ ] Backend routes work (test_api.py passes)
- [ ] Organizer tab visible and loads
- [ ] File suggestions appear after scan
- [ ] **UNDO button appears and works**
- [ ] Co-pilot button visible and responds
- [ ] Command palette opens with Ctrl+K
- [ ] Books tab shows ingestion
- [ ] Notifications appear for events
- [ ] Onboarding appears on first load

---

## 🐛 If Something Doesn't Work

### Undo Button Not Visible

**Cause:** No operations yet

**Fix:** Run Test 2 to create operations first

---

### Organizer Tab Shows Empty Panels

**Cause:** No files to organize

**Fix:** Run Test 2 to create test files, then scan

---

### Co-pilot Button Not Visible

**Cause:** Component not rendered

**Check:**
1. Browser console (F12) for errors
2. Is LibrarianCopilot imported in App.tsx? (Yes, I added it)
3. Hard refresh: Ctrl+Shift+R

**Fix:** Clear browser cache completely

---

### API Returns 404

**Cause:** Routes not loaded

**Check backend terminal for:**
```
Book dashboard router registered: /api/books/*
```

**If missing:** Backend didn't load routes properly. Check for import errors.

---

### Nothing Shows Up

**Nuclear option:**
```bash
# Kill everything
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Clear caches
del /S /Q backend\__pycache__
rmdir /S /Q frontend\dist
rmdir /S /Q frontend\node_modules\.vite

# Restart
python serve.py                    # Terminal 1
cd frontend && npm run dev         # Terminal 2

# Browser: Close all tabs, open new window
http://localhost:5173
```

---

## 📊 Expected Results After All Tests

### Database should have:
- 4 file operations (from Test 2)
- 1 undo operation (from Test 3)
- 1 book document (from Test 6)
- Several chunks (from book ingestion)
- Insights (summaries/flashcards)
- Librarian log entries

### UI should show:
- Organizer with recent operations
- Books tab with 1 book
- Trust score for book
- Co-pilot with message history

---

## 🎯 Next Steps After Testing

1. **Drop your real 14 books** into `grace_training/documents/books/`
2. **Watch them process** (3 at a time, ~15-20 min total)
3. **Check trust scores** in Books tab
4. **Query books** using co-pilot
5. **Quiz yourself** with flashcards

---

**Start with Test 1 and work through them all!** 🧪

Let me know which test you're on and if anything fails! 🚀
