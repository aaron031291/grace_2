

# External API Integration - Complete Documentation

**Phase 9: GitHub, Slack, AWS Integration with Governance & Security**

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Components](#components)
3. [Setup Instructions](#setup-instructions)
4. [API Authentication](#api-authentication)
5. [Security & Governance](#security--governance)
6. [CLI Commands](#cli-commands)
7. [Frontend UI](#frontend-ui)
8. [Grace Autonomous Behaviors](#grace-autonomous-behaviors)
9. [API Reference](#api-reference)
10. [Testing](#testing)
11. [Best Practices](#best-practices)

---

## Architecture Overview

The External API Integration system provides secure, governed access to external services:

```
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  GitHub  │    │  Slack   │    │   AWS    │              │
│  └──────────┘    └──────────┘    └──────────┘              │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────┼─────────────────────────────────┐
│                    Grace System                            │
│                         │                                  │
│  ┌──────────────────────┴──────────────────────┐          │
│  │       External API Connectors                │          │
│  │  - GitHubClient  - SlackClient  - AWSClient │          │
│  └──────────────────────┬──────────────────────┘          │
│                         │                                  │
│  ┌──────────────────────┴──────────────────────┐          │
│  │         Security & Governance Layer          │          │
│  │  - Secrets Vault  - Hunter  - Verification  │          │
│  │  - Governance Engine  - Parliament Voting   │          │
│  └──────────────────────┬──────────────────────┘          │
│                         │                                  │
│  ┌──────────────────────┴──────────────────────┐          │
│  │        Grace External Agent                  │          │
│  │  - Autonomous GitHub issue creation          │          │
│  │  - Auto Slack notifications                  │          │
│  │  - Auto S3 backups                           │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌─────────────────────────────────────────────┐          │
│  │  Interfaces: API Routes / CLI / Frontend UI │          │
│  └─────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **🔐 Secure Secrets Management**: Encrypted vault for API credentials
- **🛡️ Governance Integration**: All operations governed by policies
- **🔍 Hunter Scanning**: Security scanning on all inbound/outbound content
- **✅ Verification**: Cryptographic signatures on all operations
- **🏛️ Parliament Voting**: Major operations require Parliament approval
- **🤖 Autonomous Operations**: Grace can use APIs independently
- **💾 Memory Integration**: All API interactions stored in memory
- **📊 Cost Tracking**: AWS operation cost monitoring

---

## Components

### 1. GitHub Connector (`external_apis/github_connector.py`)

**Features:**
- Repository listing and management
- Issue creation, reading, commenting
- Pull request creation
- Commit history retrieval
- Full governance and Hunter scanning

**Methods:**
```python
await client.authenticate_with_token(token_key="github_token")
repos = await client.list_repositories(org="my-org")
issues = await client.get_issues(repo="owner/repo", state="open")
issue = await client.create_issue(repo="owner/repo", title="Bug", body="Description")
pr = await client.create_pr(repo="owner/repo", title="Feature", head="feature-branch", base="main")
commits = await client.list_commits(repo="owner/repo", branch="main")
comment = await client.create_comment(repo="owner/repo", issue_number=42, comment="Fix applied")
```

### 2. Slack Connector (`external_apis/slack_connector.py`)

**Features:**
- Channel listing
- Message sending (with governance approval)
- Message history retrieval
- File uploads
- Reminder creation
- Webhook event receiver

**Methods:**
```python
await client.authenticate_with_token(token_key="slack_token")
channels = await client.list_channels()
result = await client.send_message(channel="#general", text="Hello from Grace!")
history = await client.get_channel_history(channel="C123456", limit=100)
upload = await client.upload_file(channel="#files", file_path="data.json", title="Data")
reminder = await client.create_reminder(text="Check status", time="in 1 hour")
```

### 3. AWS Connector (`external_apis/aws_connector.py`)

**Features:**
- **S3**: Upload, download, list, delete objects
- **Lambda**: Invoke functions, list functions
- **EC2**: List instances (read-only), get status
- Cost tracking for all operations

**Methods:**
```python
await client.authenticate_with_credentials()

# S3 Operations
upload = await client.s3_upload_file(bucket="my-bucket", key="data.json", file_path="local.json")
download = await client.s3_download_file(bucket="my-bucket", key="data.json", dest_path="local.json")
objects = await client.s3_list_objects(bucket="my-bucket", prefix="backups/")
deleted = await client.s3_delete_object(bucket="my-bucket", key="old-file.json")

# Lambda Operations
result = await client.lambda_invoke_function(function_name="process-data", payload={"key": "value"})
functions = await client.lambda_list_functions()

# EC2 Operations
instances = await client.ec2_list_instances()
status = await client.ec2_get_instance_status(instance_id="i-123456")

# Cost Summary
costs = await client.get_cost_summary()
```

### 4. Secrets Vault (`secrets_vault.py`)

**Features:**
- Fernet encryption for all secrets
- Access control and permissions
- Secret rotation and expiration
- Audit logging
- Governance integration

**Methods:**
```python
# Store secret
result = await secrets_vault.store_secret(
    secret_key="github_token",
    secret_value="ghp_abc123...",
    secret_type="token",
    owner="admin",
    service="github",
    expires_in_days=90,
    rotation_days=30
)

# Retrieve secret (governance checked)
token = await secrets_vault.retrieve_secret(
    secret_key="github_token",
    accessor="grace_agent"
)

# List secrets (metadata only)
secrets = await secrets_vault.list_secrets(service="github")

# Revoke secret
await secrets_vault.revoke_secret(
    secret_key="old_token",
    actor="admin",
    reason="Token compromised"
)
```

### 5. Grace External Agent (`grace_external_agent.py`)

**Autonomous Capabilities:**

```python
agent = GraceExternalAgent()
await agent.initialize()

# Auto-create GitHub issues from tasks
task = {"title": "Bug", "description": "Fix issue", "priority": "high"}
issue = await agent.create_github_issue_from_task(task, repo="my-org/my-repo")

# Auto-notify Slack on alerts
alert = {"type": "security_breach", "severity": "critical", "message": "Alert!"}
await agent.notify_slack_on_alert(alert, channel="#alerts")

# Auto-backup to S3
data = {"memories": [...], "policies": [...]}
await agent.backup_to_s3(data, data_type="memories", bucket="grace-backups")

# Start autonomous loop
await agent.autonomous_loop(interval=300)  # Check every 5 minutes
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
# Backend dependencies
pip install PyGithub slack-sdk boto3 cryptography

# Or add to requirements.txt:
# PyGithub>=2.1.1
# slack-sdk>=3.23.0
# boto3>=1.28.0
# cryptography>=41.0.0
```

### 2. Set Up Secrets Vault

```bash
# Set vault encryption key (production)
export GRACE_VAULT_KEY="your-secure-key-here"

# Or let Grace generate one (development)
# Warning will be shown on first run
```

### 3. Configure External Services

#### GitHub Setup

1. Go to GitHub Settings → Developer Settings → Personal Access Tokens
2. Generate token with required scopes:
   - `repo` - Full repository access
   - `read:org` - Read organization data
   - `write:discussion` - Create issues/comments
3. Store in vault:

```bash
grace external secrets store github_token <YOUR_TOKEN> --service github --type token
```

#### Slack Setup

1. Create Slack App at api.slack.com/apps
2. Add OAuth scopes:
   - `channels:read` - List channels
   - `channels:history` - Read messages
   - `chat:write` - Send messages
   - `files:write` - Upload files
3. Install app to workspace
4. Store bot token:

```bash
grace external secrets store slack_token <YOUR_BOT_TOKEN> --service slack --type token
```

#### AWS Setup

1. Create IAM user with programmatic access
2. Attach policies:
   - `AmazonS3FullAccess` (or custom S3 policy)
   - `AWSLambdaRole` (for Lambda invocation)
   - `AmazonEC2ReadOnlyAccess` (for EC2 read)
3. Store credentials:

```bash
grace external secrets store aws_access_key_id <ACCESS_KEY> --service aws --type api_key
grace external secrets store aws_secret_access_key <SECRET_KEY> --service aws --type password
```

### 4. Enable External API Routes

Add to `backend/main.py`:

```python
from backend.routes.external_api_routes import router as external_router

app.include_router(external_router)
```

### 5. Configure Grace External Agent

Edit `grace_external_agent.py` configuration:

```python
agent = GraceExternalAgent()
agent.auto_create_issues = True  # Enable auto GitHub issues
agent.auto_notify_slack = True   # Enable auto Slack alerts
agent.auto_backup_s3 = True      # Enable auto S3 backups
agent.require_parliament_approval = True  # Require voting for major ops
```

---

## API Authentication

### Secrets Vault Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────┐
│ API Call │ ──> │  Connector   │ ──> │ Secrets Vault│ ──> │ Service │
└──────────┘     └──────────────┘     └──────────────┘     └─────────┘
                        │                     │
                        │                     ▼
                        │              ┌──────────────┐
                        │              │  Governance  │
                        │              └──────────────┘
                        │                     │
                        ▼                     ▼
                 ┌──────────────┐     ┌──────────────┐
                 │ Verification │     │    Hunter    │
                 └──────────────┘     └──────────────┘
```

### Token Storage Best Practices

1. **Never hardcode tokens** - Always use secrets vault
2. **Set expiration** - Rotate tokens regularly
3. **Limit permissions** - Use least-privilege access
4. **Monitor access** - Review audit logs
5. **Revoke immediately** - If compromised

---

## Security & Governance

### Governance Policies

All external API operations go through governance:

```python
# Example: GitHub issue creation requires approval
{
  "action": "github_create_issue",
  "resource": "*",
  "decision": "review",  # Requires Parliament vote
  "reason": "External mutations require approval"
}
```

### Hunter Scanning

All inbound and outbound content is scanned:

```python
# Scans performed automatically
- GitHub issue bodies (before posting)
- Slack messages (before sending)
- Downloaded S3 files
- Webhook payloads
```

### Verification Signatures

Every operation creates a verification envelope:

```python
verification_id = await verification.log_verified_action(
    action_id="github_create_issue_123",
    actor="grace_agent",
    action_type="github_create_issue",
    resource="owner/repo",
    input_data={"title": "...", "body": "..."}
)
```

### Parliament Voting

High-priority operations require Parliament approval:

```python
# Automatically triggers Parliament session
if priority == "critical":
    session_id = await parliament_engine.create_session(
        title="Critical Slack Alert",
        description="Send critical security alert to #incidents",
        category="external_api",
        risk_level="high"
    )
```

---

## CLI Commands

### GitHub Commands

```bash
# List repositories
grace external github repos
grace external github repos --org my-organization

# List issues
grace external github issues owner/repo
grace external github issues owner/repo --state closed --limit 50

# Create issue (requires governance approval)
grace external github create-issue owner/repo \
  --title "Bug: Login fails" \
  --body "Description of bug" \
  --labels bug,urgent

# List commits
grace external github commits owner/repo --branch main --limit 20
```

### Slack Commands

```bash
# List channels
grace external slack channels

# Send message (requires governance approval)
grace external slack send "#general" "Hello from Grace CLI!"

# Get channel history
grace external slack history C123456 --limit 50
```

### AWS Commands

```bash
# S3 operations
grace external aws s3 ls my-bucket
grace external aws s3 ls my-bucket --prefix backups/
grace external aws s3 upload local-file.json my-bucket remote-key.json
grace external aws s3 download my-bucket remote-key.json local-file.json

# Lambda operations
grace external aws lambda functions
grace external aws lambda invoke my-function '{"key": "value"}'

# EC2 operations
grace external aws ec2 instances
```

### Secrets Commands

```bash
# List secrets
grace external secrets list
grace external secrets list --service github

# Store secret
grace external secrets store github_token ghp_abc123 \
  --service github \
  --type token \
  --description "Personal access token"

# Retrieve secret (governed)
grace external secrets get github_token

# Revoke secret
grace external secrets revoke old_token --reason "Rotation"
```

---

## Frontend UI

### Access External APIs UI

Navigate to: `http://localhost:3000/external-apis`

### GitHub Panel Features

- Browse repositories
- View issues with filters
- Create new issues with governance
- View issue details and labels

### Slack Panel Features

- Browse channels (public/private)
- Send messages with approval
- View message history
- File upload interface

### AWS Panel Features

- **S3 Tab**: List, upload, download objects
- **Lambda Tab**: List and invoke functions
- **EC2 Tab**: View instance status
- **Costs Tab**: Track operation costs

### Secrets Manager Features

- List all secrets (metadata only)
- Create new secrets with encryption
- Filter by service
- Revoke compromised secrets
- View access counts and expiration

---

## Grace Autonomous Behaviors

### Auto GitHub Issue Creation

Grace automatically creates GitHub issues for high-priority tasks:

```python
# Triggered when Grace identifies a critical task
task = {
    "title": "Security vulnerability detected",
    "description": "Hunter found SQL injection in auth module",
    "priority": "critical",
    "category": "security"
}

# Grace creates issue automatically (with Parliament approval for critical)
issue = await grace_external_agent.create_github_issue_from_task(task)
# Creates: https://github.com/my-org/my-repo/issues/42
```

### Auto Slack Notifications

Grace sends Slack alerts for critical events:

```python
# Triggered on security alerts, system failures, etc.
alert = {
    "type": "hunter_alert",
    "severity": "critical",
    "message": "Malicious payload detected in request",
    "details": {...}
}

# Grace sends to #grace-alerts channel
await grace_external_agent.notify_slack_on_alert(alert)
```

### Auto S3 Backups

Grace backs up important data to S3:

```python
# Triggered periodically or on significant changes
data = {
    "memories": recent_memories,
    "policies": active_policies,
    "parliament_decisions": recent_votes
}

# Grace uploads to S3 with timestamp
await grace_external_agent.backup_to_s3(data, data_type="system_state")
# Uploads to: s3://grace-backups/backups/system_state/2025-01-01T12-00-00.json
```

### Autonomous Loop

Grace runs continuous background processing:

```python
# Start autonomous agent
await grace_external_agent.autonomous_loop(interval=300)  # 5 minutes

# Loop checks for:
# - Pending tasks → Create GitHub issues
# - Critical alerts → Send Slack notifications
# - Data changes → Backup to S3
# - Parliament approvals → Execute pending operations
```

---

## API Reference

### REST API Endpoints

#### GitHub Endpoints

```
POST   /api/external/github/issues              - Create issue
GET    /api/external/github/repos               - List repos
GET    /api/external/github/repos/{owner}/{repo}/issues  - Get issues
POST   /api/external/github/pr                  - Create PR
GET    /api/external/github/repos/{owner}/{repo}/commits - List commits
POST   /api/external/github/comment             - Create comment
```

#### Slack Endpoints

```
POST   /api/external/slack/message              - Send message
GET    /api/external/slack/channels             - List channels
GET    /api/external/slack/channels/{id}/history - Get history
POST   /api/external/slack/upload               - Upload file
POST   /api/external/slack/webhook              - Webhook handler
```

#### AWS Endpoints

```
POST   /api/external/aws/s3/upload              - Upload to S3
POST   /api/external/aws/s3/download            - Download from S3
GET    /api/external/aws/s3/list                - List S3 objects
DELETE /api/external/aws/s3/delete              - Delete S3 object
POST   /api/external/aws/lambda/invoke          - Invoke Lambda
GET    /api/external/aws/lambda/functions       - List functions
GET    /api/external/aws/ec2/instances          - List EC2 instances
GET    /api/external/aws/ec2/instances/{id}/status - Get status
GET    /api/external/aws/costs                  - Cost summary
```

#### Secrets Endpoints

```
GET    /api/external/secrets                    - List secrets
POST   /api/external/secrets                    - Store secret
GET    /api/external/secrets/{key}              - Retrieve secret
DELETE /api/external/secrets/{key}              - Revoke secret
```

---

## Testing

### Run Tests

```bash
# Run all external API tests
pytest tests/test_external_apis.py -v

# Or run directly
python tests/test_external_apis.py
```

### Test Coverage

- ✅ Secrets vault (store, retrieve, list, revoke)
- ✅ GitHub connector (mocked API calls)
- ✅ Slack connector (mocked API calls)
- ✅ AWS connector (mocked boto3)
- ✅ Governance integration
- ✅ Hunter scanning
- ✅ Grace autonomous agent
- ✅ Parliament voting integration

### Manual Testing

```bash
# Test secrets vault
grace external secrets store test_secret "test123" --service test

# Test GitHub (requires token)
grace external github repos

# Test Slack (requires token)
grace external slack channels

# Test AWS (requires credentials)
grace external aws s3 ls my-bucket
```

---

## Best Practices

### Security

1. **Never commit secrets** to version control
2. **Use environment variables** for vault key
3. **Rotate credentials** regularly (set rotation_days)
4. **Monitor access logs** for unusual activity
5. **Revoke immediately** if compromised

### Governance

1. **Set appropriate policies** for external operations
2. **Require Parliament approval** for critical actions
3. **Review audit logs** regularly
4. **Test governance rules** before production

### Performance

1. **Cache API responses** when appropriate
2. **Use batch operations** for multiple items
3. **Monitor API rate limits** for each service
4. **Track costs** for AWS operations

### Error Handling

1. **Graceful degradation** if API unavailable
2. **Retry logic** for transient failures
3. **Detailed error logging** for debugging
4. **User-friendly error messages** in UI

---

## Troubleshooting

### Common Issues

**Problem**: "Not authenticated" error
**Solution**: Store credentials in secrets vault first

**Problem**: "Governance denied" error
**Solution**: Check governance policies, may need Parliament approval

**Problem**: "Hunter detected critical issues" error
**Solution**: Review content being sent, remove sensitive data

**Problem**: AWS cost unexpectedly high
**Solution**: Check cost summary, review operation frequency

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Summary

Phase 9 External API Integration provides:

✅ **GitHub Integration** - Issues, PRs, repos, commits  
✅ **Slack Integration** - Messages, channels, webhooks  
✅ **AWS Integration** - S3, Lambda, EC2 operations  
✅ **Secrets Vault** - Encrypted credential storage  
✅ **Governance & Security** - All operations governed + scanned  
✅ **Parliament Voting** - Critical operations require approval  
✅ **Grace Autonomy** - Auto issue creation, alerts, backups  
✅ **CLI Interface** - Complete command-line tools  
✅ **Frontend UI** - Full web interface for all operations  
✅ **Cost Tracking** - AWS operation cost monitoring  
✅ **Comprehensive Tests** - Full test coverage  

**Grace can now integrate with the external world while maintaining security, governance, and autonomy! 🚀**
