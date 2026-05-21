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


class TestRun(unittest.TestCase):
    def _vault(self, files):
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


class TestCli(unittest.TestCase):
    def _vault(self, files):
        d = Path(tempfile.mkdtemp())
        for rel, txt in files.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt, encoding="utf-8")
        return d

    def test_repo_root_finds_git(self):
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


if __name__ == "__main__":
    unittest.main()
