import json
import tempfile
import unittest
from datetime import date as _date
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


if __name__ == "__main__":
    unittest.main()
