# Secrets Vault - Migration Guide

## 🎯 Complete Migration from .env to Vault

Step-by-step guide to move all secrets to encrypted storage.

---

## Phase 1: Setup (5 minutes)

### Step 1: Generate Vault Key

```bash
# Run setup script
SETUP_VAULT.bat
```

**Or manually:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Copy the output** (looks like: `b'Z0FBQUFBQm5kV...'`)

### Step 2: Add to Environment

**Edit `.env` file:**
```bash
# Add this line
GRACE_VAULT_KEY=b'Z0FBQUFBQm5kV...'
```

### Step 3: Restart Backend

```bash
python serve.py
```

**Verify in logs:**
```
[VAULT] Encryption key loaded from environment ✓
```

---

## Phase 2: Migrate Secrets (10 minutes)

### Option A: Automated Migration (Recommended)

```bash
# Run migration script
python migrate_to_vault.py
```

**Script will:**
1. Read secrets from .env
2. POST each to /api/secrets/store
3. Encrypt and store in vault
4. Show migration summary

**Output:**
```
📤 Migrating OPENAI_API_KEY: sk-proj-...
   ✅ Stored as secret_api_key_1234567890

📤 Migrating GITHUB_TOKEN: ghp_...
   ✅ Stored as secret_token_9876543210

✅ Migration complete!
   Migrated: 6
   Skipped: 0
   Failed: 0
```

### Option B: Manual Migration (UI)

**For each secret in .env:**

```
1. Start Grace Console
2. Click "🔐 Vault"
3. Click "+ Add Secret"
4. Click quick template (e.g., "OPENAI_API_KEY")
5. Copy value from .env
6. Paste in "Secret Value" field
7. Click "🔒 Store Secret Securely"
8. Repeat for each secret
```

**Quick templates available:**
- OPENAI_API_KEY
- GITHUB_TOKEN
- GOOGLE_SEARCH_KEY
- DUCKDUCKGO_APP_KEY
- SLACK_TOKEN
- SALESFORCE_API_KEY

---

## Phase 3: Update Backend Code (30 minutes)

### File 1: Autonomous Curriculum

**File:** `backend/learning_systems/autonomous_curriculum.py`

**Find:**
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

**Replace with:**
```python
from backend.security.secure_credential_vault import credential_vault

# In async method:
openai_key = await credential_vault.get_secret("OPENAI_API_KEY")
```

**Example:**
```python
class AutonomousCurriculum:
    async def initialize(self):
        # Get key from vault
        self.openai_key = await credential_vault.get_secret("OPENAI_API_KEY")
        
        # Configure OpenAI
        import openai
        openai.api_key = self.openai_key
```

### File 2: GitHub Knowledge Miner

**File:** `backend/knowledge/github_knowledge_miner.py`

**Find:**
```python
token = os.getenv("GITHUB_TOKEN")
```

**Replace with:**
```python
from backend.security.secure_credential_vault import credential_vault

# Get from vault
token = await credential_vault.get_secret("GITHUB_TOKEN")
```

**Already implemented:**
```python
# github_knowledge_miner.py already has:
# Try to get GitHub token from secrets vault or environment
try:
    token = await credential_vault.get_secret("GITHUB_TOKEN")
except:
    token = os.getenv("GITHUB_TOKEN")
```

### File 3: Reddit Learning

**File:** `backend/learning_systems/reddit_learning.py`

**Already has vault support:**
```python
# Try to get credentials from secrets vault first
try:
    client_id = await credential_vault.get_secret("REDDIT_CLIENT_ID")
    client_secret = await credential_vault.get_secret("REDDIT_CLIENT_SECRET")
except:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
```

### File 4: Web Search Services

**Update all search services:**

```python
# In safe_web_scraper.py or web_search_service.py
from backend.security.secure_credential_vault import credential_vault

async def get_google_search_key():
    try:
        return await credential_vault.get_secret("GOOGLE_SEARCH_KEY")
    except:
        return os.getenv("GOOGLE_SEARCH_KEY")

async def perform_google_search(query: str):
    api_key = await get_google_search_key()
    # Use api_key for search
```

---

## Phase 4: Clean Up .env (5 minutes)

### Keep in .env:
```bash
# Master vault key (required)
GRACE_VAULT_KEY=b'...'

# Configuration (not secrets)
ENVIRONMENT=production
DATABASE_URL=sqlite:///./grace.db
PORT=8017
```

### Remove from .env:
```bash
# ❌ Remove these (now in vault)
# OPENAI_API_KEY=sk-...
# GITHUB_TOKEN=ghp-...
# GOOGLE_SEARCH_KEY=AIza...
# etc.
```

### Create .env.example:
```bash
# Grace Configuration
GRACE_VAULT_KEY=<generate-with-SETUP_VAULT.bat>
ENVIRONMENT=production
DATABASE_URL=sqlite:///./grace.db
PORT=8017

# Secrets are stored in encrypted vault
# Use Grace Console (🔐 Vault panel) to add secrets
```

---

## Phase 5: Verify (5 minutes)

### Test Backend Services

**Check learning service:**
```bash
# In Python shell or backend test
from backend.learning_systems.autonomous_curriculum import autonomous_curriculum

# This should retrieve from vault
await autonomous_curriculum.initialize()

# Check logs for:
# [VAULT] Secret 'OPENAI_API_KEY' retrieved by autonomous_curriculum
```

### Test in Console

```
1. Open Grace Console
2. Click "🔐 Vault"
3. See all migrated secrets
4. Click a secret
5. Click "Reveal (Logged)"
6. Value should display
7. Go to ⚖️ Governance → Audit Log
8. See access logged
```

### Test Learning Flow

```
1. Open Chat
2. Ask Grace to learn something
3. Backend should use vault-retrieved OpenAI key
4. Check backend logs for vault access
5. No errors about missing keys
```

---

## 🔄 Ongoing Operations

### Adding New Secrets

**Via Console:**
```
Vault → + Add Secret → Custom or Template → Store
```

**Via API:**
```bash
curl -X POST http://localhost:8017/api/secrets/store \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NEW_API_KEY",
    "value": "secret-value",
    "secret_type": "api_key",
    "scope": "new_service",
    "domain": "custom",
    "tags": ["new", "api"]
  }'
```

### Rotating Secrets

**UI:**
```
Vault → Select Secret → 🔄 Rotate → New Value → Reason → Confirm
```

**Example:**
```
Secret: OPENAI_API_KEY
New Value: sk-proj-new...
Reason: "Regular 90-day rotation per security policy"
```

**Logged:**
```
timestamp: 2025-11-17 10:30:00
actor: aaron
action: rotated
resource: OPENAI_API_KEY
reason: Regular 90-day rotation per security policy
```

### Deleting Secrets

**UI:**
```
Vault → Select Secret → 🗑️ Delete → Reason → Confirm
```

**Always requires reason for audit compliance**

---

## 🛡️ Security Best Practices

### 1. Master Key Security

```bash
# Store GRACE_VAULT_KEY securely
# - Use environment variable (not in code)
# - Use secrets manager in production (AWS Secrets Manager, Azure Key Vault)
# - Rotate quarterly
# - Restrict access (only ops team)
```

### 2. Secret Rotation Schedule

```
Critical secrets (production API keys): Every 90 days
Medium secrets (development keys): Every 180 days
Low secrets (non-production): Annually
```

### 3. Access Auditing

```
Weekly: Review vault audit logs
Look for:
- Unusual access patterns
- Failed access attempts
- Access from unexpected services
- High-frequency retrievals
```

### 4. Least Privilege

```
# Tag secrets with allowed services
tags: ["learning-service-only"]

# Backend enforces:
if requesting_service not in secret.allowed_services:
    raise PermissionError()
```

---

## 📊 Migration Checklist

### Pre-Migration
- [ ] Generate GRACE_VAULT_KEY
- [ ] Add to .env
- [ ] Restart backend
- [ ] Verify vault initializes

### Migration
- [ ] Run migrate_to_vault.py
- [ ] OR manually add via UI
- [ ] Verify all secrets in vault (🔐 Vault panel)
- [ ] Test secret retrieval

### Code Updates
- [ ] Update autonomous_curriculum.py
- [ ] Update github_knowledge_miner.py
- [ ] Update web search services
- [ ] Update any custom integrations
- [ ] Test all services work

### Cleanup
- [ ] Remove secrets from .env
- [ ] Keep only GRACE_VAULT_KEY
- [ ] Create .env.example
- [ ] Update documentation
- [ ] Commit changes (secrets now safe)

### Verification
- [ ] Test learning services
- [ ] Test GitHub mining
- [ ] Test web search
- [ ] Check audit logs show access
- [ ] Verify no "missing key" errors

---

## 🎯 Quick Reference

### Store Secret
```
Vault → + Add Secret → Template → Paste → Store
```

### Retrieve in Backend
```python
key = await credential_vault.get_secret("SECRET_NAME")
```

### Rotate Secret
```
Vault → Secret → Rotate → New Value → Reason
```

### Delete Secret
```
Vault → Secret → Delete → Reason → Confirm
```

### View Audit Log
```
Vault → Secret → Access History
or
Governance → Audit Log → Filter by secret
```

---

## 🎊 Summary

✅ **Secure storage** with encryption  
✅ **Governance logging** on all access  
✅ **Easy migration** from .env  
✅ **UI management** via Vault panel  
✅ **Backend integration** examples provided  
✅ **Audit trail** for compliance  

**Your secrets are now secure and governed!** 🔐

---

## 🚀 Next Actions

1. **Run:** `SETUP_VAULT.bat`
2. **Add key to .env**
3. **Run:** `python migrate_to_vault.py`
4. **Verify:** Open Vault panel in console
5. **Update:** Backend services to use vault
6. **Clean:** Remove secrets from .env
7. **Test:** All services still work

**Complete migration in ~1 hour!** ⏱️
