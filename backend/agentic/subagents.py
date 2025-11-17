"""Definitions for specialised subagents used by the coding orchestrator."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .tools import Toolbelt


@dataclass
class SubAgentResult:
    """Captured outcome from a subagent execution."""

    step_id: str
    summary: str
    diff: Optional[Dict[str, Any]] = None
    notes: list = field(default_factory=list)
    status: str = "completed"

    def to_payload(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "summary": self.summary,
            "diff": self.diff,
            "notes": self.notes,
            "status": self.status,
        }


class BaseSubAgent:
    """Base class for all coding subagents."""

    def __init__(self, *, toolbelt: Toolbelt, intent: Dict[str, Any], code_context: Dict[str, Any], step: Dict[str, Any]):
        self.toolbelt = toolbelt
        self.intent = intent or {}
        self.code_context = code_context or {}
        self.step = step
        self.step_id = step.get("id") or str(uuid.uuid4())

    async def run(self, orchestration_ctx) -> SubAgentResult:  # noqa: ANN001
        """Execute subagent task - must be implemented by subclass"""
        raise NotImplementedError(f"{self.__class__.__name__}.run() must be implemented")


class AnalysisAgent(BaseSubAgent):
    """Collects relevant code context using deep search and symbol graph."""

    async def run(self, orchestration_ctx) -> SubAgentResult:  # noqa: ANN001
        query = self.step.get("search", orchestration_ctx.description)

        related = await self.toolbelt.deep_search(query=query, language=self.step.get("language", "python"))
        notes = [f"Found {len(related.get('matches', []))} related code blocks"]

        return SubAgentResult(
            step_id=self.step_id,
            summary="Context gathered",
            diff=None,
            notes=notes,
        )


class ImplementationAgent(BaseSubAgent):
    """Generates or edits code using stored patterns and templates."""

    async def run(self, orchestration_ctx) -> SubAgentResult:  # noqa: ANN001
        spec = {
            "name": self.step.get("target", "generated_function"),
            "description": self.step.get("description", orchestration_ctx.description),
            "parameters": self.step.get("parameters", []),
            "return_type": self.step.get("return_type", "Any"),
        }

        generation = await self.toolbelt.generate_code(spec=spec, language=self.step.get("language", "python"))

        file_path = self.step.get("file_path") or orchestration_ctx.code_context.get("file_path")
        diff = None

        if file_path:
            diff = await self.toolbelt.create_patch(file_path=file_path, new_code=generation.get("code", ""))

        return SubAgentResult(
            step_id=self.step_id,
            summary=generation.get("metadata", {}).get("generator_version", "code_generation"),
            diff=diff,
            notes=generation.get("patterns_used", []),
        )


class ReviewAgent(BaseSubAgent):
    """Performs static review of generated diffs."""

    async def run(self, orchestration_ctx) -> SubAgentResult:  # noqa: ANN001
        file_path = self.step.get("file_path")
        diff = None
        if file_path:
            diff = await self.toolbelt.preview_diff(file_path)

        findings = await self.toolbelt.static_review(diff)

        return SubAgentResult(
            step_id=self.step_id,
            summary="Static analysis completed",
            diff=diff,
            notes=findings,
        )


__all__ = [
    "SubAgentResult",
    "BaseSubAgent",
    "AnalysisAgent",
    "ImplementationAgent",
    "ReviewAgent",
]
