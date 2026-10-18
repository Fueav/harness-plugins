# Fueav Harness Plugins

`fueav-harness` is an umbrella marketplace for one explicit template migration plugin. It is a client-agnostic index only: it contains no Skill or vendored plugin source.

| Plugin | Source repository | Role |
| --- | --- | --- |
| `harness-template-sync` | [`Fueav/harness-template-sync`](https://github.com/Fueav/harness-template-sync) | Delivers one bootstrap or explicit upgrade from the canonical Scaffold Source, checks migration structure and native project results, then exits. |

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

Install only the plugin needed for the operation. The previous daily compatibility entry is retired; uninstall it when upgrading an existing installation. Restart the client or open a new session after installing.

## Migrate from the per-repository marketplaces

Codex:

```bash
codex plugin remove harness-driven-development@fueav-harness-development
codex plugin marketplace remove fueav-harness-development
codex plugin remove harness-template-sync@fueav-harness-sync
codex plugin marketplace remove fueav-harness-sync
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-template-sync@fueav-harness
```

Claude Code:

```bash
claude plugin uninstall harness-driven-development@fueav-harness-development --scope user
claude plugin marketplace remove fueav-harness-development --scope user
claude plugin uninstall harness-template-sync@fueav-harness-sync --scope user
claude plugin marketplace remove fueav-harness-sync --scope user
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-template-sync@fueav-harness --scope user
```

## Version policy

Plugin entries intentionally omit `ref`, so each plugin follows its source repository's default branch and marketplace upgrades track upstream releases. Pin an immutable installation by adding `"ref": "<tag>"` to that plugin's `source` in both manifests and releasing this repository.

## Upgrade

```bash
codex plugin remove harness-driven-development@fueav-harness
codex plugin marketplace upgrade fueav-harness
codex plugin add harness-template-sync@fueav-harness
claude plugin uninstall harness-driven-development@fueav-harness --scope user
claude plugin marketplace update fueav-harness
claude plugin update harness-template-sync@fueav-harness
```

## Verify a source checkout

```bash
python3 scripts/test_verify_release.py
python3 scripts/verify_release.py
claude plugin validate .claude-plugin/marketplace.json
```

`verify_release.py` enforces the invariants this repository owns: both manifests declare the same marketplace name, the same plugin set, and byte-identical sources including `ref`; the marketplace name never equals a plugin name; and the repository vendors no plugin source and ships no Skill.
