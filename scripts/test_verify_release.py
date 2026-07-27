#!/usr/bin/env python3
"""Regression tests for the Fueav Harness umbrella marketplace validator."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACES = (
    Path(".agents/plugins/marketplace.json"),
    Path(".claude-plugin/marketplace.json"),
)


class ReleaseValidatorTests(unittest.TestCase):
    def run_validator(self, checkout: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/verify_release.py"],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=False,
        )

    def copy_checkout(self, temp_dir: str) -> Path:
        checkout = Path(temp_dir) / "checkout"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return checkout

    def mutate(self, checkout: Path, relative_path: Path, mutation) -> None:
        path = checkout / relative_path
        document = json.loads(path.read_text())
        mutation(document)
        path.write_text(json.dumps(document, indent=2) + "\n")

    def test_accepts_clean_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_validator(self.copy_checkout(temp_dir))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_marketplace_name_equal_to_plugin_name(self) -> None:
        for relative_path in MARKETPLACES:
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as temp_dir:
                checkout = self.copy_checkout(temp_dir)
                self.mutate(
                    checkout,
                    relative_path,
                    lambda document: document.update({"name": document["plugins"][0]["name"]}),
                )
                result = self.run_validator(checkout)
                self.assertEqual(result.returncode, 1)
                self.assertIn("must never equal plugin name", result.stdout)

    def test_rejects_divergent_plugin_sets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            self.mutate(
                checkout,
                MARKETPLACES[0],
                lambda document: document["plugins"].pop(),
            )
            result = self.run_validator(checkout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("same plugin set", result.stdout)

    def test_rejects_source_drift_between_clients(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            self.mutate(
                checkout,
                MARKETPLACES[1],
                lambda document: document["plugins"][0]["source"].update({"ref": "v2.0.1"}),
            )
            result = self.run_validator(checkout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("different source per client", result.stdout)

    def test_rejects_vendored_plugin_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            (checkout / "plugins" / "harness-driven-development").mkdir(parents=True)
            result = self.run_validator(checkout)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must not vendor plugin source", result.stdout)


if __name__ == "__main__":
    unittest.main()
