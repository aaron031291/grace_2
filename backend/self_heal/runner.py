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
        while not self._stopping.is_set():
            try:
                await self._tick()
            except Exception as e:  # pragma: no cover
                try:
                    print(f"[self-heal:runner] tick error: {e}")
                except Exception:
                    pass
            await asyncio.wait_for(asyncio.sleep(self._interval), timeout=self._interval + 1)

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

    # ---- Action adapters (safe/simulated) ----
    async def _act_restart_service(self, service: str, graceful: bool = True) -> str:
        # Simulate restart; real integration can be added later
        await asyncio.sleep(0.05)
        return f"restart_service(graceful={graceful}) simulated"

    async def _act_toggle_flag(self, flag: str, state: bool) -> str:
        self._flags[flag] = {"state": bool(state), "at": datetime.now(timezone.utc)}
        return f"toggle_flag {flag} -> {state}"

    async def _act_scale_instances(self, min_delta: int) -> str:
        if not isinstance(min_delta, int) or min_delta < -3 or min_delta > 3:
            raise ValueError("min_delta out of bounds [-3,3]")
        await asyncio.sleep(0.05)
        return f"scale_instances by {min_delta} (simulated)"

    async def _act_warm_cache(self) -> str:
        await asyncio.sleep(0.05)
        return "warm_cache simulated"

    async def _act_set_logging_level(self, level: str = "DEBUG", ttl_min: int = 15) -> str:
        self._log_level_ttl = datetime.now(timezone.utc) + timedelta(minutes=int(ttl_min or 15))
        return f"set_logging_level {level} ttl={ttl_min}m (simulated)"

    async def _act_flush_circuit_breakers(self) -> str:
        await asyncio.sleep(0.02)
        return "flush_circuit_breakers simulated"

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
                # disabled by default for safety
                return False
            else:
                # Unknown check type -> fail closed
                return False
        return True

    # HARDENED: Parameter bounds validation whitelist
    PARAMETER_BOUNDS = {
        "scale_instances": {
            "min_delta": {"type": int, "min": -3, "max": 3, "required": True}
        },
        "set_logging_level": {
            "level": {"type": str, "allowed": ["DEBUG", "INFO", "WARN", "ERROR"], "default": "DEBUG"},
            "ttl_min": {"type": int, "min": 1, "max": 120, "default": 15}
        },
        "toggle_flag": {
            "flag": {"type": str, "required": True, "min_length": 1, "max_length": 50},
            "state": {"type": bool, "required": True}
        },
        "restart_service": {
            "graceful": {"type": bool, "default": True}
        }
    }
    
    def _validate_parameters(self, action: str, params: Dict[str, Any]) -> tuple[bool, str, Dict[str, Any]]:
        """
        Validate and sanitize parameters against whitelist.
        
        Returns: (valid, error_message, sanitized_params)
        """
        bounds = self.PARAMETER_BOUNDS.get(action, {})
        sanitized = {}
        
        for key, rules in bounds.items():
            value = params.get(key)
            
            # Check required
            if rules.get("required") and value is None:
                return False, f"Missing required parameter: {key}", {}
            
            # Use default if not provided
            if value is None and "default" in rules:
                value = rules["default"]
            
            if value is None:
                continue
            
            # Type validation
            expected_type = rules.get("type")
            if expected_type and not isinstance(value, expected_type):
                return False, f"Invalid type for {key}: expected {expected_type.__name__}", {}
            
            # Numeric bounds
            if isinstance(value, int):
                if "min" in rules and value < rules["min"]:
                    return False, f"{key}={value} below minimum {rules['min']}", {}
                if "max" in rules and value > rules["max"]:
                    return False, f"{key}={value} exceeds maximum {rules['max']}", {}
            
            # String constraints
            if isinstance(value, str):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    return False, f"{key} too short (min: {rules['min_length']})", {}
                if "max_length" in rules and len(value) > rules["max_length"]:
                    return False, f"{key} too long (max: {rules['max_length']})", {}
                if "allowed" in rules and value not in rules["allowed"]:
                    return False, f"{key}={value} not in allowed values {rules['allowed']}", {}
            
            sanitized[key] = value
        
        # Check for unexpected parameters (prevent injection)
        unexpected = set(params.keys()) - set(bounds.keys())
        if unexpected:
            return False, f"Unexpected parameters: {unexpected}", {}
        
        return True, "validated", sanitized
    
    async def _execute_action(self, action: str, params: Dict[str, Any]) -> str:
        # HARDENED: Validate parameters against whitelist
        valid, error_msg, sanitized_params = self._validate_parameters(action, params)
        
        if not valid:
            raise ValueError(f"Parameter validation failed: {error_msg}")
        
        # Use sanitized parameters
        fn = self._action_dispatch(action)
        return await fn(**sanitized_params) if sanitized_params else await fn()

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

            # HARDENED: Change window enforcement - BLOCK execution outside window for medium/high/critical
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
                    # HARD BLOCK: Require explicit approved request
                    if not getattr(run, "approval_request_id", None):
                        # No approval request - abort run
                        run.status = "aborted"
                        run.ended_at = now
                        session.add(AuditLog(
                            actor="runner",
                            action="playbook_run_blocked",
                            resource=str(run.id),
                            policy_checked="change_window",
                            result="blocked",
                            details=f"outside_window={outside_window} impact={impact} no_approval"
                        ))
                        # Learning entry for blocked run
                        try:
                            from ..self_heal_models import LearningLog
                            session.add(LearningLog(
                                service=run.service,
                                diagnosis=run.diagnosis,
                                action=json.dumps({"status": "blocked", "reason": "change_window"}),
                                outcome=json.dumps({"result": "blocked", "outside_window": True, "impact": impact})
                            ))
                        except Exception:
                            pass
                        await session.commit()
                        return
                    
                    # Has approval request - verify it's approved
                    from ..governance_models import ApprovalRequest
                    appr2 = await session.get(ApprovalRequest, run.approval_request_id)
                    if not appr2 or getattr(appr2, "status", "").lower() != "approved":
                        # Not approved - defer (don't abort yet, may get approved later)
                        return
            except Exception as e:
                # If change window check fails, err on side of caution - block
                run.status = "aborted"
                run.ended_at = now
                session.add(AuditLog(
                    actor="runner",
                    action="playbook_run_error",
                    resource=str(run.id),
                    policy_checked="change_window",
                    result="error",
                    details=f"change_window_check_failed: {str(e)}"
                ))
                await session.commit()
                return

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
            
            # HARDENED: Global run timeout watchdog
            from ..settings import settings
            global_timeout_seconds = settings.SELF_HEAL_RUN_TIMEOUT_MIN * 60

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

            # Use configurable base URL
            from ..settings import settings
            base_url = settings.SELF_HEAL_BASE_URL
            order = 1
            
            # Wrap entire execution in global timeout watchdog
            try:
                await asyncio.wait_for(
                    self._execute_playbook_steps(session, run, steps, base_url),
                    timeout=global_timeout_seconds
                )
            except asyncio.TimeoutError:
                # Global timeout exceeded - abort run
                run.status = "aborted"
                run.ended_at = datetime.now(timezone.utc)
                
                session.add(AuditLog(
                    actor="runner",
                    action="playbook_run_timeout",
                    resource=str(run.id),
                    policy_checked="timeout_watchdog",
                    result="aborted",
                    details=f"timeout_minutes={settings.SELF_HEAL_RUN_TIMEOUT_MIN}"
                ))
                
                # Learning entry for timeout
                try:
                    from ..self_heal_models import LearningLog
                    session.add(LearningLog(
                        service=run.service,
                        diagnosis=run.diagnosis,
                        action=json.dumps({"status": "aborted", "reason": "global_timeout"}),
                        outcome=json.dumps({
                            "result": "timeout",
                            "timeout_min": settings.SELF_HEAL_RUN_TIMEOUT_MIN,
                            "ended_at": datetime.now(timezone.utc).isoformat()
                        })
                    ))
                except Exception:
                    pass
                
                await session.commit()
                print(f"[self-heal:runner] run {run.id} aborted: global timeout ({settings.SELF_HEAL_RUN_TIMEOUT_MIN}min)")
                return
    
    async def _execute_playbook_steps(self, session, run, steps, base_url: str):
        """Execute playbook steps with validation and verification"""
        order = 1
        try:
                for step in steps:
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
