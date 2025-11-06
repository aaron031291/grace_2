"""
Observe-only self-heal scheduler
- Polls recent HealthSignals
- Runs deterministic triage
- Creates proposed PlaybookRun rows (no execution)
- Optionally drafts ApprovalRequest for high/critical or outside change windows

Feature-gated by settings.SELF_HEAL_OBSERVE_ONLY (must be True) or SELF_HEAL_EXECUTE (also acceptable).
Safe to import even if dependencies aren’t present; all imports are local within methods.
"""
from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


class ObserveOnlyScheduler:
    def __init__(self, poll_interval_s: int = 30):
        self._task: Optional[asyncio.Task] = None
        self._stopping = asyncio.Event()
        self._interval = poll_interval_s
        # In-memory suppression state (reset on process restart)
        # key: (service, diagnosis) → {"factor": int, "next_at": datetime}
        self._backoff: Dict[tuple[str, str], Dict[str, Any]] = {}
        # per-service timestamps of recent proposals for simple rate limiting
        self._rate: Dict[str, List[datetime]] = {}

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stopping.clear()
        self._task = asyncio.create_task(self._run_loop())
        
        # Subscribe to proactive predictions
        try:
            from ..trigger_mesh import trigger_mesh
            trigger_mesh.subscribe("self_heal.prediction", self._handle_prediction)
        except Exception:
            pass

    async def stop(self) -> None:
        try:
            self._stopping.set()
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
        finally:
            self._task = None

    # --- internals ---

    def _cleanup_rate(self, service: str, now: datetime) -> None:
        """Drop rate entries older than 1 hour for a service."""
        lst = self._rate.get(service, [])
        cutoff = now - timedelta(hours=1)
        self._rate[service] = [t for t in lst if t >= cutoff]

    def _should_propose(self, service: str, diagnosis: str, now: datetime) -> tuple[bool, str, int]:
        """Decide if we should create a proposal.
        Returns (ok, reason, backoff_ms). reason describes skip if ok=False.
        """
        # Rate limit: max 3/hour per service
        self._cleanup_rate(service, now)
        if len(self._rate.get(service, [])) >= 3:
            return (False, "rate_limited", 0)
        # Backoff per (service, diagnosis)
        key = (service, diagnosis)
        bo = self._backoff.get(key)
        if bo:
            next_at = bo.get("next_at")
            if isinstance(next_at, datetime) and next_at > now:
                delta_ms = int((next_at - now).total_seconds() * 1000)
                return (False, "backoff", delta_ms)
        return (True, "ok", 0)

    def _note_proposal(self, service: str, diagnosis: str, now: datetime) -> None:
        # Record rate event
        self._rate.setdefault(service, []).append(now)
        # Increase backoff factor with jitter
        key = (service, diagnosis)
        prev = self._backoff.get(key, {"factor": 0})
        factor = int(prev.get("factor", 0)) + 1
        # base sequence (minutes): 5, 10, 20, 40, 80; cap 120
        base_min = min(5 * (2 ** (factor - 1)), 120)
        # jitter ±20%
        jitter = 1.0 + (random.random() * 0.4 - 0.2)
        delay = timedelta(minutes=base_min * jitter)
        self._backoff[key] = {"factor": factor, "next_at": now + delay}

    def _is_outside_change_window(self, now: datetime) -> bool:
        """Default change window: weekdays 09:00–18:00 local time. Outside → True."""
        try:
            local = now.astimezone()
        except Exception:
            local = now
        wk = local.weekday()  # 0=Mon
        hr = local.hour
        in_window = (wk <= 4) and (9 <= hr < 18)
        return not in_window

    async def _run_loop(self) -> None:
        # Lazy imports to avoid import-time failures on optional modules
        from ..settings import settings
        if not (getattr(settings, "SELF_HEAL_OBSERVE_ONLY", True) or getattr(settings, "SELF_HEAL_EXECUTE", False)):
            return

        while not self._stopping.is_set():
            try:
                await self._tick()
            except Exception as e:  # pragma: no cover - defensive logging
                try:
                    print(f"[self-heal:scheduler] tick error: {e}")
                except Exception:
                    pass
            await asyncio.wait_for(asyncio.sleep(self._interval), timeout=self._interval + 1)

    async def _tick(self) -> None:
        from sqlalchemy import select
        from ..models import async_session
        from ..health_models import Service, HealthSignal
        from ..self_heal_models import PlaybookRun
        from ..health.triage import diagnose

        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(minutes=10)

        async with async_session() as session:
            # List services that have recent signals
            svc_rows = await session.execute(
                select(Service).order_by(Service.created_at.desc())
            )
            services = svc_rows.scalars().all()

            for svc in services:
                sig_rows = await session.execute(
                    select(HealthSignal)
                    .where(HealthSignal.service_id == svc.id)
                    .order_by(HealthSignal.created_at.desc())
                    .limit(200)
                )
                signals = [s for s in sig_rows.scalars().all() if (s.created_at or now) >= recent_cutoff]
                if not signals:
                    continue

                findings = diagnose(svc.id, signals)
                if not findings:
                    continue

                # Avoid spamming: if a recent proposed PlaybookRun for the same service and diagnosis exists, skip
                for fx in findings:
                    diag_code = fx.get("code")
                    # check for an existing recent proposed run with same diagnosis code in the last 10 minutes
                    existing = await session.execute(
                        select(PlaybookRun)
                        .where(PlaybookRun.service == svc.name)
                        .order_by(PlaybookRun.created_at.desc())
                        .limit(25)
                    )
                    skip = False
                    for run in existing.scalars().all():
                        try:
                            created_at = getattr(run, "created_at", None)
                            if created_at and created_at.tzinfo is None:
                                created_at = created_at.replace(tzinfo=timezone.utc)
                            if created_at and created_at >= recent_cutoff:
                                diag_json = json.loads(run.diagnosis) if run.diagnosis else {}
                                if diag_json.get("code") == diag_code and getattr(run, "status", "") == "proposed":
                                    skip = True
                                    break
                        except Exception:
                            pass

                    if skip:
                        continue

                    # New: rate limit and backoff checks
                    ok, reason, backoff_ms = self._should_propose(svc.name, diag_code, now)
                    if not ok:
                        try:
                            print(f"[self-heal:scheduler] skip {svc.name}/{diag_code}: {reason} backoff_ms={backoff_ms}")
                        except Exception:
                            pass
                        continue

                    # Draft a proposed PlaybookRun; selection/refinement remains to the human or executor
                    run = PlaybookRun(
                        playbook_id=None,
                        service=svc.name,
                        status="proposed",
                        requested_by="scheduler",
                        parameters=None,
                        diagnosis=json.dumps({
                            "code": fx.get("code"),
                            "title": fx.get("title"),
                            "likelihood": fx.get("likelihood"),
                            "impact": fx.get("impact"),
                            "suggested_playbooks": fx.get("suggested_playbooks", []),
                            "reasons": fx.get("reasons", []),
                        }),
                    )
                    session.add(run)
                    # Also record a learning_log entry for proposal (phase 2 of learning)
                    try:
                        from ..self_heal_models import LearningLog
                        session.add(LearningLog(
                            service=svc.name,
                            signal_ref=None,
                            diagnosis=json.dumps({
                                "code": fx.get("code"),
                                "title": fx.get("title"),
                                "likelihood": fx.get("likelihood"),
                                "impact": fx.get("impact")
                            }),
                            action=json.dumps({"status": "proposed"}),
                            outcome=None,
                        ))
                    except Exception:
                        pass

                    # Note proposal for future backoff/rate calculations
                    self._note_proposal(svc.name, diag_code, now)

                    # Autonomous approval with trust core integration
                    impact = str(fx.get("impact") or "").lower()
                    outside_window = self._is_outside_change_window(now)
                    blast_radius = await self._estimate_blast_radius(svc.name)
                    confidence = float(fx.get("likelihood") or 0.0)
                    
                    # Check if we can auto-approve (low risk with trust core)
                    ok_to_auto = (
                        impact in {"low", "medium"} and 
                        blast_radius <= 2 and 
                        confidence >= 0.7 and 
                        not outside_window
                    )
                    
                    if ok_to_auto:
                        try:
                            from ..governance import governance_engine
                            decision = await governance_engine.check(
                                actor="self_heal",
                                action="self_heal_execute",
                                resource=svc.name,
                                payload={
                                    "diag_code": diag_code,
                                    "impact": impact,
                                    "confidence": confidence,
                                    "blast_radius": blast_radius
                                }
                            )
                            
                            if decision["decision"] == "allow":
                                run.status = "approved"
                                await self._create_approval_request(
                                    session, 
                                    run, 
                                    reason=f"trust_core:auto-approved impact={impact} br={blast_radius} conf={confidence:.2f}"
                                )
                                try:
                                    from ..self_heal_models import LearningLog
                                    session.add(LearningLog(
                                        service=svc.name,
                                        signal_ref=None,
                                        diagnosis=run.diagnosis,
                                        action=json.dumps({"status": "auto_approved", "blast_radius": blast_radius}),
                                        outcome=None
                                    ))
                                except Exception:
                                    pass
                        except Exception:
                            # If trust core check fails, fall back to manual approval
                            pass
                    
                    # Create approval draft for high/critical impacts and outside change window
                    if run.status == "proposed":  # Not auto-approved
                        if impact in {"high", "critical"} or (impact == "medium" and outside_window):
                            # Avoid duplicate approval drafts for the same run
                            try:
                                from ..governance_models import ApprovalRequest
                                existing_req = await session.execute(
                                    select(ApprovalRequest).where(ApprovalRequest.event_id == run.id)
                                )
                                if existing_req.scalars().first() is None:
                                    await self._create_approval_request(session, run, reason=f"Auto-draft (impact={impact}, outside_window={outside_window}, br={blast_radius}) service={svc.name} diagnosis={diag_code}")
                            except Exception:
                                await self._create_approval_request(session, run, reason=f"Auto-draft (impact={impact}, outside_window={outside_window}, br={blast_radius}) service={svc.name} diagnosis={diag_code}")

                await session.commit()

    async def _create_approval_request(self, session, run_obj, reason: str) -> None:
        try:
            from ..governance_models import ApprovalRequest
        except Exception:
            return
        req = ApprovalRequest(
            event_id=getattr(run_obj, "id", 0) or 0,
            status="pending" if "auto-approved" not in reason else "approved",
            requested_by="scheduler",
            reason=reason,
        )
        session.add(req)
    
    async def _estimate_blast_radius(self, service_name: str) -> int:
        """Estimate blast radius by checking dependency count in health graph"""
        try:
            from ..agentic_spine import agentic_spine
            deps = await agentic_spine.health_graph.get_dependents(service_name)
            return min(len(deps or []), 10)
        except Exception:
            # If health graph unavailable, assume conservative blast radius
            return 5
    
    async def _handle_prediction(self, event):
        """Handle proactive predictions from predictor"""
        try:
            from sqlalchemy import select
            from ..models import async_session
            from ..health_models import Service
            from ..self_heal_models import PlaybookRun
            
            now = datetime.now(timezone.utc)
            service_name = event.resource
            fx = event.payload
            diag_code = fx.get("code", "prediction")
            
            # Rate limit check
            ok, reason, _ = self._should_propose(service_name, diag_code, now)
            if not ok:
                return
            
            async with async_session() as session:
                svc = await session.execute(select(Service).where(Service.name == service_name))
                service = svc.scalar_one_or_none()
                if not service:
                    return
                
                # Create proactive playbook run
                run = PlaybookRun(
                    playbook_id=None,
                    service=service_name,
                    status="proposed",
                    requested_by="predictor",
                    parameters=None,
                    diagnosis=json.dumps({
                        "code": fx.get("code"),
                        "title": fx.get("title"),
                        "likelihood": fx.get("likelihood"),
                        "impact": fx.get("impact"),
                        "suggested_playbooks": fx.get("suggested_playbooks", []),
                        "reasons": fx.get("reasons", []),
                        "proactive": True
                    }),
                )
                session.add(run)
                await session.flush()
                
                # Try autonomous approval for proactive low-risk actions
                impact = str(fx.get("impact") or "").lower()
                blast_radius = await self._estimate_blast_radius(service_name)
                confidence = float(fx.get("likelihood") or 0.0)
                
                ok_to_auto = (
                    impact in {"low", "medium"} and 
                    blast_radius <= 2 and 
                    confidence >= 0.8 and  # Higher threshold for proactive
                    not self._is_outside_change_window(now)
                )
                
                if ok_to_auto:
                    try:
                        from ..governance import governance_engine
                        decision = await governance_engine.check(
                            actor="self_heal",
                            action="self_heal_execute_proactive",
                            resource=service_name,
                            payload={
                                "diag_code": diag_code,
                                "impact": impact,
                                "confidence": confidence,
                                "blast_radius": blast_radius,
                                "proactive": True
                            }
                        )
                        
                        if decision["decision"] == "allow":
                            run.status = "approved"
                            await self._create_approval_request(
                                session,
                                run,
                                reason=f"trust_core:proactive-auto-approved impact={impact} br={blast_radius} conf={confidence:.2f}"
                            )
                    except Exception:
                        pass
                
                self._note_proposal(service_name, diag_code, now)
                await session.commit()
                
                print(f"  🔮 Proactive playbook proposed for {service_name}: {fx.get('title')} (status={run.status})")
        
        except Exception as e:
            try:
                print(f"[self-heal:scheduler] prediction handler error: {e}")
            except Exception:
                pass


# Singleton instance for app wiring
scheduler = ObserveOnlyScheduler(poll_interval_s=30)
