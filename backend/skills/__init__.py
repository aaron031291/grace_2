"""
Skills Package - Unified skill abstractions for Grace's agents
All agent actions go through skills with standard schema, tracing, and governance
"""

from backend.skills.registry import skill_registry, Skill, SkillResult

__all__ = ['skill_registry', 'Skill', 'SkillResult']
