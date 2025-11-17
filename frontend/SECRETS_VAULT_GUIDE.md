# Secrets Vault - Complete Guide

## 🔐 Overview

The Secrets Vault is a secure credential management system integrated into Grace Console. Store API keys, tokens, and passwords with encryption, governance, and audit logging.

## 🎯 Features

### Secure Storage
- ✅ Encrypted at rest using Fernet
- ✅ Master key (GRACE_VAULT_KEY) for persistence
- ✅ Secrets never exposed in logs
- ✅ Access requires authentication

### Governance Integration
- ✅ All access logged to audit trail
- ✅ Deletion requires reason
- ✅ Retrieval is logged
- ✅ Approval workflow for sensitive secrets

### UI Features
- ✅ List all secrets (metadata only)
- ✅ Reveal secret value (with audit log)
- ✅ Copy to clipboard (logged)
- ✅ Rotate/update secrets
- ✅ Delete with reason
- ✅ Quick templates for common secrets
- ✅ Audit log viewer per secret

---

## 🚀 Quick Start

### 1. Set Master Vault Key (Backend)

**Generate a key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Set environment variable:**
```bash
# Windows
set GRACE_VAULT_KEY=your-generated-key

# Or add to .env
GRACE_VAULT_KEY=your-generated-key
```

Without this, a new key is generated on each restart (secrets won't persist).

### 2. Open Vault in Console

```
1. Start Grace Console (npm run dev)
2. Click "🔐 Vault" button
3. Vault panel opens
```

---

## 💾 Storing Secrets

### Method 1: UI (Recommended)

**Step-by-step:**
```
1. Click "🔐 Vault"
2. Click "+ Add Secret"
3. Choose from quick templates:
   - OPENAI_API_KEY
   - GITHUB_TOKEN
   - GOOGLE_SEARCH_KEY
   - etc.
4. OR enter custom name
5. Select type (API Key, Token, Password, Certificate)
6. Paste secret value
7. Add domain (optional): ai, crm, search, etc.
8. Add tags (optional): learning, rag, production
9. Click "🔒 Store Secret Securely"
```

**Quick Template:**
```
Click template button → Auto-fills name, type, domain
Just paste your secret value and click Store
```

### Method 2: API (Programmatic)

```bash
curl -X POST http://localhost:8017/api/secrets/store \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OPENAI_API_KEY",
    "value": "sk-...",
    "secret_type": "api_key",
    "scope": "learning",
    "environment": "production",
    "tags": ["ai", "rag"]
  }'
```

**Response:**
```json
{
  "secret_id": "secret_api_key_1234567890",
  "name": "OPENAI_API_KEY",
  "type": "api_key",
  "encrypted": true,
  "requires_approval": true
}
```

---

## 🔍 Viewing Secrets

### List Secrets (Safe)

**What you see:**
- Secret name
- Type (API key, token, etc.)
- Domain
- Tags
- Created date
- Last used
- Use count

**What you DON'T see:**
- ❌ Secret value (never shown in list)

### View Secret Details

**Click a secret card:**
- Metadata displayed
- Tags shown
- Audit log visible (last 5 accesses)
- Actions available

### Reveal Secret Value

**To see the actual value:**
```
1. Click secret card
2. Detail panel opens
3. Value shown as: ••••••••••••••••
4. Click "👁️ Reveal (Logged)"
5. Value displayed
6. This action is logged to audit trail
```

**Security:**
- Every reveal is logged
- Actor (user ID) recorded
- Timestamp tracked
- Displayed in audit log

---

## 📋 Using Secrets

### Copy to Clipboard

**Safe method:**
```
1. Select secret
2. Click "📋 Copy to Clipboard"
3. Secret copied to clipboard
4. Access logged
5. Use in your application
```

**Clipboard auto-clears after paste (browser security)**

### In Chat (/vault command)

**Future enhancement:**
```
User: /vault get OPENAI_API_KEY
Grace: Secret copied to clipboard (access logged)
```

### In Code

**Backend retrieval:**
```python
from backend.security.secure_credential_vault import credential_vault

# Get secret
api_key = await credential_vault.get_secret("OPENAI_API_KEY")

# Use in service
openai.api_key = api_key
```

---

## 🔄 Rotating Secrets

### When to Rotate
- Key compromised
- Regular security policy (e.g., every 90 days)
- Key leaked in logs
- Team member departure

### How to Rotate

**Via UI:**
```
1. Select secret
2. Click "🔄 Rotate Secret"
3. Enter new value
4. Enter reason: "Regular 90-day rotation"
5. Click Confirm
6. Old value archived
7. New value encrypted and stored
8. Rotation logged
```

**Rotation audit log:**
```json
{
  "timestamp": "2025-11-17T10:30:00Z",
  "actor": "aaron",
  "action": "rotated",
  "resource": "OPENAI_API_KEY",
  "reason": "Regular 90-day rotation"
}
```

---

## 🗑️ Deleting Secrets

### With Governance

**Process:**
```
1. Select secret
2. Click "🗑️ Delete"
3. Prompt: "Reason for deletion (required for audit):"
4. Enter reason: "Key no longer needed"
5. Confirm deletion
6. Secret deleted (soft delete)
7. Logged to audit trail
```

**Audit entry:**
```json
{
  "timestamp": "2025-11-17T10:35:00Z",
  "actor": "aaron",
  "action": "deleted",
  "resource": "OLD_API_KEY",
  "reason": "Key no longer needed",
  "result": "success"
}
```

---

## 📊 Audit Log

### Per-Secret Audit

**View access history:**
```
Select secret → Detail panel → Access History section

Shows:
- Timestamp of access
- Action (created, accessed, rotated, deleted)
- Actor (who did it)
```

**Example log:**
```
2025-11-17 10:30:00  created   aaron
2025-11-17 10:31:15  accessed  grace-learning-service
2025-11-17 10:32:00  accessed  aaron
2025-11-17 11:00:00  rotated   aaron
```

### Global Audit

**View all vault operations:**
```
Go to: ⚖️ Governance → Audit Log tab
Filter by: resource type = "secret"

Shows all vault operations system-wide
```

---

## 🔒 Security Features

### Encryption
```python
# Secrets encrypted using Fernet (AES-128)
cipher = Fernet(GRACE_VAULT_KEY)
encrypted_value = cipher.encrypt(secret.encode())

# Stored encrypted
# Decrypted only on authorized retrieval
```

### Access Control
```typescript
// Every access includes user context
headers: {
  'Authorization': 'Bearer ${token}',
  'X-User-ID': 'aaron',
  'X-Client': 'grace-console'
}

// Backend logs access
await immutable_log.append(
  actor=user_id,
  action='retrieve_secret',
  resource=secret_name,
  subsystem='vault'
);
```

### Never Logged
- ❌ Secret values NEVER in logs
- ❌ Secret values NEVER in responses (except explicit get)
- ❌ Secret values NEVER in error messages
- ✅ Only metadata logged
- ✅ Access events logged
- ✅ Encrypted values stored

---

## 🎯 Common Use Cases

### Store OpenAI API Key

**UI:**
```
1. Click "🔐 Vault"
2. Click "+ Add Secret"
3. Click "OPENAI_API_KEY" template
4. Paste your sk-... key
5. Click "Store Secret Securely"
```

**Result:**
- Encrypted and stored
- Tagged with "ai" domain
- Available to learning services
- Access logged

### Store GitHub Token

**UI:**
```
1. Click "GITHUB_TOKEN" template
2. Paste your ghp_... token
3. Domain: "code"
4. Tags: "github", "api"
5. Store
```

**Usage in backend:**
```python
# Automatically retrieved by GitHub knowledge miner
token = await credential_vault.get_secret("GITHUB_TOKEN")
```

### Store Salesforce Credentials

**UI:**
```
1. Custom secret
2. Name: "SALESFORCE_API_KEY"
3. Type: API Key
4. Domain: "crm"
5. Paste key
6. Store
```

**Usage:**
```python
# CRM integrations auto-retrieve
api_key = await credential_vault.get_secret("SALESFORCE_API_KEY")
```

---

## 🛡️ Best Practices

### 1. Use Descriptive Names
```
✅ OPENAI_API_KEY_PRODUCTION
❌ key1
```

### 2. Tag Appropriately
```
tags: ["production", "ai", "high-value"]
```

### 3. Set Domain
```
domain: "ai"  // Groups related secrets
```

### 4. Rotate Regularly
```
Set calendar reminder: Rotate every 90 days
```

### 5. Delete Unused Secrets
```
Always provide reason for audit
```

### 6. Review Audit Logs
```
Check Access History to see who used what
```

---

## 🔧 Integration with Learning Services

### Autonomous Curriculum

**Before (hardcoded):**
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

**After (vault):**
```python
from backend.security.secure_credential_vault import credential_vault

api_key = await credential_vault.get_secret("OPENAI_API_KEY")
openai.api_key = api_key
```

### Reddit Learning

**Retrieve Reddit credentials:**
```python
reddit_client_id = await credential_vault.get_secret("REDDIT_CLIENT_ID")
reddit_client_secret = await credential_vault.get_secret("REDDIT_CLIENT_SECRET")
```

### GitHub Knowledge Miner

**Auto-retrieves token:**
```python
# Already implemented in github_knowledge_miner.py
token = await credential_vault.get_secret("GITHUB_TOKEN")
```

---

## 📊 Vault Statistics

**View stats in UI:**
- Total secrets stored
- Secrets by type (API keys, tokens, etc.)
- Secrets by domain (ai, crm, search, etc.)
- Secrets expiring soon

**Access programmatically:**
```typescript
const stats = await getVaultStats();
console.log(stats);
// {
//   total_secrets: 5,
//   by_type: { api_key: 3, token: 2 },
//   by_domain: { ai: 2, crm: 1, search: 2 },
//   expires_soon: 1
// }
```

---

## 🎨 UI Features

### Quick Templates
Pre-configured templates for:
- OPENAI_API_KEY
- GITHUB_TOKEN
- GOOGLE_SEARCH_KEY
- DUCKDUCKGO_APP_KEY
- SLACK_TOKEN
- SALESFORCE_API_KEY

Click template → Auto-fills name, type, domain → Just paste value

### Visual Indicators
- 🔑 API Key icon
- 🎫 Token icon
- 🔒 Password icon
- 📜 Certificate icon
- ⚠️ Expiring soon badge

### Copy Success Feedback
```
Click "Copy to Clipboard"
→ Button changes to "✅ Copied!" for 2 seconds
→ Returns to "📋 Copy to Clipboard"
```

---

## 🧪 Testing

### Test Secret Storage

```
1. Open Vault
2. Click "+ Add Secret"
3. Name: "TEST_KEY"
4. Value: "test-value-123"
5. Type: API Key
6. Store
7. ✓ Should appear in list
8. Click card
9. Click "Reveal"
10. ✓ Should show "test-value-123"
```

### Test Audit Logging

```
1. Reveal a secret
2. Go to Governance → Audit Log
3. Filter by resource: secret name
4. ✓ Should see "accessed" entry with your user ID
```

### Test Copy

```
1. Select secret
2. Click "Copy to Clipboard"
3. Paste in notepad
4. ✓ Secret value pasted
5. Check Governance → Audit Log
6. ✓ Should see "accessed" entry
```

---

## 🔐 Security Recommendations

### 1. Set GRACE_VAULT_KEY
```bash
# Generate strong key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set in environment
export GRACE_VAULT_KEY="<generated-key>"
```

### 2. Restrict Access
```bash
# Set file permissions on vault files
chmod 600 .grace_vault/*
```

### 3. Regular Audits
```
Weekly: Review audit logs
Monthly: Rotate high-value secrets
Quarterly: Review and remove unused secrets
```

### 4. Use Domains
```
Tag secrets by domain for easy RBAC:
- "ai" domain → Only AI services
- "crm" domain → Only CRM integrations
- "admin" domain → Requires approval
```

---

## 📋 API Reference

### List Secrets
```typescript
GET /api/vault/secrets
Response: [{ id, name, type, domain, tags, created_at, last_used }]
```

### Create Secret
```typescript
POST /api/vault/secrets
Body: { name, value, type, domain, tags }
Response: { id, name, status: 'encrypted' }
```

### Get Secret Value
```typescript
GET /api/vault/secrets/{name}
Response: { name, value, retrieved_at }
// ⚠️ Access is logged!
```

### Rotate Secret
```typescript
POST /api/vault/secrets/{name}/rotate
Body: { value: new_value, reason }
Response: { status, rotated_at }
```

### Delete Secret
```typescript
DELETE /api/vault/secrets/{name}
Body: { reason }
Response: { status, audit_log_id }
```

### Get Audit Log
```typescript
GET /api/vault/secrets/{name}/audit
Response: [{ timestamp, actor, action, result }]
```

---

## 🎯 Integration Examples

### Store OpenAI Key via UI

```
1. Open Vault
2. "+ Add Secret"
3. Click "OPENAI_API_KEY" template
4. Paste: sk-proj-...
5. Store
6. ✓ Now learning services can use it
```

### Use in Learning Service

```python
# In autonomous_curriculum.py
from backend.security.secure_credential_vault import credential_vault

async def get_openai_client():
    api_key = await credential_vault.get_secret("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)
```

### Store All Required Secrets

**For full Grace functionality:**
```
Required:
- OPENAI_API_KEY (for AI models)

Optional:
- GITHUB_TOKEN (for code knowledge)
- GOOGLE_SEARCH_KEY (for web search)
- SLACK_TOKEN (for notifications)
- SALESFORCE_API_KEY (for CRM)
```

---

## 🚨 Important Notes

### Never Hardcode Secrets
```python
# ❌ Bad
OPENAI_API_KEY = "sk-..."

# ✅ Good
api_key = await credential_vault.get_secret("OPENAI_API_KEY")
```

### Always Provide Reasons
```typescript
// For deletion
await deleteSecret(name, "Key compromised, rotating");

// For rotation  
await rotateSecret(name, newValue, "Regular 90-day rotation");
```

### Check Audit Logs
```
Regular security practice:
- Review who accessed what
- Look for unusual patterns
- Verify all accesses are legitimate
```

---

## 📊 Vault UI Components

### Secrets List
- Grid layout
- Cards with icons
- Type and domain badges
- Expiry warnings
- Click to select

### Detail Panel
- Secret metadata
- Reveal/hide value toggle
- Access history (last 5)
- Actions: Copy, Rotate, Delete

### Add Secret Form
- Quick templates
- Custom input fields
- Type selector
- Domain and tags
- Security notice

---

## 🎉 Summary

✅ **Secure credential storage** - Encrypted at rest  
✅ **Governance compliant** - All access logged  
✅ **Easy to use** - Quick templates, simple UI  
✅ **Audit trail** - Complete access history  
✅ **Integration ready** - Backend services can retrieve  
✅ **Safe operations** - Copy to clipboard, reveal with logging  

**The Secrets Vault is production-ready and integrated into Grace Console!** 🔐

---

## 🚀 Quick Commands

**Open Vault:**
```
Click: 🔐 Vault
```

**Add Secret:**
```
Click: + Add Secret → Choose template → Paste value → Store
```

**Reveal Secret:**
```
Select secret → Click: 👁️ Reveal (Logged)
```

**Copy Secret:**
```
Select secret → Click: 📋 Copy to Clipboard
```

**All operations are logged for security and compliance!** 🛡️
