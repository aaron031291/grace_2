"""
Self-heal execution runner (feature-gated)
- Picks approved PlaybookRun items and executes their steps deterministically
- Runs verification checks; on failure, performs rollback and escalates

Safety:
- Only runs when settings.SELF_HEAL_EXECUTE is True
- Requires PlaybookRun.status == 'approved' to begin execution
- Governance/approvals assumed to have occurred upstream

This runner now includes real (safe) verification hooks and action adapters.
External side effects are avoided or simulated; hooks have timeouts and
clear pass/fail semantics. Metrics checks leverage recent HealthSignal rows.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List


class ExecutionRunner:
    def __init__(self, poll_interval_s: int = 15):
        self._task: Optional[asyncio.Task] = None
        self._stopping = asyncio.Event()
        self._interval = poll_interval_s
        # simple in-memory adapters state (simulated toggles/logging TTLs)
        self._flags: Dict[str, Dict[str, Any]] = {}
        self._log_level_ttl: Optional[datetime] = None
        self._last_htm_check: Optional[datetime] = None
        
        # Real executors
        from .real_executors import real_executors
        self.executors = real_executors

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stopping.clear()
        self._task = asyncio.create_task(self._run_loop())

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

    async def _run_loop(self) -> None:
        from ..settings import settings
        if not getattr(settings, "SELF_HEAL_EXECUTE", False):
            return
            
        boot_time = datetime.now(timezone.utc)
        
        while not self._stopping.is_set():
            try:
                await self._tick()
                
                # Health Monitoring (RAG + HTM)
                # We piggyback on the runner loop to ensure consistent monitoring
                base_url = getattr(settings, "SELF_HEAL_BASE_URL", "http://localhost:8000")
                await self._check_rag_health(base_url)
                await self._check_htm_anomalies()
                
            except Exception as e:  # pragma: no cover
                try:
                    print(f"[self-heal:runner] tick error: {e}")
                except Exception:
                    pass
            
            # Adaptive Polling: Fast (15s) during boot (first 5m), Slow (3m) after
            uptime_sec = (datetime.now(timezone.utc) - boot_time).total_seconds()
            current_interval = 15 if uptime_sec < 300 else 180
            
            await asyncio.wait_for(asyncio.sleep(current_interval), timeout=current_interval + 1)

    # ---- Verification hooks ----
    async def _verify_http_health(self, base_url: str, path: str, expect: str = "ok", timeout_s: int = 20, retries: int = 2, backoff_ms: int = 250) -> bool:
        try:
            import httpx
        except Exception:
            # If httpx missing, cannot verify; be conservative
            return False
        url = base_url.rstrip("/") + path
        attempt = 0
        last_err: Optional[str] = None
        while attempt <= retries:
            try:
                async with httpx.AsyncClient(timeout=timeout_s) as client:
                    resp = await client.get(url)
                    if resp.status_code // 100 == 2:
                        try:
                            data = resp.json()
                            if str(data.get("status", "")).lower() == expect.lower():
                                return True
                        except Exception:
                            # fallback to substring match
                            if expect.lower() in (resp.text or "").lower():
                                return True
                    last_err = f"status={resp.status_code} body={resp.text[:200]}"
            except Exception as ex:  # network/timeout
                last_err = str(ex)
            attempt += 1
            await asyncio.sleep(backoff_ms / 1000.0)
        try:
            print(f"[verify:http_health] FAIL url={url} last_err={last_err}")
        except Exception:
            pass
        return False

    async def _verify_metrics_threshold(self, session, service_name: str, metric: str, gte: float | None = None, lte: float | None = None, window_min: int = 5) -> bool:
        """Use recent HealthSignal rows as a proxy for metrics checks."""
        from sqlalchemy import select
        from ..health_models import Service, HealthSignal
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=window_min)
        svc_res = await session.execute(select(Service).where(Service.name == service_name))
        svc = svc_res.scalar_one_or_none()
        if not svc:
            return False
        res = await session.execute(
            select(HealthSignal).where(
                HealthSignal.service_id == svc.id
            ).order_by(HealthSignal.created_at.desc()).limit(200)
        )
        vals: List[float] = []
        for s in res.scalars().all():
            ts = s.created_at or now
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff and (s.metric_key or "") == metric and s.value is not None:
                try:
                    vals.append(float(s.value))
                except Exception:
                    pass
        if not vals:
            return False
        v = sum(vals) / len(vals)
        if gte is not None and v < float(gte):
            return False
        if lte is not None and v > float(lte):
            return False
        return True

    async def _verify_metrics_trend(self, session, service_name: str, metric: str, direction: str = "down", window_min: int = 5) -> bool:
        from sqlalchemy import select
        from ..health_models import Service, HealthSignal
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=window_min)
        svc_res = await session.execute(select(Service).where(Service.name == service_name))
        svc = svc_res.scalar_one_or_none()
        if not svc:
            return False
        res = await session.execute(
            select(HealthSignal).where(
                HealthSignal.service_id == svc.id
            ).order_by(HealthSignal.created_at.asc()).limit(500)
        )
        series: List[tuple[datetime, float]] = []
        for s in res.scalars().all():
            ts = s.created_at or now
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff and (s.metric_key or "") == metric and s.value is not None:
                try:
                    series.append((ts, float(s.value)))
                except Exception:
                    pass
        if len(series) < 2:
            return False
        # simple slope: last - first
        slope = series[-1][1] - series[0][1]
        if direction == "down":
            return slope < 0
        else:
            return slope > 0

    # ---- Action adapters (delegated to RealExecutors) ----
    async def _act_restart_service(self, service: str, graceful: bool = True) -> str:
        res = await self.executors.restart_service({"service": service, "graceful": graceful})
        return f"restart_service: {res.get('note', str(res))}"

    async def _act_toggle_flag(self, flag: str, state: bool) -> str:
        res = await self.executors.toggle_flag({"flag": flag, "state": state})
        return f"toggle_flag: {res.get('note', str(res))}"

    async def _act_scale_instances(self, min_delta: int) -> str:
        res = await self.executors.scale_instances({"min_delta": min_delta})
        return f"scale_instances: {res.get('note', str(res))}"

    async def _act_warm_cache(self) -> str:
        res = await self.executors.warm_cache({"cache_type": "application"})
        return f"warm_cache: {res.get('note', str(res))}"

    async def _act_set_logging_level(self, level: str = "DEBUG", ttl_min: int = 15) -> str:
        res = await self.executors.set_logging_level({"level": level, "ttl_min": ttl_min})
        return f"set_logging_level: {res.get('note', str(res))}"

    async def _act_flush_circuit_breakers(self) -> str:
        res = await self.executors.flush_circuit_breakers({})
        return f"flush_circuit_breakers: {res.get('note', str(res))}"

    async def _act_noop(self) -> str:
        return "noop"

    def _action_dispatch(self, action: str):
        return {
            "restart_service": self._act_restart_service,
            "toggle_flag": self._act_toggle_flag,
            "scale_instances": self._act_scale_instances,
            "warm_cache": self._act_warm_cache,
            "set_logging_level": self._act_set_logging_level,
            "flush_circuit_breakers": self._act_flush_circuit_breakers,
            "noop": self._act_noop,
            "noop_or_safe_action": self._act_noop,
        }.get(action, self._act_noop)

    async def _run_verifications_for_step(self, session, run, step_obj, base_url: str) -> bool:
        """Run step-level verifications from VerificationCheck if available.
        Falls back to a simple /health check when none present."""
        from sqlalchemy import select
        from ..self_heal_models import VerificationCheck

        checks = []
        if getattr(run, "playbook_id", None) and getattr(step_obj, "id", None):
            res = await session.execute(
                select(VerificationCheck).where(
                    VerificationCheck.playbook_id == run.playbook_id,
                    VerificationCheck.step_id == step_obj.id,
                    VerificationCheck.scope == "post_step",
                )
            )
            checks = res.scalars().all()

        if not checks:
            # default: http health verify
            ok = await self._verify_http_health(base_url, "/health", expect="ok", timeout_s=20, retries=2)
            return ok

        # Execute all checks, require all to pass
        for chk in checks:
            try:
                cfg = json.loads(chk.config) if chk.config else {}
            except Exception:
                cfg = {}
            ctype = (chk.check_type or "").lower()
            if ctype in {"health_endpoint", "http_health"}:
                path = cfg.get("path", "/health")
                expect = cfg.get("expect", "ok")
                timeout_s = int(cfg.get("timeout_s", chk.timeout_s or 20))
                retries = int(cfg.get("retries", 2))
                backoff_ms = int(cfg.get("backoff_ms", 250))
                ok = await self._verify_http_health(base_url, path, expect, timeout_s, retries, backoff_ms)
                if not ok:
                    return False
            elif ctype == "metric" or ctype == "metrics_threshold":
                metric = cfg.get("metric")
                gte = cfg.get("gte")
                lte = cfg.get("lte")
                window_min = int(cfg.get("window_min", 5))
                ok = await self._verify_metrics_threshold(session, run.service, metric, gte, lte, window_min)
                if not ok:
                    return False
            elif ctype == "metrics_trend":
                metric = cfg.get("metric")
                direction = cfg.get("direction", "down")
                window_min = int(cfg.get("window_min", 5))
                ok = await self._verify_metrics_trend(session, run.service, metric, direction, window_min)
                if not ok:
                    return False
            elif ctype == "cli_smoke":
                # Optional CLI smoke verification (disabled by default for safety)
                try:
                    from ..settings import settings as _s
                    if not getattr(_s, "ENABLE_CLI_VERIFY", False):
                        return False
                except Exception:
                    return False
                # Run a short, safe CLI smoke test
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "py", "scripts\\cli_test.py", "smoke",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    try:
                        outs, errs = await asyncio.wait_for(proc.communicate(), timeout=float(cfg.get("timeout_s", 20)))
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                        return False
                    out_text = (outs or b"").decode("utf-8", errors="ignore")
                    err_text = (errs or b"").decode("utf-8", errors="ignore")
                    # consider success if stdout contains OK and process exited 0
                    return (proc.returncode == 0) and ("OK" in out_text or "ok" in out_text.lower())
                except Exception:
                    return False
            else:
                # Unknown check type -> fail closed
                return False
        return True

    async def _check_rag_health(self, base_url: str) -> None:
        """Check RAG service health"""
        try:
            import httpx
            from backend.core.healing_orchestrator import healing_orchestrator
            
            url = f"{base_url.rstrip('/')}/world-model/stats"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # Trigger if marked degraded or high error rate
                    if data.get("status") == "degraded" or data.get("error_count", 0) > 50:
                        await healing_orchestrator.handle_issue(
                            "rag_health_issue", 
                            f"RAG reported degraded status: {data.get('status')} (errors: {data.get('error_count')})", 
                            json.dumps(data)
                        )
        except Exception:
            pass

    async def _check_htm_anomalies(self) -> None:
        """Check for recent HTM anomalies"""
        try:
            # Attempt to import HTM detector (Chunk 7)
            # If not booted yet, this will fail gracefully
            from backend.trust_framework.htm_anomaly_detector import htm_detector_pool
            
            anomalies = htm_detector_pool.get_recent_anomalies(
                minutes=1,
                since=self._last_htm_check
            )
            
            # Update last check time
            self._last_htm_check = datetime.utcnow()
            
            if anomalies:
                from backend.core.healing_orchestrator import healing_orchestrator
                for anomaly in anomalies:
                    await healing_orchestrator.handle_issue(
                        "htm_anomaly",
                        f"HTM Anomaly detected: {anomaly.get('description')}",
                        json.dumps(anomaly)
                    )
        except ImportError:
            pass # HTM not loaded yet
        except Exception:
            pass

    async def _execute_action(self, action: str, params: Dict[str, Any]) -> str:
        # Central parameter validation (bounds/whitelist)
        try:
            if action == "scale_instances":
                min_delta = int(params.get("min_delta", 0))
                if min_delta < -3 or min_delta > 3:
                    raise ValueError("min_delta out of bounds [-3,3]")
            elif action == "set_logging_level":
                lvl = str(params.get("level", "")).upper() or "DEBUG"
                if lvl not in {"DEBUG", "INFO", "WARN", "ERROR"}:
                    raise ValueError("invalid logging level")
                ttl = int(params.get("ttl_min", 15))
                if ttl < 0:
                    raise ValueError("ttl_min must be >= 0")
            elif action == "toggle_flag":
                flag = params.get("flag")
                if not flag or not isinstance(flag, str):
                    raise ValueError("flag must be a non-empty string")
        except Exception as v_ex:
            raise v_ex
        fn = self._action_dispatch(action)
        return await fn(**params) if params else await fn()

    async def _tick(self) -> None:
        from sqlalchemy import select
        from ..models import async_session
        from ..self_heal_models import PlaybookRun, PlaybookStep as PBStep, PlaybookStepRun, VerificationCheck
        from ..governance_models import AuditLog

        now = datetime.now(timezone.utc)
        async with async_session() as session:
            # Fetch a single approved run to process
            res = await session.execute(
                select(PlaybookRun).where(PlaybookRun.status == "approved").order_by(PlaybookRun.created_at.asc()).limit(1)
            )
            run = res.scalar_one_or_none()
            if not run:
                return

            # Governance/approval gate: if there is an approval_request_id, require it to be approved
            try:
                if getattr(run, "approval_request_id", None):
                    from ..governance_models import ApprovalRequest
                    appr = await session.get(ApprovalRequest, run.approval_request_id)
                    if appr and getattr(appr, "status", "").lower() != "approved":
                        # Defer execution until approval is granted
                        return
            except Exception:
                pass

            # Enforce change window: outside window requires approval for impact not low
            try:
                impact = ""
                if run.diagnosis:
                    try:
                        d = json.loads(run.diagnosis)
                        impact = str(d.get("impact") or "").lower()
                    except Exception:
                        impact = ""
                
                # Determine if outside window (weekdays 09:00–18:00 local)
                try:
                    local_now = now.astimezone()
                except Exception:
                    local_now = now
                wk = local_now.weekday()
                hr = local_now.hour
                outside_window = not ((wk <= 4) and (9 <= hr < 18))
                if outside_window and impact in {"medium", "high", "critical"}:
                    # If there is no explicit approved request, defer execution
                    try:
                        if not getattr(run, "approval_request_id", None):
                            return
                        else:
                            from ..governance_models import ApprovalRequest
                            appr2 = await session.get(ApprovalRequest, run.approval_request_id)
                            if not appr2 or getattr(appr2, "status", "").lower() != "approved":
                                return
                    except Exception:
                        return
            except Exception:
                pass

            # LearningLog entry on approved start
            try:
                from ..self_heal_models import LearningLog
                session.add(LearningLog(service=run.service, signal_ref=None, diagnosis=run.diagnosis, action=json.dumps({"run_id": run.id, "status": "approved"}), outcome=None))
            except Exception:
                pass

            # Mark running and audit
            run.status = "running"
            run.started_at = now
            try:
                session.add(AuditLog(actor="runner", action="playbook_run_start", resource=str(run.id), policy_checked="self_heal", result="started", details=f"service={run.service}"))
            except Exception:
                pass
            await session.commit()

            # Determine steps: load from DB if playbook_id is set; otherwise simulate one step
            steps: List[Any] = []
            if getattr(run, "playbook_id", None):
                st_res = await session.execute(
                    select(PBStep).where(PBStep.playbook_id == run.playbook_id).order_by(PBStep.step_order.asc())
                )
                steps = st_res.scalars().all()
            if not steps:
                # Simulated single step
                class _Sim:
                    id = None
                    action = "noop_or_safe_action"
                    args = None
                    timeout_s = 10
                    rollback_action = None
                    rollback_args = None
                steps = [_Sim()]

            from ..settings import settings as _settings
            base_url = getattr(_settings, "SELF_HEAL_BASE_URL", "http://localhost:8000")
            order = 1
            # Global per-run timeout watchdog
            try:
                from ..settings import settings as _settings_timeout
                run_deadline = now + timedelta(minutes=int(getattr(_settings_timeout, "SELF_HEAL_RUN_TIMEOUT_MIN", 10)))
            except Exception:
                run_deadline = now + timedelta(minutes=10)

            try:
                for step in steps:
                    # Check global timeout before each step
                    if datetime.now(timezone.utc) > run_deadline:
                        run.status = "aborted"
                        run.ended_at = datetime.now(timezone.utc)
                        try:
                            session.add(AuditLog(actor="runner", action="playbook_run_end", resource=str(run.id), policy_checked="self_heal", result="aborted", details="global timeout exceeded"))
                        except Exception:
                            pass
                        try:
                            from ..self_heal_models import LearningLog
                            session.add(LearningLog(service=run.service, signal_ref=None, diagnosis=run.diagnosis, action=json.dumps({"run_id": run.id, "status": "aborted"}), outcome=json.dumps({"result": "timeout"})))
                        except Exception:
                            pass
                        await session.commit()
                        return
                    # Prepare params
                    try:
                        params = json.loads(step.args) if getattr(step, "args", None) else {}
                    except Exception:
                        params = {}

                    # Execute step
                    srun = PlaybookStepRun(
                        run_id=run.id,
                        step_id=getattr(step, "id", None),
                        step_order=order,
                        status="running",
                        log=f"Executing {getattr(step, 'action', 'noop')} params={params}",
                    )
                    session.add(srun)
                    await session.flush()

                    # Time-limited execution
                    try:
                        await asyncio.wait_for(self._execute_action(getattr(step, "action", "noop"), params), timeout=float(getattr(step, "timeout_s", 60) or 60))
                    except Exception as exec_ex:
                        srun.status = "failed"
                        srun.ended_at = datetime.now(timezone.utc)
                        srun.log = (srun.log or "") + f"\nExecution error: {exec_ex}"
                        await session.commit()
                        # Attempt rollback if available
                        try:
                            rb_action = getattr(step, "rollback_action", None)
                            if rb_action:
                                try:
                                    rb_params = json.loads(getattr(step, "rollback_args", "") or "{}")
                                except Exception:
                                    rb_params = {}
                                rb_log = await self._execute_action(rb_action, rb_params)
                                srun.log += f"\nRollback executed: {rb_log}"
                        except Exception:
                            pass
                        raise

                    # Verifications
                    ok = await self._run_verifications_for_step(session, run, step, base_url)
                    if not ok:
                        srun.status = "failed"
                        srun.ended_at = datetime.now(timezone.utc)
                        srun.log = (srun.log or "") + "\nVerification failed"
                        await session.commit()
                        # rollback if defined
                        try:
                            rb_action = getattr(step, "rollback_action", None)
                            if rb_action:
                                try:
                                    rb_params = json.loads(getattr(step, "rollback_args", "") or "{}")
                                except Exception:
                                    rb_params = {}
                                rb_log = await self._execute_action(rb_action, rb_params)
                                srun.log += f"\nRollback executed: {rb_log}"
                        except Exception:
                            pass
                        raise RuntimeError("verification_failed")

                    # Mark succeeded
                    srun.status = "succeeded"
                    srun.ended_at = datetime.now(timezone.utc)
                    srun.log = (srun.log or "") + "\nStep verification passed"
                    await session.commit()
                    order += 1

                # Post-plan verifications (if any)
                try:
                    ver_res = await session.execute(
                        select(VerificationCheck).where(VerificationCheck.playbook_id == run.playbook_id, VerificationCheck.scope == "post_plan")
                    )
                    post_checks = ver_res.scalars().all()
                except Exception:
                    post_checks = []
                all_ok = True
                for chk in post_checks:
                    try:
                        cfg = json.loads(chk.config) if chk.config else {}
                    except Exception:
                        cfg = {}
                    ctype = (chk.check_type or "").lower()
                    if ctype in {"health_endpoint", "http_health"}:
                        ok = await self._verify_http_health(base_url, cfg.get("path", "/health"), cfg.get("expect", "ok"), int(cfg.get("timeout_s", 20)), int(cfg.get("retries", 2)), int(cfg.get("backoff_ms", 250)))
                        all_ok = all_ok and ok
                    elif ctype == "metric" or ctype == "metrics_threshold":
                        ok = await self._verify_metrics_threshold(session, run.service, cfg.get("metric"), cfg.get("gte"), cfg.get("lte"), int(cfg.get("window_min", 5)))
                        all_ok = all_ok and ok
                    elif ctype == "metrics_trend":
                        ok = await self._verify_metrics_trend(session, run.service, cfg.get("metric"), cfg.get("direction", "down"), int(cfg.get("window_min", 5)))
                        all_ok = all_ok and ok
                    else:
                        all_ok = False
                if not all_ok:
                    raise RuntimeError("post_plan_verification_failed")

                run.status = "succeeded"
                run.ended_at = datetime.now(timezone.utc)
                try:
                    session.add(AuditLog(actor="runner", action="playbook_run_end", resource=str(run.id), policy_checked="self_heal", result="succeeded", details=f"service={run.service}"))
                except Exception:
                    pass

                # Write learning log entry for successful execution
                try:
                    from ..self_heal_models import LearningLog
                    entry = LearningLog(
                        service=run.service,
                        signal_ref=None,
                        diagnosis=run.diagnosis,
                        action=json.dumps({
                            "playbook_id": run.playbook_id,
                            "run_id": run.id,
                            "status": "succeeded",
                        }),
                        outcome=json.dumps({
                            "status": "succeeded",
                            "result": "ok",
                            "ended_at": datetime.now(timezone.utc).isoformat(),
                        }),
                    )
                    session.add(entry)
                except Exception:
                    pass
                await session.commit()
            except Exception as ex:
                # Mark failed/rolled_back and create incident
                run.status = "failed"
                run.ended_at = datetime.now(timezone.utc)
                try:
                    session.add(AuditLog(actor="runner", action="playbook_run_end", resource=str(run.id), policy_checked="self_heal", result="failed", details=str(ex)))
                except Exception:
                    pass

                # Learning log
                try:
                    from ..self_heal_models import LearningLog
                    entry = LearningLog(
                        service=run.service,
                        signal_ref=None,
                        diagnosis=run.diagnosis,
                        action=json.dumps({
                            "playbook_id": run.playbook_id,
                            "run_id": run.id,
                            "status": "failed",
                        }),
                        outcome=json.dumps({
                            "result": "failed",
                            "error": str(ex),
                            "ended_at": datetime.now(timezone.utc).isoformat(),
                        }),
                    )
                    session.add(entry)
                except Exception:
                    pass

                # Incident + notify
                try:
                    from ..self_heal_models import Incident, IncidentEvent
                    from ..integrations.notify import notify
                    inc = Incident(service=run.service, severity="high", status="open", title=f"Playbook run {run.id} failed", summary="Self-heal runner reported failure")
                    session.add(inc)
                    await session.flush()
                    ev = IncidentEvent(incident_id=inc.id, event_type="playbook_failed", details=json.dumps({"run_id": run.id, "error": str(ex)}))
                    session.add(ev)
                    try:
                        notify(
                            event="incident.playbook_failed",
                            payload={"run_id": run.id, "service": run.service, "error": str(ex)},
                        )
                    except Exception:
                        pass
                except Exception:
                    pass
                await session.commit()
                try:
                    print(f"[self-heal:runner] run {run.id} failed: {ex}")
                except Exception:
                    pass


# Singleton instance
runner = ExecutionRunner(poll_interval_s=15)
