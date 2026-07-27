#!/usr/bin/env python3
"""Validate the Fueav Harness umbrella marketplace package."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_NAME = "fueav-harness"
CODEX_MANIFEST = Path(".agents/plugins/marketplace.json")
CLAUDE_MANIFEST = Path(".claude-plugin/marketplace.json")
EXPECTED_PLUGINS = {
    "harness-driven-development": "https://github.com/Fueav/harness-driven-development.git",
    "harness-template-sync": "https://github.com/Fueav/harness-template-sync.git",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path, errors: list[str]) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON at {path.relative_to(ROOT)}: {exc}")
        return None


def source_key(plugin: dict) -> tuple:
    """Client-neutral identity of a plugin source, comparable across manifests."""
    source = plugin.get("source")
    if not isinstance(source, dict):
        return ("invalid", repr(source))
    return (
        source.get("source"),
        source.get("url"),
        source.get("path"),
        source.get("ref"),
    )


def validate_manifest(document: dict, label: str, errors: list[str]) -> dict[str, tuple]:
    require(
        document.get("name") == MARKETPLACE_NAME,
        f"{label} must declare marketplace name {MARKETPLACE_NAME}",
        errors,
    )

    plugins = document.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append(f"{label} must declare a non-empty plugins list")
        return {}

    sources: dict[str, tuple] = {}
    for index, plugin in enumerate(plugins):
        name = plugin.get("name") if isinstance(plugin, dict) else None
        if not isinstance(name, str) or not name:
            errors.append(f"{label} plugin at index {index} has no name")
            continue

        require(
            name != document.get("name"),
            f"{label} marketplace name must never equal plugin name {name}",
            errors,
        )

        source = plugin.get("source")
        if not isinstance(source, dict):
            errors.append(f"{label} plugin {name} must resolve a remote source, not a vendored path")
            continue

        require(
            source.get("source") == "git-subdir",
            f"{label} plugin {name} must use a git-subdir source",
            errors,
        )
        require(
            source.get("url") == EXPECTED_PLUGINS.get(name),
            f"{label} plugin {name} must resolve its own source repository",
            errors,
        )
        require(
            isinstance(source.get("path"), str) and source.get("path", "").strip(),
            f"{label} plugin {name} must declare a subdirectory path",
            errors,
        )
        sources[name] = source_key(plugin)

    return sources


def main() -> int:
    errors: list[str] = []

    require(
        not (ROOT / "plugins").exists(),
        "umbrella marketplace must not vendor plugin source; every plugin resolves remotely",
        errors,
    )
    require(
        not list(ROOT.glob("**/SKILL.md")),
        "umbrella marketplace must not ship a Skill",
        errors,
    )

    codex = load_json(ROOT / CODEX_MANIFEST, errors)
    claude = load_json(ROOT / CLAUDE_MANIFEST, errors)
    if codex is None or claude is None:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    codex_sources = validate_manifest(codex, "codex marketplace", errors)
    claude_sources = validate_manifest(claude, "claude marketplace", errors)

    require(
        codex.get("name") == claude.get("name"),
        "both manifests must declare the same marketplace name",
        errors,
    )
    require(
        set(codex_sources) == set(claude_sources),
        "both manifests must declare the same plugin set",
        errors,
    )
    require(
        set(codex_sources) == set(EXPECTED_PLUGINS),
        f"marketplace must publish exactly {sorted(EXPECTED_PLUGINS)}",
        errors,
    )

    for name in sorted(set(codex_sources) & set(claude_sources)):
        require(
            codex_sources[name] == claude_sources[name],
            f"plugin {name} resolves a different source per client",
            errors,
        )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(f"marketplace contract ok: {MARKETPLACE_NAME}")
    for name in sorted(codex_sources):
        kind, url, path, ref = codex_sources[name]
        print(f"  {name}: {kind} {url} path {path} ref {ref or 'default branch'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
