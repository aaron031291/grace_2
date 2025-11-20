# Grace Remote Learning System

## Overview

Grace can now actively learn from the internet and GitHub using your PC as a secure, governed proxy.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Grace Learning System                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐      ┌──────────────────┐       │
│  │   Firefox    │ ───> │  Your PC as      │       │
│  │   Agent      │      │  Secure Proxy    │       │
│  └──────────────┘      └──────────────────┘       │
│         │                       │                  │
│         ▼                       ▼                  │
│  ┌──────────────┐      ┌──────────────────┐       │
│  │ Web Scraper  │      │ Remote Computer  │       │
│  │              │      │ Access           │       │
│  └──────────────┘      └──────────────────┘       │
│         │                       │                  │
│         ▼                       ▼                  │
│  ┌──────────────┐      ┌──────────────────┐       │
│  │   GitHub     │      │   Governance     │       │
│  │   Miner      │ ───> │   Engine         │       │
│  └──────────────┘      └──────────────────┘       │
│                                 │                  │
│                                 ▼                  │
│                        ┌──────────────────┐        │
│                        │  Immutable Log   │        │
│                        │  (Audit Trail)   │        │
│                        └──────────────────┘        │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. Firefox Agent
- **Location**: `backend/agents/firefox_agent.py`
- **Purpose**: Browser automation for web access
- **Features**:
  - HTTPS-only browsing
  - Domain whitelist enforcement
  - Full audit logging
  - Data extraction

**Approved Domains**:
- arxiv.org (papers)
- github.com (code)
- stackoverflow.com (Q&A)
- huggingface.co (AI models)
- tensorflow.org, pytorch.org (ML docs)
- paperswithcode.com, kaggle.com (datasets)
- docs.python.org, readthedocs.io (documentation)
- wikipedia.org (general knowledge)

### 2. Remote Computer Access
- **Location**: `backend/misc/remote_computer_access.py`
- **Purpose**: Execute actions on your PC
- **Features**:
  - Run commands
  - Install packages
  - Clone repositories
  - Read/create files
  - All governed and logged

**Allowed Actions**:
- `read_file`
- `list_directory`
- `run_command`
- `check_disk_space`
- `check_memory`
- `check_processes`
- `get_system_info`
- `create_file`
- `install_package`
- `run_tests`

### 3. Web Scraper
- **Location**: `backend/utilities/safe_web_scraper.py`
- **Purpose**: Learn from web content
- **Features**:
  - Search and learn from queries
  - Learn entire topics
  - Extract structured data
  - Uses Firefox agent under the hood

### 4. GitHub Knowledge Miner
- **Location**: `backend/knowledge/github_knowledge_miner.py`
- **Purpose**: Learn from GitHub repositories
- **Features**:
  - Clone and analyze repos
  - Extract code patterns
  - Learn best practices
  - Rate limit management

## How It Works

### Boot Sequence
When Grace starts, Chunk 6.5 initializes:

```
[CHUNK 6.5] Remote Learning Systems (Internet & GitHub Access)...
  [OK] Firefox Agent: ENABLED (Internet access via your PC)
  [OK] Approved domains: 10
  [OK] Remote Computer Access: Active
  [OK] Allowed actions: 10
  [OK] Web Scraper: Active (via Firefox agent)
  [OK] Trusted domains: 11
  [OK] GitHub Knowledge Miner: Active
  [OK] 4/4 remote learning systems started

  🌐 Grace can now learn from:
    • Internet (via Firefox on your PC)
    • GitHub repositories
    • Stack Overflow, arXiv, Kaggle, etc.
    • All governed, logged, and traceable
```

### Learning Flow

1. **Query → Search**
   ```python
   result = await safe_web_scraper.search_and_learn(
       query="reinforcement learning algorithms",
       max_sources=5
   )
   ```

2. **Firefox Agent → Browse**
   - Checks governance
   - Validates domain whitelist
   - Fetches content via HTTPS
   - Logs to audit trail

3. **Extract → Store**
   - Extracts useful data
   - Stores with provenance
   - Updates knowledge base

4. **Apply → Test**
   - Tests in sandbox
   - Validates against KPIs
   - Applies if approved

## Governance & Security

### All Actions Are:
✅ **Governed** - Every action requires approval  
✅ **Logged** - Full audit trail in immutable log  
✅ **Whitelisted** - Only approved domains accessible  
✅ **HTTPS-only** - No unencrypted connections  
✅ **Traceable** - Complete provenance tracking  

### Constitutional Checks
Every remote action is validated against:
- Governance policies
- Constitutional AI principles
- Trust framework
- Security policies

## GitHub Integration

### Setup
1. Create GitHub personal access token: https://github.com/settings/tokens
2. Add to `.env`:
   ```bash
   GITHUB_TOKEN=ghp_your_token_here
   ```
3. Or store in secrets vault

### Without Token
- 60 requests/hour (unauthenticated)
- Limited to public repos

### With Token
- 5,000 requests/hour
- Access to private repos (if authorized)

## API Usage

### Web Learning
```python
from backend.utilities.safe_web_scraper import safe_web_scraper

# Search and learn
result = await safe_web_scraper.search_and_learn(
    query="kubernetes deployment patterns",
    max_sources=5
)

# Learn a topic
result = await safe_web_scraper.learn_topic(
    topic="distributed systems",
    max_pages=10
)

# Scrape specific URL
result = await safe_web_scraper.scrape_url(
    url="https://arxiv.org/abs/2103.00020",
    purpose="Learn about transformers"
)
```

### GitHub Mining
```python
from backend.knowledge.github_knowledge_miner import github_miner

# Learn from trending repos
result = await github_miner.learn_from_trending(
    category='ai_ml',
    max_repos=5
)

# Analyze specific repo
result = await github_miner.analyze_repo(
    repo_url='https://github.com/pytorch/pytorch',
    purpose='Learn PyTorch internals'
)
```

### Remote Computer Access
```python
from backend.misc.remote_computer_access import RemoteComputerAccess

remote = RemoteComputerAccess()
await remote.start()

# Run command
result = await remote.execute_action(
    action='run_command',
    parameters={'command': 'python --version'},
    purpose='Check Python version'
)

# Install package
result = await remote.execute_action(
    action='install_package',
    parameters={'package': 'transformers'},
    purpose='Install Hugging Face transformers'
)
```

## Configuration

### Environment Variables
```bash
# Enable remote learning (default: disabled)
ENABLE_REMOTE_LEARNING=true

# Enable Firefox agent (default: disabled)
ENABLE_FIREFOX_ACCESS=true

# GitHub token for API access
GITHUB_TOKEN=ghp_your_token_here

# Offline mode (disables internet learning)
OFFLINE_MODE=0
```

### Whitelist Configuration
Edit `config/autonomous_learning_whitelist.yaml` to add/remove domains.

## Monitoring

### Check Status
```bash
# Via API
curl http://localhost:8000/api/remote-learning/status

# View logs
tail -f logs/grace.log | grep -E "FIREFOX|WEB-SCRAPER|GITHUB-MINER|REMOTE-ACCESS"
```

### Audit Trail
All learning activities are logged to:
- `backend/core/immutable_log.py` - Permanent audit trail
- `logs/grace.log` - Application logs
- Database: `learning_provenance` table

## Safety Features

### Emergency Stop
Grace can be paused at any time:
```python
from backend.grace_control_center import grace_control
grace_control.pause_system()
```

This immediately stops all:
- Web browsing
- Remote access
- Learning activities

### Rate Limiting
- GitHub: Respects API rate limits
- Web scraping: Configurable delays
- Remote commands: Throttled execution

### Sandboxing
All learned knowledge tested in sandbox before application:
- Unit tests
- Integration checks
- KPI validation
- Trust scoring

## Troubleshooting

### Firefox Agent Not Starting
```
[WARN] Firefox Agent startup issue: No module named 'aiohttp'
```
**Fix**: `pip install aiohttp`

### GitHub Rate Limit Exceeded
```
[WARN] GitHub rate limit exceeded
```
**Fix**: Add GITHUB_TOKEN to .env file

### Domain Not Approved
```
[ERROR] Domain example.com not approved
```
**Fix**: Add domain to approved list in `firefox_agent.py` or config

## Examples

### Learn About New Technology
```python
# Grace searches, reads, and learns
await safe_web_scraper.learn_topic(
    topic="Rust async programming",
    max_pages=10
)
```

### Analyze Open Source Project
```python
# Grace clones and analyzes code patterns
await github_miner.analyze_repo(
    repo_url='https://github.com/fastapi/fastapi',
    purpose='Learn FastAPI architecture'
)
```

### Research Papers
```python
# Grace downloads and extracts knowledge
await firefox_agent.browse_url(
    url='https://arxiv.org/abs/1706.03762',
    purpose='Read Attention Is All You Need paper',
    extract_data=True
)
```

## Future Enhancements

- [ ] YouTube learning integration
- [ ] PDF extraction and analysis
- [ ] Code execution in sandboxed environment
- [ ] Automatic knowledge gap detection
- [ ] Multi-modal learning (images, videos)
- [ ] Federated learning across sources

---

**Status**: ✅ Active  
**Last Updated**: 2025  
**Maintained By**: Guardian + Self-Healing System
