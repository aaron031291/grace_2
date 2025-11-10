# GitHub Token Setup Guide

## Overview

Grace's GitHub Knowledge Miner can access GitHub's API in two modes:
- **Anonymous**: 60 requests/hour (limited)
- **Authenticated**: 5000 requests/hour (recommended)

## Quick Setup

### Option 1: Environment Variable (.env file) - RECOMMENDED

1. **Create a GitHub Personal Access Token**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `public_repo` (for public repositories)
   - Copy the token (starts with `ghp_`)

2. **Add to .env file**
   ```bash
   # Create .env if it doesn't exist
   cp .env.example .env
   
   # Add your token
   GITHUB_TOKEN=ghp_your_token_here
   ```

3. **Restart Grace**
   ```bash
   ./GRACE.ps1
   ```

### Option 2: Secrets Vault (More Secure)

1. **Set vault encryption key**
   ```bash
   # In .env
   GRACE_VAULT_KEY=your-base64-encoded-fernet-key
   ```

2. **Store token in vault** (programmatically)
   ```python
   from backend.secrets_vault import secrets_vault
   
   await secrets_vault.store_secret(
       secret_key='GITHUB_TOKEN',
       secret_value='ghp_your_token_here',
       secret_type='token',
       owner='system',
       service='github'
   )
   ```

## How It Works

### Token Loading Priority

1. **Secrets Vault** - Checks encrypted vault first
2. **Environment Variable** - Falls back to `GITHUB_TOKEN` env var
3. **Anonymous Mode** - If no token found, uses unauthenticated requests

### Implementation Details

#### secrets_vault.py

```python
async def get_secret(self, secret_key: str, accessor: str = "system") -> Optional[str]:
    """
    Simplified secret getter with fallback to environment variables
    
    Tries:
    1. Secrets vault
    2. Environment variable
    3. Returns None
    """
    try:
        # Try vault first
        return await self.retrieve_secret(secret_key, accessor)
    except (ValueError, PermissionError):
        # Fall back to environment variable
        env_value = os.getenv(secret_key)
        if env_value:
            return env_value
        return None
```

#### github_knowledge_miner.py

```python
async def start(self):
    """Start GitHub mining session"""
    # Try to get GitHub token from secrets vault or environment
    self.github_token = await secrets_vault.get_secret('GITHUB_TOKEN', 'github_miner')
    
    if self.github_token:
        logger.info("[GITHUB-MINER] ✅ GitHub token loaded successfully")
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.github_token}'
        }
    else:
        logger.warning(
            "[GITHUB-MINER] ⚠️  No GitHub token found!\n"
            "  Using unauthenticated requests (60 requests/hour)\n"
            "  To fix:\n"
            "    1. Create a GitHub personal access token\n"
            "    2. Add GITHUB_TOKEN=<your_token> to .env file\n"
            "    OR set GRACE_VAULT_KEY and store in vault"
        )
        headers = {'Accept': 'application/vnd.github.v3+json'}
    
    # Check and display rate limit status
    await self._check_rate_limit()
```

## Rate Limit Status

The system automatically checks and displays your current rate limit:

### With Token
```
[GITHUB-MINER] ✅ GitHub token loaded successfully
[GITHUB-MINER] 📊 Rate Limit: 4998/5000 requests remaining (resets at 15:53:35)
```

### Without Token
```
[GITHUB-MINER] ⚠️  No GitHub token found!
  Using unauthenticated requests (60 requests/hour)
[GITHUB-MINER] ⚠️  Rate Limit: 58/60 requests remaining (resets at 15:53:35)
```

### Low Rate Limit Warning
```
[GITHUB-MINER] 🚨 LOW RATE LIMIT! Only 5 requests left.
Add a GitHub token to get 5000/hour instead of 60/hour
```

## Testing

### Test Current Setup

```bash
# Test token loading
python test_github_token.py
```

This will show:
- ✅ Environment variables status
- 🔐 Secrets vault status
- 🐙 GitHub miner initialization
- 📊 Current rate limit

### Test With Mock Token

```bash
# Test with a fake token to verify mechanism
python test_with_token.py
```

## Troubleshooting

### No Token Warnings

**Symptom**: Seeing "No GitHub token found" warnings

**Solution**: 
1. Check `.env` file exists
2. Verify `GITHUB_TOKEN=ghp_...` is set
3. Restart Grace to reload environment

### Token Not Loading from Vault

**Symptom**: Token in vault but not loading

**Solution**:
1. Ensure `GRACE_VAULT_KEY` is set in `.env`
2. Check token is stored: `python -c "from backend.secrets_vault import secrets_vault; print(asyncio.run(secrets_vault.list_secrets()))"`
3. Verify token is active and not revoked

### Rate Limit Exhausted

**Symptom**: Getting rate limit errors

**Solution**:
1. Add GitHub token for 5000/hour limit
2. Wait for rate limit reset (shown in logs)
3. Reduce mining frequency

## Security Best Practices

### ✅ DO
- Use `.env` file for local development
- Add `.env` to `.gitignore` (already done)
- Use secrets vault for production
- Set `GRACE_VAULT_KEY` from secure source
- Rotate tokens regularly
- Use minimal scopes (public_repo only)

### ❌ DON'T
- Commit tokens to git
- Share tokens in logs or screenshots
- Use personal tokens in shared environments
- Give tokens unnecessary scopes

## Production Deployment

For production, use secrets vault with proper key management:

```bash
# 1. Generate secure vault key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Set in production environment (not .env)
export GRACE_VAULT_KEY="your-generated-key"

# 3. Store token in vault
# (Use admin interface or migration script)

# 4. Never set GITHUB_TOKEN env var in production
# (Use vault only for better audit trail)
```

## Monitoring

The system logs all secret access:
- Who accessed the token
- When it was accessed
- Success/failure status
- IP address and context

Check audit logs:
```sql
SELECT * FROM secret_access_log 
WHERE secret_key = 'GITHUB_TOKEN' 
ORDER BY created_at DESC;
```

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Environment variable loading | ✅ Working | Uses `GITHUB_TOKEN` from .env |
| Secrets vault integration | ✅ Working | Falls back to vault |
| GRACE_VAULT_KEY support | ✅ Working | Optional encryption key |
| Graceful fallback | ✅ Working | Anonymous mode if no token |
| Clear instructions | ✅ Working | Helpful error messages |
| Rate limit display | ✅ Working | Shows current status |
| Tested without token | ✅ Verified | Anonymous mode works |
| Tested with token | ✅ Verified | Authenticated mode works |
