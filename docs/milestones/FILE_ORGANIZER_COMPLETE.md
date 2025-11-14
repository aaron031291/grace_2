# Intelligent File Organizer - Complete ✅

## Overview

Grace's Librarian now includes an **intelligent file organizer** that:
- ✅ **Analyzes file content** to determine appropriate domain/folder
- ✅ **Automatically creates folders** for new domains
- ✅ **Moves files** to relevant directories
- ✅ **Provides undo** for all operations (accidental deletions, moves)
- ✅ **Learns from corrections** when you manually organize files
- ✅ **Reasons about domains** using content analysis and filename patterns

---

## Features

### 1. Domain-Based Organization

**The Librarian understands these domains:**
- **Business**: startup, sales, marketing, strategy, business intelligence
- **Technical**: code, documentation, API discovery, codebases
- **Finance**: finance, crypto, compliance
- **Research**: research, datasets, insights
- **Media**: YouTube, media files, web scraping, Reddit
- **Governance**: governance, constitutional, safety
- **Learning**: learning materials, domain knowledge, conversations
- **Books**: PDF/EPUB books for reading and learning

**How it works:**
1. Analyzes filename for keywords
2. Checks file extension for hints
3. Reads first 1000 characters for content patterns
4. Calculates confidence score
5. Suggests or creates target folder

### 2. Intelligent Reasoning

**Example analysis:**

File: `lean_startup_excerpt.pdf`

```yaml
Domain Analysis:
  - Filename contains 'lean_startup' → business (confidence +0.15)
  - Extension .pdf with 'book' pattern → books (confidence +0.15)
  - File size > 1MB → likely full book (confidence +0.10)
  
Final Decision:
  Domain: books
  Target Folder: grace_training/documents/books/
  Confidence: 0.90 (HIGH)
  Action: Auto-move (confidence >= 0.85)
```

### 3. Undo System

**Every operation is tracked:**
- Move operations create backups in `.librarian_backups/`
- Delete operations preserve files with restore capability
- Rename operations track old → new mapping
- All tracked in `memory_file_operations` table

**Undo UI shows:**
- Operation type (MOVE, DELETE, RENAME)
- Source → Target paths
- Timestamp
- **Undo button** (one-click restore)
- Status: Active or UNDONE

### 4. Auto-Folder Creation

**When new domains detected:**
1. Librarian creates `grace_training/{domain}/` folder
2. Generates README.md with:
   - Domain name and description
   - Auto-creation timestamp
   - Purpose statement
3. Logs creation to `memory_librarian_log`
4. Moves relevant files immediately

**Example:**
```
User drops: "bitcoin_trading_strategy.pdf"

Librarian:
  1. Analyzes → domain: crypto (new!)
  2. Creates: grace_training/crypto/
  3. Generates: grace_training/crypto/README.md
  4. Moves file: bitcoin_trading_strategy.pdf → grace_training/crypto/
  5. Logs: "New domain 'crypto' created, 1 file organized"
```

### 5. Learning from Corrections

**When you manually move a file:**
```
You move: startup_failure_analysis.txt
From: grace_training/research/
To: grace_training/startup_failures/

Librarian learns:
  - Pattern: "*failure*" → startup_failures folder
  - Confidence: 0.7 (learned from user)
  - Stored in: memory_file_organization_rules
  - Future files matching pattern: auto-suggested
```

**The more you correct, the smarter Grace gets!**

---

## User Workflows

### Workflow 1: Drop a File (Auto-Organization)

**Scenario**: You download a PDF about sales techniques

1. Drop file: `closing_techniques.pdf` into `grace_training/`
2. Librarian detects file creation
3. **Analysis**:
   - Filename: "closing" → sales domain
   - Extension: .pdf → document
   - Confidence: 0.85 (high)
4. **Auto-move** to `grace_training/sales/`
5. **Notification**: "📂 File organized: closing_techniques.pdf → sales/"
6. **Undo available** for 30 days

### Workflow 2: Undo Accidental Delete

**Scenario**: You accidentally delete a folder

1. Delete folder: `grace_training/startup_failures/`
2. **Panic!** 😱
3. Open Memory Studio → File Organizer tab
4. See operation: "DELETE → startup_failures/ (2 minutes ago)"
5. **Click "Undo"**
6. Folder restored from backup with all files intact
7. **Relief!** 😌

### Workflow 3: Manual Organization (Teaching Grace)

**Scenario**: Grace suggests wrong folder, you correct it

1. File: `market_intel_report.pdf` suggested → `grace_training/research/`
2. You think it should be in `grace_training/business_intelligence/`
3. **Manually move** file to `business_intelligence/`
4. Librarian detects manual move
5. **Learns**: "market_intel*" → business_intelligence (confidence 0.7)
6. Next file: `market_intel_2024.pdf` → **auto-suggested** to business_intelligence

### Workflow 4: Batch Organization

**Scenario**: You have 50 unorganized files

1. Open Memory Studio → File Organizer → "📚 Books" tab
2. Click **"Scan for Unorganized Files"**
3. Librarian analyzes all files in `grace_training/` root
4. **Shows suggestions**:
   - 15 files → books (confidence 0.90+)
   - 10 files → business (confidence 0.85)
   - 8 files → research (confidence 0.75)
   - 5 files → technical (confidence 0.65)
   - 12 files → unknown (confidence < 0.5)
5. **Apply All** (high confidence) → 25 files organized
6. **Review** medium/low confidence → manual decision

---

## API Endpoints

All implemented in [backend/routes/file_organizer_api.py](file:///c:/Users/aaron/grace_2/backend/routes/file_organizer_api.py)

### Get Recent Operations
```http
GET /api/librarian/file-operations?limit=20

Response:
{
  "operations": [
    {
      "operation_id": "move_1731514000.123",
      "operation_type": "move",
      "source_path": "grace_training/file.pdf",
      "target_path": "grace_training/books/file.pdf",
      "can_undo": true,
      "undone": false,
      "timestamp": "2024-11-13T10:30:00Z"
    }
  ],
  "total": 20
}
```

### Get Organization Suggestions
```http
GET /api/librarian/organization-suggestions

Response:
{
  "suggestions": [
    {
      "file_path": "grace_training/unorganized.pdf",
      "current_folder": "grace_training/",
      "suggested_folder": "grace_training/books/",
      "domain": "books",
      "confidence": 0.92,
      "reasoning": [
        "Filename contains 'book'",
        "Extension .pdf",
        "File size indicates full document"
      ]
    }
  ],
  "total": 5
}
```

### Organize File
```http
POST /api/librarian/organize-file
{
  "file_path": "grace_training/myfile.pdf",
  "target_folder": "grace_training/books/",  // optional
  "auto_move": true
}

Response:
{
  "status": "success",
  "operation_id": "move_1731514000.456",
  "new_path": "grace_training/books/myfile.pdf",
  "old_path": "grace_training/myfile.pdf"
}
```

### Undo Operation
```http
POST /api/librarian/undo/move_1731514000.456

Response:
{
  "status": "success",
  "message": "File restored to grace_training/myfile.pdf",
  "original_path": "grace_training/myfile.pdf"
}
```

### Scan and Organize All
```http
POST /api/librarian/scan-and-organize
{
  "auto_move": false  // true = auto-organize, false = just suggest
}

Response:
{
  "analyzed": 50,
  "organized": 25,
  "suggested": 15,
  "errors": 0,
  "details": [...]
}
```

### Get Domain Structure
```http
GET /api/librarian/domain-structure

Response:
{
  "structure": {
    "books": {
      "path": "grace_training/documents/books",
      "file_count": 14,
      "subdirectories": []
    },
    "business": {
      "path": "grace_training/business",
      "file_count": 23,
      "subdirectories": ["startup", "sales", "marketing"]
    }
  },
  "known_domains": {...}
}
```

---

## UI Integration

### File Organizer Panel (New!)

**Location**: Memory Studio → **File Organizer** tab

**Left Side - Organization Suggestions:**
- Card per unorganized file
- Shows: filename, current location, suggested folder
- Confidence percentage (color-coded)
- Reasoning bullets (why this suggestion?)
- **Actions**: "Apply" or "Dismiss"

**Right Side - Recent Operations:**
- Operation type badges (MOVE, DELETE, RENAME)
- Source → Target paths
- Timestamp
- **Undo button** (yellow, prominent)
- "UNDONE" badge for restored operations

**Footer:**
- "Scan for Unorganized Files" button
- Learning indicator: "Organizer learns from your corrections"

---

## Database Schema

### memory_file_operations
```sql
CREATE TABLE memory_file_operations (
  operation_id TEXT PRIMARY KEY,
  operation_type TEXT NOT NULL,      -- move, delete, rename, copy
  source_path TEXT,
  target_path TEXT,
  backup_path TEXT,                  -- for undo
  can_undo BOOLEAN DEFAULT TRUE,
  undone BOOLEAN DEFAULT FALSE,
  undone_at TIMESTAMP,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  details JSON
);
```

**Purpose**: Track all file operations for undo/redo

### memory_file_organization_rules
```sql
CREATE TABLE memory_file_organization_rules (
  rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_pattern TEXT NOT NULL,        -- regex or glob
  target_folder TEXT NOT NULL,
  confidence REAL DEFAULT 0.5,
  learned_from_user BOOLEAN DEFAULT FALSE,
  times_applied INTEGER DEFAULT 0,
  success_rate REAL DEFAULT 0.0,     -- how often user accepts
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);
```

**Purpose**: Store learned organization patterns

---

## Configuration

### Confidence Thresholds

```python
# In file_organizer_agent.py
AUTO_MOVE_THRESHOLD = 0.85    # Auto-organize if confidence >= 85%
SUGGEST_THRESHOLD = 0.50      # Suggest if confidence >= 50%
FLAG_THRESHOLD = 0.30         # Flag for review if < 30%
```

**Adjust based on preference:**
- **Conservative**: Increase to 0.95 (fewer auto-moves, more suggestions)
- **Aggressive**: Decrease to 0.70 (more auto-moves, fewer suggestions)

### Backup Retention

```python
BACKUP_RETENTION_DAYS = 30    # Keep backups for undo
```

### Domain Taxonomy

Add new domains in `file_organizer_agent.py`:
```python
self.known_domains = {
    'business': ['startup', 'sales', 'marketing'],
    'your_domain': ['subdomain1', 'subdomain2'],  # Add here
}
```

---

## How It Works (Technical)

### 1. File Detection
```python
FileSystemWatcher → on_created() → FileOrganizerAgent
```

### 2. Domain Analysis
```python
def _analyze_domain(file_path):
    # Rule 1: Filename keywords
    if 'startup' in filename:
        domains.append('business')
    
    # Rule 2: File extension
    if extension == '.pdf':
        domains.append('documents')
    
    # Rule 3: Content analysis
    content = read_first_1000_chars()
    if 'bitcoin' in content:
        domains.append('crypto')
    
    # Calculate confidence
    confidence = base_confidence + matches * 0.15
    
    return {domain, confidence, reasoning}
```

### 3. Decision Logic
```python
if confidence >= 0.85:
    auto_move()  # High confidence
elif confidence >= 0.50:
    suggest()    # Medium confidence
else:
    flag()       # Low confidence, need review
```

### 4. Undo Mechanism
```python
def _move_file(source, target):
    # 1. Create backup
    backup = create_backup(source)
    
    # 2. Move file
    shutil.move(source, target)
    
    # 3. Record operation
    save_operation({
        'type': 'move',
        'source': source,
        'target': target,
        'backup': backup,
        'can_undo': True
    })

def undo_operation(operation_id):
    # 1. Find operation
    op = get_operation(operation_id)
    
    # 2. Restore from backup
    shutil.copy(op.backup, op.source)
    
    # 3. Mark undone
    op.undone = True
```

---

## Monitoring & Maintenance

### Check Organizer Status
```http
GET /api/librarian/organization-stats

Response:
{
  "total_operations": 156,
  "operations_by_type": {
    "move": 120,
    "delete": 15,
    "rename": 21
  },
  "undone_operations": 8,
  "learned_rules": 12
}
```

### View Learning Progress
```sql
SELECT file_pattern, target_folder, times_applied, success_rate
FROM memory_file_organization_rules
WHERE learned_from_user = TRUE
ORDER BY success_rate DESC;
```

### Clean Old Backups
```python
# Automatic cleanup (runs weekly)
delete_backups_older_than(30_days)
```

---

## Future Enhancements (Optional)

### Phase 1: LLM-Powered Analysis
- [ ] Use GPT-4 for content understanding
- [ ] Semantic domain classification
- [ ] Extract topics and themes
- [ ] Multi-language support

### Phase 2: Advanced Learning
- [ ] Bayesian learning from corrections
- [ ] Collaborative filtering (if multi-user)
- [ ] Confidence boosting over time
- [ ] Pattern recognition via ML

### Phase 3: Smart Features
- [ ] Duplicate detection and merging
- [ ] Related file suggestions
- [ ] Auto-tagging based on content
- [ ] Version control for organized files

### Phase 4: Integration
- [ ] Slack/email notifications for suggestions
- [ ] Batch approval workflow
- [ ] Export organization reports
- [ ] API for external tools

---

## ✅ READY TO USE

The intelligent file organizer is production-ready:

1. **Backend**: Domain reasoning, undo system, learning
2. **Frontend**: File Organizer Panel with suggestions and undo
3. **API**: Full REST API for all operations
4. **Database**: Schemas for operations and rules tracking
5. **Documentation**: Complete guide (this file)

**Your next steps:**

1. **Open Memory Studio → File Organizer tab**
2. **Drop some files** into `grace_training/`
3. **Watch suggestions** appear
4. **Apply or dismiss** suggestions
5. **If wrong, undo** and manually organize (Grace learns!)

The Librarian will get smarter with every correction! 🤖📂✨

---

## Quick Reference

**I want to...**

- **Organize a file**: Drop it → Librarian suggests folder → Click "Apply"
- **Undo a move**: File Organizer tab → Recent Operations → Click "Undo"
- **Create new domain**: Files will auto-create folders when needed
- **Teach Grace**: Manually move file → Grace learns the pattern
- **Batch organize**: Click "Scan for Unorganized Files" → Review suggestions

**Confidence Levels:**
- 🟢 **85%+**: Auto-organized (trusted)
- 🟡 **50-85%**: Suggested (review recommended)
- 🔴 **<50%**: Flagged (manual decision needed)

---

## Support

**Issues?**
- Check logs: `logs/librarian_kernel.log`
- View operations: `GET /api/librarian/file-operations`
- Check stats: `GET /api/librarian/organization-stats`

**Questions?**
- How does reasoning work? → See "How It Works" section
- Can I customize domains? → Yes, edit `known_domains` in agent code
- Is undo permanent? → Backups kept for 30 days by default

**Ready to organize!** 🚀📚🗂️
