import json
import tempfile
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


if __name__ == "__main__":
    unittest.main()
