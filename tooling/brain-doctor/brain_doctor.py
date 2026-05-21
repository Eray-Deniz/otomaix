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


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Empty dict if no frontmatter block.

    Minimal YAML subset (no external dep): scalars, inline [a, b], block '- item'.
    """
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    block = content[3:end].strip("\n")
    body = content[end + 4:]
    fm: dict = {}
    current_key: str | None = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if re.match(r"^\s+-\s+", line) and current_key is not None:
            item = line.strip()[1:].strip().strip('"').strip("'")
            fm.setdefault(current_key, [])
            if isinstance(fm[current_key], list):
                fm[current_key].append(item)
            continue
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            fm[key] = []
            current_key = key
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            current_key = None
        else:
            fm[key] = val.strip('"').strip("'")
            current_key = None
    return fm, body


def _is_excluded(rel: str, globs: list[str]) -> bool:
    for g in globs:
        if fnmatch(rel, g):
            return True
        base = g.rstrip("*").rstrip("/")
        if base and (rel == base or rel.startswith(base + "/")):
            return True
        core = g.strip("*").strip("/")
        if core and ("/" + rel + "/").find("/" + core + "/") != -1:
            return True
    return False


def iter_markdown_files(vault_root: Path, exclude_globs: list[str]) -> list[str]:
    rels = []
    for p in vault_root.rglob("*.md"):
        rel = p.relative_to(vault_root).as_posix()
        if _is_excluded(rel, exclude_globs):
            continue
        rels.append(rel)
    return sorted(rels)


def read_pages(vault_root: Path, rels: list[str]) -> dict[str, str]:
    pages = {}
    for rel in rels:
        try:
            pages[rel] = (vault_root / rel).read_text(encoding="utf-8")
        except OSError:
            pass
    return pages


def build_page_index(rels: list[str]) -> tuple[set[str], dict[str, set[str]]]:
    path_set = set(rels)
    bidx: dict[str, set[str]] = {}
    for rel in rels:
        name = rel.rsplit("/", 1)[-1]
        stem = name[:-3] if name.endswith(".md") else name
        for key in (name, stem):
            bidx.setdefault(key, set()).add(rel)
    return path_set, bidx


_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_MDLINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def strip_code(content: str) -> str:
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    content = re.sub(r"`[^`\n]+`", "", content)
    return content


def extract_links(content: str) -> list[tuple[str, str]]:
    """Return [(kind, target)] for internal links only.

    Skips external URLs, pure anchors, and '@'-prefixed source-attribution refs.
    """
    clean = strip_code(content)
    out: list[tuple[str, str]] = []
    for m in _WIKILINK_RE.finditer(clean):
        target = m.group(1).split("|")[0].split("#")[0].strip()
        if target and not target.startswith("@"):
            out.append(("wikilink", target))
    for m in _MDLINK_RE.finditer(clean):
        target = m.group(1).split("#")[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "@")):
            continue
        if "/" in target or target.endswith(".md"):
            out.append(("mdlink", target))
    return out


def resolve_link(
    source_rel: str, target: str, path_set: set[str], basename_index: dict[str, set[str]]
) -> tuple[str, str | None]:
    """Resolve a link target per spec §7. Returns (status, resolved_rel | None).

    status: 'ok' | 'broken' | 'ambiguous'. Path-temelli denemeler basename'den ÖNCE.
    """
    candidates = [target] if target.endswith(".md") else [target, target + ".md"]
    # 1+2: exact vault-relative (as-written and .md-appended)
    for c in candidates:
        if c in path_set:
            return "ok", c
    # 3: source-relative (as-written and .md-appended)
    src_dir = source_rel.rsplit("/", 1)[0] if "/" in source_rel else ""
    for c in candidates:
        rel = os.path.normpath(os.path.join(src_dir, c)).replace(os.sep, "/")
        if rel in path_set:
            return "ok", rel
    # 4: basename fallback ONLY for targets without a path separator
    if "/" in target:
        return "broken", None
    matches = basename_index.get(target, set())
    if len(matches) == 1:
        return "ok", next(iter(matches))
    if len(matches) > 1:
        return "ambiguous", None
    return "broken", None


def check_links(
    pages: dict[str, str], path_set: set[str], basename_index: dict[str, set[str]]
) -> list[Issue]:
    issues: list[Issue] = []
    for rel, content in pages.items():
        for kind, target in extract_links(content):
            status, _ = resolve_link(rel, target, path_set, basename_index)
            if status == "ok":
                continue
            if status == "ambiguous":
                cat = "ambiguous_link"
            else:
                cat = "broken_wikilink" if kind == "wikilink" else "broken_md_link"
            issues.append(Issue("", cat, rel, f"{status}: '{target}'"))
    return issues


def check_frontmatter(pages: dict[str, str], config: dict) -> list[Issue]:
    issues: list[Issue] = []
    exempt = set(config.get("exempt_files", []))
    required = config.get("required_frontmatter", [])
    enums = config.get("enums", {})
    for rel, content in pages.items():
        if rel in exempt:
            continue
        fm, _ = parse_frontmatter(content)
        if not fm:
            issues.append(Issue("", "frontmatter_absent", rel, "Frontmatter bloğu yok"))
            continue
        for fld in required:
            if fld == "sources":
                if "sources" not in fm:
                    issues.append(Issue("", "sources_missing", rel, "sources alanı yok"))
                elif isinstance(fm["sources"], list) and not fm["sources"]:
                    issues.append(Issue("", "sources_empty", rel, "sources boş ([])"))
                continue
            if fld not in fm or fm[fld] in ("", [], None):
                issues.append(Issue("", "frontmatter_missing_field", rel, f"Zorunlu alan eksik: {fld}"))
        for fld, allowed in enums.items():
            val = fm.get(fld)
            if isinstance(val, str) and val and val not in allowed:
                issues.append(Issue("", "invalid_enum_value", rel, f"{fld}={val} enum dışı"))
    return issues


def _resolve_stale_days(rel: str, rules: list[dict], default_days):
    """First matching glob wins. Returns stale_days (may be None = exempt) or default."""
    for rule in rules:
        g = rule.get("glob", "")
        base = g.rstrip("*").rstrip("/")
        if (base and (rel == base or rel.startswith(base + "/"))) or fnmatch(rel, g):
            return rule.get("stale_days")
    return default_days


def check_stale(pages: dict[str, str], config: dict, today: date) -> list[Issue]:
    issues: list[Issue] = []
    exempt = set(config.get("exempt_files", []))
    rules = config.get("stale_rules", [])
    default_days = config.get("default_stale_days")
    for rel, content in pages.items():
        if rel in exempt:
            continue
        fm, _ = parse_frontmatter(content)
        if fm.get("status") != "active":
            continue
        days = _resolve_stale_days(rel, rules, default_days)
        if days is None:
            continue
        lv = fm.get("last-verified")
        if not isinstance(lv, str) or not lv:
            continue  # missing last-verified handled by frontmatter check
        try:
            lv_date = datetime.strptime(lv.strip(), "%Y-%m-%d").date()
        except ValueError:
            continue
        age = (today - lv_date).days
        if age > days:
            issues.append(Issue("", "stale", rel, f"last-verified {age} gün önce (eşik {days})"))
    return issues


_CONFLICT_HEADING_RE = re.compile(r"^#{2,3}\s*.*Conflicts", re.MULTILINE)
_UNRESOLVED_RE = re.compile(r"unresolved|çözülmedi|not resolved", re.IGNORECASE)


def check_conflicts(pages: dict[str, str]) -> list[Issue]:
    issues: list[Issue] = []
    for rel, content in pages.items():
        if _CONFLICT_HEADING_RE.search(content) and _UNRESOLVED_RE.search(content):
            issues.append(Issue("", "unresolved_conflicts", rel, "Çözülmemiş ⚠️ Conflicts bölümü"))
    return issues


def check_empty(pages: dict[str, str], config: dict) -> list[Issue]:
    issues: list[Issue] = []
    exempt = set(config.get("exempt_files", []))
    min_chars = config.get("min_content_chars", 100)
    for rel, content in pages.items():
        if rel in exempt:
            continue
        _, body = parse_frontmatter(content)
        n = len(body.strip())
        if n < min_chars:
            issues.append(Issue("", "empty_or_short", rel, f"Gövde {n} char (< {min_chars})"))
    return issues


def check_stub(pages: dict[str, str]) -> list[Issue]:
    issues: list[Issue] = []
    for rel, content in pages.items():
        fm, _ = parse_frontmatter(content)
        if fm.get("status") == "stub":
            issues.append(Issue("", "stub", rel, "status: stub"))
    return issues


_BACKTICK_REF_RE = re.compile(r"`([\w./-]+\.md)`")


def _extract_index_refs(index_content: str) -> list[str]:
    """index.md uses both [[wikilink]] and backtick `path.md` (spec §11)."""
    refs: list[str] = []
    for m in _WIKILINK_RE.finditer(index_content):
        t = m.group(1).split("|")[0].split("#")[0].strip()
        if t and not t.startswith("@"):
            refs.append(t)
    for m in _BACKTICK_REF_RE.finditer(index_content):
        refs.append(m.group(1).strip())
    return refs


def check_index(
    pages: dict[str, str], path_set: set[str], basename_index: dict[str, set[str]]
) -> tuple[list[Issue], set[str]]:
    issues: list[Issue] = []
    referenced: set[str] = set()
    index_content = pages.get("index.md", "")
    for target in _extract_index_refs(index_content):
        status, rel = resolve_link("index.md", target, path_set, basename_index)
        if rel:
            referenced.add(rel)
        elif status == "broken":
            issues.append(Issue("", "index_mismatch_missing_file", "index.md",
                                f"index'te var, dosya yok: '{target}'"))
    return issues, referenced


def check_page_not_in_index(pages: dict[str, str], config: dict, referenced: set[str]) -> list[Issue]:
    exempt = set(config.get("exempt_files", []))
    return [
        Issue("", "page_not_in_index", rel, "index.md kataloğunda yok")
        for rel in pages
        if rel not in exempt and rel not in referenced
    ]


def check_orphan(
    pages: dict[str, str], config: dict, path_set: set[str],
    basename_index: dict[str, set[str]], index_referenced: set[str],
) -> list[Issue]:
    exempt = set(config.get("exempt_files", []))
    referenced = set(index_referenced)
    for rel, content in pages.items():
        for _, target in extract_links(content):
            _, dest = resolve_link(rel, target, path_set, basename_index)
            if dest:
                referenced.add(dest)
    return [
        Issue("", "orphan", rel, "Hiç inbound link yok")
        for rel in pages
        if rel not in exempt and rel not in referenced
    ]


def check_deprecated_visibility(pages: dict[str, str], index_referenced: set[str]) -> list[Issue]:
    issues: list[Issue] = []
    for rel in sorted(index_referenced):
        fm, _ = parse_frontmatter(pages.get(rel, ""))
        if fm.get("status") in ("superseded", "deprecated"):
            issues.append(Issue("", "deprecated_visibility", rel,
                                f"status: {fm.get('status')} ama index'te görünür (policy candidate)"))
    return issues
