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


if __name__ == "__main__":
    unittest.main()
