# Unified Grace Console (UI Spec)

## Overview
Grace’s front end centers on three persistent pillars plus lightweight pop-out workspaces:

1. **Live Logs Pane** – continuous, color-coded event stream with filters (subsystem, mission ID, severity). Key events (follow-up launched, stakeholder alert) can be pinned.
2. **Multimodal Chat** – primary interaction surface (text, voice, attachments). Every response cites the underlying mission outcome or KPI so users can jump straight to context.
3. **Task Manager** – board/list of active, proactive, and follow-up missions with subsystem tags, current KPI deltas, and quick actions (acknowledge, request details, open preventive mission).
4. **Dynamic Workspaces (Pop-Out Tabs)** – on request (“open CRM latency dashboard”, “show mission followup_123”), Grace spawns a dedicated tab/window showing relevant charts, logs, code, or reports. Tabs remain lightweight and can be closed without affecting the main console.

Optional widgets (daily brief summary, approvals shortcut) can sit beside the chat pane but are secondary to the pillars above.

## Interaction Flow
1. User watches the log stream; any critical entry can be pinned or opened in a workspace.
2. Chat drives deeper questions (“Why the follow-up?”) and can spawn workspace tabs for detailed views (mission evidence, KPI graphs).
3. Task manager keeps missions/follow-ups front and center, allowing quick acknowledgement or escalation.
4. Grace can open multiple workspaces simultaneously; each tab references the same RAG/world-model context so knowledge stays cohesive.

## Data Sources
- Logs pane consumes trigger mesh / mission events.
- Chat leverages existing RAG + world-model APIs.
- Task manager reflects mission control, follow-up planner, and retrospectives.
- Workspaces reuse existing dashboards or render tailored views (e.g., KPI charts, code diffs).
