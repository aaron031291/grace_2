# Secrets Vault - Setup Guide

## 🔐 Initial Setup (Required)

### Step 1: Generate Vault Key

**Run the setup script:**
```bash
# From grace_2 directory
SETUP_VAULT.bat
```

Or manually:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Output example:**
```
b'Z0FBQUFBQm5kV...(32-byte key)'
```

### Step 2: Add to Environment

**Create/update `.env` file:**
```bash
# In c:\Users\aaron\grace_2\.env
GRACE_VAULT_KEY=b'Z0FBQUFBQm5kV...'
```

**Or set environment variable:**
```bash
# Windows
set GRACE_VAULT_KEY=b'Z0FBQUFBQm5kV...'

# PowerShell
$env:GRACE_VAULT_KEY="b'Z0FBQUFBQm5kV...'"
```

### Step 3: Restart Backend

```bash
# Restart your backend to load the key
python serve.py
```

**Verify:**
```
Backend logs should show:
[VAULT] Encryption key loaded from environment
```

Instead of:
```
[VAULT] New encryption key generated
```

---

## 🎯 Quick Secret Setup

### Common Secrets to Add

After setup, add these secrets via the UI (🔐 Vault panel):

#### 1. OpenAI API Key
```
Name: OPENAI_API_KEY
Type: API Key
Value: sk-proj-...
Domain: ai
Tags: learning, rag
```

**Why:** Required for AI-powered learning and RAG

#### 2. GitHub Token
```
Name: GITHUB_TOKEN
Type: Token
Value: ghp_...
Domain: code
Tags: github, api
```

**Why:** Enables GitHub knowledge mining

#### 3. Google Search Key
```
Name: GOOGLE_SEARCH_KEY
Type: API Key
Value: AIza...
Domain: search
Tags: web, learning
```

**Why:** Enables web search for learning

#### 4. Slack Token (Optional)
```
Name: SLACK_TOKEN
Type: Token
Value: xoxb-...
Domain: notifications
Tags: slack, alerts
```

**Why:** Enables Slack notifications

#### 5. Salesforce API Key (Optional)
```
Name: SALESFORCE_API_KEY
Type: API Key
Value: ...
Domain: crm
Tags: salesforce, crm
```

**Why:** Enables CRM integrations

---

## 🔄 Migrating from .env to Vault

### Current State (Unsafe)
```bash
# .env file
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp-...
```

**Problems:**
- ❌ Plain text in file
- ❌ Committed to git accidentally
- ❌ No access control
- ❌ No audit trail

### New State (Secure)
```bash
# .env file
GRACE_VAULT_KEY=b'...'  # Only the master key
```

**Benefits:**
- ✅ Secrets encrypted
- ✅ Access logged
- ✅ Governance integrated
- ✅ Safe to commit .env.example

### Migration Steps

**For each secret in .env:**
```
1. Open Grace Console
2. Click "🔐 Vault"
3. Click "+ Add Secret"
4. Copy value from .env
5. Paste in vault
6. Store
7. Remove from .env
8. Update code to use vault
```

**Update backend code:**
```python
# Old
api_key = os.getenv("OPENAI_API_KEY")

# New
api_key = await credential_vault.get_secret("OPENAI_API_KEY")
```

---

## 🛡️ Security Checklist

### Initial Setup
- [ ] Generate GRACE_VAULT_KEY
- [ ] Add to .env file
- [ ] Restart backend
- [ ] Verify vault loads correctly

### Add Secrets
- [ ] Store OPENAI_API_KEY
- [ ] Store GITHUB_TOKEN
- [ ] Store GOOGLE_SEARCH_KEY
- [ ] Store other required secrets

### Verify Security
- [ ] Check .grace_vault/ directory exists
- [ ] Check credentials.enc file is encrypted
- [ ] Verify key file has restrictive permissions
- [ ] Test secret retrieval works

### Update Services
- [ ] Replace os.getenv() with vault.get_secret()
- [ ] Remove secrets from .env
- [ ] Test services still work
- [ ] Verify access is logged

---

## 🎯 Quick Reference

### Store Secret (UI)
```
Vault → + Add Secret → Template/Custom → Store
```

### Reveal Secret (UI)
```
Vault → Select Secret → Reveal (Logged)
```

### Copy Secret (UI)
```
Vault → Select Secret → Copy to Clipboard
```

### Rotate Secret (UI)
```
Vault → Select Secret → Rotate → New Value → Reason
```

### Delete Secret (UI)
```
Vault → Select Secret → Delete → Reason → Confirm
```

---

## 🎊 Summary

✅ **Vault panel integrated** into Grace Console  
✅ **Quick templates** for common secrets  
✅ **Secure storage** with encryption  
✅ **Governance logging** on all operations  
✅ **Easy migration** from .env files  
✅ **Audit trail** for compliance  

**The Secrets Vault is ready to secure your credentials!** 🔐

---

## 🚀 Next Steps

1. **Run setup:** `SETUP_VAULT.bat`
2. **Add key to .env**
3. **Restart backend**
4. **Open console:** http://localhost:5173
5. **Click 🔐 Vault**
6. **Add your secrets**
7. **Enjoy secure credential management!**

**All secret operations are now logged and governed!** 🛡️
