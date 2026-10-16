# Fueav Harness Plugins

`fueav-harness` is an umbrella marketplace for the Fueav Harness plugin family. It is a client-agnostic index only: it contains no Skill or vendored plugin source.

| Plugin | Source repository | Role |
| --- | --- | --- |
| `harness-template-sync` | [`Fueav/harness-template-sync`](https://github.com/Fueav/harness-template-sync) | Delivers one bootstrap or explicit upgrade from the canonical Scaffold Source, verifies the migrated candidate, then exits. |

Each plugin keeps its own repository, version, release tags, evals, and release gates. This marketplace resolves plugin sources remotely, so nothing here duplicates a plugin's source of truth. Daily work uses native project commands and the pinned engine.

## Install

Codex:

```bash
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-template-sync@fueav-harness
```

Claude Code:

```bash
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-template-sync@fueav-harness --scope user
```

Install only the plugin needed for the operation. The previous daily compatibility entry is retired from this distribution; existing pinned installations can remain on their old release. Restart the client or open a new session after installing.

On a freshly added marketplace, the first `codex plugin list` can render `fueav-harness` with no plugin table while the remote sources are still being resolved. Run `codex plugin add` anyway; subsequent listings show the delivery plugin with its resolved source repository.

## Migrate from the per-repository marketplaces

The umbrella marketplace declares different install coordinates, so an existing installation must be removed before it is added again. The v4 delivery plugin migrates execution contracts; this marketplace does not alter existing installed plugins.

Codex:

```bash
codex plugin remove harness-template-sync@fueav-harness-sync
codex plugin marketplace remove fueav-harness-sync
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-template-sync@fueav-harness
```

Claude Code:

```bash
claude plugin uninstall harness-template-sync@fueav-harness-sync --scope user
claude plugin marketplace remove fueav-harness-sync --scope user
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-template-sync@fueav-harness --scope user
```

Existing per-repository releases remain available for pinned consumers. Installing a plugin from both this marketplace and its own marketplace at the same time is not supported; choose one coordinate per plugin.

## Version policy

Plugin entries intentionally omit `ref`, so each plugin follows its source repository's default branch and marketplace upgrades track upstream releases. Pin an immutable installation by adding `"ref": "<tag>"` to that plugin's `source` in both manifests and releasing this repository.

## Upgrade

```bash
codex plugin marketplace upgrade fueav-harness
claude plugin marketplace update fueav-harness
```

## Verify a source checkout

```bash
python3 scripts/test_verify_release.py
python3 scripts/verify_release.py
claude plugin validate .claude-plugin/marketplace.json
```

`verify_release.py` enforces the invariants this repository owns: both manifests declare the same marketplace name, the same plugin set, and byte-identical sources including `ref`; the marketplace name never equals a plugin name; and the repository vendors no plugin source and ships no Skill.
