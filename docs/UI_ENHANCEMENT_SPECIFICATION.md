# Grace UI Enhancement Specification

**Version:** 1.0  
**Date:** November 17, 2025  
**Status:** Implementation Ready

## Executive Summary

This document specifies the comprehensive UI/UX redesign for Grace, transforming it into a ChatGPT-style enterprise interface with advanced features for autonomous AI interaction, domain-morphic workspaces, and enterprise-grade capabilities.

## Design Philosophy

**Core Principles:**
- **Professional & Clean**: ChatGPT-inspired aesthetic with modern, minimal design
- **Domain Morphic**: Conversations spawn focused workspaces for specific domains
- **Transparency First**: Every action shows execution trace and reasoning
- **Enterprise Ready**: SSO, RBAC, audit trails, and compliance features
- **Power User Friendly**: Keyboard shortcuts, command palette, and advanced workflows

## Architecture Overview

```
Grace UI Architecture
├── Left Sidebar (Navigation)
│   ├── Grace Capabilities (Primary Nav)
│   ├── Workspaces (Domain-specific contexts)
│   └── Chat History
├── Main Content Area
│   ├── Active Workspace/Chat
│   ├── Command Palette (Ctrl-K overlay)
│   └── ExecutionTrace Panel (slide-over)
├── Top Bar
│   ├── Health Status (always visible)
│   ├── Global Search
│   └── User Menu
└── Bottom Bar
    └── Input Area (context-aware)
```

## Feature Specifications

### 1. ChatGPT-Style Layout

**Left Sidebar (260px width, collapsible)**

**Section 1: Core Actions**
- New Chat button (prominent, top)
- Search Chats (with keyboard shortcut)
- Command Palette trigger (Ctrl-K)

**Section 2: Grace Capabilities** (Primary Navigation)
```
🛡️ Guardian          - Network Healing (OSI Layers 2-7)
🔧 Self-Healing      - Infrastructure Automation
🤖 Copilot           - Autonomous Coding Agent
🌍 World Model       - Knowledge Base Management
🧠 Learning Engine   - Autonomous Learning
⚖️ Governance        - Approvals & Policies
🎯 Mission Control   - Task Orchestration
👁️ Observatory       - System Health & Metrics
💾 Memory            - File Explorer & Secrets Vault
⚡ Terminal          - Natural Language Shell
```

**Section 3: Workspaces** (Domain Morphic)
- Active workspaces with status indicators
- "+" button to create new workspace
- Drag to reorder
- Right-click context menu (rename, close, merge)

**Section 4: Chat History**
- Grouped by date (Today, Yesterday, Last 7 days, etc.)
- Search/filter
- Pin important chats
- Archive old chats

**Main Content Area**

**Chat View:**
- Clean, centered layout (max-width: 800px)
- Message bubbles with user/grace distinction
- Inline action cards for approvals
- Code blocks with syntax highlighting
- File attachments with previews
- ExecutionTrace button on each response

**Workspace View:**
- Split layout with context panel
- Domain-specific tools and shortcuts
- KPI dashboard for workspace
- Related resources sidebar

**Input Area:**
- Multi-line text input with auto-resize
- Voice input button
- File attachment button
- @ mentions for agents/capabilities
- / commands for quick actions
- Ctrl-Enter to send

### 2. Command Palette (Ctrl-K)

**Trigger:** Ctrl-K (Cmd-K on Mac)

**Features:**
- Fuzzy search across all actions
- Recent actions at top
- Categorized results:
  - Actions (Run playbook, Create mission, etc.)
  - Navigation (Go to Guardian, Open Memory, etc.)
  - Governance (Approve request #142, etc.)
  - Search (Find in World Model, Search files, etc.)

**Example Commands:**
```
run playbook network-heal
create mission deploy-crm
approve governance #142
open secrets vault
search world model "kubernetes"
go to observatory
new workspace guardian
```

**Implementation:**
- Modal overlay with backdrop blur
- Keyboard navigation (arrow keys, enter)
- Escape to close
- Show keyboard shortcuts in results
- Execute action on selection

### 3. ExecutionTrace Panel

**Trigger:** Click "Why/How" button on any response

**Layout:** Right-side slide-over panel (400px width)

**Content:**
```
ExecutionTrace
├── Request ID: uuid
├── Duration: 1.2s
├── Steps (expandable tree)
│   ├── Step 1: Query World Model
│   │   ├── Component: world_model_service
│   │   ├── Action: semantic_search
│   │   ├── Duration: 200ms
│   │   ├── Data Source: world_knowledge.json
│   │   └── Result: 5 entries found
│   ├── Step 2: Check Confidence
│   │   └── ...
│   └── Step 3: Generate Response
│       └── ...
├── Data Sources Used
│   ├── world_knowledge.json (confidence: 0.92)
│   ├── grace.db (confidence: 1.0)
│   └── llm:qwen2.5:32b (confidence: 0.85)
├── Agents Involved
│   ├── world_model_agent
│   └── conversation_agent
└── Links
    ├── View Logs
    ├── View Artifacts
    └── Export Trace
```

**Features:**
- Expandable/collapsible steps
- Click to view detailed data
- Copy trace ID
- Export as JSON
- Link to related logs/artifacts

### 4. Health Bar (Always Visible)

**Location:** Top bar, right side

**Display:**
```
Health: 79% | Trust: 75% | Confidence: 73%
```

**Color Coding:**
- Green: ≥ 90%
- Yellow: 70-89%
- Red: < 70%

**Click to Expand:**
- Mini dashboard showing domain breakdown
- Recent issues
- Quick link to Observatory
- Trend indicators (↑↓→)

### 5. Workspaces (Domain Morphic)

**Concept:** When Grace identifies a domain/topic in conversation, suggest creating a focused workspace for that context.

**Trigger Detection:**
- Keywords: "guardian", "network", "healing", "playbook" → Suggest Guardian workspace
- Keywords: "code", "pr", "deploy", "build" → Suggest Copilot workspace
- Keywords: "approve", "policy", "governance" → Suggest Governance workspace
- Keywords: "learn", "search", "knowledge" → Suggest Learning workspace

**Suggestion UI:**
```
┌─────────────────────────────────────────────────┐
│ 🛡️ Create Guardian Workspace?                   │
│                                                  │
│ This conversation involves network healing.     │
│ A focused workspace will give you:              │
│ • Network health dashboard                      │
│ • Playbook quick actions                        │
│ • Recent healing runs                           │
│                                                  │
│ [Create Workspace]  [Not Now]  [Don't Ask]     │
└─────────────────────────────────────────────────┘
```

**Workspace Features:**
- Dedicated context (separate chat history)
- Domain-specific tools in sidebar
- KPI dashboard
- Quick actions
- Related resources
- Can spawn from existing chat or create new

**Workspace Types:**
1. **Guardian Workspace**: Network health, playbooks, healing runs
2. **Copilot Workspace**: Code editor, PR list, CI status, test results
3. **Governance Workspace**: Approval queue, policy editor, audit log
4. **Learning Workspace**: Knowledge search, ingestion queue, learning jobs
5. **Mission Workspace**: Mission designer, timeline, contracts, verification
6. **Memory Workspace**: File explorer, secrets vault, artifact browser
7. **Observatory Workspace**: System metrics, domain health, alerts

### 6. Secrets Vault (Enterprise-Grade)

**Location:** Memory capability → Secrets tab

**Layout:**
```
Secrets Vault
├── Namespaces (left sidebar)
│   ├── Global
│   ├── Development
│   ├── Staging
│   ├── Production
│   └── Per-Agent
├── Secret List (center)
│   ├── Search/Filter
│   ├── Sort by: Name, Updated, Scope
│   └── Secret Cards
└── Secret Detail (right panel)
    ├── Name
    ├── Scope (env/project/agent)
    ├── Value (masked with reveal button)
    ├── Test Connection button
    ├── Rotation reminder
    ├── Usage log
    └── Actions (Edit, Delete, Copy)
```

**Features:**
- **Namespaced Secrets**: Global, per-env, per-tenant, per-agent
- **Test Connection Wizards**: OpenAI, GitHub, Slack, AWS, etc.
- **Masked Values**: Click to reveal, auto-hide after 10s
- **Copy Button**: Copy to clipboard with notification
- **Rotation Reminders**: Alert when secret is > 90 days old
- **Usage Logs**: Show which agents accessed secret and when
- **Policy Enforcement**: Prevent exfiltration to non-whitelisted agents
- **Audit Trail**: All access logged to immutable log

**Test Connection Wizards:**
```
OpenAI:
  - Input: API key
  - Test: Call /v1/models endpoint
  - Result: ✓ Valid (shows available models) or ✗ Invalid (error message)

GitHub:
  - Input: Personal Access Token
  - Test: Call /user endpoint
  - Result: ✓ Valid (shows username) or ✗ Invalid

AWS:
  - Input: Access Key ID, Secret Access Key, Region
  - Test: Call sts:GetCallerIdentity
  - Result: ✓ Valid (shows account ID) or ✗ Invalid
```

### 7. Inline Action Cards

**Concept:** When Grace proposes an action, show an actionable card instead of plain text.

**Example: Approval Request**
```
┌─────────────────────────────────────────────────┐
│ 🔧 Self-Healing Action Required                 │
│                                                  │
│ Playbook: restart-nginx                         │
│ Risk: Medium (Tier 2)                           │
│ Reason: HTTP 502 errors detected                │
│                                                  │
│ Expected Effects:                               │
│ • Nginx service restart                         │
│ • ~5s downtime                                  │
│ • Clears connection pool                        │
│                                                  │
│ Rollback Plan:                                  │
│ • Restore previous config                       │
│ • Restart with --safe-mode                      │
│                                                  │
│ KPIs to Improve:                                │
│ • HTTP 502 rate: 15% → 0%                       │
│ • Response time: 2.5s → 0.3s                    │
│                                                  │
│ [Approve] [Simulate] [Reject] [View Details]   │
└─────────────────────────────────────────────────┘
```

**Card Types:**
1. **Approval Request**: Approve/Simulate/Reject buttons
2. **Mission Proposal**: View Plan/Start Mission/Decline
3. **Learning Job**: Start Learning/Skip/Add to Queue
4. **File Upload**: Preview/Save to Memory/Discard
5. **Code Change**: View Diff/Apply/Reject
6. **Knowledge Update**: Accept/Edit/Reject

### 8. Drag-Drop File Upload

**Trigger:** Drag file over chat area or Memory workspace

**Visual Feedback:**
- Overlay with dashed border
- "Drop files here to upload" message
- Show file count if multiple

**Upload Flow:**
1. Drop files → Show upload progress
2. Process files (scan, extract metadata)
3. Show preview card with options:
   - Save to Memory (choose folder)
   - Ingest as Knowledge (add to World Model)
   - Attach to Message (send with next chat)
   - Discard

**Supported File Types:**
- Documents: .pdf, .docx, .txt, .md
- Code: .py, .js, .ts, .java, .go, etc.
- Data: .csv, .json, .yaml, .xml
- Images: .png, .jpg, .gif, .svg
- Archives: .zip, .tar.gz

### 9. Mission Designer Canvas

**Location:** Mission Control capability

**Layout:** Visual DAG (Directed Acyclic Graph) editor

**Components:**
- **Nodes**: ActionContracts (draggable)
- **Edges**: Dependencies (connect nodes)
- **Toolbar**: Add node, delete, zoom, fit to screen
- **Properties Panel**: Edit selected node

**Node Types:**
1. **Action Node**: Execute action (green)
2. **Verification Node**: Check condition (blue)
3. **Decision Node**: Branch based on result (yellow)
4. **SafeHold Node**: Create snapshot (purple)
5. **Rollback Node**: Restore snapshot (red)

**Features:**
- Drag nodes from palette
- Connect nodes to define flow
- Edit node properties (expected effects, verification hooks)
- Simulate mission (dry-run)
- View cost/time/impact estimates
- Save as template
- Export as YAML

**Example Mission:**
```
[Start] → [SafeHold Snapshot] → [Apply Code Change] → [Run Tests]
                                         ↓ (if fail)
                                    [Rollback] → [End]
                                         ↓ (if pass)
                                  [Deploy to Staging] → [Verify] → [End]
```

### 10. Memory Pro Features

**Location:** Memory capability

**Layout:** Dual-pane file manager

**Left Pane:** File tree with folders
**Right Pane:** File list or file preview

**Features:**

**File Operations:**
- Create/rename/delete files and folders
- Move/copy files (drag-drop or context menu)
- Bulk operations (select multiple, apply action)
- Upload files (drag-drop or button)
- Download files (single or bulk)

**Version History:**
- Click "History" button on file
- Show list of revisions with timestamps
- Diff view between versions
- Restore previous version

**Preview:**
- Code: Syntax highlighting with Monaco editor
- Markdown: Rendered preview
- Images: Thumbnail and full view
- PDF: Embedded viewer
- JSON/YAML: Formatted with collapsible tree

**Search:**
- Full-text search across all files
- Filter by file type, date, size
- Regex support
- Search in file content

**Quick Actions:**
- "Save to World Model" - Ingest file as knowledge
- "Pin as Source" - Mark as trusted source
- "Share" - Generate shareable link
- "Export" - Download as zip

### 11. Approval Inbox

**Location:** Governance capability

**Layout:**
```
Approval Inbox
├── Filters (top bar)
│   ├── Status: Pending/Approved/Rejected/All
│   ├── Tier: 1/2/3/All
│   ├── Domain: Guardian/Copilot/Learning/All
│   └── Risk: Low/Medium/High/All
├── Approval List (left, 40%)
│   └── Cards with: Title, Risk, Tier, Timestamp
└── Approval Detail (right, 60%)
    ├── Request Info
    ├── Proposed Action
    ├── Expected Effects
    ├── Rollback Plan
    ├── Risk Assessment
    ├── Alternative Plans (if available)
    └── Actions: Approve/Reject/Request Changes
```

**Features:**
- **Bulk Actions**: Select multiple, approve/reject all
- **Compare Plans**: View alternative approaches side-by-side
- **Notifications**: Email/Slack alerts for new requests
- **Deep Links**: Direct link to specific approval
- **Approval History**: View past decisions
- **Delegation**: Assign approval to another user

### 12. Global Search

**Location:** Top bar, center

**Trigger:** Click search box or Ctrl-F

**Search Across:**
- Chat history
- Files in Memory
- World Model entries
- Missions
- Playbooks
- Approval requests
- Logs

**Results Grouped By:**
- Chats (show message snippet)
- Files (show file path and preview)
- Knowledge (show entry content)
- Missions (show goal and status)
- Approvals (show title and status)

**Quick Actions on Results:**
- Open in context
- Copy link
- Share
- Add to workspace

## Technical Implementation

### Technology Stack

**Frontend:**
- React 19.1.1
- TypeScript 5.9.3
- Vite 7.1.7
- Framer Motion (animations)
- Lucide React (icons)
- Monaco Editor (code editing)
- React Router (navigation)
- Zustand (state management)

**UI Components:**
- Custom component library (no external UI framework)
- Tailwind CSS for styling
- CSS Grid and Flexbox for layouts
- CSS Variables for theming

### State Management

**Global State (Zustand):**
```typescript
interface GraceStore {
  // User & Auth
  user: User | null;
  token: string | null;
  
  // Navigation
  activeCapability: Capability;
  activeWorkspace: Workspace | null;
  workspaces: Workspace[];
  
  // UI State
  commandPaletteOpen: boolean;
  executionTracePanelOpen: boolean;
  selectedTrace: ExecutionTrace | null;
  
  // Health
  systemHealth: HealthMetrics;
  
  // Actions
  setActiveCapability: (capability: Capability) => void;
  createWorkspace: (type: WorkspaceType, context?: any) => void;
  closeWorkspace: (id: string) => void;
  toggleCommandPalette: () => void;
  showExecutionTrace: (trace: ExecutionTrace) => void;
}
```

**Local State (React hooks):**
- Component-specific UI state
- Form inputs
- Temporary data

### API Integration

**Base URL:** `http://localhost:8000/api`

**Key Endpoints:**
- `POST /chat` - Send message
- `GET /governance/approvals` - List approvals
- `POST /governance/approvals/{id}/decision` - Approve/reject
- `GET /mission-control/missions` - List missions
- `POST /mission-control/missions` - Create mission
- `GET /memory/files` - File tree
- `POST /memory/files/upload` - Upload file
- `GET /metrics/summary` - System health
- `POST /knowledge/search` - Search World Model

**Response Format:**
```typescript
interface SuccessResponse<T> {
  success: true;
  data: T;
  execution_trace: ExecutionTrace;
  data_provenance: DataProvenance;
}
```

### Keyboard Shortcuts

**Global:**
- `Ctrl-K` / `Cmd-K` - Command Palette
- `Ctrl-F` / `Cmd-F` - Global Search
- `Ctrl-N` / `Cmd-N` - New Chat
- `Ctrl-B` / `Cmd-B` - Toggle Sidebar
- `Ctrl-/` / `Cmd-/` - Show Shortcuts Help
- `Esc` - Close Modal/Panel

**Chat:**
- `Ctrl-Enter` / `Cmd-Enter` - Send Message
- `Shift-Enter` - New Line
- `↑` - Edit Last Message
- `Ctrl-L` / `Cmd-L` - Clear Chat

**Navigation:**
- `Ctrl-1` to `Ctrl-9` - Switch to Capability 1-9
- `Ctrl-Tab` - Next Workspace
- `Ctrl-Shift-Tab` - Previous Workspace

### Accessibility

**WCAG 2.1 Level AA Compliance:**
- Keyboard navigation for all features
- Screen reader support (ARIA labels)
- Focus indicators
- Color contrast ratios ≥ 4.5:1
- Alt text for images
- Semantic HTML

### Performance

**Optimization Strategies:**
- Virtual scrolling for long lists (chat history, file lists)
- Lazy loading for components
- Code splitting by route
- Image optimization
- Debounced search
- Memoized expensive computations
- WebSocket for real-time updates

**Target Metrics:**
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1

### Security

**Client-Side Security:**
- JWT token stored in memory (not localStorage)
- CSRF protection
- XSS prevention (sanitize user input)
- Content Security Policy
- Secure WebSocket (wss://)

**Data Handling:**
- Secrets never logged
- Sensitive data masked in UI
- Audit trail for all actions
- Session timeout (30 min idle)

## Design System

### Color Palette

**Primary Colors:**
```css
--color-primary: #7b2cbf;      /* Purple */
--color-primary-light: #9d4edd;
--color-primary-dark: #5a189a;

--color-secondary: #00d4ff;    /* Cyan */
--color-secondary-light: #33ddff;
--color-secondary-dark: #00a8cc;
```

**Neutral Colors:**
```css
--color-bg: #0f0f1e;           /* Dark background */
--color-bg-secondary: #1a1a2e; /* Card background */
--color-bg-tertiary: #252538;  /* Hover state */

--color-text: #ffffff;         /* Primary text */
--color-text-secondary: #b8b8d1; /* Secondary text */
--color-text-tertiary: #888899; /* Disabled text */
```

**Semantic Colors:**
```css
--color-success: #00ff88;
--color-warning: #ffcc00;
--color-error: #ff4444;
--color-info: #00d4ff;
```

### Typography

**Font Family:**
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'Fira Code', 'Consolas', 'Monaco', monospace;
```

**Font Sizes:**
```css
--text-xs: 0.75rem;   /* 12px */
--text-sm: 0.875rem;  /* 14px */
--text-base: 1rem;    /* 16px */
--text-lg: 1.125rem;  /* 18px */
--text-xl: 1.25rem;   /* 20px */
--text-2xl: 1.5rem;   /* 24px */
--text-3xl: 1.875rem; /* 30px */
--text-4xl: 2.25rem;  /* 36px */
```

### Spacing

**Scale (8px base):**
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

### Border Radius

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 9999px;
```

### Shadows

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.2);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.3);
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Set up new component structure
- Implement design system (colors, typography, spacing)
- Create base layout (sidebar, main area, top bar)
- Implement navigation between capabilities

### Phase 2: Core Features (Week 2)
- Command Palette
- ExecutionTrace Panel
- Health Bar
- Inline Action Cards

### Phase 3: Workspaces (Week 3)
- Workspace creation and management
- Domain detection and suggestions
- Workspace-specific tools
- Workspace persistence

### Phase 4: Advanced Features (Week 4)
- Secrets Vault
- Mission Designer Canvas
- Memory Pro features
- Approval Inbox

### Phase 5: Polish & Optimization (Week 5)
- Keyboard shortcuts
- Accessibility improvements
- Performance optimization
- Testing and bug fixes

## Success Metrics

**User Experience:**
- Task completion time reduced by 50%
- User satisfaction score ≥ 4.5/5
- Feature adoption rate ≥ 80% for core features

**Performance:**
- Page load time < 2s
- Interaction response time < 100ms
- 60 FPS animations

**Adoption:**
- 95% of operations doable from UI (no CLI required)
- Command Palette usage ≥ 40% of power users
- Workspace creation ≥ 3 per user per week

## Conclusion

This specification provides a comprehensive blueprint for transforming Grace's UI into a world-class, enterprise-ready interface. The ChatGPT-style layout combined with domain-morphic workspaces, command palette, and execution transparency will make Grace the most powerful and user-friendly autonomous AI system available.

---

**Document Version:** 1.0  
**Last Updated:** November 17, 2025  
**Owner:** Grace Development Team  
**Status:** Implementation Ready
