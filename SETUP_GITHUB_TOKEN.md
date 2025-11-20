# Quick Setup: GitHub Token

## Why You Need This

Without a GitHub token:
- ❌ **60 requests/hour** (hits rate limit in minutes)
- ❌ Remote learning fails quickly
- ❌ Chaos campaigns can't access GitHub

With a GitHub token:
- ✅ **5000 requests/hour** (plenty for all operations)
- ✅ Remote learning works smoothly
- ✅ Chaos campaigns can test GitHub integration

## Setup (3 Minutes)

### Step 1: Create GitHub Token

1. Go to: https://github.com/settings/tokens/new
2. Token name: `Grace AI - Local Dev`
3. Expiration: `90 days` (or your preference)
4. Scopes to select:
   - ✅ `public_repo` (read public repositories)
   - That's it! (minimal permissions for safety)
5. Click "Generate token"
6. **Copy the token now** (starts with `ghp_` - you can't see it again!)

### Step 2: Add to .env File

1. Open your `.env` file in `c:/Users/aaron/grace_2/.env`
2. Find the line that says `GITHUB_TOKEN=your_github_token_here`
3. Replace `your_github_token_here` with your actual token:
   ```
   GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyzABCD
   ```
4. Save the file

### Step 3: Restart Grace

```powershell
# Stop Grace (Ctrl+C if running)
# Then restart
.\START_GRACE.bat
```

## Verify It's Working

When Grace starts, you should see:

```
[GITHUB-MINER] ✅ GitHub token loaded successfully
[GITHUB-MINER] 📊 Rate Limit: 5000/5000 requests remaining (resets at XX:XX:XX)
```

Instead of:

```
[GITHUB-MINER] ⚠️  No GitHub token found!
  Using unauthenticated requests (60 requests/hour)
```

## Current Status

Check your current rate limit:
- Look for `[GITHUB-MINER]` messages in the startup logs
- If you see `5000/5000` - you're authenticated ✅
- If you see `60/60` - token not loaded ❌

## Security Notes

✅ **Safe:**
- `.env` file is in `.gitignore` (won't be committed)
- Token has minimal `public_repo` scope
- Only reads public repositories

⚠️ **Important:**
- Don't share your `.env` file
- Don't commit the token to git
- Don't screenshot/paste the token publicly

## Troubleshooting

**Problem: Token not loading after restart**
- Check the `.env` file has no extra spaces
- Make sure line looks exactly like: `GITHUB_TOKEN=ghp_your_token`
- No quotes around the token
- Save the file before restarting

**Problem: Still seeing 60/60 rate limit**
- Verify token starts with `ghp_`
- Check token hasn't expired on GitHub
- Make sure you saved `.env` file
- Try fully stopping and restarting Grace

## Need Help?

Full documentation: `docs/guides/GITHUB_TOKEN_SETUP.md`
