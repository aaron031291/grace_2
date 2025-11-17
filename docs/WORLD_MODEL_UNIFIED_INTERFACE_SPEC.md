# World Model: Unified Command Center Specification

**Date:** November 17, 2025  
**Status:** Planning  
**Goal:** Transform World Model into Grace's unified command center - replacing basic chat with a comprehensive interface that connects all capabilities

## Executive Summary

World Model will become Grace's central nervous system - a unified interface where users can:
- Communicate with Grace about everything she knows (internal world, tasks, learning loops)
- Approve/decline actions with governance oversight
- Upload multimodal content (images, video, voice, XXL files)
- Manage projects with folders and instructions
- Configure APIs and secrets
- Access all capabilities through connected tabs
- View immutable logs color-coded by system element

**Architecture:** World Model Hub as central interface → spawns specialized workspaces → all connected through shared world_model_store → backed by world_model_service facade

---

## Phase 1: World Model Hub (Core Interface)

**Goal:** Replace basic ChatView with WorldModelHub - the central command interface

### Features
1. **Dual-Pane Layout**
   - Left: Conversation thread with Grace
   - Right: World Context Panel showing:
     - Knowledge graph nodes
     - Recent artifacts
     - Active missions
     - Pending approvals
     - Learning jobs

2. **Inline Interactions**
   - ExecutionTrace viewer (click trace IDs to see reasoning)
   - InlineActionCard for approve/decline/simulate
   - Spawn workspace from conversation (`/spawn guardian`, `/spawn mission`, etc.)

3. **Unified Communication**
   - Text chat with Grace
   - Context-aware responses (Grace knows her internal state)
   - All conversations linked to world model

### Backend Requirements
- `world_model_service` facade with methods:
  - `query_context(user_query)` - Get relevant context
  - `link_trace(message_id, trace_id)` - Link execution traces
  - `list_recent_artifacts(limit)` - Recent memory items
  - `list_active_missions()` - Current missions
  - `list_pending_approvals()` - Governance queue

### API Endpoints
- `GET /api/world_model/context` - Get current context
- `GET /api/world_model/artifacts?limit=20` - Recent artifacts
- `GET /api/world_model/missions?status=active` - Active missions
- `POST /api/world_model/chat` - Send message to Grace
- `GET /api/world_model/trace/{trace_id}` - Get execution trace

### Acceptance Criteria
- ✅ Text chat works with Grace
- ✅ Traces open inline when clicked
- ✅ Can spawn workspace from conversation
- ✅ Context panel shows live items (artifacts, missions, approvals)
- ✅ All conversations stored and linked to world model

---

## Phase 2: Multimodal Attachments

**Goal:** Support images, video, files, and XXL uploads with chunked resumable uploads

### Features
1. **Unified AttachmentBar**
   - Drag-drop files directly into chat
   - Progress bars with pause/resume
   - Thumbnails for images/videos
   - File type validation and size limits

2. **Media Viewer**
   - Image gallery with zoom
   - Video player with controls
   - PDF viewer
   - Code preview (Monaco editor)

3. **XXL Upload Support**
   - Chunked uploads (configurable chunk size)
   - Resume after network interruption
   - Progress persistence across sessions

### Backend Requirements
- Chunked upload pipeline:
  - `POST /api/memory/uploads/init` - Initialize upload, get upload_id
  - `POST /api/memory/uploads/{upload_id}/chunk` - Upload chunk
  - `POST /api/memory/uploads/{upload_id}/finalize` - Complete upload
- Artifact ingestion into Memory
- Automatic linking to World Model

### API Endpoints
- `POST /api/memory/uploads/init` - Start upload
- `POST /api/memory/uploads/{upload_id}/chunk` - Upload chunk
- `POST /api/memory/uploads/{upload_id}/finalize` - Complete upload
- `GET /api/memory/artifacts/{artifact_id}` - Get artifact
- `GET /api/memory/artifacts/{artifact_id}/preview` - Get preview/thumbnail

### Acceptance Criteria
- ✅ Upload 2GB+ file successfully
- ✅ Resume upload after network interruption
- ✅ File appears in Memory and Context panel
- ✅ Thumbnails generated for images/videos
- ✅ Media viewer works for all supported types

---

## Phase 3: Voice & Voice Notes

**Goal:** Persistent voice through UI with voice notes saved to Memory

### Features
1. **Push-to-Talk**
   - Mic button in composer
   - Visual feedback while recording
   - Automatic transcription

2. **Persistent Voice Mode**
   - Toggle for continuous voice interaction
   - Grace responds with voice (optional TTS)
   - Conversation history includes transcripts

3. **Voice Notes**
   - Record and save voice notes
   - Stored as artifacts in Memory
   - Linked to conversations and world model

### Backend Requirements
- STT (Speech-to-Text) service integration
  - Whisper or existing skill
  - Real-time or batch transcription
- TTS (Text-to-Speech) for Grace's responses (optional)
- Voice note storage as artifacts

### API Endpoints
- `POST /api/media/stt` - Speech to text
- `POST /api/media/tts` - Text to speech (optional)
- `POST /api/memory/voice_notes` - Save voice note
- `GET /api/memory/voice_notes/{note_id}` - Get voice note

### Acceptance Criteria
- ✅ Talk to Grace, transcript appears in chat
- ✅ Grace responds with voice (if TTS enabled)
- ✅ Voice notes saved to Memory
- ✅ Transcripts linked to conversations

---

## Phase 4: Screen Share & Remote Access

**Goal:** Screen sharing and remote access with governance gates

### Features
1. **Screen Share**
   - Share screen via browser (getDisplayMedia)
   - Governance prompt before enabling
   - Participant can view shared screen

2. **Remote Access**
   - Launch remote session from World Model
   - Link to existing Terminal/agent capabilities
   - Governance approval required

### Backend Requirements
- Session negotiation endpoint (WebRTC/SFU or screenshot stream fallback)
- Governance gate enforcement
- Session logging for audit

### API Endpoints
- `POST /api/remote/screen_share/init` - Initialize screen share
- `POST /api/remote/session/start` - Start remote session
- `GET /api/remote/session/{session_id}/status` - Session status

### Acceptance Criteria
- ✅ Start screen share with governance prompt
- ✅ After approval, participant sees stream
- ✅ Remote tools launch from World Model
- ✅ All sessions logged in immutable audit trail

---

## Phase 5: Web Search & Learning Loops

**Goal:** Web search integration with learning job tracking

### Features
1. **Web Search**
   - Search from composer (`@web query`)
   - Results cited with provenance
   - Automatic ingestion into Memory

2. **Learning Jobs Dashboard**
   - Active learning jobs in Context panel
   - Progress tracking
   - Failed job triage
   - Link to reflection loop

### Backend Requirements
- Web search service integration
- Provenance tracking for search results
- Learning job orchestration
- Reflection loop integration

### API Endpoints
- `POST /api/search/query` - Web search
- `GET /api/learning/jobs?status=active` - Active learning jobs
- `GET /api/learning/jobs/{job_id}` - Job details
- `POST /api/learning/jobs/{job_id}/retry` - Retry failed job

### Acceptance Criteria
- ✅ Search results appear with citations
- ✅ Results ingested into Memory with provenance
- ✅ Learning jobs visible in Context panel
- ✅ Can retry failed jobs

---

## Phase 6: Governance UI & Immutable Logs

**Goal:** Comprehensive governance interface with color-coded immutable logs

### Features
1. **Approvals Inbox**
   - Inline panel in World Model
   - Filter by status, tier, domain, risk
   - Approve/Decline with one click
   - Bulk actions support

2. **Immutable Log Viewer**
   - Per action/skill audit trail
   - Trace ID, policy tier, outcome
   - Color-coded by system element:
     - 🔵 Event Bus (blue)
     - 🟢 Action Gateway (green)
     - 🟡 Reflection Loop (yellow)
     - 🔴 Skill Registry (red)
     - 🟣 Governance (purple)

3. **Governance Dashboard**
   - Dedicated workspace for deep-dive analytics
   - Policy violations
   - Approval history
   - Autonomy tier distribution

### Backend Requirements
- Immutable log storage (append-only)
- Color mapping in metadata
- Governance policy enforcement

### API Endpoints
- `GET /api/governance/approvals?status=pending` - Pending approvals
- `POST /api/governance/approvals/{approval_id}/approve` - Approve action
- `POST /api/governance/approvals/{approval_id}/decline` - Decline action
- `GET /api/governance/audit?trace_id={trace_id}` - Audit trail
- `GET /api/governance/policies` - Active policies

### Acceptance Criteria
- ✅ Approve/Decline from World Model
- ✅ Audit trail viewable with color coding
- ✅ Colors consistent across UI
- ✅ Immutable logs tamper-proof
- ✅ Governance workspace shows analytics

---

## Phase 7: Projects & API Config (Secrets Vault)

**Goal:** Project management like GPT/Claude with secure API configuration

### Features
1. **Projects**
   - Create project folders
   - Upload files with instructions
   - Pin context for project
   - Switch active project in World Model

2. **Secrets Vault**
   - Paste API keys
   - Test connections (OpenAI, GitHub, Slack, AWS, etc.)
   - Auto-configure skills
   - Namespaced secrets (global, per-env, per-tenant, per-agent)
   - Masked values (click to reveal, auto-hide after 10s)
   - Usage logs
   - Rotation reminders (alert when > 90 days old)

3. **API Auto-Config**
   - Copy/paste API key
   - Automatic skill configuration
   - Test connection wizard
   - Policy enforcement (prevent exfiltration)

### Backend Requirements
- Project storage and management
- Secrets encryption at rest
- Secret usage tracking
- Test connection endpoints for common providers

### API Endpoints
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{project_id}` - Get project details
- `POST /api/projects/{project_id}/artifacts` - Upload to project
- `POST /api/secrets` - Store secret
- `GET /api/secrets` - List secrets (masked)
- `POST /api/secrets/{secret_id}/test` - Test connection
- `GET /api/secrets/{secret_id}/usage` - Usage logs

### Acceptance Criteria
- ✅ Create project, upload files, set instructions
- ✅ Paste API key, test connection succeeds
- ✅ Skill automatically uses configured key
- ✅ Secrets masked by default
- ✅ Usage logs show which agents accessed secrets

---

## Architecture

### Frontend Architecture

```
WorldModelHub (main interface)
├── ConversationPane (left)
│   ├── MessageList
│   ├── ExecutionTraceViewer (inline)
│   ├── InlineActionCard (approve/decline)
│   └── Composer (text, voice, attachments)
└── ContextPane (right)
    ├── KnowledgeGraph
    ├── RecentArtifacts
    ├── ActiveMissions
    ├── PendingApprovals
    ├── LearningJobs
    └── ProjectSelector
```

### Backend Architecture

```
world_model_service (facade)
├── query_context()
├── link_trace()
├── list_artifacts()
├── list_missions()
├── list_approvals()
├── ingest_artifact()
├── add_secret()
└── list_projects()

Connected to:
├── event_bus
├── action_gateway
├── reflection_loop
├── skill_registry
├── memory_service
└── governance_service
```

### State Management

```
world_model_store (Zustand/Context)
├── conversations
├── artifacts
├── missions
├── approvals
├── learning_jobs
├── projects
└── active_project

Updated by:
├── Event bus subscriptions
├── API polling (3s interval)
└── WebSocket/SSE (future)
```

---

## Implementation Priority

1. **Phase 1** (Week 1-2): World Model Hub - Core interface
2. **Phase 2** (Week 2-3): Multimodal attachments
3. **Phase 3** (Week 3-4): Voice & voice notes
4. **Phase 5** (Week 4-5): Web search & learning loops (parallel with Phase 3)
5. **Phase 6** (Week 5-6): Governance UI & immutable logs
6. **Phase 4** (Week 6-7): Screen share & remote access (after governance gates)
7. **Phase 7** (Week 7-8): Projects & Secrets Vault

---

## Hardening Requirements

### Error Handling
- Retries with exponential backoff for API calls
- Resumable uploads with state persistence
- Clear user-facing errors with remediation steps
- Graceful degradation when services unavailable

### Validation
- File type/size limits enforced
- MIME type validation
- Sandboxed media viewing
- Governance prompts for risky actions

### Observability
- Structured logs with trace IDs
- User-friendly status in UI
- Backend SLIs: upload success rate, p95 latencies, error rates
- Real-time health monitoring

### Testing
- Unit tests for UI components and backend services
- Integration tests for upload → ingest → world model link → display
- E2E tests: approve flow, spawn workspace, web search with provenance
- Soak tests for large uploads and persistent voice sessions

### Security
- Secrets never rendered unmasked by default
- Copy-to-clipboard protected
- Immutable log tamper-proofing
- Governance tiers enforced server-side
- Screen share/remote access gated by governance

### Feature Flags
- Screen share/remote access (disabled by default)
- Voice TTS (optional)
- Web search (configurable providers)
- XXL upload limits (configurable)

---

## Success Metrics

### Phase 1
- World Model Hub replaces basic chat
- 100% of conversations linked to world model
- Context panel shows live data
- Can spawn workspaces from conversation

### Phase 2
- Upload success rate ≥ 99%
- Support files up to 10GB
- Resume success rate ≥ 95%
- Media viewer works for all supported types

### Phase 3
- Voice transcription accuracy ≥ 95%
- Voice notes saved to Memory
- TTS response time < 2s

### Phase 4
- Screen share works with governance gate
- Remote access sessions logged
- Zero unauthorized access attempts

### Phase 5
- Web search results cited with provenance
- Learning jobs tracked and visible
- Failed job retry success rate ≥ 80%

### Phase 6
- Approve/Decline from World Model
- Immutable logs viewable with color coding
- Zero log tampering incidents

### Phase 7
- Projects created and managed
- API keys configured and tested
- Secrets masked by default
- Usage logs accurate

---

## Open Questions

1. **WebRTC Infrastructure:** Do we have SFU/TURN servers for screen share, or should we use screenshot stream fallback?
2. **STT/TTS Providers:** Which providers are approved? Cost constraints?
3. **Storage Backend:** Local disk, S3, or other? Pre-signed URLs allowed?
4. **HTM Integration:** What is HTM and where is it in the codebase?
5. **WebSocket/SSE:** Can we use real-time connections, or must we continue polling?
6. **Max File Sizes:** What are the limits for XXL uploads?
7. **Governance Color Mapping:** Confirm color scheme for system elements
8. **Existing Endpoints:** Which world model endpoints already exist?

---

## Next Steps

1. Get user confirmation on architecture and priorities
2. Start Phase 1: World Model Hub implementation
3. Create backend `world_model_service` facade
4. Build frontend WorldModelHub component
5. Wire to existing event bus, action gateway, reflection loop
6. Test and iterate
