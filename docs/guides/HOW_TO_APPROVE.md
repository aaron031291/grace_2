# How to Grant Approvals to Grace

## 🎯 Quick Answer

When Grace shows: `[OK] Approval required: 6`

**You need to:**

1. **Keep Grace running** (don't stop `python serve.py`)
2. **Open a NEW terminal/command prompt**
3. **Navigate to the project**: `cd C:\Users\aaron\grace_2`
4. **Run the approval script**: `python approve_all.py`

---

## 📋 Step-by-Step Instructions

### Terminal 1 (Keep Running):
```bash
cd C:\Users\aaron\grace_2
python serve.py

# You'll see:
# [OK] Approval required: 6
# 
# Keep this running!
```

### Terminal 2 (New Window):
```bash
# Open a NEW terminal/command prompt
cd C:\Users\aaron\grace_2
python approve_all.py

# You'll see:
# 🔍 Fetching pending approvals...
# 📋 Found 6 pending approvals
#   ✓ Approving: GITHUB_TOKEN
#   ✓ Approving: DATABASE_ACCESS
#   ✓ Approving: FILE_SYSTEM_READ
#   ✓ Approving: FILE_SYSTEM_WRITE
#   ✓ Approving: NETWORK_ACCESS
#   ✓ Approving: LEARNING_DATA_ACCESS
# 
# ✅ Approved 6/6 requests
# 🚀 Grace is now ready!
```

### Back to Terminal 1:
Grace will now continue starting normally!

---

## 🔄 Alternative: Approve via API

If you prefer, you can approve via HTTP requests:

```bash
# Get pending approvals
curl http://localhost:8017/api/secrets/consent/pending?user_id=admin

# Approve each one
curl -X POST http://localhost:8017/api/secrets/consent/respond \
  -H "Content-Type: application/json" \
  -d '{
    "consent_id": "CONSENT_ID_HERE",
    "approved": true,
    "user_id": "admin",
    "approval_method": "manual"
  }'
```

---

## 🌐 Alternative: Approve via Web UI

1. Open browser: `http://localhost:8017`
2. Navigate to: Settings → Approvals
3. Click "Approve All" button

---

## ❓ Why Do Approvals Exist?

Grace has a governance system that requires your explicit consent for:

1. **GITHUB_TOKEN** - Access to your GitHub account
2. **DATABASE_ACCESS** - Read/write to grace.db
3. **FILE_SYSTEM_READ** - Read files from disk
4. **FILE_SYSTEM_WRITE** - Write files to disk
5. **NETWORK_ACCESS** - Make HTTP requests
6. **LEARNING_DATA_ACCESS** - Access training data

This prevents Grace from:
- Accessing credentials without permission
- Modifying files unexpectedly
- Making network calls you didn't authorize
- Using learning data inappropriately

---

## 🛡️ Security & Privacy

**In Development (your setup):**
- Safe to approve all
- You control the environment
- Easy to revoke later

**In Production:**
- Review each approval
- Grant minimal permissions
- Audit consent logs regularly

---

## 🔧 Troubleshooting

### "Cannot connect to Grace"
- Ensure Grace is running: `python serve.py`
- Check the port (default 8017)
- Try: `curl http://localhost:8017/health`

### "No approvals needed"
- They may already be approved
- Check: `python approve_all.py` again
- Grace may have auto-approved some items

### Script errors
- Ensure you're in: `C:\Users\aaron\grace_2`
- Check Python: `python --version` (should be 3.8+)
- Install dependencies: `pip install httpx`

---

## 📝 Quick Reference

```bash
# Terminal 1 - Start Grace
python serve.py

# Terminal 2 - Approve (while Grace is running)
python approve_all.py

# View pending approvals
curl http://localhost:8017/api/secrets/consent/pending?user_id=admin

# View approval stats
curl http://localhost:8017/api/secrets/consent/stats
```

---

**That's it!** Once approved, Grace will remember your choices and won't ask again unless you revoke them.
