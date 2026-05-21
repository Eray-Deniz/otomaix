#!/usr/bin/env python3
"""Otomaix Brain Doctor v1 — structural health checker for the otomaix-brain vault.

Stdlib only. Read-only with respect to the vault.
Spec: docs/specs/2026-05-21-otomaix-brain-doctor.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from fnmatch import fnmatch
from pathlib import Path

# Every category the tool can emit. Must equal set(config["severity"]) — guarded at runtime.
ALL_CATEGORIES = {
    "broken_wikilink", "broken_md_link", "ambiguous_link",
    "index_mismatch_missing_file", "page_not_in_index",
    "frontmatter_absent", "frontmatter_missing_field", "invalid_enum_value",
    "stale", "unresolved_conflicts", "empty_or_short",
    "sources_missing", "sources_empty",
    "stub", "orphan", "deprecated_visibility",
}
SEVERITY_RANK = {"error": 3, "warning": 2, "info": 1}


@dataclass
class Issue:
    severity: str
    category: str
    page: str
    detail: str
    line: int | None = None


@dataclass
class Report:
    generated: str
    total_pages: int
    issues: list[Issue] = field(default_factory=list)


def load_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_severity_coverage(config: dict) -> None:
    """Spec §6: every emittable category must have a severity mapping."""
    missing = ALL_CATEGORIES - set(config.get("severity", {}))
    if missing:
        raise ValueError(f"config.severity eksik kategoriler: {sorted(missing)}")
