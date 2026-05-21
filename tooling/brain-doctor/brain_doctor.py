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


def _exempt_files(config: dict) -> set[str]:
    """Files exempt from per-page checks (spec §5 exempt_files)."""
    return set(config.get("exempt_files", []))


def _is_under_glob_base(rel: str, glob: str) -> bool:
    """True if rel equals or is nested under the non-wildcard base of a glob."""
    base = glob.rstrip("*").rstrip("/")
    return bool(base) and (rel == base or rel.startswith(base + "/"))


def _severity_counts(issues: list[Issue]) -> dict[str, int]:
    return {s: sum(1 for i in issues if i.severity == s) for s in ("error", "warning", "info")}


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
        if _is_under_glob_base(rel, g):
            return True
        core = g.strip("*").strip("/")
        if core and ("/" + rel + "/").find("/" + core + "/") != -1:
            return True
    return False


def iter_markdown_files(vault_root: Path, exclude_globs: list[str]) -> list[str]:
    rels = []
    for p in vault_root.rglob("*.md"):
        if p.is_symlink():
            continue  # don't follow symlinks out of the vault (security review 🟡)
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


# Length bound ({1,512}) caps per-start backtracking → linear scan, prevents
# ReDoS on pathological bracket-heavy vault content (security review 🟠).
# Real link targets are well under 512 chars; longer ones are abnormal anyway.
_WIKILINK_RE = re.compile(r"\[\[([^\]]{1,512})\]\]")
_MDLINK_RE = re.compile(r"\[[^\]]{1,512}\]\(([^)]{1,512})\)")


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
    exempt = _exempt_files(config)
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
        if _is_under_glob_base(rel, g) or fnmatch(rel, g):
            return rule.get("stale_days")
    return default_days


def check_stale(pages: dict[str, str], config: dict, today: date) -> list[Issue]:
    issues: list[Issue] = []
    exempt = _exempt_files(config)
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


def check_conflicts(pages: dict[str, str], config: dict) -> list[Issue]:
    issues: list[Issue] = []
    exempt = _exempt_files(config)
    for rel, content in pages.items():
        if rel in exempt:
            continue  # meta files (AGENTS.md/CLAUDE.md vs.) conflict kuralını anlatır, kendileri conflict değil
        if _CONFLICT_HEADING_RE.search(content) and _UNRESOLVED_RE.search(content):
            issues.append(Issue("", "unresolved_conflicts", rel, "Çözülmemiş ⚠️ Conflicts bölümü"))
    return issues


def check_empty(pages: dict[str, str], config: dict) -> list[Issue]:
    issues: list[Issue] = []
    exempt = _exempt_files(config)
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
        elif status == "ambiguous":
            issues.append(Issue("", "ambiguous_link", "index.md",
                                f"index'te belirsiz atıf (birden fazla sayfa): '{target}'"))
        elif status == "broken":
            issues.append(Issue("", "index_mismatch_missing_file", "index.md",
                                f"index'te var, dosya yok: '{target}'"))
    return issues, referenced


def check_page_not_in_index(pages: dict[str, str], config: dict, referenced: set[str]) -> list[Issue]:
    exempt = _exempt_files(config)
    return [
        Issue("", "page_not_in_index", rel, "index.md kataloğunda yok")
        for rel in pages
        if rel not in exempt and rel not in referenced
    ]


def check_orphan(
    pages: dict[str, str], config: dict, path_set: set[str],
    basename_index: dict[str, set[str]], index_referenced: set[str],
) -> list[Issue]:
    exempt = _exempt_files(config)
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


def apply_severity(issues: list[Issue], config: dict) -> None:
    sev = config.get("severity", {})
    for it in issues:
        it.severity = sev[it.category]  # KeyError impossible: validate_severity_coverage ran


def run_checks(vault_root: Path, config: dict, today: date | None = None) -> Report:
    today = today or date.today()
    rels = iter_markdown_files(vault_root, config.get("exclude_globs", []))
    pages = read_pages(vault_root, rels)
    path_set, basename_index = build_page_index(rels)

    issues: list[Issue] = []
    issues += check_links(pages, path_set, basename_index)
    idx_issues, index_referenced = check_index(pages, path_set, basename_index)
    issues += idx_issues
    issues += check_page_not_in_index(pages, config, index_referenced)
    issues += check_frontmatter(pages, config)
    issues += check_stale(pages, config, today)
    issues += check_conflicts(pages, config)
    issues += check_empty(pages, config)
    issues += check_stub(pages)
    issues += check_orphan(pages, config, path_set, basename_index, index_referenced)
    issues += check_deprecated_visibility(pages, index_referenced)

    apply_severity(issues, config)
    return Report(generated=today.isoformat(), total_pages=len(pages), issues=issues)


_ICON = {"error": "🔴", "warning": "🟡", "info": "🔵"}


def render_json(report: Report) -> str:
    return json.dumps(
        {
            "generated": report.generated,
            "total_pages": report.total_pages,
            "issues": [asdict(i) for i in report.issues],
        },
        ensure_ascii=False,
        indent=2,
    )


def render_markdown(report: Report) -> str:
    counts = _severity_counts(report.issues)
    lines = [
        f"# Brain Doctor Report — {report.generated}",
        "",
        f"- Toplam sayfa: {report.total_pages}",
        f"- 🔴 error: {counts['error']}  🟡 warning: {counts['warning']}  🔵 info: {counts['info']}",
        "",
    ]
    by_cat: dict[str, list[Issue]] = {}
    for it in report.issues:
        by_cat.setdefault(it.category, []).append(it)
    for cat in sorted(by_cat):
        items = by_cat[cat]
        icon = _ICON.get(items[0].severity, "⚪")
        lines.append(f"## {icon} {cat} ({len(items)})")
        for it in items:
            loc = f":{it.line}" if it.line else ""
            lines.append(f"- `{it.page}{loc}` — {it.detail}")
        lines.append("")
    return "\n".join(lines)


def repo_root(start: Path) -> Path:
    """Walk up from a path to find the repo root (.git). Fallback: the path's dir."""
    p = start.resolve()
    for parent in [p, *p.parents]:
        if (parent / ".git").exists():
            return parent
    return p if p.is_dir() else p.parent


def resolve_report_dir(arg_output_dir: str | None, config: dict, config_path: Path) -> Path:
    raw = arg_output_dir or config.get("default_report_dir", "tooling/brain-doctor/reports")
    rp = Path(raw)
    if rp.is_absolute():
        return rp.resolve()
    # relative → anchor to the repo root of the CONFIG file, NOT cwd (Codex Turn-2 fix)
    return (repo_root(config_path) / rp).resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brain-doctor",
                                     description="Otomaix Brain Doctor v1 — vault health checker")
    parser.add_argument("--vault")
    parser.add_argument("--config", default=str(Path(__file__).with_name("brain_doctor.config.json")))
    parser.add_argument("--output-dir")
    parser.add_argument("--allow-vault-output", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-report", action="store_true")
    parser.add_argument("--min-severity", choices=["error", "warning", "info"])
    args = parser.parse_args(argv)

    try:
        config_path = Path(args.config)
        config = load_config(config_path)
        validate_severity_coverage(config)
        vault_root = Path(args.vault) if args.vault else Path(config["vault_path"])
        if not vault_root.is_dir():
            print(f"Vault yok: {vault_root}", file=sys.stderr)
            return 2
        report = run_checks(vault_root, config)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Tool/config/IO hatası: {e}", file=sys.stderr)
        return 2

    had_error = any(i.severity == "error" for i in report.issues)

    if args.min_severity:
        floor = SEVERITY_RANK[args.min_severity]
        report.issues = [i for i in report.issues if SEVERITY_RANK[i.severity] >= floor]

    counts = _severity_counts(report.issues)
    # Özet bir DIAGNOSTIC'tir → stderr. stdout yalnız veri taşır (--json'da saf JSON).
    print(f"Brain Doctor — {report.generated}: {report.total_pages} sayfa | "
          f"🔴 {counts['error']} 🟡 {counts['warning']} 🔵 {counts['info']}", file=sys.stderr)

    if args.json:
        print(render_json(report))
    elif not args.no_report:
        out_dir = resolve_report_dir(args.output_dir, config, config_path)
        vault_abs = vault_root.resolve()
        if (out_dir == vault_abs or vault_abs in out_dir.parents) and not args.allow_vault_output:
            print(f"Reddedildi: çıktı vault altına ({out_dir}). --allow-vault-output gerekli.",
                  file=sys.stderr)
            return 2
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")
            (out_dir / "report.json").write_text(render_json(report), encoding="utf-8")
            print(f"Rapor: {out_dir}/report.md (+ report.json)", file=sys.stderr)
        except OSError as e:
            print(f"Rapor yazılamadı: {e}", file=sys.stderr)
            return 2

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
