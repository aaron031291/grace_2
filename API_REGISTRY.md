# Grace API Registry

**Total Endpoints:** 427

**Last Updated:** 2025-11-18

## Table of Contents

- [Autonomous Learning](#autonomous-learning)
- [Autonomous Navigation](#autonomous-navigation)
- [Autonomous Web Learning](#autonomous-web-learning)
- [Competitor Tracking](#competitor-tracking)
- [Crypto Trading](#crypto-trading)
- [Curriculum Learning](#curriculum-learning)
- [Domain System](#domain-system)
- [Future Projects Learning](#future-projects-learning)
- [Grace's World Model](#grace's-world-model)
- [Infrastructure](#infrastructure)
- [Learning Visibility](#learning-visibility)
- [Metrics](#metrics)
- [Mission Control](#mission-control)
- [Operator Dashboard](#operator-dashboard)
- [Phase 7: SaaS Readiness](#phase-7:-saas-readiness)
- [Phase 8: E2E Testing & Production Readiness](#phase-8:-e2e-testing-and-production-readiness)
- [Port Manager](#port-manager)
- [Remote Access & Zero Trust](#remote-access-and-zero-trust)
- [SaaS Builder](#saas-builder)
- [Secure Vault](#secure-vault)
- [Storage Tracking](#storage-tracking)
- [Uncategorized](#uncategorized)
- [Vector Operations](#vector-operations)
- [agentic](#agentic)
- [auth](#auth)
- [console](#console)
- [copilot](#copilot)
- [copilot-pipeline](#copilot-pipeline)
- [guardian](#guardian)
- [ingestion](#ingestion)
- [learning](#learning)
- [learning-control](#learning-control)
- [learning-hub](#learning-hub)
- [logs](#logs)
- [memory](#memory)
- [phase6](#phase6)
- [trust_framework](#trust_framework)
- [world_model_hub](#world_model_hub)

---

## Autonomous Learning

**Endpoints:** 7

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/learning/curriculum/overview` | Get Curriculum Overview |
| GET | `/api/learning/domain/{domain_id}` | Get Domain Status |
| GET | `/api/learning/progress` | Get Learning Progress |
| POST | `/api/learning/project/complete` | Complete Project |
| POST | `/api/learning/project/start` | Start Next Project |
| POST | `/api/learning/project/work` | Work On Project |
| GET | `/api/learning/projects/priority` | Get Priority Projects |

## Autonomous Navigation

**Endpoints:** 4

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/web-navigator/auto-navigate` | Auto Navigate |
| GET | `/api/web-navigator/metrics` | Get Navigator Metrics |
| GET | `/api/web-navigator/playbook` | Get Playbook |
| GET | `/api/web-navigator/should-search` | Should Search |

## Autonomous Web Learning

**Endpoints:** 8

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/web-learning/autonomous-research` | Start Autonomous Research |
| GET | `/api/web-learning/explore/{domain}` | Explore Domain |
| POST | `/api/web-learning/learn-topic` | Learn Topic |
| POST | `/api/web-learning/search` | Search Web |
| GET | `/api/web-learning/stats` | Get Learning Stats |
| GET | `/api/web-learning/whitelist` | Get Whitelist |
| POST | `/api/web-learning/whitelist/add` | Add Trusted Domain |
| POST | `/api/web-learning/whitelist/block` | Block Domain |

## Competitor Tracking

**Endpoints:** 3

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/competitors/analyze-patterns` | Analyze Patterns |
| GET | `/api/competitors/metrics` | Get Tracking Metrics |
| POST | `/api/competitors/track` | Track Competitor |

## Crypto Trading

**Endpoints:** 3

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/crypto/install-apis` | Install Crypto Apis |
| GET | `/api/crypto/status` | Get Crypto Api Status |
| GET | `/api/crypto/test-apis` | Test Crypto Apis |

## Curriculum Learning

**Endpoints:** 4

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/curriculum/discovered` | Get Discovered Curricula |
| GET | `/api/curriculum/metrics` | Get Orchestrator Metrics |
| GET | `/api/curriculum/status` | Get Learning Status |
| POST | `/api/curriculum/trigger-learning` | Trigger Learning |

## Domain System

**Endpoints:** 26

| Method | Path | Summary |
|--------|------|----------|
| GET | `/domains/capabilities` | Get Capability Map |
| GET | `/domains/domain/{domain_id}` | Get Domain Info |
| GET | `/domains/events/history` | Get Event History |
| POST | `/domains/events/publish` | Publish Event |
| GET | `/domains/events/stats` | Get Event Stats |
| POST | `/domains/events/subscribe` | Subscribe To Events |
| GET | `/domains/events/subscriptions` | Get Subscriptions |
| GET | `/domains/find-by-capability/{capability}` | Find Domains By Capability |
| POST | `/domains/heartbeat/{domain_id}` | Domain Heartbeat |
| GET | `/domains/list` | List Domains |
| POST | `/domains/memory/apply/{contribution_id}` | Apply Contribution |
| POST | `/domains/memory/contribute` | Contribute To Memory |
| GET | `/domains/memory/domain/{domain_id}` | Get Domain Contributions |
| GET | `/domains/memory/query` | Query Collective Memory |
| GET | `/domains/memory/stats` | Get Memory Stats |
| GET | `/domains/memory/top-contributors` | Get Top Contributors |
| POST | `/domains/memory/verify/{contribution_id}` | Verify Contribution |
| POST | `/domains/register` | Register Domain |
| GET | `/domains/registry-stats` | Get Registry Stats |
| GET | `/domains/system/health` | Get System Health |
| GET | `/domains/system/overview` | Get System Overview |
| GET | `/domains/workflows-stats` | Get Workflow Stats |
| POST | `/domains/workflows/create` | Create Workflow |
| POST | `/domains/workflows/execute/{workflow_id}` | Execute Workflow |
| GET | `/domains/workflows/list` | List Workflows |
| GET | `/domains/workflows/{workflow_id}` | Get Workflow |

## Future Projects Learning

**Endpoints:** 6

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/future-projects/curriculum` | Get Curriculum |
| POST | `/api/future-projects/learn-all` | Learn All Domains |
| POST | `/api/future-projects/learn-domain` | Learn Domain |
| GET | `/api/future-projects/metrics` | Get Metrics |
| GET | `/api/future-projects/progress/{domain}` | Get Domain Progress |
| GET | `/api/future-projects/readiness` | Get Readiness |

## Grace's World Model

**Endpoints:** 10

| Method | Path | Summary |
|--------|------|----------|
| POST | `/world-model/add-knowledge` | Add Knowledge |
| POST | `/world-model/ask-grace` | Ask Grace |
| POST | `/world-model/initialize` | Initialize World Model |
| GET | `/world-model/mcp/manifest` | Get Mcp Manifest |
| GET | `/world-model/mcp/resource` | Get Mcp Resource |
| POST | `/world-model/mcp/tool` | Call Mcp Tool |
| POST | `/world-model/query` | Query World Model |
| GET | `/world-model/self-knowledge` | Get Self Knowledge |
| GET | `/world-model/stats` | Get World Model Stats |
| GET | `/world-model/system-knowledge` | Get System Knowledge |

## Infrastructure

**Endpoints:** 16

| Method | Path | Summary |
|--------|------|----------|
| GET | `/infrastructure/discovery/by-capability/{capability}` | Find By Capability |
| GET | `/infrastructure/discovery/service/{service_id}` | Get Service |
| GET | `/infrastructure/discovery/services` | Get All Services |
| GET | `/infrastructure/discovery/stats` | Get Discovery Stats |
| GET | `/infrastructure/gateway/circuit-breakers` | Get Circuit Breakers |
| GET | `/infrastructure/gateway/request-history` | Get Request History |
| POST | `/infrastructure/gateway/route` | Route Through Gateway |
| GET | `/infrastructure/gateway/stats` | Get Gateway Stats |
| POST | `/infrastructure/initialize` | Initialize Infrastructure |
| POST | `/infrastructure/load-balancer/set-weight/{service_id}` | Set Service Weight |
| GET | `/infrastructure/load-balancer/stats` | Get Load Balancer Stats |
| POST | `/infrastructure/mesh/call` | Call Through Mesh |
| GET | `/infrastructure/mesh/health` | Get Mesh Health |
| GET | `/infrastructure/mesh/stats` | Get Mesh Stats |
| GET | `/infrastructure/mesh/topology` | Get Mesh Topology |
| GET | `/infrastructure/overview` | Get Infrastructure Overview |

## Learning Visibility

**Endpoints:** 12

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/learning/activity/record` | Record Learning Activity |
| GET | `/api/learning/activity/{activity_id}` | Get Activity |
| PUT | `/api/learning/activity/{activity_id}/status` | Update Activity Status |
| POST | `/api/learning/activity/{activity_id}/validate` | Validate Activity |
| GET | `/api/learning/analytics` | Get Learning Analytics |
| GET | `/api/learning/dashboard/realtime` | Get Realtime Dashboard |
| GET | `/api/learning/health` | Learning Health Check |
| GET | `/api/learning/report/validation` | Get Validation Report |
| POST | `/api/learning/session/end` | End Learning Session |
| POST | `/api/learning/session/start` | Start Learning Session |
| GET | `/api/learning/session/{session_id}` | Get Session |
| GET | `/api/learning/sources/supported` | Get Supported Sources |

## Metrics

**Endpoints:** 1

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/metrics/summary` | Get Metrics Summary |

## Mission Control

**Endpoints:** 19

| Method | Path | Summary |
|--------|------|----------|
| GET | `/mission-control/autonomous/missions` | List Autonomous Missions |
| POST | `/mission-control/autonomous/missions` | Create Autonomous Mission |
| GET | `/mission-control/autonomous/missions/{mission_id}` | Get Autonomous Mission |
| POST | `/mission-control/autonomous/missions/{mission_id}/consensus` | Reach Mission Consensus |
| POST | `/mission-control/autonomous/missions/{mission_id}/feedback` | Add Mission Feedback |
| POST | `/mission-control/capa` | Create Capa Ticket |
| GET | `/mission-control/capa` | List Capa Tickets |
| GET | `/mission-control/metrics` | Get Metrics Catalog |
| GET | `/mission-control/missions` | List Missions |
| POST | `/mission-control/missions/create-from-manifest` | Create Mission From Manifest |
| GET | `/mission-control/missions/dynamic/{mission_id}` | Get Dynamic Mission Plan |
| POST | `/mission-control/missions/legacy` | Create Legacy Mission |
| GET | `/mission-control/missions/{mission_id}` | Get Mission |
| POST | `/mission-control/missions/{mission_id}/execute` | Execute Mission |
| GET | `/mission-control/queue/next` | Get Next Mission For Agent |
| GET | `/mission-control/status` | Get Mission Control Status |
| GET | `/mission-control/subsystems` | Get Subsystem Health |
| GET | `/mission-control/trust-scores` | Get Trust Scores |
| GET | `/mission-control/trust-scores/{agent_id}` | Get Agent Trust Score |

## Operator Dashboard

**Endpoints:** 9

| Method | Path | Summary |
|--------|------|----------|
| GET | `/operator/boot/progress` | Get Boot Progress |
| GET | `/operator/dashboard` | Get Dashboard |
| GET | `/operator/fixes` | Get Active Fixes |
| GET | `/operator/kernels` | Get Kernel Health |
| GET | `/operator/rate-limits` | Get Rate Limits |
| POST | `/operator/rollback` | Trigger Rollback |
| GET | `/operator/sbom` | Get Sbom |
| GET | `/operator/snapshots` | Get Snapshots |
| GET | `/operator/vulnerabilities` | Get Vulnerabilities |

## Phase 7: SaaS Readiness

**Endpoints:** 52

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/phase7/access-logs` | Get Access Logs |
| POST | `/api/phase7/backups` | Create Backup |
| GET | `/api/phase7/backups` | List Backups |
| GET | `/api/phase7/backups/stats` | Get Backup Stats |
| GET | `/api/phase7/backups/{backup_id}` | Get Backup |
| DELETE | `/api/phase7/backups/{backup_id}` | Delete Backup |
| POST | `/api/phase7/chaos-tests` | Create Chaos Test |
| GET | `/api/phase7/chaos-tests` | List Chaos Tests |
| GET | `/api/phase7/chaos-tests/stats` | Get Chaos Stats |
| GET | `/api/phase7/chaos-tests/{test_id}` | Get Chaos Test |
| POST | `/api/phase7/chaos-tests/{test_id}/execute` | Execute Chaos Test |
| POST | `/api/phase7/check-permission` | Check Permission |
| POST | `/api/phase7/instances` | Create Instance |
| GET | `/api/phase7/instances` | List Instances |
| GET | `/api/phase7/instances/{instance_id}` | Get Instance |
| PUT | `/api/phase7/instances/{instance_id}` | Update Instance |
| DELETE | `/api/phase7/instances/{instance_id}` | Delete Instance |
| POST | `/api/phase7/instances/{instance_id}/activate` | Activate Instance |
| GET | `/api/phase7/instances/{instance_id}/metrics` | Get Instance Metrics |
| POST | `/api/phase7/instances/{instance_id}/suspend` | Suspend Instance |
| POST | `/api/phase7/invoices` | Create Invoice |
| GET | `/api/phase7/invoices` | List Invoices |
| GET | `/api/phase7/invoices/{invoice_id}` | Get Invoice |
| POST | `/api/phase7/invoices/{invoice_id}/pay` | Pay Invoice |
| GET | `/api/phase7/permissions` | List Permissions |
| POST | `/api/phase7/restore` | Create Restore Job |
| GET | `/api/phase7/restore` | List Restore Jobs |
| GET | `/api/phase7/restore/{restore_id}` | Get Restore Job |
| POST | `/api/phase7/restore/{restore_id}/cancel` | Cancel Restore Job |
| POST | `/api/phase7/role-assignments` | Assign Role |
| POST | `/api/phase7/roles` | Create Role |
| GET | `/api/phase7/roles` | List Roles |
| GET | `/api/phase7/roles/{role_id}` | Get Role |
| PUT | `/api/phase7/roles/{role_id}` | Update Role |
| DELETE | `/api/phase7/roles/{role_id}` | Delete Role |
| GET | `/api/phase7/runbooks` | List Runbooks |
| GET | `/api/phase7/runbooks/{runbook_id}` | Get Runbook |
| GET | `/api/phase7/subscriptions` | List Subscriptions |
| POST | `/api/phase7/subscriptions` | Create Subscription |
| GET | `/api/phase7/subscriptions/tenant/{tenant_id}` | Get Subscription By Tenant |
| GET | `/api/phase7/subscriptions/{subscription_id}` | Get Subscription |
| PUT | `/api/phase7/subscriptions/{subscription_id}` | Update Subscription |
| POST | `/api/phase7/subscriptions/{subscription_id}/cancel` | Cancel Subscription |
| GET | `/api/phase7/summary` | Get Phase7 Summary |
| GET | `/api/phase7/templates` | List Templates |
| GET | `/api/phase7/templates/{template_id}` | Get Template |
| POST | `/api/phase7/usage` | Record Usage |
| GET | `/api/phase7/usage/{tenant_id}/summary` | Get Usage Summary |
| POST | `/api/phase7/users` | Create User |
| GET | `/api/phase7/users/{user_id}` | Get User |
| GET | `/api/phase7/users/{user_id}/permissions` | Get User Permissions |
| GET | `/api/phase7/users/{user_id}/roles` | Get User Roles |

## Phase 8: E2E Testing & Production Readiness

**Endpoints:** 14

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/phase8/health/component/{component}` | Get Component Health |
| GET | `/api/phase8/health/history` | Get Health History |
| GET | `/api/phase8/health/metrics` | Get Health Metrics |
| GET | `/api/phase8/health/system` | Get System Health |
| GET | `/api/phase8/integrations/map` | Get Integration Map |
| GET | `/api/phase8/integrations/validate` | Validate All Integrations |
| GET | `/api/phase8/integrations/{integration_id}` | Validate Integration |
| GET | `/api/phase8/readiness/checklist` | Get Readiness Checklist |
| GET | `/api/phase8/readiness/checks` | Get Readiness Checks |
| GET | `/api/phase8/readiness/summary` | Get Readiness Summary |
| GET | `/api/phase8/status` | Get Phase8 Status |
| GET | `/api/phase8/summary` | Get Phase8 Summary |
| GET | `/api/phase8/tests/results` | Get Test Results |
| GET | `/api/phase8/tests/status` | Get Test Status |

## Port Manager

**Endpoints:** 10

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/ports/allocations` | Get Allocations |
| GET | `/api/ports/allocations/{port}` | Get Allocation |
| POST | `/api/ports/cleanup-stale` | Cleanup Stale Ports |
| POST | `/api/ports/health-check` | Trigger Health Check |
| GET | `/api/ports/network/health` | Get Network Health |
| GET | `/api/ports/network/port-exhaustion` | Check Port Exhaustion |
| GET | `/api/ports/network/ssl-readiness` | Check Ssl Readiness |
| GET | `/api/ports/network/stats` | Get Network Stats |
| GET | `/api/ports/status` | Get Port Status |
| GET | `/api/ports/watchdog/status` | Get Watchdog Status |

## Remote Access & Zero Trust

**Endpoints:** 33

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/remote-access/approval/decide` | Human Approval Decision |
| GET | `/api/remote-access/approval/pending` | Get Pending Approvals |
| POST | `/api/remote-access/credentials/access` | Access Site Credential |
| GET | `/api/remote-access/credentials/sites` | List Credential Sites |
| POST | `/api/remote-access/credentials/store` | Store Site Credential |
| GET | `/api/remote-access/dashboard/realtime` | Realtime Activity Dashboard |
| POST | `/api/remote-access/devices/allowlist` | Allowlist Device |
| POST | `/api/remote-access/devices/register` | Register Device |
| POST | `/api/remote-access/execute` | Execute Command |
| POST | `/api/remote-access/integrations/journalclub/autonomous-download` | Autonomous Journalclub Download |
| POST | `/api/remote-access/integrations/journalclub/login-direct` | Journalclub Direct Login |
| POST | `/api/remote-access/integrations/journalclub/setup` | Setup Journalclub |
| GET | `/api/remote-access/integrations/journalclub/status` | Get Journalclub Status |
| POST | `/api/remote-access/learning/execute-autonomous` | Execute Autonomous Learning Task |
| GET | `/api/remote-access/learning/models` | Get Available Learning Models |
| GET | `/api/remote-access/learning/next-topic` | Get Next Learning Topic |
| POST | `/api/remote-access/learning/record-project` | Record Project Completion |
| POST | `/api/remote-access/learning/start-domain` | Start Learning Domain |
| GET | `/api/remote-access/learning/status` | Get Learning Status |
| POST | `/api/remote-access/rag/ask` | Ask With Rag |
| POST | `/api/remote-access/rag/ingest-text` | Ingest Text To Rag |
| POST | `/api/remote-access/rag/query` | Query Knowledge Base |
| GET | `/api/remote-access/rag/stats` | Get Rag Stats |
| GET | `/api/remote-access/recordings` | Get Recordings |
| POST | `/api/remote-access/research/batch-process` | Batch Process Papers |
| POST | `/api/remote-access/research/process-paper` | Process Research Paper |
| POST | `/api/remote-access/roles/assign` | Assign Role |
| POST | `/api/remote-access/session/create` | Create Session |
| POST | `/api/remote-access/session/start` | Start Session |
| POST | `/api/remote-access/session/stop` | Stop Session |
| GET | `/api/remote-access/session/{session_id}` | Get Session Details |
| GET | `/api/remote-access/sessions/active` | Get Active Sessions |
| POST | `/api/remote-access/system/autonomous-upgrade` | Autonomous System Upgrade |

## SaaS Builder

**Endpoints:** 4

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/saas-builder/curriculum` | Get Saas Curriculum |
| GET | `/api/saas-builder/metrics` | Get Builder Metrics |
| POST | `/api/saas-builder/recommend-stack` | Recommend Stack |
| POST | `/api/saas-builder/start-project` | Start Project |

## Secure Vault

**Endpoints:** 6

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/vault/health` | Vault Health |
| POST | `/api/vault/secrets` | Create Secret |
| GET | `/api/vault/secrets` | List Secrets |
| GET | `/api/vault/secrets/{name}` | Get Secret |
| DELETE | `/api/vault/secrets/{name}` | Revoke Secret |
| GET | `/api/vault/status` | Vault Status |

## Storage Tracking

**Endpoints:** 5

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/storage/capacity-check` | Check Capacity |
| GET | `/api/storage/learning-data` | Get Learning Data Breakdown |
| GET | `/api/storage/metrics` | Get Storage Metrics |
| POST | `/api/storage/optimize` | Optimize Storage |
| GET | `/api/storage/report` | Get Storage Report |

## Uncategorized

**Endpoints:** 34

| Method | Path | Summary |
|--------|------|----------|
| GET | `/` | Root |
| GET | `/api/analytics/domain-trends` | Get Domain Analytics Trends |
| GET | `/api/analytics/effectiveness-trend` | Get Effectiveness Trend Chart |
| GET | `/api/analytics/missions-per-domain` | Get Missions Per Domain Chart |
| GET | `/api/analytics/mttr-trend` | Get Mttr Trend Chart |
| GET | `/api/analytics/stats` | Get Analytics Stats |
| POST | `/api/chat` | Chat |
| POST | `/api/context/dismiss` | Dismiss Context |
| GET | `/api/context/suggestions` | Get Context Suggestions |
| GET | `/api/learning/status` | Learning Status |
| GET | `/api/missions/outcome/stats` | Get Mission Outcome Stats |
| POST | `/api/missions/proactive/narrative` | Create Mission Narrative |
| GET | `/api/missions/proactive/stats` | Get Proactive Mission Stats |
| POST | `/api/models/approve` | Approve Model Output |
| GET | `/api/models/available` | Models Available |
| GET | `/api/models/capabilities` | Models Capabilities |
| GET | `/api/models/performance` | Models Performance |
| POST | `/api/remote-access/capture` | Remote Capture Screenshot |
| GET | `/api/self/assessment` | Get Self Assessment |
| GET | `/api/self/domain/{domain_id}/performance` | Get Domain Performance |
| POST | `/api/self/improve` | Execute Improvement |
| GET | `/api/self/stats` | Get Self Optimization Stats |
| POST | `/api/speech/process` | Process Voice |
| POST | `/api/speech/session/end` | End Voice Session |
| POST | `/api/speech/session/start` | Start Voice Session |
| GET | `/api/speech/session/{session_id}/status` | Get Session Status |
| GET | `/api/speech/tts/sample.mp3` | Sample Tts Audio |
| POST | `/api/status-brief/generate` | Generate Status Brief Now |
| GET | `/api/status-brief/latest` | Get Latest Status Brief |
| GET | `/api/status-brief/stats` | Get Status Brief Stats |
| POST | `/api/vision/analyze` | Analyze Image |
| GET | `/api/vision/observations` | Get Visual Observations |
| POST | `/api/vision/video` | Analyze Video |
| GET | `/health` | Health Check |

## Vector Operations

**Endpoints:** 3

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/vectors/embed` | Create Embedding |
| GET | `/api/vectors/health` | Vector Health |
| GET | `/api/vectors/status` | Vector Status |

## agentic

**Endpoints:** 11

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/agentic/actions` | Get Actions |
| GET | `/api/agentic/events` | Get Events |
| GET | `/api/agentic/health` | Agentic Health |
| GET | `/api/agentic/reflections` | Get Reflections |
| GET | `/api/agentic/skills` | List Skills |
| POST | `/api/agentic/skills/execute` | Execute Skill |
| GET | `/api/agentic/skills/stats` | Get All Skill Stats |
| GET | `/api/agentic/skills/{skill_name}/stats` | Get Skill Stats |
| GET | `/api/agentic/strategy_updates` | Get Strategy Updates |
| GET | `/api/agentic/trace/{trace_id}` | Get Trace |
| GET | `/api/agentic/trust_scores` | Get Trust Scores |

## auth

**Endpoints:** 2

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/register` | Register |

## console

**Endpoints:** 2

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/console/health` | Console Health |
| GET | `/api/console/overview` | Get Console Overview |

## copilot

**Endpoints:** 7

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/copilot/actions/execute` | Execute Action |
| POST | `/api/copilot/chat/send` | Send Chat Message |
| GET | `/api/copilot/notifications` | Get Notifications |
| DELETE | `/api/copilot/notifications/{notification_id}` | Dismiss Notification |
| POST | `/api/copilot/notifications/{notification_id}/action` | Execute Notification Action |
| POST | `/api/copilot/upload` | Upload File |
| POST | `/api/copilot/voice/transcribe` | Transcribe Voice |

## copilot-pipeline

**Endpoints:** 4

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/copilot/pipeline/health` | Get Pipeline Health |
| POST | `/api/copilot/pipeline/rollback/{job_id}` | Rollback Pipeline |
| POST | `/api/copilot/pipeline/run` | Run Pipeline |
| GET | `/api/copilot/pipeline/status/{job_id}` | Get Pipeline Status |

## guardian

**Endpoints:** 8

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/guardian/failures/recent` | Get Recent Failures |
| GET | `/api/guardian/healer/stats` | Get Guardian Stats |
| GET | `/api/guardian/health` | Guardian Health |
| GET | `/api/guardian/mttr/by-issue-type` | Get Mttr By Issue Type |
| GET | `/api/guardian/mttr/by-playbook` | Get Mttr By Playbook |
| GET | `/api/guardian/osi/probe` | Probe Osi Layers |
| GET | `/api/guardian/playbooks` | List Playbooks |
| GET | `/api/guardian/stats` | Get Guardian Stats |

## ingestion

**Endpoints:** 5

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/ingest/artifacts` | List Artifacts |
| POST | `/api/ingest/file` | Ingest File |
| POST | `/api/ingest/text` | Ingest Text |
| POST | `/api/ingest/upload` | Ingest Upload |
| POST | `/api/ingest/url` | Ingest Url |

## learning

**Endpoints:** 4

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/learning/gaps` | Get Knowledge Gaps |
| POST | `/api/learning/gaps/detect` | Detect Gaps |
| POST | `/api/learning/record-query` | Record Query |
| GET | `/api/learning/stats` | Get Learning Stats |

## learning-control

**Endpoints:** 6

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/htm/tasks` | Get Htm Tasks |
| GET | `/api/learning/metrics` | Get Learning Metrics |
| GET | `/api/learning/outcomes` | Get Learning Outcomes |
| GET | `/api/learning/whitelist` | Get Whitelist |
| POST | `/api/learning/whitelist` | Add Whitelist Entry |
| DELETE | `/api/learning/whitelist/{entry_id}` | Remove Whitelist Entry |

## learning-hub

**Endpoints:** 3

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/learning/hub/health` | Get Learning Hub Health |
| GET | `/api/learning/hub/metrics` | Get Learning Metrics |
| GET | `/api/learning/hub/summary` | Get Learning Hub Summary |

## logs

**Endpoints:** 5

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/logs/domains` | Get Log Domains |
| GET | `/api/logs/governance` | Get Governance Logs |
| GET | `/api/logs/health` | Logs Health |
| GET | `/api/logs/levels` | Get Log Levels |
| GET | `/api/logs/recent` | Get Recent Logs |

## memory

**Endpoints:** 17

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/memory/artifacts` | List Artifacts |
| GET | `/api/memory/files` | Get File Tree |
| GET | `/api/memory/files/content` | Get File Content |
| POST | `/api/memory/files/content` | Save File Content |
| POST | `/api/memory/files/create` | Create File |
| DELETE | `/api/memory/files/delete` | Delete File |
| PATCH | `/api/memory/files/rename` | Rename File |
| POST | `/api/memory/files/upload` | Upload File |
| POST | `/api/memory/schemas/approve` | Approve Schema |
| GET | `/api/memory/schemas/pending` | Get Pending Schemas |
| GET | `/api/memory/status` | Get Memory Status |
| GET | `/api/memory/tables/list` | List Tables |
| GET | `/api/memory/tables/{table_name}/rows` | Get Table Rows |
| POST | `/api/memory/tables/{table_name}/rows` | Insert Table Row |
| PUT | `/api/memory/tables/{table_name}/rows/{row_id}` | Update Table Row |
| DELETE | `/api/memory/tables/{table_name}/rows/{row_id}` | Delete Table Row |
| GET | `/api/memory/tables/{table_name}/schema` | Get Table Schema |

## phase6

**Endpoints:** 20

| Method | Path | Summary |
|--------|------|----------|
| DELETE | `/api/phase6/api-keys/{key_id}` | Revoke Api Key |
| GET | `/api/phase6/health` | Health Check |
| GET | `/api/phase6/health/live` | Liveness Probe |
| GET | `/api/phase6/health/ready` | Readiness Probe |
| POST | `/api/phase6/jobs` | Submit Job |
| GET | `/api/phase6/jobs` | List Jobs |
| GET | `/api/phase6/jobs/stats` | Get Job Stats |
| GET | `/api/phase6/jobs/{job_id}` | Get Job |
| DELETE | `/api/phase6/jobs/{job_id}` | Cancel Job |
| GET | `/api/phase6/metrics/endpoints` | Get Endpoint Metrics |
| GET | `/api/phase6/metrics/golden-signals` | Get Golden Signals |
| GET | `/api/phase6/metrics/tenants/{tenant_id}` | Get Tenant Metrics |
| POST | `/api/phase6/tenants` | Create Tenant |
| GET | `/api/phase6/tenants` | List Tenants |
| GET | `/api/phase6/tenants/{tenant_id}` | Get Tenant |
| PUT | `/api/phase6/tenants/{tenant_id}` | Update Tenant |
| POST | `/api/phase6/tenants/{tenant_id}/activate` | Activate Tenant |
| POST | `/api/phase6/tenants/{tenant_id}/api-keys` | Create Api Key |
| GET | `/api/phase6/tenants/{tenant_id}/api-keys` | List Api Keys |
| POST | `/api/phase6/tenants/{tenant_id}/suspend` | Suspend Tenant |

## trust_framework

**Endpoints:** 20

| Method | Path | Summary |
|--------|------|----------|
| POST | `/api/trust/chaos-drills/run/{model_name}` | Run Chaos Drills |
| GET | `/api/trust/chaos-drills/stats` | Get Chaos Drill Stats |
| GET | `/api/trust/context/trustscore-gate/stats` | Get Trustscore Gate Stats |
| GET | `/api/trust/dashboard` | Get Trust Dashboard |
| POST | `/api/trust/data-hygiene/audit` | Audit Data |
| GET | `/api/trust/data-hygiene/stats` | Get Data Hygiene Stats |
| GET | `/api/trust/guardrails/status` | Get Guardrails Status |
| GET | `/api/trust/hallucinations/ledger` | Get Hallucination Ledger |
| GET | `/api/trust/hallucinations/model/{model_name}` | Get Model Hallucinations |
| GET | `/api/trust/hallucinations/retraining-priorities` | Get Retraining Priorities |
| GET | `/api/trust/models/health/all` | Get All Model Health |
| GET | `/api/trust/models/{model_name}/execution-window` | Get Execution Window |
| GET | `/api/trust/models/{model_name}/health` | Get Model Health |
| GET | `/api/trust/models/{model_name}/integrity` | Verify Model Integrity |
| POST | `/api/trust/models/{model_name}/rollback` | Rollback Model |
| GET | `/api/trust/models/{model_name}/snapshots` | Get Model Snapshots |
| POST | `/api/trust/models/{model_name}/stress-test` | Run Stress Test |
| GET | `/api/trust/status` | Get Trust Framework Status |
| GET | `/api/trust/uncertainty/stats` | Get Uncertainty Stats |
| GET | `/api/trust/verification/stats` | Get Verification Stats |

## world_model_hub

**Endpoints:** 24

| Method | Path | Summary |
|--------|------|----------|
| GET | `/api/world_model_hub/approvals` | List Approvals |
| POST | `/api/world_model_hub/approvals/action` | Handle Approval |
| GET | `/api/world_model_hub/artifacts` | List Artifacts |
| POST | `/api/world_model_hub/chat` | Chat With Grace |
| GET | `/api/world_model_hub/context` | Get Context |
| GET | `/api/world_model_hub/health` | Get Health |
| POST | `/api/world_model_hub/initialize` | Initialize |
| GET | `/api/world_model_hub/missions` | List Missions |
| POST | `/api/world_model_hub/multimodal/recording/start` | Start Recording |
| POST | `/api/world_model_hub/multimodal/recording/stop` | Stop Recording |
| POST | `/api/world_model_hub/multimodal/screen-share/start` | Start Screen Share |
| POST | `/api/world_model_hub/multimodal/screen-share/stop` | Stop Screen Share |
| POST | `/api/world_model_hub/multimodal/voice/toggle` | Toggle Voice |
| GET | `/api/world_model_hub/sandbox/consensus` | Get Consensus |
| GET | `/api/world_model_hub/sandbox/experiments` | List Experiments |
| GET | `/api/world_model_hub/sandbox/feedback` | Get Feedback Queue |
| GET | `/api/world_model_hub/sandbox/sovereignty` | Get Sovereignty Metrics |
| POST | `/api/world_model_hub/session/create` | Create Session |
| POST | `/api/world_model_hub/session/{session_id}/close` | Close Session |
| GET | `/api/world_model_hub/session/{session_id}/info` | Get Session Info |
| GET | `/api/world_model_hub/stats` | Get Orb Stats |
| POST | `/api/world_model_hub/tasks` | Create Task |
| GET | `/api/world_model_hub/tasks/{task_id}` | Get Task Status |
| GET | `/api/world_model_hub/trace/{trace_id}` | Get Trace |

