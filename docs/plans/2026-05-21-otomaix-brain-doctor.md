# Otomaix Brain Doctor v1 Implementation Plan

> **For Claude Code workers:** Bu plan Claude Code ile yürütülür (Otomaix workflow: Claude yazar/uygular, Codex read-only reviewer). Önerilen sub-skill: superpowers:subagent-driven-development veya superpowers:executing-plans. **Not (Codex/genel agent):** bu satır Claude'a özeldir — superpowers skill'leri Codex'e uygulanmaz; checkbox (`- [ ]`) adımları ve kod ise herkes için geçerlidir.

**Goal:** `otomaix-brain` vault'unun yapısal sağlığını denetleyen, sıfır-bağımlılık, vault'a karşı read-only tek-dosya Python CLI üret.

**Architecture:** Tek dosya `brain_doctor.py` (config-driven check fonksiyonları listesi) + `brain_doctor.config.json` (eşikler/enum/severity data). Vault taranır → `Issue` listesi → md+json rapor (repo'ya, vault'a değil). Spec: `docs/specs/2026-05-21-otomaix-brain-doctor.md`.

**Tech Stack:** Python 3.12 stdlib only (`argparse, json, os, re, sys, dataclasses, datetime, fnmatch, pathlib`). Test: stdlib `unittest`.

**Spec → kod referansı:** §5 config, §6 16 kontrol, §7 link çözümleme sırası, §8 CLI/exit/guard, §9 rapor.

---

## File Structure

- Create: `tooling/brain-doctor/brain_doctor.py` — CLI + tüm check fonksiyonları
- Create: `tooling/brain-doctor/brain_doctor.config.json` — default config (spec §5)
- Create: `tooling/brain-doctor/test_brain_doctor.py` — unittest (fixture vault)
- Create: `tooling/brain-doctor/.gitignore` — `reports/` ignore
- Create: `tooling/brain-doctor/README.md` — kullanım
- Create: `.claude/commands/brain-doctor.md` — `/brain-doctor` slash wrapper (Task 14)

**Test komutu (her yerde):** `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor -v`
Tek test: `... python3 -m unittest test_brain_doctor.TestX.test_y -v`

---

## Task 1: Scaffold — config, skeleton, dataclasses, load_config

**Files:**
- Create: `tooling/brain-doctor/brain_doctor.config.json`
- Create: `tooling/brain-doctor/brain_doctor.py`
- Create: `tooling/brain-doctor/.gitignore`
- Create: `tooling/brain-doctor/test_brain_doctor.py`

- [ ] **Step 1: Write the config file** (`brain_doctor.config.json`)

```json
{
  "vault_path": "/root/otomaix-brain",
  "default_report_dir": "tooling/brain-doctor/reports",
  "exclude_globs": ["_health/**", ".git/**", "**/assets/**", "**/.obsidian/**"],
  "exempt_files": ["log.md", "AGENTS.md", "index.md", "CLAUDE.md", "inbox/README.md"],
  "required_frontmatter": ["title", "type", "status", "tags", "sources", "verification-status", "last-verified"],
  "optional_frontmatter": ["area"],
  "enums": {
    "type": ["decision", "concept", "vendor", "template", "history", "research"],
    "status": ["active", "completed", "superseded", "stub", "frozen"],
    "verification-status": ["a-verified", "unverified"]
  },
  "stale_rules": [
    { "glob": "decisions/**", "stale_days": null },
    { "glob": "apps/social/architecture/history/**", "stale_days": null },
    { "glob": "cross-project/vendors/**", "stale_days": 30 },
    { "glob": "apps/social/templates/**", "stale_days": 30 },
    { "glob": "cross-project/infrastructure/**", "stale_days": 45 },
    { "glob": "cross-project/copywriting/**", "stale_days": 60 }
  ],
  "default_stale_days": 45,
  "min_content_chars": 100,
  "severity": {
    "broken_wikilink": "error",
    "broken_md_link": "error",
    "ambiguous_link": "error",
    "index_mismatch_missing_file": "error",
    "frontmatter_absent": "error",
    "frontmatter_missing_field": "warning",
    "invalid_enum_value": "warning",
    "stale": "warning",
    "unresolved_conflicts": "warning",
    "empty_or_short": "warning",
    "sources_missing": "warning",
    "sources_empty": "info",
    "page_not_in_index": "warning",
    "orphan": "info",
    "stub": "info",
    "deprecated_visibility": "info"
  }
}
```

- [ ] **Step 2: Write the `.gitignore`**

```
reports/
__pycache__/
```

- [ ] **Step 3: Write module skeleton** (`brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Write the first tests** (`test_brain_doctor.py`)

```python
import json
import unittest
from pathlib import Path

import brain_doctor as bd

CONFIG = bd.load_config(Path(__file__).with_name("brain_doctor.config.json"))


class TestConfig(unittest.TestCase):
    def test_config_loads(self):
        self.assertEqual(CONFIG["vault_path"], "/root/otomaix-brain")
        self.assertIn("severity", CONFIG)

    def test_severity_covers_all_categories(self):
        # Spec §6: no emittable category without a severity mapping.
        self.assertEqual(bd.ALL_CATEGORIES, set(CONFIG["severity"]))

    def test_validate_severity_coverage_raises_on_missing(self):
        broken = {"severity": {"broken_wikilink": "error"}}
        with self.assertRaises(ValueError):
            bd.validate_severity_coverage(broken)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Run tests — verify pass**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor -v`
Expected: 3 tests PASS (config loads, severity covers all 16 categories, missing raises).

- [ ] **Step 6: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): scaffold config, dataclasses, severity coverage guard"
```

---

## Task 2: Frontmatter parser

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestFrontmatter(unittest.TestCase):
    def test_scalar_and_block_list(self):
        content = (
            "---\n"
            "title: Test Page\n"
            "type: concept\n"
            "tags: [a, b]\n"
            "sources:\n"
            "  - \"@/root/x.md\"\n"
            "  - \"@/root/y.md\"\n"
            "last-verified: 2026-05-13\n"
            "---\n\n"
            "Body text here.\n"
        )
        fm, body = bd.parse_frontmatter(content)
        self.assertEqual(fm["title"], "Test Page")
        self.assertEqual(fm["type"], "concept")
        self.assertEqual(fm["tags"], ["a", "b"])
        self.assertEqual(fm["sources"], ["@/root/x.md", "@/root/y.md"])
        self.assertEqual(body.strip(), "Body text here.")

    def test_no_frontmatter(self):
        fm, body = bd.parse_frontmatter("# Just a heading\nno fm")
        self.assertEqual(fm, {})

    def test_empty_inline_list(self):
        fm, _ = bd.parse_frontmatter("---\nsources: []\n---\nx")
        self.assertEqual(fm["sources"], [])
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestFrontmatter -v`
Expected: FAIL with `AttributeError: module 'brain_doctor' has no attribute 'parse_frontmatter'`

- [ ] **Step 3: Implement `parse_frontmatter`** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestFrontmatter -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add minimal stdlib frontmatter parser"
```

---

## Task 3: File iteration, exclude, page index

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
import tempfile, os as _os

class TestScan(unittest.TestCase):
    def _vault(self, files: dict) -> Path:
        d = Path(tempfile.mkdtemp())
        for rel, txt in files.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt, encoding="utf-8")
        return d

    def test_iter_excludes(self):
        v = self._vault({
            "decisions/a.md": "x",
            "_health/report.md": "x",
            ".git/HEAD": "x",
            "cross-project/vendors/assets/img.md": "x",
        })
        rels = bd.iter_markdown_files(v, CONFIG["exclude_globs"])
        self.assertIn("decisions/a.md", rels)
        self.assertNotIn("_health/report.md", rels)
        self.assertNotIn("cross-project/vendors/assets/img.md", rels)

    def test_page_index_basename(self):
        rels = ["apps/crm/architecture/deploy.md", "apps/social/x.md"]
        path_set, bidx = bd.build_page_index(rels)
        self.assertIn("apps/crm/architecture/deploy.md", path_set)
        self.assertEqual(bidx["deploy"], {"apps/crm/architecture/deploy.md"})
        self.assertEqual(bidx["deploy.md"], {"apps/crm/architecture/deploy.md"})
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestScan -v`
Expected: FAIL — `iter_markdown_files` not defined.

- [ ] **Step 3: Implement scan helpers** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestScan -v`
Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add markdown scan, exclude, page index"
```

---

## Task 4: Code-block stripping + link extraction

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestExtract(unittest.TestCase):
    def test_extract_and_classify(self):
        content = (
            "See [[apps/crm/architecture/deploy]] and [[x|alias]] and [[y#anchor]].\n"
            "[md](./local.md) [ext](https://e.com) [src](@/root/z.md) [anchor](#sec)\n"
            "`[[in-code]]` ignored.\n"
            "```\n[[also-ignored]]\n```\n"
        )
        links = bd.extract_links(content)
        targets = {(k, t) for k, t in links}
        self.assertIn(("wikilink", "apps/crm/architecture/deploy"), targets)
        self.assertIn(("wikilink", "x"), targets)
        self.assertIn(("wikilink", "y"), targets)
        self.assertIn(("mdlink", "./local.md"), targets)
        self.assertNotIn(("wikilink", "in-code"), targets)
        self.assertNotIn(("wikilink", "also-ignored"), targets)
        for k, t in links:
            self.assertFalse(t.startswith("http"))
            self.assertFalse(t.startswith("@"))
            self.assertNotEqual(t, "#sec")
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestExtract -v`
Expected: FAIL — `extract_links`/`strip_code` not defined.

- [ ] **Step 3: Implement** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestExtract -v`
Expected: 1 test PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add code-block stripping + link extraction"
```

---

## Task 5: Link resolution (spec §7 — critical, Codex-hardened)

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestResolve(unittest.TestCase):
    def setUp(self):
        self.rels = [
            "apps/crm/architecture/deploy.md",
            "apps/social/architecture/deploy.md",   # duplicate basename "deploy"
            "decisions/2026-05-19-x.md",
            "cross-project/vendors/kling.md",
        ]
        self.path_set, self.bidx = bd.build_page_index(self.rels)

    def _r(self, src, target):
        return bd.resolve_link(src, target, self.path_set, self.bidx)[0]

    def test_exact_with_md_appended(self):
        # extensionless full path → step 2 resolves, NOT ambiguous despite dup basename
        self.assertEqual(self._r("index.md", "cross-project/vendors/kling"), "ok")
        self.assertEqual(self._r("index.md", "apps/crm/architecture/deploy"), "ok")

    def test_exact_with_extension(self):
        self.assertEqual(self._r("index.md", "decisions/2026-05-19-x.md"), "ok")

    def test_basename_only_unique(self):
        self.assertEqual(self._r("index.md", "kling"), "ok")

    def test_basename_only_ambiguous(self):
        self.assertEqual(self._r("index.md", "deploy"), "ambiguous")

    def test_path_qualified_typo_is_broken_not_basename(self):
        # path-qualified miss must NOT degrade to basename → broken (Codex Turn-3 fix)
        self.assertEqual(self._r("index.md", "apps/crm/wrong/deploy"), "broken")

    def test_source_relative(self):
        self.assertEqual(self._r("apps/crm/architecture/x.md", "deploy.md"), "ok")
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestResolve -v`
Expected: FAIL — `resolve_link` not defined.

- [ ] **Step 3: Implement `resolve_link`** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestResolve -v`
Expected: 6 tests PASS — especially `test_path_qualified_typo_is_broken_not_basename` and `test_exact_with_md_appended`.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add spec-compliant link resolution (path-before-basename)"
```

---

## Task 6: Link checks (broken/ambiguous wiring)

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestCheckLinks(unittest.TestCase):
    def test_check_links_emits_categories(self):
        rels = ["a.md", "sub/b.md", "sub/c.md", "dup/x.md", "other/x.md"]
        path_set, bidx = bd.build_page_index(rels)
        pages = {
            "a.md": "[[sub/b]] ok\n[[no/such/page]] broken wiki\n[broken md](./missing.md)\n[[x]] ambiguous",
        }
        issues = bd.check_links(pages, path_set, bidx)
        cats = sorted({i.category for i in issues})
        self.assertEqual(cats, ["ambiguous_link", "broken_md_link", "broken_wikilink"])
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestCheckLinks -v`
Expected: FAIL — `check_links` not defined.

- [ ] **Step 3: Implement `check_links`** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestCheckLinks -v`
Expected: 1 test PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add link checks (broken/ambiguous)"
```

---

## Task 7: Frontmatter checks (absent/missing/enum/sources)

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestCheckFrontmatter(unittest.TestCase):
    def test_categories(self):
        pages = {
            "index.md": "no fm but exempt",
            "ok.md": (
                "---\ntitle: T\ntype: concept\nstatus: active\ntags: [x]\n"
                "sources:\n  - \"@/r.md\"\nverification-status: unverified\nlast-verified: 2026-01-01\n---\nbody"
            ),
            "absent.md": "# no frontmatter\nbody body body",
            "missing.md": "---\ntitle: T\ntype: concept\n---\nbody",
            "badenum.md": (
                "---\ntitle: T\ntype: wrongtype\nstatus: active\ntags: [x]\n"
                "sources:\n  - \"@/r.md\"\nverification-status: unverified\nlast-verified: 2026-01-01\n---\nbody"
            ),
            "emptysrc.md": (
                "---\ntitle: T\ntype: concept\nstatus: active\ntags: [x]\nsources: []\n"
                "verification-status: unverified\nlast-verified: 2026-01-01\n---\nbody"
            ),
        }
        issues = bd.check_frontmatter(pages, CONFIG)
        by_page = {}
        for i in issues:
            by_page.setdefault(i.page, set()).add(i.category)
        self.assertNotIn("index.md", by_page)        # exempt
        self.assertNotIn("ok.md", by_page)            # complete
        self.assertIn("frontmatter_absent", by_page["absent.md"])
        self.assertIn("frontmatter_missing_field", by_page["missing.md"])
        self.assertIn("invalid_enum_value", by_page["badenum.md"])
        self.assertIn("sources_empty", by_page["emptysrc.md"])
        # missing.md lacks sources entirely → sources_missing
        self.assertIn("sources_missing", by_page["missing.md"])
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestCheckFrontmatter -v`
Expected: FAIL — `check_frontmatter` not defined.

- [ ] **Step 3: Implement `check_frontmatter`** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestCheckFrontmatter -v`
Expected: 1 test PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add frontmatter checks (absent/missing/enum/sources)"
```

---

## Task 8: Stale check (folder-keyed thresholds)

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
from datetime import date as _date

class TestStale(unittest.TestCase):
    def _page(self, status, lv):
        return (f"---\ntitle: T\ntype: concept\nstatus: {status}\ntags: [x]\n"
                f"sources:\n  - \"@/r.md\"\nverification-status: unverified\nlast-verified: {lv}\n---\nbody")

    def test_resolve_days(self):
        rules = CONFIG["stale_rules"]
        self.assertIsNone(bd._resolve_stale_days("decisions/a.md", rules, 45))
        self.assertEqual(bd._resolve_stale_days("cross-project/vendors/kling.md", rules, 45), 30)
        self.assertEqual(bd._resolve_stale_days("cross-project/databases/x.md", rules, 45), 45)

    def test_stale_only_active_and_over_threshold(self):
        today = _date(2026, 5, 21)
        pages = {
            "cross-project/vendors/old.md": self._page("active", "2026-01-01"),   # >30d → stale
            "cross-project/vendors/fresh.md": self._page("active", "2026-05-15"), # <30d → ok
            "decisions/x.md": self._page("active", "2020-01-01"),                 # exempt glob
            "cross-project/vendors/done.md": self._page("completed", "2020-01-01"),  # not active
        }
        issues = bd.check_stale(pages, CONFIG, today)
        pages_flagged = {i.page for i in issues}
        self.assertEqual(pages_flagged, {"cross-project/vendors/old.md"})
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestStale -v`
Expected: FAIL — `_resolve_stale_days`/`check_stale` not defined.

- [ ] **Step 3: Implement** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestStale -v`
Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add folder-keyed stale check"
```

---

## Task 9: Conflicts, empty/short, stub checks

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestSimpleChecks(unittest.TestCase):
    def test_conflicts(self):
        pages = {
            "a.md": "body\n## ⚠️ Conflicts\n- Status: unresolved\n",
            "b.md": "body\n## ⚠️ Conflicts\n- Status: resolved\n",
            "c.md": "no conflicts here",
        }
        flagged = {i.page for i in bd.check_conflicts(pages)}
        self.assertEqual(flagged, {"a.md"})

    def test_empty(self):
        pages = {
            "short.md": "---\ntitle: T\n---\ntiny",
            "ok.md": "---\ntitle: T\n---\n" + ("x" * 150),
            "index.md": "tiny",  # exempt
        }
        flagged = {i.page for i in bd.check_empty(pages, CONFIG)}
        self.assertEqual(flagged, {"short.md"})

    def test_stub(self):
        pages = {
            "s.md": "---\nstatus: stub\n---\nx",
            "a.md": "---\nstatus: active\n---\nx",
        }
        flagged = {i.page for i in bd.check_stub(pages)}
        self.assertEqual(flagged, {"s.md"})
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestSimpleChecks -v`
Expected: FAIL — checks not defined.

- [ ] **Step 3: Implement** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestSimpleChecks -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add conflicts/empty/stub checks"
```

---

## Task 10: Index checks + orphan + deprecated visibility

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestIndexChecks(unittest.TestCase):
    def setUp(self):
        self.pages = {
            "index.md": "# Index\n- [[decisions/a]]\n- [[missing/page]]\n- `cross-project/vendors/kling.md`\n",
            "decisions/a.md": "---\nstatus: active\n---\n" + ("x" * 150),
            "cross-project/vendors/kling.md": "---\nstatus: active\n---\n" + ("x" * 150),
            "orphan/lonely.md": "---\nstatus: active\n---\n" + ("x" * 150),
            "decisions/old.md": "---\nstatus: superseded\n---\n" + ("x" * 150),
        }
        # add old to index so deprecated_visibility triggers
        self.pages["index.md"] += "- [[decisions/old]]\n"
        self.rels = [r for r in self.pages]
        self.path_set, self.bidx = bd.build_page_index(self.rels)

    def test_index_mismatch_and_referenced(self):
        issues, referenced = bd.check_index(self.pages, self.path_set, self.bidx)
        self.assertTrue(any(i.category == "index_mismatch_missing_file" for i in issues))
        self.assertIn("decisions/a.md", referenced)
        self.assertIn("cross-project/vendors/kling.md", referenced)  # backtick ref

    def test_page_not_in_index(self):
        _, referenced = bd.check_index(self.pages, self.path_set, self.bidx)
        flagged = {i.page for i in bd.check_page_not_in_index(self.pages, CONFIG, referenced)}
        self.assertIn("orphan/lonely.md", flagged)
        self.assertNotIn("decisions/a.md", flagged)

    def test_orphan(self):
        _, referenced = bd.check_index(self.pages, self.path_set, self.bidx)
        flagged = {i.page for i in bd.check_orphan(self.pages, CONFIG, self.path_set, self.bidx, referenced)}
        self.assertIn("orphan/lonely.md", flagged)
        self.assertNotIn("decisions/a.md", flagged)  # referenced by index

    def test_deprecated_visibility(self):
        _, referenced = bd.check_index(self.pages, self.path_set, self.bidx)
        flagged = {i.page for i in bd.check_deprecated_visibility(self.pages, referenced)}
        self.assertIn("decisions/old.md", flagged)
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestIndexChecks -v`
Expected: FAIL — index/orphan checks not defined.

- [ ] **Step 3: Implement** (add to `brain_doctor.py`)

```python
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestIndexChecks -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add index/orphan/deprecated-visibility checks"
```

---

## Task 11: Severity assignment + run_checks orchestrator

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestRun(unittest.TestCase):
    def _vault(self, files):
        import tempfile
        d = Path(tempfile.mkdtemp())
        for rel, txt in files.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt, encoding="utf-8")
        return d

    def test_apply_severity_and_every_issue_mapped(self):
        v = self._vault({
            "index.md": "# Index\n- [[decisions/a]]\n",
            "decisions/a.md": ("---\ntitle: T\ntype: decision\nstatus: active\ntags: [x]\n"
                               "sources:\n  - \"@/r.md\"\nverification-status: unverified\n"
                               "last-verified: 2026-05-01\n---\n" + ("x" * 150)),
            "decisions/broken.md": "# no frontmatter and [[no/such]]\nbody body body body body",
        })
        report = bd.run_checks(v, CONFIG, today=_date(2026, 5, 21))
        self.assertGreater(len(report.issues), 0)
        # every emitted issue has a real severity from config
        for i in report.issues:
            self.assertIn(i.severity, ("error", "warning", "info"))
            self.assertIn(i.category, CONFIG["severity"])
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestRun -v`
Expected: FAIL — `run_checks`/`apply_severity` not defined.

- [ ] **Step 3: Implement** (add to `brain_doctor.py`)

```python
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
    issues += check_conflicts(pages)
    issues += check_empty(pages, config)
    issues += check_stub(pages)
    issues += check_orphan(pages, config, path_set, basename_index, index_referenced)
    issues += check_deprecated_visibility(pages, index_referenced)

    apply_severity(issues, config)
    return Report(generated=today.isoformat(), total_pages=len(pages), issues=issues)
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestRun -v`
Expected: 1 test PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add severity assignment + run_checks orchestrator"
```

---

## Task 12: Reporting (markdown + json)

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestReport(unittest.TestCase):
    def _report(self):
        return bd.Report(generated="2026-05-21", total_pages=3, issues=[
            bd.Issue("error", "broken_wikilink", "a.md", "broken: 'x'"),
            bd.Issue("info", "stub", "b.md", "status: stub"),
        ])

    def test_json(self):
        data = json.loads(bd.render_json(self._report()))
        self.assertEqual(data["total_pages"], 3)
        self.assertEqual(len(data["issues"]), 2)
        self.assertEqual(data["issues"][0]["category"], "broken_wikilink")

    def test_markdown(self):
        md = bd.render_markdown(self._report())
        self.assertIn("Brain Doctor Report", md)
        self.assertIn("error: 1", md)
        self.assertIn("broken_wikilink", md)
        self.assertIn("`a.md`", md)
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestReport -v`
Expected: FAIL — `render_json`/`render_markdown` not defined.

- [ ] **Step 3: Implement** (add to `brain_doctor.py`)

```python
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
    counts = {s: sum(1 for i in report.issues if i.severity == s) for s in ("error", "warning", "info")}
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestReport -v`
Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add markdown + json report renderers"
```

---

## Task 13: CLI main — path resolution, vault guard, exit codes

**Files:** Modify `brain_doctor.py`, `test_brain_doctor.py`

- [ ] **Step 1: Write the failing test**

```python
class TestCli(unittest.TestCase):
    def _vault(self, files):
        import tempfile
        d = Path(tempfile.mkdtemp())
        for rel, txt in files.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt, encoding="utf-8")
        return d

    def test_repo_root_finds_git(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / ".git").mkdir()
        sub = d / "tooling" / "brain-doctor"
        sub.mkdir(parents=True)
        self.assertEqual(bd.repo_root(sub / "brain_doctor.config.json"), d.resolve())

    def test_vault_output_guard_blocks(self):
        v = self._vault({"index.md": "# Index\n", "a.md": "---\ntitle: T\n---\n" + ("x" * 150)})
        # output dir inside the vault, no --allow-vault-output → exit 2
        rc = bd.main(["--vault", str(v), "--config", str(Path(__file__).with_name("brain_doctor.config.json")),
                      "--output-dir", str(v / "_health")])
        self.assertEqual(rc, 2)

    def test_json_mode_clean_vault_exit_0(self):
        v = self._vault({
            "index.md": "# Index\n- [[a]]\n",
            "a.md": ("---\ntitle: T\ntype: concept\nstatus: active\ntags: [x]\n"
                     "sources:\n  - \"@/r.md\"\nverification-status: unverified\n"
                     "last-verified: 2026-05-20\n---\n" + ("x" * 150)),
        })
        rc = bd.main(["--vault", str(v), "--config", str(Path(__file__).with_name("brain_doctor.config.json")),
                      "--json", "--no-report"])
        # may have warnings/info but no error → exit 0
        self.assertEqual(rc, 0)

    def test_json_stdout_is_pure_json(self):
        import io, contextlib
        v = self._vault({
            "index.md": "# Index\n- [[a]]\n",
            "a.md": ("---\ntitle: T\ntype: concept\nstatus: active\ntags: [x]\n"
                     "sources:\n  - \"@/r.md\"\nverification-status: unverified\n"
                     "last-verified: 2026-05-20\n---\n" + ("x" * 150)),
        })
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bd.main(["--vault", str(v), "--config", str(Path(__file__).with_name("brain_doctor.config.json")),
                     "--json"])
        # stdout MUST be pure JSON (summary + "Rapor:" go to stderr)
        data = json.loads(buf.getvalue())
        self.assertIn("issues", data)

    def test_error_exit_1(self):
        v = self._vault({"index.md": "# Index\n", "a.md": "# no frontmatter [[no/such]]\nbody body body"})
        rc = bd.main(["--vault", str(v), "--config", str(Path(__file__).with_name("brain_doctor.config.json")),
                      "--no-report"])
        self.assertEqual(rc, 1)  # broken_wikilink + frontmatter_absent = error

    def test_bad_config_exit_2(self):
        rc = bd.main(["--config", "/nonexistent/config.json"])
        self.assertEqual(rc, 2)
```

- [ ] **Step 2: Run test — verify it fails**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestCli -v`
Expected: FAIL — `main`/`repo_root` not defined.

- [ ] **Step 3: Implement** (add to `brain_doctor.py`)

```python
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

    counts = {s: sum(1 for i in report.issues if i.severity == s) for s in ("error", "warning", "info")}
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
```

- [ ] **Step 4: Run test — verify it passes**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor.TestCli -v`
Expected: 6 tests PASS (repo_root, guard blocks, json clean exit 0, json stdout pure JSON, error exit 1, bad config exit 2).

- [ ] **Step 5: Run the FULL suite**

Run: `cd tooling/brain-doctor && python3 -m unittest test_brain_doctor -v`
Expected: All tests PASS (Tasks 1–13).

- [ ] **Step 6: Commit**

```bash
git add tooling/brain-doctor/
git commit -m "feat(brain-doctor): add CLI main with repo-anchored output + vault guard + exit codes"
```

---

## Task 14: Real-vault smoke + README + slash command

**Files:**
- Create: `tooling/brain-doctor/README.md`
- Create: `.claude/commands/brain-doctor.md`

- [ ] **Step 1: Smoke run against the real vault (read-only, json to stdout)**

Run: `cd /root/otomaix/tooling/brain-doctor && python3 brain_doctor.py --json --no-report`
Expected: Console summary line + JSON; exit code echo `echo $?`. Vault NOT modified (verify `cd /root/otomaix-brain && git status --short` shows nothing new). Confirm known issues surface (e.g. `unresolved_conflicts` on özelgun-gorsel-sablon, marketingskills pages).

- [ ] **Step 2: Smoke run writing a report to the repo (default dir)**

Run: `cd /root/otomaix && python3 tooling/brain-doctor/brain_doctor.py`
Expected: writes `tooling/brain-doctor/reports/report.md` + `report.json` (repo, NOT vault). Verify `/root/otomaix-brain` untouched.

- [ ] **Step 3: Write README** (`tooling/brain-doctor/README.md`)

```markdown
# Otomaix Brain Doctor v1

`otomaix-brain` vault'unun yapısal sağlık denetçisi. Stdlib-only, vault'a karşı read-only.
Spec: `docs/specs/2026-05-21-otomaix-brain-doctor.md`.

## Kullanım

    python3 tooling/brain-doctor/brain_doctor.py            # rapor → tooling/brain-doctor/reports/
    python3 tooling/brain-doctor/brain_doctor.py --json --no-report   # stdout JSON, dosya yok
    python3 tooling/brain-doctor/brain_doctor.py --min-severity error # sadece error

Exit: 0 = error yok | 1 = ≥1 error | 2 = tool/config/IO hatası.
Vault'a yazma yalnız `--output-dir <vault>/_health --allow-vault-output` ile.

## Test

    cd tooling/brain-doctor && python3 -m unittest -v
```

- [ ] **Step 4: Write slash command** (`.claude/commands/brain-doctor.md`)

```markdown
---
description: otomaix-brain vault sağlık denetçisini çalıştır (read-only)
---

`tooling/brain-doctor/brain_doctor.py`'yi çalıştır: `python3 tooling/brain-doctor/brain_doctor.py --json --no-report`.
Çıktıyı oku, error/warning/info'yu özetle, en kritik bulguları (broken link, ambiguous, frontmatter_absent) öne çıkar.
Otomatik düzeltme YAPMA (v1 read-only). Vault'a yazma.
```

- [ ] **Step 5: Final full suite + commit**

Run: `cd tooling/brain-doctor && python3 -m unittest -v`
Expected: All PASS.

```bash
git add tooling/brain-doctor/README.md .claude/commands/brain-doctor.md
git commit -m "docs(brain-doctor): add README + /brain-doctor slash command"
```

---

## Self-Review (yazım sonrası — plan ↔ spec)

**Spec coverage (§6 16 kontrol → task):**
- broken_wikilink/broken_md_link/ambiguous_link → Task 5+6 ✓
- index_mismatch_missing_file/page_not_in_index → Task 10 ✓
- frontmatter_absent/missing_field/invalid_enum_value → Task 7 ✓
- sources_missing/sources_empty → Task 7 ✓
- stale → Task 8 ✓ · unresolved_conflicts/empty_or_short/stub → Task 9 ✓
- orphan/deprecated_visibility → Task 10 ✓
- §5 config → Task 1 ✓ · §7 çözümleme sırası → Task 5 ✓ · §8 CLI/guard/exit → Task 13 ✓ · §9 rapor → Task 12 ✓ · §10 unittest → her task ✓
- "her kategori config.severity'de" testi → Task 1 + Task 11 ✓

**Type consistency:** `Issue(severity, category, page, detail, line)` ve `resolve_link → (status, rel)` tüm task'larda tutarlı; check fonksiyonları `Issue("", cat, ...)` üretir, severity Task 11'de atanır.

**Placeholder taraması:** Yok — her step tam kod içeriyor.
