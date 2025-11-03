"""Central configuration for Grace's Transcendence code generation stack.

The goal of this module is to provide a single source of truth for
language-aware parameters, template registrations, and default behaviours
used by the understanding, planning, and generation subsystems. Keeping
these settings consolidated makes it easier to evolve the agent without
chasing scattered constants across the codebase.
"""

from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------------------
# Language context metadata
# ---------------------------------------------------------------------------

LANGUAGE_CONTEXTS: Dict[str, Dict[str, List[str]]] = {
    "python": {
        "file_patterns": [".py"],
        "keywords": ["def", "class", "import", "async", "await"],
        "frameworks": ["fastapi", "django", "flask", "sqlalchemy"],
    },
    "javascript": {
        "file_patterns": [".js", ".jsx"],
        "keywords": ["function", "const", "let", "import", "export"],
        "frameworks": ["react", "vue", "express", "node"],
    },
    "typescript": {
        "file_patterns": [".ts", ".tsx"],
        "keywords": ["interface", "type", "function", "const", "import"],
        "frameworks": ["react", "angular", "nestjs"],
    },
}


# ---------------------------------------------------------------------------
# Code generation template registry
# ---------------------------------------------------------------------------

# Maps language -> artifact type -> CodeGenerator attribute name. The
# CodeGenerator dynamically resolves these references to keep the actual
# template implementations close to the class while centralising the
# registration data here.
CODE_GENERATION_TEMPLATES: Dict[str, Dict[str, str]] = {
    "python": {
        "function": "_python_function_template",
        "class": "_python_class_template",
        "api_endpoint": "_python_api_endpoint_template",
        "test": "_python_test_template",
    }
}


# ---------------------------------------------------------------------------
# Default behaviours and preferences per language
# ---------------------------------------------------------------------------

CODE_GENERATION_DEFAULTS: Dict[str, Dict[str, str]] = {
    "python": {
        "style": "pep8",
        "docstring_style": "google",
        "test_framework": "pytest",
        "security_scan": "hunter",
    }
}


# ---------------------------------------------------------------------------
# Miscellaneous shared parameters
# ---------------------------------------------------------------------------

SUPPORTED_TASK_TYPES = (
    "create_feature",
    "fix_bug",
    "refactor",
    "add_tests",
    "implement_api",
)


DEFAULT_CODE_LANGUAGE: str = "python"

