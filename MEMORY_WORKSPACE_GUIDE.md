# 📁 Grace Memory Workspace - Complete Guide

**Feature:** Integrated file explorer and editor for Grace's training corpus  
**Status:** ✅ READY  
**Latest Commit:** 4ab03a4

---

## 🎯 What It Does

**Memory Workspace** gives you a VS Code-style file manager inside Grace for managing:
- Training data and prompts
- Knowledge base files
- Configuration files
- Ingestion templates
- Playbooks and policies

**All directly in the browser with Monaco editor!**

---

## 🚀 Quick Start

### 1. Restart Backend (Load New APIs)
```bash
Ctrl+C  # Stop current backend
python serve.py
```

### 2. Restart Frontend
```bash
Ctrl+C  # Stop current frontend
npm run dev
```

### 3. Access Memory Workspace
1. Visit http://localhost:5173
2. Click **"🧩 Memory Fusion"** in left sidebar
3. See file explorer + editor!

---

## 💡 Features

### File Tree (Left Pane)
- **Hierarchical navigation** - Expand/collapse folders
- **Icons** - Folders and files with visual indicators
- **Selection** - Click to open files
- **Size display** - See file sizes at a glance
- **Status** - Total files and workspace size shown

### Editor (Right Pane)
- **Monaco Editor** - Same as VS Code
- **Syntax highlighting** - Auto-detects by file extension
  - Markdown (.md)
  - Python (.py)
  - TypeScript (.ts, .tsx)
  - JavaScript (.js, .jsx)
  - JSON (.json)
  - YAML (.yaml, .yml)
  - Plain text (.txt)
- **Auto-save indicator** - Shows when file is modified
- **Full editing** - Copy, paste, undo, redo, search

### File Operations

**Create:**
- **New File** button (📄 icon)
  - Prompts for filename
  - Creates in selected folder
  - Opens in editor

- **New Folder** button (📁 icon)
  - Prompts for folder name
  - Creates nested folders

**Edit:**
- Click file → Opens in Monaco
- Make changes
- "Save" button (green when dirty)
- Auto-detects language

**Delete:**
- 🗑️ Delete button
- Confirmation dialog
- Recursive for folders

**Metadata Display:**
- File size
- Last modified date
- Dirty state indicator

---

## 🔌 API Integration

### Backend Endpoints (7)

```bash
# List files
GET /api/memory/files?path=subfolder

# Read file
GET /api/memory/file?path=example.md

# Save file
POST /api/memory/file?path=example.md&content=Hello

# Delete file
DELETE /api/memory/file?path=example.md&recursive=false

# Rename/move
PATCH /api/memory/file?old_path=old.md&new_path=new.md

# Create folder
POST /api/memory/folder?path=newfolder

# Service status
GET /api/memory/status
```

### Clarity Integration
**Events published:**
- `memory.file.saved`
- `memory.file.deleted`
- `memory.file.renamed`
- `memory.folder.created`

**Component registered:**
- Type: `memory_file_service`
- Trust: VERIFIED
- Tags: memory, storage, training

---

## 📂 File Structure

**Default location:** `grace_training/`

**Suggested organization:**
```
grace_training/
├── prompts/
│   ├── system_prompts.md
│   ├── user_examples.md
│   └── few_shot_examples.md
├── knowledge/
│   ├── domains/
│   │   ├── finance.md
│   │   ├── healthcare.md
│   │   └── tech.md
│   └── policies/
│       ├── governance.md
│       └── safety.md
├── ingestion/
│   ├── github_repos.json
│   ├── reddit_sources.json
│   └── web_scraping_rules.yaml
├── playbooks/
│   ├── self_healing.md
│   ├── code_generation.md
│   └── mission_planning.md
└── datasets/
    ├── training_data.csv
    └── annotations.json
```

---

## 🎯 Use Cases

### 1. Manage Training Data
- Create prompt templates
- Edit few-shot examples
- Organize by domain
- Version control ready

### 2. Configure Ingestion
- Define source lists
- Create pipeline configs
- Edit scraping rules
- Test configurations

### 3. Knowledge Base Management
- Add documentation
- Create playbooks
- Update policies
- Tag and categorize

### 4. Team Collaboration
- Share training data
- Review prompts
- Validate knowledge
- Audit changes

---

## 🔧 Advanced Features (Coming Soon)

### Sync to Memory Fusion
```typescript
// "Save & Sync" button
await saveFile(path, content);
await syncToMemoryFusion(path); // Pushes to PersistentMemory
```

### Trust Scoring
-显示 file trust scores
- Validation status
- Review history
- Conflict detection

### Version History
- Track file versions
- Compare revisions
- Restore previous versions
- Audit trail

### LLM-Assisted Editing
- "Generate summary" button
- "Improve content" action
- "Extract key points"
- Inline suggestions

### Bulk Operations
- Multi-select files
- Batch tagging
- Group moves
- Bulk sync

### Real-Time Collaboration
- WebSocket updates
- See who's editing
- Lock files
- Conflict resolution

---

## 🧪 Testing

### Test File Operations
```bash
# After restart, test API:
curl http://localhost:8000/api/memory/status

# Create a test file
curl -X POST "http://localhost:8000/api/memory/file?path=test.md&content=Hello"

# List files
curl http://localhost:8000/api/memory/files

# Read file
curl "http://localhost:8000/api/memory/file?path=test.md"

# Delete file
curl -X DELETE "http://localhost:8000/api/memory/file?path=test.md"
```

### Test in UI
1. Click Memory Fusion in sidebar
2. Click "New File" button
3. Name it "test.md"
4. Type content in Monaco editor
5. Click Save (green button)
6. See file appear in tree
7. Click Delete
8. Confirm deletion

---

## 🔍 Monitoring

### Check Events
```bash
curl http://localhost:8000/api/clarity/events?limit=20
```

**You'll see:**
- `memory.file.saved` events
- `memory.file.deleted` events
- `component.activated` (memory_file_service)

### Check Component Status
```bash
curl http://localhost:8000/api/clarity/components
```

**Should show:**
- memory_file_service (VERIFIED trust)
- ingestion_orchestrator (HIGH trust)

---

## 📊 Stats

**After creating some files:**
```json
{
  "component_id": "...",
  "status": "active",
  "total_files": 5,
  "total_size_bytes": 12458,
  "total_size_mb": 0.01
}
```

---

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────────────┐
│ Memory Workspace              Total: 5 files, 0.01 MB  │
├──────────────┬──────────────────────────────────────────┤
│ File Tree    │ Editor: example.md         [Save] [Del]  │
│              │                                           │
│ 📁 prompts   │ Monaco Editor                            │
│   📄 test.md │ # Training Data                          │
│ 📁 knowledge │ This is sample content...                │
│   📄 faq.md  │                                           │
│              │ (Full syntax highlighting)               │
│ [📄] [📁]    │                                           │
└──────────────┴──────────────────────────────────────────┘
```

---

## 🎯 Next Steps

### Immediate (After Restart)
1. Create your first training file
2. Test save/delete operations
3. Organize into folders
4. Verify events in clarity

### Short-term
1. Add "Save & Sync" button
2. Wire to Memory Fusion
3. Add trust scoring display
4. Enable file tagging

### Long-term
1. Version history
2. LLM-assisted editing
3. Real-time collaboration
4. Bulk operations
5. Media preview

---

## 🏆 Benefits

**Unified Management:**
- All training data in one place
- No need for external editors
- Integrated with Grace platform
- Event-driven updates

**Developer Experience:**
- Monaco editor = VS Code feel
- Syntax highlighting
- Keyboard shortcuts
- Familiar interface

**Clarity Integration:**
- Component lifecycle managed
- Events tracked
- Trust levels enforced
- Observable operations

**Team-Friendly:**
- Non-developers can edit
- Visual interface
- No git required
- Easy collaboration

---

**Memory Workspace transforms Grace's knowledge base management from command-line operations to a professional, integrated file management system!** 🚀

**Restart both services to see it in action!**
