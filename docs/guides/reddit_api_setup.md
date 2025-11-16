# Reddit API Setup Guide

Quick guide to enable real Reddit API integration in Grace.

## Step 1: Get Reddit API Credentials

1. Visit https://www.reddit.com/prefs/apps
2. Click **"create another app..."** at the bottom
3. Fill in the form:
   - **name**: `GraceAI` (or any name you prefer)
   - **App type**: Select **"script"**
   - **description**: `Learning bot for Grace AI`
   - **about url**: (leave blank or add your URL)
   - **redirect uri**: `http://localhost:8080`
4. Click **"create app"**
5. Note your credentials:
   - **Client ID**: The string shown under your app name (looks like: `abc123DEF456`)
   - **Client Secret**: The value in the "secret" field (looks like: `xyz789-ABC123def456`)

## Step 2: Configure Credentials

### Option A: Environment Variables (Recommended for local dev)

Add to your `.env` file:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

### Option B: Secrets Vault (Recommended for production)

Using Python:

```python
from backend.secrets_vault import secrets_vault

# Store Reddit client ID
await secrets_vault.store_secret(
    secret_key="reddit_client_id",
    secret_value="your_client_id_here",
    secret_type="api_key",
    owner="system",
    service="reddit",
    description="Reddit API Client ID"
)

# Store Reddit client secret
await secrets_vault.store_secret(
    secret_key="reddit_client_secret",
    secret_value="your_client_secret_here",
    secret_type="api_key",
    owner="system",
    service="reddit",
    description="Reddit API Client Secret"
)
```

## Step 3: Test the Integration

Run the simple test:

```bash
python test_reddit_simple.py
```

Expected output with credentials:
```
[REDDIT] ✅ Reddit API credentials loaded
[REDDIT] ✅ Using real Reddit API
[REDDIT] ✅ Fetched 5 real posts from r/programming
```

Expected output without credentials:
```
[REDDIT] ⚠️ No Reddit credentials found, using mock data
```

## Step 4: Use in Your Code

The Reddit learning system automatically uses real API when credentials are available:

```python
from backend.reddit_learning import reddit_learning

# Start the system
await reddit_learning.start()

# Learn from a subreddit (automatically uses real API if available)
result = await reddit_learning.learn_from_subreddit(
    subreddit='programming',
    topic='software engineering',
    max_posts=10
)

print(f"Fetched {result['posts_analyzed']} posts")
```

## API Rate Limits

Reddit API limits for script-type apps:
- **60 requests per minute**
- PRAW handles rate limiting automatically
- Additional 2-second delay between subreddits in `learn_topic()`

## Troubleshooting

### "No credentials found" warning
- Check that credentials are in `.env` file or secrets vault
- Ensure `.env` file is in the root directory
- Verify environment variables are loaded

### PRAW errors
- Verify client ID and secret are correct
- Check your Reddit app settings at https://www.reddit.com/prefs/apps
- Ensure app type is "script"

### Rate limit errors
- PRAW handles these automatically with retries
- If persistent, reduce `max_posts` or add delays between calls

## Security Best Practices

1. ✅ **Never commit credentials** to git
2. ✅ Keep `.env` in `.gitignore`
3. ✅ Use secrets vault for production
4. ✅ Rotate credentials periodically
5. ✅ Monitor access logs

## Without Credentials

Grace works fine without Reddit credentials - it automatically falls back to mock data. This is useful for:
- Development without API access
- Testing without rate limits
- Running when Reddit API is down
- Demonstrating functionality

The mock data maintains the same structure as real posts, so all downstream code works identically.
