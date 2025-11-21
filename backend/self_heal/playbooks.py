from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

"""
Playbook engine (dry-run):
- Defines a minimal, deterministic spec for self-healing playbooks.
- Provides a selector to choose candidate templates from a diagnosis.
- Produces an executable plan structure (no execution side effects).

This module intentionally avoids DB writes/reads so it can be used safely
in observe-only mode and during early rollout.
"""


@dataclass
class VerifyHook:
    code: str  # e.g., http_health, metrics_threshold, smoke_script
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlaybookStep:
    id: str
    action: str  # e.g., restart_service, toggle_flag, scale_instances
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_s: int = 60
    verify: List[VerifyHook] = field(default_factory=list)
    rollback: Optional["PlaybookStep"] = None


@dataclass
class PlaybookTemplate:
    code: str
    title: str
    description: str
    preconditions: Dict[str, Any] = field(default_factory=dict)
    parameters_spec: Dict[str, Any] = field(default_factory=dict)
    steps: List[PlaybookStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        def _step_to_dict(s: PlaybookStep) -> Dict[str, Any]:
            d = {
                "id": s.id,
                "action": s.action,
                "parameters": s.parameters,
                "timeout_s": s.timeout_s,
                "verify": [asdict(v) for v in s.verify],
            }
            if s.rollback:
                d["rollback"] = _step_to_dict(s.rollback)
            return d

        return {
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "preconditions": self.preconditions,
            "parameters_spec": self.parameters_spec,
            "steps": [_step_to_dict(s) for s in self.steps],
        }


# ---- Built-in templates (seed set) ----

def _template_restart_service() -> PlaybookTemplate:
    step = PlaybookStep(
        id="restart",
        action="restart_service",
        parameters={"graceful": True},
        timeout_s=90,
        verify=[
            VerifyHook(code="http_health", params={"path": "/health", "expect": "ok", "timeout_s": 30}),
            VerifyHook(code="metrics_threshold", params={"metric": "error_rate", "lte": 0.05, "window_min": 5}),
        ],
        rollback=PlaybookStep(id="noop_rollback", action="noop", parameters={}),
    )
    return PlaybookTemplate(
        code="restart_service",
        title="Restart service",
        description="Gracefully restart the target service and verify health",
        preconditions={"change_window": "allowed"},
        parameters_spec={"graceful": {"type": "bool", "default": True}},
        steps=[step],
    )


def _template_rollback_flag() -> PlaybookTemplate:
    step = PlaybookStep(
        id="disable_flag",
        action="toggle_flag",
        parameters={"flag": "new_release", "state": False},
        timeout_s=10,
        verify=[VerifyHook(code="http_health", params={"path": "/health", "expect": "ok", "timeout_s": 20})],
        rollback=PlaybookStep(id="enable_flag", action="toggle_flag", parameters={"flag": "new_release", "state": True}),
    )
    return PlaybookTemplate(
        code="rollback_flag",
        title="Rollback feature flag",
        description="Disable risky feature flag and verify service recovers",
        preconditions={"feature_flag": "available"},
        parameters_spec={"flag": {"type": "str"}, "state": {"type": "bool", "default": False}},
        steps=[step],
    )


def _template_scale_up() -> PlaybookTemplate:
    step = PlaybookStep(
        id="scale_up",
        action="scale_instances",
        parameters={"min_delta": 1},
        timeout_s=120,
        verify=[VerifyHook(code="metrics_trend", params={"metric": "latency_ms", "direction": "down", "window_min": 5})],
        rollback=PlaybookStep(id="scale_down", action="scale_instances", parameters={"min_delta": -1}),
    )
    return PlaybookTemplate(
        code="scale_up_instances",
        title="Scale up instances",
        description="Increase service capacity to relieve latency",
        preconditions={"autoscaling": "enabled"},
        parameters_spec={"min_delta": {"type": "int", "default": 1}},
        steps=[step],
    )


def _template_warm_cache() -> PlaybookTemplate:
    step = PlaybookStep(
        id="warm_cache",
        action="warm_cache",
        parameters={},
        timeout_s=60,
        verify=[VerifyHook(code="metrics_threshold", params={"metric": "cache_hit_rate", "gte": 0.8, "window_min": 10})],
        rollback=PlaybookStep(id="noop_rollback", action="noop", parameters={}),
    )
    return PlaybookTemplate(
        code="warm_cache",
        title="Warm cache",
        description="Pre-warm cache to reduce latency on hot paths",
        preconditions={},
        parameters_spec={},
        steps=[step],
    )


def _template_increase_logging() -> PlaybookTemplate:
    step = PlaybookStep(
        id="increase_logging",
        action="set_logging_level",
        parameters={"level": "DEBUG", "ttl_min": 15},
        timeout_s=10,
        verify=[],
        rollback=PlaybookStep(id="reset_logging", action="set_logging_level", parameters={"level": "INFO"}),
    )
    return PlaybookTemplate(
        code="increase_logging",
        title="Increase logging temporarily",
        description="Raise logging to DEBUG for a short TTL to assist diagnosis",
        preconditions={},
        parameters_spec={"level": {"type": "str", "default": "DEBUG"}, "ttl_min": {"type": "int", "default": 15}},
        steps=[step],
    )


def _template_flush_circuit_breakers() -> PlaybookTemplate:
    step = PlaybookStep(
        id="flush_cb",
        action="flush_circuit_breakers",
        parameters={},
        timeout_s=15,
        verify=[VerifyHook(code="metrics_threshold", params={"metric": "http_5xx_rate", "lte": 0.05, "window_min": 5})],
        rollback=PlaybookStep(id="noop_rollback", action="noop", parameters={}),
    )
    return PlaybookTemplate(
        code="flush_circuit_breakers",
        title="Flush circuit breakers",
        description="Clear tripped breakers to allow recovery attempts",
        preconditions={},
        parameters_spec={},
        steps=[step],
    )


_BUILTINS: Dict[str, PlaybookTemplate] = {
    t.code: t for t in [
        _template_restart_service(),
        _template_rollback_flag(),
        _template_scale_up(),
        _template_warm_cache(),
        _template_increase_logging(),
        _template_flush_circuit_breakers(),
    ]
}


def list_templates() -> List[Dict[str, Any]]:
    return [tpl.to_dict() for tpl in _BUILTINS.values()]


def select_for_diagnosis(service: str, diagnosis_code: Optional[str] = None, severity: Optional[str] = None) -> List[PlaybookTemplate]:
    """Deterministic mapping from diagnosis to candidate templates."""
    candidates: List[str] = []
    if diagnosis_code == "service_down":
        candidates = ["restart_service", "rollback_flag"]
    elif diagnosis_code == "latency_spike":
        candidates = ["scale_up_instances", "warm_cache"]
    elif diagnosis_code == "elevated_errors":
        candidates = ["flush_circuit_breakers", "restart_service"]
    elif diagnosis_code == "general_degradation":
        candidates = ["increase_logging", "warm_cache"]
    else:
        # Fallback general set
        candidates = ["increase_logging", "restart_service"]

    # Severity can bias order (critical -> restart earlier)
    if severity in {"high", "critical"} and "restart_service" in candidates:
        candidates = ["restart_service"] + [c for c in candidates if c != "restart_service"]

    return [
        _BUILTINS[c] for c in candidates if c in _BUILTINS
    ]


def plan(service: str, diagnosis_code: Optional[str] = None, severity: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Produce a dry-run plan from templates. No execution, pure data."""
    parameters = parameters or {}
    templates = select_for_diagnosis(service, diagnosis_code, severity)
    if not templates:
        return {
            "service": service,
            "diagnosis": diagnosis_code,
            "severity": severity,
            "plans": [],
            "note": "No matching playbooks found"
        }

    def _materialize(tpl: PlaybookTemplate) -> Dict[str, Any]:
        # Merge defaults with provided parameters for the template's spec
        merged_params = {}
        for k, spec in tpl.parameters_spec.items():
            if k in parameters:
                merged_params[k] = parameters[k]
            elif isinstance(spec, dict) and "default" in spec:
                merged_params[k] = spec["default"]
        # Apply merged params to steps where keys match
        steps: List[Dict[str, Any]] = []
        for s in tpl.steps:
            s_dict = asdict(s)
            # asdict converts nested dataclasses too; keep verify hooks as dicts
            # Apply merged params keys if present in s.parameters
            if s_dict.get("parameters"):
                for k, v in merged_params.items():
                    if k in s_dict["parameters"]:
                        s_dict["parameters"][k] = v
            steps.append(s_dict)
        return {
            "template": tpl.code,
            "title": tpl.title,
            "description": tpl.description,
            "service": service,
            "preconditions": tpl.preconditions,
            "parameters": merged_params,
            "steps": steps,
            "execution": {"mode": "dry_run"},
        }

    return {
        "service": service,
        "diagnosis": diagnosis_code,
        "severity": severity,
        "plans": [_materialize(t) for t in templates],
    }
'        _template_bundle_drift_detector(),' 
'        _template_kernel_handshake_auto_repair(),' 
