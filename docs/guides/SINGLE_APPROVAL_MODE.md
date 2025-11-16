# Single Approval Mode

## 🎯 Overview

Instead of 6 separate approval prompts, Grace now uses **ONE single approval point** for all operations.

---

## ✅ How to Start Grace with Single Approval

### Option 1: Use the Batch File (Easiest)
```bash
START_GRACE_APPROVED.bat
```

This automatically grants approval for all operations.

---

### Option 2: Set Environment Variable Once
```bash
set GRACE_AUTO_APPROVE=true
set GRACE_ENV=development
set GRACE_SINGLE_APPROVAL=true
python serve.py
```

---

### Option 3: Use .env.development File
Copy `.env.development` to `.env`:
```bash
copy .env.development .env
python serve.py
```

The `.env` file contains:
```
GRACE_AUTO_APPROVE=true
GRACE_ENV=development
GRACE_SINGLE_APPROVAL=true
```

---

## 🔐 What Gets Approved

With single approval, you authorize:

1. **Database Access** - Read/write to grace.db
2. **File System Access** - Read/write to directories  
3. **Network Access** - API calls, external services
4. **Secrets Access** - Environment variables, API keys
5. **Execution Permissions** - Run scripts, commands
6. **Learning Data Access** - Access to training data

All with **ONE approval** instead of 6.

---

## 🚀 Recommended Setup

For development, add this to your `.env` file:

```bash
# Single Approval Mode
GRACE_AUTO_APPROVE=true
GRACE_ENV=development
GRACE_SINGLE_APPROVAL=true
GRACE_BATCH_CONSENT=true
GRACE_SKIP_CONSENT_PROMPTS=true
```

Then just run:
```bash
python serve.py
```

Grace will start immediately with all permissions granted.

---

## 🔄 For Production

In production, you'll want more granular control:

```bash
# Production Mode - Individual Approvals
GRACE_ENV=production
GRACE_SINGLE_APPROVAL=false
GRACE_AUTO_APPROVE=false
```

This restores the 6 individual approval prompts for security.

---

## 🎯 Quick Commands

```bash
# Development (single approval, auto-granted)
START_GRACE_APPROVED.bat

# Or manually:
set GRACE_AUTO_APPROVE=true && python serve.py

# Check approval status (from Python):
from backend.security.single_approval import single_approval
print(single_approval.get_status())
```

---

## 📋 Environment Variables Reference

| Variable | Values | Effect |
|----------|--------|--------|
| `GRACE_AUTO_APPROVE` | true/false | Auto-grant approval on startup |
| `GRACE_ENV` | development/production | Environment mode |
| `GRACE_SINGLE_APPROVAL` | true/false | Use single approval point |
| `GRACE_BATCH_CONSENT` | true/false | Batch all consents together |
| `GRACE_SKIP_CONSENT_PROMPTS` | true/false | Skip individual prompts |

---

**Status**: Single approval mode configured! Start Grace with pre-granted permissions. ✅
