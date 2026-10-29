"""sourceproof corpus: pack metadata plus 50 authored source-verification skills.

Skills are authored as plain dicts in ``part1``..``part3`` and loaded once into
the validated :class:`~sourceproof.model.Skill` shape.
"""

from __future__ import annotations

from typing import Any

from ..model import skill_from_dict
from .part1 import SKILLS as PART1
from .part2 import SKILLS as PART2
from .part3 import SKILLS as PART3

PACK: dict[str, Any] = {
    "name": "sourceproof",
    "version": "1.0.0",
    "category": "source-review",
    "license": "MIT",
    "runtime": "Claude Code, opencode, or any agent runtime that loads SKILL.md files",
    "description": (
        "50 validated skills for proving a source-level finding against the tree "
        "it came from: the file, the line, the sink, and a call path whose every "
        "hop the reviewer can check, with a CLI that does the checking."
    ),
    "expected_skills": 50,
    "meta_keys": ("phase",),
    "requires_verification": False,
}

SKILLS: list[Any] = [skill_from_dict(raw) for raw in (*PART1, *PART2, *PART3)]
BY_SLUG: dict[str, Any] = {skill.slug: skill for skill in SKILLS}
