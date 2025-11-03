"""Common tools exposed to orchestrator subagents."""

from __future__ import annotations

import asyncio
import difflib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..code_memory import code_memory
from ..code_generator import code_generator
from ..immutable_log import immutable_log


class Toolbelt:
    """Utility helpers that subagents can invoke."""

    async def deep_search(self, *, query: str, language: str = "python", limit: int = 10) -> Dict[str, Any]:
        """Semantic-ish search across stored code patterns and symbols."""

        matches = await code_memory.deep_search(query=query, language=language, limit=limit)
        return {"matches": matches}

    async def generate_code(self, *, spec: Dict[str, Any], language: str = "python") -> Dict[str, Any]:
        """Generate code using Grace's code generator."""

        return await code_generator.generate_function(spec=spec, language=language)

    async def create_patch(self, *, file_path: str, new_code: str) -> Dict[str, Any]:
        """Create a diff patch for the given file without applying it."""

        original = await self._read_file_async(file_path)

        patch = difflib.unified_diff(
            original.splitlines(),
            new_code.splitlines(),
            fromfile=file_path,
            tofile=file_path,
            lineterm="",
        )

        patch_text = "\n".join(list(patch))

        return {
            "file_path": file_path,
            "patch": patch_text,
            "new_code": new_code,
        }

    async def preview_diff(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Return the latest diff proposal logged for a file if present."""

        entries = await immutable_log.get_entries(resource=file_path, limit=1)
        if not entries:
            return None

        payload = entries[0].get("payload") if isinstance(entries[0], dict) else entries[0]
        try:
            parsed = json.loads(payload) if isinstance(payload, str) else payload
        except Exception:
            parsed = {"payload": payload}

        return parsed.get("diff") if isinstance(parsed, dict) else parsed

    async def static_review(self, diff: Optional[Dict[str, Any]]) -> List[str]:
        """Naive static review placeholder that looks for risky patterns."""

        if not diff or not diff.get("patch"):
            return ["No diff provided"]

        patch = diff["patch"].lower()
        findings = []
        if "todo" in patch:
            findings.append("Diff still contains TODO markers")
        if "eval(" in patch or "exec(" in patch:
            findings.append("Potential dynamic execution detected")
        if "password" in patch:
            findings.append("Possible secret reference - ensure secure handling")
        return findings or ["No static issues detected"]

    async def run_validation_suite(self, task_id: str, progress_cb):  # noqa: ANN001
        """Placeholder validation suite that simply marks progress."""

        for pct in (25, 50, 75, 100):
            await asyncio.sleep(0.1)
            await progress_cb(task_id, pct)
        return {"status": "success"}

    async def _read_file_async(self, file_path: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, Path(file_path).read_text)


__all__ = ["Toolbelt"]
